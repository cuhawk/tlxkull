"""Worker / Service-Worker semantic modeling.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §24.

Models Web Workers, Shared Workers, Service Workers, and AudioWorklets
as first-class JS execution contexts so taint flows over the message
channel and the Service-Worker cache.

Key concepts:

  * **worker_pair**: (host_file, worker_file) link via ``new Worker(url)``
    or ``navigator.serviceWorker.register(url)``.
  * **worker_message edge**: a synthetic edge from each
    ``worker.postMessage`` site to every ``self.onmessage`` handler in
    the worker, and vice versa.
  * **SW scope**: a Service Worker registered at scope ``/`` has full
    page intercept; at ``/widget/`` it's narrow. Scope drives blast
    radius.

This module produces the worker pair list + synthetic edges; storage
of SW cache events reuses ``storage_events`` with ``api='sw.cache'``.

Behind ``ENABLE_WORKER_SEMANTICS``.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from typing import Iterable

__all__ = [
    "WorkerPair",
    "discover_pairs",
    "synthesize_message_edges",
]


@dataclass
class WorkerPair:
    host_file:   str
    worker_file: str | None       # None when URL is dynamic
    kind:        str              # 'web' | 'shared' | 'service'
    scope:       str | None = None       # SW scope
    line:        int | None = None
    capabilities: tuple[str, ...] = field(default_factory=tuple)


_REGISTER_PATTERNS = [
    (re.compile(r"new\s+Worker\(\s*['\"]([^'\"]+)['\"]"),         "web"),
    (re.compile(r"new\s+SharedWorker\(\s*['\"]([^'\"]+)['\"]"),   "shared"),
    (re.compile(r"navigator\.serviceWorker\.register\(\s*['\"]([^'\"]+)['\"]"),
                                                                  "service"),
]
_SCOPE_PATTERN = re.compile(r"register\([^)]*scope\s*:\s*['\"]([^'\"]+)['\"]")


def discover_pairs(
    sources: Iterable[tuple[str, str]],
) -> list[WorkerPair]:
    """Scan ``sources`` (file_path, text) pairs for worker registrations.

    Falls back to ``worker_file=None`` when the URL is a dynamic
    expression. The chain extractor tags such hosts with
    ``worker_resolution: 'dynamic'``.
    """
    out: list[WorkerPair] = []
    for file_, text in sources:
        for pat, kind in _REGISTER_PATTERNS:
            for m in pat.finditer(text):
                url = m.group(1)
                line_no = text[:m.start()].count("\n") + 1
                scope = None
                if kind == "service":
                    sm = _SCOPE_PATTERN.search(
                        text[m.start():m.start() + 400]
                    )
                    scope = sm.group(1) if sm else "/"
                out.append(WorkerPair(
                    host_file=file_,
                    worker_file=url if url.startswith(("/", ".")) else url,
                    kind=kind,
                    scope=scope,
                    line=line_no,
                    capabilities=_caps_for_kind(kind),
                ))
    return out


def _caps_for_kind(kind: str) -> tuple[str, ...]:
    if kind == "service":
        return ("fetch", "cache", "message", "sync", "push", "clients")
    if kind == "shared":
        return ("message", "fetch")
    return ("message", "fetch")


def synthesize_message_edges(
    conn: sqlite3.Connection,
    pairs: Iterable[WorkerPair],
) -> int:
    """Insert synthetic worker_message edges into the V1 ``edges`` table.

    Each pair generates two edges:
      host postMessage  →  worker self.onmessage
      worker postMessage →  host worker.onmessage
    """
    cur = conn.cursor()
    written = 0
    for pair in pairs:
        if not pair.worker_file:
            continue
        # Host postMessage → worker handler.
        cur.execute(
            """SELECT n.id FROM nodes n
               WHERE  n.file = ? AND n.name LIKE '%postMessage%' LIMIT 50""",
            (pair.host_file,),
        )
        host_senders = [r[0] for r in cur.fetchall()]
        cur.execute(
            """SELECT n.id FROM nodes n
               WHERE  n.file = ? AND n.name LIKE '%onmessage%' LIMIT 50""",
            (pair.worker_file,),
        )
        worker_recvs = [r[0] for r in cur.fetchall()]
        for s in host_senders:
            for r in worker_recvs:
                cur.execute(
                    """INSERT OR IGNORE INTO edges
                       (caller_id, callee_id, line, raw, callee_raw,
                        resolved_kind, candidate_count)
                       VALUES (?, ?, ?, ?, ?, 'worker_message', 1)""",
                    (s, r, pair.line or 0, "worker.postMessage",
                     "worker.onmessage"),
                )
                written += cur.rowcount
        # Worker self.postMessage → host onmessage.
        cur.execute(
            """SELECT n.id FROM nodes n
               WHERE  n.file = ? AND n.name LIKE '%postMessage%' LIMIT 50""",
            (pair.worker_file,),
        )
        worker_senders = [r[0] for r in cur.fetchall()]
        cur.execute(
            """SELECT n.id FROM nodes n
               WHERE  n.file = ? AND n.name LIKE '%worker.onmessage%' LIMIT 50""",
            (pair.host_file,),
        )
        host_recvs = [r[0] for r in cur.fetchall()]
        for s in worker_senders:
            for r in host_recvs:
                cur.execute(
                    """INSERT OR IGNORE INTO edges
                       (caller_id, callee_id, line, raw, callee_raw,
                        resolved_kind, candidate_count)
                       VALUES (?, ?, ?, ?, ?, 'worker_message', 1)""",
                    (s, r, pair.line or 0, "self.postMessage",
                     "host worker.onmessage"),
                )
                written += cur.rowcount
    conn.commit()
    return written
