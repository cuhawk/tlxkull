"""Tests for InteractionDriver — pure mocked Playwright."""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.mock_backend.core.interaction_driver import (
    InteractionDriver,
    InteractionEvent,
)


class _FakePage:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []
        self.fail: set[str] = set()

    def _record(self, name: str, *args: Any, **kwargs: Any) -> Any:
        self.calls.append((name, args, kwargs))
        if name in self.fail:
            raise RuntimeError(f"{name} failed")
        return None

    def fill(self, selector: str, value: str) -> None:
        self._record("fill", selector, value)

    def click(self, selector: str) -> None:
        self._record("click", selector)

    def dispatch_event(self, selector: str, event: str) -> None:
        self._record("dispatch_event", selector, event)

    def evaluate(self, script: str, arg: Any = None) -> Any:
        return self._record("evaluate", script, arg)


@pytest.mark.asyncio
async def test_fill_form_returns_form_fill_event():
    page = _FakePage()
    drv = InteractionDriver(page)
    ev = await drv.fill_form("#email", "x@y.z")
    assert isinstance(ev, InteractionEvent)
    assert ev.kind == "form_fill"
    assert ev.selector == "#email"
    assert ev.value == "x@y.z"
    assert ev.timestamp_ms > 0
    assert ("fill", ("#email", "x@y.z"), {}) in page.calls


@pytest.mark.asyncio
async def test_click_returns_click_event():
    page = _FakePage()
    drv = InteractionDriver(page)
    ev = await drv.click("button.submit")
    assert ev.kind == "click"
    assert ev.selector == "button.submit"
    assert ev.value is None


@pytest.mark.asyncio
async def test_post_message_returns_postmessage_event():
    page = _FakePage()
    drv = InteractionDriver(page)
    ev = await drv.post_message("https://evil.example", {"x": 1})
    assert ev.kind == "postmessage"
    assert ev.selector == "https://evil.example"
    assert ev.value is None
    assert page.calls and page.calls[0][0] == "evaluate"


@pytest.mark.asyncio
async def test_dispatch_returns_dispatch_event():
    page = _FakePage()
    drv = InteractionDriver(page)
    ev = await drv.dispatch("#thing", "input")
    assert ev.kind == "dispatch"
    assert ev.selector == "#thing"
    assert ev.value == "input"


@pytest.mark.asyncio
async def test_fill_element_not_found_returns_not_found_no_raise():
    page = _FakePage()
    page.fail.add("fill")
    drv = InteractionDriver(page)
    ev = await drv.fill_form("#missing", "v")
    assert ev.kind == "form_fill"
    assert ev.value == "not_found"


@pytest.mark.asyncio
async def test_click_element_not_found_returns_not_found():
    page = _FakePage()
    page.fail.add("click")
    drv = InteractionDriver(page)
    ev = await drv.click("#missing")
    assert ev.kind == "click"
    assert ev.value == "not_found"


@pytest.mark.asyncio
async def test_dispatch_failure_returns_not_found():
    page = _FakePage()
    page.fail.add("dispatch_event")
    drv = InteractionDriver(page)
    ev = await drv.dispatch("#bad", "click")
    assert ev.value == "not_found"


@pytest.mark.asyncio
async def test_postmessage_failure_returns_not_found():
    page = MagicMock()
    page.evaluate.side_effect = RuntimeError("nope")
    drv = InteractionDriver(page)
    ev = await drv.post_message("*", {})
    assert ev.kind == "postmessage"
    assert ev.value == "not_found"
