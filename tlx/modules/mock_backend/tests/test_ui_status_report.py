"""Phase 7C Task 6 — /mock-backend status + report subcommands."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
from modules.mock_backend.ui import _handle_mock_backend


@pytest.fixture()
def db_with_session(tmp_path: Path) -> tuple[sqlite3.Connection, Path]:
    p = tmp_path / "mb.db"
    conn = init_session_db(p)
    record_session(conn, "sess-A", "/cg.db", "/proj")
    return conn, p


def _kernel_with(db: sqlite3.Connection) -> MagicMock:
    k = MagicMock()
    k.services.get.side_effect = lambda key: (
        db if key == "mock_backend_db" else None
    )
    return k


def _insert_finding(
    conn: sqlite3.Connection,
    session_id: str,
    chain_id: str,
    confirmed: int,
    hits: list[dict],
    probe: str = "p",
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO mock_findings "
        "(session_id, chain_id, confirmed, probe_value, hits_json) "
        "VALUES (?, ?, ?, ?, ?)",
        (session_id, chain_id, confirmed, probe, json.dumps(hits)),
    )
    conn.commit()


def test_status_with_no_findings_says_never(db_with_session):
    conn, _ = db_with_session
    kernel = _kernel_with(conn)
    out = _handle_mock_backend(["status", "sess-A"], kernel)
    assert "Total chains confirmed: 0 / 0" in out
    assert "Last run: never" in out


def test_status_counts_confirmed_correctly(db_with_session):
    conn, _ = db_with_session
    _insert_finding(conn, "sess-A", "c-1", 1, [{"sink_type": "console"}])
    _insert_finding(conn, "sess-A", "c-2", 0, [])
    _insert_finding(conn, "sess-A", "c-3", 1, [{"sink_type": "innerHTML"}])
    kernel = _kernel_with(conn)
    out = _handle_mock_backend(["status", "sess-A"], kernel)
    assert "Total chains confirmed: 2 / 3" in out
    assert "Last run: " in out and "never" not in out


def test_report_json_returns_valid_json(db_with_session):
    conn, _ = db_with_session
    _insert_finding(conn, "sess-A", "c-1", 1, [{"sink_type": "console"}])
    _insert_finding(conn, "sess-A", "c-2", 0, [])
    kernel = _kernel_with(conn)
    out = _handle_mock_backend(
        ["report", "sess-A", "--format", "json"], kernel,
    )
    payload = json.loads(out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    ids = {p["chain_id"] for p in payload}
    assert ids == {"c-1", "c-2"}


def test_report_text_default_lists_chains(db_with_session):
    conn, _ = db_with_session
    _insert_finding(conn, "sess-A", "c-1", 1, [{"sink_type": "console"}])
    _insert_finding(conn, "sess-A", "c-2", 0, [])
    kernel = _kernel_with(conn)
    out = _handle_mock_backend(["report", "sess-A"], kernel)
    assert "confirmed" in out.lower()
    assert "c-1" in out
    assert "c-2" in out
    assert "console" in out


def test_status_usage_when_no_session_id(db_with_session):
    conn, _ = db_with_session
    kernel = _kernel_with(conn)
    out = _handle_mock_backend(["status"], kernel)
    assert out.startswith("usage")


def test_report_usage_when_no_session_id(db_with_session):
    conn, _ = db_with_session
    kernel = _kernel_with(conn)
    out = _handle_mock_backend(["report"], kernel)
    assert out.startswith("usage")
