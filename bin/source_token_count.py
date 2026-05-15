#!/usr/bin/env python3
"""Long-context viability probe (T1.3).

Estimate the token count of ``targets/<name>/sources/`` (heuristic:
bytes / 4). When the estimate is at or below the threshold (default
800k tokens), write ``targets/<name>/opus/whole_tree_prompt.md`` — a
prompt + file manifest the user can hand to a Claude Code subagent
running with the 1M-context Opus model.

Per the API-key whitelist this script does NOT call any LLM. It only
measures + emits the artifact. The audit / gap pass still happens via
the existing pipeline, but with ``docs_query`` retrieval skipped.

Usage:
  bin/source_token_count.py <target_dir>
      [--threshold N]   # default 800000
      [--chars-per-token N]   # default 4

Updates ``status.json.long_context = {eligible, est_tokens, ...}``
and ``status.json.phases.long_context``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    resolve_target_dir,
    status_lock,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)

tlx_sys_path()


def write_whole_tree_prompt(
    target: Path, sources_root: Path, est: dict, threshold: int
) -> Path:
    out_dir = target / "opus"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "whole_tree_prompt.md"

    files: list[Path] = sorted(
        p for p in sources_root.rglob("*") if p.is_file()
    )
    manifest_lines = [
        f"- {p.relative_to(sources_root)} ({p.stat().st_size}B)"
        for p in files
        if p.suffix.lower()
        in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".html", ".json")
    ]

    body = f"""# Long-context audit prompt — {target.name}

The full source tree at `{sources_root}` fits within the long-context
budget (~{est['est_tokens']:,} estimated tokens, threshold
{threshold:,}). Hand this file to a Claude Code subagent running on
Opus-class long-context to perform any of:

- whole-bundle adjacent-function-gap pass (T1.1)
- whole-bundle taint review (skip the cascade since you're seeing
  every callsite anyway)
- bundle-wide secret + URL surface review (cross-check with
  `index/jsluice.jsonl` if present)

## Instructions for the subagent

1. Read every file under `{sources_root.relative_to(target.parent)}/`
   that you need; default to a budget of ~{est['est_tokens']:,} tokens.
2. Honor scope: do NOT read any file under
   `targets/<other-target>/`. Stay within `{target.name}`.
3. Honor the API-key whitelist: do not invoke any external LLM beyond
   your own conversation context.
4. Deliverables:
   - For taint review: a list of confirmed source→sink chains with
     verdict + PoC.
   - For gap audit: a JSON array of `{{function, missing_control,
     reason, severity}}` per Justin Gardner's template (see
     `wiki/techniques/recon/adjacent-function-gap.md`).
5. Write findings to `targets/{target.name}/opus/long_context/`.

## File manifest ({len(manifest_lines)} files)

"""
    body += "\n".join(manifest_lines) + "\n"
    out.write_text(body)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    ap.add_argument("--threshold", type=int, default=800_000)
    ap.add_argument("--chars-per-token", type=int, default=4)
    args = ap.parse_args()

    try:
        target = resolve_target_dir(args.target_dir)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    sources_root = target / "sources"
    if not sources_root.exists():
        skipped = {
            "status": "skipped",
            "ts": utcnow(),
            "reason": "sources/ missing — run sourcemap-explode first",
        }
        write_status_phase(target, "long_context", skipped)
        print(json.dumps(skipped, indent=2))
        return 0

    from modules.js_analyzer.audit_pipeline import source_token_estimate

    est = source_token_estimate(
        sources_root, chars_per_token=args.chars_per_token
    )
    eligible = est["est_tokens"] <= args.threshold
    artifact_path: Path | None = None
    if eligible and est["files"] > 0:
        artifact_path = write_whole_tree_prompt(
            target, sources_root, est, args.threshold
        )

    result = {
        "status": "done",
        "ts": utcnow(),
        "eligible": eligible,
        "threshold": args.threshold,
        "chars_per_token": args.chars_per_token,
        "files": est["files"],
        "bytes": est["bytes"],
        "est_tokens": est["est_tokens"],
        "by_ext": est["by_ext"],
        "artifact": str(artifact_path.relative_to(target)) if artifact_path else None,
    }
    with status_lock(target) as data:
        data.setdefault("phases", {})["long_context"] = result
        data["long_context"] = {
            "eligible": eligible,
            "est_tokens": est["est_tokens"],
            "threshold": args.threshold,
            "ts": result["ts"],
        }
    print(json.dumps(result, indent=2))
    if eligible:
        print(
            f"\nlong-context mode active; if you want to run the whole-bundle "
            f"adjacent-gap pass, dispatch via `/feature-dev` with the contents "
            f"of {artifact_path.relative_to(target) if artifact_path else 'opus/whole_tree_prompt.md'}.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
