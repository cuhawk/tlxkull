"""Tests for mock_start Playwright wiring — Phase 7E.3."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
from modules.mock_backend.mock_backend_config import MockBackendConfig
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


async def _async_noop() -> None:
    return None


@pytest.mark.asyncio
async def test_mock_start_uses_factory_when_registered(
    kernel: MagicMock,
) -> None:
    captured_url: list[str] = []
    fake_page = MagicMock()

    async def fake_open(url: str) -> tuple[Any, Any]:
        captured_url.append(url)
        return fake_page, _async_noop

    kernel.services.register("mock_start_open_page", fake_open)

    response = await mock_start_async(kernel, "s1")
    try:
        assert response["page_available"] is True
        assert captured_url[0] == response["url"]
        reg = kernel.services.get("mock_backend_servers")
        assert reg["s1"]["page"] is fake_page
    finally:
        await mock_stop_async(kernel, "s1")


@pytest.mark.asyncio
async def test_mock_start_continues_when_factory_raises(
    kernel: MagicMock,
) -> None:
    async def bad_open(url: str) -> tuple[Any, Any]:
        raise RuntimeError("no chromium")

    kernel.services.register("mock_start_open_page", bad_open)

    response = await mock_start_async(kernel, "s1")
    try:
        assert response["page_available"] is False
        assert response["port"] > 0
        reg = kernel.services.get("mock_backend_servers")
        assert reg["s1"]["page"] is None
        assert reg["s1"]["pw_close"] is None
    finally:
        await mock_stop_async(kernel, "s1")


@pytest.mark.asyncio
async def test_mock_stop_invokes_pw_close(kernel: MagicMock) -> None:
    close_calls: list[int] = []

    async def fake_open(url: str) -> tuple[Any, Any]:
        return MagicMock(), _async_noop

    kernel.services.register("mock_start_open_page", fake_open)
    await mock_start_async(kernel, "s1")
    reg = kernel.services.get("mock_backend_servers")
    reg["s1"]["pw_close"] = lambda: close_calls.append(1)

    out = await mock_stop_async(kernel, "s1")
    assert out["stopped"] is True
    assert close_calls == [1]


@pytest.mark.asyncio
async def test_mock_stop_swallows_pw_close_failure(
    kernel: MagicMock,
) -> None:
    async def fake_open(url: str) -> tuple[Any, Any]:
        return MagicMock(), _async_noop

    kernel.services.register("mock_start_open_page", fake_open)
    await mock_start_async(kernel, "s1")
    reg = kernel.services.get("mock_backend_servers")

    def boom() -> None:
        raise RuntimeError("close failed")

    reg["s1"]["pw_close"] = boom

    out = await mock_stop_async(kernel, "s1")
    assert out["stopped"] is True
