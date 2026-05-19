#!/usr/bin/env python3
"""Wiki lint — structural pass only (no LLM contradiction; not whitelisted)."""
import os, re, sys, time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

ROOT = Path("/Users/soural/Documents/TLX/wiki")
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
SEEN_RE = re.compile(r'(?i)seen[- ]in[- ]the[- ]wild|seen-in-wild|sightings?:|observed:')
DATE_RE = re.compile(r'(20\d{2})-(\d{2})-(\d{2})')

now = datetime.now()
stale_threshold = timedelta(days=180)

EXCLUDE_ROOTS = {"_external"}  # vendored, don't lint
LEAF_OK = {"SCHEMA.md"}        # always leaves

all_files = []
for p in ROOT.rglob("*.md"):
    rel = p.relative_to(ROOT)
    parts = rel.parts
    if parts and parts[0] in EXCLUDE_ROOTS:
        continue
    if rel.name.startswith("_lint_"):
        continue
    all_files.append(p)

file_set = {p.resolve() for p in all_files}
inbound = defaultdict(list)
dangling = []

for p in all_files:
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        continue
    base = p.parent
    for m in LINK_RE.finditer(text):
        href = m.group(2).split('#')[0].split('?')[0].strip()
        if not href: continue
        if href.startswith(('http://','https://','mailto:','#')): continue
        # resolve relative
        if href.startswith('/'):
            target = ROOT / href.lstrip('/')
        else:
            target = (base / href).resolve()
        # only care about .md targets inside wiki/
        if not str(target).startswith(str(ROOT)):
            continue
        if target.suffix == "" and not target.exists():
            # try .md
            t_md = target.with_suffix(".md")
            if t_md.exists():
                target = t_md
        if target.suffix == ".md":
            if target.exists():
                inbound[target.resolve()].append(p.resolve())
            else:
                dangling.append((p, href))

# Orphans
orphans = []
for p in all_files:
    rp = p.resolve()
    if rp in inbound and inbound[rp]:
        continue
    parts = p.relative_to(ROOT).parts
    if parts and parts[0] == "findings":
        continue  # leaves by design
    if p.name in LEAF_OK:
        continue
    if p.name == "README.md" or p.name == "index.md":
        continue  # entry points
    orphans.append(p)

# Stale techniques
stale = []
for p in all_files:
    parts = p.relative_to(ROOT).parts
    if not parts or parts[0] != "techniques":
        continue
    if len(parts) == 1:
        continue  # top-level technique index, skip
    text = p.read_text(encoding="utf-8", errors="replace")
    dates = DATE_RE.findall(text)
    last_seen = None
    if dates:
        cand = [datetime(int(y),int(m),int(d)) for y,m,d in dates if 2020<=int(y)<=2030]
        if cand:
            last_seen = max(cand)
    if last_seen is None:
        last_seen = datetime.fromtimestamp(p.stat().st_mtime)
    if (now - last_seen) > stale_threshold:
        stale.append((p, last_seen))

# Report
today = now.strftime("%Y%m%d")
out = ROOT / f"_lint_{today}.md"
lines = []
lines.append(f"# Wiki lint — {now.strftime('%Y-%m-%d')}")
lines.append("")
lines.append(f"_files scanned: {len(all_files)} (excludes `_external/**`, `_lint_*.md`)_")
lines.append(f"_contradictions: skipped — LLM call not in API whitelist per CLAUDE.md_")
lines.append("")
lines.append(f"## Orphans ({len(orphans)})")
lines.append("")
lines.append("Pages with zero inbound links from other wiki pages.")
lines.append("Excludes `findings/**`, `SCHEMA.md`, `README.md`, `index.md`.")
lines.append("")
# Group orphans by top dir
by_dir = defaultdict(list)
for p in orphans:
    parts = p.relative_to(ROOT).parts
    by_dir[parts[0] if parts else "_root"].append(p)
for d in sorted(by_dir.keys()):
    lst = sorted(by_dir[d], key=lambda x: x.stat().st_mtime, reverse=True)
    lines.append(f"### {d}/ ({len(lst)})")
    lines.append("")
    for p in lst[:200]:
        rel = p.relative_to(ROOT)
        ts = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
        lines.append(f"- `wiki/{rel}` — {ts}")
    if len(lst) > 200:
        lines.append(f"- _...{len(lst)-200} more truncated_")
    lines.append("")

lines.append(f"## Dangling links ({len(dangling)})")
lines.append("")
lines.append("Links pointing to .md files that do not exist.")
lines.append("")
# Group by source file
by_src = defaultdict(list)
for p, href in dangling:
    by_src[p].append(href)
src_sorted = sorted(by_src.items(), key=lambda kv: len(kv[1]), reverse=True)
for p, hrefs in src_sorted[:100]:
    rel = p.relative_to(ROOT)
    lines.append(f"- `wiki/{rel}` ({len(hrefs)}):")
    for h in hrefs[:10]:
        lines.append(f"  - `{h}`")
    if len(hrefs) > 10:
        lines.append(f"  - _...{len(hrefs)-10} more_")
if len(src_sorted) > 100:
    lines.append(f"- _...{len(src_sorted)-100} more source files truncated_")
lines.append("")

lines.append(f"## Stale techniques ({len(stale)})")
lines.append("")
lines.append("`techniques/**` pages whose newest dated entry / mtime is >180 days ago.")
lines.append("")
for p, ls in sorted(stale, key=lambda x: x[1]):
    rel = p.relative_to(ROOT)
    lines.append(f"- `wiki/{rel}` — last seen {ls.strftime('%Y-%m-%d')}")

out.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote: {out}")
print(f"orphans={len(orphans)} dangling={len(dangling)} stale={len(stale)}")
