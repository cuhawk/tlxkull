#!/usr/bin/env python3
"""Detect targets stuck at the hot->audited workflow gap.

Background: pipeline_calibration_2026-05-18 found that on big targets,
`chains/hot.jsonl` populates but `opus/` stays empty -- the audit phase
never fires. Cause is user-habit (session ends before
cc-taint-adversarial / opus-deep-audit runs), not static analysis.

This checker scans every target dir and reports the per-target audit-gap
state plus the next concrete command to close it. Wire into a
SessionStart hook so the gap surfaces at the top of every session.

Output format: one block per target with a gap; nothing for clean
targets. Exits 0 always (diagnostic, not a gate).

Skips `-syn` targets (Synack reference-only per memory rule).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import TARGETS_DIR  # noqa: E402


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as fh:
        return sum(1 for line in fh if line.strip())


def _audited_chain_ids(target: Path) -> set[str]:
    """Chains that have any audit output (cc-taint json OR opus md)."""
    out: set[str] = set()
    opus = target / "opus"
    if opus.exists():
        for child in opus.iterdir():
            if child.suffix in (".json", ".md") and not child.name.startswith("_"):
                out.add(child.stem)
    fp_arch = target / "chains" / "_fp_archive.jsonl"
    if fp_arch.exists():
        with fp_arch.open() as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                    cid = rec.get("chain_id")
                    if cid is not None:
                        out.add(str(cid))
                except json.JSONDecodeError:
                    continue
    return out


def _expanded_chain_ids(target: Path) -> set[str]:
    expanded = target / "chains" / "expanded"
    if not expanded.exists():
        return set()
    return {p.stem for p in expanded.glob("*.json")}


def _prompts_ready(target: Path) -> int:
    promp_dir = target / "opus" / "_prompts"
    if not promp_dir.exists():
        return 0
    return len(list(promp_dir.glob("*.md")))


def _hot_chain_ids(hot_path: Path) -> set[str]:
    out: set[str] = set()
    if not hot_path.exists():
        return out
    with hot_path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                cid = rec.get("chain_id") or rec.get("id")
                if cid is not None:
                    out.add(str(cid))
            except json.JSONDecodeError:
                continue
    return out


def check_target(target: Path) -> dict | None:
    name = target.name
    if name.endswith("-syn"):
        return None

    chains = target / "chains"
    hot = chains / "hot.jsonl"
    dom_reach = chains / "dom_reachable.jsonl"

    hot_n = _count_jsonl(hot)
    dom_n = _count_jsonl(dom_reach)
    primary = dom_reach if dom_n > 0 else hot
    primary_ids = _hot_chain_ids(primary)
    primary_n = len(primary_ids)

    if primary_n == 0:
        return None

    audited = _audited_chain_ids(target)
    audited_for_primary = primary_ids & audited
    expanded = _expanded_chain_ids(target) & primary_ids
    prompts = _prompts_ready(target)

    audited_n = len(audited_for_primary)
    if audited_n >= primary_n:
        return None

    if dom_n > 0:
        chains_input = "chains/dom_reachable.jsonl"
    else:
        chains_input = "chains/hot.jsonl"

    if not expanded:
        next_step = (
            f"python3 bin/expand_snippet.py --target {name} --all "
            f"--chains-input {chains_input}"
        )
        stage = "expand"
    elif prompts == 0:
        next_step = (
            f"python3 bin/cc_taint_runner.py --target {name} prepare "
            f"--chains-input {chains_input}"
        )
        stage = "prepare-prompts"
    else:
        next_step = (
            "/cc-taint-adversarial " + name +
            "   # dispatch subagents per opus/_prompts/<id>.md"
        )
        stage = "dispatch-subagents"

    return {
        "target": name,
        "primary": primary.name,
        "primary_n": primary_n,
        "audited_n": audited_n,
        "expanded_n": len(expanded),
        "prompts_ready": prompts,
        "stage": stage,
        "next_step": next_step,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--target", help="Check a single target instead of every dir under targets/."
    )
    ap.add_argument(
        "--json", action="store_true", help="Emit JSON instead of human output."
    )
    args = ap.parse_args()

    if args.target:
        roots = [TARGETS_DIR / args.target]
    else:
        roots = sorted(p for p in TARGETS_DIR.iterdir() if p.is_dir())

    gaps = []
    for target in roots:
        if not target.exists():
            continue
        gap = check_target(target)
        if gap:
            gaps.append(gap)

    if args.json:
        print(json.dumps(gaps, indent=2))
        return 0

    if not gaps:
        return 0

    print(f"[audit-gap] {len(gaps)} target(s) stuck at hot->audited:")
    for g in gaps:
        audited_frac = f"{g['audited_n']}/{g['primary_n']}"
        print(
            f"  - {g['target']}: audited {audited_frac} from {g['primary']} "
            f"(expanded={g['expanded_n']}, prompts={g['prompts_ready']}, stage={g['stage']})"
        )
        print(f"      next: {g['next_step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
