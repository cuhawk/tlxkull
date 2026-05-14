"""Wiki structural lint — orphans + dangling links + stale.

Supports both:
- standard markdown:  [text](relative/path.md)
- obsidian wikilinks: [[slug]] or [[../path/slug]]

Writes wiki/_lint_<YYYYMMDD>.md. Does NOT touch any wiki page.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WIKI = REPO / "wiki"

# Ignore these for orphan detection (leaves by design)
ORPHAN_EXEMPT_PATTERNS = [
    "SCHEMA.md",
    "_ingest_log.jsonl",
    "_lint_",
    "findings/",
    "_external/",
    "sources/podcasts/ct/whisper/",  # transcripts dir is not in graph
    "README.md",  # per-folder README pages are leaves
    "_wiki_ingest_summary.md",
]

STALE_THRESHOLD_DAYS = 180


def is_exempt(rel: str) -> bool:
    return any(p in rel for p in ORPHAN_EXEMPT_PATTERNS)


_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def slug_to_candidates(slug: str, all_pages: set[str]) -> list[str]:
    """Resolve a wikilink slug to potential page paths.

    Tries:
    - exact path match with .md suffix
    - directory match -> notes.md or SUMMARY.md or README.md inside dir
    - basename-only match across the tree
    """
    s = slug.split("#", 1)[0].split("|", 1)[0].strip()
    if not s:
        return []
    if s.endswith(".md"):
        s_md = s
    else:
        s_md = s + ".md"
    cands = []
    # directory link -> resolve to index page
    if not s.endswith(".md"):
        for idx in ("notes.md", "SUMMARY.md", "README.md"):
            for p in all_pages:
                if p.endswith(f"/{s}/{idx}") or p == f"{s}/{idx}":
                    cands.append(p)
    # exact match by basename
    for p in all_pages:
        if Path(p).name == Path(s_md).name:
            cands.append(p)
        elif p.endswith("/" + s_md):
            cands.append(p)
    return list(dict.fromkeys(cands))


def main() -> None:
    md_files = sorted([
        p for p in WIKI.rglob("*.md")
        if "_external/" not in str(p.relative_to(WIKI))
        and not p.name.startswith("_lint_")
    ])
    rel_files = {str(p.relative_to(WIKI)): p for p in md_files}
    all_rel = set(rel_files.keys())

    inbound = defaultdict(set)  # rel_target -> set(rel_source)
    dangling = []  # (rel_source, link_text, link_target)

    for rel, p in rel_files.items():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # markdown links
        for m in _MD_LINK_RE.finditer(text):
            lt = m.group(2).split("#", 1)[0].strip()
            if not lt or lt.startswith(("http://", "https://", "mailto:")):
                continue
            target_abs = (p.parent / lt).resolve()
            try:
                target_rel = str(target_abs.relative_to(WIKI))
            except ValueError:
                continue
            if target_rel in all_rel:
                inbound[target_rel].add(rel)
            else:
                # only flag .md misses
                if lt.endswith(".md") or "/" in lt:
                    dangling.append((rel, m.group(1), lt))
        # wikilinks
        for m in _WIKILINK_RE.finditer(text):
            slug = m.group(1)
            cands = slug_to_candidates(slug, all_rel)
            if not cands:
                dangling.append((rel, slug, f"[[{slug}]] (unresolved)"))
            else:
                for c in cands:
                    inbound[c].add(rel)

    # Orphans: not in inbound + not exempt
    orphans = []
    for rel in sorted(all_rel):
        if is_exempt(rel):
            continue
        if not inbound.get(rel):
            orphans.append(rel)

    # Stale: techniques/* with no Seen-in-the-wild entry in last 180 days
    now = dt.datetime.now(dt.timezone.utc).date()
    stale = []
    seen_re = re.compile(r"\{date:\s*(\d{4}-\d{2}-\d{2})")
    for rel, p in rel_files.items():
        if "techniques/" not in rel:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        dates = seen_re.findall(text)
        if not dates:
            continue  # no seen-in-wild yet; not stale, just unused
        try:
            latest = max(dt.date.fromisoformat(d) for d in dates)
        except ValueError:
            continue
        age = (now - latest).days
        if age > STALE_THRESHOLD_DAYS:
            stale.append((rel, latest.isoformat(), age))

    today = now.isoformat()
    report = WIKI / f"_lint_{today.replace('-', '')}.md"

    lines = []
    lines.append(f"# Wiki lint -- {today}\n")
    lines.append(f"Total pages: {len(all_rel)}\n")
    lines.append(f"Orphans: {len(orphans)}")
    lines.append(f"Dangling links: {len(dangling)}")
    lines.append(f"Stale techniques: {len(stale)}\n")

    lines.append(f"## Orphans ({len(orphans)})\n")
    if orphans:
        lines.append("Pages with zero inbound markdown / wikilink references.\n")
        for o in orphans:
            lines.append(f"- {o}")
    else:
        lines.append("None.")
    lines.append("")

    lines.append(f"## Dangling links ({len(dangling)})\n")
    if dangling:
        # Group by source page
        by_src = defaultdict(list)
        for src, txt, tgt in dangling:
            by_src[src].append((txt, tgt))
        for src in sorted(by_src):
            lines.append(f"- {src}")
            for txt, tgt in by_src[src][:5]:
                lines.append(f"  - {tgt}  ({txt!r})")
            if len(by_src[src]) > 5:
                lines.append(f"  - ... +{len(by_src[src]) - 5} more")
    else:
        lines.append("None.")
    lines.append("")

    lines.append(f"## Stale techniques ({len(stale)})\n")
    if stale:
        lines.append("Pages with no Seen-in-the-wild entry in > "
                     f"{STALE_THRESHOLD_DAYS} days.\n")
        for rel, last, age in sorted(stale, key=lambda x: -x[2])[:50]:
            lines.append(f"- {rel} -- last {last} ({age}d)")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Contradictions (skipped)\n")
    lines.append(
        "Contradiction detection requires LLM judge calls and was skipped "
        "this run per CLAUDE.md API-key whitelist. Structural lint only.\n"
    )

    report.write_text("\n".join(lines))
    print(f"wrote {report.relative_to(REPO)}")
    print(f"orphans={len(orphans)} dangling={len(dangling)} stale={len(stale)}")


if __name__ == "__main__":
    main()
