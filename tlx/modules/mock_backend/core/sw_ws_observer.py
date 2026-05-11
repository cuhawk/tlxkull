"""SWWSObserver — observe ServiceWorker registrations + WebSocket frames.

Read-only. Hooks Playwright + CDP to watch:
  - navigator.serviceWorker.getRegistrations() → SWObservation list
  - Network.webSocketFrameSent / webSocketFrameReceived → WSFrame list

Frame payloads are truncated at 200 chars before logging.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


_PAYLOAD_SNIPPET_LEN = 200


@dataclass
class SWObservation:
    scope: str
    script_url: str


@dataclass
class WSFrame:
    url: str
    direction: str
    payload_snippet: str


def _now_ms() -> float:
    return time.time() * 1000.0


def _truncate(text: str | None) -> str:
    if text is None:
        return ""
    s = str(text)
    return s[:_PAYLOAD_SNIPPET_LEN]


class SWWSObserver:
    def __init__(self, page: Any) -> None:
        self.page = page

    async def observe(
        self,
        url: str,
        duration_ms: int = 5000,
    ) -> tuple[list[SWObservation], list[WSFrame]]:
        return await asyncio.to_thread(self._observe_sync, url, duration_ms)

    def _observe_sync(
        self, url: str, duration_ms: int
    ) -> tuple[list[SWObservation], list[WSFrame]]:
        sw_obs: list[SWObservation] = []
        ws_frames: list[WSFrame] = []

        ws_url_by_id: dict[str, str] = {}
        cdp = self._make_cdp_session()

        def on_ws_created(params: dict) -> None:
            rid = str(params.get("requestId") or "")
            wurl = str(params.get("url") or "")
            if rid:
                ws_url_by_id[rid] = wurl

        def _frame(direction: str) -> Any:
            def handler(params: dict) -> None:
                rid = str(params.get("requestId") or "")
                wurl = ws_url_by_id.get(rid, "")
                resp = params.get("response") or {}
                payload = resp.get("payloadData", "") if isinstance(resp, dict) else ""
                ws_frames.append(WSFrame(
                    url=wurl,
                    direction=direction,
                    payload_snippet=_truncate(payload),
                ))
            return handler

        if cdp is not None:
            try:
                cdp.send("Network.enable")
            except Exception:
                pass
            try:
                cdp.on("Network.webSocketCreated", on_ws_created)
                cdp.on("Network.webSocketFrameSent", _frame("sent"))
                cdp.on(
                    "Network.webSocketFrameReceived", _frame("received"),
                )
            except Exception as exc:
                logger.debug("sw_ws_observer.cdp_attach_failed", error=str(exc))

        try:
            self.page.goto(url, wait_until="networkidle")
        except Exception as exc:
            logger.debug("sw_ws_observer.goto_failed", error=str(exc))

        try:
            self.page.wait_for_timeout(duration_ms)
        except Exception:
            pass

        try:
            registrations = self.page.evaluate(
                "() => navigator.serviceWorker "
                "  ? navigator.serviceWorker.getRegistrations()"
                "      .then(rs => rs.map(r => ({"
                "        scope: r.scope, "
                "        scriptURL: (r.active && r.active.scriptURL) || "
                "                   (r.installing && r.installing.scriptURL) || "
                "                   '' "
                "      })))"
                "  : []"
            )
        except Exception as exc:
            logger.debug("sw_ws_observer.sw_eval_failed", error=str(exc))
            registrations = []

        for r in registrations or []:
            if isinstance(r, dict):
                sw_obs.append(SWObservation(
                    scope=str(r.get("scope") or ""),
                    script_url=str(r.get("scriptURL") or ""),
                ))

        return sw_obs, ws_frames

    def _make_cdp_session(self) -> Any:
        ctx = getattr(self.page, "context", None)
        if ctx is None:
            return None
        try:
            return ctx.new_cdp_session(self.page)
        except Exception:
            return None
