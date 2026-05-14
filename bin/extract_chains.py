#!/usr/bin/env python3
"""Extract source→sink chains from a per-target js_analyzer.db snapshot.

Bypasses the MCP server's globally-bound CallGraph (which reads the shared
~/.tlx/js_analyzer.db and mixes data across targets). Instantiates a fresh
CallGraph against the per-target snapshot, runs the same reporter pipeline
js_get_chains uses (`extract_findings` → trace_to_sink + find_pp_chains),
and writes:

    targets/<name>/chains/all.jsonl       (every chain returned)
    targets/<name>/chains/hot.jsonl       (top hot = min(20, count*0.1))
    targets/<name>/chains/triage.json     (sink/source distribution + stats)

Usage:
  bin/extract_chains.py <target_dir>
      [--db <path-to-snapshot-js_analyzer.db>]
      [--severity high|medium|low]
      [--max-hot N]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TLX = ROOT / "tlx"
sys.path.insert(0, str(TLX))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target_dir")
    ap.add_argument("--db", default=None)
    ap.add_argument("--severity", default="high")
    ap.add_argument("--max-hot", type=int, default=20)
    a = ap.parse_args()

    target_dir = Path(a.target_dir).resolve()
    name = target_dir.name
    db_path = Path(a.db) if a.db else (target_dir / "db" / "js_analyzer.db")
    if not db_path.exists():
        print(f"snapshot DB missing: {db_path}", file=sys.stderr)
        return 2

    out_dir = target_dir / "chains"
    out_dir.mkdir(parents=True, exist_ok=True)

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.callgraph_tools import set_callgraph
    from modules.js_analyzer.reporter import extract_findings

    cg = CallGraph(db_path)
    set_callgraph(cg, base_paths=[str(target_dir / "sources")])

    findings = extract_findings(
        gemini_reply="",
        target_folder=str(target_dir / "sources"),
        callgraph=cg,
        severity=a.severity,
    )
    if findings is None:
        print("no chains extracted (no sources or no sinks at severity)", file=sys.stderr)
        return 3

    chains = findings.get("chains", [])
    # Sort by score desc (extract_findings already sorts but make sure).
    chains.sort(key=lambda c: c.get("score", 0), reverse=True)

    # Write all.jsonl
    all_path = out_dir / "all.jsonl"
    with all_path.open("w") as f:
        for c in chains:
            f.write(json.dumps(c) + "\n")

    # hot.jsonl: top min(max_hot, ceil(count * 0.1))
    n_hot = min(a.max_hot, max(1, math.ceil(len(chains) * 0.1)))
    hot_path = out_dir / "hot.jsonl"
    with hot_path.open("w") as f:
        for c in chains[:n_hot]:
            f.write(json.dumps(c) + "\n")

    sink_dist = Counter()
    src_dist = Counter()
    for c in chains:
        sink_dist[c.get("sink", {}).get("taxonomy_id", "?")] += 1
        src_dist[c.get("source", {}).get("taxonomy_id", "?")] += 1

    triage = {
        "target": name,
        "db": str(db_path),
        "severity": a.severity,
        "total": len(chains),
        "hot": n_hot,
        "sink_dist": dict(sink_dist.most_common()),
        "source_dist": dict(src_dist.most_common()),
        "index_stats": findings.get("index_stats", {}),
    }
    (out_dir / "triage.json").write_text(json.dumps(triage, indent=2))
    print(json.dumps(triage, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
