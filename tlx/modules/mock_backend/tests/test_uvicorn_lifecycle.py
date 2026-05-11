"""Tests for core/uvicorn_lifecycle.py — Phase 7G."""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from modules.mock_backend.core import uvicorn_lifecycle


class _FakeSocket:
    def __init__(self, port: int) -> None:
        self._port = port

    def getsockname(self) -> tuple[str, int]:
        return ("127.0.0.1", self._port)


class _FakeInnerServer:
    def __init__(self, port: int) -> None:
        self.sockets = [_FakeSocket(port)]


class _FakeServer:
    """Fake uvicorn.Server that flips ``started`` after a short delay."""

    def __init__(
        self,
        config: Any,
        *,
        start_after: float = 0.0,
        will_start: bool = True,
        bound_port: int = 12345,
    ) -> None:
        self.config = config
        self.started = False
        self.should_exit = False
        self.servers = [_FakeInnerServer(bound_port)] if will_start else []
        self._start_after = start_after
        self._will_start = will_start

    async def serve(self) -> None:
        if self._will_start:
            await asyncio.sleep(self._start_after)
            self.started = True
        # Run until should_exit flips.
        while not self.should_exit:
            await asyncio.sleep(0.01)


class _FakeConfig:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs


def _patch_uvicorn(monkeypatch: pytest.MonkeyPatch, server_factory: Any) -> dict:
    """Replace uvicorn.Config and uvicorn.Server. Returns capture dict."""
    captured: dict[str, Any] = {}

    def _config(*args: Any, **kwargs: Any) -> _FakeConfig:
        cfg = _FakeConfig(*args, **kwargs)
        captured["config"] = cfg
        return cfg

    def _server(config: Any) -> Any:
        srv = server_factory(config)
        captured["server"] = srv
        return srv

    import uvicorn
    monkeypatch.setattr(uvicorn, "Config", _config)
    monkeypatch.setattr(uvicorn, "Server", _server)
    return captured


@pytest.mark.asyncio
async def test_boot_app_returns_server_task_port_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cap = _patch_uvicorn(
        monkeypatch,
        lambda cfg: _FakeServer(cfg, bound_port=54321),
    )
    server, task, port = await uvicorn_lifecycle.boot_app(
        object(), poll_iterations=10, poll_interval=0.01,
    )
    assert server is cap["server"]
    assert isinstance(task, asyncio.Task)
    assert port == 54321
    await uvicorn_lifecycle.shutdown(server, task)


@pytest.mark.asyncio
async def test_boot_app_returns_none_when_server_fails_to_start(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_uvicorn(
        monkeypatch,
        lambda cfg: _FakeServer(cfg, will_start=False),
    )
    server, task, port = await uvicorn_lifecycle.boot_app(
        object(), poll_iterations=3, poll_interval=0.01,
    )
    assert server is None
    assert task is None
    assert port == 0


@pytest.mark.asyncio
async def test_shutdown_idempotent_on_none_inputs() -> None:
    await uvicorn_lifecycle.shutdown(None, None)
    await uvicorn_lifecycle.shutdown(None, asyncio.create_task(asyncio.sleep(0)))
    fake = _FakeServer(object())
    await uvicorn_lifecycle.shutdown(fake, None)


@pytest.mark.asyncio
async def test_shutdown_cancels_task_on_timeout() -> None:
    async def _hang() -> None:
        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            raise

    class _ServerStub:
        should_exit = False

    server = _ServerStub()
    task = asyncio.create_task(_hang())
    await uvicorn_lifecycle.shutdown(server, task, timeout=0.05)
    assert server.should_exit is True
    # Give the cancellation a moment to land.
    await asyncio.sleep(0.01)
    assert task.cancelled() or task.done()


@pytest.mark.asyncio
async def test_boot_app_kwargs_flow_through_to_uvicorn_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cap = _patch_uvicorn(
        monkeypatch,
        lambda cfg: _FakeServer(cfg, bound_port=9999),
    )
    server, task, _ = await uvicorn_lifecycle.boot_app(
        "some-app",
        host="0.0.0.0",
        port=8080,
        log_level="warning",
        access_log=True,
        lifespan="on",
        poll_iterations=10, poll_interval=0.01,
    )
    cfg = cap["config"]
    assert cfg.args[0] == "some-app"
    assert cfg.kwargs["host"] == "0.0.0.0"
    assert cfg.kwargs["port"] == 8080
    assert cfg.kwargs["log_level"] == "warning"
    assert cfg.kwargs["access_log"] is True
    assert cfg.kwargs["lifespan"] == "on"
    await uvicorn_lifecycle.shutdown(server, task)
