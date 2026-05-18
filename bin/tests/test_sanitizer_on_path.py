"""Synthetic-fixture tests for bin/sanitizer_on_path.py.

Covers:
1. Chain with no sanitizer on path → marked clean.
2. Chain with matching-category sanitizer on path → marked sanitized.
3. Chain with category-mismatched sanitizer → marked clean.
4. 'any'-clearing sanitizer defuses every chain.
5. Strict-dominance: sanitizer after the next call-out doesn't count.
6. Strict-dominance: terminal-node sanitizer always counts.
7. Source-side category match (URL-encoding source) defuses URL sinks.
8. Empty path returns clean.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN))

import sanitizer_on_path as sop  # noqa: E402


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
CREATE TABLE node_sanitizers (
    node_id INT NOT NULL,
    taxonomy_id TEXT NOT NULL,
    line INT NOT NULL,
    clears TEXT NOT NULL,
    PRIMARY KEY (node_id, taxonomy_id, line)
);
CREATE TABLE edges (
    caller_id INT NOT NULL,
    callee_id INT,
    line INT,
    raw TEXT,
    callee_raw TEXT,
    resolved_kind TEXT,
    PRIMARY KEY (caller_id, line, callee_raw)
);
"""


def _conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    return c


def _add_node(c, nid, qname):
    c.execute(
        "INSERT INTO nodes (id, qualified_name, file, name, parent, kind, "
        "start_line, end_line) "
        "VALUES (?, ?, ?, ?, NULL, 'function', 1, 50)",
        (nid, qname, "app.js", qname.split("::")[-1]),
    )


def _add_san(c, nid, sid, line, clears):
    c.execute(
        "INSERT INTO node_sanitizers (node_id, taxonomy_id, line, clears) "
        "VALUES (?, ?, ?, ?)",
        (nid, sid, line, clears),
    )


def _add_call(c, caller, callee, line):
    c.execute(
        "INSERT OR REPLACE INTO edges "
        "(caller_id, callee_id, line, raw, callee_raw, resolved_kind) "
        "VALUES (?, ?, ?, ?, ?, 'exact')",
        (caller, callee, line, f"c{line}", f"c{line}"),
    )


def _chain(src_tax, sink_tax, path):
    src_qname = path[0] if path else "missing::src"
    sink_qname = path[-1] if path else "missing::sink"
    return {
        "id": 1,
        "source": {"qname": src_qname, "taxonomy_id": src_tax,
                   "file": "app.js", "line": 1},
        "sink": {"qname": sink_qname, "taxonomy_id": sink_tax,
                 "file": "app.js", "line": 1},
        "path": path,
        "depth": max(0, len(path) - 1),
        "score": 50.0,
    }


# ── tests ──────────────────────────────────────────────────────────────


def test_no_sanitizer_is_clean():
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_node(c, 2, "app::b")
    chain = _chain("location_hash", "innerHTML_assign", ["app::a", "app::b"])
    san = sop._load_sanitizers_by_qname(c)
    out, sanitized, clean = sop.annotate_chains([chain], san, {}, False)
    assert out[0]["sanitized"] is False
    assert len(clean) == 1 and not sanitized


def test_matching_category_sanitizes():
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_node(c, 2, "app::b")
    _add_san(c, 1, "sanitizer_dompurify", 5, "html,attribute")
    chain = _chain("location_hash", "innerHTML_assign", ["app::a", "app::b"])
    san = sop._load_sanitizers_by_qname(c)
    out, sanitized, clean = sop.annotate_chains([chain], san, {}, False)
    assert out[0]["sanitized"] is True
    ev = out[0]["sanitizer_evidence"]
    assert ev["sanitizer_id"] == "sanitizer_dompurify"
    assert "html" in ev["matched_categories"]
    assert len(sanitized) == 1 and not clean


