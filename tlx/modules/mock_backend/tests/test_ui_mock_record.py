"""Slash-layer tests for /mock-backend record."""
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
from modules.mock_backend.ui import _handle_mock_backend


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


def _flow_rows(kernel: MagicMock) -> list[tuple]:
    db = kernel.services.get("mock_backend_db")
    return db.execute(
        "SELECT method, path, response_body, status_code "
        "FROM mock_flow WHERE session_id='s1'",
    ).fetchall()


def test_slash_record_writes_row(kernel: MagicMock):
    out = _handle_mock_backend(
        ["record", "s1", "GET", "/api/me", '{"role":"viewer"}'],
        kernel,
    )
    assert "recorded: GET /api/me" in out
    rows = _flow_rows(kernel)
    assert len(rows) == 1
    assert rows[0][0] == "GET"
    assert rows[0][1] == "/api/me"
    assert rows[0][2] == '{"role":"viewer"}'


def test_slash_record_with_status_flag(kernel: MagicMock):
    out = _handle_mock_backend(
        ["record", "s1", "POST", "/api/login", '{"token":"x"}',
         "--status", "201"],
        kernel,
    )
    assert "(status=201)" in out
    rows = _flow_rows(kernel)
    assert rows[0][3] == 201


def test_slash_record_usage_when_args_missing(kernel: MagicMock):
    out = _handle_mock_backend(["record"], kernel)
    assert "usage:" in out


def test_slash_record_invalid_status(kernel: MagicMock):
    out = _handle_mock_backend(
        ["record", "s1", "GET", "/x", "{}", "--status", "abc"],
        kernel,
    )
    assert "invalid status" in out
