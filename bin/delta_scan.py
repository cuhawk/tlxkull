#!/usr/bin/env python3
"""Differential scan / delta analysis driver.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §18.

Compares two per-target snapshot DBs (prior vs current) and reports:
  * file / node / tag / edge deltas
  * the subset of chains whose path touches the delta (radius=R)

Default ``prior`` = ``<target>/db/_prior/js_analyzer.db``. The driver
rotates the current DB into ``_prior/`` after a successful run so the
next invocation has a fresh baseline (override with --no-rotate).

Usage:
  bin/delta_scan.py <target>                  # diff vs _prior baseline
  bin/delta_scan.py <target> --prior <path>   # explicit prior DB
  bin/delta_scan.py <target> --no-rotate      # don't roll baseline forward
  bin/delta_scan.py <target> --chains <path>  # filter this chain JSONL
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    per_target_db,
    pick_chain_input,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--prior", default=None,
                    help="prior snapshot DB (default: <target>/db/_prior/js_analyzer.db)")
    ap.add_argument("--current", default=None,
                    help="current snapshot DB (default: <target>/db/js_analyzer.db)")
    ap.add_argument("--chains", default=None,
                    help="chains JSONL to filter (default: pick_chain_input)")
    ap.add_argument("--radius", type=int, default=3,
                    help="reachability radius (currently 1-hop intersection)")
    ap.add_argument("--no-rotate", action="store_true",
                    help="don't rotate current → _prior after the run")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    current_db = Path(args.current).resolve() if args.current else per_target_db(target)
    prior_db = Path(args.prior).resolve() if args.prior else (
        target / "db" / "_prior" / "js_analyzer.db"
    )

    if not current_db.exists():
        print(f"missing current db: {current_db}", file=sys.stderr)
        return 2
    if not prior_db.exists():
        print(
            f"no prior baseline at {prior_db}; nothing to compare. "
            f"Run once more (with this same baseline) after the next "
            f"js-index to populate.",
            file=sys.stderr,
        )
        prior_db.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(current_db, prior_db)
        return 0

    tlx_sys_path()
    from modules.js_analyzer.v2.delta_scan import (  # noqa: E402
        classify_delta_chains,
        compute_delta,
        reachable_chains_from_delta,
    )

    delta = compute_delta(prior_db, current_db)
    out_dir = target / "chains"
    out_dir.mkdir(parents=True, exist_ok=True)

    delta_summary = {
        "schema": delta.schema_version,
        "files_added": len(delta.files_added),
        "files_removed": len(delta.files_removed),
        "files_modified": len(delta.files_modified),
        "nodes_added": len(delta.nodes_added),
        "nodes_removed": len(delta.nodes_removed),
        "tags_added": len(delta.tags_added),
        "tags_removed": len(delta.tags_removed),
        "edges_added": delta.edges_added,
        "edges_removed": delta.edges_removed,
        "elapsed_s": delta.elapsed_s,
    }

    chains_input = (
        Path(args.chains).resolve() if args.chains else pick_chain_input(target)
    )
    delta_chains: list[dict] = []
    delta_categorized: dict[str, list[dict]] = {}
    if chains_input and chains_input.exists():
        delta_chains = reachable_chains_from_delta(
            chains_input, delta, radius=args.radius, current_db=current_db,
        )
        delta_categorized = classify_delta_chains(delta_chains, delta)
        out_file = out_dir / "delta.jsonl"
        out_file.write_text(
            "\n".join(json.dumps(c) for c in delta_chains)
            + ("\n" if delta_chains else "")
        )
        for bucket, rows in delta_categorized.items():
            (out_dir / f"{bucket}.jsonl").write_text(
                "\n".join(json.dumps(r) for r in rows)
                + ("\n" if rows else "")
            )

    md_path = out_dir / "delta_summary.md"
    lines = [
        f"# Delta scan — {target.name}",
        f"_Generated: {utcnow()}_",
        "",
        f"- Files: +{len(delta.files_added)} / -{len(delta.files_removed)} / ~{len(delta.files_modified)}",
        f"- Nodes: +{len(delta.nodes_added)} / -{len(delta.nodes_removed)}",
        f"- Tags:  +{len(delta.tags_added)} / -{len(delta.tags_removed)}",
        f"- Edges: +{delta.edges_added} / -{delta.edges_removed}",
        "",
    ]
    if delta_chains:
        lines.append(f"## Chains touched by delta ({len(delta_chains)})")
        for c in delta_chains[:50]:
            src = (c.get("source") or {}).get("qname", "?")
            snk = (c.get("sink") or {}).get("qname", "?")
            lines.append(f"- `{src}` → `{snk}`  (score {c.get('score')})")
    md_path.write_text("\n".join(lines))

    summary = {
        "target": target.name,
        "prior_db": str(prior_db),
        "current_db": str(current_db),
        "chains_input": str(chains_input) if chains_input else None,
        "delta": delta_summary,
        "delta_chains": len(delta_chains),
        "delta_buckets": {k: len(v) for k, v in delta_categorized.items()},
        "outputs": {
            "delta_jsonl": str(out_dir / "delta.jsonl") if delta_chains else None,
            "delta_md": str(md_path),
            "buckets": {
                k: str(out_dir / f"{k}.jsonl")
                for k in delta_categorized.keys()
            },
        },
    }

    if not args.no_rotate:
        shutil.copy2(current_db, prior_db)
        summary["baseline_rotated"] = True

    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "delta_scan",
        {
            "status": "done",
            "ts": utcnow(),
            "delta_chains": len(delta_chains),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
