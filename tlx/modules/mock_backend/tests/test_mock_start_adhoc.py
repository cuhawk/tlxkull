"""Tests for 7K.1 — mock_start ad-hoc gate."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
from modules.mock_backend.mock_backend_config import MockBackendConfig
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


def _kernel(tmp_path: Path, seed: list[str] | None = None) -> MagicMock:
    db = tmp_path / "mb.db"
    init_session_db(db).close()
    cfg = MockBackendConfig(
        db_path=str(db), workspace_dir=str(tmp_path / "ws"),
    )
    (tmp_path / "ws").mkdir(parents=True, exist_ok=True)
    if seed:
        conn = sqlite3.connect(str(db))
        for sid in seed:
            record_session(conn, sid, "", "")
        conn.close()
    k = MagicMock()
    k.services = _Services()
    k.services.register(
        "mock_backend_db",
        sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


async def _async_noop() -> None:
    return None


async def _fake_open(url: str) -> tuple[Any, Any]:
    return MagicMock(), _async_noop


@pytest.mark.asyncio
async def test_unknown_session_without_ad_hoc_returns_error(
    tmp_path: Path,
) -> None:
    k = _kernel(tmp_path, seed=["s1"])
    out = await mock_start_async(k, "typo")
    assert "error" in out
    assert "not found" in out["error"]


@pytest.mark.asyncio
async def test_unknown_session_error_lists_known_sessions(
    tmp_path: Path,
) -> None:
    k = _kernel(tmp_path, seed=["sa", "sb", "sc"])
    out = await mock_start_async(k, "missing")
    assert "error" in out
    msg = out["error"]
    assert "sa" in msg and "sb" in msg and "sc" in msg


@pytest.mark.asyncio
async def test_unknown_session_error_handles_empty_db(
    tmp_path: Path,
) -> None:
    k = _kernel(tmp_path)
    out = await mock_start_async(k, "anything")
    assert "error" in out
    assert "no such session" in out["error"]


@pytest.mark.asyncio
async def test_ad_hoc_true_creates_and_starts(tmp_path: Path) -> None:
    k = _kernel(tmp_path)
    k.services.register("mock_start_open_page", _fake_open)
    out = await mock_start_async(k, "fresh", ad_hoc=True)
    try:
        assert "error" not in out
        assert out["port"] > 0
        db = k.services.get("mock_backend_db")
        row = db.execute(
            "SELECT id FROM mock_sessions WHERE id=?", ("fresh",),
        ).fetchone()
        assert row is not None
    finally:
        await mock_stop_async(k, "fresh")


@pytest.mark.asyncio
async def test_known_session_works_without_ad_hoc(tmp_path: Path) -> None:
    k = _kernel(tmp_path, seed=["s1"])
    k.services.register("mock_start_open_page", _fake_open)
    out = await mock_start_async(k, "s1")
    try:
        assert "error" not in out
        assert out["port"] > 0
    finally:
        await mock_stop_async(k, "s1")
