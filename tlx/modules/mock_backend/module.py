"""mock_backend module — Phase 7A wiring.

Exports MODULE = ModuleSpec(...) per the kernel module contract.

Tools:
    mock_extract — pull routes + DOM scaffold from a js_analyzer index.
    mock_export  — serialise routes to OpenAPI 3.1.

Reads from `js_analyzer_callgraph` service. Writes:
    - SQLite at ~/.tlx/mock_backend.db (mock_sessions, mock_routes only).
    - HTML scaffold at ~/.tlx/mock_backend/<session_id>/index.html.
    - OpenAPI at  ~/.tlx/mock_backend/<session_id>/openapi.json.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

import structlog

from kernel.modules import ModuleSpec, RegisteredModule
from kernel.tools import Tool

from .core.dom_scaffolder import build_host_html
from .core.fuzzing_seed_exporter import (
    export_burp_scope,
    export_ffuf,
)
from .core.hidden_endpoint_finder import find_hidden
from .core.openapi_exporter import export_openapi
from .core.reporter import (
    get_routes,
    get_session,
    init_session_db,
    record_routes,
    record_session,
    render_extract_summary,
)
from .core.route_extractor import extract_routes
from .mock_backend_config import MockBackendConfig
from .tools.mock_auth import mock_auth_handler
from .tools.mock_authz import mock_authz_handler
from .tools.mock_confirm import mock_confirm_handler
from .tools.mock_observe import mock_observe_handler
from .tools.mock_probe import mock_probe_handler
from .tools.mock_record import mock_record_handler
from .tools.mock_run import mock_run_handler
from .tools.mock_start import (
    mock_start_handler,
    mock_stop_async,
    mock_stop_handler,
)
from .ui import register_slash_commands

logger = structlog.get_logger(__name__)


def _mock_extract_handler(kernel: Any):
    def _handle(target_dir: str = "") -> str:
        if not target_dir:
            return "[mock_extract] target_dir required"

        cg = kernel.services.get("js_analyzer_callgraph")
        if cg is None:
            return (
                "[mock_extract] js_analyzer not initialised. "
                "Run /js_analyzer <target> first."
            )

        db = kernel.services.get("mock_backend_db")
        cfg = kernel.services.get("mock_backend_config")
        if db is None or cfg is None:
            return "[mock_extract] mock_backend not registered"

        session_id = uuid.uuid4().hex[:12]
        project_root = Path(target_dir).expanduser().resolve()

        routes = extract_routes(cg, project_root)
        scaffolded = build_host_html(cg, project_root)

        workspace = cfg.workspace_dir_resolved / session_id
        workspace.mkdir(parents=True, exist_ok=True)
        html_path = workspace / "index.html"
        html_path.write_text(scaffolded, encoding="utf-8")

        record_session(
            db, session_id, str(getattr(cg, "db_path", "")), str(project_root),
            str(html_path),
        )
        record_routes(db, session_id, routes)

        summary = render_extract_summary(routes)
        return (
            f"session_id: {session_id}\n"
            f"scaffold: {html_path}\n\n{summary}"
        )

    return _handle


def _mock_export_handler(kernel: Any):
    def _handle(
        session_id: str = "",
        format: str = "openapi",
        host: str = "127.0.0.1",
    ) -> str:
        sid = (session_id or "").strip()
        fmt = (format or "openapi").lower()

        db = kernel.services.get("mock_backend_db")
        cfg = kernel.services.get("mock_backend_config")
        if db is None or cfg is None:
            return "[mock_export] mock_backend not registered"

        session = get_session(db, sid)
        if session is None:
            return f"[mock_export] session '{sid}' not found"

        out_dir = cfg.workspace_dir_resolved / sid
        out_dir.mkdir(parents=True, exist_ok=True)

        if fmt == "openapi":
            spec = export_openapi(cfg.db_path_resolved, sid)
            out = out_dir / "openapi.json"
            out.write_text(
                json.dumps(spec, indent=2), encoding="utf-8",
            )
            return f"OpenAPI 3.1 written to {out}"

        if fmt == "ffuf":
            text = export_ffuf(sid, cfg.db_path_resolved)
            out = out_dir / "paths.txt"
            out.write_text(text, encoding="utf-8")
            n = len(text.splitlines()) if text else 0
            return f"ffuf paths ({n}) written to {out}"

        if fmt == "burp":
            xml = export_burp_scope(
                sid, cfg.db_path_resolved, host=host,
            )
            out = out_dir / "scope.xml"
            out.write_text(xml, encoding="utf-8")
            return f"Burp scope (host={host}) written to {out}"

        if fmt == "hidden":
            routes = get_routes(db, sid)
            rows = db.execute(
                "SELECT DISTINCT path FROM mock_requests "
                "WHERE session_id=? AND source IN ('probe', 'confirm')",
                (sid,),
            ).fetchall()
            observed = [r[0] for r in rows if r and r[0]]
            hidden_paths = find_hidden(routes, observed)
            out = out_dir / "hidden.json"
            out.write_text(
                json.dumps(hidden_paths, indent=2),
                encoding="utf-8",
            )
            return (
                f"hidden endpoints ({len(hidden_paths)}) "
                f"written to {out}"
            )

        return (
            f"[mock_export] unknown format '{fmt}'. "
            f"Supported: openapi, ffuf, burp, hidden."
        )

    return _handle


def _build_tools(kernel: Any) -> list[Tool]:
    return [
        Tool(
            name="mock_extract",
            description=(
                "Extract API routes and DOM scaffold from a js_analyzer-"
                "indexed target. No browser, no server — pure data layer. "
                "Returns session_id for use with mock_export and (in later "
                "sessions) mock_start. Requires /js_analyzer <target> to "
                "have run first against the same target."
            ),
            params={
                "type": "object",
                "properties": {
                    "target_dir": {
                        "type": "string",
                        "description": "Path to JS-indexed target.",
                    },
                },
                "required": ["target_dir"],
            },
            handler=_mock_extract_handler(kernel),
        ),
        Tool(
            name="mock_export",
            description=(
                "Export session artifacts. Formats: openapi (writes "
                "openapi.json with x-tlx-summary), ffuf (paths.txt, "
                "newline-separated), burp (scope.xml for Burp Suite "
                "Pro target scope import), hidden (hidden.json — "
                "paths observed via mock_probe but not in extracted "
                "routes). For burp, optional 'host' arg sets the "
                "scope host (default 127.0.0.1; pass the real target "
                "host when exporting for use against production)."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "format": {
                        "type": "string",
                        "enum": ["openapi", "ffuf", "burp", "hidden"],
                    },
                    "host": {
                        "type": "string",
                        "description": (
                            "Burp scope host. Ignored for non-burp "
                            "formats. Default 127.0.0.1."
                        ),
                    },
                },
                "required": ["session_id", "format"],
            },
            handler=_mock_export_handler(kernel),
        ),
        Tool(
            name="mock_confirm",
            description=(
                "Confirm a single js_analyzer pp_chain by booting a mock "
                "server, loading the host HTML in headless Chromium, and "
                "watching CDP/console/network sinks for the probe sentinel. "
                "Returns JSON with chain_id, confirmed, hits, probe_value, "
                "server_url. Requires Playwright Chromium installed "
                "(playwright install chromium)."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "chain_id":   {"type": "string"},
                },
                "required": ["session_id", "chain_id"],
            },
            handler=mock_confirm_handler(kernel),
        ),
        Tool(
            name="mock_run",
            description=(
                "Batch-confirm every pp_chain for a session in a single "
                "mock-server boot. Loads chains from the js_analyzer "
                "callgraph DB, drives Playwright per-chain against one "
                "shared FastAPI instance, and writes mock_findings rows. "
                "Returns JSON with session_id, total, confirmed, and the "
                "per-chain result list."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                },
                "required": ["session_id"],
            },
            handler=mock_run_handler(kernel),
        ),
        Tool(
            name="mock_start",
            description=(
                "Boot the per-session FastAPI mock server on 127.0.0.1 "
                "(port=0 → OS-assigned). Persists the bound port into "
                "mock_sessions.port and keeps the server alive until "
                "mock_stop. Returns JSON with port and url."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "port":       {"type": "integer"},
                },
                "required": ["session_id"],
            },
            handler=mock_start_handler(kernel),
        ),
        Tool(
            name="mock_stop",
            description=(
                "Shutdown the per-session running mock server. Returns "
                "JSON with stopped=true on success."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                },
                "required": ["session_id"],
            },
            handler=mock_stop_handler(kernel),
        ),
        Tool(
            name="mock_authz",
            description=(
                "Mutate a role/flag field in the stored response for "
                "(session_id, route) and reload the running page; "
                "returns AuthzFlipResult JSON with original_value, "
                "flipped_value, and unified DOM diff."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "route":      {"type": "string"},
                    "field":      {"type": "string"},
                },
                "required": ["session_id", "route", "field"],
            },
            handler=mock_authz_handler(kernel),
        ),
        Tool(
            name="mock_auth",
            description=(
                "Run AuthAnalyzer.observe(url) and persist all "
                "observations into mock_auth_obs. Captures localStorage, "
                "sessionStorage, cookies, Authorization/Cookie headers, "
                "and JWT-shaped console strings. Returns JSON with "
                "observations and count."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "url":        {"type": "string"},
                },
                "required": ["session_id", "url"],
            },
            handler=mock_auth_handler(kernel),
        ),
        Tool(
            name="mock_probe",
            description=(
                "Run ExecutionLoop.run() — boot mock server, drive "
                "interactions through Playwright, collect SinkMonitor "
                "hits and observed network URLs not in route_specs. "
                "Pass interactions as JSON-encoded list of "
                "{type, selector, value} dicts. Set auto=true to "
                "enumerate forms + buttons on the page automatically "
                "and fire them with sentinel-injected values; deduped "
                "against user-supplied interactions; capped at 50."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id":        {"type": "string"},
                    "interactions_json": {"type": "string"},
                    "auto": {"type": "boolean", "default": False},
                },
                "required": ["session_id"],
            },
            handler=mock_probe_handler(kernel),
        ),
        Tool(
            name="mock_record",
            description=(
                "Record a stored response into mock_flow. Used by "
                "mock_authz (reads stored GET responses to flip a "
                "field) and as a general-purpose flow-replay primer. "
                "response_body is stored as text; non-JSON bodies are "
                "preserved verbatim. status_code defaults to 200. "
                "Method is upper-cased."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id":    {"type": "string"},
                    "method":        {"type": "string"},
                    "path":          {"type": "string"},
                    "response_body": {"type": "string"},
                    "request_body":  {"type": "string"},
                    "status_code":   {"type": "integer"},
                },
                "required": [
                    "session_id", "method", "path", "response_body",
                ],
            },
            handler=mock_record_handler(kernel),
        ),
        Tool(
            name="mock_observe",
            description=(
                "Observe ServiceWorker registrations and WebSocket "
                "frames for the given URL via Playwright + CDP. "
                "Persists to mock_sw_obs and mock_ws_frames tables. "
                "WebSocket payload snippets truncated at 200 chars. "
                "Returns JSON with sw_observations, ws_frames, "
                "sw_count, ws_count."
            ),
            params={
                "type": "object",
                "properties": {
                    "session_id":  {"type": "string"},
                    "url":         {"type": "string"},
                    "duration_ms": {"type": "integer"},
                },
                "required": ["session_id", "url"],
            },
            handler=mock_observe_handler(kernel),
        ),
    ]


def _shutdown_mock_backend(kernel: Any) -> None:
    """Kernel shutdown hook — stop sessions, stop bg loop, join thread."""
    if kernel.services.get("mock_backend_db") is None:
        logger.warning("mock_backend.shutdown_hook_missing_db")
        return

    reg = kernel.services.get("mock_backend_servers") or {}
    bg_loop = kernel.services.get("mock_backend_bg_loop")
    bg_thread = kernel.services.get("mock_backend_bg_thread")

    sids = list(reg.keys())

    for sid in sids:
        if bg_loop is None or not bg_loop.is_running():
            logger.warning(
                "mock_backend.shutdown_loop_dead",
                session_id=sid,
            )
            continue
        try:
            fut = asyncio.run_coroutine_threadsafe(
                mock_stop_async(kernel, sid), bg_loop,
            )
            fut.result(timeout=5.0)
        except Exception as exc:
            logger.warning(
                "mock_backend.shutdown_session_failed",
                session_id=sid, error=str(exc),
            )

    if bg_loop is not None and bg_loop.is_running():
        try:
            bg_loop.call_soon_threadsafe(bg_loop.stop)
        except Exception:
            pass

    if bg_thread is not None and bg_thread.is_alive():
        try:
            bg_thread.join(timeout=5.0)
        except Exception:
            pass


def _register(kernel: Any, config: Any) -> RegisteredModule:
    cfg = config if isinstance(config, MockBackendConfig) else MockBackendConfig()

    db_path = cfg.db_path_resolved
    db_path.parent.mkdir(parents=True, exist_ok=True)
    workspace = cfg.workspace_dir_resolved
    workspace.mkdir(parents=True, exist_ok=True)

    conn = init_session_db(db_path)
    kernel.services.register("mock_backend_db", conn)
    kernel.services.register("mock_backend_config", cfg)

    tools = _build_tools(kernel)
    for t in tools:
        kernel.tools.register(t)

    register_slash_commands(kernel)

    if hasattr(kernel, "on_shutdown"):
        kernel.on_shutdown(lambda: _shutdown_mock_backend(kernel))

    logger.info("mock_backend.registered", workspace=str(workspace))
    return RegisteredModule(spec=MODULE, tools=tools, config=cfg)


MODULE = ModuleSpec(
    name="mock_backend",
    version="0.1.0",
    requires_kernel=">=0.1.0",
    depends_on=[],
    optional_deps=["js_analyzer"],
    config_schema=MockBackendConfig,
    register_fn=_register,
)
