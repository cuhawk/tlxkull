#!/usr/bin/env python3
"""Backlink ingested blog source pages from matching people/<x>.md pages.

Idempotent: section bounded by markers; re-running updates the list in place.
"""
import re
from pathlib import Path

ROOT = Path("/Users/soural/Documents/TLX/wiki")

# blog dir under sources/blogs/personal/ → people page slug under people/
# Only entries for which a matching people page exists and the author is
# the *primary* writer (skip multi-author org blogs).
MAP = {
    "embracethered":   "johann-rehberger",
    "kevin-mizu":      "kevin-mizu",
    "spaceraccoon":    "spaceraccoon",
    "zlz-buerhaus":    "zlz",
    "matt-brown":      "matt-brown",
    "corben-leo":      "corben-leo",
    "slonser":         "slonser",
    "sam-curry":       "sam-curry",
    "rez0-thacker":    "rez0",
    "inti":            "inti-de-ceukelaire",
    "alex-chapman":    "alex-chapman",
    "sam-erb":         "sam-erb",
    "orange-tsai":     "orange-tsai",   # create page if missing
    "daniel-thatcher": "daniel-thatcher",
    "douglas-day":     "douglas-day",
    "gal-nagli":       "gal-nagli",
    "gareth-heyes":    "gareth-heyes",
    "jack-cable":      "jack-cable",
    "james-kettle":    "james-kettle",
    "johan-carlsson":  "johan-carlsson",
    "jr0ch17":         "jr0ch17",
    "matanber":        "matanber",
    "mathias-karlsson":"mathias-karlsson",
    "naglinagli-gh":   "gal-nagli",  # alias
    "nick-copi":       "nick-copi",
    "renniepak-csp":   "renniepak",
    # Aliases for legacy / per-book domains owned by an existing person:
    "skeletonscribe-kettle": "james-kettle",
    "thespanner-heyes":      "gareth-heyes",
    "spaceraccoon-book":     "spaceraccoon",
    "daniel-miessler":       "daniel-miessler",
}

MARK_S = "<!-- sources:auto:start -->"
MARK_E = "<!-- sources:auto:end -->"

def build_block(blog_dir: Path) -> str:
    pages = sorted(blog_dir.glob("*.md"))
    if not pages:
        return ""
    lines = [MARK_S, "## Ingested blog posts", ""]
    for p in pages:
        rel = p.relative_to(ROOT).as_posix()
        title = p.stem.replace("blog-", "").replace("-", " ")
        lines.append(f"- [{title}]({'../' + rel})")
    lines.append("")
    lines.append(MARK_E)
    return "\n".join(lines)

def upsert(people_md: Path, block: str):
    if not block:
        return False
    if not people_md.exists():
        # create minimal stub
        people_md.write_text(
            f"---\ntitle: {people_md.stem}\nslug: {people_md.stem}\n---\n\n# {people_md.stem}\n\n{block}\n",
            encoding="utf-8")
        return True
    txt = people_md.read_text(encoding="utf-8")
    if MARK_S in txt and MARK_E in txt:
        new = re.sub(
            re.escape(MARK_S) + r".*?" + re.escape(MARK_E),
            block, txt, count=1, flags=re.DOTALL)
    else:
        new = txt.rstrip() + "\n\n" + block + "\n"
    if new != txt:
        people_md.write_text(new, encoding="utf-8")
        return True
    return False

changed = []
skipped_empty = []
for blog_name, person_slug in MAP.items():
    blog_dir = ROOT / "sources/blogs/personal" / blog_name
    if not blog_dir.is_dir():
        continue
    block = build_block(blog_dir)
    if not block:
        skipped_empty.append(blog_name)
        continue
    target = ROOT / "people" / f"{person_slug}.md"
    if upsert(target, block):
        changed.append((blog_name, person_slug, len(list(blog_dir.glob("*.md")))))

print(f"updated {len(changed)} people pages:")
for b, p, n in changed:
    print(f"  {b} → people/{p}.md  ({n} posts)")
if skipped_empty:
    print(f"empty blog dirs (skipped): {', '.join(skipped_empty)}")
