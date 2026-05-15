"""External tag ingestion.

Maps (file, line, taxonomy_id, kind, severity, source) findings produced by
out-of-band tools (jsluice, future CSPT scanner, etc.) into ``node_tags``
rows on a per-target ``js_analyzer.db``. Each finding is resolved to the
innermost ``nodes`` row that contains its line. Findings whose file does
not match any indexed node are returned as orphans for the caller to log.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterable


@dataclass
class TagFinding:
    file: str
    line: int
    taxonomy_id: str
    kind: str
    severity: str
    source: str


@dataclass
class IngestStats:
    inserted: int = 0
    duplicate: int = 0
    orphan: int = 0


def _resolve_node(conn: sqlite3.Connection, file: str, line: int) -> int | None:
    row = conn.execute(
        """
        SELECT id FROM nodes
        WHERE file = ?
          AND start_line <= ?
          AND (end_line IS NULL OR end_line >= ?)
        ORDER BY (COALESCE(end_line, ?) - start_line) ASC
        LIMIT 1
        """,
        (file, line, line, line),
    ).fetchone()
    return row[0] if row else None


def ingest(
    conn: sqlite3.Connection, findings: Iterable[TagFinding]
) -> tuple[IngestStats, list[TagFinding]]:
    stats = IngestStats()
    orphans: list[TagFinding] = []
    cur = conn.cursor()
    for f in findings:
        nid = _resolve_node(conn, f.file, f.line)
        if nid is None:
            stats.orphan += 1
            orphans.append(f)
            continue
        before = conn.total_changes
        cur.execute(
            "INSERT OR IGNORE INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (nid, f.taxonomy_id, f.kind, f.severity, f.line, f.source),
        )
        if conn.total_changes > before:
            stats.inserted += 1
        else:
            stats.duplicate += 1
    conn.commit()
    return stats, orphans
