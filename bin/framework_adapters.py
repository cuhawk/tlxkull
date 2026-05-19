#!/usr/bin/env python3
"""Framework adapter driver.

Plan: plans/ARCHITECTURE_EVOLUTION.md §6.

Runs ``patch_tags`` + ``rewrite_edges`` from every detected (or
explicitly requested) adapter against a per-target snapshot DB.

Usage:
  bin/framework_adapters.py <target>              # auto from frameworks.json
  bin/framework_adapters.py <target> --framework react --framework vue
  bin/framework_adapters.py <target> --list       # show registry
  bin/framework_adapters.py <target> --tags-only  # skip rewrite_edges
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


def _detect_frameworks(target: Path) -> list[str]:
    fp = target / "frameworks.json"
    if not fp.exists():
        return []
    try:
        data = json.loads(fp.read_text())
    except Exception:
        return []
    out: list[str] = []
    if isinstance(data, dict):
        for key in ("detected", "frameworks"):
            v = data.get(key)
            if isinstance(v, list):
                out = [str(x).lower() for x in v]
                break
    elif isinstance(data, list):
        out = [str(x).lower() for x in data]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--framework", action="append", default=[])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--tags-only", action="store_true")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    tlx_sys_path()
    from modules.js_analyzer.frameworks import all_names, get  # noqa: E402

    if args.list:
        print(json.dumps({"registered": all_names()}, indent=2))
        return 0

    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    chosen = [f.lower() for f in args.framework] or _detect_frameworks(target)
    if not chosen:
        print("no frameworks detected and none specified", file=sys.stderr)
        return 2

    summary: dict = {"target": target.name, "frameworks": []}
    conn = sqlite3.connect(str(db))
    try:
        for name in chosen:
            ad = get(name)
            if ad is None:
                summary["frameworks"].append(
                    {"name": name, "status": "no_adapter"}
                )
                continue
            patched = ad.patch_tags(conn)
            edges = 0 if args.tags_only else ad.rewrite_edges(conn)
            summary["frameworks"].append(
                {
                    "name": ad.name,
                    "tags_patched": patched,
                    "edges_rewritten": edges,
                }
            )
    finally:
        conn.close()
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "framework_adapters",
        {
            "status": "done",
            "ts": utcnow(),
            "frameworks": chosen,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
