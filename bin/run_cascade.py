#!/usr/bin/env python3
"""Run the two-tier audit cascade gate (T1.2) over chains/hot.jsonl
(or chains/dom_reachable.jsonl when present).

Reads each chain id, joins to the full chain extracted from the
per-target snapshot DB (so we get path snippets + framework tags), then
runs ``audit_pipeline.cascade_triage``. Writes:

    targets/<name>/chains/survivors.jsonl     # gate verdict='escalate'
    targets/<name>/chains/rejected.jsonl      # gate verdict='reject'
    targets/<name>/chains/cascade_stats.json
    targets/<name>/status.json.phases.cascade

The Sonnet triage cost is tracked separately under
``status.json.cascade_cost_usd`` (a fraction of overall opus_cost — kept
out of opus_cost so the budget cap remains an Opus budget).

Usage:
  bin/run_cascade.py <target_dir>
      [--db <per-target.db>]
      [--input <chains/...jsonl>]   # default: dom_reachable then hot
      [--severity high|medium|low]
      [--no-deadcode]               # skip deterministic dead-code check
      [--model <claude-sonnet-...>]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    per_target_db,
    pick_chain_input,
    resolve_target_dir,
    status_lock,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)

tlx_sys_path()


def load_chain_ids(path: Path) -> list:
    ids: list = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = row.get("id")
            if cid is not None:
                ids.append(cid)
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    ap.add_argument("--db", default=None)
    ap.add_argument("--input", default=None)
    ap.add_argument("--severity", default="high")
    ap.add_argument("--no-deadcode", action="store_true")
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    try:
        target = resolve_target_dir(args.target_dir)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    db_path = Path(args.db) if args.db else per_target_db(target)
    if not db_path.exists():
        print(f"per-target DB missing: {db_path}", file=sys.stderr)
        return 3

    input_path = pick_chain_input(target, args.input)
    if input_path is None:
        print("no input chains file found (looked for chains/dom_reachable.jsonl + chains/hot.jsonl)", file=sys.stderr)
        return 4

    wanted_ids = set(load_chain_ids(input_path))
    if not wanted_ids:
        print(f"input file has zero chain ids: {input_path}", file=sys.stderr)
        return 5

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.callgraph_tools import set_callgraph
    from modules.js_analyzer.reporter import extract_findings
    from modules.js_analyzer.audit_pipeline import cascade_triage

    cg = CallGraph(db_path)
    set_callgraph(cg, base_paths=[str(target / "sources")])
    findings = extract_findings(
        gemini_reply="",
        target_folder=str(target / "sources"),
        callgraph=cg,
        severity=args.severity,
    )
    if findings is None:
        print("no chains extracted from per-target DB", file=sys.stderr)
        return 6

    chains_full = [c for c in findings.get("chains", []) if c.get("id") in wanted_ids]
    if not chains_full:
        print(
            f"none of the {len(wanted_ids)} requested ids exist in fresh extract; "
            "did you re-run js-index after the chains file was written?",
            file=sys.stderr,
        )
        return 7

    # Use a separate sqlite connection for the dead-code query — CallGraph
    # holds its own open connection but we don't want to share cursors.
    deadcode_conn = sqlite3.connect(str(db_path)) if not args.no_deadcode else None
    try:
        result = cascade_triage(
            chains_full,
            findings=findings,
            callgraph_db=deadcode_conn,
            model=args.model,
            skip_dead_code=args.no_deadcode,
        )
    finally:
        if deadcode_conn is not None:
            deadcode_conn.close()
        cg.close()

    chains_dir = target / "chains"
    chains_dir.mkdir(parents=True, exist_ok=True)
    with (chains_dir / "survivors.jsonl").open("w") as f:
        for c in result.survivors:
            f.write(json.dumps(c, default=str) + "\n")
    with (chains_dir / "rejected.jsonl").open("w") as f:
        for c in result.rejected:
            f.write(json.dumps(c, default=str) + "\n")

    s = result.stats
    cascade_stats = {
        "ts": utcnow(),
        "input": str(input_path.relative_to(target)),
        "total": s.total,
        "rejected": s.rejected,
        "escalated": s.escalated,
        "rejected_dead_code": s.rejected_dead_code,
        "rejected_sonnet": s.rejected_sonnet,
        "gate_cost_usd": round(s.gate_cost_usd, 6),
        "gate_duration_ms": s.gate_duration_ms,
        "parse_failures": s.parse_failures,
        "model": args.model or "default",
    }
    (chains_dir / "cascade_stats.json").write_text(
        json.dumps(cascade_stats, indent=2)
    )
    write_status_phase(target, "cascade", {**cascade_stats, "status": "done"})
    with status_lock(target) as data:
        data["cascade_cost_usd"] = round(
            float(data.get("cascade_cost_usd", 0)) + s.gate_cost_usd, 6
        )

    print(json.dumps(cascade_stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
