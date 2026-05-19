"""V2 §24 — Worker / Service Worker semantic modeling.

Detects worker boundaries (``new Worker(...)``, ``navigator.serviceWorker
.register(...)``, SharedWorker constructors) and the message channel
edges between host pages and their workers.

Off by default; ``JS_ENABLE_WORKER_SEMANTICS=1`` to enable.

Outputs:
- table ``worker_pairs`` (host_file ↔ worker_file)
- table ``worker_messages``
- sidecar ``worker_semantics.json``
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
CREATE TABLE IF NOT EXISTS worker_pairs (
    id INTEGER PRIMARY KEY,
    host_node_id INTEGER NOT NULL,
    worker_file TEXT NOT NULL,
    kind TEXT NOT NULL,         -- 'web' | 'shared' | 'service' | 'audio-worklet'
    scope TEXT,                 -- service-worker scope when known
    host_file TEXT,
    line INTEGER
);
CREATE INDEX IF NOT EXISTS idx_worker_kind ON worker_pairs(kind);

CREATE TABLE IF NOT EXISTS worker_messages (
    id INTEGER PRIMARY KEY,
    sender_node_id INTEGER NOT NULL,
    target_node_id INTEGER,       -- nullable when target file isn't indexed
    channel TEXT NOT NULL,        -- 'host->worker' | 'worker->host' | 'sw->client'
    cross_client INTEGER DEFAULT 0,
    file TEXT,
    line INTEGER
);
"""


_NEW_WORKER_RE = re.compile(
    r"""new\s+(Worker|SharedWorker|AudioWorkletNode)\s*\(\s*['"`]([^'"`]+)['"`]""",
)
_SW_REGISTER_RE = re.compile(
    r"""navigator\.serviceWorker\.register\s*\(\s*['"`]([^'"`]+)['"`]"""
    r"""(?:[^)]*scope\s*:\s*['"`]([^'"`]+)['"`])?""",
    re.DOTALL,
)
_WORKER_POSTMESSAGE_RE = re.compile(
    r"""(?:worker|sw|registration\.active)\.postMessage\s*\(""",
    re.IGNORECASE,
)
_SELF_POSTMESSAGE_RE = re.compile(r"""self\.postMessage\s*\(""")
_CLIENTS_MATCHALL_RE = re.compile(
    r"""clients\.matchAll\s*\(.*?\)\s*\.\s*then\s*\(""",
    re.DOTALL,
)


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    clear_table(conn, "worker_pairs")
    clear_table(conn, "worker_messages")

    meta = load_node_meta(conn)
    workers: list[tuple] = []
    messages: list[tuple] = []

    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        node = meta.get(caller_id, {})
        for m in _NEW_WORKER_RE.finditer(raw):
            kind = {"Worker": "web", "SharedWorker": "shared",
                    "AudioWorkletNode": "audio-worklet"}[m.group(1)]
            workers.append((
                caller_id, m.group(2), kind, None,
                node.get("file", ""), int(line or 0),
            ))
        sw = _SW_REGISTER_RE.search(raw)
        if sw:
            workers.append((
                caller_id, sw.group(1), "service", sw.group(2) or "/",
                node.get("file", ""), int(line or 0),
            ))
        if _WORKER_POSTMESSAGE_RE.search(raw):
            messages.append((
                caller_id, None, "host->worker", 0,
                node.get("file", ""), int(line or 0),
            ))
        if _SELF_POSTMESSAGE_RE.search(raw):
            messages.append((
                caller_id, None, "worker->host", 0,
                node.get("file", ""), int(line or 0),
            ))
        if _CLIENTS_MATCHALL_RE.search(raw):
            messages.append((
                caller_id, None, "sw->client", 1,
                node.get("file", ""), int(line or 0),
            ))

    for r in workers:
        conn.execute(
            "INSERT INTO worker_pairs "
            "(host_node_id, worker_file, kind, scope, host_file, line) "
            "VALUES (?,?,?,?,?,?)", r,
        )
    for r in messages:
        conn.execute(
            "INSERT INTO worker_messages "
            "(sender_node_id, target_node_id, channel, cross_client, "
            " file, line) VALUES (?,?,?,?,?,?)", r,
        )
    conn.commit()

    sidecar = {
        "worker_pairs": len(workers),
        "worker_messages": len(messages),
        "by_kind": {k: int(n) for k, n in conn.execute(
            "SELECT kind, COUNT(*) FROM worker_pairs GROUP BY kind"
        )},
        "by_channel": {k: int(n) for k, n in conn.execute(
            "SELECT channel, COUNT(*) FROM worker_messages GROUP BY channel"
        )},
    }
    write_sidecar(target_dir, "worker_semantics.json", sidecar)
    return sidecar
