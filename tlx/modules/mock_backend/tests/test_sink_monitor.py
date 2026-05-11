"""Tests for mock_backend sink_monitor (Phase 7B Task 3).

Mocks Playwright sync API — never launches a real browser.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from modules.mock_backend.core.sink_monitor import SinkHit, SinkMonitor


def _fake_playwright(
    *,
    fire_console: list[str] | None = None,
    fire_response_url: list[str] | None = None,
    dom_hits: list[dict] | None = None,
) -> tuple[MagicMock, dict]:
    """Build a fake sync_playwright context manager and event handlers dict.

    Returns (mock_sync_playwright, captured) where captured["handlers"] is
    populated by page.on() registrations.
    """
    fire_console = fire_console or []
    fire_response_url = fire_response_url or []
    dom_hits = dom_hits or []
    captured: dict[str, Any] = {"handlers": {}, "goto_called": False}

    fake_page = MagicMock()
    fake_context = MagicMock()
    fake_browser = MagicMock()

    def _on(event: str, h: Any) -> None:
        captured["handlers"][event] = h

    fake_page.on = _on

    def _goto(url: str, **_kw: Any) -> None:
        captured["goto_called"] = True
        captured["url"] = url
        for text in fire_console:
            msg = MagicMock()
            msg.text = text
            h = captured["handlers"].get("console")
            if h:
                h(msg)
        for rurl in fire_response_url:
            resp = MagicMock()
            resp.url = rurl
            resp.body.return_value = b""
            h = captured["handlers"].get("response")
            if h:
                h(resp)

    fake_page.goto = _goto
    fake_page.evaluate = MagicMock(return_value=dom_hits)
    fake_page.wait_for_timeout = MagicMock()

    fake_context.new_page.return_value = fake_page
    fake_context.new_cdp_session.return_value = MagicMock()
    fake_browser.new_context.return_value = fake_context

    fake_p = MagicMock()
    fake_p.chromium.launch.return_value = fake_browser

    cm = MagicMock()
    cm.__enter__.return_value = fake_p
    cm.__exit__.return_value = None

    sp = MagicMock(return_value=cm)
    return sp, captured


@pytest.mark.asyncio
async def test_observe_returns_empty_when_no_sentinel_seen():
    sp, _captured = _fake_playwright()
    with patch("playwright.sync_api.sync_playwright", sp):
        mon = SinkMonitor(sentinel="probe-xss-XYZ", timeout_ms=10)
        hits = await mon.observe("http://127.0.0.1:8000/")
    assert hits == []


@pytest.mark.asyncio
async def test_observe_records_console_hit_with_sentinel():
    sp, _captured = _fake_playwright(
        fire_console=["got value: probe-xss-ABCD here"],
    )
    with patch("playwright.sync_api.sync_playwright", sp):
        mon = SinkMonitor(
            sentinel="probe-xss-ABCD", timeout_ms=10, chain_id="chain-1"
        )
        hits = await mon.observe("http://127.0.0.1:8000/")
    assert len(hits) == 1
    h = hits[0]
    assert isinstance(h, SinkHit)
    assert h.sink_type == "console"
    assert h.sentinel == "probe-xss-ABCD"
    assert h.chain_id == "chain-1"
    assert "probe-xss-ABCD" in h.detail
    assert h.timestamp_ms > 0


@pytest.mark.asyncio
async def test_observe_console_without_sentinel_ignored():
    sp, _captured = _fake_playwright(
        fire_console=["unrelated message", "still nothing here"],
    )
    with patch("playwright.sync_api.sync_playwright", sp):
        mon = SinkMonitor(sentinel="probe-xss-Z", timeout_ms=10)
        hits = await mon.observe("http://127.0.0.1:8000/")
    assert hits == []


@pytest.mark.asyncio
async def test_observe_records_network_hit_when_url_contains_sentinel():
    sp, _captured = _fake_playwright(
        fire_response_url=[
            "http://evil.example.com/leak?token=probe-xss-ABCD",
        ],
    )
    with patch("playwright.sync_api.sync_playwright", sp):
        mon = SinkMonitor(
            sentinel="probe-xss-ABCD", timeout_ms=10, chain_id="c2"
        )
        hits = await mon.observe("http://127.0.0.1:8000/")
    assert len(hits) == 1
    assert hits[0].sink_type == "network"
    assert "probe-xss-ABCD" in hits[0].detail


@pytest.mark.asyncio
async def test_observe_records_dom_mutation_hit():
    sp, _captured = _fake_playwright(
        dom_hits=[{"ts": 1234567.0, "len": 42}],
    )
    with patch("playwright.sync_api.sync_playwright", sp):
        mon = SinkMonitor(
            sentinel="probe-xss-DEAD", timeout_ms=10, chain_id="c3"
        )
        hits = await mon.observe("http://127.0.0.1:8000/")
    assert len(hits) == 1
    assert hits[0].sink_type == "dom_mutation"
    assert "len=42" in hits[0].detail
    assert hits[0].chain_id == "c3"


def test_sink_hit_dataclass_fields():
    h = SinkHit(
        chain_id="c", sentinel="s", sink_type="console",
        detail="d", timestamp_ms=1.0,
    )
    assert h.chain_id == "c"
    assert h.sentinel == "s"
    assert h.sink_type == "console"
    assert h.detail == "d"
    assert h.timestamp_ms == 1.0
