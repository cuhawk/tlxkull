"""OpenAPI 3.x exporter — extends 7A's to_openapi() with 7D summary fields.

Adds an ``x-tlx-summary`` block under ``info`` with counts of recorded
auth observations and mock_findings rows for the session.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .reporter import _open_conn, get_routes, to_openapi


def export_openapi(
    db_path: Path,
    session_id: str,
) -> dict[str, Any]:
    """Build OpenAPI dict for ``session_id`` with TLX session summary."""
    conn = _open_conn(db_path)
    try:
        routes = get_routes(conn, session_id)
        spec = to_openapi(routes)

        auth_count = conn.execute(
            "SELECT COUNT(*) FROM mock_auth_obs WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]
        findings_count = conn.execute(
            "SELECT COUNT(*) FROM mock_findings WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]
        confirmed_count = conn.execute(
            "SELECT COUNT(*) FROM mock_findings "
            "WHERE session_id=? AND confirmed=1",
            (session_id,),
        ).fetchone()[0]
    finally:
        conn.close()

    info = spec.setdefault("info", {})
    info["x-tlx-summary"] = {
        "session_id": session_id,
        "auth_observations": int(auth_count),
        "findings_total": int(findings_count),
        "findings_confirmed": int(confirmed_count),
    }
    return spec
