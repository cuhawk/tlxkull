"""Per-session FastAPI app factory.

Caller is responsible for binding to 127.0.0.1 and choosing a port.
This factory does not start the server.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .route_extractor import RouteSpec

_PARAM_RE = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")
_QUERY_RE = re.compile(r"\?.*$")


def url_to_starlette_path(url: str) -> str:
    """Convert URL templates to Starlette path-param syntax.

    Rules:
        :id            → {id}
        *              → {wild_N}     (N increments per * within the path)
        trailing ?...  → stripped
    """
    if not url:
        return "/"
    path = _QUERY_RE.sub("", url)
    path = _PARAM_RE.sub(lambda m: "{" + m.group(1) + "}", path)

    counter = {"n": 0}

    def _star(_m: re.Match[str]) -> str:
        idx = counter["n"]
        counter["n"] += 1
        return "{" + f"wild_{idx}" + "}"

    path = re.sub(r"\*", _star, path)
    if not path.startswith("/"):
        path = "/" + path
    return path


def create_app(
    session_id: str,
    scaffolded_html: str,
    static_dir: Path,
    routes: list[RouteSpec],
    response_provider: Callable[[RouteSpec, str], Any],
    probe_id: str,
    db_path: Path | None = None,
    request_log_source: str = "probe",
) -> FastAPI:
    """Build a fresh FastAPI per call. NOT cached.

    When ``db_path`` is provided, attaches RequestLoggerMiddleware so
    every inbound request is captured in mock_requests (and mock_flow
    on JSON 2xx).
    """
    app = FastAPI(title=f"tlx-mock-{session_id}")
    static_dir = Path(static_dir)
    static_dir.mkdir(parents=True, exist_ok=True)

    if db_path is not None:
        from .request_logger import RequestLoggerMiddleware
        app.add_middleware(
            RequestLoggerMiddleware,
            session_id=session_id,
            db_path=Path(db_path),
            source=request_log_source,
        )

    @app.get("/", response_class=HTMLResponse)
    async def root() -> HTMLResponse:
        return HTMLResponse(scaffolded_html)

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    seen: set[tuple[str, str]] = set()
    for route in routes:
        path = url_to_starlette_path(route.url)
        method = route.method.upper()
        key = (path, method)
        if key in seen:
            continue
        seen.add(key)

        async def handler(
            _request: Request, _r: RouteSpec = route
        ) -> Response:
            value = response_provider(_r, probe_id)
            if isinstance(value, str):
                return HTMLResponse(value)
            if isinstance(value, (dict, list)):
                return JSONResponse(value)
            return JSONResponse({"data": value})

        app.add_api_route(path, handler, methods=[method])

    return app
