#!/usr/bin/env python3
"""Infer the runtime browser context for a target.

Reads CSP / Trusted Types / framework / sandbox-iframe evidence from
``targets/<name>/`` (response headers, ``raw/*.html``, ``index/frameworks.json``,
``runtime/*/state.json``, per-target DB tags) and writes
``targets/<name>/browser_context.json``.

Consumed by ``modules.js_analyzer.sink_viability`` to multiply chain
scores by a CSP/TT/parser/framework-aware viability factor.

Idempotent — re-running overwrites the JSON. Safe to call before or
after ``js-index``; richer DB evidence appears only after indexing.

Usage:
  bin/infer_browser_context.py <target_name|path>
      [--explicit-csp 'default-src self; script-src ...']
      [--db PATH]
      [--quiet]
      [--no-status]
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--explicit-csp", default=None, help="CSP header value to add as an additional evidence source")
    ap.add_argument("--db", default=None, help="Per-target DB path (defaults to targets/<name>/db/js_analyzer.db)")
    ap.add_argument("--quiet", action="store_true", help="Only print the output path")
    ap.add_argument("--no-status", action="store_true", help="Do not write status.json.phases.browser_context")
    args = ap.parse_args(argv)

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    tlx_sys_path()
    try:
        from modules.js_analyzer.browser_context import infer, save  # noqa: E402
    except ImportError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    try:
        ctx = infer(
            target,
            db_path=args.db,
            explicit_csp_header=args.explicit_csp,
        )
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "browser-context-infer", e)
        return 1

    out_path = save(ctx, target)
    payload = asdict(ctx)

    if args.quiet:
        print(str(out_path))
    else:
        # Trim payload for the console — full JSON lands in the file.
        summary = {
            "target": target.name,
            "output": str(out_path),
            "csp": {
                "raw_present": bool(payload["csp"]["raw"]),
                "source": payload["csp"]["source"],
                "trusted_types_required": payload["csp"]["trusted_types_required"],
                "unsafe_inline_allowed": payload["csp"]["unsafe_inline_allowed"],
                "unsafe_eval_allowed": payload["csp"]["unsafe_eval_allowed"],
                "script_src_count": len(payload["csp"]["script_src"]),
            },
            "trusted_types": {
                "enforced": payload["trusted_types"]["enforced"],
                "policy_count": len(payload["trusted_types"]["policies"]),
            },
            "rendering": payload["rendering"],
            "sandbox_iframe_count": len(payload["sandbox_iframes"]),
            "evidence_files": payload["evidence_files"][:10],
        }
        print(json.dumps(summary, indent=2))

    if not args.no_status:
        write_status_phase(
            target,
            "browser_context",
            {
                "status": "done",
                "ts": utcnow(),
                "output": str(out_path),
                "csp_source": payload["csp"]["source"],
                "trusted_types_enforced": payload["trusted_types"]["enforced"],
                "framework": payload["rendering"]["framework"],
            },
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
