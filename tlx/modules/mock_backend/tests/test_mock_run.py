"""Phase 7C Task 5 — batch confirmation in one server boot."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.mock_backend.core.browser_session import (
    BrowserSession,
    ConfirmResult,
)
from modules.mock_backend.core.payload_injector import PayloadInjector
from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
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
        record_session(conn, "sess1", "/cg.db", "/proj")
    finally:
        conn.close()
    return "sess1"


@pytest.mark.asyncio
async def test_run_all_chains_returns_one_result_per_chain(
    db_path: Path,
    session_seeded: str,
    monkeypatch: pytest.MonkeyPatch,
):
    boots = {"count": 0}

    async def fake_boot(self: Any, app: Any) -> str:
        boots["count"] += 1
        self._server = MagicMock()
        self._serve_task = AsyncMock()
        return "http://127.0.0.1:9999/"

    async def fake_shutdown(self: Any) -> None:
        self._server = None
        self._serve_task = None

    fake_observe = AsyncMock(return_value=[
        SinkHit("c", "p", "console", "leak", 1.0),
    ])

    monkeypatch.setattr(BrowserSession, "_boot_server", fake_boot)
    monkeypatch.setattr(BrowserSession, "_shutdown_server", fake_shutdown)

    chains = [
        {"chain_id": "c-1", "source_qname": "mod::a", "sink_type": "innerHTML"},
        {"chain_id": "c-2", "source_qname": "mod::b", "sink_type": "innerHTML"},
        {"chain_id": "c-3", "source_qname": "mod::c", "sink_type": "innerHTML"},
    ]

    bs = BrowserSession(db_path, PayloadInjector())
    with patch(
        "modules.mock_backend.core.browser_session.SinkMonitor"
    ) as mon_cls:
        mon_cls.return_value.observe = fake_observe
        results = await bs.run_all_chains(
            session_id=session_seeded,
            chains=chains,
            route_specs=[],
            dom_specs=[],
        )

    assert len(results) == 3
    assert all(r.confirmed for r in results)
    assert boots["count"] == 1


@pytest.mark.asyncio
async def test_run_all_chains_writes_one_finding_per_chain(
    db_path: Path,
    session_seeded: str,
    monkeypatch: pytest.MonkeyPatch,
):
    async def fake_boot(self: Any, app: Any) -> str:
        self._server = MagicMock()
        self._serve_task = AsyncMock()
        return "http://127.0.0.1:9999/"

    async def fake_shutdown(self: Any) -> None:
        self._server = None
        self._serve_task = None

    monkeypatch.setattr(BrowserSession, "_boot_server", fake_boot)
    monkeypatch.setattr(BrowserSession, "_shutdown_server", fake_shutdown)

    fake_observe = AsyncMock(return_value=[])

    chains = [
        {"chain_id": "x-1", "source_qname": "mod::a"},
        {"chain_id": "x-2", "source_qname": "mod::b"},
    ]

    bs = BrowserSession(db_path, PayloadInjector())
    with patch(
        "modules.mock_backend.core.browser_session.SinkMonitor"
    ) as mon_cls:
        mon_cls.return_value.observe = fake_observe
        await bs.run_all_chains(
            session_id=session_seeded,
            chains=chains,
            route_specs=[],
            dom_specs=[],
        )

    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT chain_id, confirmed FROM mock_findings "
            "WHERE session_id=? ORDER BY chain_id",
            (session_seeded,),
        ).fetchall()
    finally:
        conn.close()
    assert [r[0] for r in rows] == ["x-1", "x-2"]
    assert all(r[1] == 0 for r in rows)


@pytest.mark.asyncio
async def test_run_all_chains_empty_returns_empty():
    bs = BrowserSession(Path("/tmp/nope.db"), PayloadInjector())
    results = await bs.run_all_chains(
        session_id="s", chains=[], route_specs=[], dom_specs=[],
    )
    assert results == []


@pytest.mark.asyncio
async def test_mock_run_tool_returns_valid_json(
    db_path: Path, session_seeded: str, monkeypatch: pytest.MonkeyPatch,
):
    from modules.mock_backend.tools import mock_run as mr_mod

    cfg = MagicMock()
    cfg.db_path_resolved = db_path

    db_conn = MagicMock()
    cg = MagicMock()

    kernel = MagicMock()
    kernel.services.get.side_effect = lambda key: {
        "mock_backend_db":     db_conn,
        "mock_backend_config": cfg,
        "js_analyzer_callgraph": cg,
    }.get(key)

    fake_chains = [
        {"id": "c-1", "source": {"qname": "m::a"},
         "sink": {"taxonomy_id": "innerHTML"}},
        {"id": "c-2", "source": {"qname": "m::b"},
         "sink": {"taxonomy_id": "innerHTML"}},
    ]

    monkeypatch.setattr(mr_mod, "load_chains", lambda _cg: fake_chains)
    monkeypatch.setattr(mr_mod, "get_routes", lambda _c, _s: [])

    fake_results = [
        ConfirmResult(
            chain_id="c-1", confirmed=True,
            hits=[SinkHit("c-1", "p1", "console", "x", 1.0)],
            probe_value="p1", server_url="http://127.0.0.1:9999/",
        ),
        ConfirmResult(
            chain_id="c-2", confirmed=False, hits=[],
            probe_value="p2", server_url="http://127.0.0.1:9999/",
        ),
    ]

    async def fake_run_all_chains(self, **_kw):
        return fake_results

    monkeypatch.setattr(BrowserSession, "run_all_chains", fake_run_all_chains)

    handler = mr_mod.mock_run_handler(kernel)
    out = await handler(session_id=session_seeded)
    payload = json.loads(out)
    assert payload["session_id"] == session_seeded
    assert payload["total"] == 2
    assert payload["confirmed"] == 1
    assert len(payload["results"]) == 2
    assert payload["results"][0]["chain_id"] == "c-1"
    assert payload["results"][0]["confirmed"] is True


@pytest.mark.asyncio
async def test_mock_run_missing_session_id_returns_error():
    from modules.mock_backend.tools.mock_run import mock_run_async

    kernel = MagicMock()
    out = await mock_run_async(kernel, "")
    assert "error" in out


def test_mock_run_tool_registered_in_module():
    from modules.mock_backend.module import _build_tools

    kernel = MagicMock()
    tools = _build_tools(kernel)
    names = sorted(t.name for t in tools)
    assert "mock_run" in names
