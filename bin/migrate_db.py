#!/usr/bin/env python3
"""DB schema migration runner.

Plan: plans/ARCHITECTURE_EVOLUTION.md §10.4 + V2 schema (v2_schema.py).

Forward-only. Backs up the target DB into ``targets/<name>/db/.bak/``
before applying.

Usage:
  bin/migrate_db.py <target>             # migrate per-target snapshot
  bin/migrate_db.py --global             # migrate ~/.tlx/js_analyzer.db (asks first)
  bin/migrate_db.py <target> --dry-run   # report current vs target version
  bin/migrate_db.py <target> --no-backup # skip the .bak/ snapshot
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    per_target_db,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


def _backup_db(db_path: Path) -> Path | None:
    bak_dir = db_path.parent / ".bak"
    bak_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    bak_path = bak_dir / f"{db_path.stem}.{ts}{db_path.suffix}"
    shutil.copy2(db_path, bak_path)
    return bak_path


def _migrate(db_path: Path, *, do_backup: bool, dry_run: bool) -> dict:
    tlx_sys_path()
    from modules.js_analyzer.v2_schema import (  # noqa: E402
        V2_SCHEMA_VERSION,
        apply,
        current_version,
    )

    conn = sqlite3.connect(str(db_path))
    try:
        before = current_version(conn)
        if dry_run:
            return {
                "db": str(db_path),
                "current": before,
                "target": V2_SCHEMA_VERSION,
                "needs_migration": before < V2_SCHEMA_VERSION,
                "dry_run": True,
            }
        bak = _backup_db(db_path) if do_backup else None
        applied = apply(conn)
        conn.commit()
        after = current_version(conn)
        return {
            "db": str(db_path),
            "current_before": before,
            "current_after": after,
            "applied_version": applied,
            "backup": str(bak) if bak else None,
            "ts": utcnow(),
        }
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("target", nargs="?", help="target name or path")
    g.add_argument("--global", dest="globally", action="store_true",
                   help="migrate ~/.tlx/js_analyzer.db instead of a per-target snapshot")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()

    if args.globally:
        db_path = Path.home() / ".tlx" / "js_analyzer.db"
        if not db_path.exists():
            print(f"missing global db: {db_path}", file=sys.stderr)
            return 2
        if not args.dry_run:
            print(
                "About to migrate the GLOBAL db at "
                f"{db_path}. This affects every target.",
                file=sys.stderr,
            )
        result = _migrate(db_path, do_backup=not args.no_backup, dry_run=args.dry_run)
    else:
        target = resolve_target_dir(args.target)
        db_path = per_target_db(target)
        if not db_path.exists():
            print(f"missing db: {db_path}", file=sys.stderr)
            return 2
        result = _migrate(db_path, do_backup=not args.no_backup, dry_run=args.dry_run)
        if not args.dry_run:
            write_status_phase(
                target,
                "migrate_db",
                {
                    "status": "done",
                    "ts": utcnow(),
                    "applied_version": result.get("applied_version"),
                    "backup": result.get("backup"),
                },
            )

    import json
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
