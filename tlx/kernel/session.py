"""SQLite-backed session store — single source of truth for session state."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from kernel.schema import Message, Usage

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  name TEXT UNIQUE,
  created_at INTEGER NOT NULL,
  active_engine TEXT NOT NULL,
  active_model TEXT NOT NULL,
  caveman_mode TEXT NOT NULL DEFAULT 'lite',
  compaction_threshold INTEGER DEFAULT 120000
);

CREATE TABLE IF NOT EXISTS turns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL REFERENCES sessions(id),
  idx INTEGER NOT NULL,
  role TEXT NOT NULL,
  content_json TEXT NOT NULL,
  usage_json TEXT,
  cost_usd REAL,
  ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tool_calls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  turn_id INTEGER NOT NULL REFERENCES turns(id),
  name TEXT NOT NULL,
  args_json TEXT NOT NULL,
  result_json TEXT,
  duration_ms INTEGER,
  ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS kv (
  session_id TEXT NOT NULL REFERENCES sessions(id),
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  PRIMARY KEY (session_id, key)
);

CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id, idx);
"""


class SessionNotFoundError(Exception):
    """Raised when load() can't find a session by name."""


class Session(BaseModel):
    id: str
    name: str | None
    created_at: int
    active_engine: str
    active_model: str
    caveman_mode: str
    compaction_threshold: int


def _row_to_session(row: sqlite3.Row) -> Session:
    return Session(
        id=row["id"],
        name=row["name"],
        created_at=row["created_at"],
        active_engine=row["active_engine"],
        active_model=row["active_model"],
        caveman_mode=row["caveman_mode"],
        compaction_threshold=row["compaction_threshold"],
    )


class SessionStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        self._current_session_id: str | None = None

    def set_current_session(self, session_id: str) -> None:
        self._current_session_id = session_id

    def set(self, key: str, value: str, session_id: str | None = None) -> None:
        sid = session_id or self._current_session_id
        if sid is None:
            raise RuntimeError("session_store.set: no session selected")
        self._conn.execute(
            "INSERT OR REPLACE INTO kv (session_id, key, value) VALUES (?, ?, ?)",
            (sid, key, value),
        )
        self._conn.commit()

    def get(self, key: str, session_id: str | None = None) -> str | None:
        sid = session_id or self._current_session_id
        if sid is None:
            return None
        row = self._conn.execute(
            "SELECT value FROM kv WHERE session_id = ? AND key = ?",
            (sid, key),
        ).fetchone()
        return row["value"] if row else None

    def close(self) -> None:
        self._conn.close()

    def new_session(self, engine: str, model: str) -> Session:
        sid = str(uuid.uuid4())
        now = int(time.time())
        self._conn.execute(
            "INSERT INTO sessions (id, name, created_at, active_engine, active_model, "
            "caveman_mode, compaction_threshold) VALUES (?, NULL, ?, ?, ?, 'lite', 120000)",
            (sid, now, engine, model),
        )
        self._conn.commit()
        return Session(
            id=sid,
            name=None,
            created_at=now,
            active_engine=engine,
            active_model=model,
            caveman_mode="lite",
            compaction_threshold=120000,
        )

    def save_as(self, session_id: str, name: str) -> None:
        cur = self._conn.execute(
            "UPDATE sessions SET name = ? WHERE id = ?", (name, session_id)
        )
        if cur.rowcount == 0:
            raise SessionNotFoundError(f"session id not found: {session_id}")
        self._conn.commit()

    def load(self, name: str) -> Session:
        row = self._conn.execute(
            "SELECT * FROM sessions WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            raise SessionNotFoundError(f"no session named: {name}")
        return _row_to_session(row)

    def clear_all(self) -> None:
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("DELETE FROM tool_calls")
        self._conn.execute("DELETE FROM turns")
        self._conn.execute("DELETE FROM kv")
        self._conn.execute("DELETE FROM sessions")
        self._conn.commit()

    def list_sessions(self) -> list[Session]:
        rows = self._conn.execute(
            "SELECT * FROM sessions ORDER BY created_at DESC"
        ).fetchall()
        return [_row_to_session(r) for r in rows]

    def append_turn(
        self,
        session_id: str,
        role: str,
        content: str | list[Any],
        usage: Usage | None,
        cost_usd: float | None,
    ) -> int:
        next_idx_row = self._conn.execute(
            "SELECT COALESCE(MAX(idx) + 1, 0) AS n FROM turns WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        idx = int(next_idx_row["n"])

        if isinstance(content, str):
            content_json = json.dumps(content)
        else:
            content_json = json.dumps(
                [
                    block.model_dump(mode="json") if hasattr(block, "model_dump") else block
                    for block in content
                ]
            )

        usage_json = usage.model_dump_json() if usage is not None else None
        ts = int(time.time())

        cur = self._conn.execute(
            "INSERT INTO turns (session_id, idx, role, content_json, usage_json, cost_usd, ts) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, idx, role, content_json, usage_json, cost_usd, ts),
        )
        self._conn.commit()
        rowid = cur.lastrowid
        if rowid is None:
            raise RuntimeError("INSERT into turns produced no lastrowid")
        return int(rowid)

    def append_tool_call(
        self,
        turn_id: int,
        name: str,
        args: dict,
        result: str | None,
        duration_ms: int | None,
    ) -> None:
        self._conn.execute(
            "INSERT INTO tool_calls (turn_id, name, args_json, result_json, duration_ms, ts) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (turn_id, name, json.dumps(args), result, duration_ms, int(time.time())),
        )
        self._conn.commit()

    def get_history(self, session_id: str) -> list[Message]:
        rows = self._conn.execute(
            "SELECT role, content_json FROM turns WHERE session_id = ? ORDER BY idx ASC",
            (session_id,),
        ).fetchall()
        out: list[Message] = []
        for row in rows:
            content = json.loads(row["content_json"])
            out.append(Message.model_validate({"role": row["role"], "content": content}))
        return out

    def cache_hit_rate(self, session_id: str) -> float:
        rows = self._conn.execute(
            "SELECT usage_json FROM turns WHERE session_id = ? AND usage_json IS NOT NULL",
            (session_id,),
        ).fetchall()
        total_in = 0
        total_cache_read = 0
        total_cache_write = 0
        for row in rows:
            data = json.loads(row["usage_json"])
            total_in += int(data.get("input_tokens", 0))
            total_cache_read += int(data.get("cache_read_tokens", 0))
            total_cache_write += int(data.get("cache_write_tokens", 0))
        denom = total_in + total_cache_read + total_cache_write
        if denom <= 0:
            return 0.0
        return total_cache_read / denom
