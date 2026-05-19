"""V2 §13 — DOM Clobbering candidate detection.

For each ``window.X`` / ``document.X`` / unguarded global read in the
indexed source, look for HTML sinks whose attribute policy permits
``id``/``name`` attributes (most do, unless DOMPurify is configured
to strip them). Emit ``clobber_candidates`` rows pairing the two.

Off by default; ``JS_ENABLE_DOM_CLOBBER=1`` to enable.

Outputs:
- tables ``global_reads``, ``clobber_candidates``
- sidecar ``clobber_candidates.json``
- chain sidecar ``chains/clobber.jsonl`` is emitted by the master driver
  (not here — this module only populates the DB).
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from modules.js_analyzer.v2._common import (
    clear_table,
    exec_ddl,
    load_node_meta,
    write_sidecar,
)

__all__ = ["run"]


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS global_reads (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    global_name TEXT NOT NULL,
    access_path TEXT NOT NULL,
    unguarded INTEGER DEFAULT 1,
    consumer_kind TEXT,
    file TEXT,
    line INTEGER
);
CREATE INDEX IF NOT EXISTS idx_global_reads_name ON global_reads(global_name);

CREATE TABLE IF NOT EXISTS clobber_candidates (
    id INTEGER PRIMARY KEY,
    html_sink_node INTEGER NOT NULL,
    global_read_id INTEGER NOT NULL,
    global_name TEXT NOT NULL,
    gadget_shape TEXT NOT NULL,
    reachability_score REAL NOT NULL,
    rationale TEXT
);
CREATE INDEX IF NOT EXISTS idx_clob_global ON clobber_candidates(global_name);
"""


_GLOBAL_READ_RE = re.compile(
    r"""\b(?:window|self|globalThis|document)\s*\.\s*([A-Za-z_$][\w$]*)(?:\s*\.\s*([\w$]+))?""",
)
_TYPEOF_GUARD_RE = re.compile(
    r"""\btypeof\s+(?:window|self|globalThis|document)\s*\.\s*([A-Za-z_$][\w$]*)\s*[!=]==?""",
)
_HTML_SINK_TAXONOMIES = (
    "innerHTML_assign",
    "outerHTML_assign",
    "insertAdjacentHTML_call",
    "document_write",
    "dangerouslySetInnerHTML",
    "vue_v_html_sink",
    "angular_inner_html_binding",
    "createContextualFragment",
)


def _consumer_kind(raw: str) -> str:
    rl = raw.lower()
    if "innerhtml" in rl or "outerhtml" in rl or "document.write" in rl:
        return "string-sink"
    if "fetch(" in rl or "axios" in rl or "xhr" in rl:
        return "data-fetch"
    if "location" in rl and "=" in rl:
        return "navigate"
    if rl.endswith(")"):
        return "function-call"
    return "config"


def _detect_global_reads(conn: sqlite3.Connection) -> list[tuple]:
    meta = load_node_meta(conn)
    out: list[tuple] = []
    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        for m in _GLOBAL_READ_RE.finditer(raw):
            head = m.group(1)
            sub = m.group(2)
            if head in {"location", "history", "navigator", "screen"}:
                continue
            if head.startswith("__webpack") or head.startswith("__VITE"):
                continue
            access = f"window.{head}" + (f".{sub}" if sub else "")
            guard = 0 if _TYPEOF_GUARD_RE.search(raw) else 1
            consumer = _consumer_kind(raw)
            node = meta.get(caller_id, {})
            out.append((
                caller_id, head, access, guard, consumer,
                node.get("file", ""), int(line or 0),
            ))
    return out


def _pair_with_html_sinks(conn: sqlite3.Connection) -> list[tuple]:
    placeholders = ",".join("?" * len(_HTML_SINK_TAXONOMIES))
    html_sinks = conn.execute(
        f"SELECT node_id FROM node_tags "
        f"WHERE kind = 'sink' AND taxonomy_id IN ({placeholders})",
        _HTML_SINK_TAXONOMIES,
    ).fetchall()

    reads = conn.execute(
        "SELECT id, node_id, global_name, unguarded FROM global_reads WHERE unguarded=1"
    ).fetchall()
    if not html_sinks or not reads:
        return []

    out: list[tuple] = []
    # Quadratic but bounded by html sinks × unguarded reads. Cap per
    # global_name at 30 candidates to avoid explosion on heavily-reused
    # globals.
    per_global: dict[str, int] = {}
    for sink_row in html_sinks:
        for read_row in reads:
            rid, _rnid, gname, _ = read_row
            if per_global.get(gname, 0) >= 30:
                continue
            shape = "plain-id"
            score = 0.5
            rationale = f"window.{gname} unguarded read + HTML sink permits id/name"
            out.append((sink_row[0], rid, gname, shape, score, rationale))
            per_global[gname] = per_global.get(gname, 0) + 1
    return out


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    clear_table(conn, "global_reads")
    clear_table(conn, "clobber_candidates")

    reads = _detect_global_reads(conn)
    for r in reads:
        conn.execute(
            "INSERT INTO global_reads (node_id, global_name, access_path, "
            "unguarded, consumer_kind, file, line) VALUES (?,?,?,?,?,?,?)",
            r,
        )
    conn.commit()

    pairs = _pair_with_html_sinks(conn)
    for p in pairs:
        conn.execute(
            "INSERT INTO clobber_candidates (html_sink_node, global_read_id, "
            "global_name, gadget_shape, reachability_score, rationale) "
            "VALUES (?,?,?,?,?,?)", p,
        )
    conn.commit()

    sidecar = {
        "global_reads": len(reads),
        "clobber_candidates": len(pairs),
        "globals_observed": _top_globals(conn),
    }
    write_sidecar(target_dir, "clobber_candidates.json", sidecar)
    return sidecar


def _top_globals(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT global_name, COUNT(*) AS n FROM global_reads "
        "GROUP BY global_name ORDER BY n DESC LIMIT 20"
    ).fetchall()
    return [{"global_name": n, "count": int(c)} for n, c in rows]
