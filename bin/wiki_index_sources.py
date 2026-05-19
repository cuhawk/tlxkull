#!/usr/bin/env python3
"""Generate _index.md per source dir + top-level sources/_index.md to close
orphan status for bulk-ingested source pages.

Idempotent: overwrites _index.md files only.
"""
from pathlib import Path

ROOT = Path("/Users/soural/Documents/TLX/wiki")
SRC = ROOT / "sources"

# dirs that should get a flat _index.md listing every .md (non-recursive)
DIRS = [
    "hacktivity",
    "blogs/bughunters",
    "blogs/detectify",
    "blogs/msrc",
    "blogs/p0",
    "blogs/personal/portswigger-research",
    "blogs/personal/daniel-miessler",
    "blogs/personal/assetnote",
    "blogs/personal/securitum-research",
    "blogs/personal/oversecured",
    "podcasts/ct",
]

def write_dir_index(rel_dir: str):
    d = SRC / rel_dir
    if not d.is_dir():
        return 0, None
    pages = sorted([p for p in d.glob("*.md") if p.name != "_index.md"])
    if not pages:
        return 0, None
    title = rel_dir.replace("/", " · ")
    lines = [f"# {title}", "",
             f"_Auto-generated index. {len(pages)} ingested pages._", ""]
    for p in pages:
        name = p.stem.replace("blog-", "").replace("-", " ")
        lines.append(f"- [{name}]({p.name})")
    idx = d / "_index.md"
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(pages), idx

results = []
for rd in DIRS:
    n, idx = write_dir_index(rd)
    if n:
        results.append((rd, n, idx))
        print(f"  {rd}/_index.md  ({n} entries)")

# Top-level sources/_index.md linking all dir indexes
top_lines = ["# Sources index", "",
             "Auto-generated. Each entry below is a directory index that",
             "lists every ingested page in that source bucket.", ""]
for rd, n, idx in results:
    top_lines.append(f"- [{rd}]({idx.relative_to(SRC).as_posix()}) — {n} pages")
top = SRC / "_index.md"
top.write_text("\n".join(top_lines) + "\n", encoding="utf-8")
print(f"\nwrote {top}")
print(f"total dir indexes: {len(results)}")
print(f"total entries linked: {sum(n for _,n,_ in results)}")
