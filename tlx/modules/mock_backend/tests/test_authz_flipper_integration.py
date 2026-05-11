"""Integration test for Phase 7E.3.

Proves mock_authz produces a non-empty UI diff when mock_start wires
a real (fake) Playwright page into the registry. Without 7E.3,
mock_authz fell through to _NullPage and always returned an empty
diff.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
from modules.mock_backend.core.stored_flow_replay import StoredFlowReplay
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.tools.mock_authz import mock_authz_async
from modules.mock_backend.tools.mock_start import (
    mock_start_async,
    mock_stop_async,
)


class _Services:
    def __init__(self) -> None:
        self._reg: dict[str, Any] = {}

    def register(self, name: str, value: Any) -> None:
        self._reg[name] = value

    def get(self, name: str) -> Any:
        return self._reg.get(name)


@pytest.fixture()
def kernel(tmp_path: Path) -> MagicMock:
    db = tmp_path / "mb.db"
    init_session_db(db).close()
    cfg = MockBackendConfig(
        db_path=str(db), workspace_dir=str(tmp_path / "ws"),
    )
    (tmp_path / "ws").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    record_session(conn, "s1", "/cg.db", "/proj")
    conn.close()

    k = MagicMock()
    k.services = _Services()
    k.services.register(
        "mock_backend_db",
        sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


class _RoleAwarePage:
    """Fake page whose innerHTML reflects whether AuthzFlipper has
    set an override entry for self.route on the live FastAPI app.

    Before override: HTML embeds the originally-stored role
    ("viewer"). After override (which AuthzFlipper writes into
    ``app.state._authz_overrides`` before calling page.reload): HTML
    embeds the flipped role ("admin").
    """

    def __init__(self, route: str, original_role: str) -> None:
        self.route = route
        self.original_role = original_role
        self.app: Any = None
        self._html = self._render(original_role)

    @staticmethod
    def _render(role: str) -> str:
        return (
            f"<html><body>"
            f"<div id='role'>{role}</div>"
            f"</body></html>"
        )

    def _has_override(self) -> bool:
        if self.app is None:
            return False
        overrides = getattr(self.app.state, "_authz_overrides", None)
        if not overrides:
            return False
        return any(path == self.route for (_method, path) in overrides)

    def goto(self, url: str, **kwargs: Any) -> None:
        return None

    def reload(self, **kwargs: Any) -> None:
        role = "admin" if self._has_override() else self.original_role
        self._html = self._render(role)

    def evaluate(self, script: str) -> str:
        return self._html

    def content(self) -> str:
        return self._html


@pytest.mark.asyncio
async def test_mock_authz_produces_nonempty_diff_when_role_flips(
    kernel: MagicMock,
) -> None:
    cfg = kernel.services.get("mock_backend_config")
    replay = StoredFlowReplay(cfg.db_path_resolved)
    replay.record(
        "s1", "GET", "/api/me", None, json.dumps({"role": "viewer"}),
    )

    page = _RoleAwarePage(route="/api/me", original_role="viewer")

    async def _async_noop() -> None:
        return None

    async def fake_open(url: str) -> tuple[Any, Any]:
        return page, _async_noop

    kernel.services.register("mock_start_open_page", fake_open)

    start = await mock_start_async(kernel, "s1")
    assert start["page_available"] is True

    reg = kernel.services.get("mock_backend_servers")
    page.app = reg["s1"]["app"]

    try:
        result = await mock_authz_async(
            kernel, "s1", "/api/me", "role",
        )
    finally:
        await mock_stop_async(kernel, "s1")

    assert result["original_value"] == "viewer"
    assert result["flipped_value"] == "admin"
    diff = result["ui_diff"]
    assert diff != ""
    assert "viewer" in diff
    assert "admin" in diff
