"""mock_run tool — Phase 7C batch chain confirmation.

Loads every pp_chain for a session from the js_analyzer callgraph DB,
boots one mock server, runs all chains against it, returns aggregate
JSON. Server is booted once and shut down once for the whole run.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from ..core.browser_session import BrowserSession
from ..core.payload_injector import PayloadInjector
from ..core.reporter import get_routes
from .mock_confirm import _flatten_chain, load_chains


async def mock_run_async(kernel: Any, session_id: str) -> dict:
    if not session_id:
        return {"error": "session_id required"}

    db_conn = kernel.services.get("mock_backend_db")
    cfg = kernel.services.get("mock_backend_config")
    cg = kernel.services.get("js_analyzer_callgraph")
    if db_conn is None or cfg is None:
        return {"error": "mock_backend not registered"}
    if cg is None:
        return {"error": "js_analyzer not initialised"}

    chains = load_chains(cg)
    if not chains:
        return {
            "session_id": session_id,
            "total": 0,
            "confirmed": 0,
            "results": [],
        }

    flat_chains = [_flatten_chain(c) for c in chains]
    routes = get_routes(db_conn, session_id)

    progress_fn = getattr(kernel, "report_progress", None)
    total = len(flat_chains)

    def _emit(stage: str, detail: str = "") -> None:
        if callable(progress_fn):
            try:
                progress_fn(stage, detail)
            except Exception:
                pass

    _emit("mock_run.start", f"0/{total}")

    bs = BrowserSession(cfg.db_path_resolved, PayloadInjector())
    results = await bs.run_all_chains(
        session_id=session_id,
        chains=flat_chains,
        route_specs=routes,
        dom_specs=[],
    )

    out = []
    confirmed = 0
    for n, r in enumerate(results, start=1):
        if r.confirmed:
            confirmed += 1
        out.append({
            "chain_id":    r.chain_id,
            "confirmed":   bool(r.confirmed),
            "hits":        [asdict(h) for h in r.hits],
            "probe_value": r.probe_value,
            "server_url":  r.server_url,
        })
        _emit("mock_run.chain", f"{n}/{total}")

    return {
        "session_id": session_id,
        "total":      len(out),
        "confirmed":  confirmed,
        "results":    out,
    }


def mock_run_handler(kernel: Any):
    async def _handle(session_id: str = "") -> str:
        payload = await mock_run_async(kernel, session_id)
        return json.dumps(payload)

    return _handle
