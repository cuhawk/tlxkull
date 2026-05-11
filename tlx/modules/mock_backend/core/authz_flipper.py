"""AuthzFlipper — mutate role/flag fields in a mock response, diff UI.

Deterministic, no LLM. Per-(method, path) override entries live in a
dict consulted by a single BaseHTTPMiddleware installed at construction.
A flip writes the override, reloads the page, captures innerHTML, then
removes the override — all under try/finally. Single dict op is atomic
under CPython's GIL, so concurrent flips on different routes don't
race on app.routes.
"""
from __future__ import annotations

import asyncio
import copy
import difflib
from dataclasses import dataclass
from typing import Any

import structlog
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = structlog.get_logger(__name__)


_ROLE_LIKE = {"user", "viewer", "guest", "member", "anonymous"}


@dataclass
class AuthzFlipResult:
    route: str
    field: str
    original_value: Any
    flipped_value: Any
    ui_diff: str


def _flip_value(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        if value.lower() in _ROLE_LIKE:
            return "admin"
        return "admin"
    if isinstance(value, int):
        return value | 0xFFFF
    return value


def _patch_field(body: dict, field: str, new_value: Any) -> dict:
    out = copy.deepcopy(body)
    cur: Any = out
    parts = field.split(".")
    for p in parts[:-1]:
        if not isinstance(cur, dict) or p not in cur:
            return out
        cur = cur[p]
    if isinstance(cur, dict) and parts[-1] in cur:
        cur[parts[-1]] = new_value
    return out


def _read_field(body: dict, field: str) -> Any:
    cur: Any = body
    for p in field.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def _normalize_route(route: str) -> str:
    if not route.startswith("/"):
        route = "/" + route
    return route


class AuthzFlipper:
    def __init__(self, server_app: Any) -> None:
        self.server_app = server_app
        self._overrides: dict[tuple[str, str], dict] = {}
        self._install_middleware()
        try:
            server_app.state._authz_overrides = self._overrides
        except Exception:
            pass

    def _install_middleware(self) -> None:
        overrides = self._overrides

        class _Override(BaseHTTPMiddleware):
            async def dispatch(
                self, request: Request, call_next: Any
            ) -> Any:
                key = (request.method.upper(), request.url.path)
                body = overrides.get(key)
                if body is not None:
                    return JSONResponse(body)
                return await call_next(request)

        try:
            self.server_app.add_middleware(_Override)
        except Exception:
            self.server_app.user_middleware.insert(0, Middleware(_Override))
            self.server_app.middleware_stack = (
                self.server_app.build_middleware_stack()
            )

    async def flip(
        self,
        page: Any,
        route: str,
        response_body: dict,
        field: str,
        method: str = "GET",
    ) -> AuthzFlipResult:
        original_value = _read_field(response_body, field)
        flipped_value = _flip_value(original_value)
        flipped_body = _patch_field(response_body, field, flipped_value)

        before_html = await self._innerHTML(page)
        key = (method.upper(), _normalize_route(route))
        self._overrides[key] = flipped_body
        try:
            await asyncio.to_thread(self._reload, page)
            after_html = await self._innerHTML(page)
        finally:
            self._overrides.pop(key, None)

        diff_lines = difflib.unified_diff(
            before_html.splitlines(),
            after_html.splitlines(),
            lineterm="",
            fromfile="before",
            tofile="after",
        )
        ui_diff = "\n".join(diff_lines)

        return AuthzFlipResult(
            route=_normalize_route(route),
            field=field,
            original_value=original_value,
            flipped_value=flipped_value,
            ui_diff=ui_diff,
        )

    @staticmethod
    def _reload(page: Any) -> None:
        try:
            page.reload(wait_until="networkidle")
        except Exception:
            try:
                page.reload()
            except Exception:
                pass

    async def _innerHTML(self, page: Any) -> str:
        def _do() -> str:
            try:
                return page.evaluate("() => document.body.innerHTML") or ""
            except Exception:
                return ""

        return await asyncio.to_thread(_do)
