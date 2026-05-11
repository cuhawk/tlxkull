"""Tests for Phase 7D tools: mock_start, mock_stop, mock_authz,
mock_auth, mock_probe."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.mock_backend.core.execution_loop import (
    DiscoveryResult,
    ExecutionLoop,
)
from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
from modules.mock_backend.core.stored_flow_replay import StoredFlowReplay
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.tools.mock_auth import mock_auth_async
from modules.mock_backend.tools.mock_authz import mock_authz_async
from modules.mock_backend.tools.mock_probe import mock_probe_async
from modules.mock_backend.tools.mock_start import (
    mock_start_async,
    mock_stop_async,
)


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
        "mock_backend_db", sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


# ── mock_start / mock_stop ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_start_returns_port_and_url(kernel: MagicMock):
    out = await mock_start_async(kernel, "s1")
    assert out.get("port", 0) > 0
    assert out["url"].startswith("http://127.0.0.1:")
    stop = await mock_stop_async(kernel, "s1")
    assert stop["stopped"] is True


@pytest.mark.asyncio
async def test_mock_start_idempotent_when_already_running(kernel: MagicMock):
    a = await mock_start_async(kernel, "s1")
    b = await mock_start_async(kernel, "s1")
    assert a["port"] == b["port"]
    assert b.get("already_running") is True
    await mock_stop_async(kernel, "s1")


@pytest.mark.asyncio
async def test_mock_stop_when_not_running_returns_false(kernel: MagicMock):
    out = await mock_stop_async(kernel, "never-started")
    assert out["stopped"] is False


@pytest.mark.asyncio
async def test_mock_start_persists_port(kernel: MagicMock):
    out = await mock_start_async(kernel, "s1")
    db = kernel.services.get("mock_backend_db")
    row = db.execute(
        "SELECT port FROM mock_sessions WHERE id='s1'"
    ).fetchone()
    assert row[0] == out["port"]
    await mock_stop_async(kernel, "s1")


# ── mock_authz ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_authz_returns_flip_result(kernel: MagicMock):
    cfg = kernel.services.get("mock_backend_config")
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record("s1", "GET", "/api/me", None,
               json.dumps({"role": "viewer"}))
    await mock_start_async(kernel, "s1")
    try:
        out = await mock_authz_async(kernel, "s1", "/api/me", "role")
    finally:
        await mock_stop_async(kernel, "s1")
    assert out["original_value"] == "viewer"
    assert out["flipped_value"] == "admin"
    assert "ui_diff" in out
    assert out["route"] == "/api/me"


@pytest.mark.asyncio
async def test_mock_authz_errors_when_no_stored_flow(kernel: MagicMock):
    await mock_start_async(kernel, "s1")
    try:
        out = await mock_authz_async(kernel, "s1", "/missing", "role")
    finally:
        await mock_stop_async(kernel, "s1")
    assert "error" in out


@pytest.mark.asyncio
async def test_mock_authz_errors_when_server_not_running(kernel: MagicMock):
    cfg = kernel.services.get("mock_backend_config")
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record("s1", "GET", "/api/x", None, json.dumps({"role": "viewer"}))
    out = await mock_authz_async(kernel, "s1", "/api/x", "role")
    assert "error" in out


# ── mock_auth ───────────────────────────────────────────────────────


class _AuthFakePage:
    def __init__(self) -> None:
        self.context = type("C", (), {"cookies": staticmethod(lambda: [])})()

    def on(self, ev: str, h: Any) -> None:
        return None

    def goto(self, url: str, **kw: Any) -> None:
        return None

    def wait_for_timeout(self, ms: int) -> None:
        return None

    def evaluate(self, script: str, kind: str | None = None) -> Any:
        if kind == "localStorage":
            return [["jwt", "abcdef"]]
        return []


@pytest.mark.asyncio
async def test_mock_auth_returns_observations_and_persists(
    kernel: MagicMock,
):
    kernel.services.register("mock_auth_page", _AuthFakePage())
    out = await mock_auth_async(kernel, "s1", "http://x/")
    assert "observations" in out
    assert out["count"] >= 1
    cfg = kernel.services.get("mock_backend_config")
    conn = sqlite3.connect(str(cfg.db_path_resolved))
    try:
        n = conn.execute(
            "SELECT COUNT(*) FROM mock_auth_obs WHERE session_id='s1'"
        ).fetchone()[0]
    finally:
        conn.close()
    assert n == out["count"]


@pytest.mark.asyncio
async def test_mock_auth_returns_error_on_missing_args(kernel: MagicMock):
    out = await mock_auth_async(kernel, "", "")
    assert "error" in out


# ── mock_probe ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_probe_runs_execution_loop(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
):
    captured: dict = {}

    async def fake_run(self: Any, session_id: str, route_specs: list,
                       dom_specs: list, interactions: list,
                       auto_explore: bool = False) -> DiscoveryResult:
        captured["session_id"] = session_id
        captured["interactions"] = list(interactions)
        return DiscoveryResult(
            url="http://127.0.0.1:42/", interactions=[],
            sink_hits=[], new_routes=["http://127.0.0.1:42/api/secret"],
        )

    monkeypatch.setattr(ExecutionLoop, "run", fake_run)

    interactions = [{"type": "click", "selector": "#go"}]
    out = await mock_probe_async(kernel, "s1", interactions)
    assert captured["session_id"] == "s1"
    assert captured["interactions"] == interactions
    assert out["new_routes_count"] == 1
    assert out["url"] == "http://127.0.0.1:42/"
