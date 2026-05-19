#!/usr/bin/env python3
"""Obfuscation normalization driver.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §16.

Two modes:

  per-node    — walk every node in the snapshot, read its source slice,
                run the 5-pass pipeline, persist into
                ``obfuscation_normalized``.

  one-shot    — take a file or stdin, print normalized text + applied
                passes. Useful when validating the pipeline on tricky
                snippets.

Usage:
  bin/obfuscation_normalize.py <target>             # per-node mode
  bin/obfuscation_normalize.py --file <path>        # one-shot
  echo '<text>' | bin/obfuscation_normalize.py --stdin
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
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("target", nargs="?")
    g.add_argument("--file", default=None, help="one-shot mode: file path")
    g.add_argument("--stdin", action="store_true", help="one-shot mode: read stdin")
    ap.add_argument("--db", default=None)
    args = ap.parse_args()

    tlx_sys_path()
    from modules.js_analyzer.obfuscation_normalize import (  # noqa: E402
        normalize_all_nodes,
        normalize_snippet,
    )

    if args.file or args.stdin:
        if args.stdin:
            text = sys.stdin.read()
        else:
            text = Path(args.file).read_text(encoding="utf-8", errors="replace")
        res = normalize_snippet(text)
        print(json.dumps({
            "passes_applied": res.passes_applied,
            "original_size": res.original_size,
            "final_size": res.final_size,
            "confidence": res.confidence,
        }, indent=2))
        print("---")
        print(res.normalized)
        return 0

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2
    conn = sqlite3.connect(str(db))
    try:
        sidecar = normalize_all_nodes(conn, target)
    finally:
        conn.close()
    print(json.dumps({"target": target.name, **sidecar}, indent=2))
    write_status_phase(
        target,
        "obfuscation_normalize",
        {
            "status": "done",
            "ts": utcnow(),
            "rows_saved": sidecar.get("rows_saved", 0),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
