#!/usr/bin/env python3
"""Paginate Caido for all JS URLs matching a host filter, dedupe, diff vs known.

This script does NOT call Caido directly (Caido MCP must be called from
Claude). Instead, accept JSON pages of caido_list_requests output, merge,
filter, and produce a delta vs the target's existing url_list_v*.txt.

Usage:
  # From Claude orchestrator: call caido_list_requests with pagination,
  # write each page to a temp file, then:
  python3 bin/caido_export_js.py \
      --pages page1.json page2.json ... \
      --host-substr coolblue \
      --target coolblue-intigriti \
      --out targets/coolblue-intigriti/raw/www.coolblue.de/_log/url_list_v3.txt
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pages", nargs="+", required=True, help="Caido response JSON files")
    p.add_argument("--host-substr", required=True, help="Host substring filter (e.g. coolblue)")
    p.add_argument("--target", required=True, help="Target dir name under targets/")
    p.add_argument("--out", required=True, help="Output URL list path")
    args = p.parse_args()

    all_urls: set[str] = set()
    for page_path in args.pages:
        try:
            data = json.loads(Path(page_path).read_text())
        except Exception as e:
            print(f"WARN: skipping {page_path}: {e}", file=sys.stderr)
            continue
        for req in data.get("requests", []):
            url = req.get("url", "")
            if args.host_substr in url and re.search(r"\.js(\?|$)", url):
                all_urls.add(url)

    # Read known URLs from prior url_list_v*.txt
    target_dir = ROOT / "targets" / args.target
    known: set[str] = set()
    for f in target_dir.rglob("url_list_v*.txt"):
        for line in f.read_text().splitlines():
            line = line.strip()
            if line:
                known.add(line)

    delta = sorted(all_urls - known)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(delta) + ("\n" if delta else ""))

    # Summarize
    mfes: dict[str, int] = {}
    for u in delta:
        m = re.search(r"/_app/([^/]+)/", u)
        if m:
            mfes[m.group(1)] = mfes.get(m.group(1), 0) + 1
        else:
            mfes["_other"] = mfes.get("_other", 0) + 1

    summary = {
        "captured_unique": len(all_urls),
        "already_known": len(all_urls & known),
        "delta_new": len(delta),
        "out": args.out,
        "mfe_distribution": mfes,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
