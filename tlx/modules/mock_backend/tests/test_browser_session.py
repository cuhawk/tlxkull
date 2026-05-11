"""Tests for mock_backend browser_session (Phase 7B Task 4)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from modules.mock_backend.core.browser_session import (
    BrowserSession,
    ConfirmResult,
    _write_finding,
)
from modules.mock_backend.core.payload_injector import PayloadInjector
from modules.mock_backend.core.reporter import init_session_db, record_session
from modules.mock_backend.core.sink_monitor import SinkHit


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    p = tmp_path / "mb.db"
    init_session_db(p).close()
    return p


@pytest.fixture()
def session_seeded(db_path: Path) -> str:
    conn = sqlite3.connect(str(db_path))
    try:
        # use the open conn directly (record_session takes a connection)
        record_session(conn, "sess1", "/cg.db", "/proj")
    finally:
        conn.close()
    return "sess1"


def test_write_finding_inserts_row(db_path: Path, session_seeded: str):
    chain = {"chain_id": "c-1", "source_qname": "x::y", "sink_type": "innerHTML"}
    result = ConfirmResult(
        chain_id="c-1", confirmed=True,
        hits=[SinkHit(
            chain_id="c-1", sentinel="probe-xss-AAAA",
            sink_type="console", detail="leak", timestamp_ms=42.0,
        )],
        probe_value="probe-xss-AAAA",
        server_url="http://127.0.0.1:1234/",
    )
    _write_finding(db_path, session_seeded, chain, result)
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT session_id, chain_id, confirmed, probe_value, hits_json "
            "FROM mock_findings"
        ).fetchall()
    finally:
        conn.close()
    assert len(rows) == 1
    sid, cid, confirmed, probe_value, hits_json = rows[0]
    assert sid == session_seeded
    assert cid == "c-1"
    assert confirmed == 1
    assert probe_value == "probe-xss-AAAA"
    payload = json.loads(hits_json)
    assert payload[0]["sink_type"] == "console"


def test_write_finding_idempotent_on_rerun(db_path: Path, session_seeded: str):
    chain = {"chain_id": "c-2", "source_qname": "x"}
    result = ConfirmResult(
        chain_id="c-2", confirmed=False, hits=[],
        probe_value="p", server_url="",
    )
    _write_finding(db_path, session_seeded, chain, result)
    _write_finding(db_path, session_seeded, chain, result)
    _write_finding(db_path, session_seeded, chain, result)
    conn = sqlite3.connect(str(db_path))
    try:
        n = conn.execute(
            "SELECT COUNT(*) FROM mock_findings WHERE chain_id='c-2'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert n == 1


def test_write_finding_updates_confirmed_on_rerun(
    db_path: Path, session_seeded: str
):
    chain = {"chain_id": "c-3"}
    r1 = ConfirmResult(chain_id="c-3", confirmed=False, hits=[],
                      probe_value="p1")
    r2 = ConfirmResult(
        chain_id="c-3", confirmed=True,
        hits=[SinkHit("c-3", "p2", "console", "x", 1.0)],
        probe_value="p2",
    )
    _write_finding(db_path, session_seeded, chain, r1)
    _write_finding(db_path, session_seeded, chain, r2)
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT confirmed, probe_value FROM mock_findings "
            "WHERE chain_id='c-3'"
        ).fetchone()
    finally:
        conn.close()
    assert row[0] == 1
    assert row[1] == "p2"


@pytest.mark.asyncio
async def test_confirm_chain_with_hits_marks_confirmed_true(
    db_path: Path, session_seeded: str, monkeypatch: pytest.MonkeyPatch
):
    async def fake_observe(
        self: Any, app: Any, probe_spec: Any, chain_id: str
    ) -> tuple[list[SinkHit], str]:
        return (
            [SinkHit(
                chain_id=chain_id, sentinel=probe_spec.probe_value,
                sink_type="console", detail="leaked!", timestamp_ms=1.0,
            )],
            "http://127.0.0.1:9999/",
        )

    monkeypatch.setattr(BrowserSession, "_observe", fake_observe)

    bs = BrowserSession(db_path, PayloadInjector())
    chain = {
        "chain_id": "c-conf-1",
        "source_qname": "modules.app::input",
        "sink_type": "innerHTML",
    }
    result = await bs.confirm_chain(
        session_id=session_seeded, chain=chain,
        route_specs=[], dom_specs=[],
    )
    assert result.confirmed is True
    assert result.chain_id == "c-conf-1"
    assert len(result.hits) == 1
    assert result.probe_value.startswith("probe-xss-")
    assert result.server_url == "http://127.0.0.1:9999/"

    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT confirmed FROM mock_findings WHERE chain_id='c-conf-1'"
        ).fetchone()
    finally:
        conn.close()
    assert row[0] == 1


@pytest.mark.asyncio
async def test_confirm_chain_with_no_hits_marks_confirmed_false(
    db_path: Path, session_seeded: str, monkeypatch: pytest.MonkeyPatch
):
    async def fake_observe(
        self: Any, app: Any, probe_spec: Any, chain_id: str
    ) -> tuple[list[SinkHit], str]:
        return ([], "http://127.0.0.1:9999/")

    monkeypatch.setattr(BrowserSession, "_observe", fake_observe)

    bs = BrowserSession(db_path, PayloadInjector())
    chain = {"chain_id": "c-conf-2", "source_qname": "x"}
    result = await bs.confirm_chain(
        session_id=session_seeded, chain=chain,
        route_specs=[], dom_specs=[],
    )
    assert result.confirmed is False
    assert result.hits == []

    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT confirmed FROM mock_findings WHERE chain_id='c-conf-2'"
        ).fetchone()
    finally:
        conn.close()
    assert row[0] == 0


def test_confirm_result_dataclass_defaults():
    r = ConfirmResult(chain_id="x", confirmed=True)
    assert r.hits == []
    assert r.probe_value == ""
    assert r.server_url == ""
