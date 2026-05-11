"""Tests for StoredFlowReplay — Phase 7D Task 5."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.mock_backend.core.reporter import init_session_db
from modules.mock_backend.core.stored_flow_replay import StoredFlowReplay


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    p = tmp_path / "mb.db"
    init_session_db(p).close()
    return p


def test_record_inserts_mock_flow_row(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record(
        session_id="s1", method="GET", path="/api/users",
        request_body=None, response_body='{"data": [1, 2]}',
        status_code=200,
    )
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT method, path, response_body, status_code, source "
            "FROM mock_flow WHERE session_id='s1'"
        ).fetchall()
    finally:
        conn.close()
    assert rows == [
        ("GET", "/api/users", '{"data": [1, 2]}', 200, "record"),
    ]


def test_get_replay_handler_returns_body_on_match(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "POST", "/api/login", None,
               '{"token": "abc"}', 201)
    out = sfr.get_replay_handler("s1", "/api/login", "POST")
    assert out is not None
    assert out["body"] == {"token": "abc"}
    assert out["status_code"] == 201


def test_get_replay_handler_returns_none_on_miss(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/a", None, '{}')
    assert sfr.get_replay_handler("s1", "/missing", "GET") is None
    assert sfr.get_replay_handler("s2", "/a", "GET") is None
    assert sfr.get_replay_handler("s1", "/a", "POST") is None


def test_install_on_app_adds_routes_for_recorded_paths(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/api/x", None, '{"x":1}')
    sfr.record("s1", "POST", "/api/y", None, '{"y":2}', 201)

    app = FastAPI()
    added = sfr.install_on_app(app, "s1")
    assert added == 2

    client = TestClient(app)
    r = client.get("/api/x")
    assert r.status_code == 200
    assert r.json() == {"x": 1}
    r2 = client.post("/api/y")
    assert r2.status_code == 201
    assert r2.json() == {"y": 2}


def test_install_on_app_skips_existing_route(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/api/x", None, '{"replay":true}')
    app = FastAPI()

    @app.get("/api/x")
    async def existing() -> dict:
        return {"existing": True}

    added = sfr.install_on_app(app, "s1")
    assert added == 0

    client = TestClient(app)
    r = client.get("/api/x")
    assert r.json() == {"existing": True}


def test_install_on_app_returns_zero_when_no_recorded(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    app = FastAPI()
    assert sfr.install_on_app(app, "s-empty") == 0
