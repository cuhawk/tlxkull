"""V2 §12 — Cross-origin trust + origin provenance modeling.

Captures every postMessage send + onmessage handler from ``edges.raw``
and classifies origin validation as ``strict``/``loose``/``none``.
Surfaces:

- table ``origin_validations`` (handler-side)
- table ``post_messages`` (sender-side; captures targetOrigin)
- sidecar ``origin_trust_graph.json``
- per-node tag ``loose_origin_validation`` (source) / ``broadcast_postmessage`` (sink).

Off by default; ``JS_ENABLE_ORIGIN_TRUST=1`` to enable.
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
CREATE TABLE IF NOT EXISTS origin_validations (
    id INTEGER PRIMARY KEY,
    handler_node_id INTEGER NOT NULL,
    file TEXT NOT NULL,
    line INTEGER,
    validation_kind TEXT NOT NULL,    -- 'strict' | 'loose' | 'none'
    expression TEXT,
    bypass_classes TEXT               -- JSON list
);
CREATE INDEX IF NOT EXISTS idx_origin_kind ON origin_validations(validation_kind);

CREATE TABLE IF NOT EXISTS post_messages (
    id INTEGER PRIMARY KEY,
    sender_node_id INTEGER NOT NULL,
    file TEXT NOT NULL,
    line INTEGER,
    target_origin TEXT,               -- literal when known; '<dynamic>' otherwise
    broadcast INTEGER NOT NULL        -- 1 if target_origin = '*'
);
CREATE INDEX IF NOT EXISTS idx_post_target ON post_messages(target_origin);
"""


_ONMESSAGE_RE = re.compile(
    r"""(?:window|self|globalThis|\w+)\s*\.?addEventListener\s*\(\s*['"`]message['"`]"""
    r"""|\w+\.onmessage\s*=""",
)
_POSTMESSAGE_RE = re.compile(
    r"""\.postMessage\s*\(\s*([^,)]+)(?:\s*,\s*['"`]([^'"`]+)['"`])?""",
    re.DOTALL,
)
_STRICT_CHECK_RE = re.compile(
    r"""\b(event|e|msg|message|ev)\.origin\s*[!=]==\s*['"`][^'"`]+['"`]""",
)
_LOOSE_CHECK_RE = re.compile(
    r"""\b(event|e|msg|message|ev)\.origin\s*\.(?:startsWith|endsWith|indexOf|includes|match)\s*\(""",
)


def _classify_handler_origin(file_text: str, around_line: int, window: int = 80) -> tuple[str, str, list]:
    """Inspect a window of text and classify origin validation.

    Returns ``(kind, expression, bypass_classes)``.
    """
    lines = file_text.splitlines()
    if not lines:
        return "none", "", []
    start = max(0, around_line - 1)
    end = min(len(lines), around_line + window)
    snippet = "\n".join(lines[start:end])
    strict = _STRICT_CHECK_RE.search(snippet)
    if strict:
        return "strict", strict.group(0), []
    loose = _LOOSE_CHECK_RE.search(snippet)
    if loose:
        method = loose.group(0)
        bypasses: list[str] = []
        if "startsWith" in method:
            bypasses.append("subdomain_prefix")
        if "endsWith" in method:
            bypasses.append("origin_suffix")
        if "indexOf" in method or "includes" in method:
            bypasses.append("substring_anywhere")
        if "match" in method:
            bypasses.append("regex_quirks")
        return "loose", method, bypasses
    return "none", "", ["unchecked"]


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    ensure_node_tags_columns(conn)
    clear_table(conn, "origin_validations")
    clear_table(conn, "post_messages")
    clear_table(conn, "node_tags", where="source='origin_trust'")

    meta = load_node_meta(conn)
    target_dir = Path(target_dir)

    file_cache: dict[str, str] = {}

    def _file_text(path: str) -> str:
        if path in file_cache:
            return file_cache[path]
        # Try sources/<path> then raw/<path> then bare path.
        for candidate in (target_dir / "sources" / path, target_dir / "raw" / path, Path(path)):
            if candidate.exists() and candidate.is_file():
                try:
                    file_cache[path] = candidate.read_text(encoding="utf-8", errors="replace")
                    return file_cache[path]
                except Exception:
                    continue
        file_cache[path] = ""
        return ""

    handler_rows: list[tuple] = []
    sender_rows: list[tuple] = []

    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        node = meta.get(caller_id, {})
        file = node.get("file", "")

        if _ONMESSAGE_RE.search(raw):
            text = _file_text(file)
            kind, expression, bypasses = _classify_handler_origin(text, int(line or 0))
            handler_rows.append((
                caller_id, file, int(line or 0),
                kind, expression, json.dumps(bypasses),
            ))

        pm = _POSTMESSAGE_RE.search(raw)
        if pm:
            target_origin = pm.group(2) or "<dynamic>"
            broadcast = 1 if target_origin == "*" else 0
            sender_rows.append((
                caller_id, file, int(line or 0),
                target_origin, broadcast,
            ))

    for r in handler_rows:
        conn.execute(
            "INSERT INTO origin_validations "
            "(handler_node_id, file, line, validation_kind, expression, bypass_classes) "
            "VALUES (?,?,?,?,?,?)", r,
        )
    for r in sender_rows:
        conn.execute(
            "INSERT INTO post_messages "
            "(sender_node_id, file, line, target_origin, broadcast) "
            "VALUES (?,?,?,?,?)", r,
        )

    # Tag handlers with loose / none origin checks as elevated-confidence
    # sources. Strict-validated handlers keep base continuation tag only.
    tagged_loose = 0
    for nid, kind in conn.execute(
        "SELECT DISTINCT handler_node_id, validation_kind FROM origin_validations"
    ):
        if kind in ("loose", "none"):
            conn.execute(
                "INSERT OR IGNORE INTO node_tags "
                "(node_id, taxonomy_id, kind, severity, line, source, confidence, evidence) "
                "VALUES (?, ?, 'source', 'high', 0, 'origin_trust', ?, ?)",
                (nid,
                 "loose_origin_validation" if kind == "loose" else "missing_origin_validation",
                 0.85 if kind == "none" else 0.7,
                 json.dumps({"validation_kind": kind})),
            )
            tagged_loose += 1
    conn.commit()

    # Tag broadcast postMessage sends as sinks (data exfil class).
    tagged_broadcast = 0
    for nid in conn.execute(
        "SELECT DISTINCT sender_node_id FROM post_messages WHERE broadcast=1"
    ):
        conn.execute(
            "INSERT OR IGNORE INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source, confidence, evidence) "
            "VALUES (?, 'broadcast_postmessage', 'sink', 'medium', 0, 'origin_trust', 0.7, ?)",
            (nid[0], json.dumps({"target_origin": "*"})),
        )
        tagged_broadcast += 1
    conn.commit()

    sidecar = {
        "handlers": len(handler_rows),
        "senders": len(sender_rows),
        "loose_or_none_handlers": tagged_loose,
        "broadcast_senders": tagged_broadcast,
        "validation_kind_distribution": _validation_distribution(conn),
    }
    write_sidecar(target_dir, "origin_trust_graph.json", sidecar)
    return sidecar


def _validation_distribution(conn: sqlite3.Connection) -> dict[str, int]:
    return {kind: int(n) for kind, n in conn.execute(
        "SELECT validation_kind, COUNT(*) FROM origin_validations GROUP BY validation_kind"
    )}
