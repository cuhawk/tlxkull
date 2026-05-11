"""SQLite + OpenAPI serialisation for mock_backend.

## Connection scoping

Two deliberate patterns coexist:

- **Shared connection** at kernel.services["mock_backend_db"]:
  opened by init_session_db, used by slash dispatch (sync thread)
  and the bg event-loop thread (mock_start servers). Transactions
  on this conn are visible across both threads because
  check_same_thread=False.

- **Per-call connections** opened by _write_finding
  (browser_session.py), mock_auth (tools/mock_auth.py), and
  StoredFlowReplay._connect (stored_flow_replay.py): short-lived,
  cross thread boundaries, do not coordinate with the shared
  conn's transaction. They go through _open_conn for consistent
  pragmas.

Both patterns are safe under WAL. Do not try to unify.
"""
from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .route_extractor import RouteSpec
from .sw_ws_observer import SWObservation, WSFrame

SCHEMA = """
CREATE TABLE IF NOT EXISTS mock_sessions (
  id TEXT PRIMARY KEY,
  cg_db_path TEXT NOT NULL,
  target TEXT NOT NULL,
  port INTEGER DEFAULT 0,
  mode TEXT DEFAULT 'extract',
  scaffolded_html_path TEXT,
  started TEXT NOT NULL,
  stopped TEXT
);

CREATE TABLE IF NOT EXISTS mock_routes (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL
    REFERENCES mock_sessions(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  method TEXT NOT NULL,
  shape_hint TEXT,
  ui_reachable INTEGER DEFAULT 0,
  source_file TEXT,
  source_line INTEGER,
  sink_id TEXT
);

CREATE TABLE IF NOT EXISTS mock_findings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL
    REFERENCES mock_sessions(id) ON DELETE CASCADE,
  chain_id TEXT NOT NULL,
  confirmed INTEGER NOT NULL DEFAULT 0,
  probe_value TEXT,
  hits_json TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE (session_id, chain_id)
);

CREATE TABLE IF NOT EXISTS mock_auth_obs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  key TEXT,
  value_snippet TEXT,
  observed_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mock_flow (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  method TEXT NOT NULL,
  path TEXT NOT NULL,
  request_body TEXT,
  response_body TEXT NOT NULL,
  status_code INTEGER DEFAULT 200,
  source TEXT NOT NULL DEFAULT 'record',
  recorded_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mock_requests (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id    TEXT NOT NULL,
  method        TEXT NOT NULL,
  path          TEXT NOT NULL,
  query_string  TEXT,
  status_code   INTEGER,
  request_body_snippet  TEXT,
  response_body_snippet TEXT,
  content_type  TEXT,
  source        TEXT NOT NULL,
  observed_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mock_sw_obs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  scope TEXT NOT NULL,
  script_url TEXT NOT NULL,
  observed_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS mock_ws_frames (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  url TEXT NOT NULL,
  direction TEXT NOT NULL,
  payload_snippet TEXT,
  observed_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_routes_session
  ON mock_routes(session_id);
CREATE INDEX IF NOT EXISTS idx_findings_session
  ON mock_findings(session_id);
CREATE INDEX IF NOT EXISTS idx_auth_obs_session
  ON mock_auth_obs(session_id);
CREATE INDEX IF NOT EXISTS idx_flow_session
  ON mock_flow(session_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_mock_flow_smp
  ON mock_flow(session_id, method, path);
CREATE INDEX IF NOT EXISTS idx_requests_session
  ON mock_requests(session_id);
CREATE INDEX IF NOT EXISTS idx_requests_session_path
  ON mock_requests(session_id, path);
CREATE INDEX IF NOT EXISTS idx_sw_obs_session
  ON mock_sw_obs(session_id);
CREATE INDEX IF NOT EXISTS idx_ws_frames_session
  ON mock_ws_frames(session_id);
"""


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA synchronous=NORMAL")


def _open_conn(db_path: Path) -> sqlite3.Connection:
    """Per-call short-lived connection. WAL already set by
    init_session_db on first open; this just applies per-conn
    pragmas."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    _apply_pragmas(conn)
    return conn


def init_session_db(db_path: Path) -> sqlite3.Connection:
    """Open (or create) the mock_backend SQLite DB and ensure schema.

    ``check_same_thread=False`` because mock_backend tooling crosses
    threads (slash-dispatch sync thread vs the long-running event-loop
    thread used to keep mock_start servers alive between calls).
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.executescript(SCHEMA)
    _migrate_mock_flow_source(conn)
    conn.execute("PRAGMA journal_mode=WAL")
    _apply_pragmas(conn)
    conn.commit()
    return conn


def _migrate_mock_flow_source(conn: sqlite3.Connection) -> None:
    """Idempotent ALTER: add `source` column to mock_flow on legacy DBs.

    Fresh DBs already have the column via SCHEMA. Re-opens raise
    OperationalError("duplicate column name") which we swallow.
    Any other failure mode propagates — silent skip would mask real
    schema corruption.
    """
    try:
        conn.execute(
            "ALTER TABLE mock_flow ADD COLUMN source TEXT NOT NULL "
            "DEFAULT 'record'"
        )
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def record_session(
    conn: sqlite3.Connection,
    session_id: str,
    cg_db_path: str,
    target: str,
    scaffolded_html_path: str | None = None,
) -> None:
    conn.execute(
        "INSERT INTO mock_sessions "
        "(id, cg_db_path, target, port, mode, scaffolded_html_path, started) "
        "VALUES (?, ?, ?, 0, 'extract', ?, ?)",
        (session_id, cg_db_path, target, scaffolded_html_path, _now()),
    )
    conn.commit()


