"""mock_start / mock_stop tools — Phase 7D Task 8.

Boots/stops a per-session FastAPI mock server. Server stays running
until mock_stop is called; running state lives in
``kernel.services["mock_backend_servers"]`` (process-local).

Port is also written into ``mock_sessions.port`` for status queries.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
from typing import Any

import structlog

from ..core import pw_session, uvicorn_lifecycle
from ..core.mock_server import create_app
from ..core.reporter import get_routes, get_session, record_session
from ..core.response_factory import build_response

logger = structlog.get_logger(__name__)


async def _open_page_for_mock_start(kernel: Any, url: str) -> tuple[Any, Any]:
    """Return (page, async_close). Tests inject via ``mock_start_open_page``.

    Live path delegates to ``pw_session.open_page`` with the original
    ``wait_until="load"`` + 5s timeout used by ``_default_pw_factory``.
    """
    fake = kernel.services.get("mock_start_open_page")
    if fake is not None:
        return await fake(url)
    return await pw_session.open_page(
        url, wait_until="load", timeout_ms=5000,
    )


def _registry(kernel: Any) -> dict:
    reg = kernel.services.get("mock_backend_servers")
    if reg is None:
        reg = {}
        kernel.services.register("mock_backend_servers", reg)
    return reg


def _bg_loop(kernel: Any) -> Any:
    """Return a single long-running event loop, started in a thread.

    Slash-command dispatch uses ``asyncio.run`` which creates+destroys
    a fresh loop per call. Uvicorn servers booted there die as soon as
    the call returns. This loop persists for the kernel lifetime so
    booted servers stay alive between mock_start and mock_stop.
    """
    import threading

    loop = kernel.services.get("mock_backend_bg_loop")
    if loop is not None and loop.is_running():
        return loop

    new_loop = asyncio.new_event_loop()

    def _run() -> None:
        asyncio.set_event_loop(new_loop)
        new_loop.run_forever()

    t = threading.Thread(target=_run, daemon=True, name="mock-backend-loop")
    t.start()
    kernel.services.register("mock_backend_bg_loop", new_loop)
    kernel.services.register("mock_backend_bg_thread", t)
    return new_loop


async def _await_task(task: Any) -> None:
    try:
        await task
    except Exception:
        pass


def _maybe_stop_loop(kernel: Any, loop: Any) -> None:
    reg = kernel.services.get("mock_backend_servers") or {}
    if reg:
        return
    try:
        loop.call_soon_threadsafe(loop.stop)
    except Exception:
        pass


def _persist_port(db_conn: Any, session_id: str, port: int) -> None:
    db_conn.execute(
        "UPDATE mock_sessions SET port=?, mode='running' WHERE id=?",
        (int(port), session_id),
    )
    db_conn.commit()


def _list_known_sessions(db_conn: Any, limit: int = 10) -> list[str]:
    rows = db_conn.execute(
        "SELECT id FROM mock_sessions ORDER BY started DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [r[0] for r in rows]


async def mock_start_async(
    kernel: Any,
    session_id: str,
    port: int = 0,
    ad_hoc: bool = False,
) -> dict:
    if not session_id:
        return {"error": "session_id required"}

    db_conn = kernel.services.get("mock_backend_db")
    cfg = kernel.services.get("mock_backend_config")
    if db_conn is None or cfg is None:
        return {"error": "mock_backend not registered"}

    reg = _registry(kernel)
    if session_id in reg:
        info = reg[session_id]
        return {
            "port": info.get("port", 0),
            "url": info.get("url", ""),
            "already_running": True,
        }

    sess = get_session(db_conn, session_id)
    if sess is None:
        if not ad_hoc:
            existing = _list_known_sessions(db_conn, limit=10)
            hint = (
                "no such session"
                if not existing
                else f"known: {', '.join(existing)}"
            )
            return {
                "error": (
                    f"session '{session_id}' not found. "
                    f"{hint}. "
                    "Pass ad_hoc=True / --ad-hoc to create on the fly."
                )
            }
        record_session(db_conn, session_id, "", "")

    routes = get_routes(db_conn, session_id)
    workspace = cfg.workspace_dir_resolved / session_id
    workspace.mkdir(parents=True, exist_ok=True)
    html_path = workspace / "index.html"
    if html_path.exists():
        scaffolded = html_path.read_text(encoding="utf-8")
    else:
        scaffolded = "<!DOCTYPE html><html><body></body></html>"

    static_dir = workspace / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    def provider(route: Any, pid: str) -> Any:
        return build_response(route, pid, variant="default")

    app = create_app(
        session_id=session_id,
        scaffolded_html=scaffolded,
        static_dir=static_dir,
        routes=routes,
        response_provider=provider,
        probe_id="",
        db_path=cfg.db_path_resolved,
        request_log_source="extern",
    )

    server, serve_task, bound_port = await uvicorn_lifecycle.boot_app(app)
    if server is None or bound_port == 0:
        return {"error": "failed to bind server"}

    url = f"http://127.0.0.1:{bound_port}/"

    page: Any = None
    pw_close: Any = None
    try:
        page, pw_close = await _open_page_for_mock_start(kernel, url)
    except Exception as exc:
        logger.warning(
            "mock_start.pw_boot_failed",
            session_id=session_id, error=str(exc),
        )

    reg[session_id] = {
        "server": server,
        "serve_task": serve_task,
        "app": app,
        "port": bound_port,
        "url": url,
        "page": page,
        "pw_close": pw_close,
    }
    _persist_port(db_conn, session_id, bound_port)
    return {
        "port": bound_port,
        "url": url,
        "page_available": page is not None,
    }


async def mock_stop_async(kernel: Any, session_id: str) -> dict:
    if not session_id:
        return {"error": "session_id required"}
    reg = _registry(kernel)
    info = reg.pop(session_id, None)
    if info is None:
        return {"stopped": False, "reason": "not running"}
    pw_close = info.get("pw_close")
    if pw_close is not None:
        try:
            result = pw_close()
            if asyncio.iscoroutine(result):
                await result
        except Exception:
            pass
    server = info.get("server")
    serve_task = info.get("serve_task")
    bg_loop = info.get("loop")
    if server is None or serve_task is None:
        pass
    elif bg_loop is not None and bg_loop.is_running():
        server.should_exit = True
        try:
            fut = asyncio.run_coroutine_threadsafe(
                _await_task(serve_task), bg_loop,
            )
            fut.result(timeout=5.0)
        except Exception:
            pass
        _maybe_stop_loop(kernel, bg_loop)
    else:
        await uvicorn_lifecycle.shutdown(server, serve_task)
    db_conn = kernel.services.get("mock_backend_db")
    if db_conn is not None:
        try:
            db_conn.execute(
                "UPDATE mock_sessions SET port=0, mode='stopped' WHERE id=?",
                (session_id,),
            )
            db_conn.commit()
        except sqlite3.Error:
            pass
    return {"stopped": True}


def mock_start_handler(kernel: Any):
    async def _handle(session_id: str = "", port: int = 0) -> str:
        payload = await mock_start_async(kernel, session_id, port)
        return json.dumps(payload)

    return _handle


def mock_stop_handler(kernel: Any):
    async def _handle(session_id: str = "") -> str:
        payload = await mock_stop_async(kernel, session_id)
        return json.dumps(payload)

    return _handle
