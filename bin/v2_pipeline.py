#!/usr/bin/env python3
"""V2 master pipeline runner.

Invokes every V2 subsystem whose env flag is enabled, against a
per-target snapshot DB. Idempotent — every module clears its own rows
before re-inserting.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §11-§24.

Usage:
  bin/v2_pipeline.py <target>
      [--db PATH]
      [--only sec1,sec2,...]     # subset by stage key
      [--all]                    # force every stage on regardless of env
      [--quiet]
      [--no-status]

Stage keys:
  parser_context, persistent_taint, origin_trust, dom_clobber,
  pp_gadgets, deobfuscation_normalize, corpus_patterns,
  sink_reachability, auth_abuse, worker_semantics

(query_dsl, delta_scan, multi_target_corr, chain_compression run via
 their own dedicated drivers; they don't touch the DB.)
"""
from __future__ import annotations

import argparse
import json
import os
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


_ALL_STAGES = [
    "parser_context",
    "persistent_taint",
    "origin_trust",
    "dom_clobber",
    "pp_gadgets",
    "deobfuscation_normalize",
    "corpus_patterns",
    "sink_reachability",
    "auth_abuse",
    "worker_semantics",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--only", default=None, help="Comma-separated stage keys")
    ap.add_argument("--all", action="store_true",
                    help="Force every stage on regardless of env flags")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db_path.exists():
        msg = f"per-target DB missing: {db_path}. Run db-isolate snapshot first."
        print(f"error: {msg}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "v2-pipeline", msg)
        return 2

    if args.all:
        # Force every stage on for this invocation.
        for stage in _ALL_STAGES:
            env_key = "JS_ENABLE_" + stage.upper()
            os.environ[env_key] = "1"

    tlx_sys_path()
    from modules.js_analyzer.v2 import run_enabled_stages  # noqa: E402

    only = [s.strip() for s in args.only.split(",")] if args.only else None
    t0 = time.monotonic()
    conn = sqlite3.connect(str(db_path))
    try:
        result = run_enabled_stages(conn, target, only=only)
    finally:
        conn.close()
    elapsed = round(time.monotonic() - t0, 3)
    result["target"] = target.name
    result["db"] = str(db_path)
    result["elapsed_s"] = elapsed

    if args.quiet:
        # Print a single one-line summary.
        ran = list((result.get("stages") or {}).keys())
        print(f"v2 ran={len(ran)} elapsed_s={elapsed} stages={','.join(ran)}")
    else:
        print(json.dumps(result, indent=2, default=str))

    if not args.no_status:
        write_status_phase(
            target,
            "v2_pipeline",
            {
                "status": "done",
                "ts": utcnow(),
                "stages_run": list((result.get("stages") or {}).keys()),
                "elapsed_s": elapsed,
                "schema_version": result.get("schema_version"),
            },
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
