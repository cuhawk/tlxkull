"""RequestLoggerMiddleware — observe every inbound request to a
per-session mock server.

Writes one row to ``mock_requests`` per request. JSON 2xx/3xx
responses also auto-prime ``mock_flow`` (replaces the old manual
``mock_record`` workflow for ``mock_authz``).

Body snippets are capped at ``_BODY_SNIPPET_MAX`` bytes. SQLite write
runs in a worker thread to keep the event loop unblocked. Any write
failure is swallowed at debug — middleware must not break the response
path.
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .reporter import _open_conn

logger = structlog.get_logger(__name__)

_BODY_SNIPPET_MAX = 2048


def _truncate(data: bytes) -> str:
    if not data:
        return ""
    return data[:_BODY_SNIPPET_MAX].decode("utf-8", errors="replace")


async def _read_body_safe(request: Request) -> str:
    try:
        body = await request.body()
    except Exception:
        return ""
    return _truncate(body)


async def _capture_response(response: Response) -> tuple[str, str, Response]:
    ctype = response.headers.get("content-type", "") or ""
    body_iter: AsyncIterator[bytes] | None = getattr(
        response, "body_iterator", None,
    )
    if body_iter is None:
        body_bytes = getattr(response, "body", b"") or b""
        return _truncate(bytes(body_bytes)), ctype, response

    chunks: list[bytes] = []
    async for chunk in body_iter:
        chunks.append(chunk if isinstance(chunk, bytes) else bytes(chunk))
    body = b"".join(chunks)
    headers = dict(response.headers)
    headers.pop("content-length", None)
    rebuilt = Response(
        content=body,
        status_code=response.status_code,
        headers=headers,
        media_type=ctype or None,
    )
    return _truncate(body), ctype, rebuilt


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: object,
        *,
        session_id: str,
        db_path: Path,
        source: str = "probe",
    ) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._sid = session_id
        self._db = Path(db_path)
        self._source = source

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        req_body = await _read_body_safe(request)
        response = await call_next(request)
        resp_body, ctype, rebuilt = await _capture_response(response)

        try:
            await asyncio.to_thread(
                self._write,
                request.method,
                request.url.path,
                request.url.query,
                rebuilt.status_code,
                req_body,
                resp_body,
                ctype,
            )
        except Exception as e:
            logger.debug("request_logger_write_failed", error=str(e))

        return rebuilt

    def _write(
        self,
        method: str,
        path: str,
        query_string: str,
        status_code: int,
        req_body: str,
        resp_body: str,
        ctype: str,
    ) -> None:
        conn = _open_conn(self._db)
        try:
            conn.execute(
                "INSERT INTO mock_requests "
                "(session_id, method, path, query_string, status_code, "
                " request_body_snippet, response_body_snippet, "
                " content_type, source) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self._sid,
                    method,
                    path,
                    query_string or None,
                    int(status_code),
                    req_body or None,
                    resp_body or None,
                    ctype or None,
                    self._source,
                ),
            )
            if (
                ctype.lower().startswith("application/json")
                and 200 <= int(status_code) < 400
            ):
                conn.execute(
                    "INSERT INTO mock_flow "
                    "(session_id, method, path, request_body, "
                    " response_body, status_code, source) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?) "
                    "ON CONFLICT(session_id, method, path) DO UPDATE SET "
                    "  request_body = excluded.request_body, "
                    "  response_body = excluded.response_body, "
                    "  status_code = excluded.status_code, "
                    "  source = excluded.source, "
                    "  recorded_at = datetime('now')",
                    (
                        self._sid,
                        method.upper(),
                        path,
                        req_body or None,
                        resp_body or "",
                        int(status_code),
                        self._source,
                    ),
                )
            conn.commit()
        finally:
            conn.close()
