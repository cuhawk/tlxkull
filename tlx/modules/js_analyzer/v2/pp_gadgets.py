"""V2 §14 — Prototype-pollution gadget discovery.

Two halves:

1. ``implicit_lookups`` — record every ``obj[k]`` / destructuring read
   where ``k`` is parameter-shaped or attacker-influenceable.
2. ``pp_gadgets`` — load the framework gadget catalog and join with
   detected frameworks.

A pollution write reaching one of these gadgets is a real exploit
chain. The chain extractor consumes the join.

Off by default; ``JS_ENABLE_PP_GADGETS=1`` to enable.
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
CREATE TABLE IF NOT EXISTS implicit_lookups (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    key_kind TEXT NOT NULL,
    key_value TEXT,
    has_default INTEGER DEFAULT 0,
    has_typeof_guard INTEGER DEFAULT 0,
    consumer_kind TEXT,
    file TEXT,
    line INTEGER,
    raw TEXT
);
CREATE INDEX IF NOT EXISTS idx_lookup_consumer ON implicit_lookups(consumer_kind);

CREATE TABLE IF NOT EXISTS pp_gadgets (
    id INTEGER PRIMARY KEY,
    framework TEXT NOT NULL,
    version_range TEXT,
    key_path TEXT NOT NULL,
    gadget_kind TEXT NOT NULL,
    rationale TEXT,
    confidence REAL DEFAULT 0.8
);
CREATE INDEX IF NOT EXISTS idx_gadget_framework ON pp_gadgets(framework);
"""


# Static gadget catalog. Tiny but useful — most real PP exploits target
# one of these key_paths.
_GADGET_CATALOG: list[dict] = [
    {"framework": "lodash",  "version_range": "<4.17.21", "key_path": "__proto__.toString",         "gadget_kind": "render",   "rationale": "lodash merge toString pollution leads to template injection", "confidence": 0.85},
    {"framework": "lodash",  "version_range": "<4.17.21", "key_path": "constructor.prototype.merge","gadget_kind": "config-override", "rationale": "deep-merge chain pollutes downstream config",         "confidence": 0.70},
    {"framework": "merge",   "version_range": "any",      "key_path": "__proto__.x",                "gadget_kind": "config-override", "rationale": "merge() recursive copy of __proto__",                "confidence": 0.80},
    {"framework": "react",   "version_range": "any",      "key_path": "dangerouslySetInnerHTML.__html","gadget_kind": "render",  "rationale": "polluted default props feed React renderer",          "confidence": 0.85},
    {"framework": "next",    "version_range": "<13.5.0",  "key_path": "router.pathname",            "gadget_kind": "redirect", "rationale": "Next router default consumed without validation",       "confidence": 0.70},
    {"framework": "angular", "version_range": "<14",       "key_path": "$eval",                      "gadget_kind": "exec",     "rationale": "polluted $eval still works on Angular.js pre-14",        "confidence": 0.65},
    {"framework": "vue",     "version_range": "<2.7",      "key_path": "_v",                          "gadget_kind": "render",   "rationale": "Vue 2 _v render helper consumes polluted text",          "confidence": 0.70},
    {"framework": "router",  "version_range": "any",      "key_path": "matched.props",              "gadget_kind": "config-override", "rationale": "vue-router / react-router default props pollution", "confidence": 0.70},
    {"framework": "sanitizer", "version_range": "any",    "key_path": "ADD_TAGS",                    "gadget_kind": "render",   "rationale": "DOMPurify ADD_TAGS array polluted via Array.prototype",  "confidence": 0.75},
    {"framework": "json",    "version_range": "any",      "key_path": "toJSON",                      "gadget_kind": "exec",     "rationale": "polluted toJSON runs during JSON.stringify",             "confidence": 0.60},
]


_COMPUTED_LOOKUP_RE = re.compile(
    r"""([A-Za-z_$][\w$]*)\s*\[\s*([A-Za-z_$][\w$.]*)\s*\]"""
    r"""(?!\s*=(?![=]))""",
)
_DESTRUCT_DEFAULT_RE = re.compile(
    r"""(?:const|let|var)\s*\{\s*([\w$]+)\s*(?:=\s*([^},]+))?\s*\}""",
)


def _detect_lookups(conn: sqlite3.Connection) -> list[tuple]:
    meta = load_node_meta(conn)
    out: list[tuple] = []
    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        for m in _COMPUTED_LOOKUP_RE.finditer(raw):
            base, key = m.group(1), m.group(2)
            if base.lower() in {"window", "document", "self", "globalthis", "process", "console"}:
                continue
            has_default = 1 if "??" in raw or "||" in raw else 0
            has_typeof = 1 if re.search(r"\btypeof\s+" + re.escape(base) + r"\b", raw) else 0
            node = meta.get(caller_id, {})
            out.append((
                caller_id, "computed", key, has_default, has_typeof,
                "function-call" if raw.rstrip().endswith(")") else "set-prop",
                node.get("file", ""), int(line or 0), raw[:240],
            ))
        for m in _DESTRUCT_DEFAULT_RE.finditer(raw):
            name = m.group(1)
            default = m.group(2) or ""
            node = meta.get(caller_id, {})
            out.append((
                caller_id, "destructure", name, 1 if default else 0, 0,
                "render", node.get("file", ""), int(line or 0), raw[:240],
            ))
    # Cap to avoid runaway on dense bundles.
    return out[:50000]


def _load_gadget_catalog(conn: sqlite3.Connection) -> int:
    rows = 0
    for g in _GADGET_CATALOG:
        conn.execute(
            "INSERT OR IGNORE INTO pp_gadgets "
            "(framework, version_range, key_path, gadget_kind, rationale, confidence) "
            "VALUES (?,?,?,?,?,?)",
            (g["framework"], g["version_range"], g["key_path"],
             g["gadget_kind"], g["rationale"], g["confidence"]),
        )
        rows += 1
    conn.commit()
    return rows


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    clear_table(conn, "implicit_lookups")
    clear_table(conn, "pp_gadgets")

    lookups = _detect_lookups(conn)
    for row in lookups:
        conn.execute(
            "INSERT INTO implicit_lookups "
            "(node_id, key_kind, key_value, has_default, has_typeof_guard, "
            " consumer_kind, file, line, raw) VALUES (?,?,?,?,?,?,?,?,?)",
            row,
        )
    conn.commit()
    gadget_rows = _load_gadget_catalog(conn)

    sidecar = {
        "implicit_lookups": len(lookups),
        "gadgets_in_catalog": gadget_rows,
        "lookup_by_kind": {k: int(n) for k, n in conn.execute(
            "SELECT key_kind, COUNT(*) FROM implicit_lookups GROUP BY key_kind"
        )},
        "gadget_by_framework": {k: int(n) for k, n in conn.execute(
            "SELECT framework, COUNT(*) FROM pp_gadgets GROUP BY framework"
        )},
    }
    write_sidecar(target_dir, "pp_gadgets.json", sidecar)
    return sidecar
