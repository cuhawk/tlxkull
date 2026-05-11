"""Export seed lists for downstream fuzzing tools (ffuf / Burp).

Reads recorded paths from the per-session ``mock_flow`` table.
"""
from __future__ import annotations

import xml.sax.saxutils as _xml
from pathlib import Path

from .reporter import _open_conn


def _distinct_paths(db_path: Path, session_id: str) -> list[str]:
    conn = _open_conn(db_path)
    try:
        rows = conn.execute(
            "SELECT DISTINCT path FROM mock_flow "
            "WHERE session_id=? ORDER BY path",
            (session_id,),
        ).fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows if r and r[0]]


def export_ffuf(session_id: str, db_path: Path) -> str:
    """Newline-separated path list — one path per line, no trailing newline."""
    paths = _distinct_paths(Path(db_path), session_id)
    return "\n".join(paths)


def export_burp_scope(
    session_id: str,
    db_path: Path,
    host: str,
) -> str:
    """Burp Suite Pro scope XML for one host + every recorded path."""
    paths = _distinct_paths(Path(db_path), session_id)
    items: list[str] = []
    safe_host = _xml.escape(host)
    for p in paths:
        safe_path = _xml.escape(p)
        items.append(
            "<item>"
            "<enabled>true</enabled>"
            f"<host>{safe_host}</host>"
            f"<file>{safe_path}</file>"
            "<protocol>http</protocol>"
            "</item>"
        )
    return (
        "<BurpSuite><target><scope>"
        + "".join(items)
        + "</scope></target></BurpSuite>"
    )
