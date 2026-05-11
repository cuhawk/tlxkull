"""Phase 7E.2 — /mock-backend export slash subcommand."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.mock_backend.core.stored_flow_replay import StoredFlowReplay
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.module import _register
from modules.mock_backend.tests.test_core import (
    _build_kernel,
    _FakeCallGraph,
    _write_js,
)
from modules.mock_backend.ui import _handle_mock_backend


@pytest.fixture()
def project_root(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def cg(tmp_path: Path) -> _FakeCallGraph:
    return _FakeCallGraph(tmp_path / "cg.db")


def _setup(
    tmp_path: Path,
    project_root: Path,
    cg: _FakeCallGraph,
) -> tuple[object, MockBackendConfig, str]:
    rel = _write_js(project_root, "app.js", "fetch('/api/users');")
    nid = cg.add_node(file=rel, start=1, end=2)
    cg.add_tag(nid, "fetch_call", line=1)
    cg.commit()

    kernel = _build_kernel(tmp_path)
    kernel.services.register("js_analyzer_callgraph", cg)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    extract = next(t for t in reg.tools if t.name == "mock_extract")
    out = extract.handler(target_dir=str(project_root))
    sid = out.split("session_id:")[1].split("\n")[0].strip()
    return kernel, cfg, sid


def test_slash_export_ffuf_writes_file(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, cfg, sid = _setup(tmp_path, project_root, cg)
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record(sid, "GET", "/api/a", None, "{}")

    out = _handle_mock_backend(["export", sid, "ffuf"], kernel)
    assert "ffuf paths" in out
    assert (cfg.workspace_dir_resolved / sid / "paths.txt").is_file()


def test_slash_export_burp_with_host_flag(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, cfg, sid = _setup(tmp_path, project_root, cg)
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record(sid, "GET", "/api/x", None, "{}")

    _handle_mock_backend(
        ["export", sid, "burp", "--host", "target.test"], kernel,
    )
    scope = (cfg.workspace_dir_resolved / sid / "scope.xml").read_text(
        encoding="utf-8",
    )
    assert "<host>target.test</host>" in scope


def test_slash_export_usage_when_args_missing(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, _cfg, _sid = _setup(tmp_path, project_root, cg)
    out = _handle_mock_backend(["export"], kernel)
    assert "usage:" in out
