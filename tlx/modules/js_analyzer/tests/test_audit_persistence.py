"""Audit-run persistence tests (Phase 4F step 2)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from modules.js_analyzer.audit_persistence import AuditRun, _open_conn
from modules.js_analyzer.callgraph import SCHEMA


def _fresh_db(tmp_path: Path) -> sqlite3.Connection:
    db = tmp_path / "js_analyzer.db"
    conn = sqlite3.connect(str(db), check_same_thread=False)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def test_audit_run_lifecycle_persists_start_finish(tmp_path):
    conn = _fresh_db(tmp_path)
    run = AuditRun(conn, "session-A", "/tgt/folder")
    run_id = run.start()
    assert run_id > 0

    rows = conn.execute(
        "SELECT shell_session_id, target_folder, status, finished_at "
        "FROM js_audit_runs WHERE id=?",
        (run_id,),
    ).fetchone()
    assert rows[0] == "session-A"
    assert rows[1] == "/tgt/folder"
    assert rows[2] == "running"
    assert rows[3] is None

    run.finish("completed", total_tokens=1234, cost_usd=0.42,
               consults_used=2, consults_cost_usd=0.10)
    rows = conn.execute(
        "SELECT status, total_tokens, cost_usd, consults_used, "
        "       consults_cost_usd, failure_reason, finished_at "
        "FROM js_audit_runs WHERE id=?",
        (run_id,),
    ).fetchone()
    assert rows[0] == "completed"
    assert rows[1] == 1234
    assert rows[2] == pytest.approx(0.42)
    assert rows[3] == 2
    assert rows[4] == pytest.approx(0.10)
    assert rows[5] is None
    assert rows[6] is not None


def test_audit_turns_recorded_in_order_with_telemetry(tmp_path):
    conn = _fresh_db(tmp_path)
    run = AuditRun(conn, "s", "/t")
    run.start()
    run.append_turn("user", "hello", 0, 0, 0.0)
    run.append_turn("assistant",
                    [{"type": "text", "text": "hi"}],
                    tokens_in=10, tokens_out=5, cost_usd=0.01)
    run.append_turn("tool_result",
                    [{"type": "tool_result", "tool_use_id": "x", "content": "ok"}],
                    0, 0, 0.0)

    rows = conn.execute(
        "SELECT turn_index, role, content_json, tokens_in, tokens_out, cost_usd "
        "FROM js_audit_turns WHERE run_id=? ORDER BY turn_index",
        (run.run_id,),
    ).fetchall()
    assert [r[0] for r in rows] == [0, 1, 2]
    assert [r[1] for r in rows] == ["user", "assistant", "tool_result"]
    assert rows[0][2] == "hello"
    assert json.loads(rows[1][2]) == [{"type": "text", "text": "hi"}]
    assert rows[1][3] == 10
    assert rows[1][4] == 5
    assert rows[1][5] == pytest.approx(0.01)


def test_audit_run_failed_status_records_failure_reason(tmp_path):
    conn = _fresh_db(tmp_path)
    run = AuditRun(conn, "s", "/t")
    run.start()
    run.finish("failed", 0, 0.0, 0, 0.0, failure_reason="boom")
    row = conn.execute(
        "SELECT status, failure_reason FROM js_audit_runs WHERE id=?",
        (run.run_id,),
    ).fetchone()
    assert row == ("failed", "boom")


def test_audit_run_cap_exceeded_status_when_token_limit_hit(tmp_path):
    conn = _fresh_db(tmp_path)
    run = AuditRun(conn, "s", "/t")
    run.start()
    run.finish("cap_exceeded", 80_001, 4.20, 0, 0.0)
    row = conn.execute(
        "SELECT status, total_tokens FROM js_audit_runs WHERE id=?",
        (run.run_id,),
    ).fetchone()
    assert row[0] == "cap_exceeded"
    assert row[1] == 80_001


def test_multiple_runs_in_same_shell_session_have_distinct_run_ids(tmp_path):
    conn = _fresh_db(tmp_path)
    a = AuditRun(conn, "session-X", "/t1").start()
    b = AuditRun(conn, "session-X", "/t2").start()
    assert a != b
    n = conn.execute(
        "SELECT COUNT(*) FROM js_audit_runs WHERE shell_session_id=?",
        ("session-X",),
    ).fetchone()[0]
    assert n == 2


def test_run_finish_called_in_finally_on_exception(tmp_path):
    conn = _fresh_db(tmp_path)
    run = AuditRun(conn, "s", "/t")
    run.start()

    err: Exception | None = None
    try:
        try:
            raise RuntimeError("simulated")
        finally:
            run.finish("failed", 0, 0.0, 0, 0.0, failure_reason="simulated")
    except RuntimeError as e:
        err = e

    assert err is not None
    row = conn.execute(
        "SELECT status, failure_reason FROM js_audit_runs WHERE id=?",
        (run.run_id,),
    ).fetchone()
    assert row == ("failed", "simulated")


def test_open_conn_applies_pragmas(tmp_path):
    db = tmp_path / "x.db"
    sqlite3.connect(str(db)).close()
    conn = _open_conn(db)
    timeout = conn.execute("PRAGMA busy_timeout").fetchone()[0]
    sync = conn.execute("PRAGMA synchronous").fetchone()[0]
    assert timeout == 5000
    assert sync == 1  # NORMAL
