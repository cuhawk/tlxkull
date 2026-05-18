#!/usr/bin/env python3
"""Fast chain extractor for minified-only / huge-bundle targets.

The reporter-driven ``extract_chains.py`` enumerates trace_to_sink BFS per
source, which explodes on 50k+ sources × 8-depth pathfinding (typical of a
real production bundle). This script trades depth for tractability:

1. Self-loop intraprocedural chains: nodes that carry BOTH a source tag
   and a sink tag (any kind). Source = sink = same qname, depth=0.
2. Direct-caller chains (optional, depth=1): every node tagged source
   whose direct callees include a sink-tagged node. Skipped by default
   to keep wall-clock bounded.

Output schema mirrors ``bin/extract_chains.py``:
    chains/all.jsonl   — every chain
    chains/hot.jsonl   — top min(--max-hot, ceil(N*0.1))
    chains/triage.json — distribution + stats

Per CLAUDE.md per-target DB isolation: ``--db`` is explicit, no fallback.
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import resolve_target_dir, per_target_db  # noqa: E402


_SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0, "": 0}


def _allowed_severities(min_sev: str) -> tuple[str, ...]:
    cutoff = _SEVERITY_RANK.get(min_sev.lower(), 3)
    return tuple(s for s, r in _SEVERITY_RANK.items() if r >= cutoff and s)


def _score(src_sev: str, sink_sev: str,
           src_conf: float = 1.0, sink_conf: float = 1.0) -> float:
    raw = _SEVERITY_RANK.get(src_sev, 0) * _SEVERITY_RANK.get(sink_sev, 0) * 10
    return round(float(raw) * src_conf * sink_conf, 2)


def extract(conn: sqlite3.Connection, severity: str) -> list[dict]:
    sevs = _allowed_severities(severity)
    qmarks = ",".join("?" * len(sevs))

    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    src_conf = "src.confidence" if "confidence" in cols else "1.0"
    snk_conf = "snk.confidence" if "confidence" in cols else "1.0"
    src_src = "src.source" if "source" in cols else "'regex'"
    snk_src = "snk.source" if "source" in cols else "'regex'"

    # Pick every (node, source_tag, sink_tag) where both tags live on the
    # same node — that's an intraprocedural source→sink self-loop.
    rows = conn.execute(
        f"""
        SELECT
            n.id, n.qualified_name, n.file, n.start_line, n.end_line,
            src.taxonomy_id AS src_tax, src.severity AS src_sev, src.line AS src_line,
            snk.taxonomy_id AS snk_tax, snk.severity AS snk_sev, snk.line AS snk_line,
            {src_conf} AS src_conf, {snk_conf} AS snk_conf,
            {src_src} AS src_tag_source, {snk_src} AS snk_tag_source
        FROM nodes n
        JOIN node_tags src ON src.node_id = n.id AND src.kind = 'source'
        JOIN node_tags snk ON snk.node_id = n.id AND snk.kind = 'sink'
        WHERE src.severity IN ({qmarks}) AND snk.severity IN ({qmarks})
          AND n.kind IN ('function','arrow','method')
          AND (n.end_line - n.start_line) < 400
        """,
        sevs + sevs,
    ).fetchall()

    chains: list[dict] = []
    chain_id = 0
    for r in rows:
        (node_id, qname, file_, start_line, end_line,
         src_tax, src_sev, src_line,
         snk_tax, snk_sev, snk_line,
         src_conf_v, snk_conf_v,
         src_tag_src, snk_tag_src) = r
        src_conf_v = float(src_conf_v) if src_conf_v is not None else 1.0
        snk_conf_v = float(snk_conf_v) if snk_conf_v is not None else 1.0
        chain_id += 1
        chains.append({
            "id": chain_id,
            "source": {
                "qname": qname,
                "file": file_,
                "line": src_line or start_line,
                "taxonomy_id": src_tax,
                "kind": "source",
                "severity": src_sev,
                "confidence": src_conf_v,
                "tag_source": src_tag_src or "regex",
            },
            "sink": {
                "qname": qname,
                "file": file_,
                "line": snk_line or start_line,
                "taxonomy_id": snk_tax,
                "kind": "sink",
                "severity": snk_sev,
                "confidence": snk_conf_v,
                "tag_source": snk_tag_src or "regex",
            },
            "path": [qname],
            "depth": 0,
            "cross_file": False,
            "confidence": round(src_conf_v * snk_conf_v, 4),
            "score": _score(src_sev, snk_sev, src_conf_v, snk_conf_v),
            "vuln_class_hint": f"{src_tax} → {snk_tax}",
        })
    return chains


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--db", help="Per-target js_analyzer.db (default: per-target snapshot)")
    ap.add_argument("--severity", default="high",
                    help="Minimum sink/source severity threshold")
    ap.add_argument("--max-hot", type=int, default=20)
    ap.add_argument("--max-all", type=int, default=2000,
                    help="Hard cap on all.jsonl size to keep downstream bounded")
    args = ap.parse_args(argv)

    target = resolve_target_dir(args.target)
    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db_path.exists():
        print(f"snapshot DB missing: {db_path}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        chains = extract(conn, args.severity)
    finally:
        conn.close()

    chains.sort(key=lambda c: (-c["score"], c["sink"]["qname"]))
    if args.max_all and len(chains) > args.max_all:
        chains = chains[: args.max_all]

    out_dir = target / "chains"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_path = out_dir / "all.jsonl"
    with all_path.open("w") as f:
        for c in chains:
            f.write(json.dumps(c) + "\n")

    n_hot = min(args.max_hot, max(1, math.ceil(len(chains) * 0.1))) if chains else 0
    hot_path = out_dir / "hot.jsonl"
    with hot_path.open("w") as f:
        for c in chains[:n_hot]:
            f.write(json.dumps(c) + "\n")

    sink_dist = Counter(c["sink"]["taxonomy_id"] for c in chains)
    src_dist = Counter(c["source"]["taxonomy_id"] for c in chains)
    file_dist = Counter(c["sink"]["file"] for c in chains)

    triage = {
        "target": target.name,
        "db": str(db_path),
        "severity": args.severity,
        "mode": "intraprocedural_self_loop",
        "total": len(chains),
        "hot": n_hot,
        "sink_dist": dict(sink_dist.most_common(20)),
        "source_dist": dict(src_dist.most_common(20)),
        "file_dist": dict(file_dist.most_common(20)),
    }
    (out_dir / "triage.json").write_text(json.dumps(triage, indent=2))
    print(json.dumps(triage, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
