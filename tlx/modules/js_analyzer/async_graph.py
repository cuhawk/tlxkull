"""Async / event continuation graph construction.

Plan: plans/ARCHITECTURE_EVOLUTION.md §3.

The static callgraph captures synchronous calls: ``f()`` → callee. It
does NOT capture handler dispatch through async producers:

    el.addEventListener('click', onClick);   // onClick is callee but no edge exists
    p.then(handler);                          // same
    setTimeout(fn, 10);                       // same
    window.addEventListener('message', recv); // postMessage taint never reaches recv

This module scans ``edges.raw`` for producer call patterns, resolves
the handler argument to a node id (when possible), and writes a
**continuation edge** plus a ``continuations`` row that records the
producer kind and the shape of taint flowing into the handler.

The chain extractor + interprocedural taint solver consume these
continuation edges identically to normal edges, so async-derived flows
appear in ``chains/all.jsonl`` without any further wiring.

Idempotent: rerunning clears prior continuation rows / edges before
inserting new ones.

Operates against a per-target ``db/js_analyzer.db`` snapshot — never
the global DB. Caller is ``bin/build_async_edges.py``.

Pure SQL + regex. No LLM, no network.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path

__all__ = [
    "ProducerMatch",
    "ContinuationEdge",
    "detect_producers",
    "build_continuation_edges",
    "ensure_schema",
    "discover_and_persist",
    "EDGE_CLASS_CONTINUATION",
]


EDGE_CLASS_CONTINUATION = "continuation"
EDGE_CLASS_SYNC = "sync"


# ── Producer catalogue ───────────────────────────────────────────────────


@dataclass(frozen=True)
class _Producer:
    kind: str                       # canonical name used in continuations.producer_kind
    pattern: re.Pattern             # match against edges.raw
    arg_index: int                  # which positional arg is the handler
    event_taint_paths: tuple[str, ...] = ()
    taint_through: bool = True


# Producers ordered most-specific → least-specific so the first match
# wins. Patterns capture the handler argument as group ``handler`` when
# possible (we still fall back to a generic arg scanner below).
PRODUCERS: tuple[_Producer, ...] = (
    _Producer(
        kind="addEventListener_message",
        pattern=re.compile(
            r"""(?P<target>window|document|self|globalThis)?\s*\.?addEventListener\s*\(\s*['"`]message['"`]\s*,\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
            re.IGNORECASE,
        ),
        arg_index=1,
        event_taint_paths=("data", "origin", "source"),
    ),
    _Producer(
        kind="onmessage_assign",
        pattern=re.compile(
            r"""(?P<target>\w+)\.onmessage\s*=\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=("data", "origin", "source"),
    ),
    _Producer(
        kind="addEventListener_generic",
        pattern=re.compile(
            r"""addEventListener\s*\(\s*['"`](?P<event>[^'"`]+)['"`]\s*,\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
            re.IGNORECASE,
        ),
        arg_index=1,
        event_taint_paths=("target.value", "target.innerText", "detail", "data"),
    ),
    _Producer(
        kind="promise_then",
        pattern=re.compile(
            r"""\.then\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=("__resolved__",),
    ),
    _Producer(
        kind="promise_catch",
        pattern=re.compile(
            r"""\.catch\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=("__rejected__",),
    ),
    _Producer(
        kind="promise_finally",
        pattern=re.compile(
            r"""\.finally\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        # finally handler does NOT receive the resolved value
        event_taint_paths=(),
        taint_through=False,
    ),
    _Producer(
        kind="set_timer",
        pattern=re.compile(
            r"""\b(?:setTimeout|setInterval|setImmediate|requestAnimationFrame|requestIdleCallback)\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=(),       # timer args are user-supplied at registration
        taint_through=False,
    ),
    _Producer(
        kind="mutation_observer",
        pattern=re.compile(
            r"""new\s+MutationObserver\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=("0.target",),
    ),
    _Producer(
        kind="intersection_observer",
        pattern=re.compile(
            r"""new\s+IntersectionObserver\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=(),
        taint_through=False,
    ),
    _Producer(
        kind="rxjs_subscribe",
        pattern=re.compile(
            r"""\.subscribe\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=("__emit__",),
    ),
    _Producer(
        kind="websocket_onmessage",
        pattern=re.compile(
            r"""\b(?P<target>\w+)\.onmessage\s*=\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=("data",),
    ),
    _Producer(
        kind="fetch_then_chain",
        pattern=re.compile(
            r"""\bfetch\s*\([^)]*\)\s*\.then\s*\(\s*(?P<handler>[A-Za-z_$][\w$.]*|\([^)]*\)\s*=>|function\s*\(|async\s+function|async\s*\()""",
        ),
        arg_index=0,
        event_taint_paths=("__resolved__",),
    ),
)


# ── Data shapes ─────────────────────────────────────────────────────────


@dataclass
class ProducerMatch:
    caller_id: int
    raw: str
    line: int
    callee_raw: str
    producer_kind: str
    handler_text: str               # the captured handler expression
    handler_is_inline: bool
    event_taint_paths: tuple[str, ...]
    taint_through: bool


@dataclass
class ContinuationEdge:
    caller_id: int
    callee_id: int                  # resolved handler node id
    line: int
    raw: str
    callee_raw: str                 # synthetic: 'continuation:<handler_text>'
    producer_kind: str
    event_taint_paths: list[str] = field(default_factory=list)
    taint_through: bool = True
    handler_is_inline: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ── Detection ────────────────────────────────────────────────────────────


def detect_producers(conn: sqlite3.Connection) -> list[ProducerMatch]:
    """Walk every edges row and look for producer patterns in raw text."""
    matches: list[ProducerMatch] = []
    rows = conn.execute(
        "SELECT caller_id, raw, line, callee_raw FROM edges WHERE raw IS NOT NULL"
    ).fetchall()

    for caller_id, raw, line, callee_raw in rows:
        if not raw:
            continue
        rl = raw.lstrip()
        for prod in PRODUCERS:
            m = prod.pattern.search(rl)
            if not m:
                continue
            handler = m.group("handler") if "handler" in m.groupdict() else ""
            if not handler:
                continue
            inline = handler.startswith(("(", "function", "async"))
            matches.append(ProducerMatch(
                caller_id=int(caller_id),
                raw=raw,
                line=int(line or 0),
                callee_raw=callee_raw or "",
                producer_kind=prod.kind,
                handler_text=handler.strip(),
                handler_is_inline=inline,
                event_taint_paths=prod.event_taint_paths,
                taint_through=prod.taint_through,
            ))
            break  # one producer per raw — most-specific wins
    return matches


# ── Handler resolution ───────────────────────────────────────────────────


def _resolve_handler(
    conn: sqlite3.Connection,
    pm: ProducerMatch,
    *,
    nodes_by_file_line: dict,
    nodes_by_local_name: dict,
    caller_file: str,
) -> int | None:
    """Resolve handler text to a node id.

    Strategy:
      1. Inline handler (arrow/function expr): find any synthetic node
         in the same file whose start_line is within ±3 of the call
         line (Babel's ast_extractor.js emits these as
         ``::event_handler_N`` / arrow children).
      2. Bare identifier: find a node in same file matching that name;
         fall back to any module that exports a node with that name.
      3. Dotted (``mod.handleClick``): look for callee_raw match in the
         original edges table.
    """
    if pm.handler_is_inline:
        candidates = nodes_by_file_line.get(caller_file, [])
        best = None
        best_dist = 999
        for nid, name, start_line, parent_qname in candidates:
            if start_line <= 0:
                continue
            dist = abs(start_line - pm.line)
            if dist <= 5 and (name.startswith("event_handler_") or "anon" in name
                              or name.startswith("_anon") or parent_qname):
                if dist < best_dist:
                    best, best_dist = nid, dist
        return best

    name = pm.handler_text
    if "." in name:
        # Dotted: try the right-most segment as a fallback.
        name = name.split(".")[-1]

    by_file = nodes_by_local_name.get((caller_file, name))
    if by_file:
        return by_file
    # Same-name fallback (lower confidence — picks any function with
    # this name; the existing name_match resolver behaves identically).
    rows = conn.execute(
        "SELECT id FROM nodes WHERE name = ? ORDER BY id LIMIT 1",
        (name,),
    ).fetchone()
    return rows[0] if rows else None


# ── Schema ──────────────────────────────────────────────────────────────


_CREATE_CONTINUATIONS = """
CREATE TABLE IF NOT EXISTS continuations (
    caller_id            INTEGER NOT NULL,
    callee_id            INTEGER NOT NULL,
    line                 INTEGER NOT NULL,
    callee_raw           TEXT    NOT NULL,
    producer_kind        TEXT    NOT NULL,
    event_taint_paths    TEXT    NOT NULL,    -- JSON list
    taint_through        INTEGER NOT NULL,
    handler_is_inline    INTEGER NOT NULL,
    PRIMARY KEY (caller_id, line, callee_raw)
);
CREATE INDEX IF NOT EXISTS idx_cont_callee   ON continuations(callee_id);
CREATE INDEX IF NOT EXISTS idx_cont_producer ON continuations(producer_kind);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    """Add edge_class column to edges (if missing) and create the
    continuations table. Idempotent."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(edges)")}
    if "edge_class" not in cols:
        conn.execute(
            f"ALTER TABLE edges ADD COLUMN edge_class TEXT NOT NULL DEFAULT '{EDGE_CLASS_SYNC}'"
        )
        conn.commit()
    conn.executescript(_CREATE_CONTINUATIONS)
    conn.commit()


# ── Persistence ─────────────────────────────────────────────────────────


def build_continuation_edges(
    conn: sqlite3.Connection,
    matches: list[ProducerMatch],
) -> list[ContinuationEdge]:
    """Resolve handlers + produce ContinuationEdge records (no DB
    insert yet — caller decides when to persist)."""
    # Build lookup tables once.
    nodes_by_file_line: dict[str, list[tuple]] = {}
    nodes_by_local_name: dict[tuple[str, str], int] = {}
    file_by_id: dict[int, str] = {}
    parent_qname_by_id: dict[int, str] = {}
    for nid, qname, file, name, parent, start_line in conn.execute(
        "SELECT id, qualified_name, file, name, parent, start_line FROM nodes"
    ):
        nodes_by_file_line.setdefault(file or "", []).append(
            (nid, name or "", start_line or 0, parent or "")
        )
        if file and name:
            nodes_by_local_name.setdefault((file, name), nid)
        file_by_id[nid] = file or ""
        parent_qname_by_id[nid] = parent or ""

    edges: list[ContinuationEdge] = []
    for pm in matches:
        caller_file = file_by_id.get(pm.caller_id, "")
        callee_id = _resolve_handler(
            conn, pm,
            nodes_by_file_line=nodes_by_file_line,
            nodes_by_local_name=nodes_by_local_name,
            caller_file=caller_file,
        )
        if callee_id is None:
            continue
        synthetic_raw = f"continuation:{pm.producer_kind}:{pm.handler_text[:64]}"
        edges.append(ContinuationEdge(
            caller_id=pm.caller_id,
            callee_id=callee_id,
            line=pm.line,
            raw=pm.raw,
            callee_raw=synthetic_raw,
            producer_kind=pm.producer_kind,
            event_taint_paths=list(pm.event_taint_paths),
            taint_through=pm.taint_through,
            handler_is_inline=pm.handler_is_inline,
        ))
    return edges


# Mapping from producer_kind → (source_taxonomy_id, severity, default_confidence)
# Only producers whose handlers receive *attacker-influenceable* data get a
# synthetic source tag. Timers, finally, IntersectionObserver get none.
CONTINUATION_SOURCE_MAP: dict[str, tuple[str, str, float]] = {
    "addEventListener_message": ("continuation_message_data", "high", 0.75),
    "onmessage_assign":          ("continuation_message_data", "high", 0.75),
    "websocket_onmessage":       ("continuation_websocket_data", "high", 0.70),
    "promise_then":              ("continuation_promise_resolved", "medium", 0.50),
    "promise_catch":             ("continuation_promise_rejected", "low", 0.40),
    "addEventListener_generic":  ("continuation_event_target_value", "medium", 0.55),
    "mutation_observer":         ("continuation_mutation_target", "medium", 0.50),
    "rxjs_subscribe":            ("continuation_observable_emit", "medium", 0.50),
    "fetch_then_chain":          ("continuation_fetch_body", "high", 0.60),
}


def inject_continuation_sources(conn: sqlite3.Connection) -> dict:
    """Tag handler nodes as receiving event-shaped taint.

    For each continuation edge whose producer carries attacker-controlled
    data, insert a ``node_tags`` row on the callee with
    ``source='continuation'`` and a taxonomy_id drawn from
    ``CONTINUATION_SOURCE_MAP``. Idempotent — clears prior
    ``source='continuation'`` rows first.

    Confidence intentionally < 1.0 so a chain rooted in a continuation
    source ranks below an equivalent chain rooted in a directly-tagged
    DOM source. Direct + continuation source on the same node keeps the
    higher-confidence row.
    """
    # Ensure schema (in case caller didn't).
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    if "confidence" not in cols:
        conn.execute(
            "ALTER TABLE node_tags ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0"
        )
    if "source" not in cols:
        conn.execute(
            "ALTER TABLE node_tags ADD COLUMN source TEXT NOT NULL DEFAULT 'regex'"
        )
    if "evidence" not in cols:
        conn.execute("ALTER TABLE node_tags ADD COLUMN evidence TEXT")
    conn.commit()

    before = conn.execute(
        "SELECT COUNT(*) FROM node_tags WHERE source='continuation'"
    ).fetchone()[0]
    conn.execute("DELETE FROM node_tags WHERE source='continuation'")
    conn.commit()

    rows = conn.execute(
        "SELECT callee_id, producer_kind, line FROM continuations"
    ).fetchall()

    import json as _json
    inserted = 0
    by_taxonomy: dict[str, int] = {}
    for callee_id, producer_kind, line in rows:
        mapping = CONTINUATION_SOURCE_MAP.get(producer_kind)
        if not mapping:
            continue
        tax_id, sev, conf = mapping
        evidence = _json.dumps({"producer_kind": producer_kind})
        cur = conn.execute(
            "INSERT OR IGNORE INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source, confidence, evidence) "
            "VALUES (?, ?, 'source', ?, ?, 'continuation', ?, ?)",
            (callee_id, tax_id, sev, line or 0, conf, evidence),
        )
        if cur.rowcount > 0:
            inserted += 1
            by_taxonomy[tax_id] = by_taxonomy.get(tax_id, 0) + 1
    conn.commit()
    return {
        "continuation_source_tags_cleared": before,
        "continuation_source_tags_inserted": inserted,
        "by_taxonomy": by_taxonomy,
    }


def discover_and_persist(conn: sqlite3.Connection) -> dict:
    """End-to-end: schema, detect, resolve, persist. Returns stats."""
    ensure_schema(conn)

    # Clear prior continuation evidence so re-runs are idempotent.
    before_edges = conn.execute(
        "SELECT COUNT(*) FROM edges WHERE edge_class = ?",
        (EDGE_CLASS_CONTINUATION,),
    ).fetchone()[0]
    conn.execute("DELETE FROM edges WHERE edge_class = ?", (EDGE_CLASS_CONTINUATION,))
    before_cont = conn.execute("SELECT COUNT(*) FROM continuations").fetchone()[0]
    conn.execute("DELETE FROM continuations")
    conn.commit()

    matches = detect_producers(conn)
    edges = build_continuation_edges(conn, matches)

    by_kind: dict[str, int] = {}
    inserted_edges = 0
    inserted_cont = 0
    for e in edges:
        by_kind[e.producer_kind] = by_kind.get(e.producer_kind, 0) + 1
        # Edge row uses the same schema as sync edges with edge_class set.
        cur = conn.execute(
            "INSERT OR IGNORE INTO edges "
            "(caller_id, callee_id, line, raw, callee_raw, resolved_kind, edge_class) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (e.caller_id, e.callee_id, e.line, e.raw, e.callee_raw,
             "continuation", EDGE_CLASS_CONTINUATION),
        )
        if cur.rowcount > 0:
            inserted_edges += 1
        # Continuation metadata.
        import json
        cur2 = conn.execute(
            "INSERT OR IGNORE INTO continuations "
            "(caller_id, callee_id, line, callee_raw, producer_kind, "
            " event_taint_paths, taint_through, handler_is_inline) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (e.caller_id, e.callee_id, e.line, e.callee_raw,
             e.producer_kind, json.dumps(e.event_taint_paths),
             1 if e.taint_through else 0,
             1 if e.handler_is_inline else 0),
        )
        if cur2.rowcount > 0:
            inserted_cont += 1
    conn.commit()

    return {
        "matches_detected": len(matches),
        "edges_inserted": inserted_edges,
        "continuations_inserted": inserted_cont,
        "edges_cleared": before_edges,
        "continuations_cleared": before_cont,
        "by_kind": by_kind,
    }
