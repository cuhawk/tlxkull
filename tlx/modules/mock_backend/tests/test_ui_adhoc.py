"""Slash tests for 7K.1 — /mock-backend start --ad-hoc."""
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
from modules.mock_backend.ui import _HELP, _handle_mock_backend


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
    record_session(conn, "known", "/cg.db", "/proj")
    conn.close()
    k = MagicMock()
    k.services = _Services()
    k.services.register(
        "mock_backend_db", sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


def test_slash_start_unknown_session_errors_without_flag(
    kernel: MagicMock,
) -> None:
    out = _handle_mock_backend(["start", "ghost"], kernel)
    assert "[/mock-backend start]" in out
    assert "not found" in out


def test_slash_start_with_ad_hoc_flag_creates(
    kernel: MagicMock,
) -> None:
    try:
        out = _handle_mock_backend(
            ["start", "newone", "--ad-hoc"], kernel,
        )
        assert "Server running at http://127.0.0.1:" in out
        db = kernel.services.get("mock_backend_db")
        row = db.execute(
            "SELECT id FROM mock_sessions WHERE id=?", ("newone",),
        ).fetchone()
        assert row is not None
    finally:
        _handle_mock_backend(["stop", "newone"], kernel)


def test_slash_start_help_mentions_ad_hoc() -> None:
    assert "--ad-hoc" in _HELP
