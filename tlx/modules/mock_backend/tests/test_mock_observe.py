"""Tests for mock_observe tool + slash — Phase 7H."""
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
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.tools.mock_observe import mock_observe_async
from modules.mock_backend.ui import _handle_mock_backend


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
        "mock_backend_db", sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


class _FakeCDP:
    def __init__(self) -> None:
        self.handlers: dict[str, list] = {}

    def send(self, method: str, params: Any = None) -> None:
        return None

    def on(self, event: str, handler: Any) -> None:
        self.handlers.setdefault(event, []).append(handler)

    def emit(self, event: str, params: dict) -> None:
        for h in self.handlers.get(event, []):
            h(params)


class _FakeContext:
    def __init__(self, cdp: _FakeCDP) -> None:
        self._cdp = cdp

    def new_cdp_session(self, page: Any) -> _FakeCDP:
        return self._cdp


class _FakePage:
    def __init__(
        self,
        sw_registrations: list[dict] | None = None,
        ws_events: list[tuple[str, dict]] | None = None,
    ) -> None:
        self._cdp = _FakeCDP()
        self.context = _FakeContext(self._cdp)
        self._sw = sw_registrations or []
        self._ws_events = ws_events or []

    def goto(self, url: str, **kw: Any) -> None:
        for ev, params in self._ws_events:
            self._cdp.emit(ev, params)

    def wait_for_timeout(self, ms: int) -> None:
        return None

    def evaluate(self, script: str) -> Any:
        if "navigator.serviceWorker" in script:
            return list(self._sw)
        return None


# ── happy paths ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_observe_returns_sw_and_ws(kernel: MagicMock):
    page = _FakePage(
        sw_registrations=[
            {"scope": "https://app/", "scriptURL": "https://app/sw.js"},
        ],
        ws_events=[
            ("Network.webSocketCreated",
             {"requestId": "r1", "url": "ws://app/socket"}),
            ("Network.webSocketFrameReceived",
             {"requestId": "r1", "response": {"payloadData": "hello"}}),
            ("Network.webSocketFrameSent",
             {"requestId": "r1", "response": {"payloadData": "ping"}}),
        ],
    )
    kernel.services.register("mock_observe_page", page)

    out = await mock_observe_async(kernel, "s1", "http://x/", duration_ms=1)
    assert out["sw_count"] == 1
    assert out["ws_count"] == 2
    assert out["sw_observations"][0]["scope"] == "https://app/"
    dirs = {f["direction"] for f in out["ws_frames"]}
    assert dirs == {"sent", "received"}


@pytest.mark.asyncio
async def test_mock_observe_persists_sw_obs(kernel: MagicMock):
    page = _FakePage(sw_registrations=[
        {"scope": "https://a/", "scriptURL": "https://a/sw.js"},
        {"scope": "https://b/", "scriptURL": "https://b/sw.js"},
    ])
    kernel.services.register("mock_observe_page", page)

    out = await mock_observe_async(kernel, "s1", "http://x/", duration_ms=1)
    assert out["sw_count"] == 2

    cfg = kernel.services.get("mock_backend_config")
    conn = sqlite3.connect(str(cfg.db_path_resolved))
    try:
        n = conn.execute(
            "SELECT COUNT(*) FROM mock_sw_obs WHERE session_id='s1'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert n == 2


@pytest.mark.asyncio
async def test_mock_observe_persists_ws_frames(kernel: MagicMock):
    page = _FakePage(ws_events=[
        ("Network.webSocketCreated",
         {"requestId": "r1", "url": "ws://x/"}),
        ("Network.webSocketFrameSent",
         {"requestId": "r1", "response": {"payloadData": "p"}}),
        ("Network.webSocketFrameReceived",
         {"requestId": "r1", "response": {"payloadData": "q"}}),
    ])
    kernel.services.register("mock_observe_page", page)

    out = await mock_observe_async(kernel, "s1", "http://x/", duration_ms=1)
    assert out["ws_count"] == 2

    cfg = kernel.services.get("mock_backend_config")
    conn = sqlite3.connect(str(cfg.db_path_resolved))
    try:
        rows = conn.execute(
            "SELECT direction FROM mock_ws_frames "
            "WHERE session_id='s1' ORDER BY id"
        ).fetchall()
    finally:
        conn.close()
    assert len(rows) == 2
    assert {r[0] for r in rows} == {"sent", "received"}


@pytest.mark.asyncio
async def test_mock_observe_empty_does_not_error(kernel: MagicMock):
    page = _FakePage()
    kernel.services.register("mock_observe_page", page)

    out = await mock_observe_async(kernel, "s1", "http://x/", duration_ms=1)
    assert out["sw_count"] == 0
    assert out["ws_count"] == 0
    assert "error" not in out


# ── error paths ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_observe_missing_session_id(kernel: MagicMock):
    out = await mock_observe_async(kernel, "", "http://x/")
    assert "error" in out


@pytest.mark.asyncio
async def test_mock_observe_missing_url(kernel: MagicMock):
    out = await mock_observe_async(kernel, "s1", "")
    assert "error" in out


@pytest.mark.asyncio
async def test_mock_observe_unknown_session(kernel: MagicMock):
    out = await mock_observe_async(kernel, "ghost", "http://x/")
    assert "error" in out
    assert "not found" in out["error"]


# ── close-callable invariant ───────────────────────────────────────


@pytest.mark.asyncio
async def test_close_invoked_even_on_observer_exception(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch,
):
    closed = {"n": 0}

    page = _FakePage()
    from modules.mock_backend.tools import mock_observe as mo

    async def _wrapped(k: Any, url: str) -> tuple[Any, Any]:
        async def _close() -> None:
            closed["n"] += 1
        return page, _close

    monkeypatch.setattr(mo, "_open_page", _wrapped)

    from modules.mock_backend.core import sw_ws_observer

    async def _boom(self: Any, url: str, duration_ms: int = 5000) -> Any:
        raise RuntimeError("observer boom")

    monkeypatch.setattr(sw_ws_observer.SWWSObserver, "observe", _boom)

    with pytest.raises(RuntimeError, match="observer boom"):
        await mock_observe_async(kernel, "s1", "http://x/", duration_ms=1)
    assert closed["n"] == 1


# ── slash dispatch ─────────────────────────────────────────────────


def test_observe_slash_dispatches_correctly(kernel: MagicMock):
    page = _FakePage(
        sw_registrations=[{"scope": "https://a/", "scriptURL": "https://a/sw.js"}],
    )
    kernel.services.register("mock_observe_page", page)

    out = _handle_mock_backend(
        ["observe", "s1", "http://x/", "--duration", "1"], kernel,
    )
    assert "sw_count: 1" in out
    assert "ws_count: 0" in out
    assert "https://a/sw.js" in out


def test_observe_slash_missing_args(kernel: MagicMock):
    out = _handle_mock_backend(["observe"], kernel)
    assert "usage:" in out
    out2 = _handle_mock_backend(["observe", "s1"], kernel)
    assert "usage:" in out2


def test_observe_slash_invalid_duration(kernel: MagicMock):
    out = _handle_mock_backend(
        ["observe", "s1", "http://x/", "--duration", "abc"], kernel,
    )
    assert "invalid duration" in out


def test_observe_slash_returns_payload_as_text(kernel: MagicMock):
    page = _FakePage()
    kernel.services.register("mock_observe_page", page)
    out = _handle_mock_backend(
        ["observe", "s1", "http://x/"], kernel,
    )
    # Plain text dump, not JSON.
    assert "sw_count:" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)
