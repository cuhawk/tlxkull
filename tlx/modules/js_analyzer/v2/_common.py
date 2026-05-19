"""Shared helpers for V2 subsystems.

Idempotent SQL DDL execution, regex scan helpers, JSON sidecar writers.
Every V2 module imports from here so schema-creation and stats-shape
stay consistent.
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

__all__ = [
    "exec_ddl",
    "clear_table",
    "scan_edge_raw",
    "scan_node_files",
    "load_node_meta",
    "write_sidecar",
    "ensure_node_tags_columns",
    "ensure_edges_columns",
]


def exec_ddl(conn: sqlite3.Connection, ddl: str) -> None:
    """Run a multi-statement DDL block. Idempotent (CREATE IF NOT EXISTS)."""
    conn.executescript(ddl)
    conn.commit()


def clear_table(conn: sqlite3.Connection, table: str, *, where: str = "") -> int:
    """Delete rows; return count cleared. Tolerates missing table."""
    try:
        before = conn.total_changes
        sql = f"DELETE FROM {table}"
        if where:
            sql += f" WHERE {where}"
        conn.execute(sql)
        conn.commit()
        return conn.total_changes - before
    except sqlite3.OperationalError:
        return 0


def scan_edge_raw(
    conn: sqlite3.Connection,
    pattern: re.Pattern[str],
    *,
    extra_cols: tuple[str, ...] = (),
) -> Iterable[tuple]:
    """Yield ``(caller_id, line, raw, *extra)`` for every edges row whose
    raw text matches ``pattern``. Order: caller_id, line.
    """
    cols = "caller_id, line, raw"
    if extra_cols:
        cols += ", " + ", ".join(extra_cols)
    for row in conn.execute(
        f"SELECT {cols} FROM edges WHERE raw IS NOT NULL"
    ):
        if pattern.search(row[2] or ""):
            yield row


def scan_node_files(conn: sqlite3.Connection) -> dict[int, str]:
    """node_id → file."""
    return {nid: file or "" for nid, file in
            conn.execute("SELECT id, file FROM nodes")}


def load_node_meta(conn: sqlite3.Connection) -> dict[int, dict]:
    """node_id → {qname, file, name, start_line, end_line, parent}."""
    out: dict[int, dict] = {}
    for nid, qname, file, name, parent, sl, el in conn.execute(
        "SELECT id, qualified_name, file, name, parent, start_line, end_line FROM nodes"
    ):
        out[nid] = {
            "qname": qname or f"<n{nid}>",
            "file": file or "",
            "name": name or "",
            "parent": parent or "",
            "start_line": sl or 0,
            "end_line": el or sl or 0,
        }
    return out


def write_sidecar(target_dir: str | Path, filename: str, payload: Any) -> Path:
    """Persist a JSON sidecar under ``targets/<name>/`` and return the path."""
    p = Path(target_dir) / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return p


def ensure_node_tags_columns(conn: sqlite3.Connection) -> None:
    """Make sure node_tags has the v1+v2 metadata columns we expect."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    if "confidence" not in cols:
        conn.execute("ALTER TABLE node_tags ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0")
    if "source" not in cols:
        conn.execute("ALTER TABLE node_tags ADD COLUMN source TEXT NOT NULL DEFAULT 'regex'")
    if "evidence" not in cols:
        conn.execute("ALTER TABLE node_tags ADD COLUMN evidence TEXT")
    conn.commit()


def ensure_edges_columns(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(edges)")}
    if "edge_class" not in cols:
        conn.execute("ALTER TABLE edges ADD COLUMN edge_class TEXT NOT NULL DEFAULT 'sync'")
    conn.commit()
