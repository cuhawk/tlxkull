"""V2 §22 — Sink reachability validation.

Models route → entry-point mapping plus lifecycle phase of each sink
so the chain extractor can multiply chain severity by an
``activation_likelihood`` factor.

Off by default; ``JS_ENABLE_SINK_REACHABILITY=1`` to enable.

Outputs:
- table ``sink_lifecycle``
- table ``route_map``
- sidecar ``sink_reachability.json``
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from modules.js_analyzer.v2._common import (
    clear_table,
    exec_ddl,
    load_node_meta,
    write_sidecar,
)

__all__ = ["run"]


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sink_lifecycle (
    node_id INTEGER PRIMARY KEY,
    framework TEXT NOT NULL,
    lifecycle_phase TEXT NOT NULL,
    attacker_can_trigger INTEGER DEFAULT 1,
    activation_likelihood REAL NOT NULL,
    rationale TEXT
);

CREATE TABLE IF NOT EXISTS route_map (
    id INTEGER PRIMARY KEY,
    route_path TEXT NOT NULL,
    entry_module TEXT NOT NULL,
    framework TEXT NOT NULL,
    guard_qname TEXT,
    guard_kind TEXT,
    auth_required INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_route_path ON route_map(route_path);
"""


_ROUTE_RE = re.compile(
    r"""(?:Route|<Route|path:|registerRoute|defineRoute)\s*\(?\s*['"`]([^'"`]+)['"`]""",
    re.IGNORECASE,
)
_GUARD_RE = re.compile(
    r"""\b(?:requireAuth|isAuthenticated|isAdmin|useUser\(\)\.isAdmin|hasRole|guard|canActivate)\b""",
)
_LIFECYCLE_PATTERNS = [
    ("react", "mount",       re.compile(r"\buseEffect\s*\(\s*[^,]+,\s*\[\s*\]\s*\)|componentDidMount")),
    ("react", "update",      re.compile(r"\buseEffect\s*\(|componentDidUpdate")),
    ("react", "unmount",     re.compile(r"\bcomponentWillUnmount|useEffect[^)]*return\s+\(?function|useEffect[^)]*return\s*\(?")),
    ("react", "error",       re.compile(r"\bcomponentDidCatch|ErrorBoundary")),
    ("next",  "revalidate",  re.compile(r"\b(?:getServerSideProps|revalidate|fetcher)\b")),
    ("vue",   "mount",       re.compile(r"\bcreated\s*\(\)|mounted\s*\(\)|onMounted\s*\(")),
    ("angular","mount",      re.compile(r"\bngOnInit\b")),
    ("sw",    "sw_install",  re.compile(r"\bself\.addEventListener\s*\(\s*['\"`]install['\"`]")),
    ("sw",    "sw_fetch",    re.compile(r"\bself\.addEventListener\s*\(\s*['\"`]fetch['\"`]")),
]


_ACTIVATION_DEFAULTS: dict[str, float] = {
    "mount":       1.0,
    "update":      0.9,
    "unmount":     0.20,
    "error":       0.15,
    "revalidate":  0.85,
    "sw_install":  0.4,
    "sw_fetch":    0.9,
    "unknown":     0.6,
}


def _detect_routes(conn: sqlite3.Connection) -> list[tuple]:
    meta = load_node_meta(conn)
    out: list[tuple] = []
    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        m = _ROUTE_RE.search(raw)
        if not m:
            continue
        node = meta.get(caller_id, {})
        path = m.group(1)
        if not path.startswith("/") and "/" not in path:
            continue
        guard = _GUARD_RE.search(raw)
        guard_qname = guard.group(0) if guard else None
        auth = 1 if (guard_qname and any(k in guard_qname.lower()
                                         for k in ("auth", "admin", "role"))) else 0
        out.append((
            path, node.get("file", ""), "react", guard_qname,
            "client-only" if guard_qname else None, auth,
        ))
    return out


def _classify_lifecycle(file_text: str) -> tuple[str, str]:
    for fw, phase, pat in _LIFECYCLE_PATTERNS:
        if pat.search(file_text):
            return fw, phase
    return "unknown", "unknown"


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    clear_table(conn, "sink_lifecycle")
    clear_table(conn, "route_map")

    target_dir = Path(target_dir)
    file_cache: dict[str, str] = {}

    def _file_text(path: str) -> str:
        if path in file_cache:
            return file_cache[path]
        for candidate in (target_dir / "sources" / path, target_dir / "raw" / path, Path(path)):
            if candidate.exists() and candidate.is_file():
                try:
                    file_cache[path] = candidate.read_text(encoding="utf-8", errors="replace")
                    return file_cache[path]
                except Exception:
                    continue
        file_cache[path] = ""
        return ""

    # Route map
    route_rows = _detect_routes(conn)
    seen_paths: set[tuple] = set()
    for r in route_rows:
        key = (r[0], r[1])
        if key in seen_paths:
            continue
        seen_paths.add(key)
        conn.execute(
            "INSERT INTO route_map (route_path, entry_module, framework, "
            " guard_qname, guard_kind, auth_required) VALUES (?,?,?,?,?,?)",
            r,
        )

    # Sink lifecycle classification.
    #
    # Performance: classify each FILE once, then bulk-tag every sink in
    # that file. Per-node classification on netlify-shaped targets (9k
    # sinks × multi-MB bundles) is O(sinks × file_size) which hangs.
    # The file-keyed cache makes it O(files × file_size + sinks).
    meta = load_node_meta(conn)
    sink_node_ids = [r[0] for r in conn.execute(
        "SELECT DISTINCT node_id FROM node_tags WHERE kind='sink'"
    )]
    # Group sinks by file.
    sinks_by_file: dict[str, list[int]] = {}
    for nid in sink_node_ids:
        node = meta.get(nid)
        if not node:
            continue
        sinks_by_file.setdefault(node["file"], []).append(nid)

    # Cap: skip absurdly large files (> 4MB).
    MAX_FILE_BYTES = 4 * 1024 * 1024
    file_class: dict[str, tuple[str, str]] = {}
    for f in sinks_by_file:
        text = _file_text(f) if f else ""
        if len(text) > MAX_FILE_BYTES:
            file_class[f] = ("unknown", "unknown")
            continue
        file_class[f] = _classify_lifecycle(text) if text else ("unknown", "unknown")

    classified = 0
    by_phase: dict[str, int] = {}
    for file, nids in sinks_by_file.items():
        framework, phase = file_class.get(file, ("unknown", "unknown"))
        likelihood = _ACTIVATION_DEFAULTS.get(phase, 0.6)
        attacker = 0 if phase in ("unmount", "error") else 1
        rationale = f"sink in {phase} ({framework})"
        for nid in nids:
            conn.execute(
                "INSERT OR REPLACE INTO sink_lifecycle "
                "(node_id, framework, lifecycle_phase, attacker_can_trigger, "
                " activation_likelihood, rationale) VALUES (?,?,?,?,?,?)",
                (nid, framework, phase, attacker, likelihood, rationale),
            )
            classified += 1
            by_phase[phase] = by_phase.get(phase, 0) + 1
    conn.commit()

    sidecar = {
        "routes": len(seen_paths),
        "sinks_classified": classified,
        "by_phase": by_phase,
    }
    write_sidecar(target_dir, "sink_reachability.json", sidecar)
    return sidecar
