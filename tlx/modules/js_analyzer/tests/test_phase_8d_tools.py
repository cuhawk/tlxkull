"""Phase 8D — js_analyzer MCP-facing tool wrappers + allowlist."""
from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kernel.tools import ToolRegistry
from mcp_server.allowlist import TOOL_ALLOWLIST
from modules.js_analyzer.callgraph import CallGraph
from modules.js_analyzer.module import JsAnalyzerConfig
from modules.js_analyzer.tools_extra import make_extra_tools

# ---------- helpers ----------

def _kernel(tmp_path: Path, sandbox_ok: bool = True) -> tuple[MagicMock, CallGraph]:
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))  # noqa: F841
    cg = CallGraph(tmp_path / "cg.db")

    kernel = MagicMock()
    services = {"js_analyzer_callgraph": cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.sandbox.is_allowed.return_value = sandbox_ok
    kernel.session_id = "test-session"
    kernel.tools = ToolRegistry()
    return kernel, cg


def _stub_extractor():
    class _StubExtractor:
        ready = True
        reason = ""
        def __init__(self, *a, **kw): pass  # noqa: E701
        def set_frameworks(self, fw): pass  # noqa: E701
        def extract(self, files): return {}  # noqa: E701
    return _StubExtractor


# ---------- allowlist ----------

def test_allowlist_size_is_16():
    assert len(TOOL_ALLOWLIST) == 16


def test_allowlist_contains_phase_8d_wrappers():
    expected = {
        "js_index_target", "js_get_chains", "js_examine_chain",
        "js_get_snippet", "js_submit_finding", "js_export_findings",
        "js_run_audit", "js_audit_status",
        "mock_extract", "mock_start", "mock_stop", "mock_confirm",
        "mock_run", "mock_export",
        "docs_query", "session_kv_get",
    }
    assert TOOL_ALLOWLIST == frozenset(expected)


# ---------- js_index_target ----------

def test_js_index_target_returns_structured_payload(tmp_path):
    """Returns JSON with the expected key set."""
    (tmp_path / "package.json").write_text(
        '{"dependencies": {"vue": "^3.0.0"}}', encoding="utf-8"
    )
    (tmp_path / "app.js").write_text("const x = 1;", encoding="utf-8")

    kernel, cg = _kernel(tmp_path)
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    tools = make_extra_tools(kernel, cfg)
    by_name = {t.name: t for t in tools}

    with patch("modules.js_analyzer.ast_bridge.ASTExtractor", _stub_extractor()):
        out = by_name["js_index_target"].handler(target_folder=str(tmp_path))
    cg.close()

    payload = json.loads(out)
    assert "error" not in payload
    expected_keys = {
        "target", "nodes", "edges", "tags", "frameworks", "itp",
        "cached_unchanged", "files_total",
    }
    assert expected_keys.issubset(payload.keys())
    assert isinstance(payload["nodes"], int)
    assert isinstance(payload["edges"], int)
    assert isinstance(payload["tags"], int)
    assert isinstance(payload["frameworks"], list)
    assert "vue" in payload["frameworks"]
    assert payload["itp"] == {"arg_edges": payload["itp"]["arg_edges"],
                              "flows": payload["itp"]["flows"]}
    assert "arg_edges" in payload["itp"]
    assert "flows" in payload["itp"]


def test_js_index_target_blocks_outside_sandbox(tmp_path):
    kernel, cg = _kernel(tmp_path, sandbox_ok=False)
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    tools = make_extra_tools(kernel, cfg)
    by_name = {t.name: t for t in tools}

    out = by_name["js_index_target"].handler(target_folder=str(tmp_path))
    cg.close()
    payload = json.loads(out)
    assert "error" in payload
    assert "outside sandbox" in payload["error"]


# ---------- js_get_chains ----------

def test_js_get_chains_matches_extract_findings(tmp_path):
    """Tool result == reporter.extract_findings() output, capped at max_chains."""
    from modules.js_analyzer import reporter

    kernel, cg = _kernel(tmp_path)
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    tools = make_extra_tools(kernel, cfg)
    by_name = {t.name: t for t in tools}

    fake = {
        "target_folder": str(tmp_path),
        "index_stats": {"nodes": 5, "edges": 4, "tags": 3},
        "chains": [
            {"id": i, "path": [f"f.js::fn{i}"], "score": 90 - i,
             "source": {}, "sink": {}}
            for i in range(30)
        ],
        "snippets": {f"f.js::fn{i}": f"// fn{i}" for i in range(30)},
    }

    with patch.object(reporter, "extract_findings", return_value=fake):
        out = by_name["js_get_chains"].handler(
            target_folder=str(tmp_path), max_chains=5,
        )
    cg.close()

    payload = json.loads(out)
    assert payload["target_folder"] == str(tmp_path)
    assert payload["index_stats"] == fake["index_stats"]
    assert len(payload["chains"]) == 5
    assert [c["id"] for c in payload["chains"]] == [0, 1, 2, 3, 4]
    # snippets pruned to qnames in returned chains only
    expected_snips = {f"f.js::fn{i}" for i in range(5)}
    assert set(payload["snippets"].keys()) == expected_snips


def test_js_get_chains_no_findings_returns_empty_list(tmp_path):
    from modules.js_analyzer import reporter

    kernel, cg = _kernel(tmp_path)
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    tools = make_extra_tools(kernel, cfg)
    by_name = {t.name: t for t in tools}

    with patch.object(reporter, "extract_findings", return_value=None):
        out = by_name["js_get_chains"].handler(target_folder=str(tmp_path))
    cg.close()
    payload = json.loads(out)
    assert payload["chains"] == []
    assert "index_stats" in payload


# ---------- js_run_audit ----------

@pytest.mark.asyncio
async def test_js_run_audit_returns_run_id_within_100ms(tmp_path):
    """Inserts row with status='running' + uuid external_run_id; returns within 100ms."""
    from modules.js_analyzer import claude_agent, reporter

    kernel, cg = _kernel(tmp_path)
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    tools = make_extra_tools(kernel, cfg)
    by_name = {t.name: t for t in tools}

    fake_findings = {
        "target_folder": str(tmp_path),
        "index_stats": {"nodes": 1, "edges": 0, "tags": 0},
        "chains": [],
        "snippets": {},
    }

    async def _fake_audit(findings, kern, *, external_run_id=None):
        # Block long enough that the test sees status='running'.
        await asyncio.sleep(2.0)
        return "done"

    with patch.object(reporter, "extract_findings", return_value=fake_findings), \
         patch.object(claude_agent, "analyse_chains_async", _fake_audit):
        t0 = time.monotonic()
        out = by_name["js_run_audit"].handler(target_folder=str(tmp_path))
        elapsed = time.monotonic() - t0

    payload = json.loads(out)
    run_id = payload["run_id"]
    assert isinstance(run_id, str) and len(run_id) >= 16
    assert payload["status"] == "running"
    assert elapsed < 0.1, f"js_run_audit took {elapsed:.3f}s (>100ms)"

    # DB row exists with status='running' and matching external_run_id.
    conn = sqlite3.connect(str(cg.db_path))
    try:
        row = conn.execute(
            "SELECT status, external_run_id FROM js_audit_runs "
            "WHERE external_run_id=?",
            (run_id,),
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0] == "running"
    assert row[1] == run_id

    # let the bg task finish so pytest doesn't warn about pending tasks
    await asyncio.sleep(0)
    pending = [t for t in asyncio.all_tasks() if not t.done()
               and t is not asyncio.current_task()]
    for t in pending:
        t.cancel()
    for t in pending:
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass
    cg.close()


# ---------- js_audit_status ----------

@pytest.mark.asyncio
async def test_js_audit_status_reflects_lifecycle(tmp_path):
    """status='running' immediately, transitions to 'completed' after task finishes."""
    from modules.js_analyzer import claude_agent, reporter
    from modules.js_analyzer.audit_persistence import AuditRun, _open_conn

    kernel, cg = _kernel(tmp_path)
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    tools = make_extra_tools(kernel, cfg)
    by_name = {t.name: t for t in tools}

    fake_findings = {
        "target_folder": str(tmp_path),
        "index_stats": {"nodes": 1, "edges": 0, "tags": 0},
        "chains": [],
        "snippets": {},
    }

    finished = asyncio.Event()

    async def _fake_audit(findings, kern, *, external_run_id=None):
        # Attach to existing row, append a turn, finish('completed').
        conn = _open_conn(cg.db_path)
        try:
            run = AuditRun(
                conn,
                shell_session_id="test-session",
                target_folder=str(tmp_path),
                external_run_id=external_run_id,
            )
            run.start()
            run.append_turn("user", "hello", tokens_in=10, tokens_out=0)
            run.append_turn("assistant", "ok", tokens_in=0, tokens_out=5,
                            cost_usd=0.01)
            run.finish("completed", total_tokens=15, cost_usd=0.01,
                       consults_used=0, consults_cost_usd=0.0)
        finally:
            conn.close()
        finished.set()
        return "done"

    with patch.object(reporter, "extract_findings", return_value=fake_findings), \
         patch.object(claude_agent, "analyse_chains_async", _fake_audit):
        out = by_name["js_run_audit"].handler(target_folder=str(tmp_path))

    run_id = json.loads(out)["run_id"]

    # Immediate status: running (the bg task hasn't finished yet because we
    # haven't yielded long enough, but even if it did, the row was inserted
    # synchronously with status='running').
    status_now = json.loads(by_name["js_audit_status"].handler(run_id=run_id))
    assert status_now["status"] in {"running", "completed"}
    assert status_now["run_id"] == run_id

    # Wait for completion.
    await asyncio.wait_for(finished.wait(), timeout=5.0)
    # Yield control so the bg task can finalize anything else.
    for _ in range(5):
        await asyncio.sleep(0)

    after = json.loads(by_name["js_audit_status"].handler(run_id=run_id))
    assert after["status"] == "completed"
    assert after["total_tokens"] == 15
    assert after["cost_usd"] == pytest.approx(0.01)
    assert len(after["turns"]) == 2
    assert [t["role"] for t in after["turns"]] == ["user", "assistant"]
    cg.close()


def test_js_audit_status_unknown_run_id(tmp_path):
    kernel, cg = _kernel(tmp_path)
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    tools = make_extra_tools(kernel, cfg)
    by_name = {t.name: t for t in tools}

    out = by_name["js_audit_status"].handler(run_id="nonexistent-uuid")
    cg.close()
    payload = json.loads(out)
    assert "error" in payload
    assert "nonexistent-uuid" in payload["error"]


# ---------- /js_analyzer slash dispatches through tool ----------

def test_slash_dispatches_through_js_index_target_tool(tmp_path):
    """/js_analyzer slash MUST call kernel.tools.dispatch('js_index_target', ...)."""
    from modules.js_analyzer.module import _slash_js_analyzer

    (tmp_path / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")

    kernel = MagicMock()
    services = {"js_analyzer_callgraph": cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.sandbox.is_allowed.return_value = True
    kernel.sandbox.list_roots.return_value = []

    captured = {}

    async def _fake_dispatch(name, args):
        captured["name"] = name
        captured["args"] = dict(args)
        # Return an empty success payload so _format_index_summary can render it.
        return json.dumps({
            "target": str(tmp_path),
            "nodes": 0, "edges": 0, "tags": 0,
            "frameworks": [],
            "itp": {"arg_edges": 0, "flows": 0},
            "cached_unchanged": 0,
            "files_total": 1,
        })

    kernel.tools.dispatch = _fake_dispatch

    out = asyncio.run(_slash_js_analyzer(str(tmp_path), kernel, cfg))
    cg.close()

    assert captured["name"] == "js_index_target"
    assert captured["args"] == {"target_folder": str(tmp_path)}
    assert "frameworks:" in out
    assert "js_analyzer indexed" in out
