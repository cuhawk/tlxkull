"""Tests for 7E.7 — mock_backend shutdown hook."""
from __future__ import annotations

import asyncio
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.mock_backend import module as mb_module
from modules.mock_backend.core.reporter import record_session
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.module import (
    _register,
    _shutdown_mock_backend,
)
from modules.mock_backend.tools.mock_start import (
    _bg_loop,
    mock_start_async,
)
from modules.mock_backend.tools.mock_start import (
    mock_stop_async as _real_mock_stop_async,
)


class _Services:
    def __init__(self) -> None:
        self._d: dict[str, Any] = {}

    def register(self, name: str, value: Any) -> None:
        self._d[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        return self._d.get(name, default)


def _build_kernel() -> Any:
    k = MagicMock()
    k.services = _Services()
    k.tools = MagicMock()
    k.tools.register = MagicMock()
    pending: list = []
    k.defer_slash_register = lambda cmd: pending.append(cmd)
    k._pending_slash = pending
    k.on_shutdown = MagicMock()
    return k


def _seed_session(db_path: Path, sid: str) -> None:
    conn = sqlite3.connect(str(db_path))
    record_session(conn, sid, "", "")
    conn.close()


def _start_session_on_bg_loop(kernel: Any, sid: str) -> dict:
    loop = _bg_loop(kernel)
    fut = asyncio.run_coroutine_threadsafe(
        mock_start_async(kernel, sid), loop,
    )
    return fut.result(timeout=10.0)


def _wait_thread_dead(t: threading.Thread, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while t.is_alive() and time.time() < deadline:
        time.sleep(0.05)


def test_shutdown_stops_all_active_sessions(tmp_path: Path) -> None:
    kernel = _build_kernel()
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    async def _async_noop() -> None:
        return None

    async def _fake_open(url: str) -> tuple[Any, Any]:
        return MagicMock(), _async_noop

    kernel.services.register("mock_start_open_page", _fake_open)
    db_path = tmp_path / "mb.db"
    _seed_session(db_path, "s1")
    _seed_session(db_path, "s2")

    r1 = _start_session_on_bg_loop(kernel, "s1")
    r2 = _start_session_on_bg_loop(kernel, "s2")
    assert "error" not in r1 and "error" not in r2

    _shutdown_mock_backend(kernel)

    assert kernel.services.get("mock_backend_servers") == {}

    bg_thread = kernel.services.get("mock_backend_bg_thread")
    assert bg_thread is not None
    _wait_thread_dead(bg_thread)
    assert not bg_thread.is_alive()

    conn = sqlite3.connect(str(db_path))
    rows = conn.execute(
        "SELECT id, mode FROM mock_sessions "
        "WHERE id IN ('s1','s2') ORDER BY id"
    ).fetchall()
    conn.close()
    assert len(rows) == 2
    for _, mode in rows:
        assert mode == "stopped"


def test_shutdown_no_op_when_no_servers_started(tmp_path: Path) -> None:
    kernel = _build_kernel()
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    _shutdown_mock_backend(kernel)
    assert kernel.services.get("mock_backend_bg_thread") is None
    assert kernel.services.get("mock_backend_bg_loop") is None


def test_shutdown_continues_when_one_session_stop_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    kernel = _build_kernel()
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    async def _async_noop() -> None:
        return None

    async def _fake_open(url: str) -> tuple[Any, Any]:
        return MagicMock(), _async_noop

    kernel.services.register("mock_start_open_page", _fake_open)
    db_path = tmp_path / "mb.db"
    _seed_session(db_path, "s1")
    _seed_session(db_path, "s2")

    _start_session_on_bg_loop(kernel, "s1")
    _start_session_on_bg_loop(kernel, "s2")

    async def flaky_stop(k: Any, sid: str) -> dict:
        if sid == "s1":
            raise RuntimeError("boom")
        return await _real_mock_stop_async(k, sid)

    monkeypatch.setattr(mb_module, "mock_stop_async", flaky_stop)

    _shutdown_mock_backend(kernel)

    reg = kernel.services.get("mock_backend_servers")
    assert reg is not None
    assert reg.get("s2") is None

    bg_loop = kernel.services.get("mock_backend_bg_loop")
    bg_thread = kernel.services.get("mock_backend_bg_thread")
    assert bg_loop is not None and not bg_loop.is_running()
    assert bg_thread is not None
    _wait_thread_dead(bg_thread)
    assert not bg_thread.is_alive()


def test_register_installs_shutdown_hook(tmp_path: Path) -> None:
    kernel = _build_kernel()
    installed: list = []
    kernel.on_shutdown = lambda cb: installed.append(cb)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    assert len(installed) == 1
    installed[0]()


def test_register_skips_hook_when_kernel_lacks_on_shutdown(
    tmp_path: Path,
) -> None:
    class _MiniKernel:
        def __init__(self) -> None:
            self.services = _Services()
            self.tools = MagicMock()
            self.tools.register = MagicMock()
            self._pending_slash: list = []

        def defer_slash_register(self, cmd: Any) -> None:
            self._pending_slash.append(cmd)

    kernel = _MiniKernel()
    assert not hasattr(kernel, "on_shutdown")
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)


def test_shutdown_hook_returns_cleanly_when_db_service_missing() -> None:
    class _MiniKernel:
        def __init__(self) -> None:
            self.services = _Services()

    kernel = _MiniKernel()
    _shutdown_mock_backend(kernel)
    assert kernel.services.get("mock_backend_bg_thread") is None
