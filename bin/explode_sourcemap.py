#!/usr/bin/env python3
"""Explode every .js.map file under <raw_dir> into an original source tree
at <sources_dir>.

Called by the `sourcemap-explode` skill. Pure-python (json only); no
dependency on TLX modules.

Usage:
  python bin/explode_sourcemap.py <raw_dir> <sources_dir>
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

WEBPACK_PREFIXES = ("webpack:///", "webpack://", "webpack-internal:///")


def _normalize(src_path: str) -> Path:
    p = src_path
    for prefix in WEBPACK_PREFIXES:
        if p.startswith(prefix):
            p = p[len(prefix):]
            break
    p = p.split("?", 1)[0]
    p = re.sub(r"^\./", "", p)
    p = re.sub(r"^\.+/", "", p)  # leading "./" or "../"
    p = p.lstrip("/")
    return Path(p)


def explode(raw_dir: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    nomap_dir = out_dir / "_nomap"
    nomap_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict = {"maps": [], "conflicts": [], "malformed": [], "nomap_files": []}
    conflicts = Counter()
    map_files = list(raw_dir.rglob("*.js.map"))

    for mp in map_files:
        try:
            with mp.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            manifest["malformed"].append({"path": str(mp), "error": str(e)})
            continue

        sources = data.get("sources", [])
        contents = data.get("sourcesContent")
        if not contents or len(contents) != len(sources):
            manifest["malformed"].append({"path": str(mp),
                                          "error": "sources/sourcesContent length mismatch"})
            continue

        for src_path, content in zip(sources, contents, strict=False):
            if content is None:
                continue
            normalized = _normalize(src_path)
            dest = out_dir / normalized
            if dest.exists():
                existing = dest.read_text(encoding="utf-8", errors="replace")
                if existing != content:
                    keep_longer = content if len(content) > len(existing) else existing
                    dest.write_text(keep_longer, encoding="utf-8")
                    conflicts[str(normalized)] += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")

        manifest["maps"].append({"path": str(mp), "sources_emitted": len(sources)})

    # Copy any .js that has no sibling .js.map into _nomap/
    for js in raw_dir.rglob("*.js"):
        if (js.with_suffix(".js.map")).exists():
            continue
        rel = js.relative_to(raw_dir)
        dest = nomap_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(js.read_bytes())
        manifest["nomap_files"].append(str(rel))

    manifest["conflicts"] = [{"path": k, "count": v} for k, v in conflicts.items()]
    (out_dir / "_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8",
    )
    return manifest


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    raw = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if not raw.is_dir():
        print(f"raw_dir not found: {raw}", file=sys.stderr)
        return 2
    res = explode(raw, out)
    summary = {
        "maps_processed": len(res["maps"]),
        "malformed": len(res["malformed"]),
        "conflicts": len(res["conflicts"]),
        "nomap_files": len(res["nomap_files"]),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
