"""Phase 7F — `mock_export hidden` reads `mock_requests`, not `mock_flow`.

Filter on source IN ('probe', 'confirm') so curl traffic captured via
`mock_start` (`source='extern'`) is not treated as a hidden-endpoint
discovery signal.
"""
from __future__ import annotations

import json
from pathlib import Path

from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.module import _register
from modules.mock_backend.tests.test_core import (
    _build_kernel,
    _FakeCallGraph,
    _write_js,
)


def _setup(tmp_path: Path):
    project_root = tmp_path / "src"
    project_root.mkdir()
    cg = _FakeCallGraph(tmp_path / "cg.db")
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


def _export(reg):
    return next(t for t in reg.tools if t.name == "mock_export")


def _ins_request(db, sid: str, path: str, source: str) -> None:
    db.execute(
        "INSERT INTO mock_requests "
        "(session_id, method, path, status_code, source) "
        "VALUES (?, 'GET', ?, 200, ?)",
        (sid, path, source),
    )
    db.commit()


def test_probe_request_to_unknown_path_appears_in_hidden(
    tmp_path: Path,
):
    kernel, cfg, sid, reg = _setup(tmp_path)
    db = kernel.services.get("mock_backend_db")
    _ins_request(db, sid, "/api/secret", "probe")

    export = _export(reg)
    export.handler(session_id=sid, format="hidden")
    hidden_file = cfg.workspace_dir_resolved / sid / "hidden.json"
    assert json.loads(hidden_file.read_text(encoding="utf-8")) == [
        "/api/secret"
    ]


def test_extern_source_filtered_out_of_hidden(tmp_path: Path):
    kernel, cfg, sid, reg = _setup(tmp_path)
    db = kernel.services.get("mock_backend_db")
    _ins_request(db, sid, "/api/curl_noise", "extern")

    export = _export(reg)
    export.handler(session_id=sid, format="hidden")
    hidden_file = cfg.workspace_dir_resolved / sid / "hidden.json"
    assert json.loads(hidden_file.read_text(encoding="utf-8")) == []


def test_empty_mock_requests_returns_empty_list(tmp_path: Path):
    kernel, cfg, sid, reg = _setup(tmp_path)
    export = _export(reg)
    export.handler(session_id=sid, format="hidden")
    hidden_file = cfg.workspace_dir_resolved / sid / "hidden.json"
    assert json.loads(hidden_file.read_text(encoding="utf-8")) == []


def test_confirm_source_also_counted(tmp_path: Path):
    kernel, cfg, sid, reg = _setup(tmp_path)
    db = kernel.services.get("mock_backend_db")
    _ins_request(db, sid, "/api/from_confirm", "confirm")

    export = _export(reg)
    export.handler(session_id=sid, format="hidden")
    hidden_file = cfg.workspace_dir_resolved / sid / "hidden.json"
    assert json.loads(hidden_file.read_text(encoding="utf-8")) == [
        "/api/from_confirm"
    ]
