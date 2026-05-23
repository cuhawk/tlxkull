#!/usr/bin/env python3
"""Aggregate in-scope assets across targets/*-<platform>/http.md into per-platform/per-class files.

Bucket each `- in:` line by `# type:` tag:
  ip_cidr   <- cidr, cidr_v, ip_address, ip
  wildcards <- wildcard
  urls      <- url, api, domain

Writes targets/scope_<platform>_<bucket>.txt deduped+sorted.
"""
import re
from pathlib import Path
from collections import defaultdict

PLATFORMS = {"h1": "hackerone", "bc": "bugcrowd", "intigriti": "intigriti"}
BUCKETS = {
    "ip_cidr": {"cidr", "cidr_v", "ip_address", "ip", "iprange"},
    "wildcards": {"wildcard"},
    "urls": {"url", "api", "domain"},
}
LINE_RE = re.compile(r"^-\s*in:\s*(.*?)\s*#\s*type:\s*([a-z_]+)", re.IGNORECASE)
IP_SHAPE_RE = re.compile(
    r"^\s*(?:\d{1,3}\.){3}\d{1,3}(?:\s*[-/]\s*(?:\d{1,3}\.){3}\d{1,3}|/\d{1,2})?\s*$"
)

ROOT = Path(__file__).resolve().parent.parent / "targets"
UPSTREAM = Path(__file__).resolve().parent / "scope_upstream"

assets: dict[tuple[str, str], set[str]] = defaultdict(set)

for suffix, platform in PLATFORMS.items():
    for tdir in sorted(ROOT.glob(f"*-{suffix}")):
        http = tdir / "http.md"
        if not http.is_file():
            continue
        for line in http.read_text(errors="replace").splitlines():
            m = LINE_RE.match(line.strip())
            if not m:
                continue
            raw, typ = m.group(1).strip(), m.group(2).lower()
            if IP_SHAPE_RE.match(raw):
                assets[(platform, "ip_cidr")].add(raw)
                continue
            for bucket, types in BUCKETS.items():
                if typ in types:
                    assets[(platform, bucket)].add(raw)
                    break

if UPSTREAM.is_dir():
    for sidecar in sorted(UPSTREAM.glob("*.txt")):
        stem = sidecar.stem
        for bucket in BUCKETS:
            if stem.endswith(f"_{bucket}"):
                platform = stem[: -len(f"_{bucket}")]
                if platform in PLATFORMS.values():
                    for line in sidecar.read_text(errors="replace").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#"):
                            assets[(platform, bucket)].add(line)
                break

for (platform, bucket), items in assets.items():
    out = ROOT / f"scope_{platform}_{bucket}.txt"
    out.write_text("\n".join(sorted(items)) + "\n")
    print(f"{out.relative_to(ROOT.parent)}: {len(items)}")
