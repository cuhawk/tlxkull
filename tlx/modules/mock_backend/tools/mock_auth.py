"""mock_auth tool — Phase 7D Task 8.

Runs AuthAnalyzer.observe against a URL using a fresh Playwright page,
persists every AuthObservation into mock_auth_obs, and returns the
list as JSON.

Tests substitute a fake page via ``kernel.services["mock_auth_page"]``
to avoid launching real Chromium.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from ..core import pw_session
from ..core.auth_analyzer import AuthAnalyzer, record_auth_observations
from ..core.reporter import _open_conn


async def _open_page(kernel: Any) -> tuple[Any, Any]:
    """Return (page, cleanup_callable). cleanup_callable is async.

    Live path delegates to ``pw_session.open_page("about:blank")`` —
    ``AuthAnalyzer.observe`` performs its own ``page.goto`` against the
    real URL, so the initial blank navigation is intentional.
    """
    fake = kernel.services.get("mock_auth_page")
    if fake is not None:
        async def _noop() -> None:
            return None
        return fake, _noop

    return await pw_session.open_page("about:blank")


async def mock_auth_async(
    kernel: Any, session_id: str, url: str
) -> dict:
    if not session_id or not url:
        return {"error": "session_id and url required"}

    cfg = kernel.services.get("mock_backend_config")
    db_conn = kernel.services.get("mock_backend_db")
    if cfg is None or db_conn is None:
        return {"error": "mock_backend not registered"}

    page, cleanup = await _open_page(kernel)
    try:
        analyzer = AuthAnalyzer(page)
        observations = await analyzer.observe(url)
    finally:
        try:
            await cleanup()
        except Exception:
            pass

    persist_conn = _open_conn(cfg.db_path_resolved)
    try:
        record_auth_observations(persist_conn, session_id, observations)
    finally:
        persist_conn.close()

    return {
        "observations": [asdict(o) for o in observations],
        "count": len(observations),
    }


def mock_auth_handler(kernel: Any):
    async def _handle(session_id: str = "", url: str = "") -> str:
        payload = await mock_auth_async(kernel, session_id, url)
        return json.dumps(payload)

    return _handle
