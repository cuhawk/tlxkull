#!/usr/bin/env python3
"""IDOR + state-desync detector driver.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §23.

Usage:
  bin/auth_idor.py <target>
  bin/auth_idor.py <target> --idor-only
  bin/auth_idor.py <target> --state-desync-only
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
    ap.add_argument("--idor-only", action="store_true")
    ap.add_argument("--state-desync-only", action="store_true")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    tlx_sys_path()
    from modules.js_analyzer.auth_idor import (  # noqa: E402
        detect_idor,
        detect_state_desync,
        write_sidecars,
    )

    conn = sqlite3.connect(str(db))
    try:
        idor = [] if args.state_desync_only else detect_idor(conn)
        desync = [] if args.idor_only else detect_state_desync(conn)
    finally:
        conn.close()

    sidecar = write_sidecars(target, idor, desync)
    summary = {
        "target": target.name,
        "db": str(db),
        "idor": len(idor),
        "state_desync": len(desync),
        "outputs": sidecar.get("outputs", {}),
        "top_idor": [
            {"file": f.file, "line": f.line, "endpoint": f.endpoint,
             "confidence": f.confidence}
            for f in idor[:5]
        ],
        "top_state_desync": [
            {"function": f.function_qname,
             "auth_line": f.auth_read_line, "action_line": f.action_line,
             "confidence": f.confidence}
            for f in desync[:5]
        ],
    }
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "auth_idor",
        {
            "status": "done",
            "ts": utcnow(),
            "idor": len(idor),
            "state_desync": len(desync),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
