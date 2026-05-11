"""mock_authz tool — Phase 7D Task 8.

Loads stored response for a (session_id, route) from mock_flow,
runs AuthzFlipper.flip against the running mock server's app, returns
the AuthzFlipResult as JSON.

Requires mock_start to have booted the server first; otherwise returns
an error. Uses the running app from
``kernel.services["mock_backend_servers"]``.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from ..core.authz_flipper import AuthzFlipper
from ..core.stored_flow_replay import StoredFlowReplay


class _NullPage:
    """Page substitute for when no Playwright page is attached.

    AuthzFlipper.flip needs ``page.evaluate`` to read innerHTML and
    ``page.reload``. The tool layer doesn't own a browser; if no page
    is available we still want a deterministic structured response.
    """

    def __init__(self) -> None:
        self.calls: list[str] = []

    def evaluate(self, script: str) -> str:
        self.calls.append(script)
        return ""

    def reload(self, **kw: Any) -> None:
        return None


async def mock_authz_async(
    kernel: Any, session_id: str, route: str, field: str
) -> dict:
    if not session_id or not route or not field:
        return {"error": "session_id, route and field required"}

    db_conn = kernel.services.get("mock_backend_db")
    cfg = kernel.services.get("mock_backend_config")
    if db_conn is None or cfg is None:
        return {"error": "mock_backend not registered"}

    sfr = StoredFlowReplay(cfg.db_path_resolved)
    stored = sfr.get_replay_handler(session_id, route, "GET")
    if stored is None or not isinstance(stored.get("body"), dict):
        return {
            "error": (
                f"no stored flow for {route}. Run /mock-backend probe "
                f"{session_id} first to auto-capture, or "
                f"/mock-backend record {session_id} GET {route} <body> "
                "for manual override."
            )
        }

    reg = kernel.services.get("mock_backend_servers") or {}
    info = reg.get(session_id)
    if info is None:
        return {
            "error": (
                f"server not running for session '{session_id}'. "
                "Run /mock-backend start first."
            )
        }

    page = info.get("page") or _NullPage()
    flipper = AuthzFlipper(info["app"])
    result = await flipper.flip(
        page=page,
        route=route,
        response_body=stored["body"],
        field=field,
    )
    return asdict(result)


def mock_authz_handler(kernel: Any):
    async def _handle(
        session_id: str = "", route: str = "", field: str = ""
    ) -> str:
        payload = await mock_authz_async(kernel, session_id, route, field)
        return json.dumps(payload)

    return _handle
