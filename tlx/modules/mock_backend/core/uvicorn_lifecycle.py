"""Shared uvicorn server lifecycle for per-session FastAPI mock servers.

Replaces three duplicated _boot_server / _shutdown_server pairs in
mock_start, browser_session, and execution_loop. Pure async; no
Playwright, no SQLite, no anthropic.
"""
from __future__ import annotations

import asyncio
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


async def boot_app(
    app: Any,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    log_level: str = "error",
    access_log: bool = False,
    lifespan: str = "off",
    poll_iterations: int = 200,
    poll_interval: float = 0.05,
) -> tuple[Any, Any, int]:
    """Boot a uvicorn server for ``app`` and return (server, serve_task, port).

    Polls ``server.started`` for up to ``poll_iterations * poll_interval``
    seconds. If the server doesn't start, requests exit and awaits the
    serve_task before returning ``(None, None, 0)``. Caller is responsible
    for shutting down via ``shutdown(server, serve_task)``.

    Port is extracted from ``server.servers[0].sockets[0].getsockname()[1]``.
    Returns 0 if extraction fails — caller decides whether 0 is acceptable.
    """
    import uvicorn

    config = uvicorn.Config(
        app, host=host, port=port,
        log_level=log_level, access_log=access_log, lifespan=lifespan,
    )
    server = uvicorn.Server(config)
    serve_task = asyncio.create_task(server.serve())

    for _ in range(poll_iterations):
        if server.started:
            break
        await asyncio.sleep(poll_interval)

    if not server.started:
        server.should_exit = True
        await serve_task
        return None, None, 0

    bound_port = 0
    try:
        servers = getattr(server, "servers", None) or []
        if servers and servers[0].sockets:
            bound_port = servers[0].sockets[0].getsockname()[1]
    except Exception:
        bound_port = 0

    return server, serve_task, bound_port


async def shutdown(
    server: Any,
    serve_task: Any,
    *,
    timeout: float = 5.0,
) -> None:
    """Shutdown a uvicorn server cleanly. Cancels serve_task if it doesn't
    exit within ``timeout`` seconds. Idempotent — None inputs are no-ops."""
    if server is None or serve_task is None:
        return
    server.should_exit = True
    try:
        await asyncio.wait_for(serve_task, timeout=timeout)
    except TimeoutError:
        serve_task.cancel()
