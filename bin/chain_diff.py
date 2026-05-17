#!/usr/bin/env python3
"""Diff two chain JSONL files by (source_qname, sink_qname) pair.

Usage:
    bin/chain_diff.py <old.jsonl> <new.jsonl>

Reports:
  - added: pairs in new not in old
  - removed: pairs in old not in new
  - kept: pairs in both
  - file-pair distribution of new chains
  - taxonomy-pair distribution of new chains
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def pair(c: dict) -> tuple[str, str]:
    return (c["source"]["qname"], c["sink"]["qname"])


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    old = load(Path(sys.argv[1]))
    new = load(Path(sys.argv[2]))
    old_pairs = {pair(c): c for c in old}
    new_pairs = {pair(c): c for c in new}

    added = sorted(set(new_pairs) - set(old_pairs))
    removed = sorted(set(old_pairs) - set(new_pairs))
    kept = sorted(set(new_pairs) & set(old_pairs))

    print(f"old: {len(old)}  new: {len(new)}")
    print(f"  added:   {len(added)}")
    print(f"  removed: {len(removed)}")
    print(f"  kept:    {len(kept)}")
    print()

    if added:
        added_chains = [new_pairs[p] for p in added]
        print("=== added: file-pair distribution ===")
        fp = Counter(
            (c["source"]["file"].split("__")[0], c["sink"]["file"].split("__")[0])
            for c in added_chains
        )
        for k, n in fp.most_common(20):
            print(f"  {n:4d}  {k[0][:40]:40s} -> {k[1][:40]}")
        print()
        print("=== added: taxonomy-pair distribution ===")
        tx = Counter(
            (c["source"]["taxonomy_id"], c["sink"]["taxonomy_id"])
            for c in added_chains
        )
        for k, n in tx.most_common(20):
            print(f"  {n:4d}  {k[0]:40s} -> {k[1]}")
        print()
        print("=== added: cross-file chains (top 30 by score) ===")
        cross = [c for c in added_chains if c.get("cross_file")]
        for c in sorted(cross, key=lambda x: -x.get("score", 0))[:30]:
            print(
                f"  score={c.get('score',0):.1f}  "
                f"{c['source']['taxonomy_id']:30s} -> {c['sink']['taxonomy_id']:30s}  "
                f"{c['source']['file'][:30]} -> {c['sink']['file'][:30]}"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
