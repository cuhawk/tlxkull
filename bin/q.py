#!/usr/bin/env python3
"""Query DSL CLI — read-only fluent query over a per-target snapshot DB.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §17.

Simple JSON query spec on the command line. The four predicates the
underlying DSL exposes are:

  sources               — taxonomy_id, taxonomy_id__in, severity, severity__in
  sinks                 — same
  where_no_sanitizer    — boolean flag
  frameworks_any        — list of frameworks
  confidence_min        — float in [0, 1]
  top                   — int (LIMIT)

Two invocation forms:

  bin/q.py <target> --spec '{"sources":{"taxonomy_id":"location_hash"},
                              "sinks":{"taxonomy_id__in":["innerHTML_assign"]},
                              "where_no_sanitizer":true,
                              "top":50}'

  bin/q.py <target> --sources-taxid location_hash \\
                    --sinks-taxid innerHTML_assign --sinks-taxid eval_call \\
                    --no-sanitizer --top 50

Output: JSON to stdout. ``--md`` prints a compact markdown table.
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
)


def _apply_filters(query, spec: dict) -> None:
    src = spec.get("sources") or {}
    if src:
        query.sources(**src)
    snk = spec.get("sinks") or {}
    if snk:
        query.sinks(**snk)
    if spec.get("where_no_sanitizer"):
        query.where_no_sanitizer()
    if "frameworks_any" in spec and spec["frameworks_any"]:
        query.frameworks_any(*spec["frameworks_any"])
    if "confidence_min" in spec:
        query.confidence_min(float(spec["confidence_min"]))
    if "top" in spec:
        query.top(int(spec["top"]))


def _render_md(result: dict) -> str:
    lines = []
    for section in ("sources", "sinks"):
        rows = result.get(section) or []
        if not rows:
            continue
        lines.append(f"## {section} ({len(rows)})")
        lines.append("")
        lines.append("| qname | file:line | taxonomy_id | sev | conf |")
        lines.append("|---|---|---|---|---|")
        for r in rows[:200]:
            lines.append(
                f"| `{r.get('qname','')}` "
                f"| `{r.get('file','')}:{r.get('line','')}` "
                f"| {r.get('taxonomy_id','')} "
                f"| {r.get('severity','')} "
                f"| {r.get('confidence',0):.3f} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--spec", default=None,
                    help="JSON query spec; overrides every other --* flag")
    ap.add_argument("--sources-taxid", action="append", default=[])
    ap.add_argument("--sinks-taxid", action="append", default=[])
    ap.add_argument("--no-sanitizer", action="store_true")
    ap.add_argument("--frameworks", action="append", default=[])
    ap.add_argument("--confidence-min", type=float, default=0.0)
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--md", action="store_true",
                    help="render markdown tables instead of JSON")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    if args.spec:
        try:
            spec = json.loads(args.spec)
        except json.JSONDecodeError as e:
            print(f"invalid --spec JSON: {e}", file=sys.stderr)
            return 2
    else:
        src: dict = {}
        if len(args.sources_taxid) == 1:
            src["taxonomy_id"] = args.sources_taxid[0]
        elif args.sources_taxid:
            src["taxonomy_id__in"] = args.sources_taxid
        snk: dict = {}
        if len(args.sinks_taxid) == 1:
            snk["taxonomy_id"] = args.sinks_taxid[0]
        elif args.sinks_taxid:
            snk["taxonomy_id__in"] = args.sinks_taxid
        spec = {
            "sources": src,
            "sinks": snk,
            "where_no_sanitizer": args.no_sanitizer,
            "frameworks_any": args.frameworks,
            "confidence_min": args.confidence_min,
            "top": args.top,
        }

    tlx_sys_path()
    from modules.js_analyzer.v2.query_dsl import Q  # noqa: E402

    conn = sqlite3.connect(str(db))
    try:
        q = Q(conn)
        _apply_filters(q, spec)
        result = q.resolve().to_dict()
    finally:
        conn.close()

    if args.md:
        print(_render_md(result))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
