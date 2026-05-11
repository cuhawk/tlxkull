"""Phase 7F — `mock_flow` UNIQUE(session_id, method, path) regression.

Prior to 7F, `StoredFlowReplay.record()` did a plain INSERT and could
leak rows when called multiple times for the same key. The unique
index + INSERT ... ON CONFLICT DO UPDATE gives us upsert semantics.

Also covers the legacy-DB migration path: a populated database without
a `source` column must continue to open, with pre-existing rows
defaulting to `source='record'`.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from modules.mock_backend.core.reporter import init_session_db
from modules.mock_backend.core.stored_flow_replay import StoredFlowReplay


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    p = tmp_path / "mb.db"
    init_session_db(p).close()
    return p


def _rows(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute(
            "SELECT method, path, response_body, status_code, source "
            "FROM mock_flow WHERE session_id='s1'"
        ).fetchall()
    finally:
        conn.close()


def test_duplicate_record_yields_one_row(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/api/me", None, '{"role":"viewer"}')
    sfr.record("s1", "GET", "/api/me", None, '{"role":"admin"}')
    rows = _rows(db_path)
    assert len(rows) == 1


def test_update_semantics_response_body_overwritten(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/api/me", None, '{"role":"viewer"}', 200)
    sfr.record("s1", "GET", "/api/me", None, '{"role":"admin"}', 201)
    rows = _rows(db_path)
    assert rows == [("GET", "/api/me", '{"role":"admin"}', 201, "record")]


def test_source_overwrites_on_upsert(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record(
        "s1", "GET", "/x", None, "{}", 200, source="record",
    )
    sfr.record(
        "s1", "GET", "/x", None, "{}", 200, source="probe",
    )
    rows = _rows(db_path)
    assert rows == [("GET", "/x", "{}", 200, "probe")]


def test_distinct_paths_keep_separate_rows(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/a", None, "{}")
    sfr.record("s1", "GET", "/b", None, "{}")
    sfr.record("s1", "POST", "/a", None, "{}")
    rows = _rows(db_path)
    assert len(rows) == 3


def test_legacy_db_without_source_column_migrates(tmp_path: Path):
    """ALTER TABLE adds source on re-open; existing rows get
    DEFAULT 'record'."""
    db_path = tmp_path / "legacy.db"
    legacy = sqlite3.connect(str(db_path))
    try:
        legacy.executescript(
            """
            CREATE TABLE mock_flow (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              method TEXT NOT NULL,
              path TEXT NOT NULL,
              request_body TEXT,
              response_body TEXT NOT NULL,
              status_code INTEGER DEFAULT 200,
              recorded_at TEXT DEFAULT (datetime('now'))
            );
            INSERT INTO mock_flow
              (session_id, method, path, request_body,
               response_body, status_code)
              VALUES ('s1', 'GET', '/old', NULL, '{}', 200);
            """
        )
        legacy.commit()
    finally:
        legacy.close()

    init_session_db(db_path).close()

    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT path, source FROM mock_flow WHERE session_id='s1'"
        ).fetchone()
    finally:
        conn.close()
    assert row == ("/old", "record")


def test_init_session_db_idempotent_on_reopen(tmp_path: Path):
    """Re-opening a fresh DB must not raise (ALTER would fail loud)."""
    db_path = tmp_path / "fresh.db"
    init_session_db(db_path).close()
    init_session_db(db_path).close()
    init_session_db(db_path).close()
