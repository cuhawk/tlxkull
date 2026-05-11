"""Playwright-based interaction primitives.

Drives the live page during execution-driven discovery (Phase 7D).
Every blocking Playwright call is wrapped in ``asyncio.to_thread`` so
the event loop stays free.

No anthropic / google.genai imports; no LLM calls.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


KNOWN_INTERACTION_KINDS: frozenset[str] = frozenset({
    "fill", "form_fill",
    "click",
    "dispatch",
    "postmessage", "post_message",
})
"""Accepted ``type`` values in ExecutionLoop._dispatch_one.

Both canonical names and aliases are listed: the dispatcher
normalises with ``.lower()`` and accepts either form. Source of
truth for input validation in mock_probe. If ``_dispatch_one``
gains a new kind/alias, update this set in lockstep.
"""


@dataclass
class InteractionEvent:
    kind: str
    selector: str
    value: str | None
    timestamp_ms: float


def _now_ms() -> float:
    return time.time() * 1000.0


class InteractionDriver:
    """Async wrapper around Playwright page interactions.

    Methods never raise on element-not-found — they return an
    InteractionEvent with ``value="not_found"``. Caller decides what
    to do next.
    """

    def __init__(self, page: Any) -> None:
        self.page = page

    async def fill_form(
        self, selector: str, value: str
    ) -> InteractionEvent:
        def _do() -> str | None:
            try:
                self.page.fill(selector, value)
                return value
            except Exception as exc:
                logger.debug(
                    "interaction_driver.fill_failed",
                    selector=selector, error=str(exc),
                )
                return None

        result = await asyncio.to_thread(_do)
        return InteractionEvent(
            kind="form_fill",
            selector=selector,
            value=result if result is not None else "not_found",
            timestamp_ms=_now_ms(),
        )

    async def click(self, selector: str) -> InteractionEvent:
        def _do() -> bool:
            try:
                self.page.click(selector)
                return True
            except Exception as exc:
                logger.debug(
                    "interaction_driver.click_failed",
                    selector=selector, error=str(exc),
                )
                return False

        ok = await asyncio.to_thread(_do)
        return InteractionEvent(
            kind="click",
            selector=selector,
            value=None if ok else "not_found",
            timestamp_ms=_now_ms(),
        )

    async def dispatch(
        self, selector: str, event: str
    ) -> InteractionEvent:
        def _do() -> bool:
            try:
                self.page.dispatch_event(selector, event)
                return True
            except Exception as exc:
                logger.debug(
                    "interaction_driver.dispatch_failed",
                    selector=selector, ev_name=event, error=str(exc),
                )
                return False

        ok = await asyncio.to_thread(_do)
        return InteractionEvent(
            kind="dispatch",
            selector=selector,
            value=event if ok else "not_found",
            timestamp_ms=_now_ms(),
        )

    async def post_message(
        self, origin: str, data: dict
    ) -> InteractionEvent:
        def _do() -> bool:
            try:
                self.page.evaluate(
                    "({origin, data}) => window.postMessage(data, origin)",
                    {"origin": origin, "data": data},
                )
                return True
            except Exception as exc:
                logger.debug(
                    "interaction_driver.postmessage_failed",
                    origin=origin, error=str(exc),
                )
                return False

        ok = await asyncio.to_thread(_do)
        return InteractionEvent(
            kind="postmessage",
            selector=origin,
            value=None if ok else "not_found",
            timestamp_ms=_now_ms(),
        )
