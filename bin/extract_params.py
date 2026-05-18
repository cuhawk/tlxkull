#!/usr/bin/env python3
"""Extract per-target URL param dictionary from two layers.

Layer A (static): grep bundle sources for literal param names in
`URLSearchParams.get('NAME')`, `searchParams.get('NAME')`, `req.query.NAME`,
`router.query.NAME`, `useRouter().query.NAME`, `params.NAME`,
`new URL(...).searchParams.get('NAME')`.

Layer B (live): parse wayback_param_urls.txt and any caido replay/capture
exports for actual URL params seen in the wild.

Outputs:
  targets/<name>/param_dictionary.json — {param: {static_hits, live_hits, in_scope}}
  Optional --aggregate-into <path>: append to a cross-target frequency table.

Usage:
  python3 bin/extract_params.py <target-name> [--aggregate-into wiki/payloads/param-dictionary.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "targets"

# Static extraction patterns — each captures the param-name literal.
STATIC_PATTERNS = [
    re.compile(r"""\b(?:URLSearchParams\s*\([^)]*\)|searchParams)\s*\.get\s*\(\s*['"]([A-Za-z_][\w.-]{0,80})['"]"""),
    re.compile(r"""\.get\s*\(\s*['"]([A-Za-z_][\w.-]{0,80})['"]\s*\)\s*[;,)]"""),  # generic .get() — over-matches; filtered below
    re.compile(r"""\breq\.query\.([A-Za-z_][\w$]{0,80})"""),
    re.compile(r"""\brouter\.query\.([A-Za-z_][\w$]{0,80})"""),
    re.compile(r"""\buseRouter\s*\(\s*\)\.query\.([A-Za-z_][\w$]{0,80})"""),
    re.compile(r"""\bparams\.([A-Za-z_][\w$]{0,80})"""),
    re.compile(r"""new\s+URL\s*\([^)]*\)\.searchParams\.get\s*\(\s*['"]([A-Za-z_][\w.-]{0,80})['"]"""),
    re.compile(r"""\bevent\.url\.searchParams\.get\s*\(\s*['"]([A-Za-z_][\w.-]{0,80})['"]"""),
]

# Names that look like real URL params, not random object keys, function names, etc.
GENERIC_BLOCKLIST = {
    "constructor", "prototype", "length", "name", "value", "type", "data", "key",
    "id", "default", "current", "props", "state", "context", "self", "this",
    "config", "options", "params", "query", "search", "hash", "pathname",
    "toString", "valueOf", "call", "apply", "bind", "then", "catch", "finally",
    "hasOwnProperty", "indexOf", "slice", "split", "join", "push", "pop", "shift",
    "filter", "map", "reduce", "forEach", "find", "some", "every", "includes",
    "match", "replace", "trim", "concat", "substr", "substring",
}


def extract_static(target_dir: Path) -> dict[str, int]:
    """Walk sources/ and return {param_name: hit_count}."""
    sources = target_dir / "sources"
    if not sources.is_dir():
        return {}
    hits: dict[str, int] = {}
    for js in sources.rglob("*.js"):
        try:
            text = js.read_text(errors="ignore")
        except Exception:
            continue
        for pat in STATIC_PATTERNS:
            for m in pat.finditer(text):
                name = m.group(1)
                if name in GENERIC_BLOCKLIST or len(name) < 2 or len(name) > 64:
                    continue
                if name.startswith("_") and name.endswith("_"):  # __FOO__ react internals
                    continue
                hits[name] = hits.get(name, 0) + 1
    return hits


def extract_live(target_dir: Path) -> dict[str, int]:
    """Parse wayback_param_urls.txt + any caido_replay/*.json for live param sightings."""
    hits: dict[str, int] = {}
    wb = target_dir / "wayback_param_urls.txt"
    if wb.is_file():
        for line in wb.read_text(errors="ignore").splitlines():
            url = line.strip()
            if not url:
                continue
            try:
                qs = parse_qs(urlparse(url).query, keep_blank_values=True)
            except Exception:
                continue
            for k in qs:
                if not k or k in GENERIC_BLOCKLIST or len(k) > 64:
                    continue
                hits[k] = hits.get(k, 0) + 1
    return hits


def load_scope_hosts(target_dir: Path) -> list[str]:
    status = target_dir / "status.json"
    if not status.is_file():
        return []
    try:
        data = json.loads(status.read_text())
    except Exception:
        return []
    out: list[str] = []
    for entry in data.get("scope", {}).get("in", []):
        v = entry.get("value") or ""
        if not v:
            continue
        # strip wildcards and labels
        v = v.replace("*.", "").split()[0]
        out.append(v)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--aggregate-into", help="Optional cross-target frequency JSON to update")
    ap.add_argument("--top", type=int, default=40, help="Print top-N most-hit params")
    args = ap.parse_args()

    target_dir = TARGETS / args.target
    if not target_dir.is_dir():
        print(f"no such target: {target_dir}", file=sys.stderr)
        return 1

    static_hits = extract_static(target_dir)
    live_hits = extract_live(target_dir)
    scope_hosts = load_scope_hosts(target_dir)

    all_params = set(static_hits) | set(live_hits)
    out: dict[str, dict] = {}
    for p in all_params:
        out[p] = {
            "static_hits": static_hits.get(p, 0),
            "live_hits": live_hits.get(p, 0),
            "total": static_hits.get(p, 0) + live_hits.get(p, 0),
        }

    dict_path = target_dir / "param_dictionary.json"
    dict_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {dict_path} — {len(out)} params")

    # Top-N preview
    sorted_params = sorted(out.items(), key=lambda kv: -kv[1]["total"])
    print(f"\nTop {args.top} (by static+live hits) for {args.target}:")
    for name, info in sorted_params[: args.top]:
        print(f"  {info['total']:>4}  static={info['static_hits']:<4}  live={info['live_hits']:<4}  {name}")

    if args.aggregate_into:
        agg_path = Path(args.aggregate_into)
        if not agg_path.is_absolute():
            agg_path = ROOT / agg_path
        agg = {}
        if agg_path.is_file():
            try:
                agg = json.loads(agg_path.read_text())
            except Exception:
                agg = {}
        for name, info in out.items():
            row = agg.setdefault(name, {"targets": {}, "total_targets": 0, "total_hits": 0})
            row["targets"][args.target] = info["total"]
            row["total_targets"] = len(row["targets"])
            row["total_hits"] = sum(row["targets"].values())
        agg_path.parent.mkdir(parents=True, exist_ok=True)
        agg_path.write_text(json.dumps(agg, indent=2, sort_keys=True) + "\n")
        print(f"\nupdated cross-target dict: {agg_path} ({len(agg)} params, {sum(1 for v in agg.values() if v['total_targets']>1)} multi-target)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
