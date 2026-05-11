"""mock_probe tool — Phase 7D Task 9 helper.

Runs ExecutionLoop.run() against a session. Used by /mock-backend probe.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from ..core.execution_loop import ExecutionLoop
from ..core.interaction_driver import KNOWN_INTERACTION_KINDS
from ..core.payload_injector import PayloadInjector
from ..core.reporter import get_routes
from ..core.sink_monitor import SinkMonitor


async def mock_probe_async(
    kernel: Any,
    session_id: str,
    interactions: list[dict] | None = None,
    auto: bool = False,
) -> dict:
    if not session_id:
        return {"error": "session_id required"}

    db_conn = kernel.services.get("mock_backend_db")
    cfg = kernel.services.get("mock_backend_config")
    if db_conn is None or cfg is None:
        return {"error": "mock_backend not registered"}

    routes = get_routes(db_conn, session_id)
    injector = PayloadInjector()
    sentinel = injector.sentinel_for(session_id)
    monitor = SinkMonitor(sentinel=sentinel, timeout_ms=2000)

    loop = ExecutionLoop(cfg.db_path_resolved, injector, monitor)

    valid: list[dict] = []
    invalid: list[dict] = []
    for spec in (interactions or []):
        if not isinstance(spec, dict):
            invalid.append({"reason": "not a dict", "value": spec})
            continue
        kind = (spec.get("type") or "").lower()
        if kind in KNOWN_INTERACTION_KINDS:
            valid.append(spec)
        else:
            invalid.append(spec)

    result = await loop.run(
        session_id=session_id,
        route_specs=routes,
        dom_specs=[],
        interactions=valid,
        auto_explore=auto,
    )
    return {
        "url": result.url,
        "interactions": [asdict(e) for e in result.interactions],
        "sink_hits": [asdict(h) for h in result.sink_hits],
        "new_routes": list(result.new_routes),
        "interactions_fired": len(result.interactions),
        "sink_hits_count": len(result.sink_hits),
        "new_routes_count": len(result.new_routes),
        "unknown_interactions": invalid,
        "unknown_interactions_count": len(invalid),
        "auto_explored": result.auto_explored,
        "auto_added_count": result.auto_added_count,
    }


def mock_probe_handler(kernel: Any):
    async def _handle(
        session_id: str = "",
        interactions_json: str = "",
        auto: bool = False,
    ) -> str:
        try:
            interactions = (
                json.loads(interactions_json) if interactions_json else []
            )
        except json.JSONDecodeError:
            interactions = []
        if not isinstance(interactions, list):
            interactions = []
        payload = await mock_probe_async(
            kernel, session_id, interactions, auto=auto,
        )
        return json.dumps(payload)

    return _handle
