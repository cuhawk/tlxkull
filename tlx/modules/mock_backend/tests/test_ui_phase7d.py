"""Tests for /mock-backend Phase 7D subcommands."""
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
        "mock_backend_db", sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


def test_unknown_subcommand_does_not_raise(kernel: MagicMock):
    out = _handle_mock_backend(["wat"], kernel)
    assert "unknown subcommand" in out


def test_help_prints_when_no_args(kernel: MagicMock):
    out = _handle_mock_backend([], kernel)
    assert "usage" in out.lower()


def test_start_then_stop_dispatch(kernel: MagicMock):
    out = _handle_mock_backend(["start", "s1"], kernel)
    assert "Server running at http://127.0.0.1:" in out
    out2 = _handle_mock_backend(["stop", "s1"], kernel)
    assert "Server stopped." in out2


def test_start_invalid_port_returns_error(kernel: MagicMock):
    out = _handle_mock_backend(["start", "s1", "abc"], kernel)
    assert "invalid arg" in out


def test_stop_when_not_running_returns_message(kernel: MagicMock):
    out = _handle_mock_backend(["stop", "ghost"], kernel)
    assert "[/mock-backend stop]" in out


def test_authz_dispatch_returns_table(kernel: MagicMock):
    cfg = kernel.services.get("mock_backend_config")
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record("s1", "GET", "/api/me", None,
               json.dumps({"role": "viewer"}))
    _handle_mock_backend(["start", "s1"], kernel)
    try:
        out = _handle_mock_backend(
            ["authz", "s1", "/api/me", "role"], kernel,
        )
    finally:
        _handle_mock_backend(["stop", "s1"], kernel)
    assert "route:" in out
    assert "viewer" in out
    assert "admin" in out


def test_authz_missing_args_prints_usage(kernel: MagicMock):
    out = _handle_mock_backend(["authz", "s1"], kernel)
    assert "usage:" in out


def test_auth_dispatch(kernel: MagicMock):
    class _P:
        context = type("C", (), {"cookies": staticmethod(lambda: [])})()
        def on(self, ev: str, h: Any) -> None: return None
        def goto(self, url: str, **kw: Any) -> None: return None
        def wait_for_timeout(self, ms: int) -> None: return None
        def evaluate(self, script: str, kind: str | None = None) -> Any:
            if kind == "localStorage":
                return [["k", "v"]]
            return []

    kernel.services.register("mock_auth_page", _P())
    out = _handle_mock_backend(
        ["auth", "s1", "http://x/"], kernel,
    )
    assert "observations:" in out


def test_auth_missing_args(kernel: MagicMock):
    out = _handle_mock_backend(["auth"], kernel)
    assert "usage:" in out


def test_probe_dispatch_no_interactions(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
):
    async def fake_run(self: Any, **kw: Any) -> DiscoveryResult:
        return DiscoveryResult(
            url="http://127.0.0.1:42/",
            interactions=[], sink_hits=[], new_routes=[],
        )
    monkeypatch.setattr(ExecutionLoop, "run", fake_run)

    out = _handle_mock_backend(["probe", "s1"], kernel)
    assert "interactions fired:" in out
    assert "sink hits:" in out
    assert "new routes:" in out


def test_probe_with_interactions_file(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    captured = {}

    async def fake_run(
        self: Any, session_id: str, route_specs: list,
        dom_specs: list, interactions: list,
        auto_explore: bool = False,
    ) -> DiscoveryResult:
        captured["interactions"] = list(interactions)
        captured["auto_explore"] = auto_explore
        return DiscoveryResult(
            url="", interactions=[], sink_hits=[], new_routes=[],
        )

    monkeypatch.setattr(ExecutionLoop, "run", fake_run)

    ifile = tmp_path / "i.json"
    ifile.write_text(json.dumps([
        {"type": "click", "selector": "#go"},
    ]))
    _handle_mock_backend(
        ["probe", "s1", "--interactions", str(ifile)], kernel,
    )
    assert captured["interactions"][0]["selector"] == "#go"


def test_probe_missing_session(kernel: MagicMock):
    out = _handle_mock_backend(["probe"], kernel)
    assert "usage:" in out


def test_probe_bad_interactions_file(
    kernel: MagicMock, tmp_path: Path
):
    bad = tmp_path / "bad.json"
    bad.write_text("not json{")
    out = _handle_mock_backend(
        ["probe", "s1", "--interactions", str(bad)], kernel,
    )
    assert "[/mock-backend probe]" in out


def test_probe_auto_flag_passes_through(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
):
    captured: dict = {}

    async def fake_run(
        self: Any, session_id: str, route_specs: list,
        dom_specs: list, interactions: list,
        auto_explore: bool = False,
    ) -> DiscoveryResult:
        captured["auto_explore"] = auto_explore
        return DiscoveryResult(
            url="http://127.0.0.1:42/",
            interactions=[], sink_hits=[], new_routes=[],
            auto_explored=auto_explore,
            auto_added_count=3 if auto_explore else 0,
        )

    monkeypatch.setattr(ExecutionLoop, "run", fake_run)

    out = _handle_mock_backend(["probe", "s1", "--auto"], kernel)
    assert captured["auto_explore"] is True
    assert "auto-added:" in out
    assert "3" in out


def test_probe_without_auto_flag_defaults_off(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
):
    captured: dict = {}

    async def fake_run(
        self: Any, session_id: str, route_specs: list,
        dom_specs: list, interactions: list,
        auto_explore: bool = False,
    ) -> DiscoveryResult:
        captured["auto_explore"] = auto_explore
        return DiscoveryResult(
            url="http://127.0.0.1:42/",
            interactions=[], sink_hits=[], new_routes=[],
        )

    monkeypatch.setattr(ExecutionLoop, "run", fake_run)

    out = _handle_mock_backend(["probe", "s1"], kernel)
    assert captured["auto_explore"] is False
    assert "auto-added:" not in out
