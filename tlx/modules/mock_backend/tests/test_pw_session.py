"""Tests for core/pw_session.py — Phase 7G."""
from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

import pytest

from modules.mock_backend.core import pw_session


class _FakePage:
    def __init__(self) -> None:
        self.goto_calls: list[tuple[str, dict]] = []
        self.closed = 0

    def goto(self, url: str, **kwargs: Any) -> None:
        self.goto_calls.append((url, kwargs))

    def close(self) -> None:
        self.closed += 1


class _FakeBrowser:
    def __init__(self) -> None:
        self.closed = 0
        self.page = _FakePage()

    def new_page(self) -> _FakePage:
        return self.page

    def close(self) -> None:
        self.closed += 1


class _FakeChromium:
    def __init__(self) -> None:
        self.browser = _FakeBrowser()
        self.launch_kwargs: dict | None = None

    def launch(self, **kwargs: Any) -> _FakeBrowser:
        self.launch_kwargs = kwargs
        return self.browser


class _FakeCtx:
    def __init__(self) -> None:
        self.chromium = _FakeChromium()
        self.stopped = 0

    def stop(self) -> None:
        self.stopped += 1


class _FakeStarter:
    """Stand-in for ``sync_playwright()`` returning ``.start()`` -> ctx."""

    def __init__(self) -> None:
        self.ctx = _FakeCtx()

    def start(self) -> _FakeCtx:
        return self.ctx


def _install_fake_playwright(
    monkeypatch: pytest.MonkeyPatch, starter: _FakeStarter,
) -> None:
    fake_module = ModuleType("playwright.sync_api")

    def sync_playwright() -> _FakeStarter:
        return starter

    fake_module.sync_playwright = sync_playwright  # type: ignore[attr-defined]
    pkg = ModuleType("playwright")
    pkg.sync_api = fake_module  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "playwright", pkg)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", fake_module)


@pytest.mark.asyncio
async def test_open_page_returns_page_and_close_callable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    starter = _FakeStarter()
    _install_fake_playwright(monkeypatch, starter)
    page, close = await pw_session.open_page("http://example.com/")
    assert page is starter.ctx.chromium.browser.page
    assert callable(close)
    await close()


@pytest.mark.asyncio
async def test_close_callable_is_idempotent_swallows_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    starter = _FakeStarter()
    _install_fake_playwright(monkeypatch, starter)
    page, close = await pw_session.open_page("http://example.com/")

    # First close
    await close()
    # Make every cleanup step throw — second close must still not raise.
    page.close = lambda: (_ for _ in ()).throw(RuntimeError("boom"))  # type: ignore[assignment]
    starter.ctx.chromium.browser.close = (  # type: ignore[assignment]
        lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    starter.ctx.stop = (  # type: ignore[assignment]
        lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    await close()  # should not raise


@pytest.mark.asyncio
async def test_open_page_passes_wait_until_and_timeout_to_goto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    starter = _FakeStarter()
    _install_fake_playwright(monkeypatch, starter)
    page, close = await pw_session.open_page(
        "http://x/", wait_until="networkidle", timeout_ms=12345, headless=False,
    )
    assert page.goto_calls == [
        ("http://x/", {"wait_until": "networkidle", "timeout": 12345}),
    ]
    assert starter.ctx.chromium.launch_kwargs == {"headless": False}
    await close()


@pytest.mark.asyncio
async def test_open_page_propagates_playwright_import_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force the import inside _make to raise.
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)
    with pytest.raises(ImportError):
        await pw_session.open_page("http://x/")
