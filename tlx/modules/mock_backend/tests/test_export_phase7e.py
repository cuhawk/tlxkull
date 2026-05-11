"""Phase 7E.2 — mock_export tool ffuf/burp/hidden/openapi-summary."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest

from modules.mock_backend.core.stored_flow_replay import StoredFlowReplay
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.module import _register
from modules.mock_backend.tests.test_core import (
    _build_kernel,
    _FakeCallGraph,
    _write_js,
)


def _setup(
    tmp_path: Path,
    project_root: Path,
    cg: _FakeCallGraph,
) -> tuple[Any, MockBackendConfig, str, Any]:
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
    return kernel, cfg, sid, reg


def _export_tool(reg):
    return next(t for t in reg.tools if t.name == "mock_export")


@pytest.fixture()
def project_root(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def cg(tmp_path: Path) -> _FakeCallGraph:
    return _FakeCallGraph(tmp_path / "cg.db")


def test_export_ffuf_writes_paths_file(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, cfg, sid, reg = _setup(tmp_path, project_root, cg)
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record(sid, "GET", "/api/a", None, "{}")
    sfr.record(sid, "GET", "/api/b", None, "{}")

    export = _export_tool(reg)
    out = export.handler(session_id=sid, format="ffuf")
    assert "ffuf paths" in out

    paths_file = cfg.workspace_dir_resolved / sid / "paths.txt"
    assert paths_file.is_file()
    lines = paths_file.read_text(encoding="utf-8").split("\n")
    assert "/api/a" in lines
    assert "/api/b" in lines


def test_export_burp_writes_scope_xml_with_host(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, cfg, sid, reg = _setup(tmp_path, project_root, cg)
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record(sid, "GET", "/api/x", None, "{}")

    export = _export_tool(reg)
    out = export.handler(session_id=sid, format="burp", host="target.test")
    assert "host=target.test" in out

    scope_file = cfg.workspace_dir_resolved / sid / "scope.xml"
    assert scope_file.is_file()
    xml_text = scope_file.read_text(encoding="utf-8")
    root = ET.fromstring(xml_text)
    assert root.tag == "BurpSuite"
    assert "<host>target.test</host>" in xml_text


def test_export_burp_default_host_is_127(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, cfg, sid, reg = _setup(tmp_path, project_root, cg)
    sfr = StoredFlowReplay(cfg.db_path_resolved)
    sfr.record(sid, "GET", "/api/x", None, "{}")

    export = _export_tool(reg)
    export.handler(session_id=sid, format="burp")
    scope_file = cfg.workspace_dir_resolved / sid / "scope.xml"
    assert "<host>127.0.0.1</host>" in scope_file.read_text(encoding="utf-8")


def test_export_hidden_returns_observed_minus_known(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, cfg, sid, reg = _setup(tmp_path, project_root, cg)
    db = kernel.services.get("mock_backend_db")
    for path in ("/api/users", "/api/secret"):
        db.execute(
            "INSERT INTO mock_requests "
            "(session_id, method, path, status_code, source) "
            "VALUES (?, 'GET', ?, 200, 'probe')",
            (sid, path),
        )
    db.commit()

    export = _export_tool(reg)
    out = export.handler(session_id=sid, format="hidden")
    assert "(1)" in out

    hidden_file = cfg.workspace_dir_resolved / sid / "hidden.json"
    assert hidden_file.is_file()
    data = json.loads(hidden_file.read_text(encoding="utf-8"))
    assert data == ["/api/secret"]


def test_export_openapi_now_includes_summary(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph,
):
    kernel, cfg, sid, reg = _setup(tmp_path, project_root, cg)
    db = kernel.services.get("mock_backend_db")
    db.execute(
        "INSERT INTO mock_findings "
        "(session_id, chain_id, confirmed, probe_value, hits_json) "
        "VALUES (?, 'c-1', 1, 'p', '[]')",
        (sid,),
    )
    db.commit()

    export = _export_tool(reg)
    export.handler(session_id=sid, format="openapi")
    spec_path = cfg.workspace_dir_resolved / sid / "openapi.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    summary = spec["info"]["x-tlx-summary"]
    assert summary["findings_total"] == 1
    assert summary["findings_confirmed"] == 1
    assert summary["session_id"] == sid
