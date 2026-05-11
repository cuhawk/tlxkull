"""Phase 7F — `mock_authz` works without manual `mock_record` prime.

When middleware auto-captures probe/confirm responses into
`mock_flow`, the previously required `StoredFlowReplay.record()` call
is no longer needed. Verify the auto-prime path and the updated
error message.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.mock_backend.core.reporter import (
    init_session_db,
    record_session,
)
from modules.mock_backend.core.request_logger import (
    RequestLoggerMiddleware,
)
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.tools.mock_authz import mock_authz_async
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
        "mock_backend_db",
        sqlite3.connect(str(db), check_same_thread=False),
    )
    k.services.register("mock_backend_config", cfg)
    return k


def _drive_probe_traffic(db_path: Path, sid: str) -> None:
    """Hit a JSON endpoint via middleware to auto-prime mock_flow."""
    app = FastAPI()

    @app.get("/api/me")
    async def me() -> dict:
        return {"role": "viewer"}

    app.add_middleware(
        RequestLoggerMiddleware,
        session_id=sid,
        db_path=db_path,
        source="probe",
    )
    client = TestClient(app)
    r = client.get("/api/me")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_mock_authz_works_without_manual_record(
    kernel: MagicMock,
):
    cfg = kernel.services.get("mock_backend_config")
    _drive_probe_traffic(cfg.db_path_resolved, "s1")

    db = sqlite3.connect(str(cfg.db_path_resolved))
    try:
        rows = db.execute(
            "SELECT method, path, source FROM mock_flow "
            "WHERE session_id='s1'"
        ).fetchall()
    finally:
        db.close()
    assert rows == [("GET", "/api/me", "probe")]

    await mock_start_async(kernel, "s1")
    try:
        out = await mock_authz_async(kernel, "s1", "/api/me", "role")
    finally:
        await mock_stop_async(kernel, "s1")

    assert "error" not in out
    assert out["original_value"] == "viewer"
    assert out["flipped_value"] == "admin"


@pytest.mark.asyncio
async def test_authz_error_mentions_probe_before_record(
    kernel: MagicMock,
):
    await mock_start_async(kernel, "s1")
    try:
        out = await mock_authz_async(kernel, "s1", "/missing", "role")
    finally:
        await mock_stop_async(kernel, "s1")

    msg = out.get("error", "")
    p = msg.find("/mock-backend probe")
    r = msg.find("/mock-backend record")
    assert p != -1
    assert r != -1
    assert p < r
