"""Tests for mock_probe auto-explore plumbing (Phase 7I)."""
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
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.tools.mock_probe import (
    mock_probe_async,
    mock_probe_handler,
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
        "mock_backend_db",
        sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


def _patch_loop(monkeypatch: pytest.MonkeyPatch, *,
                auto_added: int = 0) -> dict:
    captured: dict = {}

    async def fake_run(
        self: Any,
        session_id: str,
        route_specs: list,
        dom_specs: list,
        interactions: list,
        auto_explore: bool = False,
    ) -> DiscoveryResult:
        captured["auto_explore"] = auto_explore
        return DiscoveryResult(
            url="http://127.0.0.1:42/",
            interactions=[],
            sink_hits=[],
            new_routes=[],
            auto_explored=auto_explore,
            auto_added_count=auto_added if auto_explore else 0,
        )

    monkeypatch.setattr(ExecutionLoop, "run", fake_run)
    return captured


@pytest.mark.asyncio
async def test_mock_probe_auto_true_passes_through_to_execution_loop(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_loop(monkeypatch, auto_added=2)
    out = await mock_probe_async(kernel, "s1", [], auto=True)
    assert captured["auto_explore"] is True
    assert out["auto_explored"] is True
    assert out["auto_added_count"] == 2


@pytest.mark.asyncio
async def test_mock_probe_auto_false_default_does_not_trigger_enumeration(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_loop(monkeypatch, auto_added=99)
    out = await mock_probe_async(kernel, "s1", [])
    assert captured["auto_explore"] is False
    assert out["auto_explored"] is False
    assert out["auto_added_count"] == 0


@pytest.mark.asyncio
async def test_mock_probe_response_includes_auto_fields(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_loop(monkeypatch)
    out = await mock_probe_async(kernel, "s1", [])
    assert "auto_explored" in out
    assert "auto_added_count" in out


@pytest.mark.asyncio
async def test_mock_probe_handler_passes_auto_kwarg(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_loop(monkeypatch, auto_added=1)
    handler = mock_probe_handler(kernel)
    out_str = await handler(
        session_id="s1", interactions_json="", auto=True,
    )
    payload = json.loads(out_str)
    assert captured["auto_explore"] is True
    assert payload["auto_explored"] is True
    assert payload["auto_added_count"] == 1
