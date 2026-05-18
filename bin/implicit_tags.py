#!/usr/bin/env python3
"""Run implicit-tag closure expansion against a per-target snapshot DB.

Reads direct tags from ``targets/<name>/db/js_analyzer.db``, walks the
callgraph up to ``--max-hops`` (default 2) with confidence decay
``--decay ** hop`` (default 0.7), and:

1. Writes one JSONL record per derived tag to
   ``targets/<name>/tags_discovered.jsonl``.
2. Persists the same rows into the per-target ``node_tags`` table with
   ``source='implicit_closure'`` so downstream readers
   (``bin/extract_chains.py``, ``interprocedural_taint.solve_...``) pick
   them up without further changes.
3. Updates ``status.json.phases.implicit_tags`` with stats.

Idempotent: rerunning clears prior ``implicit_*`` rows + overwrites the
JSONL.

Usage:
  bin/implicit_tags.py <target_dir|target_name>
      [--db PATH] [--decay 0.7] [--max-hops 2]
      [--min-confidence 0.0] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from dataclasses import asdict
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


def _open_db(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(
            f"per-target DB missing: {db_path}. Run db-isolate snapshot first."
        )
    conn = sqlite3.connect(str(db_path))
    # Ensure the confidence + evidence columns exist on legacy snapshots
    # taken before the schema migration landed.
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    if "confidence" not in cols:
        conn.execute(
            "ALTER TABLE node_tags ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0"
        )
    if "evidence" not in cols:
        conn.execute("ALTER TABLE node_tags ADD COLUMN evidence TEXT")
    if "source" not in cols:
        conn.execute(
            "ALTER TABLE node_tags ADD COLUMN source TEXT NOT NULL DEFAULT 'regex'"
        )
    conn.commit()
    return conn


def _write_jsonl(out_path: Path, tags) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for t in tags:
            f.write(json.dumps(asdict(t), separators=(",", ":")) + "\n")
            n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None, help="Per-target snapshot DB path")
    ap.add_argument("--decay", type=float, default=0.7)
    ap.add_argument("--max-hops", type=int, default=2)
    ap.add_argument("--min-confidence", type=float, default=0.0)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute + print stats; do not write JSONL or insert into DB.",
    )
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    tlx_sys_path()
    from modules.js_analyzer.implicit_tags import (  # noqa: E402
        IMPLICIT_CLOSURE_SOURCE,
        discover,
        persist,
    )

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    db_path = Path(args.db).resolve() if args.db else per_target_db(target)

    t0 = time.monotonic()
    try:
        conn = _open_db(db_path)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "implicit-tags", e)
        return 2

    try:
        tags = discover(
            conn,
            decay=args.decay,
            max_hops=args.max_hops,
            min_confidence=args.min_confidence,
        )
        by_kind = {"sink": 0, "source": 0}
        by_hop: dict[int, int] = {}
        for t in tags:
            by_kind[t.kind] = by_kind.get(t.kind, 0) + 1
            by_hop[t.hop] = by_hop.get(t.hop, 0) + 1

        persist_stats = {"cleared": 0, "inserted": 0, "duplicate": 0}
        jsonl_path = target / "tags_discovered.jsonl"
        wrote = 0
        if not args.dry_run:
            persist_stats = persist(conn, tags, clear_existing=True)
            wrote = _write_jsonl(jsonl_path, tags)

        elapsed_s = round(time.monotonic() - t0, 3)
        summary = {
            "target": target.name,
            "db": str(db_path),
            "decay": args.decay,
            "max_hops": args.max_hops,
            "min_confidence": args.min_confidence,
            "discovered": len(tags),
            "by_kind": by_kind,
            "by_hop": by_hop,
            "persist": persist_stats,
            "jsonl_path": str(jsonl_path),
            "jsonl_rows": wrote,
            "tag_source": IMPLICIT_CLOSURE_SOURCE,
            "dry_run": bool(args.dry_run),
            "elapsed_s": elapsed_s,
        }
        print(json.dumps(summary, indent=2))

        if not args.no_status and not args.dry_run:
            write_status_phase(
                target,
                "implicit_tags",
                {
                    "status": "done",
                    "ts": utcnow(),
                    "discovered": len(tags),
                    "by_kind": by_kind,
                    "by_hop": by_hop,
                    "inserted": persist_stats["inserted"],
                    "cleared": persist_stats["cleared"],
                    "elapsed_s": elapsed_s,
                    "decay": args.decay,
                    "max_hops": args.max_hops,
                },
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
