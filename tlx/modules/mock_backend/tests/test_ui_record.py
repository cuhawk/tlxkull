"""Tests for /mock-backend record body-file / body-stdin flags (Phase 7J)."""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

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


def _read_flow(cfg: MockBackendConfig, sid: str, path: str) -> tuple[Any, int]:
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    data = sfr.get_replay_handler(sid, path, "POST")
    assert data is not None
    return data["body"], data["status_code"]


def test_record_with_body_file_flag_reads_from_file(
    kernel: MagicMock, tmp_path: Path,
):
    payload_path = tmp_path / "body.json"
    payload_path.write_text(json.dumps({"x": 1}), encoding="utf-8")
    out = _handle_mock_backend(
        ["record", "s1", "POST", "/api/x",
         "--body-file", str(payload_path)],
        kernel,
    )
    assert "recorded:" in out
    cfg = kernel.services.get("mock_backend_config")
    body, status = _read_flow(cfg, "s1", "/api/x")
    assert body == {"x": 1}
    assert status == 200


def test_record_with_body_stdin_flag_reads_from_stdin(
    kernel: MagicMock, monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"y":2}'))
    out = _handle_mock_backend(
        ["record", "s1", "POST", "/api/y", "--body-stdin"],
        kernel,
    )
    assert "recorded:" in out
    cfg = kernel.services.get("mock_backend_config")
    body, _ = _read_flow(cfg, "s1", "/api/y")
    assert body == {"y": 2}


def test_record_both_flags_returns_error(
    kernel: MagicMock, tmp_path: Path,
):
    p = tmp_path / "b"
    p.write_text("{}", encoding="utf-8")
    out = _handle_mock_backend(
        ["record", "s1", "POST", "/api/x",
         "--body-file", str(p), "--body-stdin"],
        kernel,
    )
    assert "specify only one of" in out


def test_record_no_body_returns_usage(kernel: MagicMock):
    out = _handle_mock_backend(["record", "s1", "POST", "/api/x"], kernel)
    assert out.startswith("usage:")


def test_record_body_file_missing_returns_error(
    kernel: MagicMock, tmp_path: Path,
):
    missing = tmp_path / "nope.json"
    out = _handle_mock_backend(
        ["record", "s1", "POST", "/api/x", "--body-file", str(missing)],
        kernel,
    )
    assert "cannot read" in out


def test_record_positional_body_still_works(kernel: MagicMock):
    out = _handle_mock_backend(
        ["record", "s1", "POST", "/api/x", '{"z":3}'],
        kernel,
    )
    assert "recorded:" in out


def test_record_status_flag_with_body_file(
    kernel: MagicMock, tmp_path: Path,
):
    p = tmp_path / "b.json"
    p.write_text("{}", encoding="utf-8")
    _handle_mock_backend(
        ["record", "s1", "POST", "/api/s",
         "--body-file", str(p), "--status", "201"],
        kernel,
    )
    cfg = kernel.services.get("mock_backend_config")
    _, status = _read_flow(cfg, "s1", "/api/s")
    assert status == 201
