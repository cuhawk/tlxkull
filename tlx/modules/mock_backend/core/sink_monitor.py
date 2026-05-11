"""Headless-browser sink-confirmation observer.

Boots Playwright Chromium in headless mode, navigates to a URL served
by the per-session mock_server, and watches for the probe sentinel
showing up in any sink-firing context (console, DOM, network).

Playwright sync API is wrapped in asyncio.to_thread to avoid blocking
the event loop. No anthropic / google.genai imports.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SinkHit:
    chain_id: str
    sentinel: str
    sink_type: str
    detail: str
    timestamp_ms: float
    extra: dict[str, Any] = field(default_factory=dict)


_DOM_PROBE_JS = """
(sentinel) => {
  window.__tlxDomHits = window.__tlxDomHits || [];
  const seen = new Set();
  const scan = () => {
    try {
      const html = document.documentElement
        ? document.documentElement.innerHTML
        : '';
      if (html && html.includes(sentinel) && !seen.has(html.length)) {
        seen.add(html.length);
        window.__tlxDomHits.push({
          ts: Date.now(),
          len: html.length
        });
      }
    } catch (e) { /* ignore */ }
  };
  const obs = new MutationObserver(scan);
  obs.observe(document.documentElement, {
    subtree: true, childList: true, attributes: true, characterData: true
  });
  scan();
}
"""


class SinkMonitor:
    def __init__(
        self,
        sentinel: str,
        timeout_ms: int = 8000,
        chain_id: str = "",
    ) -> None:
        self.sentinel = sentinel
        self.timeout_ms = timeout_ms
        self.chain_id = chain_id

    async def observe(self, url: str) -> list[SinkHit]:
        return await asyncio.to_thread(self._observe_sync, url)

    def _observe_sync(self, url: str) -> list[SinkHit]:
        from playwright.sync_api import sync_playwright

        hits: list[SinkHit] = []
        sentinel = self.sentinel
        chain_id = self.chain_id

        def _now_ms() -> float:
            return time.time() * 1000.0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            def on_console(msg: Any) -> None:
                try:
                    text = msg.text
                except Exception:
                    text = str(msg)
                if sentinel in (text or ""):
                    hits.append(SinkHit(
                        chain_id=chain_id,
                        sentinel=sentinel,
                        sink_type="console",
                        detail=text or "",
                        timestamp_ms=_now_ms(),
                    ))

            def on_response(resp: Any) -> None:
                try:
                    rurl = resp.url
                except Exception:
                    rurl = ""
                if sentinel in (rurl or ""):
                    hits.append(SinkHit(
                        chain_id=chain_id,
                        sentinel=sentinel,
                        sink_type="network",
                        detail=rurl,
                        timestamp_ms=_now_ms(),
                    ))
                    return
                try:
                    body = resp.body()
                    if body and sentinel.encode("utf-8") in body:
                        hits.append(SinkHit(
                            chain_id=chain_id,
                            sentinel=sentinel,
                            sink_type="network",
                            detail=rurl,
                            timestamp_ms=_now_ms(),
                        ))
                except Exception:
                    pass

            page.on("console", on_console)
            page.on("response", on_response)

            try:
                cdp = context.new_cdp_session(page)
                cdp.send("DOM.enable")
            except Exception:
                pass

            try:
                page.goto(url, wait_until="networkidle",
                          timeout=self.timeout_ms)
            except Exception:
                pass

            try:
                page.evaluate(_DOM_PROBE_JS, sentinel)
            except Exception:
                pass

            page.wait_for_timeout(self.timeout_ms)

            try:
                dom_hits = page.evaluate("() => window.__tlxDomHits || []")
            except Exception:
                dom_hits = []
            for h in dom_hits or []:
                hits.append(SinkHit(
                    chain_id=chain_id,
                    sentinel=sentinel,
                    sink_type="dom_mutation",
                    detail=f"len={h.get('len', 0)}",
                    timestamp_ms=float(h.get("ts", _now_ms())),
                ))

            context.close()
            browser.close()
        return hits
