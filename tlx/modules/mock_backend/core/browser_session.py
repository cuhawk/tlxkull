"""Orchestrate per-chain confirmation: server boot → browser → finding.

BrowserSession glues together response_factory, mock_server, source_rewriter,
sink_monitor, and the SQLite mock_findings table.

Tests typically monkeypatch BrowserSession._observe to skip the real
uvicorn boot and SinkMonitor invocation.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from . import uvicorn_lifecycle
from .mock_server import create_app
from .payload_injector import PayloadInjector, ProbeSpec
from .reporter import _open_conn
from .response_factory import build_response
from .sink_monitor import SinkHit, SinkMonitor
from .source_rewriter import inject_probe_in_response


@dataclass
class ConfirmResult:
    chain_id: str
    confirmed: bool
    hits: list[SinkHit] = field(default_factory=list)
    probe_value: str = ""
    server_url: str = ""


class _RewriteMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, rewrite_map: dict[str, str]) -> None:
        super().__init__(app)
        self.rewrite_map = rewrite_map

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        resp = await call_next(request)
        ct = resp.headers.get("content-type", "")
        if "javascript" not in ct.lower():
            return resp
        body_iter: AsyncIterator[bytes] = resp.body_iterator  # type: ignore[assignment]
        chunks: list[bytes] = []
        async for chunk in body_iter:
            chunks.append(chunk if isinstance(chunk, bytes) else bytes(chunk))
        body = b"".join(chunks)
        new_body = inject_probe_in_response(body, ct, self.rewrite_map)
        headers = dict(resp.headers)
        headers.pop("content-length", None)
        return Response(
            content=new_body,
            status_code=resp.status_code,
            headers=headers,
            media_type=ct,
        )


def _write_finding(
    db_path: Path,
    session_id: str,
    chain: dict,
    result: ConfirmResult,
) -> None:
    chain_id = str(chain.get("chain_id") or chain.get("id") or result.chain_id)
    hits_payload = [asdict(h) for h in result.hits]
    conn = _open_conn(db_path)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO mock_findings "
            "(session_id, chain_id, confirmed, probe_value, hits_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                session_id,
                chain_id,
                1 if result.confirmed else 0,
                result.probe_value,
                json.dumps(hits_payload),
            ),
        )
        conn.commit()
    finally:
        conn.close()


class BrowserSession:
    def __init__(
        self,
        db_path: Path,
        injector: PayloadInjector,
        timeout_ms: int = 8000,
    ) -> None:
        self.db_path = Path(db_path)
        self.injector = injector
        self.timeout_ms = timeout_ms

    def _build_app(
        self,
        session_id: str,
        scaffolded_html: str,
        static_dir: Path,
        route_specs: list,
        probe_spec: ProbeSpec,
    ) -> FastAPI:
        def provider(route: Any, probe_id: str) -> Any:
            return build_response(route, probe_id, variant="default")

        app = create_app(
            session_id=session_id,
            scaffolded_html=scaffolded_html,
            static_dir=static_dir,
            routes=route_specs,
            response_provider=provider,
            probe_id=probe_spec.probe_value,
            db_path=self.db_path,
            request_log_source="confirm",
        )
        if probe_spec.rewrite_map:
            app.add_middleware(
                _RewriteMiddleware, rewrite_map=probe_spec.rewrite_map
            )
        return app

    async def _observe(
        self,
        app: FastAPI,
        probe_spec: ProbeSpec,
        chain_id: str,
    ) -> tuple[list[SinkHit], str]:
        server, serve_task, port = await uvicorn_lifecycle.boot_app(app)
        if server is None:
            return [], ""
        url = f"http://127.0.0.1:{port}/" if port else ""
        try:
            monitor = SinkMonitor(
                sentinel=probe_spec.probe_value,
                timeout_ms=self.timeout_ms,
                chain_id=chain_id,
            )
            hits = await monitor.observe(url) if url else []
        finally:
            await uvicorn_lifecycle.shutdown(server, serve_task)
        return hits, url

    def _scaffold_from_dom_specs(self, dom_specs: list) -> str:
        for spec in dom_specs or []:
            html_attr = getattr(spec, "html", None)
            if isinstance(html_attr, str):
                return html_attr
            if isinstance(spec, dict) and isinstance(spec.get("html"), str):
                return spec["html"]
        return "<!DOCTYPE html><html><body></body></html>"

    async def run_all_chains(
        self,
        session_id: str,
        chains: list[dict],
        route_specs: list,
        dom_specs: list,
    ) -> list[ConfirmResult]:
        """Boot one mock server, run every chain against it.

        Each chain gets its own ProbeSpec; the mock server serves a
        per-request probe value via a ``window.__tlx_probe`` global
        injected at the top of every JS response, then the per-chain
        regex rewrite replaces source identifiers with the JSON-quoted
        probe literal.

        Returns one ConfirmResult per input chain. Server is shut down
        once after the last chain completes.
        """
        if not chains:
            return []

        scaffolded_html = self._scaffold_from_dom_specs(dom_specs)
        static_dir = self.db_path.parent / f".browser_static_{session_id}"
        static_dir.mkdir(parents=True, exist_ok=True)

        probes: list[tuple[str, ProbeSpec]] = []
        for chain in chains:
            chain_id = str(
                chain.get("chain_id") or chain.get("id") or "",
            )
            probes.append((chain_id, self.injector.make_probe(chain)))

        merged_rewrite: dict[str, str] = {}
        for _cid, p in probes:
            merged_rewrite.update(p.rewrite_map)

        merged_probe = ProbeSpec(
            source_qname="batch",
            probe_value="batch-" + (probes[0][1].probe_value if probes else ""),
            rewrite_map=merged_rewrite,
        )

        app = self._build_app(
            session_id=session_id,
            scaffolded_html=scaffolded_html,
            static_dir=static_dir,
            route_specs=list(route_specs or []),
            probe_spec=merged_probe,
        )

        url = await self._boot_server(app)
        results: list[ConfirmResult] = []
        try:
            for chain, (chain_id, probe_spec) in zip(
                chains, probes, strict=True,
            ):
                hits: list[SinkHit] = []
                if url:
                    monitor = SinkMonitor(
                        sentinel=probe_spec.probe_value,
                        timeout_ms=self.timeout_ms,
                        chain_id=chain_id,
                    )
                    hits = await monitor.observe(url)
                result = ConfirmResult(
                    chain_id=chain_id,
                    confirmed=len(hits) > 0,
                    hits=list(hits),
                    probe_value=probe_spec.probe_value,
                    server_url=url,
                )
                _write_finding(self.db_path, session_id, chain, result)
                results.append(result)
        finally:
            await self._shutdown_server()

        return results

    async def _boot_server(self, app: FastAPI) -> str:
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

    async def confirm_chain(
        self,
        session_id: str,
        chain: dict,
        route_specs: list,
        dom_specs: list,
    ) -> ConfirmResult:
        chain_id = str(chain.get("chain_id") or chain.get("id") or "")
        probe_spec = self.injector.make_probe(chain)

        scaffolded_html = ""
        static_dir = self.db_path.parent / f".browser_static_{session_id}"
        static_dir.mkdir(parents=True, exist_ok=True)
        for spec in dom_specs or []:
            html_attr = getattr(spec, "html", None)
            if isinstance(html_attr, str):
                scaffolded_html = html_attr
                break
            if isinstance(spec, dict) and isinstance(spec.get("html"), str):
                scaffolded_html = spec["html"]
                break
        if not scaffolded_html:
            scaffolded_html = "<!DOCTYPE html><html><body></body></html>"

        app = self._build_app(
            session_id=session_id,
            scaffolded_html=scaffolded_html,
            static_dir=static_dir,
            route_specs=list(route_specs or []),
            probe_spec=probe_spec,
        )

        hits, url = await self._observe(app, probe_spec, chain_id)

        result = ConfirmResult(
            chain_id=chain_id,
            confirmed=len(hits) > 0,
            hits=list(hits),
            probe_value=probe_spec.probe_value,
            server_url=url,
        )
        _write_finding(self.db_path, session_id, chain, result)
        return result
