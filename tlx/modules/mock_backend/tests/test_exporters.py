"""Tests for Phase 7D Task 7 exporters."""
from __future__ import annotations

import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from modules.mock_backend.core.fuzzing_seed_exporter import (
    export_burp_scope,
    export_ffuf,
)
from modules.mock_backend.core.hidden_endpoint_finder import (
    find_hidden,
)
from modules.mock_backend.core.openapi_exporter import export_openapi
from modules.mock_backend.core.reporter import (
    init_session_db,
    record_routes,
    record_session,
)
from modules.mock_backend.core.route_extractor import RouteSpec
from modules.mock_backend.core.stored_flow_replay import StoredFlowReplay


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    p = tmp_path / "mb.db"
    init_session_db(p).close()
    return p


# ── ffuf ─────────────────────────────────────────────────────────────


def test_export_ffuf_returns_paths_one_per_line(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/api/users", None, "{}")
    sfr.record("s1", "POST", "/api/admin", None, "{}")
    sfr.record("s1", "GET", "/api/users", None, "{}")  # duplicate
    out = export_ffuf("s1", db_path)
    lines = out.split("\n")
    assert "/api/users" in lines
    assert "/api/admin" in lines
    assert len(lines) == 2  # distinct only


def test_export_ffuf_empty_session(db_path: Path):
    assert export_ffuf("none", db_path) == ""


# ── burp scope ───────────────────────────────────────────────────────


def test_export_burp_scope_is_valid_xml(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/api/x", None, "{}")
    sfr.record("s1", "GET", "/api/y", None, "{}")
    xml = export_burp_scope("s1", db_path, host="example.com")
    root = ET.fromstring(xml)
    assert root.tag == "BurpSuite"
    items = root.findall("./target/scope/item")
    assert len(items) == 2


def test_export_burp_scope_correct_host(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/x", None, "{}")
    xml = export_burp_scope("s1", db_path, host="target.test")
    assert "<host>target.test</host>" in xml


def test_export_burp_scope_escapes_xml_metacharacters(db_path: Path):
    sfr = StoredFlowReplay(db_path)
    sfr.record("s1", "GET", "/x?a=<b>&c=d", None, "{}")
    xml = export_burp_scope("s1", db_path, host="ex.com")
    root = ET.fromstring(xml)
    items = root.findall("./target/scope/item")
    assert items
    file_text = items[0].findtext("file")
    assert "<b>" in file_text


# ── hidden endpoint finder ───────────────────────────────────────────


def test_find_hidden_returns_only_unknown_paths():
    known = [
        RouteSpec(url="/api/users", method="GET", shape_hint=None,
                  source_file="", source_line=0, sink_id=""),
    ]
    observed = [
        "http://127.0.0.1:5/api/users",
        "http://127.0.0.1:5/api/secret",
    ]
    out = find_hidden(known, observed)
    assert out == ["/api/secret"]


def test_find_hidden_returns_empty_when_all_known():
    known = [
        RouteSpec(url="/api/x", method="GET", shape_hint=None,
                  source_file="", source_line=0, sink_id=""),
        RouteSpec(url="/api/y", method="POST", shape_hint=None,
                  source_file="", source_line=0, sink_id=""),
    ]
    observed = [
        "http://127.0.0.1:1/api/x",
        "http://127.0.0.1:1/api/y",
    ]
    assert find_hidden(known, observed) == []


def test_find_hidden_dedups_observed():
    known: list = []
    observed = [
        "http://127.0.0.1:1/a",
        "http://127.0.0.1:1/a",
        "http://127.0.0.1:1/a?x=1",
    ]
    out = find_hidden(known, observed)
    assert out == ["/a"]


def test_find_hidden_handles_dict_routes():
    known = [{"url": "/api/x"}, {"path": "/api/z"}]
    observed = [
        "http://h/api/x",
        "http://h/api/y",
        "http://h/api/z",
    ]
    assert find_hidden(known, observed) == ["/api/y"]


def test_find_hidden_templated_route_matches_single_segment():
    known = [{"path": "/api/users/*/posts"}]
    observed = ["http://h/api/users/123/posts"]
    assert find_hidden(known, observed) == []


def test_find_hidden_templated_route_does_not_match_extra_segments():
    known = [{"path": "/api/users/*"}]
    observed = [
        "http://h/api/users/123",
        "http://h/api/users/123/profile",
    ]
    assert find_hidden(known, observed) == ["/api/users/123/profile"]


def test_find_hidden_multi_star_template_matches():
    known = [{"path": "/a/*/b/*/c"}]
    observed = ["http://h/a/x/b/y/c"]
    assert find_hidden(known, observed) == []


def test_find_hidden_star_does_not_cross_slashes():
    known = [{"path": "/api/*"}]
    observed = ["http://h/api/a/b"]
    assert find_hidden(known, observed) == ["/api/a/b"]


def test_find_hidden_mixed_templated_and_literal():
    known = [
        {"path": "/api/users/*/posts"},
        {"path": "/api/health"},
    ]
    observed = [
        "http://h/api/users/42/posts",
        "http://h/api/health",
        "http://h/api/secret",
    ]
    assert find_hidden(known, observed) == ["/api/secret"]


# ── openapi exporter ─────────────────────────────────────────────────


def test_export_openapi_includes_summary_block(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    try:
        record_session(conn, "s1", "/cg.db", "/proj")
        record_routes(conn, "s1", [
            RouteSpec(url="/api/x", method="GET", shape_hint=None,
                      source_file="a.js", source_line=1, sink_id="fetch_call"),
        ])
        conn.execute(
            "INSERT INTO mock_findings "
            "(session_id, chain_id, confirmed, probe_value, hits_json) "
            "VALUES ('s1', 'c-1', 1, 'p', '[]')"
        )
        conn.execute(
            "INSERT INTO mock_findings "
            "(session_id, chain_id, confirmed, probe_value, hits_json) "
            "VALUES ('s1', 'c-2', 0, 'p', '[]')"
        )
        conn.execute(
            "INSERT INTO mock_auth_obs (session_id, kind, key, value_snippet) "
            "VALUES ('s1', 'localStorage', 'jwt', 'xx')"
        )
        conn.commit()
    finally:
        conn.close()

    spec = export_openapi(db_path, "s1")
    assert spec["info"]["x-tlx-summary"] == {
        "session_id": "s1",
        "auth_observations": 1,
        "findings_total": 2,
        "findings_confirmed": 1,
    }
    assert "/api/x" in spec["paths"]
