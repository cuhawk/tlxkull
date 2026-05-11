"""Tests for RequestLoggerMiddleware — Phase 7F."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.testclient import TestClient

from modules.mock_backend.core.reporter import init_session_db
from modules.mock_backend.core.request_logger import (
    _BODY_SNIPPET_MAX,
    RequestLoggerMiddleware,
)


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    p = tmp_path / "mb.db"
    init_session_db(p).close()
    return p


def _build_app(
    db_path: Path,
    *,
    sid: str = "s1",
    source: str = "probe",
) -> FastAPI:
    app = FastAPI()

    @app.get("/api/items")
    async def items() -> dict:
        return {"items": [1, 2, 3]}

    @app.post("/api/echo")
    async def echo(request) -> dict:  # type: ignore[no-untyped-def]
        body = await request.body()
        return {"len": len(body)}

    @app.get("/forbidden")
    async def forbidden() -> JSONResponse:
        return JSONResponse({"err": "no"}, status_code=403)

    @app.get("/text")
    async def text() -> PlainTextResponse:
        return PlainTextResponse("hello world")

    app.add_middleware(
        RequestLoggerMiddleware,
        session_id=sid,
        db_path=db_path,
        source=source,
    )
    return app


def _rows(db_path: Path, table: str, sid: str = "s1") -> list:
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(
            f"SELECT * FROM {table} WHERE session_id=?",
            (sid,),
        ).fetchall()
    finally:
        conn.close()


def test_middleware_writes_mock_requests_row_on_each_request(
    db_path: Path,
):
    client = TestClient(_build_app(db_path))
    r = client.get("/api/items")
    assert r.status_code == 200
    rows = _rows(db_path, "mock_requests")
    assert len(rows) == 1


def test_middleware_writes_one_row_per_request(db_path: Path):
    client = TestClient(_build_app(db_path))
    client.get("/api/items")
    client.get("/api/items")
    client.get("/forbidden")
    assert len(_rows(db_path, "mock_requests")) == 3


def test_request_body_snippet_truncated(db_path: Path):
    client = TestClient(_build_app(db_path))
    big = "x" * (_BODY_SNIPPET_MAX + 5000)
    client.post("/api/echo", content=big)
    conn = sqlite3.connect(str(db_path))
    try:
        snippet = conn.execute(
            "SELECT request_body_snippet FROM mock_requests "
            "WHERE path='/api/echo'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert len(snippet) == _BODY_SNIPPET_MAX


def test_response_body_snippet_truncated(db_path: Path):
    app = FastAPI()

    big = "y" * (_BODY_SNIPPET_MAX + 5000)

    @app.get("/big")
    async def big_handler() -> PlainTextResponse:
        return PlainTextResponse(big)

    app.add_middleware(
        RequestLoggerMiddleware,
        session_id="s1",
        db_path=db_path,
        source="probe",
    )
    client = TestClient(app)
    r = client.get("/big")
    assert r.text == big
    conn = sqlite3.connect(str(db_path))
    try:
        snippet = conn.execute(
            "SELECT response_body_snippet FROM mock_requests "
            "WHERE path='/big'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert len(snippet) == _BODY_SNIPPET_MAX


def test_json_2xx_writes_both_mock_requests_and_mock_flow(
    db_path: Path,
):
    client = TestClient(_build_app(db_path))
    client.get("/api/items")
    assert len(_rows(db_path, "mock_requests")) == 1
    assert len(_rows(db_path, "mock_flow")) == 1

    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT method, path, source, status_code FROM mock_flow"
        ).fetchone()
    finally:
        conn.close()
    assert row == ("GET", "/api/items", "probe", 200)


def test_json_4xx_writes_only_mock_requests(db_path: Path):
    client = TestClient(_build_app(db_path))
    client.get("/forbidden")
    assert len(_rows(db_path, "mock_requests")) == 1
    assert len(_rows(db_path, "mock_flow")) == 0


def test_non_json_response_writes_only_mock_requests(db_path: Path):
    client = TestClient(_build_app(db_path))
    client.get("/text")
    assert len(_rows(db_path, "mock_requests")) == 1
    assert len(_rows(db_path, "mock_flow")) == 0


def test_middleware_exception_during_write_does_not_break_response(
    db_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    from modules.mock_backend.core import request_logger

    def boom(*args, **kwargs):
        raise RuntimeError("simulated db failure")

    monkeypatch.setattr(
        request_logger.RequestLoggerMiddleware,
        "_write",
        boom,
    )
    client = TestClient(_build_app(db_path))
    r = client.get("/api/items")
    assert r.status_code == 200
    assert r.json() == {"items": [1, 2, 3]}


@pytest.mark.parametrize("source", ["probe", "confirm", "extern"])
def test_source_param_flows_through(db_path: Path, source: str):
    client = TestClient(_build_app(db_path, source=source))
    client.get("/api/items")
    conn = sqlite3.connect(str(db_path))
    try:
        req_src = conn.execute(
            "SELECT source FROM mock_requests WHERE path='/api/items'"
        ).fetchone()[0]
        flow_src = conn.execute(
            "SELECT source FROM mock_flow WHERE path='/api/items'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert req_src == source
    assert flow_src == source
