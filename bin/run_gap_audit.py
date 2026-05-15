#!/usr/bin/env python3
"""Adjacent-function gap audit (T1.1).

Find sibling functions that don't call a given security control —
"forgotten security control" pattern from
``wiki/techniques/recon/adjacent-function-gap.md``.

Writes:
    targets/<name>/chains/gap_<control_slug>.jsonl   # gap-shaped chains
    targets/<name>/chains/gap_<control_slug>_stats.json
    targets/<name>/status.json.phases.gap_<control_slug>

Each chain is shaped to feed ``audit_pipeline.cascade_triage`` and the
existing Opus deep-audit pipeline downstream.

Usage:
  bin/run_gap_audit.py <target_dir> <control_qname>
      [--db <per-target.db>]
      [--max-gaps N]            # default 50; cascade then audits top 20
      [--cascade]               # also run the Sonnet gate over the gaps
      [--model <claude-...>]    # cascade model override

Example:
  bin/run_gap_audit.py acme-h1 'auth.RequireRole' --cascade
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
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)

tlx_sys_path()

from modules.js_analyzer.gap_analyzer import _slug  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    ap.add_argument("control_qname")
    ap.add_argument("--db", default=None)
    ap.add_argument("--max-gaps", type=int, default=50)
    ap.add_argument("--cascade", action="store_true")
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

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.gap_analyzer import find_gaps

    cg = CallGraph(db_path)
    try:
        gaps, stats = find_gaps(cg, args.control_qname, max_gaps=args.max_gaps)
    finally:
        cg.close()

    slug = _slug(args.control_qname)
    chains_dir = target / "chains"
    chains_dir.mkdir(parents=True, exist_ok=True)
    out_file = chains_dir / f"gap_{slug}.jsonl"
    with out_file.open("w") as f:
        for c in gaps:
            f.write(json.dumps(c) + "\n")

    cascade_summary: dict | None = None
    if args.cascade and gaps:
        from modules.js_analyzer.callgraph_tools import set_callgraph
        from modules.js_analyzer.audit_pipeline import cascade_triage

        cg2 = CallGraph(db_path)
        set_callgraph(cg2, base_paths=[str(target / "sources")])
        # Build a minimal findings dict so sonnet_triage can fetch snippets.
        snippets = _gather_snippets(cg2, target, gaps)
        findings = {
            "chains": gaps,
            "snippets": snippets,
            "framework_tags": [],
        }
        deadcode_conn = sqlite3.connect(str(db_path))
        try:
            res = cascade_triage(
                gaps,
                findings=findings,
                callgraph_db=deadcode_conn,
                model=args.model,
            )
        finally:
            deadcode_conn.close()
            cg2.close()

        with (chains_dir / f"gap_{slug}_survivors.jsonl").open("w") as f:
            for c in res.survivors:
                f.write(json.dumps(c, default=str) + "\n")
        with (chains_dir / f"gap_{slug}_rejected.jsonl").open("w") as f:
            for c in res.rejected:
                f.write(json.dumps(c, default=str) + "\n")
        cascade_summary = {
            "total": res.stats.total,
            "rejected": res.stats.rejected,
            "escalated": res.stats.escalated,
            "rejected_dead_code": res.stats.rejected_dead_code,
            "rejected_sonnet": res.stats.rejected_sonnet,
            "gate_cost_usd": round(res.stats.gate_cost_usd, 6),
            "gate_duration_ms": res.stats.gate_duration_ms,
            "parse_failures": res.stats.parse_failures,
        }

    result = {
        "status": "done",
        "ts": utcnow(),
        "control": args.control_qname,
        "callers_found": stats["callers_found"],
        "gaps_found": stats["gaps_found"],
        "max_gaps": args.max_gaps,
        "output_file": str(out_file.relative_to(target)),
        "cascade": cascade_summary,
    }
    (chains_dir / f"gap_{slug}_stats.json").write_text(
        json.dumps(result, indent=2, default=str)
    )
    write_status_phase(target, f"gap_{slug}", result)
    print(json.dumps(result, indent=2, default=str))
    return 0


def _gather_snippets(cg, target: Path, gaps: list[dict]) -> dict:
    """Read source bytes for each fn_gap qname so cascade_triage can show them."""
    sources_root = target / "sources"
    out: dict[str, str] = {}
    for c in gaps:
        qname = c.get("fn_gap")
        if not qname or qname in out:
            continue
        row = cg.conn.execute(
            "SELECT file, start_line, end_line FROM nodes WHERE qualified_name = ?",
            (qname,),
        ).fetchone()
        if not row:
            out[qname] = "<not in DB>"
            continue
        file_rel, sl, el = row
        path = sources_root / file_rel
        if not path.exists():
            path = (target / "raw" / file_rel)
        if not path.exists():
            out[qname] = f"<source file missing: {file_rel}>"
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as e:
            out[qname] = f"<read error: {e}>"
            continue
        sl = max(1, (sl or 1)) - 1
        el = min(len(lines), (el or sl + 1))
        snippet = "\n".join(lines[sl:el])[:8000]
        out[qname] = snippet
    return out


if __name__ == "__main__":
    raise SystemExit(main())
