"""Tests for mock_probe interaction-kind validation (Phase 7E.9)."""
from __future__ import annotations

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
from modules.mock_backend.tools.mock_probe import mock_probe_async


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


def _patch_loop(monkeypatch: pytest.MonkeyPatch) -> dict:
    captured: dict = {}

    async def fake_run(
        self: Any,
        session_id: str,
        route_specs: list,
        dom_specs: list,
        interactions: list,
        auto_explore: bool = False,
    ) -> DiscoveryResult:
        captured["session_id"] = session_id
        captured["interactions"] = list(interactions)
        captured["auto_explore"] = auto_explore
        return DiscoveryResult(
            url="http://127.0.0.1:42/",
            interactions=[],
            sink_hits=[],
            new_routes=[],
        )

    monkeypatch.setattr(ExecutionLoop, "run", fake_run)
    return captured


@pytest.mark.asyncio
async def test_unknown_kinds_filtered_before_loop_run(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_loop(monkeypatch)
    interactions = [
        {"type": "click", "selector": "#a"},
        {"type": "frobnicate", "selector": "#b"},
    ]
    out = await mock_probe_async(kernel, "s1", interactions)
    assert len(captured["interactions"]) == 1
    assert captured["interactions"][0]["type"] == "click"
    assert out["unknown_interactions_count"] == 1
    assert out["unknown_interactions"][0]["type"] == "frobnicate"


@pytest.mark.asyncio
async def test_canonical_and_alias_kinds_both_accepted(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_loop(monkeypatch)
    interactions = [
        {"type": "fill", "selector": "#a", "value": "x"},
        {"type": "form_fill", "selector": "#b", "value": "y"},
        {"type": "postmessage", "selector": "*"},
        {"type": "post_message", "selector": "*"},
    ]
    out = await mock_probe_async(kernel, "s1", interactions)
    assert len(captured["interactions"]) == 4
    assert out["unknown_interactions"] == []
    assert out["unknown_interactions_count"] == 0


@pytest.mark.asyncio
async def test_non_dict_entries_marked_unknown(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_loop(monkeypatch)
    interactions: list[Any] = [
        {"type": "click", "selector": "#a"},
        "garbage",
        42,
        None,
    ]
    out = await mock_probe_async(kernel, "s1", interactions)
    assert len(captured["interactions"]) == 1
    assert captured["interactions"][0]["type"] == "click"
    assert out["unknown_interactions_count"] == 3
    reasons = [u.get("reason") for u in out["unknown_interactions"]]
    assert reasons == ["not a dict", "not a dict", "not a dict"]
    values = [u.get("value") for u in out["unknown_interactions"]]
    assert values == ["garbage", 42, None]


@pytest.mark.asyncio
async def test_case_insensitive_kind_match(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _patch_loop(monkeypatch)
    interactions = [
        {"type": "CLICK", "selector": "#a"},
        {"type": "Form_Fill", "selector": "#b", "value": "y"},
    ]
    out = await mock_probe_async(kernel, "s1", interactions)
    assert len(captured["interactions"]) == 2
    assert out["unknown_interactions_count"] == 0


@pytest.mark.asyncio
async def test_unknown_interactions_field_present_when_empty(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_loop(monkeypatch)
    out = await mock_probe_async(
        kernel, "s1", [{"type": "click", "selector": "#a"}]
    )
    assert "unknown_interactions" in out
    assert out["unknown_interactions"] == []
    assert "unknown_interactions_count" in out
    assert out["unknown_interactions_count"] == 0
