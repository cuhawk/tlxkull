"""Tests for mock_confirm tool + slash command (Phase 7B Task 5)."""
from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.mock_backend.core.browser_session import BrowserSession, ConfirmResult
from modules.mock_backend.core.sink_monitor import SinkHit
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.module import _register
from modules.mock_backend.tools import mock_confirm as mc


class _Services:
    def __init__(self) -> None:
        self._d: dict[str, object] = {}

    def register(self, name: str, obj: object) -> None:
        self._d[name] = obj

    def get(self, name: str, default: Any = None) -> Any:
        return self._d.get(name, default)


def _build_kernel() -> MagicMock:
    kernel = MagicMock()
    kernel.services = _Services()
    kernel.tools = MagicMock()
    kernel.tools.register = MagicMock()
    pending: list = []
    kernel.defer_slash_register = lambda cmd: pending.append(cmd)
    kernel._pending_slash = pending
    return kernel


class _FakeCG:
    def __init__(self, chains: list[dict]) -> None:
        self._chains = chains
        self.conn = sqlite3.connect(":memory:")


@pytest.fixture()
def kernel_with_module(tmp_path: Path) -> MagicMock:
    kernel = _build_kernel()
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    return kernel


def _seed_session(kernel: Any, session_id: str = "sess-1") -> str:
    db = kernel.services.get("mock_backend_db")
    db.execute(
        "INSERT INTO mock_sessions "
        "(id, cg_db_path, target, port, mode, started) "
        "VALUES (?, '/cg', '/p', 0, 'extract', '2026-05-08')",
        (session_id,),
    )
    db.commit()
    return session_id


def test_register_now_includes_mock_confirm(tmp_path: Path):
    kernel = _build_kernel()
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    names = {t.name for t in reg.tools}
    assert "mock_confirm" in names


def test_flatten_chain_extracts_source_qname_and_sink_type():
    chain = {
        "id": 7,
        "source": {"qname": "mod::handler", "line": 12,
                    "taxonomy_id": "proto_assign_direct"},
        "sink":   {"qname": "mod::sink", "line": 99,
                    "taxonomy_id": "innerHTML_assign"},
    }
    flat = mc._flatten_chain(chain)
    assert flat["source_qname"] == "mod::handler"
    assert flat["source_line"] == 12
    assert flat["sink_type"] == "innerHTML_assign"
    assert flat["chain_id"] == "7"


def test_find_chain_by_id_matches_int_or_string():
    chains = [{"id": 1}, {"id": 2}, {"id": 3}]
    assert mc.find_chain_by_id(chains, "2") == {"id": 2}
    assert mc.find_chain_by_id(chains, "missing") is None


def test_mock_confirm_async_errors_when_session_id_empty(
    kernel_with_module: Any
):
    kernel_with_module.services.register("js_analyzer_callgraph", _FakeCG([]))
    payload = asyncio.run(mc.mock_confirm_async(
        kernel_with_module, "", "1"
    ))
    assert "error" in payload


def test_mock_confirm_async_errors_when_js_analyzer_missing(
    kernel_with_module: Any
):
    payload = asyncio.run(mc.mock_confirm_async(
        kernel_with_module, "sess-1", "1"
    ))
    assert "error" in payload
    assert "js_analyzer" in payload["error"]


def test_mock_confirm_async_returns_confirmed_payload(
    kernel_with_module: Any, monkeypatch: pytest.MonkeyPatch
):
    sid = _seed_session(kernel_with_module, "sess-A")
    chain = {
        "id": 1,
        "source": {"qname": "m::src", "line": 1, "taxonomy_id": "proto_assign_direct"},
        "sink":   {"qname": "m::sink", "line": 5, "taxonomy_id": "innerHTML_assign"},
    }
    fake_cg = _FakeCG([chain])
    kernel_with_module.services.register("js_analyzer_callgraph", fake_cg)

    monkeypatch.setattr(mc, "load_chains", lambda cg: [chain])

    async def fake_confirm_chain(
        self: BrowserSession, session_id: str, chain: dict,
        route_specs: list, dom_specs: list,
    ) -> ConfirmResult:
        return ConfirmResult(
            chain_id=str(chain.get("chain_id", "")),
            confirmed=True,
            hits=[SinkHit(
                chain_id=str(chain.get("chain_id", "")),
                sentinel="probe-xss-AAAA",
                sink_type="console",
                detail="leaked", timestamp_ms=1.0,
            )],
            probe_value="probe-xss-AAAA",
            server_url="http://127.0.0.1:1234/",
        )

    monkeypatch.setattr(BrowserSession, "confirm_chain", fake_confirm_chain)

    payload = asyncio.run(mc.mock_confirm_async(
        kernel_with_module, sid, "1"
    ))
    assert payload["confirmed"] is True
    assert isinstance(payload["confirmed"], bool)
    assert payload["chain_id"] == "1"
    assert payload["probe_value"].startswith("probe-xss-")
    assert payload["server_url"].startswith("http://127.0.0.1:")
    assert isinstance(payload["hits"], list)
    assert payload["hits"][0]["sink_type"] == "console"


