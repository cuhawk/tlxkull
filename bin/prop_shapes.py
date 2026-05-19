#!/usr/bin/env python3
"""Dynamic property resolution driver.

Plan: plans/ARCHITECTURE_EVOLUTION.md §2.

Three phases:

  ingest_object_keys  — harvest ObjectExpression / ClassDeclaration keys
                        into ``prop_shapes``.
  ingest_string_facts — harvest ``const X = "..."`` into ``string_facts``.
  refine_dynamic_edges — rewrite ``edges.resolved_kind`` for refinable
                        dynamic calls.

Usage:
  bin/prop_shapes.py <target>           # all three phases
  bin/prop_shapes.py <target> --ingest-only
  bin/prop_shapes.py <target> --refine-only
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--ingest-only", action="store_true")
    ap.add_argument("--refine-only", action="store_true")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    tlx_sys_path()
    from modules.js_analyzer.prop_shapes import (  # noqa: E402
        ingest_object_keys,
        ingest_string_facts,
        refine_dynamic_edges,
    )
    from modules.js_analyzer.v2_schema import apply as v2_apply  # noqa: E402

    conn = sqlite3.connect(str(db))
    try:
        v2_apply(conn)
        conn.commit()
        summary: dict = {"target": target.name, "db": str(db)}
        if not args.refine_only:
            sources_root = str(target / "sources")
            n_shapes = ingest_object_keys(conn, sources_root=sources_root)
            n_facts = ingest_string_facts(conn)
            conn.commit()
            summary["prop_shapes_rows"] = n_shapes
            summary["string_facts_rows"] = n_facts
        if not args.ingest_only:
            refined = refine_dynamic_edges(conn)
            summary.update(refined)
    finally:
        conn.close()
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "prop_shapes",
        {
            "status": "done",
            "ts": utcnow(),
            "refined_callsites": summary.get("refined_callsites", 0),
            "prop_shapes_rows": summary.get("prop_shapes_rows", 0),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
