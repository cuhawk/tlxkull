#!/usr/bin/env python3
"""Route → sink reachability BFS driver.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §22.4b.

Walks the callgraph forward from every entry in ``route_map`` and
populates ``route_sink_reach``. Sinks unreachable from any route are
marked dead in ``sink_lifecycle`` (activation × 0.1 + attacker_can_
trigger cleared). High-fanout sinks receive a small activation bonus.

Run after the v2 ``sink_reachability`` stage.

Usage:
  bin/reachability_bfs.py <target>
  bin/reachability_bfs.py <target> --max-depth 16
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
    ap.add_argument("--max-depth", type=int, default=12)
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    tlx_sys_path()
    from modules.js_analyzer.reachability_bfs import compute_reachability  # noqa: E402

    conn = sqlite3.connect(str(db))
    try:
        rep = compute_reachability(conn, max_depth=args.max_depth)
    finally:
        conn.close()

    summary = {
        "target": target.name,
        "db": str(db),
        "routes_seen": rep.routes_seen,
        "sinks_total": rep.sinks_total,
        "sinks_reachable": rep.sinks_reachable,
        "sinks_dead": rep.sinks_dead,
        "avg_routes_per_sink": rep.avg_routes_per_sink,
        "elapsed_s": rep.elapsed_s,
    }
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "reachability_bfs",
        {
            "status": "done",
            "ts": utcnow(),
            "sinks_reachable": rep.sinks_reachable,
            "sinks_dead": rep.sinks_dead,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
