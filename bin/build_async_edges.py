#!/usr/bin/env python3
"""Build async / event continuation edges in a per-target snapshot DB.

Scans edges.raw for producer call patterns (addEventListener, .then,
.catch, setTimeout, MutationObserver, RxJS subscribe, ...), resolves
the handler argument to a node id, and writes one continuation edge
plus one ``continuations`` metadata row per match.

Idempotent — prior continuation edges + rows are cleared first.

Plan: plans/ARCHITECTURE_EVOLUTION.md §3.

Usage:
  bin/build_async_edges.py <target>
      [--db PATH]
      [--dry-run]
      [--no-status]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    per_target_db,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="Detect producers + print stats without writing.")
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    tlx_sys_path()
    from modules.js_analyzer.async_graph import (  # noqa: E402
        build_continuation_edges,
        detect_producers,
        discover_and_persist,
        ensure_schema,
        inject_continuation_sources,
    )

    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db_path.exists():
        msg = f"per-target DB missing: {db_path}. Run db-isolate snapshot first."
        print(f"error: {msg}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "async-edges", msg)
        return 2

    t0 = time.monotonic()
    conn = sqlite3.connect(str(db_path))
    try:
        if args.dry_run:
            ensure_schema(conn)
            matches = detect_producers(conn)
            edges = build_continuation_edges(conn, matches)
            by_kind: dict[str, int] = {}
            for e in edges:
                by_kind[e.producer_kind] = by_kind.get(e.producer_kind, 0) + 1
            stats = {
                "target": target.name,
                "db": str(db_path),
                "matches_detected": len(matches),
                "edges_resolvable": len(edges),
                "by_kind": by_kind,
                "dry_run": True,
                "elapsed_s": round(time.monotonic() - t0, 3),
            }
        else:
            stats = discover_and_persist(conn)
            inject_stats = inject_continuation_sources(conn)
            stats.update(inject_stats)
            stats["target"] = target.name
            stats["db"] = str(db_path)
            stats["dry_run"] = False
            stats["elapsed_s"] = round(time.monotonic() - t0, 3)

        print(json.dumps(stats, indent=2))

        if not args.no_status and not args.dry_run:
            write_status_phase(
                target,
                "async_edges",
                {
                    "status": "done",
                    "ts": utcnow(),
                    "edges_inserted": stats.get("edges_inserted", 0),
                    "continuations_inserted": stats.get("continuations_inserted", 0),
                    "by_kind": stats.get("by_kind", {}),
                    "elapsed_s": stats["elapsed_s"],
                },
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
