"""ExecutionLoop — orchestrate interaction-driven discovery (Phase 7D).

Boots the per-session mock server, opens Playwright, attaches a
SinkMonitor, drives a list of interactions through InteractionDriver,
collects observed network traffic + sink hits, then shuts everything
down. Returns a DiscoveryResult.

All Playwright sync calls are funneled through ``asyncio.to_thread``.
No anthropic / google.genai imports.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from . import pw_session, uvicorn_lifecycle
from .interaction_driver import InteractionDriver, InteractionEvent
from .mock_server import create_app
from .payload_injector import PayloadInjector
from .response_factory import build_response
from .sink_monitor import SinkHit, SinkMonitor

logger = structlog.get_logger(__name__)


@dataclass
class DiscoveryResult:
    url: str
    interactions: list[InteractionEvent] = field(default_factory=list)
    sink_hits: list[SinkHit] = field(default_factory=list)
    new_routes: list[str] = field(default_factory=list)
    auto_explored: bool = False
    auto_added_count: int = 0


class ExecutionLoop:
    """Drive a full interaction-driven discovery pass.

    Tests typically monkeypatch ``_boot_server`` / ``_open_page`` /
    ``_run_monitor`` to skip real uvicorn + Chromium and inject
    deterministic fakes.
    """

    def __init__(
        self,
        db_path: Path,
        injector: PayloadInjector,
        monitor: SinkMonitor,
    ) -> None:
        self.db_path = Path(db_path)
        self.injector = injector
        self.monitor = monitor

    async def run(
        self,
        session_id: str,
        route_specs: list,
        dom_specs: list,
        interactions: list[dict],
        auto_explore: bool = False,
    ) -> DiscoveryResult:
        scaffolded_html = self._scaffold_from_dom_specs(dom_specs)
        static_dir = self.db_path.parent / f".browser_static_{session_id}"
        static_dir.mkdir(parents=True, exist_ok=True)

        probe_id = self.injector.sentinel_for(session_id)

        def provider(route: Any, pid: str) -> Any:
            return build_response(route, pid, variant="default")

        app = create_app(
            session_id=session_id,
            scaffolded_html=scaffolded_html,
            static_dir=static_dir,
            routes=list(route_specs or []),
            response_provider=provider,
            probe_id=probe_id,
            db_path=self.db_path,
            request_log_source="probe",
        )

        url = ""
        observed_urls: list[str] = []
        events: list[InteractionEvent] = []
        hits: list[SinkHit] = []
        auto_added = 0

        page_close: Any = None
        try:
            url = await self._boot_server(app)
            page = None
            if url:
                page, page_close = await pw_session.open_page(
                    url, wait_until="networkidle", timeout_ms=30000,
                )
            if page is not None:
                self._attach_observer(page, observed_urls)
                driver = InteractionDriver(page)
                for spec in interactions or []:
                    ev = await self._dispatch_one(driver, spec)
                    if ev is not None:
                        events.append(ev)
                if auto_explore:
                    from .page_explorer import (
                        dedup_against,
                        enumerate_interactions,
                    )
                    discovered = await enumerate_interactions(
                        page, probe_id,
                    )
                    discovered = dedup_against(
                        discovered, interactions or [],
                    )
                    for spec in discovered:
                        ev = await self._dispatch_one(driver, spec)
                        if ev is not None:
                            events.append(ev)
                            auto_added += 1
                hits = await self._run_monitor(url)
        finally:
            if page_close is not None:
                try:
                    await page_close()
                except Exception:
                    pass
            await self._shutdown_server()

        known_urls = {url} if url else set()
        new_routes = [
            u for u in observed_urls if u and u not in known_urls
        ]

        return DiscoveryResult(
            url=url,
            interactions=events,
            sink_hits=list(hits),
            new_routes=new_routes,
            auto_explored=auto_explore,
            auto_added_count=auto_added,
        )

    def _scaffold_from_dom_specs(self, dom_specs: list) -> str:
        for spec in dom_specs or []:
            html_attr = getattr(spec, "html", None)
            if isinstance(html_attr, str):
                return html_attr
            if isinstance(spec, dict) and isinstance(spec.get("html"), str):
                return spec["html"]
        return "<!DOCTYPE html><html><body></body></html>"

    async def _dispatch_one(
        self, driver: InteractionDriver, spec: dict
    ) -> InteractionEvent | None:
        kind = (spec.get("type") or "").lower()
        sel = spec.get("selector") or ""
        val = spec.get("value")
        if kind in ("fill", "form_fill"):
            return await driver.fill_form(sel, str(val or ""))
        if kind == "click":
            return await driver.click(sel)
        if kind == "dispatch":
            return await driver.dispatch(sel, str(val or ""))
        if kind in ("postmessage", "post_message"):
            origin = sel or "*"
            data = spec.get("data") or {}
            if not isinstance(data, dict):
                data = {"raw": data}
            return await driver.post_message(origin, data)
        logger.debug("execution_loop.unknown_interaction", kind=kind)
        return None

    async def _boot_server(self, app: Any) -> str:
        self._server, self._serve_task, port = await uvicorn_lifecycle.boot_app(
            app,
        )
        if self._server is None:
            return ""
        return f"http://127.0.0.1:{port}/" if port else ""

    async def _shutdown_server(self) -> None:
        server = getattr(self, "_server", None)
        serve_task = getattr(self, "_serve_task", None)
        await uvicorn_lifecycle.shutdown(server, serve_task)
        self._server = None
        self._serve_task = None

    def _attach_observer(self, page: Any, observed: list[str]) -> None:
        try:
            def on_request(req: Any) -> None:
                try:
                    observed.append(req.url)
                except Exception:
                    pass
            page.on("request", on_request)
        except Exception as exc:
            logger.debug("execution_loop.attach_failed", error=str(exc))

    async def _run_monitor(self, url: str) -> list[SinkHit]:
        if not url:
            return []
        try:
            return await self.monitor.observe(url)
        except Exception as exc:
            logger.debug("execution_loop.monitor_failed", error=str(exc))
            return []


def _now_ms() -> float:
    return time.time() * 1000.0
