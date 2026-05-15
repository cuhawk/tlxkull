#!/usr/bin/env python3
"""Build-manifest extractor (T2.3).

Parse framework build manifests under ``targets/<name>/raw/`` to
enumerate SPA routes — including hidden admin paths — that the standard
crawl missed. Feeds the route list back into ``js-harvest`` for re-crawl.

Supported manifests:
  - Next.js   `_buildManifest.js`, `routes-manifest.json`
  - Rspack    `rspack.client.json`
  - Vite      `manifest.json`
  - CRA       `asset-manifest.json`

Usage:
  bin/build_manifest_extract.py <target_dir>

Output:
    targets/<name>/index/routes.jsonl  — one route per line:
        { "source_manifest": "...", "route": "/foo/[id]",
          "kind": "static|dynamic", "framework": "next|vite|rspack|cra" }
    status.json.phases.build_manifest
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import resolve_target_dir, utcnow, write_status_phase  # noqa: E402


_NEXT_BUILDMANIFEST_REGEX = re.compile(
    r"self\.__BUILD_MANIFEST\s*=\s*(\{[\s\S]*?\})\s*;",
    re.MULTILINE,
)


def parse_next_build_manifest(content: str) -> list[dict]:
    """``_buildManifest.js`` is a JS object literal — keys are route
    paths, values are chunk arrays. Pull keys via regex; do NOT try to
    eval JS.
    """
    m = _NEXT_BUILDMANIFEST_REGEX.search(content)
    body = m.group(1) if m else content
    keys = re.findall(r'"((?:/[^"]*)?(?:\\\\.|[^"\\\\])*)"\s*:\s*\[', body)
    return [
        {"route": k, "kind": "dynamic" if "[" in k else "static", "framework": "next"}
        for k in keys
        if k.startswith("/")
    ]


def parse_next_routes_manifest(data: dict) -> list[dict]:
    out: list[dict] = []
    for r in data.get("staticRoutes", []) or []:
        out.append(
            {"route": r.get("page") or r.get("regex"), "kind": "static", "framework": "next"}
        )
    for r in data.get("dynamicRoutes", []) or []:
        out.append(
            {"route": r.get("page") or r.get("regex"), "kind": "dynamic", "framework": "next"}
        )
    return [x for x in out if x["route"]]


def parse_vite_manifest(data: dict) -> list[dict]:
    out: list[dict] = []
    for key, val in data.items():
        if isinstance(val, dict) and val.get("isEntry"):
            out.append(
                {"route": f"/{key}", "kind": "static", "framework": "vite"}
            )
    return out


def parse_rspack_manifest(data: dict) -> list[dict]:
    out: list[dict] = []
    chunks = data.get("entrypoints") or data.get("namedChunks") or {}
    if isinstance(chunks, dict):
        for name in chunks:
            out.append({"route": f"/{name}", "kind": "static", "framework": "rspack"})
    return out


def parse_cra_asset_manifest(data: dict) -> list[dict]:
    files = data.get("files") or {}
    out: list[dict] = []
    for k in files:
        if k.endswith(".html"):
            out.append(
                {"route": f"/{k.removesuffix('.html')}", "kind": "static", "framework": "cra"}
            )
    return out


def find_and_extract(raw_root: Path) -> tuple[list[dict], list[str]]:
    """Walk ``raw_root`` looking for manifest files; return (routes, scanned)."""
    routes: list[dict] = []
    scanned: list[str] = []

    for p in raw_root.rglob("_buildManifest.js"):
        scanned.append(str(p.relative_to(raw_root)))
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for r in parse_next_build_manifest(content):
            r["source_manifest"] = str(p.relative_to(raw_root))
            routes.append(r)

    for name, parser in (
        ("routes-manifest.json", parse_next_routes_manifest),
        ("manifest.json", parse_vite_manifest),
        ("rspack.client.json", parse_rspack_manifest),
        ("asset-manifest.json", parse_cra_asset_manifest),
    ):
        for p in raw_root.rglob(name):
            scanned.append(str(p.relative_to(raw_root)))
            try:
                data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
            except (json.JSONDecodeError, OSError):
                continue
            for r in parser(data):
                r["source_manifest"] = str(p.relative_to(raw_root))
                routes.append(r)

    seen: set[tuple] = set()
    unique: list[dict] = []
    for r in routes:
        key = (r.get("framework"), r.get("route"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    unique.sort(key=lambda x: (x["framework"], x["route"]))
    return unique, scanned


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    args = ap.parse_args()

    try:
        target = resolve_target_dir(args.target_dir)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    raw_root = target / "raw"
    if not raw_root.exists():
        skipped = {
            "status": "skipped",
            "ts": utcnow(),
            "reason": "raw/ missing — run js-harvest first",
        }
        write_status_phase(target, "build_manifest", skipped)
        print(json.dumps(skipped, indent=2))
        return 0

    routes, scanned = find_and_extract(raw_root)
    out_dir = target / "index"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "routes.jsonl"
    with out_file.open("w") as f:
        for r in routes:
            f.write(json.dumps(r) + "\n")

    by_framework: dict[str, int] = {}
    for r in routes:
        by_framework[r["framework"]] = by_framework.get(r["framework"], 0) + 1

    result = {
        "status": "done",
        "ts": utcnow(),
        "manifests_scanned": len(scanned),
        "routes_extracted": len(routes),
        "by_framework": by_framework,
        "output_file": str(out_file.relative_to(target)),
        "manifest_paths": scanned[:20],
    }
    write_status_phase(target, "build_manifest", result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
