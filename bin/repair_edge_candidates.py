#!/usr/bin/env python3
"""Backfill ``edges.candidate_count`` for legacy DBs.

Pre-patch, the callgraph indexer didn't store the candidate-count for
``resolved_kind='name_match'`` edges. Without it, downstream chain
extraction can't tell "1-of-2 ambiguous name match" from "1-of-500
single-letter minified collision". This script computes
``candidate_count`` for every ``name_match`` edge by counting how many
``nodes.name`` rows share the bare callee name.

Idempotent — sets candidate_count for every name_match edge regardless
of prior value.

Per CLAUDE.md API-key whitelist: no LLM calls. Pure SQL.
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
    utcnow,
    write_status_phase,
)


def _bare_name(callee: str) -> str:
    if not callee:
        return ""
    if callee.startswith("new "):
        callee = callee[4:]
    return callee.rsplit(".", 1)[-1]


def _ensure_column(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(edges)")}
    if "candidate_count" not in cols:
        conn.execute(
            "ALTER TABLE edges ADD COLUMN candidate_count INT NOT NULL DEFAULT 1"
        )
        conn.commit()


def _backfill(conn: sqlite3.Connection, dry_run: bool) -> dict:
    # Count bare-name occurrences once.
    name_counts: dict[str, int] = {}
    for name, n in conn.execute("SELECT name, COUNT(*) FROM nodes GROUP BY name"):
        name_counts[name or ""] = n

    rows = conn.execute(
        "SELECT rowid, callee_raw FROM edges WHERE resolved_kind='name_match'"
    ).fetchall()

    updates: list[tuple[int, int]] = []
    hist: dict[int, int] = {}
    for rowid, callee_raw in rows:
        bare = _bare_name(callee_raw or "")
        count = name_counts.get(bare, 1)
        if count < 1:
            count = 1
        updates.append((count, rowid))
        hist[count] = hist.get(count, 0) + 1

    if not dry_run and updates:
        cur = conn.cursor()
        cur.executemany(
            "UPDATE edges SET candidate_count=? WHERE rowid=?",
            updates,
        )
        conn.commit()

    return {
        "name_match_edges": len(rows),
        "updated": 0 if dry_run else len(updates),
        "candidate_count_hist_top": dict(
            sorted(hist.items(), key=lambda kv: -kv[0])[:10]
        ),
        "candidate_count_hist_bottom": dict(
            sorted(hist.items(), key=lambda kv: kv[0])[:5]
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db_path.exists():
        print(f"error: per-target DB missing: {db_path}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "repair-edge-candidates",
                                FileNotFoundError(str(db_path)))
        return 2

    t0 = time.monotonic()
    conn = sqlite3.connect(str(db_path))
    try:
        _ensure_column(conn)
        stats = _backfill(conn, dry_run=args.dry_run)
        elapsed_s = round(time.monotonic() - t0, 3)
        summary = {
            "target": target.name,
            "db": str(db_path),
            "dry_run": bool(args.dry_run),
            "elapsed_s": elapsed_s,
            **stats,
        }
        print(json.dumps(summary, indent=2))

        if not args.no_status and not args.dry_run:
            write_status_phase(
                target,
                "repair_edge_candidates",
                {
                    "status": "done",
                    "ts": utcnow(),
                    "name_match_edges": stats["name_match_edges"],
                    "updated": stats["updated"],
                    "elapsed_s": elapsed_s,
                },
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
