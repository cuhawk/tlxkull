"""Tests for mock_backend Phase 7A core."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from modules.mock_backend.core.dom_scaffolder import build_host_html
from modules.mock_backend.core.mock_server import (
    create_app,
    url_to_starlette_path,
)
from modules.mock_backend.core.reporter import (
    get_routes,
    get_session,
    init_session_db,
    record_routes,
    record_session,
    render_extract_summary,
    to_openapi,
)
from modules.mock_backend.core.response_factory import (
    PROBE_SENTINEL,
    build_response,
)
from modules.mock_backend.core.route_extractor import (
    HTTP_SINK_IDS,
    RouteSpec,
    extract_routes,
)
from modules.mock_backend.mock_backend_config import MockBackendConfig
from modules.mock_backend.module import MODULE, _register

# ── fake callgraph fixtures ──────────────────────────────────────────────


class _FakeCallGraph:
    """Minimal callgraph stub: in-memory SQLite with the columns we read.

    Includes only the nodes / node_tags / import_edges / variables tables
    that mock_backend reads — everything else is omitted to keep fixtures
    small.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.executescript("""
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            qualified_name TEXT, file TEXT, name TEXT, parent TEXT,
            kind TEXT, start_line INT, end_line INT
        );
        CREATE TABLE node_tags (
            node_id INT, taxonomy_id TEXT, kind TEXT, severity TEXT,
            line INT, source TEXT
        );
        CREATE TABLE import_edges (
            id INTEGER PRIMARY KEY, file TEXT, local_name TEXT,
            source_module TEXT, imported_name TEXT, line INT
        );
        CREATE TABLE variables (
            id INTEGER PRIMARY KEY, node_id INT, name TEXT, first_line INT
        );
        """)

    def add_node(
        self, *, file: str, name: str = "fn", start: int = 1, end: int = 100
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO nodes (qualified_name, file, name, kind, start_line, end_line) "
            "VALUES (?, ?, ?, 'function', ?, ?)",
            (f"{file}::{name}", file, name, start, end),
        )
        return cur.lastrowid  # type: ignore[return-value]

    def add_tag(self, node_id: int, taxonomy_id: str, line: int) -> None:
        self.conn.execute(
            "INSERT INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source) "
            "VALUES (?, ?, 'sink', 'medium', ?, 'ast')",
            (node_id, taxonomy_id, line),
        )

    def add_import(self, file: str, source_module: str) -> None:
        self.conn.execute(
            "INSERT INTO import_edges "
            "(file, local_name, source_module, imported_name, line) "
            "VALUES (?, 'X', ?, 'X', 1)",
            (file, source_module),
        )

    def commit(self) -> None:
        self.conn.commit()


