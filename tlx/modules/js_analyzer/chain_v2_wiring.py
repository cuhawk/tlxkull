"""V2 factor wiring for chain extractors.

Loads every V2 sidecar table from a per-target snapshot DB and exposes
two surfaces:

  factors = load_v2_factors(conn)        # one-shot load
  m       = score_sink(sink_id, factors) # multiplier in [0.0, 1.5]

Plus three side-emission helpers run after primary chain extraction:

  inject_storage_edges(adj, factors)     # mutate adjacency in-place
  emit_clobber_chains(target, factors, chains)
  emit_pp_chains(target, factors, chains)

All paths degrade to neutral (multiplier 1.0, zero synthetic edges) when
the underlying V2 table is empty or missing. Caller never needs to gate
on ENABLE_* flags — population gates that.

Plan refs: V2 §11 §12 §13 §14 §15 §22 §23.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# ---------------------------------------------------------------------------
# Factor container
# ---------------------------------------------------------------------------


@dataclass
class V2Factors:
    # §11
    storage_events: list[dict] = field(default_factory=list)
    storage_edges: list[tuple[int, int, dict]] = field(default_factory=list)  # (writer_node, reader_node, meta)
    # §12
    provenance: dict[int, dict] = field(default_factory=dict)
    # §13
    global_reads: list[dict] = field(default_factory=list)
    clobber_candidates: list[dict] = field(default_factory=list)
    # §14
    implicit_lookups: list[dict] = field(default_factory=list)
    pp_gadgets: list[dict] = field(default_factory=list)
    # §15
    sink_contexts: dict[int, dict] = field(default_factory=dict)
    # §22
    sink_lifecycle: dict[int, dict] = field(default_factory=dict)
    # §23
    auth_state_nodes: dict[int, dict] = field(default_factory=dict)
    # V1 §9 TT policy body verdicts; key = handler; value = block_p
    tt_policy_block_p: float = 1.0     # highest-block among policies in file scope
    tt_policy_evidence: list[dict] = field(default_factory=list)

    def empty(self) -> bool:
        return not (
            self.storage_events or self.provenance or self.global_reads
            or self.clobber_candidates or self.implicit_lookups
            or self.pp_gadgets or self.sink_contexts
            or self.sink_lifecycle or self.auth_state_nodes
            or self.tt_policy_evidence
        )


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return row is not None


def _rows(conn: sqlite3.Connection, sql: str) -> list[dict]:
    try:
        cur = conn.execute(sql)
    except sqlite3.OperationalError:
        return []
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def load_v2_factors(conn: sqlite3.Connection) -> V2Factors:
    f = V2Factors()
    if _table_exists(conn, "storage_events"):
        f.storage_events = _rows(
            conn,
            "SELECT id, node_id, api, op, key_static, key_dynamic, "
            "key_provenance, value_node, is_secret_hint, phase, file, "
            "line, framework_hint FROM storage_events",
        )
        f.storage_edges = _synthesize_storage_edges(f.storage_events)
    if _table_exists(conn, "node_provenance"):
        for r in _rows(
            conn,
            "SELECT node_id, origin_label, channel, validation_kind, "
            "bypass_classes, confidence FROM node_provenance",
        ):
            f.provenance[int(r["node_id"])] = r
    if _table_exists(conn, "global_reads"):
        f.global_reads = _rows(
            conn,
            "SELECT id, node_id, global_name, access_path, unguarded, "
            "consumer_kind, consumer_node, file, line FROM global_reads",
        )
    if _table_exists(conn, "clobber_candidates"):
        f.clobber_candidates = _rows(
            conn,
            "SELECT id, html_sink_node, html_sink_attrs_allowed, "
            "global_read_id, gadget_shape, reachability_score "
            "FROM clobber_candidates",
        )
    if _table_exists(conn, "implicit_lookups"):
        f.implicit_lookups = _rows(
            conn,
            "SELECT id, node_id, object_origin, key_kind, key_value, "
            "has_default, has_typeof_guard, consumer_kind, consumer_node, "
            "file, line FROM implicit_lookups",
        )
    if _table_exists(conn, "pp_gadgets"):
        f.pp_gadgets = _rows(
            conn,
            "SELECT framework, version_range, key_path, gadget_kind, "
            "rationale, confidence FROM pp_gadgets",
        )
    if _table_exists(conn, "sink_contexts"):
        for r in _rows(
            conn,
            "SELECT node_id, context_class, encoding_state, "
            "execution_viable, rationale FROM sink_contexts",
        ):
            f.sink_contexts[int(r["node_id"])] = r
    if _table_exists(conn, "sink_lifecycle"):
        for r in _rows(
            conn,
            "SELECT node_id, framework, lifecycle_phase, "
            "attacker_can_trigger FROM sink_lifecycle",
        ):
            f.sink_lifecycle[int(r["node_id"])] = r
    if _table_exists(conn, "auth_state_nodes"):
        for r in _rows(
            conn,
            "SELECT node_id, role, source, framework, trust, "
            "derives_from, consumer_node FROM auth_state_nodes",
        ):
            f.auth_state_nodes[int(r["node_id"])] = r
    if _table_exists(conn, "tt_policies"):
        rows = _rows(
            conn,
            "SELECT node_id, policy_name, handler, body_class, block_p, "
            "rationale, file, line FROM tt_policies",
        )
        f.tt_policy_evidence = rows
        if rows:
            # Use the strongest policy (max block_p) since a single
            # strong policy enforced via require-trusted-types-for
            # is enough to block sinks. Conservative: 0.5 floor when
            # require-trusted-types-for is not enforced (caller can
            # override by checking browser_context.trusted_types.enforced).
            f.tt_policy_block_p = max(float(r["block_p"]) for r in rows)
    return f


# ---------------------------------------------------------------------------
# §11 storage edges synthesis (writer→reader pairing)
# ---------------------------------------------------------------------------


def _synthesize_storage_edges(events: list[dict]) -> list[tuple[int, int, dict]]:
    by_key: dict[tuple[str, str], dict[str, list[dict]]] = defaultdict(
        lambda: {"write": [], "read": []}
    )
    for e in events:
        if not e.get("key_static"):
            continue
        if e["op"] not in ("read", "write"):
            continue
        by_key[(e["api"], e["key_static"])][e["op"]].append(e)

    out: list[tuple[int, int, dict]] = []
    for (api, key), bucket in by_key.items():
        if not (bucket["write"] and bucket["read"]):
            continue
        for w in bucket["write"]:
            for r in bucket["read"]:
                if w["node_id"] == r["node_id"]:
                    continue
                # §11.7 base confidence model
                base = 0.6  # literal key match
                if w.get("value_node"):
                    base += 0.2
                if w.get("phase") and r.get("phase") and w["phase"] != r["phase"]:
                    base += 0.1  # cross-phase narrative bonus
                if w.get("is_secret_hint"):
                    base -= 0.1
                base = max(0.05, min(0.95, base))
                out.append(
                    (
                        int(w["node_id"]),
                        int(r["node_id"]),
                        {
                            "api": api,
                            "key": key,
                            "write_line": w.get("line"),
                            "read_line": r.get("line"),
                            "confidence": round(base, 3),
                            "write_phase": w.get("phase"),
                            "read_phase": r.get("phase"),
                            "framework_hint": w.get("framework_hint")
                                or r.get("framework_hint"),
                        },
                    )
                )
    return out


def inject_storage_edges(
    adj: dict[int, list[tuple[int, str, int, str]]],
    factors: V2Factors,
    *,
    max_per_writer: int = 4,
) -> int:
    """Insert synthetic edges from storage writers to readers.

    Returns the number of edges added. Hop weight is encoded by
    edge_class='storage_hop'; the extractor multiplies P by ~0.5 per hop.
    """
    if not factors.storage_edges:
        return 0
    added = 0
    per_writer: dict[int, int] = defaultdict(int)
    for w, r, meta in factors.storage_edges:
        if per_writer[w] >= max_per_writer:
            continue
        adj[w].append((r, "storage", 1, "storage_hop"))
        per_writer[w] += 1
        added += 1
    return added


# ---------------------------------------------------------------------------
# Sink-time multipliers
# ---------------------------------------------------------------------------


_VIABILITY_M = {"viable": 1.0, "conditional": 0.55, "blocked": 0.10}


def score_sink(
    sink_node_id: int,
    sink_taxid: str,
    head_id: int,
    factors: V2Factors,
) -> dict:
    """Return per-multiplier breakdown + total for a sink emission.

    head_id is the chain endpoint node — used to check auth-gating + PP
    gadget context. sink_node_id and head_id are normally equal, but
    kept distinct so chain expansions past the sink remain expressible.
    """
    breakdown = {
        "parser_context": 1.0,
        "lifecycle": 1.0,
        "auth_state": 1.0,
        "origin_trust": 1.0,
        "pp_gadget": 1.0,
        "tt_policy": 1.0,
    }
    # §15 parser-context viability
    ctx = factors.sink_contexts.get(sink_node_id)
    if ctx:
        breakdown["parser_context"] = _VIABILITY_M.get(
            (ctx.get("execution_viable") or "viable"), 1.0
        )
    # §22 lifecycle activation
    lc = factors.sink_lifecycle.get(sink_node_id)
    if lc:
        breakdown["lifecycle"] = 1.0 if lc.get("attacker_can_trigger") else 0.3
    # §23 auth-state mediation. If sink's qname is gated by an auth
    # state node, the sink severity is conditioned on bypassing the
    # gate. Lower trust = harder to bypass = downgrade.
    auth = factors.auth_state_nodes.get(sink_node_id)
    if auth:
        breakdown["auth_state"] = max(0.2, 1.0 - float(auth.get("trust") or 0))
    # §12 origin trust on path head (postMessage/storage etc.)
    prov = factors.provenance.get(head_id)
    if prov:
        kind = prov.get("validation_kind") or "none"
        m = {
            "strict": 0.2,
            "library": 0.3,
            "loose": 0.5,
            "none": 0.8,
            "send": 1.0,
        }.get(kind, 0.7)
        breakdown["origin_trust"] = m
    # V1 §9 Trusted Types policy — only applies to script-execution sinks.
    if factors.tt_policy_evidence and _tt_applies_to_sink(sink_taxid):
        breakdown["tt_policy"] = max(0.05, 1.0 - factors.tt_policy_block_p)
    # §14 PP gadget match — small bonus if sink is in a known gadget
    # key_path. Keyed by sink_taxid family.
    if factors.pp_gadgets:
        for g in factors.pp_gadgets:
            if g.get("gadget_kind") and _gadget_matches_sink(
                g["gadget_kind"], sink_taxid
            ):
                breakdown["pp_gadget"] = 1.0 + 0.2 * float(g.get("confidence") or 0)
                break
    total = 1.0
    for v in breakdown.values():
        total *= v
    return {"multiplier": round(total, 4), "breakdown": breakdown}


_TT_GUARDED_SINKS = (
    "innerHTML_assign", "outerHTML_assign", "insertAdjacentHTML_call",
    "document_write", "document_writeln", "srcdoc_assign",
    "iframe_srcdoc_assign", "eval_call", "function_constructor",
    "set_timeout_string", "set_interval_string", "script_text_assign",
    "react_dangerously_set_inner_html",
)


def _tt_applies_to_sink(sink_taxid: str) -> bool:
    return any(tok == sink_taxid or tok in sink_taxid for tok in _TT_GUARDED_SINKS)


def _gadget_matches_sink(gadget_kind: str, sink_taxid: str) -> bool:
    fam = {
        "exec": ("eval", "function_ctor", "script_text", "set_timeout_string"),
        "render": ("innerHTML", "outerHTML", "insertAdjacentHTML",
                   "document_write", "srcdoc", "react_dangerously"),
        "redirect": ("location_assign", "location_href", "open_redirect", "window_open"),
        "config-override": (),
    }.get(gadget_kind, ())
    return any(token in sink_taxid for token in fam)


# ---------------------------------------------------------------------------
# Side-emission: clobber + pp chains
# ---------------------------------------------------------------------------


def emit_clobber_chains(
    target_dir: Path,
    factors: V2Factors,
    chains: Iterable[dict],
    nodes: dict[int, tuple[str, str]] | None = None,
) -> int:
    """Write ``chains/clobber.jsonl`` joining clobber candidates with the
    primary chain set. Each clobber candidate becomes one row even if no
    primary chain reaches its sink — clobber gadgets are independently
    interesting (gadget-only attack surface).

    Returns row count.
    """
    if not factors.clobber_candidates:
        return 0
    chains_by_sink: dict[int, list[dict]] = defaultdict(list)
    for c in chains:
        sid = (c.get("sink") or {}).get("node_id")
        if sid is not None:
            chains_by_sink[int(sid)].append(c)

    rows: list[dict] = []
    gr_by_id = {g["id"]: g for g in factors.global_reads}
    for cc in factors.clobber_candidates:
        sink_node = int(cc["html_sink_node"])
        gr = gr_by_id.get(int(cc["global_read_id"]))
        rec = {
            "kind": "clobber",
            "sink_node": sink_node,
            "sink_qname": (nodes or {}).get(sink_node, ("", ""))[0]
                if nodes else None,
            "global_name": (gr or {}).get("global_name"),
            "access_path": (gr or {}).get("access_path"),
            "gadget_shape": cc.get("gadget_shape"),
            "reachability_score": cc.get("reachability_score"),
            "consumer_kind": (gr or {}).get("consumer_kind"),
            "primary_chains": [
                {"id": pc.get("id"), "score": pc.get("score")}
                for pc in chains_by_sink.get(sink_node, [])[:3]
            ],
        }
        rows.append(rec)
    out = target_dir / "chains" / "clobber.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""))
    return len(rows)


def emit_pp_chains(
    target_dir: Path,
    factors: V2Factors,
    chains: Iterable[dict],
    nodes: dict[int, tuple[str, str]] | None = None,
) -> int:
    """Write ``chains/pp.jsonl`` — pairs of (implicit lookup, matching
    gadget catalog entry).

    Match heuristic: lookup.key_value equals last segment of
    gadget.key_path (e.g. ``__proto__.exec`` matches lookup of ``exec``
    with object_origin tagged via ``ENABLE_PP_GADGETS`` ingest). Lookups
    with ``has_default=1`` or ``has_typeof_guard=1`` are downweighted.
    """
    if not (factors.implicit_lookups and factors.pp_gadgets):
        return 0
    by_leaf: dict[str, list[dict]] = defaultdict(list)
    for g in factors.pp_gadgets:
        leaf = (g.get("key_path") or "").split(".")[-1]
        if leaf:
            by_leaf[leaf].append(g)
    rows: list[dict] = []
    for lu in factors.implicit_lookups:
        key = lu.get("key_value") or ""
        # Strip quotes the AST extractor may keep.
        key = key.strip("'\"")
        candidates = by_leaf.get(key)
        if not candidates:
            continue
        guarded = bool(lu.get("has_default") or lu.get("has_typeof_guard"))
        for g in candidates:
            base = float(g.get("confidence") or 0.5)
            if guarded:
                base *= 0.5
            rows.append(
                {
                    "kind": "pp_gadget",
                    "lookup_node": int(lu["node_id"]),
                    "lookup_qname": (nodes or {}).get(int(lu["node_id"]), ("", ""))[0]
                        if nodes else None,
                    "lookup_file": lu.get("file"),
                    "lookup_line": lu.get("line"),
                    "consumer_kind": lu.get("consumer_kind"),
                    "gadget_framework": g.get("framework"),
                    "gadget_version_range": g.get("version_range"),
                    "gadget_key_path": g.get("key_path"),
                    "gadget_kind": g.get("gadget_kind"),
                    "gadget_rationale": g.get("rationale"),
                    "confidence": round(base, 3),
                }
            )
    rows.sort(key=lambda r: -r["confidence"])
    out = target_dir / "chains" / "pp.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""))
    return len(rows)
