"""Synthetic-fixture unit tests for implicit_tags closure expander.

Covers:
1. Sink back-propagation along resolved edges (1 hop, 2 hops).
2. Source forward-propagation along resolved edges.
3. Decay 0.7 ** hop confidence.
4. Direct tags are never overridden.
5. ``persist()`` is idempotent across re-runs.
6. ``max_hops=0`` returns no tags.
7. Dynamic/unresolved edges are ignored.
8. Per-(node, taxonomy) shortest path wins (higher confidence kept).
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tlx"))

from modules.js_analyzer.implicit_tags import (  # noqa: E402
    DEFAULT_DECAY,
    IMPLICIT_CLOSURE_SOURCE,
    discover,
    persist,
)


SCHEMA = """
CREATE TABLE nodes (
    id             INTEGER PRIMARY KEY,
    qualified_name TEXT UNIQUE,
    file           TEXT,
    name           TEXT,
    parent         TEXT,
    kind           TEXT,
    start_line     INT,
    end_line       INT
);
CREATE TABLE edges (
    caller_id     INT NOT NULL,
    callee_id     INT,
    line          INT,
    raw           TEXT,
    callee_raw    TEXT,
    resolved_kind TEXT,
    PRIMARY KEY (caller_id, line, callee_raw)
);
CREATE TABLE node_tags (
    node_id     INT NOT NULL,
    taxonomy_id TEXT NOT NULL,
    kind        TEXT NOT NULL,
    severity    TEXT NOT NULL,
    line        INT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'regex',
    confidence  REAL NOT NULL DEFAULT 1.0,
    evidence    TEXT,
    PRIMARY KEY (node_id, taxonomy_id, line)
);
"""


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    return c


def _add_node(c, nid, qname, file="app.js", start=1, end=10):
    c.execute(
        "INSERT INTO nodes (id, qualified_name, file, name, parent, kind, "
        "start_line, end_line) VALUES (?, ?, ?, ?, NULL, 'function', ?, ?)",
        (nid, qname, file, qname.split("::")[-1], start, end),
    )


def _add_edge(c, caller, callee, line=1, raw_name=None, kind="exact"):
    c.execute(
        "INSERT OR REPLACE INTO edges "
        "(caller_id, callee_id, line, raw, callee_raw, resolved_kind) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (caller, callee, line, raw_name or f"call{line}", raw_name or f"call{line}", kind),
    )


def _add_tag(c, node_id, taxonomy_id, kind, severity="high", line=5,
             source="regex", confidence=1.0):
    c.execute(
        "INSERT INTO node_tags "
        "(node_id, taxonomy_id, kind, severity, line, source, confidence) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (node_id, taxonomy_id, kind, severity, line, source, confidence),
    )


# ── tests ──────────────────────────────────────────────────────────────


def test_sink_back_propagates_one_hop():
    c = _conn()
    _add_node(c, 1, "app.js::renderHTML")          # sink (direct)
    _add_node(c, 2, "app.js::displayMsg")          # caller of renderHTML
    _add_edge(c, 2, 1, line=20, raw_name="renderHTML")
    _add_tag(c, 1, "innerHTML_assign", "sink", "high")
    c.commit()

    out = discover(c)
    assert len(out) == 1
    t = out[0]
    assert t.node_id == 2
    assert t.taxonomy_id == "innerHTML_assign"
    assert t.kind == "sink"
    assert t.hop == 1
    assert abs(t.confidence - DEFAULT_DECAY) < 1e-6
    assert t.path == ["app.js::renderHTML", "app.js::displayMsg"]


def test_sink_back_propagates_two_hops():
    c = _conn()
    # primitive   <- wrapper        <- caller
    _add_node(c, 1, "app.js::raw_innerHTML")
    _add_node(c, 2, "app.js::renderHTML")
    _add_node(c, 3, "ui.js::Page.render")
    _add_edge(c, 2, 1, line=10, raw_name="raw_innerHTML")
    _add_edge(c, 3, 2, line=20, raw_name="renderHTML")
    _add_tag(c, 1, "innerHTML_assign", "sink", "high")
    c.commit()

    out = sorted(discover(c, max_hops=2), key=lambda t: t.hop)
    assert [t.node_id for t in out] == [2, 3]
    assert [t.hop for t in out] == [1, 2]
    assert abs(out[0].confidence - DEFAULT_DECAY) < 1e-6
    assert abs(out[1].confidence - DEFAULT_DECAY ** 2) < 1e-6


def test_source_forward_propagates():
    c = _conn()
    # source (location.hash read) -> consumer
    _add_node(c, 1, "app.js::readHash")
    _add_node(c, 2, "app.js::parseInput")
    _add_edge(c, 1, 2, line=5, raw_name="parseInput")
    _add_tag(c, 1, "location_hash", "source", "medium")
    c.commit()

    out = discover(c)
    assert len(out) == 1
    assert out[0].node_id == 2
    assert out[0].kind == "source"
    assert out[0].taxonomy_id == "location_hash"
    assert out[0].hop == 1


def test_direct_tag_not_overridden():
    c = _conn()
    _add_node(c, 1, "app.js::a")
    _add_node(c, 2, "app.js::b")
    _add_edge(c, 2, 1, line=5, raw_name="a")
    _add_tag(c, 1, "eval_call", "sink", "high")
    # b ALSO has a direct tag for the same taxonomy — closure must not
    # shadow it with a lower-confidence implicit row.
    _add_tag(c, 2, "eval_call", "sink", "high", line=99, source="regex")
    c.commit()

    out = discover(c)
    # b is already direct; expander must skip emitting an implicit copy.
    assert all(t.node_id != 2 for t in out)


def test_max_hops_zero_returns_empty():
    c = _conn()
    _add_node(c, 1, "a")
    _add_node(c, 2, "b")
    _add_edge(c, 2, 1, line=1, raw_name="a")
    _add_tag(c, 1, "eval_call", "sink", "high")
    c.commit()
    assert discover(c, max_hops=0) == []


def test_unresolved_edges_ignored():
    c = _conn()
    _add_node(c, 1, "x")
    _add_node(c, 2, "y")
    _add_edge(c, 2, 1, line=1, raw_name="x", kind="unresolved")
    _add_tag(c, 1, "eval_call", "sink", "high")
    c.commit()
    assert discover(c) == []


def test_dynamic_edges_ignored():
    c = _conn()
    _add_node(c, 1, "x")
    _add_node(c, 2, "y")
    _add_edge(c, 2, 1, line=1, raw_name="x", kind="dynamic")
    _add_tag(c, 1, "eval_call", "sink", "high")
    c.commit()
    assert discover(c) == []


def test_shortest_path_wins_confidence():
    """Two paths to same node: 1-hop and 2-hop. Keep the 1-hop conf."""
    c = _conn()
    _add_node(c, 1, "sink_prim")
    _add_node(c, 2, "wrapper")
    _add_node(c, 3, "caller_both")
    # Direct: caller -> sink_prim (1 hop back from sink_prim view).
    _add_edge(c, 3, 1, line=1, raw_name="sink_prim")
    # Indirect: caller -> wrapper -> sink_prim (2 hops back).
    _add_edge(c, 3, 2, line=2, raw_name="wrapper")
    _add_edge(c, 2, 1, line=3, raw_name="sink_prim")
    _add_tag(c, 1, "eval_call", "sink", "high")
    c.commit()

    out = discover(c, max_hops=2)
    by_node = {t.node_id: t for t in out}
    assert 3 in by_node
    # caller_both got 1-hop confidence, not 2-hop.
    assert abs(by_node[3].confidence - DEFAULT_DECAY) < 1e-6
    assert by_node[3].hop == 1


def test_persist_idempotent():
    c = _conn()
    _add_node(c, 1, "a")
    _add_node(c, 2, "b")
    _add_edge(c, 2, 1, line=1, raw_name="a")
    _add_tag(c, 1, "eval_call", "sink", "high")
    c.commit()

    tags = discover(c)
    stats1 = persist(c, tags)
    stats2 = persist(c, tags)
    assert stats1["inserted"] == 1
    # Re-run cleared the old row then re-inserted; counts match.
    assert stats2["inserted"] == 1
    assert stats2["cleared"] == 1
    rows = c.execute(
        "SELECT node_id, taxonomy_id, source, confidence, evidence "
        "FROM node_tags WHERE source LIKE 'implicit_%'"
    ).fetchall()
    assert len(rows) == 1
    nid, tid, source, conf, evidence = rows[0]
    assert nid == 2 and tid == "eval_call" and source == IMPLICIT_CLOSURE_SOURCE
    assert abs(conf - DEFAULT_DECAY) < 1e-6
    ev = json.loads(evidence)
    assert ev["hop"] == 1
    assert ev["path"] == ["a", "b"]


def test_persist_does_not_clobber_direct():
    """Persist must never delete or overwrite direct tags."""
    c = _conn()
    _add_node(c, 1, "a")
    _add_node(c, 2, "b")
    _add_edge(c, 2, 1, line=1, raw_name="a")
    _add_tag(c, 1, "eval_call", "sink", "high", source="regex")
    _add_tag(c, 2, "innerHTML_assign", "sink", "high", source="ast")
    c.commit()

    tags = discover(c)
    persist(c, tags)
    direct_count = c.execute(
        "SELECT COUNT(*) FROM node_tags WHERE source NOT LIKE 'implicit_%'"
    ).fetchone()[0]
    assert direct_count == 2


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