@pytest.fixture()
def project_root(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def cg(tmp_path: Path) -> _FakeCallGraph:
    return _FakeCallGraph(tmp_path / "cg.db")


def _write_js(root: Path, rel: str, source: str) -> str:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return rel


# ── module registration ─────────────────────────────────────────────────


class _Services:
    def __init__(self) -> None:
        self._d: dict[str, object] = {}

    def register(self, name: str, obj: object) -> None:
        self._d[name] = obj

    def get(self, name: str, default=None):
        return self._d.get(name, default)


def _build_kernel(tmp_path: Path) -> MagicMock:
    kernel = MagicMock()
    kernel.services = _Services()
    kernel.tools = MagicMock()
    kernel.tools.register = MagicMock()
    pending: list = []
    kernel.defer_slash_register = lambda cmd: pending.append(cmd)
    kernel._pending_slash = pending
    return kernel


def test_register_creates_db_tables(tmp_path: Path):
    kernel = _build_kernel(tmp_path)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    db = kernel.services.get("mock_backend_db")
    tables = {
        r[0] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {"mock_sessions", "mock_routes", "mock_findings", "mock_auth_obs"}.issubset(tables)


def test_register_creates_workspace(tmp_path: Path):
    kernel = _build_kernel(tmp_path)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    assert (tmp_path / "ws").is_dir()


def test_register_registers_expected_tools(tmp_path: Path):
    kernel = _build_kernel(tmp_path)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    names = {t.name for t in reg.tools}
    assert names == {
        "mock_extract", "mock_export", "mock_confirm", "mock_run",
        "mock_start", "mock_stop", "mock_authz", "mock_auth", "mock_probe",
        "mock_record", "mock_observe",
    }


def test_register_registers_slash_command(tmp_path: Path):
    kernel = _build_kernel(tmp_path)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    _register(kernel, cfg)
    assert any(c.name == "mock-backend" for c in kernel._pending_slash)


def test_module_spec_basics():
    assert MODULE.name == "mock_backend"
    assert MODULE.config_schema is MockBackendConfig
    assert "js_analyzer" in MODULE.optional_deps


# ── route_extractor ─────────────────────────────────────────────────────


def test_route_extractor_finds_fetch_calls(project_root: Path, cg: _FakeCallGraph):
    rel = _write_js(project_root, "app.js",
                     "function go(){ fetch('/api/users'); }")
    nid = cg.add_node(file=rel, start=1, end=3)
    cg.add_tag(nid, "fetch_call", line=1)
    cg.commit()
    routes = extract_routes(cg, project_root)
    assert len(routes) == 1
    assert routes[0].url == "/api/users"
    assert routes[0].method == "GET"
    assert routes[0].sink_id == "fetch_call"


def test_route_extractor_finds_axios_method_calls(project_root: Path, cg: _FakeCallGraph):
    rel = _write_js(project_root, "app.js",
                     "axios.post('/api/login', {});")
    nid = cg.add_node(file=rel, start=1, end=2)
    cg.add_tag(nid, "axios_call", line=1)
    cg.commit()
    routes = extract_routes(cg, project_root)
    assert len(routes) == 1
    assert routes[0].url == "/api/login"
    assert routes[0].method == "POST"


def test_route_extractor_finds_xhr_open(project_root: Path, cg: _FakeCallGraph):
    rel = _write_js(project_root, "app.js",
                     "xhr.open('PUT', '/api/items/42');")
    nid = cg.add_node(file=rel, start=1, end=2)
    cg.add_tag(nid, "xhr_open_call", line=1)
    cg.commit()
    routes = extract_routes(cg, project_root)
    assert len(routes) == 1
    assert routes[0].url == "/api/items/42"
    assert routes[0].method == "PUT"


def test_route_extractor_replaces_template_interpolation_with_star(
    project_root: Path, cg: _FakeCallGraph
):
    rel = _write_js(project_root, "app.js",
                     "fetch(`/api/users/${id}/posts`);")
    nid = cg.add_node(file=rel, start=1, end=2)
    cg.add_tag(nid, "fetch_call", line=1)
    cg.commit()
    routes = extract_routes(cg, project_root)
    assert routes[0].url == "/api/users/*/posts"


def test_route_extractor_returns_empty_for_no_sinks(
    project_root: Path, cg: _FakeCallGraph
):
    cg.commit()
    routes = extract_routes(cg, project_root)
    assert routes == []


def test_route_extractor_method_in_options_object(
    project_root: Path, cg: _FakeCallGraph
):
    rel = _write_js(project_root, "app.js",
                     "fetch('/api/x', { method: 'DELETE' });")
    nid = cg.add_node(file=rel, start=1, end=2)
    cg.add_tag(nid, "fetch_call", line=1)
    cg.commit()
    routes = extract_routes(cg, project_root)
    assert routes[0].method == "DELETE"


def test_route_extractor_http_sink_ids_includes_known():
    expected = {"fetch_call", "fetch_with_user_input", "xhr_open_call",
                "axios_call", "ssrf_node_sink"}
    assert HTTP_SINK_IDS == frozenset(expected)


# ── dom_scaffolder ─────────────────────────────────────────────────────


def test_scaffolder_emits_react_root_when_react_tag_present(
    project_root: Path, cg: _FakeCallGraph
):
    cg.add_import("app.js", "react")
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert '<div id="root"></div>' in html_doc


def test_scaffolder_emits_vue_app_when_vue_tag_present(
    project_root: Path, cg: _FakeCallGraph
):
    cg.add_import("app.js", "vue")
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert '<div id="app"></div>' in html_doc


def test_scaffolder_emits_angular_root_when_angular_tag_present(
    project_root: Path, cg: _FakeCallGraph
):
    cg.add_import("app.js", "@angular/core")
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert "<app-root></app-root>" in html_doc


def test_scaffolder_includes_getElementById_targets(
    project_root: Path, cg: _FakeCallGraph
):
    rel = _write_js(project_root, "app.js",
                     "document.getElementById('user-name');")
    cg.add_node(file=rel, start=1, end=2)
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert '<div id="user-name"></div>' in html_doc


def test_scaffolder_includes_querySelector_class_and_id_targets(
    project_root: Path, cg: _FakeCallGraph
):
    rel = _write_js(project_root, "app.js",
                     "document.querySelector('#hero');"
                     "document.querySelector('.btn');")
    cg.add_node(file=rel, start=1, end=2)
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert '<div id="hero"></div>' in html_doc
    assert '<div class="btn"></div>' in html_doc


def test_scaffolder_emits_beacon_script(project_root: Path, cg: _FakeCallGraph):
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert "__tlxBeacon" in html_doc
    assert "TLX_BEACON:" in html_doc


def test_scaffolder_synthetic_form_when_form_used(
    project_root: Path, cg: _FakeCallGraph
):
    rel = _write_js(project_root, "app.js",
                     "const fd = new FormData(); document.forms[0];")
    cg.add_node(file=rel, start=1, end=2)
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert '<form id="tlx-form">' in html_doc
    assert 'name="email"' in html_doc


def test_scaffolder_emits_script_tags_for_entries(
    project_root: Path, cg: _FakeCallGraph
):
    (project_root / "package.json").write_text(
        json.dumps({"main": "index.js"}), encoding="utf-8"
    )
    (project_root / "index.js").write_text("// entry", encoding="utf-8")
    cg.commit()
    html_doc = build_host_html(cg, project_root)
    assert '<script src="/static/index.js"></script>' in html_doc


# ── response_factory ───────────────────────────────────────────────────


def test_response_factory_default_replaces_probe_sentinel():
    route = RouteSpec(
        url="/x", method="GET",
        shape_hint={"user": {"name": PROBE_SENTINEL, "id": 1}},
        source_file="app.js", source_line=1, sink_id="fetch_call",
    )
    out = build_response(route, "TLX42", variant="default")
    assert out == {"user": {"name": "TLX42", "id": 1}}


def test_response_factory_handles_none_shape_hint():
    route = RouteSpec(url="/x", method="GET", shape_hint=None,
                      source_file="", source_line=0, sink_id="fetch_call")
    out = build_response(route, "TLX42", variant="default")
    assert out == {"data": "TLX42"}


def test_response_factory_deep_xss_wraps_with_img_payload():
    route = RouteSpec(url="/x", method="GET", shape_hint={"v": PROBE_SENTINEL},
                      source_file="", source_line=0, sink_id="fetch_call")
    out = build_response(route, "TLX42", variant="deep_xss")
    assert out == {"v": 'TLX42<img src=x onerror=__tlxBeacon("TLX42")>'}


def test_response_factory_stub_variants_raise():
    route = RouteSpec(url="/x", method="GET", shape_hint=None,
                      source_file="", source_line=0, sink_id="fetch_call")
    for variant in ("admin_role", "pp_payload", "redirect"):
        with pytest.raises(NotImplementedError):
            build_response(route, "TLX42", variant=variant)


def test_response_factory_does_not_mutate_shape_hint():
    shape = {"a": PROBE_SENTINEL}
    route = RouteSpec(url="/x", method="GET", shape_hint=shape,
                      source_file="", source_line=0, sink_id="fetch_call")
    build_response(route, "TLX42", variant="default")
    assert shape == {"a": PROBE_SENTINEL}


# ── mock_server ────────────────────────────────────────────────────────


def _route(url: str, method: str = "GET") -> RouteSpec:
    return RouteSpec(url=url, method=method, shape_hint=None,
                     source_file="", source_line=0, sink_id="fetch_call")


def test_create_app_returns_fastapi_instance(tmp_path: Path):
    app = create_app(
        "sid", "<html></html>", tmp_path / "static",
        [], lambda r, p: {"ok": True}, "PROBE",
    )
    from fastapi import FastAPI
    assert isinstance(app, FastAPI)


def test_create_app_root_returns_scaffolded_html(tmp_path: Path):
    html_doc = "<html><body>HELLO</body></html>"
    app = create_app(
        "sid", html_doc, tmp_path / "static", [],
        lambda r, p: {"ok": True}, "PROBE",
    )
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "HELLO" in resp.text


def test_create_app_dispatches_routes_to_response_provider(tmp_path: Path):
    routes = [_route("/api/users")]
    captured: list[tuple] = []

    def provider(r: RouteSpec, probe: str):
        captured.append((r.url, probe))
        return {"hit": r.url, "probe": probe}

    app = create_app(
        "sid", "<html></html>", tmp_path / "static",
        routes, provider, "PROBE",
    )
    client = TestClient(app)
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert resp.json() == {"hit": "/api/users", "probe": "PROBE"}
    assert captured == [("/api/users", "PROBE")]


def test_create_app_two_calls_return_distinct_apps(tmp_path: Path):
    a1 = create_app("s1", "<a/>", tmp_path / "s1", [], lambda r, p: {}, "P")
    a2 = create_app("s2", "<a/>", tmp_path / "s2", [], lambda r, p: {}, "P")
    assert a1 is not a2


def test_url_to_starlette_path_translates_id_param():
    assert url_to_starlette_path("/users/:id") == "/users/{id}"


def test_url_to_starlette_path_translates_wildcards():
    assert url_to_starlette_path("/api/*/x/*") == "/api/{wild_0}/x/{wild_1}"


def test_url_to_starlette_path_strips_query():
    assert url_to_starlette_path("/api/x?a=1&b=2") == "/api/x"


# ── reporter ────────────────────────────────────────────────────────────


def test_init_session_db_creates_all_tables(tmp_path: Path):
    db = init_session_db(tmp_path / "mb.db")
    tables = {
        r[0] for r in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {"mock_sessions", "mock_routes", "mock_findings", "mock_auth_obs"}.issubset(tables)


def test_record_and_get_session_roundtrip(tmp_path: Path):
    db = init_session_db(tmp_path / "mb.db")
    record_session(db, "abc123", "/cg.db", "/proj", "/proj/index.html")
    s = get_session(db, "abc123")
    assert s is not None
    assert s["target"] == "/proj"
    assert s["scaffolded_html_path"] == "/proj/index.html"


def test_record_and_get_routes_roundtrip(tmp_path: Path):
    db = init_session_db(tmp_path / "mb.db")
    record_session(db, "abc", "/cg", "/p")
    routes = [
        RouteSpec(url="/x", method="GET", shape_hint={"a": 1},
                  source_file="app.js", source_line=10, sink_id="fetch_call"),
        RouteSpec(url="/y", method="POST", shape_hint=None,
                  source_file="app.js", source_line=20, sink_id="axios_call"),
    ]
    record_routes(db, "abc", routes)
    fetched = get_routes(db, "abc")
    assert len(fetched) == 2
    by_url = {r.url: r for r in fetched}
    assert by_url["/x"].shape_hint == {"a": 1}
    assert by_url["/y"].method == "POST"


def test_to_openapi_groups_methods_by_path():
    routes = [
        RouteSpec("/u", "GET", None, "", 0, "fetch_call"),
        RouteSpec("/u", "POST", None, "", 0, "fetch_call"),
        RouteSpec("/u/:id", "GET", None, "", 0, "fetch_call"),
    ]
    spec = to_openapi(routes)
    assert "/u" in spec["paths"]
    assert set(spec["paths"]["/u"].keys()) == {"get", "post"}
    assert "/u/{id}" in spec["paths"]


def test_render_extract_summary_lists_methods():
    routes = [
        RouteSpec("/a", "GET", None, "", 0, "fetch_call"),
        RouteSpec("/b", "GET", None, "", 0, "fetch_call"),
        RouteSpec("/c", "POST", None, "", 0, "axios_call"),
    ]
    out = render_extract_summary(routes)
    assert "GET: 2" in out
    assert "POST: 1" in out
    assert "fetch_call" in out


def test_render_extract_summary_empty_returns_zero():
    assert "0" in render_extract_summary([])


# ── tools ──────────────────────────────────────────────────────────────


def test_mock_extract_requires_js_analyzer_service(tmp_path: Path):
    kernel = _build_kernel(tmp_path)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    tool = next(t for t in reg.tools if t.name == "mock_extract")
    out = tool.handler(target_dir=str(tmp_path))
    assert "js_analyzer not initialised" in out


def test_mock_extract_creates_session_and_routes(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph
):
    rel = _write_js(project_root, "app.js", "fetch('/api/x');")
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
    tool = next(t for t in reg.tools if t.name == "mock_extract")
    out = tool.handler(target_dir=str(project_root))
    assert "session_id:" in out
    db = kernel.services.get("mock_backend_db")
    sessions = db.execute("SELECT id, target FROM mock_sessions").fetchall()
    assert len(sessions) == 1
    routes = db.execute("SELECT url, method FROM mock_routes").fetchall()
    assert ("/api/x", "GET") in routes


def test_mock_extract_writes_html_file(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph
):
    cg.commit()
    kernel = _build_kernel(tmp_path)
    kernel.services.register("js_analyzer_callgraph", cg)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    tool = next(t for t in reg.tools if t.name == "mock_extract")
    out = tool.handler(target_dir=str(project_root))
    line = next(line for line in out.splitlines() if line.startswith("scaffold:"))
    html_path = Path(line.split(": ", 1)[1].strip())
    assert html_path.is_file()
    text = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in text


def test_mock_export_openapi_writes_file(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph
):
    rel = _write_js(project_root, "app.js", "fetch('/api/x');")
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
    export = next(t for t in reg.tools if t.name == "mock_export")

    out_extract = extract.handler(target_dir=str(project_root))
    sid = out_extract.split("session_id:")[1].split("\n")[0].strip()
    out_export = export.handler(session_id=sid, format="openapi")
    assert "OpenAPI 3.1 written" in out_export
    spec_path = cfg.workspace_dir_resolved / sid / "openapi.json"
    assert spec_path.is_file()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    assert spec["openapi"].startswith("3.1")
    assert "/api/x" in spec["paths"]


def test_mock_export_unknown_format_returns_message(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph
):
    cg.commit()
    kernel = _build_kernel(tmp_path)
    kernel.services.register("js_analyzer_callgraph", cg)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    extract = next(t for t in reg.tools if t.name == "mock_extract")
    export = next(t for t in reg.tools if t.name == "mock_export")

    out_extract = extract.handler(target_dir=str(project_root))
    sid = out_extract.split("session_id:")[1].split("\n")[0].strip()
    # ffuf now writes a file (was: "Session 7D" placeholder)
    out_ffuf = export.handler(session_id=sid, format="ffuf")
    assert "ffuf paths" in out_ffuf
    # truly unknown still rejects
    out_unknown = export.handler(session_id=sid, format="weird")
    assert "unknown format" in out_unknown


def test_mock_export_session_not_found(tmp_path: Path):
    kernel = _build_kernel(tmp_path)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    export = next(t for t in reg.tools if t.name == "mock_export")
    out = export.handler(session_id="nope", format="openapi")
    assert "not found" in out


# ── end-to-end ─────────────────────────────────────────────────────────


def test_extract_then_export_roundtrip(
    tmp_path: Path, project_root: Path, cg: _FakeCallGraph
):
    _write_js(project_root, "app.js", "fetch('/api/users');")
    rel = "app.js"
    nid = cg.add_node(file=rel, start=1, end=2)
    cg.add_tag(nid, "fetch_call", line=1)
    cg.add_import("app.js", "react")
    cg.commit()

    kernel = _build_kernel(tmp_path)
    kernel.services.register("js_analyzer_callgraph", cg)
    cfg = MockBackendConfig(
        db_path=str(tmp_path / "mb.db"),
        workspace_dir=str(tmp_path / "ws"),
    )
    reg = _register(kernel, cfg)
    extract = next(t for t in reg.tools if t.name == "mock_extract")
    export = next(t for t in reg.tools if t.name == "mock_export")

    out_extract = extract.handler(target_dir=str(project_root))
    assert "Routes:" in out_extract
    sid = out_extract.split("session_id:")[1].split("\n")[0].strip()

    out_export = export.handler(session_id=sid, format="openapi")
    assert "OpenAPI" in out_export

    spec = json.loads(
        (cfg.workspace_dir_resolved / sid / "openapi.json").read_text()
    )
    assert "/api/users" in spec["paths"]
    assert "get" in spec["paths"]["/api/users"]


# ── slash command ─────────────────────────────────────────────────────


def test_slash_help_lists_subcommands(tmp_path: Path):
    from modules.mock_backend.ui import _slash_handler
    kernel = _build_kernel(tmp_path)
    out = _slash_handler("", kernel)
    assert "extract" in out
    assert "export" in out


def test_slash_unknown_subcommand_prints_help(tmp_path: Path):
    from modules.mock_backend.ui import _slash_handler
    kernel = _build_kernel(tmp_path)
    out = _slash_handler("nonsense", kernel)
    assert "unknown subcommand" in out
