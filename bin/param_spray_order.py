#!/usr/bin/env python3
"""Emit a priority-ordered param spray list per target.

Tier order:
  1. target-static    — high-hit params from this target's bundle (extract_params.py output)
  2. target-live      — params seen in this target's wayback + browse logs
  3. cross-target     — top-N from wiki/payloads/param-dictionary.json where total_targets >= --min-targets
  4. seclists tail    — only if first 3 dry (< --thin-threshold params combined); reads from
                        a configured seclists path (--seclists), top-N

Writes targets/<name>/param_spray_order.txt — newline-delimited, dedup-preserved.
Does NOT actually send any HTTP. Sprayer is a separate tool.

Usage:
  python3 bin/param_spray_order.py <target-name>
  python3 bin/param_spray_order.py <target-name> --seclists /path/to/burp-params.txt --top-cross 50
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "targets"
CROSS_PATH = ROOT / "wiki" / "payloads" / "param-dictionary.json"


def load_target_dict(target_dir: Path) -> dict[str, dict]:
    p = target_dir / "param_dictionary.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def load_cross_dict() -> dict[str, dict]:
    if not CROSS_PATH.is_file():
        return {}
    try:
        return json.loads(CROSS_PATH.read_text())
    except Exception:
        return {}


def load_seclists(seclists_path: Path | None, limit: int) -> list[str]:
    if not seclists_path or not seclists_path.is_file():
        return []
    out: list[str] = []
    for line in seclists_path.read_text(errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
        if len(out) >= limit:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--static-min", type=int, default=2, help="Min static_hits for tier-1 inclusion")
    ap.add_argument("--live-min", type=int, default=1, help="Min live_hits for tier-2 inclusion")
    ap.add_argument("--top-cross", type=int, default=50, help="Max cross-target params to add as tier 3")
    ap.add_argument("--min-targets", type=int, default=2, help="Cross-target threshold (targets a param must appear in)")
    ap.add_argument("--seclists", help="Path to seclists params file (newline-delimited)")
    ap.add_argument("--seclists-top", type=int, default=200, help="Cap for seclists tier")
    ap.add_argument("--thin-threshold", type=int, default=30, help="Trigger seclists only if tiers 1+2+3 yield fewer than this many params")
    args = ap.parse_args()

    target_dir = TARGETS / args.target
    if not target_dir.is_dir():
        print(f"no such target: {target_dir}", file=sys.stderr)
        return 1

    target_dict = load_target_dict(target_dir)
    cross_dict = load_cross_dict()

    # Tier 1 — target-static
    tier1 = sorted(
        [name for name, info in target_dict.items() if info.get("static_hits", 0) >= args.static_min],
        key=lambda n: -target_dict[n].get("static_hits", 0),
    )

    # Tier 2 — target-live (exclude tier1)
    tier1_set = set(tier1)
    tier2 = sorted(
        [name for name, info in target_dict.items() if info.get("live_hits", 0) >= args.live_min and name not in tier1_set],
        key=lambda n: -target_dict[n].get("live_hits", 0),
    )

    # Tier 3 — cross-target (excluding tiers 1+2)
    seen = set(tier1) | set(tier2)
    cross_candidates = sorted(
        [(n, r) for n, r in cross_dict.items() if r.get("total_targets", 0) >= args.min_targets and n not in seen],
        key=lambda kv: -kv[1].get("total_hits", 0),
    )
    tier3 = [n for n, _ in cross_candidates[: args.top_cross]]

    # Tier 4 — seclists tail (only if thin)
    combined_count = len(tier1) + len(tier2) + len(tier3)
    tier4: list[str] = []
    if combined_count < args.thin_threshold:
        sec = load_seclists(Path(args.seclists), args.seclists_top) if args.seclists else []
        seen |= set(tier3)
        tier4 = [n for n in sec if n not in seen][: args.seclists_top]

    # Emit
    out_path = target_dir / "param_spray_order.txt"
    with out_path.open("w") as fh:
        fh.write(f"# tier 1 — target-static ({len(tier1)})\n")
        for n in tier1:
            fh.write(f"{n}\n")
        fh.write(f"\n# tier 2 — target-live ({len(tier2)})\n")
        for n in tier2:
            fh.write(f"{n}\n")
        fh.write(f"\n# tier 3 — cross-target frequency >={args.min_targets} targets ({len(tier3)})\n")
        for n in tier3:
            fh.write(f"{n}\n")
        fh.write(f"\n# tier 4 — seclists fallback ({len(tier4)}) [emitted only when tiers 1+2+3 < {args.thin_threshold}]\n")
        for n in tier4:
            fh.write(f"{n}\n")

    print(f"wrote {out_path}")
    print(f"  tier 1 (target-static): {len(tier1)}")
    print(f"  tier 2 (target-live):   {len(tier2)}")
    print(f"  tier 3 (cross-target):  {len(tier3)}")
    print(f"  tier 4 (seclists):      {len(tier4)}{' [skipped — tiers 1+2+3 not thin]' if combined_count >= args.thin_threshold else ''}")
    print(f"  total:                  {len(tier1) + len(tier2) + len(tier3) + len(tier4)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
