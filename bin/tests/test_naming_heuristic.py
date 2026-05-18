"""Synthetic-fixture tests for bin/naming_heuristic.py.

Covers:
1. render_html rule fires on `renderHTML`, `setHTML`, etc.
2. unsafe_html rule fires on `unsafeInjectHtml`, `rawHtml`.
3. read_query source rule fires on `getQueryParam`, `parseUrlParam`.
4. Direct (non-implicit_naming) tag is never duplicated.
5. ``--rules`` subset gates which rules run.
6. Empty / non-matching names produce no tags.
7. ``persist()`` is idempotent across re-runs (clears prior naming rows).
8. Confidence below ``min_confidence`` is filtered.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN))

import naming_heuristic as nh  # noqa: E402


SCHEMA = """
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    qualified_name TEXT UNIQUE,
    file TEXT,
    name TEXT,
    parent TEXT,
    kind TEXT,
    start_line INT,
    end_line INT
);
CREATE TABLE node_tags (
    node_id INT NOT NULL,
    taxonomy_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    severity TEXT NOT NULL,
    line INT NOT NULL,
    source TEXT NOT NULL DEFAULT 'regex',
    confidence REAL NOT NULL DEFAULT 1.0,
    evidence TEXT,
    PRIMARY KEY (node_id, taxonomy_id, line)
);
"""


def _conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    return c


def _add_node(c, nid, qname, kind="function"):
    c.execute(
        "INSERT INTO nodes (id, qualified_name, file, name, parent, kind, "
        "start_line, end_line) "
        "VALUES (?, ?, ?, ?, NULL, ?, 1, 50)",
        (nid, qname, "app.js", qname.rsplit("::", 1)[-1], kind),
    )


def _add_tag(c, nid, tax_id, kind="sink", source="regex"):
    c.execute(
        "INSERT INTO node_tags "
        "(node_id, taxonomy_id, kind, severity, line, source, confidence) "
        "VALUES (?, ?, ?, ?, 1, ?, 1.0)",
        (nid, tax_id, kind, "high", source),
    )


# ── tests ──────────────────────────────────────────────────────────────


def test_render_html_rule_fires():
    c = _conn()
    _add_node(c, 1, "app.js::renderHTML")
    _add_node(c, 2, "app.js::setHTML")
    _add_node(c, 3, "app.js::appendMarkup")
    _add_node(c, 4, "app.js::doSomethingElse")
    c.commit()

    out = nh.discover(c)
    matched = {t.qname for t in out if t.rule_name == "render_html"}
    assert "app.js::renderHTML" in matched
    assert "app.js::setHTML" in matched
    assert "app.js::appendMarkup" in matched
    assert "app.js::doSomethingElse" not in matched


def test_unsafe_html_rule_fires():
    c = _conn()
    _add_node(c, 1, "app.js::unsafeInjectHtml")
    _add_node(c, 2, "app.js::rawHtmlAppend")
    c.commit()

    out = nh.discover(c)
    qnames = {t.qname for t in out if t.rule_name == "unsafe_html"}
    assert "app.js::unsafeInjectHtml" in qnames
    assert "app.js::rawHtmlAppend" in qnames


def test_read_query_source_fires():
    c = _conn()
    _add_node(c, 1, "app.js::getQueryParam")
    _add_node(c, 2, "app.js::parseUrlParam")
    _add_node(c, 3, "app.js::extractHashParam")
    c.commit()

    out = nh.discover(c)
    matches = [t for t in out if t.rule_name == "read_query"]
    qnames = {t.qname for t in matches}
    assert "app.js::getQueryParam" in qnames
    assert "app.js::parseUrlParam" in qnames
    assert "app.js::extractHashParam" in qnames
    # All read_query hits must be sources, not sinks.
    assert all(t.kind == "source" for t in matches)


def test_skips_already_tagged_taxonomy():
    c = _conn()
    _add_node(c, 1, "app.js::renderHTML")
    _add_tag(c, 1, "naming_render_html", source="regex")  # pre-existing direct
    c.commit()

    out = nh.discover(c)
    assert not any(
        t.node_id == 1 and t.taxonomy_id == "naming_render_html"
        for t in out
    )


def test_rules_subset_filters():
    c = _conn()
    _add_node(c, 1, "app.js::renderHTML")
    _add_node(c, 2, "app.js::getQueryParam")
    c.commit()

    out = nh.discover(c, enabled_rules=["render_html"])
    rules = {t.rule_name for t in out}
    assert rules == {"render_html"}


def test_empty_db_returns_no_tags():
    c = _conn()
    assert nh.discover(c) == []


def test_min_confidence_filter():
    c = _conn()
    _add_node(c, 1, "app.js::renderHTML")           # conf 0.4
    _add_node(c, 2, "app.js::execUserCode")          # conf 0.3
    c.commit()

    out_all = nh.discover(c)
    out_strict = nh.discover(c, min_confidence=0.4)
    confs_all = {round(t.confidence, 2) for t in out_all}
    confs_strict = {round(t.confidence, 2) for t in out_strict}
    assert 0.3 in confs_all
    assert 0.3 not in confs_strict
    assert 0.4 in confs_strict


def test_persist_idempotent():
    c = _conn()
    _add_node(c, 1, "app.js::renderHTML")
    c.commit()

    tags = nh.discover(c)
    s1 = nh.persist(c, tags)
    s2 = nh.persist(c, tags)
    assert s1["inserted"] >= 1
    assert s2["inserted"] == s1["inserted"]
    assert s2["cleared"] >= 1
    rows = c.execute(
        "SELECT node_id, taxonomy_id, source, confidence "
        "FROM node_tags WHERE source = 'implicit_naming'"
    ).fetchall()
    assert len(rows) == s2["inserted"]
    for _, _, source, conf in rows:
        assert source == "implicit_naming"
        assert 0.0 < conf < 1.0


def test_arrow_and_method_nodes_match():
    c = _conn()
    _add_node(c, 1, "Page::renderHTML", kind="method")
    _add_node(c, 2, "app::renderHTML", kind="arrow")
    c.commit()
    out = nh.discover(c)
    assert {t.node_id for t in out if t.rule_name == "render_html"} == {1, 2}


def test_non_function_nodes_ignored():
    c = _conn()
    _add_node(c, 1, "module.js::renderHTML", kind="program")
    c.commit()
    out = nh.discover(c)
    assert out == []


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failures = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as e:
            failures += 1
            print(f"FAIL {fn.__name__}: {e}")
            traceback.print_exc()
    if failures:
        sys.exit(1)
    print(f"\nAll {len(fns)} tests passed.")
