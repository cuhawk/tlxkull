"""V2 §11 — Persistent client-side state taint.

Records storage events (localStorage/sessionStorage/cookies/IndexedDB/
history.pushState/window.name/BroadcastChannel/Cache API) from
``edges.raw`` patterns, then synthesises ``storage_edges`` write→read
pairs keyed by literal key + bundle proximity.

Off by default. Enabled via ``JS_ENABLE_PERSISTENT_TAINT=1``.

Produces:
- table ``storage_events``
- view-equivalent table ``storage_edges`` (materialised pair table)
- per-target sidecar ``persistence_edges.json``
- node_tags rows tagging readers as ``stored_xss_read`` sources
  (kind=source, confidence 0.45-0.6 per V1 §11.7).
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from modules.js_analyzer.v2._common import (
    clear_table,
    ensure_node_tags_columns,
    exec_ddl,
    load_node_meta,
    write_sidecar,
)

__all__ = ["run"]


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS storage_events (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    api TEXT NOT NULL,
    op TEXT NOT NULL,
    key_static TEXT,
    key_provenance TEXT,
    is_secret_hint INTEGER DEFAULT 0,
    file TEXT NOT NULL,
    line INTEGER,
    raw TEXT,
    framework_hint TEXT
);
CREATE INDEX IF NOT EXISTS idx_storage_key ON storage_events(key_static, op);
CREATE INDEX IF NOT EXISTS idx_storage_api ON storage_events(api, op);

CREATE TABLE IF NOT EXISTS storage_edges (
    id INTEGER PRIMARY KEY,
    write_event_id INTEGER NOT NULL,
    read_event_id  INTEGER NOT NULL,
    api TEXT NOT NULL,
    key_static TEXT,
    same_bundle INTEGER NOT NULL,
    confidence REAL NOT NULL,
    rationale TEXT
);
CREATE INDEX IF NOT EXISTS idx_storage_edges_key ON storage_edges(key_static);
"""


# Each entry: (api, op, regex)
_PATTERNS = [
    ("localStorage",   "write", re.compile(r"localStorage\.setItem\s*\(\s*['\"`]([^'\"`]+)['\"`]")),
    ("localStorage",   "write", re.compile(r"localStorage\[\s*['\"`]([^'\"`]+)['\"`]\s*\]\s*=")),
    ("localStorage",   "read",  re.compile(r"localStorage\.getItem\s*\(\s*['\"`]([^'\"`]+)['\"`]")),
    ("localStorage",   "read",  re.compile(r"localStorage\[\s*['\"`]([^'\"`]+)['\"`]\s*\](?!\s*=)")),
    ("sessionStorage", "write", re.compile(r"sessionStorage\.setItem\s*\(\s*['\"`]([^'\"`]+)['\"`]")),
    ("sessionStorage", "read",  re.compile(r"sessionStorage\.getItem\s*\(\s*['\"`]([^'\"`]+)['\"`]")),
    ("cookie",         "write", re.compile(r"document\.cookie\s*=\s*['\"`]([^=;'\"`]+)\s*=")),
    ("cookie",         "read",  re.compile(r"document\.cookie\b(?!\s*=)")),
    ("indexedDB",      "write", re.compile(r"\.put\s*\(\s*[^,]+,\s*['\"`]([^'\"`]+)['\"`]")),
    ("indexedDB",      "read",  re.compile(r"\.get\s*\(\s*['\"`]([^'\"`]+)['\"`]\s*\)")),
    ("cacheApi",       "write", re.compile(r"cache\.put\s*\(")),
    ("cacheApi",       "read",  re.compile(r"cache\.match\s*\(")),
    ("history",        "write", re.compile(r"history\.(?:pushState|replaceState)\s*\(")),
    ("window.name",    "write", re.compile(r"window\.name\s*=")),
    ("window.name",    "read",  re.compile(r"window\.name\b(?!\s*=)")),
    ("broadcastChannel", "write", re.compile(r"new\s+BroadcastChannel\s*\(\s*['\"`]([^'\"`]+)['\"`]")),
]


_SECRET_KEY_RE = re.compile(
    r"(?:^|[._-])(?:token|jwt|auth|access[_-]?token|refresh|secret|api[_-]?key|sso)\b",
    re.IGNORECASE,
)


