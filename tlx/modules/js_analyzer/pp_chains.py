"""Prototype-pollution gadget chain pathfinder.

Two-stage attack model:
  Stage 1 (PP write): proto_assign_bracket / proto_assign_direct / proto_assign_merge
  Stage 2 (gadget):   property read flowing into innerHTML / eval / setTimeout / etc.

A chain links a Stage-1 source node to a Stage-2 sink node via the existing
call graph. Reuses existing sink taxonomy IDs (innerHTML_assign etc.) — we
do not re-tag the sink, only re-interpret it given a PP source.

Public API:
    find_pp_chains(conn, max_depth=8) -> list[dict]
"""

import sqlite3
from pathlib import Path
from typing import Any

import structlog

from modules.js_analyzer.pathfind import find_paths

logger = structlog.get_logger(__name__)


PP_SOURCE_IDS = (
    "proto_assign_bracket",
    "proto_assign_direct",
    "proto_assign_merge",
)

GADGET_SINK_IDS = (
    "innerHTML_assign",
    "outerHTML_assign",
    "eval_call",
    "eval_indirect",
    "new_Function",
    "setTimeout_string",
    "setInterval_string",
    "document_write",
    "document_writeln",
    "dangerouslySetInnerHTML",
)

MAX_PAIRS = 500
TOP_PP_NODES_ON_OVERLOAD = 20
MAX_CHAINS_RETURNED = 50


def _node_meta(conn: sqlite3.Connection, node_id: int) -> tuple[str, str, int] | None:
    row = conn.execute(
        "SELECT qualified_name, file, start_line FROM nodes WHERE id=?",
        (node_id,),
    ).fetchone()
    if not row:
        return None
    return row[0], row[1] or "", row[2] or 0


def find_pp_chains(conn: sqlite3.Connection, max_depth: int = 8) -> list[dict]:
    try:
        # ── Phase A: PP write sources ────────────────────────────────────
        pp_q = (
            "SELECT node_id, taxonomy_id, line FROM node_tags "
            "WHERE kind='source' AND taxonomy_id IN ("
            + ",".join("?" * len(PP_SOURCE_IDS))
            + ")"
        )
        pp_rows = conn.execute(pp_q, PP_SOURCE_IDS).fetchall()
        if not pp_rows:
            return []

        # ── Phase B: gadget sink nodes ───────────────────────────────────
        gadget_q = (
            "SELECT node_id, taxonomy_id, line FROM node_tags "
            "WHERE kind='sink' AND taxonomy_id IN ("
            + ",".join("?" * len(GADGET_SINK_IDS))
            + ")"
        )
        gadget_rows = conn.execute(gadget_q, GADGET_SINK_IDS).fetchall()
        if not gadget_rows:
            return []

        # ── Performance guard ────────────────────────────────────────────
        pp_list = list(pp_rows)
        gadget_list = list(gadget_rows)
        if len(pp_list) * len(gadget_list) > MAX_PAIRS:
            logger.info(
                "pp_chains_pair_budget_exceeded",
                pp_writes=len(pp_list),
                gadgets=len(gadget_list),
                budget=MAX_PAIRS,
                limit=TOP_PP_NODES_ON_OVERLOAD,
            )
            # Resolve files for stable alphabetical pick
            decorated: list[tuple[str, tuple[Any, ...]]] = []
            for r in pp_list:
                meta = _node_meta(conn, r[0])
                file_key = meta[1] if meta else ""
                decorated.append((file_key, r))
            decorated.sort(key=lambda x: x[0])
            pp_list = [r for _, r in decorated[:TOP_PP_NODES_ON_OVERLOAD]]

        # ── Phase C: pathfind for each pair ──────────────────────────────
        # key: (src_file, src_node_id, sink_node_id) -> chain dict
        best: dict[tuple[str, int, int], dict] = {}
        for pp_node_id, pp_tax, pp_line in pp_list:
            src_meta = _node_meta(conn, pp_node_id)
            if not src_meta:
                continue
            src_qname, src_file, src_start = src_meta

            for sink_node_id, sink_tax, sink_line in gadget_list:
                sink_meta = _node_meta(conn, sink_node_id)
                if not sink_meta:
                    continue
                sink_qname, sink_file, _sink_start = sink_meta

                paths = find_paths(
                    conn,
                    from_qname=src_qname,
                    to_kind="node",
                    to_qname=sink_qname,
                    max_depth=max_depth,
                    max_paths=1,
                )
                if not paths:
                    continue
                p = paths[0]
                cross_file = (src_file != sink_file)

                if pp_tax == "proto_assign_merge":
                    score = 0.7
                elif cross_file:
                    score = 0.8
                else:
                    score = 1.0

                key = (src_file, pp_node_id, sink_node_id)
                existing = best.get(key)
                if existing is None or p.depth < existing["depth"]:
                    best[key] = {
                        "source": {
                            "qname":       src_qname,
                            "file":        src_file,
                            "line":        pp_line or src_start,
                            "taxonomy_id": pp_tax,
                            "kind":        "pp_write",
                        },
                        "sink": {
                            "qname":       sink_qname,
                            "file":        sink_file,
                            "line":        sink_line,
                            "taxonomy_id": sink_tax,
                            "kind":        "gadget_sink",
                        },
                        "path":       list(p.qualified_names),
                        "depth":      p.depth,
                        "score":      score,
                        "cross_file": cross_file,
                    }

        # ── Phase D: rank & cap ──────────────────────────────────────────
        chains = list(best.values())
        chains.sort(key=lambda c: (-c["score"], c["depth"],
                                   c["source"]["qname"], c["sink"]["qname"]))
        chains = chains[:MAX_CHAINS_RETURNED]
        for i, c in enumerate(chains, start=1):
            c["id"] = i
        return chains

    except Exception as exc:
        logger.warning("pp_chains_error", error=str(exc))
        return []


# Silence unused-import warning when running on environments without
# Path used elsewhere; kept per import constraint.
_ = Path
