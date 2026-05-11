"""Shared Playwright page lifecycle for sync-API browser interactions.

Replaces three duplicated _open_page / factory / cleanup helpers in
mock_start, mock_auth, and execution_loop. Wraps all blocking Playwright
calls in asyncio.to_thread.

Does NOT replace sink_monitor's `with sync_playwright():` pattern —
that's a context-scoped observe, intentionally different.
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


async def open_page(
    url: str,
    *,
    headless: bool = True,
    wait_until: str = "load",
    timeout_ms: int = 5000,
) -> tuple[Any, Callable[[], Awaitable[None]]]:
    """Boot Playwright Chromium, open a page at ``url``, return (page, close_async).

    The close_async callable swallows per-step errors and is safe to call
    multiple times (per-step try/except). Caller is responsible for invoking
    it — typical pattern is try/finally.

    Raises on Playwright import failure or boot failure. Callers that need
    log-and-degrade behavior wrap in their own try/except.
    """
    def _make() -> tuple[Any, Any, Any]:
        from playwright.sync_api import sync_playwright
        ctx = sync_playwright().start()
        browser = ctx.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        return ctx, browser, page

    ctx, browser, page = await asyncio.to_thread(_make)

    def _close_sync() -> None:
        try:
            page.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
        try:
            ctx.stop()
        except Exception:
            pass

    async def _close_async() -> None:
        await asyncio.to_thread(_close_sync)

    return page, _close_async
