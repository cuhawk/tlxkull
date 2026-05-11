"""Audit-run persistence over the js_audit_runs / js_audit_turns tables.

Replay-ready: every assistant + tool_result turn is stored verbatim.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _open_conn(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def _serialize(content: Any) -> str:
    if isinstance(content, str):
        return content
    try:
        return json.dumps(content, default=_block_to_dict)
    except TypeError:
        return json.dumps(str(content))


def _block_to_dict(obj: Any) -> Any:
    """Best-effort serializer for anthropic SDK content blocks."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    return str(obj)


class AuditRun:
    """Lifecycle wrapper over js_audit_runs + js_audit_turns.

    Caller owns the connection. Methods commit each write so partial
    runs are durable on crash.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        shell_session_id: str,
        target_folder: str,
        external_run_id: str | None = None,
    ) -> None:
        self.conn = conn
        self.shell_session_id = shell_session_id
        self.target_folder = target_folder
        self.external_run_id = external_run_id
        self.run_id: int | None = None
        self._turn_index = 0

    def start(self) -> int:
        if self.external_run_id is not None:
            row = self.conn.execute(
                "SELECT id FROM js_audit_runs WHERE external_run_id=?",
                (self.external_run_id,),
            ).fetchone()
            if row is not None:
                self.run_id = int(row[0])
                return self.run_id
        started_at = datetime.now(UTC).isoformat()
        cur = self.conn.execute(
            "INSERT INTO js_audit_runs "
            "(shell_session_id, target_folder, started_at, status, "
            " external_run_id) "
            "VALUES (?, ?, ?, 'running', ?)",
            (
                self.shell_session_id,
                self.target_folder,
                started_at,
                self.external_run_id,
            ),
        )
        self.conn.commit()
        self.run_id = int(cur.lastrowid)
        return self.run_id

    def append_turn(
        self,
        role: str,
        content: Any,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        if self.run_id is None:
            raise RuntimeError("AuditRun.append_turn called before start()")
        self.conn.execute(
            "INSERT INTO js_audit_turns "
            "(run_id, turn_index, role, content_json, "
            " tokens_in, tokens_out, cost_usd) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self.run_id,
                self._turn_index,
                role,
                _serialize(content),
                tokens_in,
                tokens_out,
                cost_usd,
            ),
        )
        self.conn.commit()
        self._turn_index += 1

    def finish(
        self,
        status: str,
        total_tokens: int,
        cost_usd: float,
        consults_used: int,
        consults_cost_usd: float,
        failure_reason: str | None = None,
    ) -> None:
        if self.run_id is None:
            raise RuntimeError("AuditRun.finish called before start()")
        finished_at = datetime.now(UTC).isoformat()
        self.conn.execute(
            "UPDATE js_audit_runs SET "
            "  finished_at=?, status=?, total_tokens=?, cost_usd=?, "
            "  consults_used=?, consults_cost_usd=?, failure_reason=? "
            "WHERE id=?",
            (
                finished_at,
                status,
                total_tokens,
                cost_usd,
                consults_used,
                consults_cost_usd,
                failure_reason,
                self.run_id,
            ),
        )
        self.conn.commit()
