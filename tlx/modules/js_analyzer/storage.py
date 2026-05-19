"""Persistent client-side state taint (storage_events + synthetic edges).

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §11.

Captures localStorage / sessionStorage / IndexedDB / Cache API /
cookies / history.pushState / window.name / BroadcastChannel /
Service-Worker cache reads and writes from the AST extractor's call
records, then synthesizes write→read edges keyed by storage API + key.

Two sides:

  1. ``ingest(conn, calls)`` — populates ``storage_events`` from raw call
     records produced by ast_extractor.js. The extractor stamps each
     storage-touching site with ``ast_kind == 'storage_event'`` plus
     ``api``, ``op``, ``key_static``, ``value_node``, ``framework_hint``,
     and the surrounding ``node_id`` / ``file`` / ``line``.

  2. ``synthesize_edges(conn, *, max_pairs)`` — joins write rows to read
     rows by (api, key_static) and yields synthetic edges. Confidence
     follows §11.7.

The chain extractor consumes ``synthesize_edges`` as a generator of
extra ``(from_node, to_node, kind='storage', confidence)`` rows and
plugs them into its BFS with a per-chain ``max_storage_hops`` cap
(default 1) and a global ``max_pairs`` cap (default 2000).

Behind ``ENABLE_PERSISTENT_TAINT``.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterable, Iterator

__all__ = [
    "StorageAPI",
    "StorageEvent",
    "ingest",
    "synthesize_edges",
    "persistence_confidence",
    "SECRET_KEY_HINTS",
]


# Recognized persistence APIs, mapped to a coarse phase hint when the
# API alone implies a phase (most don't).
StorageAPI = str   # "localStorage" | "sessionStorage" | ... etc

_VALID_APIS: frozenset[StorageAPI] = frozenset((
    "localStorage", "sessionStorage", "indexedDB",
    "cookie", "cacheApi", "history", "window.name",
    "broadcastChannel", "sw.cache",
))


# Heuristic key-name patterns that mark a stored value as likely-sensitive.
SECRET_KEY_HINTS: tuple[str, ...] = (
    "token", "jwt", "auth", "session", "refresh",
    "access", "bearer", "credential", "secret", "key",
)


@dataclass(frozen=True)
class StorageEvent:
    node_id: int
    api: StorageAPI
    op: str                 # 'read' | 'write' | 'delete' | 'list'
    key_static: str | None
    key_dynamic: str | None
    key_provenance: str     # 'literal' | 'configured' | 'user-input' | 'computed'
    value_node: int | None
    is_secret_hint: bool
    phase: str | None       # 'early-load' | 'user-action' | 'post-fetch' | 'shutdown'
    file: str
    line: int | None
    framework_hint: str | None


def _classify_phase(qname: str, file: str) -> str | None:
    """Coarse phase inference from the enclosing function qname.

    Best-effort; returns ``None`` when undetermined so downstream
    scoring degrades to the API default.
    """
    q = (qname or "").lower()
    if any(p in q for p in ("init", "bootstrap", "main", "setup",
                            "componentdidmount", "useeffect", "onmounted")):
        return "early-load"
    if any(p in q for p in ("click", "submit", "handle", "onchange",
                            "press", "tap", "input")):
        return "user-action"
    if any(p in q for p in ("then", "callback", "onsuccess", "onload",
                            "onresult", "onresponse", "fetch", "axios")):
        return "post-fetch"
    if any(p in q for p in ("beforeunload", "unmount", "destroy",
                            "componentwillunmount")):
        return "shutdown"
    return None


def _is_secret_hint(key: str | None) -> bool:
    if not key:
        return False
    k = key.lower()
    return any(h in k for h in SECRET_KEY_HINTS)


def ingest(
    conn: sqlite3.Connection,
    calls: Iterable[dict],
) -> int:
    """Insert storage events from a stream of AST-extractor call records.

    Each record is expected to carry::

        {
          "ast_kind": "storage_event",
          "node_id": int,
          "api": str,
          "op": "read"|"write"|"delete"|"list",
          "key_static": str | None,
          "key_dynamic": str | None,
          "key_provenance": str,
          "value_node": int | None,
          "qname": str,         # enclosing function qname
          "file": str,
          "line": int | None,
          "framework_hint": str | None,
        }

    Unknown or malformed records are skipped. Returns the count of rows
    actually inserted.
    """
    cur = conn.cursor()
    inserted = 0
    for rec in calls:
        if (rec.get("ast_kind") != "storage_event") or rec.get("api") not in _VALID_APIS:
            continue
        api = rec["api"]
        op = rec.get("op")
        if op not in ("read", "write", "delete", "list"):
            continue
        ev = StorageEvent(
            node_id        = rec.get("node_id") or 0,
            api            = api,
            op             = op,
            key_static     = rec.get("key_static"),
            key_dynamic    = rec.get("key_dynamic"),
            key_provenance = rec.get("key_provenance") or "literal",
            value_node     = rec.get("value_node"),
            is_secret_hint = _is_secret_hint(rec.get("key_static")),
            phase          = _classify_phase(rec.get("qname", ""),
                                              rec.get("file", "")),
            file           = rec.get("file") or "",
            line           = rec.get("line"),
            framework_hint = rec.get("framework_hint"),
        )
        try:
            cur.execute(
                """INSERT OR IGNORE INTO storage_events
                   (node_id, api, op, key_static, key_dynamic,
                    key_provenance, value_node, is_secret_hint, phase,
                    file, line, framework_hint)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (ev.node_id, ev.api, ev.op, ev.key_static, ev.key_dynamic,
                 ev.key_provenance, ev.value_node, int(ev.is_secret_hint),
                 ev.phase, ev.file, ev.line, ev.framework_hint),
            )
            inserted += cur.rowcount
        except sqlite3.OperationalError:
            # Table missing: caller forgot to run v2_schema.apply(); be
            # explicit so they can see what's wrong.
            raise
    conn.commit()
    return inserted


