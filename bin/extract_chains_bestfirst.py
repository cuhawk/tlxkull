#!/usr/bin/env python3
"""Best-first chain extractor with confidence-driven pruning.

Plan: plans/ARCHITECTURE_EVOLUTION.md §8.

Successor to ``bin/extract_chains_bounded.py``. Same inputs (per-target
DB snapshot, node_tags), same output shape (chains/all.jsonl,
chains/hot.jsonl, triage.json), but the BFS is replaced by a best-first
priority queue keyed by partial P(chain). Branches with partial
probability below ``--p-cutoff`` are pruned before expansion.

When ``targets/<name>/browser_context.json`` exists the per-chain
viability factor (CSP / Trusted Types / parser context / framework)
multiplies into P(chain). When ``node_sanitizers`` carries a
sanitizer-on-path verdict, that sanitizer's effective confidence is
folded in via ``(1 - block_p)``.

Lives alongside ``extract_chains_bounded.py``; does not replace it.
Default workflow keeps the bounded extractor in front, with best-first
gated by ``--use-bestfirst`` in the future skill driver. For now this
script is opt-in.

Usage:
  bin/extract_chains_bestfirst.py <target>
      [--db PATH]
      [--severity high]
      [--max-chains 4000]
      [--max-hot 50]
      [--p-cutoff 0.05]
      [--max-paths-per-source 64]
      [--continuation]  / [--no-continuation]
      [--quiet]
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    per_target_db,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


def _load_tags(conn, severity: str):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    conf_col = "t.confidence" if "confidence" in cols else "1.0 AS confidence"
    src_col = "t.source" if "source" in cols else "'regex' AS source"
    rows = conn.execute(
        f"SELECT n.id, n.qualified_name, n.file, n.start_line, "
        f"       t.taxonomy_id, t.kind, t.severity, {conf_col}, {src_col} "
        f"FROM node_tags t JOIN nodes n ON n.id = t.node_id"
    ).fetchall()
    sources, sinks = {}, {}
    sev_ranks = {"high": 3, "medium": 2, "low": 1}
    min_sev = sev_ranks.get(severity, 3)
    for nid, qname, file, line, tax, kind, sev, conf, src in rows:
        if kind == "sink" and sev_ranks.get(sev, 0) < min_sev:
            continue
        rec = {"id": nid, "qname": qname, "file": file, "line": line,
               "taxonomy_id": tax, "kind": kind, "severity": sev,
               "confidence": float(conf) if conf is not None else 1.0,
               "tag_source": src or "regex"}
        bag = sinks if kind == "sink" else sources if kind == "source" else None
        if bag is None:
            continue
        existing = bag.get(nid)
        if existing is None or rec["confidence"] > existing["confidence"]:
            bag[nid] = rec
    nodes = {nid: (qname, file or "") for nid, qname, file in
             conn.execute("SELECT id, qualified_name, file FROM nodes")}
    return sources, sinks, nodes


def _load_edges(conn, *, allow_continuation: bool, max_name_match: int = 10):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(edges)")}
    has_cand = "candidate_count" in cols
    has_eclass = "edge_class" in cols

    sql = "SELECT caller_id, callee_id, resolved_kind"
    cand_idx = -1
    eclass_idx = -1
    next_idx = 3
    if has_cand:
        sql += ", candidate_count"
        cand_idx = next_idx
        next_idx += 1
    if has_eclass:
        sql += ", edge_class"
        eclass_idx = next_idx
        next_idx += 1
    sql += " FROM edges WHERE callee_id IS NOT NULL"

    adj: dict[int, list[tuple[int, str, int, str]]] = defaultdict(list)
    for row in conn.execute(sql):
        caller, callee, rk = row[0], row[1], row[2]
        cand = row[cand_idx] if cand_idx >= 0 else 1
        eclass = row[eclass_idx] if eclass_idx >= 0 else "sync"
        if rk == "name_match" and (cand or 1) > max_name_match:
            continue
        if eclass == "continuation" and not allow_continuation:
            continue
        adj[caller].append((callee, rk or "", cand or 1, eclass or "sync"))
    return adj


def _sanitizer_map(conn):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_sanitizers)")}
    if "node_id" not in cols:
        return {}
    out: dict[int, list[dict]] = defaultdict(list)
    for nid, taxid, line, clears in conn.execute(
        "SELECT node_id, taxonomy_id, line, clears FROM node_sanitizers"
    ):
        out[int(nid)].append({"taxonomy_id": taxid, "line": line, "clears": clears or ""})
    return out


def _viability_for(sink_taxid: str, bctx):
    if bctx is None:
        return 1.0
    try:
        from modules.js_analyzer.sink_viability import compute
        return compute(sink_taxid, bctx)
    except Exception:
        return 1.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--severity", default="high")
    ap.add_argument("--max-chains", type=int, default=4000)
    ap.add_argument("--max-hot", type=int, default=50)
    ap.add_argument("--p-cutoff", type=float, default=0.05)
    ap.add_argument("--max-paths-per-source", type=int, default=64)
    ap.add_argument("--max-name-match-candidates", type=int, default=10)
    ap.add_argument(
        "--no-continuation", action="store_true",
        help="Disable async continuation edges (default: on if any present).",
    )
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    tlx_sys_path()
    from modules.js_analyzer.chain_confidence import (  # noqa: E402
        adaptive_depth,
        compute_partial,
        edge_confidence,
        source_controllability,
    )
    from modules.js_analyzer.chain_v2_wiring import (  # noqa: E402
        emit_clobber_chains,
        emit_pp_chains,
        inject_storage_edges,
        load_v2_factors,
        score_sink,
    )
    try:
        from modules.js_analyzer.browser_context import load as load_ctx  # noqa: E402
        bctx = load_ctx(target)
        if not (bctx.csp.raw or bctx.trusted_types.enforced or bctx.rendering.framework):
            bctx = None
    except Exception:
        bctx = None

    t0 = time.monotonic()
    conn = sqlite3.connect(str(db))
    sources, sinks, nodes = _load_tags(conn, args.severity)
    adj = _load_edges(
        conn,
        allow_continuation=not args.no_continuation,
        max_name_match=args.max_name_match_candidates,
    )
    san_map = _sanitizer_map(conn)
    v2_factors = load_v2_factors(conn)
    storage_edges_added = inject_storage_edges(adj, v2_factors)
    conn.close()

    if not args.quiet:
        print(
            f"sources={len(sources)} sinks={len(sinks)} "
            f"edges={sum(len(v) for v in adj.values())} "
            f"sanitizers_on_nodes={len(san_map)} bctx={'yes' if bctx else 'no'}",
            file=sys.stderr,
        )

    sink_ids = set(sinks.keys())
    chains: list[dict] = []
    chain_keys: set[tuple] = set()
    per_source_emitted: Counter = Counter()

    for src_id, src in sorted(
        sources.items(),
        key=lambda kv: (-kv[1]["confidence"], kv[0]),
    ):
        if len(chains) >= args.max_chains:
            break

        # Min-heap on -P_partial so highest-probability frontier pops first.
        p0 = source_controllability(src["taxonomy_id"], src["confidence"])
        # Entries: (-p, path, edge_records, san_confidences, cont_hops, dyn_hops)
        pq: list[tuple] = [(-p0, [src_id], [], [], 0, 0)]
        visited: set[tuple[int, int]] = set()

        while pq and per_source_emitted[src_id] < args.max_paths_per_source:
            neg_p, path, edge_records, san_conf_list, cont_hops, dyn_hops = heapq.heappop(pq)
            p_partial = -neg_p
            if p_partial < args.p_cutoff:
                continue
            head = path[-1]

            if head in sink_ids and len(path) > 1:
                snk = sinks[head]
                viab = _viability_for(snk["taxonomy_id"], bctx)
                cc = compute_partial(
                    source_taxonomy_id=src["taxonomy_id"],
                    source_tag_confidence=src["confidence"],
                    edge_kinds=edge_records,
                    sanitizer_confidences=san_conf_list,
                    viability_factor=viab,
                    continuation_hops=cont_hops,
                    dynamic_hops=dyn_hops,
                )
                v2_score = score_sink(snk["id"], snk["taxonomy_id"], head, v2_factors)
                p_final = cc.p_raw * snk["confidence"] * v2_score["multiplier"]
                # Count storage hops on path
                storage_hops = sum(1 for rk, _c in edge_records if rk == "storage")
                key = (src_id, snk["id"], tuple(path))
                if key not in chain_keys:
                    chain_keys.add(key)
                    chain = {
                        "id": len(chains) + 1,
                        "source": {
                            "node_id": src_id,
                            "qname": src["qname"], "file": src["file"], "line": src["line"],
                            "taxonomy_id": src["taxonomy_id"], "confidence": src["confidence"],
                            "tag_source": src["tag_source"],
                        },
                        "sink": {
                            "node_id": snk["id"],
                            "qname": snk["qname"], "file": snk["file"], "line": snk["line"],
                            "taxonomy_id": snk["taxonomy_id"], "confidence": snk["confidence"],
                            "tag_source": snk["tag_source"],
                        },
                        "path": [nodes[n][0] for n in path if n in nodes],
                        "path_files": [nodes[n][1] for n in path if n in nodes],
                        "depth": len(path) - 1,
                        "p_chain": round(p_final, 4),
                        "p_calibrated": cc.p_calibrated,
                        "confidence_breakdown": cc.to_dict(),
                        "viability_factor": round(viab, 4),
                        "v2_multiplier": v2_score["multiplier"],
                        "v2_breakdown": v2_score["breakdown"],
                        "continuation_hops": cont_hops,
                        "has_continuation": cont_hops > 0,
                        "storage_hops": storage_hops,
                        "score": round(p_final * 100, 2),
                    }
                    chains.append(chain)
                    per_source_emitted[src_id] += 1
                continue

            depth_budget = adaptive_depth(p_partial)
            if len(path) >= depth_budget:
                continue

            for callee_id, rk, cand, eclass in adj.get(head, ()):
                if callee_id in path:
                    continue
                vkey = (callee_id, len(path))
                if vkey in visited:
                    continue
                visited.add(vkey)
                e_conf = edge_confidence(rk, cand)
                if rk == "continuation":
                    new_cont = cont_hops + 1
                else:
                    new_cont = cont_hops
                new_dyn = dyn_hops + (1 if rk in ("dynamic", "dynamic_overapprox", "prop_shape") else 0)
                # Cap storage hops per chain at 1 (V2 §11.6).
                cur_storage_hops = sum(1 for r, _ in edge_records if r == "storage")
                if rk == "storage" and cur_storage_hops >= 1:
                    continue
                # Sanitizer on the next node, if any.
                new_san = list(san_conf_list)
                for s in san_map.get(callee_id, []):
                    # Without §5 reality wiring (target-dir context),
                    # treat the static taxonomy clears as soft 0.6
                    # confidence — registry-aware tuning is owned by
                    # reporter.score_chain when ENABLE_SANITIZER_REALITY
                    # is on. Best-first runs cheap.
                    new_san.append(0.6)
                new_p = p_partial * e_conf
                # Apply continuation / dynamic / storage discount per hop.
                if rk == "continuation":
                    new_p *= 0.95
                if rk in ("dynamic", "dynamic_overapprox", "prop_shape"):
                    new_p *= 0.90
                if rk == "storage":
                    # Synthetic persistence edge weight 0.5 per V2 §11.6.
                    new_p *= 0.50
                # Apply sanitizer probability if newly added.
                for sc in new_san[len(san_conf_list):]:
                    new_p *= (1.0 - sc)
                if new_p < args.p_cutoff:
                    continue
                heapq.heappush(
                    pq,
                    (-new_p, path + [callee_id],
                     edge_records + [(rk, cand)],
                     new_san,
                     new_cont, new_dyn),
                )

    chains.sort(key=lambda c: c["score"], reverse=True)
    out_dir = target / "chains"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "all_bestfirst.jsonl").write_text(
        "\n".join(json.dumps(c) for c in chains) + ("\n" if chains else "")
    )
    n_hot = min(args.max_hot, max(1, math.ceil(len(chains) * 0.1)))
    (out_dir / "hot_bestfirst.jsonl").write_text(
        "\n".join(json.dumps(c) for c in chains[:n_hot]) + ("\n" if chains else "")
    )
    # V2 side-emit (chains/clobber.jsonl, chains/pp.jsonl).
    clobber_rows = emit_clobber_chains(target, v2_factors, chains, nodes)
    pp_rows = emit_pp_chains(target, v2_factors, chains, nodes)

    sink_dist = Counter(c["sink"]["taxonomy_id"] for c in chains)
    src_dist = Counter(c["source"]["taxonomy_id"] for c in chains)
    summary = {
        "target": target.name,
        "db": str(db),
        "total": len(chains),
        "hot": n_hot,
        "p_cutoff": args.p_cutoff,
        "max_chains": args.max_chains,
        "max_paths_per_source": args.max_paths_per_source,
        "viability_used": bctx is not None,
        "continuation_used": not args.no_continuation,
        "sink_dist": dict(sink_dist.most_common()),
        "source_dist": dict(src_dist.most_common()),
        "elapsed_s": round(time.monotonic() - t0, 3),
        "v2": {
            "factors_present": not v2_factors.empty(),
            "storage_edges_added": storage_edges_added,
            "clobber_chains_emitted": clobber_rows,
            "pp_chains_emitted": pp_rows,
        },
        "outputs": {
            "all": str(out_dir / "all_bestfirst.jsonl"),
            "hot": str(out_dir / "hot_bestfirst.jsonl"),
            "clobber": str(out_dir / "clobber.jsonl") if clobber_rows else None,
            "pp": str(out_dir / "pp.jsonl") if pp_rows else None,
        },
    }
    print(json.dumps(summary, indent=2))

    write_status_phase(
        target,
        "extract_chains_bestfirst",
        {
            "status": "done",
            "ts": utcnow(),
            "total": len(chains),
            "hot": n_hot,
            "elapsed_s": summary["elapsed_s"],
            "p_cutoff": args.p_cutoff,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