def test_mismatched_category_is_clean():
    """URL-encoding sanitizer on path does NOT defuse an HTML sink."""
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_node(c, 2, "app::b")
    _add_san(c, 1, "sanitizer_encodeURIComponent", 5, "url")
    chain = _chain("location_hash", "innerHTML_assign", ["app::a", "app::b"])
    san = sop._load_sanitizers_by_qname(c)
    out, *_ = sop.annotate_chains([chain], san, {}, False)
    assert out[0]["sanitized"] is False


def test_any_clears_everything():
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_san(c, 1, "sanitizer_Number_coerce", 5, "any")
    chain = _chain("location_hash", "innerHTML_assign", ["app::a"])
    san = sop._load_sanitizers_by_qname(c)
    out, *_ = sop.annotate_chains([chain], san, {}, False)
    assert out[0]["sanitized"] is True
    assert "any" in out[0]["sanitizer_evidence"]["clears"]


def test_strict_dominance_late_sanitizer_skipped():
    """Sanitizer at line 30 after call-out at line 10 doesn't dominate."""
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_node(c, 2, "app::sink")
    _add_call(c, 1, 2, line=10)        # call to sink at line 10
    _add_san(c, 1, "sanitizer_dompurify", 30, "html")  # AFTER the call
    chain = _chain("location_hash", "innerHTML_assign", ["app::a", "app::sink"])
    san = sop._load_sanitizers_by_qname(c)
    calls = sop._load_call_lines(c)
    out, *_ = sop.annotate_chains([chain], san, calls, strict_dominance=True)
    assert out[0]["sanitized"] is False


def test_strict_dominance_early_sanitizer_counts():
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_node(c, 2, "app::sink")
    _add_call(c, 1, 2, line=20)
    _add_san(c, 1, "sanitizer_dompurify", 5, "html")  # before call
    chain = _chain("location_hash", "innerHTML_assign", ["app::a", "app::sink"])
    san = sop._load_sanitizers_by_qname(c)
    calls = sop._load_call_lines(c)
    out, *_ = sop.annotate_chains([chain], san, calls, strict_dominance=True)
    assert out[0]["sanitized"] is True


def test_strict_dominance_terminal_node_always_counts():
    """Sink-function sanitizer counts regardless of line order — there's
    no 'next call' to dominate over inside the terminal frame."""
    c = _conn()
    _add_node(c, 1, "app::sink")
    _add_san(c, 1, "sanitizer_dompurify", 99, "html")
    chain = _chain("location_hash", "innerHTML_assign", ["app::sink"])
    san = sop._load_sanitizers_by_qname(c)
    out, *_ = sop.annotate_chains([chain], san, {}, strict_dominance=True)
    assert out[0]["sanitized"] is True


def test_source_side_url_sanitizer_defuses_url_sink():
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_node(c, 2, "app::b")
    _add_san(c, 1, "sanitizer_encodeURIComponent", 5, "url")
    chain = _chain("location_search", "location_href_assign",
                   ["app::a", "app::b"])
    san = sop._load_sanitizers_by_qname(c)
    out, *_ = sop.annotate_chains([chain], san, {}, False)
    assert out[0]["sanitized"] is True


def test_empty_path_is_clean():
    c = _conn()
    chain = _chain("location_hash", "innerHTML_assign", [])
    san = sop._load_sanitizers_by_qname(c)
    out, *_ = sop.annotate_chains([chain], san, {}, False)
    assert out[0]["sanitized"] is False


def test_unknown_taxonomy_only_any_clears():
    c = _conn()
    _add_node(c, 1, "app::a")
    _add_san(c, 1, "sanitizer_dompurify", 5, "html")
    chain = _chain("unknown_source", "unknown_sink", ["app::a"])
    san = sop._load_sanitizers_by_qname(c)
    out, *_ = sop.annotate_chains([chain], san, {}, False)
    # html sanitizer doesn't apply to unknown-category sink
    assert out[0]["sanitized"] is False
    # but `any` would
    _add_san(c, 1, "sanitizer_Number_coerce", 6, "any")
    san = sop._load_sanitizers_by_qname(c)
    out, *_ = sop.annotate_chains([chain], san, {}, False)
    assert out[0]["sanitized"] is True


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
