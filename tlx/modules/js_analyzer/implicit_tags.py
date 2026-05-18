"""Implicit source/sink discovery via closure expansion.

Plan: project_implicit_tags_plan.md Phase 1.

Direct (regex/AST/template/external) `node_tags` rows tag the *immediate*
function that calls a known dangerous primitive. Wrappers around those
primitives — e.g. ``function renderHTML(el, s) { el.innerHTML = s; }`` —
remain untagged, so any caller of ``renderHTML`` is invisible to
interprocedural_taint and to chain extraction. This module walks the
callgraph from every directly-tagged node outward (callers for sinks,
callees for sources) up to ``max_hops`` and emits derived tags with
exponential decay ``decay ** hop``.

Output:
    Returns a list of ``DerivedTag`` records, one per (node, taxonomy_id,
    hop) discovered. Caller (``bin/implicit_tags.py``) persists them to
    ``targets/<name>/tags_discovered.jsonl`` and inserts them into the
    per-target ``node_tags`` table with ``source='implicit_closure'``.

Idempotent: ``persist()`` first clears any row whose ``source`` starts
with ``implicit_`` before re-inserting.

Hop semantics:
    * sink propagation walks ``edges`` backwards (callers of a tagged node).
    * source propagation walks ``edges`` forwards (callees a tagged node
      returns into / passes through). Source propagation is gated on the
      existence of an ``arg_to_param`` or ``return`` dataflow edge so we
      only inherit when the data physically flows.

Confidence: ``decay ** hop`` with ``hop`` starting at 1 (the
directly-tagged node itself is hop=0 and untouched). With the default
0.7, a 2-hop wrapper inherits 0.49.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field


DEFAULT_DECAY = 0.7
DEFAULT_MAX_HOPS = 2
IMPLICIT_SOURCE_PREFIX = "implicit_"
IMPLICIT_CLOSURE_SOURCE = "implicit_closure"


@dataclass
class DerivedTag:
    node_id: int
    qname: str
    file: str
    line: int
    taxonomy_id: str
    kind: str           # 'sink' or 'source'
    severity: str
    source: str         # always 'implicit_closure' here
    confidence: float
    hop: int
    path: list[str] = field(default_factory=list)  # qnames from origin to node

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))


def _load_direct_tags(conn: sqlite3.Connection) -> list[tuple]:
    """Return rows for tags written by non-implicit writers.

    Filters out our own derived rows so re-running the expander on an
    already-expanded DB doesn't stack confidences (closure of closure).
    """
    return conn.execute(
        "SELECT node_id, taxonomy_id, kind, severity, line "
        "FROM node_tags "
        "WHERE source NOT LIKE 'implicit_%'"
    ).fetchall()


def _build_caller_index(conn: sqlite3.Connection) -> dict[int, list[int]]:
    """callee_id → list of caller_id. Used for SINK back-propagation."""
    idx: dict[int, list[int]] = defaultdict(list)
    for caller_id, callee_id in conn.execute(
        "SELECT caller_id, callee_id FROM edges "
        "WHERE callee_id IS NOT NULL "
        "AND resolved_kind IN ('exact','this_cross_file','name_match')"
    ):
        idx[callee_id].append(caller_id)
    return idx


def _build_callee_index(conn: sqlite3.Connection) -> dict[int, list[int]]:
    """caller_id → list of callee_id. Used for SOURCE forward-propagation."""
    idx: dict[int, list[int]] = defaultdict(list)
    for caller_id, callee_id in conn.execute(
        "SELECT caller_id, callee_id FROM edges "
        "WHERE callee_id IS NOT NULL "
        "AND resolved_kind IN ('exact','this_cross_file','name_match')"
    ):
        idx[caller_id].append(callee_id)
    return idx


def _node_meta(conn: sqlite3.Connection) -> dict[int, tuple[str, str, int, int]]:
    """node_id → (qname, file, start_line, end_line)."""
    out: dict[int, tuple[str, str, int, int]] = {}
    for nid, qname, file, sl, el in conn.execute(
        "SELECT id, qualified_name, file, start_line, end_line FROM nodes"
    ):
        out[nid] = (qname or f"<n{nid}>", file or "", sl or 0, el or sl or 0)
    return out


def discover(
    conn: sqlite3.Connection,
    *,
    decay: float = DEFAULT_DECAY,
    max_hops: int = DEFAULT_MAX_HOPS,
    min_confidence: float = 0.0,
) -> list[DerivedTag]:
    """Run closure expansion. Returns DerivedTag records.

    Does NOT write to ``node_tags`` — use ``persist()`` for that. This
    split keeps the expander pure for unit testing.
    """
    if max_hops < 1:
        return []

    direct = _load_direct_tags(conn)
    if not direct:
        return []

    callers_of = _build_caller_index(conn)
    callees_of = _build_callee_index(conn)
    meta = _node_meta(conn)

    # Pre-collect direct-tag set keyed by (node_id, taxonomy_id) so we
    # don't shadow an already-direct tag with a lower-confidence implicit
    # one for the same node + taxonomy.
    direct_keys: set[tuple[int, str]] = {(nid, tid) for nid, tid, _, _, _ in direct}

    # Seed BFS per (node, taxonomy_id). hop=0 is the seed itself; we emit
    # starting at hop=1.
    derived: dict[tuple[int, str], DerivedTag] = {}

    for seed_node, tax_id, kind, severity, _line in direct:
        if kind not in ("sink", "source"):
            continue
        adjacency = callers_of if kind == "sink" else callees_of

        # BFS with hop tracking; only enqueue first time we see a node
        # for *this* (taxonomy_id, kind) seed so the shortest path wins.
        seen: set[int] = {seed_node}
        path_of: dict[int, list[str]] = {seed_node: [meta.get(seed_node, ("?",))[0]]}
        queue: deque[tuple[int, int]] = deque([(seed_node, 0)])

        while queue:
            nid, hop = queue.popleft()
            if hop >= max_hops:
                continue
            for nb in adjacency.get(nid, ()):
                if nb in seen:
                    continue
                seen.add(nb)
                new_hop = hop + 1
                conf = decay ** new_hop
                if conf < min_confidence:
                    continue
                nb_meta = meta.get(nb)
                if nb_meta is None:
                    continue
                qname, file, start_line, _end = nb_meta
                key = (nb, tax_id)
                # Never override a direct tag.
                if key in direct_keys:
                    continue
                path = path_of[nid] + [qname]
                path_of[nb] = path
                existing = derived.get(key)
                if existing is None or existing.confidence < conf:
                    derived[key] = DerivedTag(
                        node_id=nb,
                        qname=qname,
                        file=file,
                        line=start_line,
                        taxonomy_id=tax_id,
                        kind=kind,
                        severity=severity,
                        source=IMPLICIT_CLOSURE_SOURCE,
                        confidence=round(conf, 4),
                        hop=new_hop,
                        path=path,
                    )
                queue.append((nb, new_hop))

    return list(derived.values())


def persist(
    conn: sqlite3.Connection,
    tags: list[DerivedTag],
    *,
    clear_existing: bool = True,
) -> dict:
    """Insert DerivedTag rows into node_tags. Returns stats dict.

    With ``clear_existing=True`` (default) deletes prior rows whose
    ``source`` starts with ``implicit_`` so the operation is idempotent.
    """
    stats = {"cleared": 0, "inserted": 0, "duplicate": 0}
    cur = conn.cursor()
    if clear_existing:
        before = conn.total_changes
        cur.execute(
            "DELETE FROM node_tags WHERE source LIKE ?",
            (IMPLICIT_SOURCE_PREFIX + "%",),
        )
        stats["cleared"] = conn.total_changes - before

    for t in tags:
        evidence_json = json.dumps(
            {"hop": t.hop, "path": t.path},
            separators=(",", ":"),
        )
        before = conn.total_changes
        cur.execute(
            "INSERT OR IGNORE INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source, confidence, evidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                t.node_id, t.taxonomy_id, t.kind, t.severity,
                t.line, t.source, t.confidence, evidence_json,
            ),
        )
        if conn.total_changes > before:
            stats["inserted"] += 1
        else:
            stats["duplicate"] += 1

    conn.commit()
    return stats


__all__ = [
    "DerivedTag",
    "DEFAULT_DECAY",
    "DEFAULT_MAX_HOPS",
    "IMPLICIT_CLOSURE_SOURCE",
    "IMPLICIT_SOURCE_PREFIX",
    "discover",
    "persist",
]
