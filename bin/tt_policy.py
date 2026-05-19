#!/usr/bin/env python3
"""Trusted Types policy body classifier driver.

Plan: plans/ARCHITECTURE_EVOLUTION.md §9.

Reads ``trusted_types_create_policy``-tagged nodes from a per-target
snapshot DB, classifies each handler body (createHTML / createScript /
createScriptURL), and persists verdicts to ``tt_policies``.

Usage:
  bin/tt_policy.py <target>
  bin/tt_policy.py <target> --db <path>
  bin/tt_policy.py <target> --dry-run
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
    ap.add_argument("--dry-run", action="store_true",
                    help="print verdicts without persisting")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    tlx_sys_path()
    from modules.js_analyzer.trusted_types_policy import (  # noqa: E402
        discover,
        persist,
    )
    from modules.js_analyzer.v2_schema import apply as v2_apply  # noqa: E402

    conn = sqlite3.connect(str(db))
    try:
        # Ensure tt_policies table exists.
        v2_apply(conn)
        conn.commit()
        verdicts = discover(conn)
        if not args.dry_run:
            saved = persist(conn, verdicts)
            conn.commit()
        else:
            saved = 0
    finally:
        conn.close()

    summary = {
        "target": target.name,
        "db": str(db),
        "verdicts_total": len(verdicts),
        "verdicts_saved": saved,
        "by_body_class": _count_by(verdicts, "body_class"),
        "by_handler": _count_by(verdicts, "handler"),
        "sample": [
            {
                "node_id": v.node_id,
                "policy_name": v.policy_name,
                "handler": v.handler,
                "body_class": v.body_class,
                "block_p": v.block_p,
                "file": v.file,
                "line": v.line,
            }
            for v in verdicts[:10]
        ],
    }
    print(json.dumps(summary, indent=2))
    if not args.dry_run:
        write_status_phase(
            target,
            "tt_policy",
            {"status": "done", "ts": utcnow(), "verdicts": len(verdicts)},
        )
    return 0


def _count_by(verdicts, key: str) -> dict:
    out: dict[str, int] = {}
    for v in verdicts:
        k = getattr(v, key)
        out[k] = out.get(k, 0) + 1
    return out


if __name__ == "__main__":
    raise SystemExit(main())
