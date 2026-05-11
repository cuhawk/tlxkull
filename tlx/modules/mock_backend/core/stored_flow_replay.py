"""StoredFlowReplay — record/replay HTTP flows from SQLite.

Backs the per-session ``mock_flow`` table. Recording inserts a row;
replay rebuilds a deterministic FastAPI handler that returns the
stored ``response_body`` + ``status_code`` for a given (path, method).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from .reporter import _open_conn

logger = structlog.get_logger(__name__)


class StoredFlowReplay:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        return _open_conn(self.db_path)

    def record(
        self,
        session_id: str,
        method: str,
        path: str,
        request_body: str | None,
        response_body: str,
        status_code: int = 200,
        source: str = "record",
    ) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO mock_flow "
                "(session_id, method, path, request_body, response_body, "
                " status_code, source) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(session_id, method, path) DO UPDATE SET "
                "  request_body = excluded.request_body, "
                "  response_body = excluded.response_body, "
                "  status_code = excluded.status_code, "
                "  source = excluded.source, "
                "  recorded_at = datetime('now')",
                (
                    session_id,
                    method.upper(),
                    path,
                    request_body,
                    response_body,
                    int(status_code),
                    source,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def get_replay_handler(
        self,
        session_id: str,
        path: str,
        method: str,
    ) -> dict | None:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT response_body, status_code FROM mock_flow "
                "WHERE session_id=? AND path=? AND method=? "
                "ORDER BY id DESC LIMIT 1",
                (session_id, path, method.upper()),
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        body_text, status = row
        try:
            body: Any = json.loads(body_text) if body_text else None
        except Exception:
            body = body_text
        return {"body": body, "status_code": int(status)}

    def install_on_app(
        self,
        app: FastAPI,
        session_id: str,
    ) -> int:
        """Install replay routes for every distinct (method, path).

        Existing routes take priority — only adds a route if not present.
        Returns the number of new routes installed.
        """
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT DISTINCT method, path FROM mock_flow "
                "WHERE session_id=?",
                (session_id,),
            ).fetchall()
        finally:
            conn.close()

        existing: set[tuple[str, str]] = set()
        for r in app.routes:
            rpath = getattr(r, "path", None)
            rmethods = getattr(r, "methods", None) or set()
            if rpath:
                for m in rmethods:
                    existing.add((str(m).upper(), rpath))

        added = 0
        for method, path in rows:
            key = (str(method).upper(), str(path))
            if key in existing:
                continue
            self._add_route(app, session_id, str(path), str(method))
            added += 1
        return added

    def _add_route(
        self,
        app: FastAPI,
        session_id: str,
        path: str,
        method: str,
    ) -> None:
        replay = self

        async def _handler(request: Request) -> Response:
            data = replay.get_replay_handler(session_id, path, method)
            if data is None:
                return JSONResponse({"error": "no replay"}, status_code=404)
            body = data["body"]
            status = data["status_code"]
            if isinstance(body, (dict, list)):
                return JSONResponse(body, status_code=status)
            return Response(
                content=str(body) if body is not None else "",
                status_code=status,
            )

        app.add_api_route(path, _handler, methods=[method.upper()])
