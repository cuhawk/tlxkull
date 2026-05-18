#!/usr/bin/env python3
"""Repair node_tags rows whose ``line`` field falls outside the owning node's
``start_line..end_line`` body. These phantom-line tags are FPs by construction:
they were inserted with a line number that doesn't correspond to anything in the
function the tag is attached to. Discovered on coolblue-intigriti where 51% of
direct (regex/ast/template) tags were out-of-bounds.

Repair strategy (default): DELETE the out-of-bounds rows. The next js-index
run will re-tag with corrected bounds (assuming the indexer-side patch is in
place). Implicit-derived rows (source LIKE 'implicit_%') are also dropped
since they may have been derived from broken direct tags.

Idempotent — re-running on a clean DB is a no-op.

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


def _audit(conn: sqlite3.Connection) -> dict:
    rows = conn.execute(
        "SELECT t.source, COUNT(*) AS n FROM node_tags t "
        "JOIN nodes n ON n.id = t.node_id "
        "WHERE (t.line < n.start_line OR t.line > n.end_line) "
        "GROUP BY t.source"
    ).fetchall()
    by_source = {src: n for src, n in rows}
    total_oob = sum(by_source.values())
    total_tags = conn.execute("SELECT COUNT(*) FROM node_tags").fetchone()[0]
    return {
        "total_tags": total_tags,
        "out_of_bounds_total": total_oob,
        "out_of_bounds_by_source": by_source,
        "out_of_bounds_pct": round(
            100.0 * total_oob / max(1, total_tags), 1
        ),
    }


def _repair(conn: sqlite3.Connection, drop_implicit: bool) -> dict:
    stats = {"deleted_oob": 0, "deleted_implicit": 0}
    before = conn.total_changes
    conn.execute(
        "DELETE FROM node_tags WHERE rowid IN ("
        "  SELECT t.rowid FROM node_tags t JOIN nodes n ON n.id = t.node_id "
        "  WHERE (t.line < n.start_line OR t.line > n.end_line)"
        ")"
    )
    stats["deleted_oob"] = conn.total_changes - before
    if drop_implicit:
        before = conn.total_changes
        conn.execute(
            "DELETE FROM node_tags WHERE source LIKE 'implicit_%'"
        )
        stats["deleted_implicit"] = conn.total_changes - before
    conn.commit()
    return stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument(
        "--keep-implicit", action="store_true",
        help="Don't drop implicit_* rows. Default behaviour drops them "
             "since they may have been derived from broken direct tags."
    )
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
            append_status_error(target, "repair-tag-bounds",
                                FileNotFoundError(str(db_path)))
        return 2

    t0 = time.monotonic()
    conn = sqlite3.connect(str(db_path))
    try:
        pre_audit = _audit(conn)
        repair_stats = {"deleted_oob": 0, "deleted_implicit": 0}
        if not args.dry_run:
            repair_stats = _repair(conn, drop_implicit=not args.keep_implicit)
        post_audit = _audit(conn) if not args.dry_run else pre_audit

        elapsed_s = round(time.monotonic() - t0, 3)
        summary = {
            "target": target.name,
            "db": str(db_path),
            "pre_audit": pre_audit,
            "repair_stats": repair_stats,
            "post_audit": post_audit,
            "dry_run": bool(args.dry_run),
            "keep_implicit": bool(args.keep_implicit),
            "elapsed_s": elapsed_s,
        }
        print(json.dumps(summary, indent=2))

        if not args.no_status and not args.dry_run:
            write_status_phase(
                target,
                "repair_tag_bounds",
                {
                    "status": "done",
                    "ts": utcnow(),
                    "deleted_oob": repair_stats["deleted_oob"],
                    "deleted_implicit": repair_stats["deleted_implicit"],
                    "post_total_tags": post_audit["total_tags"],
                    "post_oob_total": post_audit["out_of_bounds_total"],
                    "elapsed_s": elapsed_s,
                },
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