def test_mock_confirm_tool_handler_returns_valid_json(
    kernel_with_module: Any, monkeypatch: pytest.MonkeyPatch
):
    sid = _seed_session(kernel_with_module, "sess-B")
    chain = {
        "id": 2,
        "source": {"qname": "m::src", "line": 1, "taxonomy_id": "proto_assign_direct"},
        "sink":   {"qname": "m::sink", "line": 5, "taxonomy_id": "innerHTML_assign"},
    }
    fake_cg = _FakeCG([chain])
    kernel_with_module.services.register("js_analyzer_callgraph", fake_cg)
    monkeypatch.setattr(mc, "load_chains", lambda cg: [chain])

    async def fake_confirm_chain(
        self: BrowserSession, session_id: str, chain: dict,
        route_specs: list, dom_specs: list,
    ) -> ConfirmResult:
        return ConfirmResult(
            chain_id=str(chain.get("chain_id", "")),
            confirmed=False, hits=[],
            probe_value="probe-xss-ZZZZ",
            server_url="http://127.0.0.1:0/",
        )

    monkeypatch.setattr(BrowserSession, "confirm_chain", fake_confirm_chain)

    handler = mc.mock_confirm_handler(kernel_with_module)
    out = asyncio.run(handler(session_id=sid, chain_id="2"))
    parsed = json.loads(out)
    assert isinstance(parsed["confirmed"], bool)
    assert parsed["confirmed"] is False
    assert parsed["chain_id"] == "2"


def test_mock_confirm_chain_not_found_returns_error(
    kernel_with_module: Any, monkeypatch: pytest.MonkeyPatch
):
    sid = _seed_session(kernel_with_module, "sess-C")
    fake_cg = _FakeCG([])
    kernel_with_module.services.register("js_analyzer_callgraph", fake_cg)
    monkeypatch.setattr(mc, "load_chains", lambda cg: [])
    payload = asyncio.run(mc.mock_confirm_async(
        kernel_with_module, sid, "missing"
    ))
    assert "error" in payload
    assert "not found" in payload["error"]


def test_slash_confirm_with_chain_id_returns_json(
    kernel_with_module: Any, monkeypatch: pytest.MonkeyPatch
):
    from modules.mock_backend.ui import _slash_handler
    sid = _seed_session(kernel_with_module, "sess-D")
    chain = {
        "id": 3,
        "source": {"qname": "m::src", "line": 1, "taxonomy_id": "proto_assign_direct"},
        "sink":   {"qname": "m::sink", "line": 5, "taxonomy_id": "innerHTML_assign"},
    }
    fake_cg = _FakeCG([chain])
    kernel_with_module.services.register("js_analyzer_callgraph", fake_cg)

    from modules.mock_backend import ui as ui_mod
    monkeypatch.setattr(ui_mod, "load_chains", lambda cg: [chain])
    monkeypatch.setattr(mc, "load_chains", lambda cg: [chain])

    async def fake_confirm_chain(
        self: BrowserSession, session_id: str, chain: dict,
        route_specs: list, dom_specs: list,
    ) -> ConfirmResult:
        return ConfirmResult(
            chain_id="3", confirmed=True,
            hits=[], probe_value="p", server_url="u",
        )

    monkeypatch.setattr(BrowserSession, "confirm_chain", fake_confirm_chain)

    out = _slash_handler(f"confirm {sid} 3", kernel_with_module)
    payload = json.loads(out)
    assert payload["confirmed"] is True
    assert payload["chain_id"] == "3"


def test_slash_confirm_help_when_no_args(kernel_with_module: Any):
    from modules.mock_backend.ui import _slash_handler
    out = _slash_handler("confirm", kernel_with_module)
    assert "usage:" in out


@pytest.mark.asyncio
async def test_slash_confirm_all_chains_uses_single_boot(
    kernel_with_module: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    from modules.mock_backend.ui import _slash_handler

    sid = _seed_session(kernel_with_module, "sess-multi")
    chains = [
        {
            "id": i,
            "source": {"qname": f"m::s{i}", "line": 1,
                       "taxonomy_id": "proto_assign_direct"},
            "sink":   {"qname": f"m::k{i}", "line": 5,
                       "taxonomy_id": "innerHTML_assign"},
        }
        for i in range(1, 6)
    ]
    kernel_with_module.services.register(
        "js_analyzer_callgraph", _FakeCG(chains),
    )

    from modules.mock_backend import ui as ui_mod
    from modules.mock_backend.tools import mock_run as mr_mod
    monkeypatch.setattr(ui_mod, "load_chains", lambda cg: chains)
    monkeypatch.setattr(mr_mod, "load_chains", lambda cg: chains)

    boot_count = {"n": 0}

    async def fake_boot(self: Any, app: Any) -> str:
        boot_count["n"] += 1
        self._server = MagicMock()
        self._serve_task = AsyncMock()
        return "http://127.0.0.1:9999/"

    async def fake_shutdown(self: Any) -> None:
        self._server = None
        self._serve_task = None

    monkeypatch.setattr(BrowserSession, "_boot_server", fake_boot)
    monkeypatch.setattr(BrowserSession, "_shutdown_server", fake_shutdown)

    with patch(
        "modules.mock_backend.core.browser_session.SinkMonitor"
    ) as mon_cls:
        mon_cls.return_value.observe = AsyncMock(return_value=[])
        out = _slash_handler(f"confirm {sid}", kernel_with_module)

    assert boot_count["n"] == 1
    assert "chain_id" in out and "sink_type" in out
    for i in range(1, 6):
        assert f"  {i:>4} |" in out
