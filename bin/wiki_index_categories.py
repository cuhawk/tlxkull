#!/usr/bin/env python3
"""Round 2: index techniques/<cat>/, payloads/<cat>/, tools/<cat>/ subdirs
+ a top-level _index.md per category root, then a wiki/README.md root.

Idempotent: overwrites _index.md and README.md only.
"""
from pathlib import Path

ROOT = Path("/Users/soural/Documents/TLX/wiki")

CATEGORIES = ["techniques", "payloads", "tools"]

def write_dir_index(d: Path) -> int:
    pages = sorted([p for p in d.glob("*.md") if p.name != "_index.md"])
    subdirs = sorted([s for s in d.iterdir() if s.is_dir()])
    if not pages and not subdirs:
        return 0
    title = d.relative_to(ROOT).as_posix().replace("/", " · ")
    lines = [f"# {title}", "", f"_Auto-generated index._", ""]
    if subdirs:
        lines.append("## Subsections")
        lines.append("")
        for s in subdirs:
            sub_idx = s / "_index.md"
            if sub_idx.exists():
                lines.append(f"- [{s.name}/](./{s.name}/_index.md)")
            else:
                lines.append(f"- [{s.name}/](./{s.name}/)")
        lines.append("")
    if pages:
        lines.append("## Pages")
        lines.append("")
        for p in pages:
            name = p.stem.replace("-", " ")
            lines.append(f"- [{name}]({p.name})")
        lines.append("")
    (d / "_index.md").write_text("\n".join(lines), encoding="utf-8")
    return len(pages) + len(subdirs)

total = 0
for cat in CATEGORIES:
    root_d = ROOT / cat
    if not root_d.is_dir():
        continue
    # walk every subdir bottom-up so parent indexes can reference child _index.md
    all_dirs = sorted([d for d in root_d.rglob("*") if d.is_dir()], key=lambda x: -len(x.parts))
    for d in all_dirs:
        n = write_dir_index(d)
        if n:
            total += 1
    # top-level cat root last
    n = write_dir_index(root_d)
    if n:
        total += 1
        print(f"  {cat}/_index.md")

# people/_index already exists (orphan in lint); we just regenerate a clean one
# linking each person page
people = ROOT / "people"
ppl_pages = sorted([p for p in people.glob("*.md") if p.name not in ("_index.md",)])
plines = ["# People", "", f"_{len(ppl_pages)} profiles._", ""]
for p in ppl_pages:
    plines.append(f"- [{p.stem.replace('-', ' ').title()}]({p.name})")
(people / "_index.md").write_text("\n".join(plines) + "\n", encoding="utf-8")
print("  people/_index.md")

# targets/_index — flat list of targets
targets = ROOT / "targets"
if targets.is_dir():
    tpages = sorted([p for p in targets.glob("*.md") if p.name not in ("_index.md",)])
    if tpages:
        tlines = ["# Targets (wiki notes)", "", f"_{len(tpages)} entries._", ""]
        for p in tpages:
            tlines.append(f"- [{p.stem}]({p.name})")
        (targets / "_index.md").write_text("\n".join(tlines) + "\n", encoding="utf-8")
        print("  targets/_index.md")

# wiki root README
readme = ROOT / "README.md"
rlines = ["# Wiki", "",
          "Personal LLM-maintained bug-bounty wiki.",
          "Auto-generated indexes; manual content under each section.", "",
          "## Sections", "",
          "- [Techniques](techniques/_index.md)",
          "- [Payloads](payloads/_index.md)",
          "- [Tools](tools/_index.md)",
          "- [People](people/_index.md)",
          "- [Sources](sources/_index.md)",
          "- [Targets (notes)](targets/_index.md)",
          "- [Findings](findings/)",
          "- [Schema](SCHEMA.md)", ""]
readme.write_text("\n".join(rlines), encoding="utf-8")
print(f"  README.md")
print(f"total dir indexes: {total}")