def _detect_events(conn: sqlite3.Connection) -> list[tuple]:
    """Scan edges.raw + node bodies for storage patterns.

    Returns rows ready for INSERT INTO storage_events.
    """
    meta = load_node_meta(conn)
    found: list[tuple] = []
    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        for api, op, pat in _PATTERNS:
            m = pat.search(raw)
            if not m:
                continue
            key_static = m.group(1) if m.groups() else None
            key_provenance = "literal" if key_static else "computed"
            secret_hint = 1 if (key_static and _SECRET_KEY_RE.search(key_static)) else 0
            node = meta.get(caller_id, {})
            found.append((
                caller_id, api, op, key_static, key_provenance,
                secret_hint, node.get("file", ""), int(line or 0),
                raw[:240], None,
            ))
    return found


def _build_pair_edges(conn: sqlite3.Connection) -> list[tuple]:
    """For every (api, key_static) with both writes and reads, emit a
    storage_edges row per (write, read) pair. Confidence per V1 §11.7.
    """
    pairs: list[tuple] = []
    rows = conn.execute(
        "SELECT id, node_id, api, op, key_static, is_secret_hint, file "
        "FROM storage_events WHERE key_static IS NOT NULL"
    ).fetchall()
    by_key: dict[tuple[str, str], dict[str, list]] = {}
    for r in rows:
        eid, nid, api, op, key, secret, file = r
        bucket = by_key.setdefault((api, key), {"write": [], "read": []})
        bucket.setdefault(op, []).append(r)

    for (api, key), bucket in by_key.items():
        writes = bucket.get("write") or []
        reads = bucket.get("read") or []
        if not writes or not reads:
            continue
        for w in writes:
            for r in reads:
                same_bundle = 1 if (w[6] == r[6]) else 0
                conf = 0.6
                if same_bundle:
                    conf += 0.05
                if w[5] or r[5]:
                    conf += 0.05
                conf = min(0.95, conf)
                rationale = (
                    f"key={key!r} literal match across "
                    f"{'same' if same_bundle else 'different'} bundle"
                )
                pairs.append((w[0], r[0], api, key, same_bundle, conf, rationale))
    return pairs


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    ensure_node_tags_columns(conn)
    clear_table(conn, "storage_events")
    clear_table(conn, "storage_edges")
    clear_table(conn, "node_tags", where="source='persistent_taint'")

    events = _detect_events(conn)
    for row in events:
        conn.execute(
            "INSERT INTO storage_events "
            "(node_id, api, op, key_static, key_provenance, is_secret_hint, "
            " file, line, raw, framework_hint) VALUES (?,?,?,?,?,?,?,?,?,?)",
            row,
        )
    conn.commit()

    pairs = _build_pair_edges(conn)
    for p in pairs:
        conn.execute(
            "INSERT INTO storage_edges (write_event_id, read_event_id, api, "
            "key_static, same_bundle, confidence, rationale) "
            "VALUES (?,?,?,?,?,?,?)",
            p,
        )
    conn.commit()

    # Tag reader nodes as a new source kind 'persistent_storage_read'
    # so they can flow downstream like any DOM source.
    tagged = 0
    for r in conn.execute(
        "SELECT DISTINCT se.node_id, se.api, AVG(sed.confidence) "
        "FROM storage_events se "
        "JOIN storage_edges sed ON sed.read_event_id = se.id "
        "WHERE se.op = 'read' GROUP BY se.node_id, se.api"
    ).fetchall():
        nid, api, conf = r
        conn.execute(
            "INSERT OR IGNORE INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source, confidence, evidence) "
            "VALUES (?, ?, 'source', 'medium', 0, 'persistent_taint', ?, ?)",
            (nid, f"persistent_{api}_read", float(conf or 0.5),
             json.dumps({"api": api})),
        )
        tagged += 1
    conn.commit()

    sidecar = {
        "events": len(events),
        "pairs": len(pairs),
        "reader_tags": tagged,
        "api_breakdown": _api_breakdown(conn),
    }
    write_sidecar(target_dir, "persistence_edges.json", sidecar)
    return sidecar


def _api_breakdown(conn: sqlite3.Connection) -> dict:
    out: dict[str, dict[str, int]] = {}
    for api, op, n in conn.execute(
        "SELECT api, op, COUNT(*) FROM storage_events GROUP BY api, op"
    ):
        out.setdefault(api, {})[op] = int(n)
    return out
