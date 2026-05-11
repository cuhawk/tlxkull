"""Tests for SWWSObserver — Phase 7D Task 6."""
from __future__ import annotations

from typing import Any

import pytest

from modules.mock_backend.core.sw_ws_observer import (
    SWObservation,
    SWWSObserver,
)


class _FakeCDP:
    def __init__(self) -> None:
        self.handlers: dict[str, list] = {}
        self.sent: list[str] = []

    def send(self, method: str, params: Any = None) -> None:
        self.sent.append(method)

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
        cdp: _FakeCDP,
        sw_registrations: list[dict] | None = None,
        ws_events: list[tuple[str, dict]] | None = None,
    ) -> None:
        self.context = _FakeContext(cdp)
        self._sw = sw_registrations or []
        self._cdp = cdp
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


@pytest.mark.asyncio
async def test_observe_returns_tuple_of_two_lists():
    cdp = _FakeCDP()
    page = _FakePage(cdp)
    obs = SWWSObserver(page)
    sw, ws = await obs.observe("http://x/", duration_ms=1)
    assert isinstance(sw, list)
    assert isinstance(ws, list)


@pytest.mark.asyncio
async def test_sw_registration_parsed_into_swobservation():
    cdp = _FakeCDP()
    page = _FakePage(cdp, sw_registrations=[
        {"scope": "https://app/", "scriptURL": "https://app/sw.js"},
    ])
    obs = SWWSObserver(page)
    sw, _ = await obs.observe("http://x/", duration_ms=1)
    assert sw == [SWObservation(
        scope="https://app/", script_url="https://app/sw.js",
    )]


@pytest.mark.asyncio
async def test_ws_frame_captured_with_direction_and_snippet():
    cdp = _FakeCDP()
    page = _FakePage(cdp, ws_events=[
        ("Network.webSocketCreated",
         {"requestId": "r1", "url": "ws://app/socket"}),
        ("Network.webSocketFrameReceived",
         {"requestId": "r1", "response": {"payloadData": "hello"}}),
        ("Network.webSocketFrameSent",
         {"requestId": "r1", "response": {"payloadData": "ping"}}),
    ])
    obs = SWWSObserver(page)
    sw, ws = await obs.observe("http://x/", duration_ms=1)
    assert any(f.direction == "received" and f.payload_snippet == "hello"
               for f in ws)
    assert any(f.direction == "sent" and f.payload_snippet == "ping"
               for f in ws)
    assert all(f.url == "ws://app/socket" for f in ws if f.url)


@pytest.mark.asyncio
async def test_payload_snippet_truncated_at_200():
    long = "A" * 500
    cdp = _FakeCDP()
    page = _FakePage(cdp, ws_events=[
        ("Network.webSocketCreated",
         {"requestId": "r2", "url": "ws://x/"}),
        ("Network.webSocketFrameSent",
         {"requestId": "r2", "response": {"payloadData": long}}),
        ("Network.webSocketFrameReceived",
         {"requestId": "r2", "response": {"payloadData": long}}),
    ])
    obs = SWWSObserver(page)
    sw, ws = await obs.observe("http://x/", duration_ms=1)
    assert all(len(f.payload_snippet) <= 200 for f in ws)
    assert any(len(f.payload_snippet) == 200 for f in ws)
