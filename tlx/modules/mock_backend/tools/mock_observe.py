"""mock_observe tool — wire SWWSObserver to a tool + slash.

Boots Playwright via core.pw_session.open_page, runs SWWSObserver
against url for duration_ms, persists observations into mock_sw_obs
and mock_ws_frames. Test injection via
``kernel.services["mock_observe_page"]`` (mirrors mock_auth_page).
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from ..core import pw_session
from ..core.reporter import (
    _open_conn,
    get_session,
    record_sw_observations,
    record_ws_frames,
)
from ..core.sw_ws_observer import SWWSObserver


async def _open_page(kernel: Any, url: str) -> tuple[Any, Any]:
    fake = kernel.services.get("mock_observe_page")
    if fake is not None:
        async def _noop() -> None:
            return None
        return fake, _noop

    return await pw_session.open_page(
        url, wait_until="load", timeout_ms=10_000,
    )


async def mock_observe_async(
    kernel: Any,
    session_id: str,
    url: str,
    duration_ms: int = 5000,
) -> dict:
    if not session_id or not url:
        return {"error": "session_id and url required"}

    cfg = kernel.services.get("mock_backend_config")
    db_conn = kernel.services.get("mock_backend_db")
    if cfg is None or db_conn is None:
        return {"error": "mock_backend not registered"}

    if get_session(db_conn, session_id) is None:
        return {"error": f"session '{session_id}' not found"}

    page, close_async = await _open_page(kernel, url)
    try:
        observer = SWWSObserver(page)
        sw, ws = await observer.observe(url, duration_ms)
    finally:
        try:
            await close_async()
        except Exception:
            pass

    persist_conn = _open_conn(cfg.db_path_resolved)
    try:
        record_sw_observations(persist_conn, session_id, sw)
        record_ws_frames(persist_conn, session_id, ws)
    finally:
        persist_conn.close()

    return {
        "sw_observations": [asdict(o) for o in sw],
        "ws_frames": [asdict(f) for f in ws],
        "sw_count": len(sw),
        "ws_count": len(ws),
    }


def mock_observe_handler(kernel: Any):
    async def _handle(
        session_id: str = "", url: str = "", duration_ms: int = 5000,
    ) -> str:
        payload = await mock_observe_async(
            kernel, session_id, url, duration_ms,
        )
        return json.dumps(payload)

    return _handle
