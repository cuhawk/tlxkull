"""Synthetic-fixture tests for bin/bucket_inversion.py.

Covers:
1. Three sibling methods carry innerHTML_assign → 4th sibling gets implicit_bucket tag.
2. Threshold: only 2 tagged siblings → no inference.
3. File-level (NULL parent) functions never participate.
4. Cross-class siblings are not grouped.
5. Implicit-only siblings don't count (direct_only=True, default).
6. With --count-implicit-siblings, implicit tags can drive inference.
7. ``persist()`` is idempotent + does not clobber direct tags.
8. Already-direct tagged node never receives implicit_bucket for same taxonomy.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN))

import bucket_inversion as bi  # noqa: E402


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


def _add_method(c, nid, file, parent, name, start_line=1, kind="method"):
    c.execute(
        "INSERT INTO nodes (id, qualified_name, file, name, parent, kind, "
        "start_line, end_line) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (nid, f"{file}::{parent}.{name}" if parent else f"{file}::{name}",
         file, name, parent, kind, start_line, start_line + 20),
    )


def _add_tag(c, nid, tax_id="innerHTML_assign", kind="sink",
             severity="high", source="regex", confidence=1.0, line=5):
    c.execute(
        "INSERT OR IGNORE INTO node_tags "
        "(node_id, taxonomy_id, kind, severity, line, source, confidence) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nid, tax_id, kind, severity, line, source, confidence),
    )


# ── tests ──────────────────────────────────────────────────────────────


def test_three_tagged_siblings_seed_fourth():
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "Renderer", f"render{i}")
    for nid in (1, 2, 3):
        _add_tag(c, nid)
    c.commit()

    out = bi.discover(c)
    target_ids = {t.node_id for t in out}
    assert target_ids == {4}
    assert out[0].taxonomy_id == "innerHTML_assign"
    assert out[0].kind == "sink"
    assert out[0].confidence == 0.5
    ev = out[0].evidence
    assert ev["rule"] == "sibling_density"
    assert ev["tagged_siblings"] == 3
    assert ev["total_siblings"] == 4


def test_two_tagged_siblings_no_inference():
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "Renderer", f"render{i}")
    for nid in (1, 2):
        _add_tag(c, nid)
    c.commit()

    out = bi.discover(c)
    assert out == []


def test_file_level_functions_skipped():
    """NULL parent → file-level fns; sibling concept doesn't apply."""
    c = _conn()
    for i in range(1, 5):
        c.execute(
            "INSERT INTO nodes (id, qualified_name, file, name, parent, "
            "kind, start_line, end_line) "
            "VALUES (?, ?, ?, ?, NULL, 'function', 1, 20)",
            (i, f"util.js::fn{i}", "util.js", f"fn{i}"),
        )
    for nid in (1, 2, 3):
        _add_tag(c, nid)
    c.commit()
    assert bi.discover(c) == []


def test_cross_class_does_not_group():
    c = _conn()
    # Renderer methods (3 tagged, 1 untagged) — group A
    _add_method(c, 1, "ui.js", "Renderer", "a")
    _add_method(c, 2, "ui.js", "Renderer", "b")
    _add_method(c, 3, "ui.js", "Renderer", "c")
    # Unrelated class — different parent
    _add_method(c, 5, "ui.js", "OtherClass", "x")
    _add_method(c, 6, "ui.js", "OtherClass", "y")
    for nid in (1, 2, 3):
        _add_tag(c, nid)
    c.commit()

    out = bi.discover(c)
    # No untagged sibling in Renderer (only 3 members exist, all tagged)
    # OtherClass has no tagged members so no inference.
    assert out == []


def test_implicit_tags_dont_count_by_default():
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "Renderer", f"render{i}")
    # All three tagged tags come from implicit-closure expansion.
    for nid in (1, 2, 3):
        _add_tag(c, nid, source="implicit_closure", confidence=0.7)
    c.commit()
    assert bi.discover(c) == []


def test_implicit_can_count_when_flag_set():
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "Renderer", f"render{i}")
    for nid in (1, 2, 3):
        _add_tag(c, nid, source="implicit_closure", confidence=0.7)
    c.commit()
    out = bi.discover(c, direct_only=False)
    assert {t.node_id for t in out} == {4}


def test_persist_idempotent():
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "Renderer", f"render{i}")
    for nid in (1, 2, 3):
        _add_tag(c, nid)
    c.commit()

    tags = bi.discover(c)
    s1 = bi.persist(c, tags)
    s2 = bi.persist(c, tags)
    assert s1["inserted"] == 1
    assert s2["cleared"] == 1
    assert s2["inserted"] == 1
    # Direct tags must remain intact.
    direct = c.execute(
        "SELECT COUNT(*) FROM node_tags WHERE source NOT LIKE 'implicit_%'"
    ).fetchone()[0]
    assert direct == 3


def test_already_tagged_skipped():
    """Sibling that ALREADY has the taxonomy tagged (any source) is not duplicated."""
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "Renderer", f"render{i}")
    for nid in (1, 2, 3):
        _add_tag(c, nid)
    # Sibling 4 already has innerHTML_assign via implicit_naming
    _add_tag(c, 4, source="implicit_naming", confidence=0.4)
    c.commit()

    out = bi.discover(c)
    # No new tag for node 4 (already tagged with same taxonomy)
    assert all(t.node_id != 4 for t in out)


def test_arrow_kind_participates():
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "App", f"handler{i}", kind="arrow")
    for nid in (1, 2, 3):
        _add_tag(c, nid)
    c.commit()
    out = bi.discover(c)
    assert {t.node_id for t in out} == {4}


def test_severity_propagates():
    c = _conn()
    for i in range(1, 5):
        _add_method(c, i, "ui.js", "App", f"render{i}")
    for nid in (1, 2, 3):
        _add_tag(c, nid, tax_id="dangerouslySetInnerHTML",
                 severity="critical")
    c.commit()
    out = bi.discover(c)
    assert out[0].severity == "critical"
    assert out[0].taxonomy_id == "dangerouslySetInnerHTML"


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