def persistence_confidence(write_row: dict, read_row: dict) -> float:
    """§11.7 confidence model. Inputs are sqlite Row-like dicts with
    keys matching ``storage_events`` columns.
    """
    score = 0.0
    if write_row.get("key_static") and write_row["key_static"] == read_row.get("key_static"):
        score += 0.6
    if write_row.get("value_node"):
        score += 0.2     # value carried a real expression, not a literal
    # Bundle-entry penalty placeholder — chain extractor knows its
    # entry context and can subtract 0.2 when read lives in a different
    # webpack chunk. Done caller-side; here we keep the base.
    if write_row.get("phase") in ("early-load", "post-fetch") \
       and read_row.get("phase") == "user-action":
        score += 0.1     # Trinity-style narrative bonus
    return max(0.05, min(0.95, score))


def synthesize_edges(
    conn: sqlite3.Connection,
    *,
    max_pairs: int = 2000,
) -> Iterator[dict]:
    """Yield ``(write, read)`` pairings as synthetic edge dicts.

    Yielded edge shape::

        {
          "kind": "storage",
          "api": "localStorage",
          "key": "lastRoute",
          "from_node": <value_node of write>,
          "to_node":   <node_id of read>,
          "write_file": ..., "write_line": ...,
          "read_file":  ..., "read_line": ...,
          "confidence": float,
          "phase_pair": (write_phase, read_phase),
        }

    Generation is bounded by ``max_pairs`` to keep the BFS tractable
    on the rare global-bundle case.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT w.node_id   AS w_node,
               w.api       AS w_api,
               w.key_static AS w_key,
               w.value_node AS w_val,
               w.file      AS w_file,
               w.line      AS w_line,
               w.phase     AS w_phase,
               r.node_id   AS r_node,
               r.file      AS r_file,
               r.line      AS r_line,
               r.phase     AS r_phase
        FROM   storage_events w
        JOIN   storage_events r
          ON   w.api = r.api
         AND   w.op  = 'write'
         AND   r.op  = 'read'
         AND   w.key_static = r.key_static
         AND   w.key_static IS NOT NULL
        LIMIT  ?""",
        (max_pairs,),
    )
    for row in cur.fetchall():
        keys = ("w_node", "w_api", "w_key", "w_val", "w_file", "w_line",
                "w_phase", "r_node", "r_file", "r_line", "r_phase")
        d = dict(zip(keys, row))
        conf = persistence_confidence(
            {"key_static": d["w_key"], "value_node": d["w_val"],
             "phase": d["w_phase"]},
            {"key_static": d["w_key"], "phase": d["r_phase"]},
        )
        yield {
            "kind":        "storage",
            "api":         d["w_api"],
            "key":         d["w_key"],
            "from_node":   d["w_val"] or d["w_node"],
            "to_node":     d["r_node"],
            "write_file":  d["w_file"], "write_line": d["w_line"],
            "read_file":   d["r_file"], "read_line":  d["r_line"],
            "confidence":  conf,
            "phase_pair":  (d["w_phase"], d["r_phase"]),
        }
