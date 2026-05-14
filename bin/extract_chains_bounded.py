#!/usr/bin/env python3
"""Bounded source→sink chain extractor for a per-target js_analyzer.db snapshot.

The full reporter.extract_findings is unbounded and pathological on dense
graphs (no per-source path cap, no global cap). For triage purposes we only
need top-scored candidates, so this script:

  1. Reads tags + nodes + edges directly from the per-target snapshot DB.
  2. Iterates source-tagged nodes, BFS to sinks with hard caps.
  3. Scores (sink_severity × source_severity – log(depth+1)).
  4. Writes targets/<name>/chains/{all,hot}.jsonl + triage.json.

Caps (tunable):
  --max-depth        hop limit (default 5)
  --max-paths-per-source   default 10
  --max-total        global cap (default 2000)
  --severity         high|medium|low (default high)
  --max-hot          hot.jsonl size (default 20)

PP gadget chains are detected lightly: any tagged `pp_write` source that
reaches a `pp_gadget_*` sink within max_depth is emitted with
vuln_class_hint set.
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path


SINK_SEV = {
    "innerHTML_assign": 90, "outerHTML_assign": 90, "dangerouslySetInnerHTML": 90,
    "document_write": 90, "eval_call": 95, "new_Function": 95,
    "setTimeout_string": 90, "setInterval_string": 90,
    "pp_gadget_setTimeout": 92, "pp_gadget_innerHTML": 92,
    "computed_proto_assign": 80, "object_setPrototypeOf": 80,
    "event_handler_attr_assign": 70, "xhr_open_call": 50,
    "angular_modern_bypassSecurityTrust": 85, "location_assign": 70,
}
SRC_SEV = {
    "location_search": 90, "location_hash": 90, "window_name": 85,
    "document_referrer": 80, "URLSearchParams_ctor": 85, "URLSearchParams_get": 85,
    "postMessage_event": 75, "onmessage_handler": 75, "message_event_listener": 75,
    "JSON_parse_call": 60, "xhr_responseText": 55,
    "localStorage_get": 50, "localStorage_bracket": 50, "sessionStorage_get": 50,
    "angular_localstorage_read": 50,
    "proto_assign_merge": 70, "proto_assign_bracket": 70, "proto_assign_assign": 70,
    "sveltekit_params": 65,
}

PP_GADGET_PREFIX = "pp_gadget_"


def _load_nodes_tags(conn: sqlite3.Connection, severity: str) -> tuple[dict, dict, dict, dict]:
    rows = conn.execute(
        "SELECT n.id, n.qualified_name, n.file, n.start_line, "
        "       t.taxonomy_id, t.kind, t.severity "
        "FROM node_tags t JOIN nodes n ON n.id = t.node_id"
    ).fetchall()
    sources: dict[int, dict] = {}
    sinks: dict[int, dict] = {}
    sev_ranks = {"high": 3, "medium": 2, "low": 1}
    min_sev = sev_ranks.get(severity, 3)
    for nid, qname, file, line, tax, kind, sev in rows:
        if sev_ranks.get(sev, 0) < min_sev and "sink" in kind:
            continue
        rec = {"id": nid, "qname": qname, "file": file, "line": line,
               "taxonomy_id": tax, "kind": kind, "severity": sev}
        if kind == "sink":
            sinks[nid] = rec
        elif kind == "source":
            sources[nid] = rec
    qname_by_id = {nid: q for nid, q, *_ in conn.execute("SELECT id, qualified_name, file FROM nodes")}
    file_by_id = {nid: f for nid, _, f in conn.execute("SELECT id, qualified_name, file FROM nodes")}
    return sources, sinks, qname_by_id, file_by_id


def _load_edges(conn: sqlite3.Connection) -> dict[int, list[int]]:
    adj: dict[int, list[int]] = defaultdict(list)
    for caller, callee in conn.execute(
        "SELECT caller_id, callee_id FROM edges WHERE callee_id IS NOT NULL"
    ):
        adj[caller].append(callee)
    return adj


def _bfs(src_id: int, adj: dict[int, list[int]], sink_ids: set[int],
         max_depth: int, max_paths: int) -> list[list[int]]:
    if src_id in sink_ids:
        return [[src_id]]
    paths: list[list[int]] = []
    q: deque[tuple[int, list[int]]] = deque([(src_id, [src_id])])
    seen = {src_id}
    while q and len(paths) < max_paths:
        node, path = q.popleft()
        if len(path) > max_depth + 1:
            continue
        for nxt in adj.get(node, ()):
            if nxt in path:
                continue
            new_path = path + [nxt]
            if nxt in sink_ids:
                paths.append(new_path)
                if len(paths) >= max_paths:
                    break
                continue
            if nxt in seen and len(new_path) > 3:
                continue
            seen.add(nxt)
            if len(new_path) <= max_depth:
                q.append((nxt, new_path))
    return paths


def _score(src_tax: str, sink_tax: str, depth: int) -> float:
    base = SRC_SEV.get(src_tax, 40) + SINK_SEV.get(sink_tax, 40)
    penalty = math.log(depth + 1) * 5
    return round(max(0.0, min(100.0, base / 2 - penalty + 30)), 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target_dir")
    ap.add_argument("--db", default=None)
    ap.add_argument("--severity", default="high")
    ap.add_argument("--max-depth", type=int, default=5)
    ap.add_argument("--max-paths-per-source", type=int, default=10)
    ap.add_argument("--max-total", type=int, default=2000)
    ap.add_argument("--max-hot", type=int, default=20)
    a = ap.parse_args()

    target_dir = Path(a.target_dir).resolve()
    name = target_dir.name
    db = Path(a.db) if a.db else (target_dir / "db" / "js_analyzer.db")
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr); return 2

    conn = sqlite3.connect(str(db))
    sources, sinks, qname_by_id, file_by_id = _load_nodes_tags(conn, a.severity)
    adj = _load_edges(conn)
    print(f"sources={len(sources)} sinks={len(sinks)} edges={sum(len(v) for v in adj.values())}", file=sys.stderr)

    sink_ids = set(sinks)
    chains: list[dict] = []
    chain_id = 0

    for src_id, src in sources.items():
        if len(chains) >= a.max_total:
            break
        paths = _bfs(src_id, adj, sink_ids, a.max_depth, a.max_paths_per_source)
        for p in paths:
            sink_id = p[-1]
            snk = sinks.get(sink_id)
            if not snk:
                continue
            chain_id += 1
            depth = len(p) - 1
            is_pp = snk["taxonomy_id"].startswith(PP_GADGET_PREFIX) or "pp_write" in str(src.get("kind",""))
            chains.append({
                "id": chain_id,
                "source": {"qname": src["qname"], "file": src["file"],
                           "line": src["line"], "taxonomy_id": src["taxonomy_id"],
                           "kind": src["kind"]},
                "sink": {"qname": snk["qname"], "file": snk["file"],
                         "line": snk["line"], "taxonomy_id": snk["taxonomy_id"],
                         "kind": snk["kind"]},
                "path": [qname_by_id.get(n, str(n)) for n in p],
                "depth": depth,
                "cross_file": len({file_by_id.get(n, "") for n in p}) > 1,
                "score": _score(src["taxonomy_id"], snk["taxonomy_id"], depth),
                **({"vuln_class_hint": "Prototype Pollution gadget chain"} if is_pp else {}),
            })
            if len(chains) >= a.max_total:
                break

    chains.sort(key=lambda c: c["score"], reverse=True)
    out = target_dir / "chains"
    out.mkdir(parents=True, exist_ok=True)
    (out / "all.jsonl").write_text("\n".join(json.dumps(c) for c in chains) + ("\n" if chains else ""))
    n_hot = min(a.max_hot, max(1, math.ceil(len(chains) * 0.1)))
    (out / "hot.jsonl").write_text("\n".join(json.dumps(c) for c in chains[:n_hot]) + ("\n" if chains else ""))

    sink_dist = Counter(c["sink"]["taxonomy_id"] for c in chains)
    src_dist = Counter(c["source"]["taxonomy_id"] for c in chains)
    triage = {"target": name, "db": str(db), "severity": a.severity,
              "caps": {"max_depth": a.max_depth, "max_paths_per_source": a.max_paths_per_source,
                       "max_total": a.max_total},
              "total": len(chains), "hot": n_hot,
              "sink_dist": dict(sink_dist.most_common()),
              "source_dist": dict(src_dist.most_common())}
    (out / "triage.json").write_text(json.dumps(triage, indent=2))
    print(json.dumps(triage, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
