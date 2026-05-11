"""Phase 8D — MCP-facing js_analyzer tool wrappers.

Four tools added in this layer:

  * js_index_target   — wraps the /js_analyzer slash logic.
                        Single source of truth: the slash now dispatches
                        through this tool.
  * js_get_chains     — wraps reporter.extract_findings().
  * js_run_audit      — fire-and-forget audit launcher. Inserts a row
                        into js_audit_runs with status='running' and a
                        uuid4 external_run_id, spawns
                        analyse_chains_async() as a background task,
                        returns the run_id within 100 ms.
  * js_audit_status   — reads js_audit_runs + js_audit_turns by
                        external_run_id.

run_id is a uuid4 string keyed via the js_audit_runs.external_run_id
column (see callgraph.py SCHEMA + 8D migration). The integer id PK is
preserved for AuditRun's internal lifecycle.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from kernel.tools import Tool

_logger = structlog.get_logger(__name__)


def _audit_db_path(kernel: Any) -> Path | None:
    """Resolve ~/.tlx/js_analyzer.db via the registered CallGraph service."""
    services = getattr(kernel, "services", None)
    if services is None:
        return None
    cg = services.get("js_analyzer_callgraph")
    if cg is None:
        return None
    return getattr(cg, "db_path", None)


def _open_audit_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def _resolve_target(kernel: Any, target_folder: str) -> tuple[Path | None, str | None]:
    """Validate target path against sandbox + filesystem.

    Returns (resolved_path, None) on success; (None, error_message) on failure.
    """
    target = Path(target_folder).expanduser().resolve()
    sandbox = getattr(kernel, "sandbox", None)
    if sandbox is not None and not sandbox.is_allowed(str(target)):
        return None, f"js_analyzer: path outside sandbox roots: {target}"
    if not target.exists() or not target.is_dir():
        return None, f"js_analyzer: not a directory: {target}"
    return target, None


def _tool_js_index_target(kernel: Any, cfg: Any, target_folder: str) -> str:
    """Index a JS folder; return JSON {nodes, edges, tags, frameworks, itp,
    cached_unchanged, files_total, target} or {error, ...}."""
    from modules.js_analyzer.module import _index_target_payload

    target, err = _resolve_target(kernel, target_folder)
    if err is not None:
        return json.dumps({"error": err})
    cfg.target = str(target)
    payload = _index_target_payload(kernel, target, cfg)
    return json.dumps(payload)


def _tool_js_get_chains(
    kernel: Any, cfg: Any, target_folder: str, max_chains: int = 20,
) -> str:
    """Return reporter.extract_findings() output, capped at max_chains."""
    from modules.js_analyzer.reporter import extract_findings

    target, err = _resolve_target(kernel, target_folder)
    if err is not None:
        return json.dumps({"error": err})

    cg = kernel.services.get("js_analyzer_callgraph")
    if cg is None:
        return json.dumps({"error": "js_analyzer: callgraph service missing"})

    try:
        max_chains_int = max(1, int(max_chains))
    except (TypeError, ValueError):
        max_chains_int = 20

    findings = extract_findings(
        gemini_reply="",
        target_folder=str(target),
        callgraph=cg,
        severity=cfg.severity,
    )
    if findings is None:
        return json.dumps({
            "target_folder": str(target),
            "chains": [],
            "snippets": {},
            "index_stats": {
                "nodes": cg.node_count(),
                "edges": cg.edge_count(),
                "tags": cg.tag_count(),
            },
        })

    chains = list(findings.get("chains", []))[:max_chains_int]
    keep_qnames: set[str] = set()
    for chain in chains:
        for q in chain.get("path", []) or []:
            keep_qnames.add(q)
    snippets = {
        q: v for q, v in findings.get("snippets", {}).items()
        if q in keep_qnames
    }
    return json.dumps({
        "target_folder": findings.get("target_folder", str(target)),
        "index_stats": findings.get("index_stats", {}),
        "chains": chains,
        "snippets": snippets,
    })


def _insert_audit_run(
    db_path: Path, shell_session_id: str, target_folder: str,
    external_run_id: str,
) -> int:
    """Synchronously insert a js_audit_runs row with status='running'."""
    conn = _open_audit_conn(db_path)
    try:
        started_at = datetime.now(UTC).isoformat()
        cur = conn.execute(
            "INSERT INTO js_audit_runs "
            "(shell_session_id, target_folder, started_at, status, "
            " external_run_id) "
            "VALUES (?, ?, ?, 'running', ?)",
            (shell_session_id, target_folder, started_at, external_run_id),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def _tool_js_run_audit(kernel: Any, cfg: Any, target_folder: str) -> str:
    """Fire-and-forget audit launcher.

    1. Validate target.
    2. Build findings via extract_findings (synchronous).
    3. Insert js_audit_runs row with status='running' and uuid external_run_id.
    4. Spawn analyse_chains_async(... external_run_id=...) as bg task.
    5. Return {"run_id": uuid} immediately.
    """
    from modules.js_analyzer.claude_agent import analyse_chains_async
    from modules.js_analyzer.reporter import extract_findings

    target, err = _resolve_target(kernel, target_folder)
    if err is not None:
        return json.dumps({"error": err})

    cg = kernel.services.get("js_analyzer_callgraph")
    if cg is None:
        return json.dumps({"error": "js_analyzer: callgraph service missing"})

    findings = extract_findings(
        gemini_reply="",
        target_folder=str(target),
        callgraph=cg,
        severity=cfg.severity,
    )
    if findings is None:
        return json.dumps({"error": "js_analyzer: no source→sink chains found"})

    state = kernel.services.get("js_analyzer_state")
    if state is not None:
        state.last_findings = findings

    db_path = _audit_db_path(kernel)
    if db_path is None:
        return json.dumps({"error": "js_analyzer: audit db path unavailable"})

    run_id = uuid.uuid4().hex
    shell_session_id = str(getattr(kernel, "session_id", "unknown"))
    try:
        _insert_audit_run(db_path, shell_session_id, str(target), run_id)
    except Exception as exc:
        _logger.warning("js_analyzer.run_audit_insert_failed", error=str(exc))
        return json.dumps({"error": f"js_analyzer: audit insert failed: {exc}"})

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    coro = analyse_chains_async(
        findings, kernel, external_run_id=run_id,
    )
    if loop is not None:
        task = loop.create_task(coro)

        def _on_done(_t: asyncio.Task) -> None:
            exc = _t.exception() if not _t.cancelled() else None
            if exc is not None:
                _logger.warning("js_analyzer.run_audit_task_failed",
                                run_id=run_id, error=str(exc))

        task.add_done_callback(_on_done)
    else:
        # No running loop — close the unused coroutine to avoid warnings.
        # Caller must invoke this tool from inside an event loop.
        coro.close()
        return json.dumps({
            "error": "js_analyzer: js_run_audit requires a running event loop",
        })

    return json.dumps({"run_id": run_id, "status": "running"})


def _tool_js_audit_status(kernel: Any, run_id: str) -> str:
    """Read row + turns by external_run_id (uuid)."""
    db_path = _audit_db_path(kernel)
    if db_path is None:
        return json.dumps({"error": "js_analyzer: audit db path unavailable"})

    conn = _open_audit_conn(db_path)
    try:
        row = conn.execute(
            "SELECT id, shell_session_id, target_folder, started_at, "
            "       finished_at, status, total_tokens, cost_usd, "
            "       consults_used, consults_cost_usd, failure_reason "
            "FROM js_audit_runs WHERE external_run_id=?",
            (run_id,),
        ).fetchone()
        if row is None:
            return json.dumps({"error": f"unknown run_id: {run_id}"})
        (
            internal_id, shell_session_id, target_folder, started_at,
            finished_at, status, total_tokens, cost_usd, consults_used,
            consults_cost_usd, failure_reason,
        ) = row
        turns_rows = conn.execute(
            "SELECT turn_index, role, tokens_in, tokens_out, cost_usd, "
            "       observed_at "
            "FROM js_audit_turns WHERE run_id=? ORDER BY turn_index",
            (internal_id,),
        ).fetchall()
    finally:
        conn.close()

    turns = [
        {
            "turn_index": t[0],
            "role": t[1],
            "tokens_in": t[2] or 0,
            "tokens_out": t[3] or 0,
            "cost_usd": float(t[4] or 0.0),
            "observed_at": t[5],
        }
        for t in turns_rows
    ]
    return json.dumps({
        "run_id": run_id,
        "shell_session_id": shell_session_id,
        "target_folder": target_folder,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "total_tokens": int(total_tokens or 0),
        "cost_usd": float(cost_usd or 0.0),
        "consults_used": int(consults_used or 0),
        "consults_cost_usd": float(consults_cost_usd or 0.0),
        "failure_reason": failure_reason,
        "turns": turns,
    })


def make_extra_tools(kernel: Any, cfg: Any) -> list[Tool]:
    """Build the four 8D Tool wrappers."""
    return [
        Tool(
            name="js_index_target",
            description=(
                "Index a JS target folder into the call graph. Returns "
                "JSON: {target, nodes, edges, tags, frameworks, itp, "
                "cached_unchanged, files_total} or {error}."
            ),
            params={
                "type": "object",
                "properties": {
                    "target_folder": {
                        "type": "string",
                        "description": "Absolute path to the JS folder.",
                    },
                },
                "required": ["target_folder"],
            },
            handler=lambda target_folder: _tool_js_index_target(
                kernel, cfg, target_folder,
            ),
            requires=["path_access"],
        ),
        Tool(
            name="js_get_chains",
            description=(
                "Return the top-scored source→sink chains for an indexed "
                "target. Wraps reporter.extract_findings(); honours "
                "max_chains (default 20)."
            ),
            params={
                "type": "object",
                "properties": {
                    "target_folder": {"type": "string"},
                    "max_chains":    {"type": "integer"},
                },
                "required": ["target_folder"],
            },
            handler=lambda target_folder, max_chains=20: _tool_js_get_chains(
                kernel, cfg, target_folder, max_chains,
            ),
            requires=["path_access"],
        ),
        Tool(
            name="js_run_audit",
            description=(
                "Launch the audit loop in the background. Returns "
                "{\"run_id\": <uuid>} within 100 ms; poll with "
                "js_audit_status. Caps unchanged "
                "(MAX_CONSULTS=5, $1.50/run, $2.00 audit budget)."
            ),
            params={
                "type": "object",
                "properties": {
                    "target_folder": {"type": "string"},
                },
                "required": ["target_folder"],
            },
            handler=lambda target_folder: _tool_js_run_audit(
                kernel, cfg, target_folder,
            ),
            requires=["path_access"],
        ),
        Tool(
            name="js_audit_status",
            description=(
                "Read run row + turn list for a js_run_audit handle. "
                "status ∈ {'running', 'completed', 'failed', "
                "'cap_exceeded'}."
            ),
            params={
                "type": "object",
                "properties": {
                    "run_id": {"type": "string"},
                },
                "required": ["run_id"],
            },
            handler=lambda run_id: _tool_js_audit_status(kernel, run_id),
        ),
    ]