def record_routes(
    conn: sqlite3.Connection,
    session_id: str,
    routes: list[RouteSpec],
) -> None:
    import json
    import uuid
    for r in routes:
        rid = uuid.uuid4().hex[:12]
        conn.execute(
            "INSERT INTO mock_routes "
            "(id, session_id, url, method, shape_hint, ui_reachable, "
            " source_file, source_line, sink_id) "
            "VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)",
            (
                rid,
                session_id,
                r.url,
                r.method,
                json.dumps(r.shape_hint) if r.shape_hint is not None else None,
                r.source_file,
                r.source_line,
                r.sink_id,
            ),
        )
    conn.commit()


def get_session(
    conn: sqlite3.Connection, session_id: str
) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT id, cg_db_path, target, port, mode, "
        "scaffolded_html_path, started, stopped "
        "FROM mock_sessions WHERE id=?",
        (session_id,),
    ).fetchone()
    if row is None:
        return None
    keys = (
        "id", "cg_db_path", "target", "port", "mode",
        "scaffolded_html_path", "started", "stopped",
    )
    return dict(zip(keys, row, strict=True))


def get_routes(
    conn: sqlite3.Connection, session_id: str
) -> list[RouteSpec]:
    import json
    rows = conn.execute(
        "SELECT url, method, shape_hint, source_file, source_line, sink_id "
        "FROM mock_routes WHERE session_id=? "
        "ORDER BY source_file, source_line, method, url",
        (session_id,),
    ).fetchall()
    out: list[RouteSpec] = []
    for url, method, shape_hint, source_file, source_line, sink_id in rows:
        shape: dict[str, Any] | None
        shape = json.loads(shape_hint) if shape_hint else None
        out.append(RouteSpec(
            url=url,
            method=method,
            shape_hint=shape,
            source_file=source_file or "",
            source_line=source_line or 0,
            sink_id=sink_id or "",
        ))
    return out


def render_extract_summary(routes: list[RouteSpec]) -> str:
    """Markdown summary: total, methods breakdown, top 10 by frequency, sinks."""
    if not routes:
        return "**Routes:** 0 (no HTTP sinks found)"

    total = len(routes)
    methods = Counter(r.method for r in routes)
    sinks = Counter(r.sink_id for r in routes)
    by_url: Counter[str] = Counter()
    for r in routes:
        by_url[f"{r.method} {r.url}"] += 1

    lines = [
        f"**Routes:** {total}",
        "",
        "**Methods:**",
    ]
    for m, n in methods.most_common():
        lines.append(f"- {m}: {n}")
    lines.append("")
    lines.append("**Top 10 by frequency:**")
    for key, n in by_url.most_common(10):
        lines.append(f"- {key} ×{n}")
    lines.append("")
    lines.append("**Sinks:**")
    for s, n in sinks.most_common():
        lines.append(f"- {s}: {n}")
    return "\n".join(lines)


def _strip_probe(node: Any) -> Any:
    """Replace PROBE_SENTINEL leaves with an empty string for OpenAPI cleanliness."""
    from .response_factory import PROBE_SENTINEL
    if isinstance(node, dict):
        return {k: _strip_probe(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_strip_probe(v) for v in node]
    if isinstance(node, str) and node == PROBE_SENTINEL:
        return ""
    return node


def to_openapi(routes: list[RouteSpec]) -> dict[str, Any]:
    """OpenAPI 3.1 dict — group routes by path, aggregate methods."""
    from .mock_server import url_to_starlette_path

    paths: dict[str, dict[str, Any]] = defaultdict(dict)
    for r in routes:
        path = url_to_starlette_path(r.url)
        method = r.method.lower()
        if method in paths[path]:
            continue
        example = _strip_probe(r.shape_hint) if r.shape_hint else {}
        paths[path][method] = {
            "summary": f"{r.method} {r.url}",
            "responses": {
                "200": {
                    "description": "OK",
                    "content": {
                        "application/json": {"example": example},
                    },
                },
            },
        }

    return {
        "openapi": "3.1.0",
        "info": {"title": "tlx mock_backend extracted routes", "version": "0.1.0"},
        "servers": [{"url": "http://127.0.0.1"}],
        "paths": dict(sorted(paths.items())),
    }


def record_sw_observations(
    conn: sqlite3.Connection,
    session_id: str,
    observations: list[SWObservation],
) -> int:
    if not observations:
        return 0
    rows = [(session_id, o.scope, o.script_url) for o in observations]
    try:
        conn.execute("BEGIN")
        conn.executemany(
            "INSERT INTO mock_sw_obs (session_id, scope, script_url) "
            "VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return len(rows)


def record_ws_frames(
    conn: sqlite3.Connection,
    session_id: str,
    frames: list[WSFrame],
) -> int:
    if not frames:
        return 0
    rows = [
        (session_id, f.url, f.direction, f.payload_snippet) for f in frames
    ]
    try:
        conn.execute("BEGIN")
        conn.executemany(
            "INSERT INTO mock_ws_frames "
            "(session_id, url, direction, payload_snippet) "
            "VALUES (?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return len(rows)
