"""Tests for mock_record tool — Phase 7E.4."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.tools.mock_record import mock_record_async


class _Services:
    def __init__(self) -> None:
        self._reg: dict[str, Any] = {}

    def register(self, name: str, value: Any) -> None:
        self._reg[name] = value

    def get(self, name: str) -> Any:
        return self._reg.get(name)


@pytest.fixture()
def kernel(tmp_path: Path) -> MagicMock:
    db = tmp_path / "mb.db"
    init_session_db(db).close()
    cfg = MockBackendConfig(
        db_path=str(db), workspace_dir=str(tmp_path / "ws"),
    )
    (tmp_path / "ws").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    record_session(conn, "s1", "/cg.db", "/proj")
    conn.close()

    k = MagicMock()
    k.services = _Services()
    k.services.register(
        "mock_backend_db",
        sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


def _flow_rows(kernel: MagicMock, session_id: str = "s1") -> list[tuple]:
    db = kernel.services.get("mock_backend_db")
    return db.execute(
        "SELECT method, path, request_body, response_body, status_code "
        "FROM mock_flow WHERE session_id=?",
        (session_id,),
    ).fetchall()


@pytest.mark.asyncio
async def test_mock_record_inserts_row(kernel: MagicMock):
    out = await mock_record_async(
        kernel, "s1", "GET", "/api/me", '{"role":"viewer"}',
    )
    assert out["recorded"] is True
    assert out["method"] == "GET"
    rows = _flow_rows(kernel)
    assert len(rows) == 1
    method, path, _req, resp, status = rows[0]
    assert method == "GET"
    assert path == "/api/me"
    assert resp == '{"role":"viewer"}'
    assert status == 200


@pytest.mark.asyncio
async def test_mock_record_method_upper_cased(kernel: MagicMock):
    out = await mock_record_async(
        kernel, "s1", "get", "/api/x", '{"a":1}',
    )
    assert out["method"] == "GET"
    rows = _flow_rows(kernel)
    assert rows[0][0] == "GET"


@pytest.mark.asyncio
async def test_mock_record_default_status_200(kernel: MagicMock):
    await mock_record_async(
        kernel, "s1", "GET", "/api/x", '{"a":1}',
    )
    rows = _flow_rows(kernel)
    assert rows[0][4] == 200


@pytest.mark.asyncio
async def test_mock_record_explicit_status(kernel: MagicMock):
    out = await mock_record_async(
        kernel, "s1", "POST", "/api/login", '{"token":"x"}',
        status_code=201,
    )
    assert out["status_code"] == 201
    rows = _flow_rows(kernel)
    assert rows[0][4] == 201


@pytest.mark.asyncio
async def test_mock_record_session_not_found(kernel: MagicMock):
    out = await mock_record_async(
        kernel, "nope", "GET", "/x", "{}",
    )
    assert "error" in out
    assert "not found" in out["error"]
    rows = _flow_rows(kernel, session_id="nope")
    assert rows == []


@pytest.mark.asyncio
async def test_mock_record_non_json_body_stored_verbatim(kernel: MagicMock):
    body = "<html>plain text</html>"
    out = await mock_record_async(
        kernel, "s1", "GET", "/page", body,
    )
    assert out["recorded"] is True
    rows = _flow_rows(kernel)
    assert rows[0][3] == body


@pytest.mark.asyncio
async def test_mock_record_missing_required_returns_error(kernel: MagicMock):
    cases: list[tuple[str, str, str, str]] = [
        ("", "GET", "/x", "{}"),
        ("s1", "", "/x", "{}"),
        ("s1", "GET", "", "{}"),
        ("s1", "GET", "/x", ""),
    ]
    for sid, method, path, body in cases:
        out = await mock_record_async(kernel, sid, method, path, body)
        assert "error" in out, (sid, method, path, body)
    rows = _flow_rows(kernel)
    assert rows == []
