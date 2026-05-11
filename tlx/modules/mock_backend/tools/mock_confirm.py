"""mock_confirm tool — Phase 7B chain confirmation entry point.

Loads a chain by id from the js_analyzer callgraph, builds a probe via
PayloadInjector, runs BrowserSession.confirm_chain (which boots the
mock server, observes via Playwright, writes mock_findings).

Input:  session_id, chain_id
Output: JSON string with chain_id, confirmed, hits, probe_value, server_url.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..core.browser_session import BrowserSession
from ..core.payload_injector import PayloadInjector
from ..core.reporter import get_routes


def _flatten_chain(chain: dict) -> dict:
    """Adapt a pp_chains chain dict to the flat shape PayloadInjector expects."""
    src = chain.get("source") or {}
    sink = chain.get("sink") or {}
    return {
        "chain_id": str(chain.get("id") or chain.get("chain_id") or ""),
        "id": chain.get("id"),
        "source_qname": src.get("qname") or chain.get("source_qname") or "",
        "source_line":  src.get("line")  or chain.get("source_line")  or 0,
        "sink_type":    sink.get("taxonomy_id") or chain.get("sink_type") or "",
        "sink_qname":   sink.get("qname")  or chain.get("sink_qname")  or "",
        "raw":          chain,
    }


def load_chains(cg: Any) -> list[dict]:
    """Pull pp_chains from callgraph without importing js_analyzer at module load.

    The js_analyzer ports are kept on sys.path by its own register-time shim;
    we only consult pp_chains lazily here.
    """
    if cg is None or not hasattr(cg, "conn"):
        return []
    try:
        ja_dir = Path(__file__).resolve().parents[2] / "js_analyzer"
        if str(ja_dir) not in sys.path:
            sys.path.insert(0, str(ja_dir))
        from pp_chains import find_pp_chains  # type: ignore[import-not-found]
        return find_pp_chains(cg.conn)
    except Exception:
        return []


def find_chain_by_id(chains: list[dict], chain_id: str) -> dict | None:
    cid = str(chain_id).strip()
    for c in chains:
        if str(c.get("id")) == cid or str(c.get("chain_id")) == cid:
            return c
    return None


async def mock_confirm_async(
    kernel: Any, session_id: str, chain_id: str
) -> dict:
    if not session_id or not chain_id:
        return {"error": "session_id and chain_id required"}

    db_conn = kernel.services.get("mock_backend_db")
    cfg = kernel.services.get("mock_backend_config")
    cg = kernel.services.get("js_analyzer_callgraph")
    if db_conn is None or cfg is None:
        return {"error": "mock_backend not registered"}
    if cg is None:
        return {"error": "js_analyzer not initialised"}

    chains = load_chains(cg)
    chain = find_chain_by_id(chains, chain_id)
    if chain is None:
        return {"error": f"chain '{chain_id}' not found"}

    flat = _flatten_chain(chain)
    routes = get_routes(db_conn, session_id)

    bs = BrowserSession(cfg.db_path_resolved, PayloadInjector())
    result = await bs.confirm_chain(
        session_id=session_id,
        chain=flat,
        route_specs=routes,
        dom_specs=[],
    )
    return {
        "chain_id":    result.chain_id,
        "confirmed":   bool(result.confirmed),
        "hits":        [asdict(h) for h in result.hits],
        "probe_value": result.probe_value,
        "server_url":  result.server_url,
    }


def mock_confirm_handler(kernel: Any):
    async def _handle(session_id: str = "", chain_id: str = "") -> str:
        payload = await mock_confirm_async(kernel, session_id, chain_id)
        return json.dumps(payload)

    return _handle
