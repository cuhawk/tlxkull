"""V2 §23 — Client-side authorization / state abuse expansion.

Surfaces:
- ``auth_state_nodes`` — useUser/useSession/Redux auth slice consumers
- ``token_provenance`` — where tokens are born / stored / read
- ``route_guards`` — client-only guards (already captured in route_map
  via §22 when both subsystems run together)

Off by default; ``JS_ENABLE_AUTH_ABUSE=1`` to enable.
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
CREATE TABLE IF NOT EXISTS auth_state_nodes (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    role TEXT NOT NULL,         -- 'identity' | 'permission' | 'token' | 'role-claim'
    source TEXT NOT NULL,
    framework TEXT,
    trust REAL NOT NULL,
    file TEXT,
    line INTEGER,
    raw TEXT
);
CREATE INDEX IF NOT EXISTS idx_auth_role ON auth_state_nodes(role);

CREATE TABLE IF NOT EXISTS token_provenance (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    birthplace TEXT NOT NULL,
    storage TEXT,
    leak_surface TEXT,
    file TEXT,
    line INTEGER
);
CREATE INDEX IF NOT EXISTS idx_token_storage ON token_provenance(storage);
"""


_AUTH_PATTERNS = [
    (re.compile(r"\buseUser\s*\(\s*\)"),         "identity",   "useUser",    "react",     0.6),
    (re.compile(r"\buseSession\s*\(\s*\)"),      "identity",   "useSession", "nextauth",  0.7),
    (re.compile(r"\buseAuth0\s*\(\s*\)"),        "identity",   "useAuth0",   "auth0",     0.7),
    (re.compile(r"\buseAuth\s*\(\s*\)"),         "identity",   "useAuth",    "custom",    0.5),
    (re.compile(r"\.isAdmin\b"),                 "permission", "client_state","redux",    0.4),
    (re.compile(r"\.isAuthenticated\b"),         "identity",   "client_state","redux",    0.4),
    (re.compile(r"\.roles\b|\.role\b"),          "role-claim", "client_state","redux",    0.5),
    (re.compile(r"\baccess[_-]?token\b", re.I),  "token",      "varname",    None,        0.6),
    (re.compile(r"\brefresh[_-]?token\b", re.I), "token",      "varname",    None,        0.6),
    (re.compile(r"\bjwt\b", re.I),               "token",      "varname",    None,        0.55),
]


_TOKEN_STORAGE_HINTS = [
    (re.compile(r"localStorage\.setItem\s*\([^)]*token", re.I),    "localStorage"),
    (re.compile(r"sessionStorage\.setItem\s*\([^)]*token", re.I), "sessionStorage"),
    (re.compile(r"document\.cookie\s*=[^;]*token", re.I),         "cookie"),
    (re.compile(r"\bin[_-]?memory\b", re.I),                       "in-memory"),
]

_LEAK_SURFACE_HINTS = [
    (re.compile(r"location\.href\s*=|location\.assign\s*\(|window\.open\s*\("), "url-write"),
    (re.compile(r"\.postMessage\s*\("),                                          "postMessage"),
    (re.compile(r"console\.(?:log|error|info)\s*\("),                            "console.log"),
    (re.compile(r"Sentry\.|Bugsnag\.|datadog|newrelic", re.I),                   "error-reporting"),
]


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    clear_table(conn, "auth_state_nodes")
    clear_table(conn, "token_provenance")

    meta = load_node_meta(conn)
    auth_rows: list[tuple] = []
    token_rows: list[tuple] = []

    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        node = meta.get(caller_id, {})

        for pat, role, source, framework, trust in _AUTH_PATTERNS:
            if pat.search(raw):
                auth_rows.append((
                    caller_id, role, source, framework, trust,
                    node.get("file", ""), int(line or 0), raw[:240],
                ))
                if role == "token":
                    storage = next((s for pat2, s in _TOKEN_STORAGE_HINTS if pat2.search(raw)), None)
                    leak = next((s for pat2, s in _LEAK_SURFACE_HINTS if pat2.search(raw)), None)
                    token_rows.append((
                        caller_id, source, storage, leak,
                        node.get("file", ""), int(line or 0),
                    ))
                break  # first-pattern-wins per row

    for r in auth_rows:
        conn.execute(
            "INSERT INTO auth_state_nodes "
            "(node_id, role, source, framework, trust, file, line, raw) "
            "VALUES (?,?,?,?,?,?,?,?)", r,
        )
    for r in token_rows:
        conn.execute(
            "INSERT INTO token_provenance "
            "(node_id, birthplace, storage, leak_surface, file, line) "
            "VALUES (?,?,?,?,?,?)", r,
        )
    conn.commit()

    sidecar = {
        "auth_state_rows": len(auth_rows),
        "token_rows": len(token_rows),
        "by_role": {role: int(n) for role, n in conn.execute(
            "SELECT role, COUNT(*) FROM auth_state_nodes GROUP BY role"
        )},
        "tokens_with_leak_surface": int(conn.execute(
            "SELECT COUNT(*) FROM token_provenance WHERE leak_surface IS NOT NULL"
        ).fetchone()[0]),
    }
    write_sidecar(target_dir, "auth_abuse.json", sidecar)
    return sidecar
