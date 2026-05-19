#!/usr/bin/env python3
"""Service Worker fetch interception + cache taint driver.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §24.4c-e.

Usage:
  bin/sw_intercept.py <target>
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
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    tlx_sys_path()
    from modules.js_analyzer.sw_intercept import run  # noqa: E402

    conn = sqlite3.connect(str(db))
    try:
        sidecar = run(conn, target)
    finally:
        conn.close()

    summary = {
        "target": target.name,
        "db": str(db),
        **sidecar,
    }
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "sw_intercept",
        {
            "status": "done",
            "ts": utcnow(),
            "fetch_handlers": sidecar.get("fetch_handlers", 0),
            "cache_writes": sidecar.get("cache_writes", 0),
            "unvalidated_message_handlers":
                sidecar.get("unvalidated_message_handlers", 0),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
