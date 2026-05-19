"""Split MSRC crawl payload, filtering out pure announcement posts (Patch Tuesday notes,
MVR recognition, quest-award PR, etc.) so only technical/research posts land in wiki."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("/Users/soural/Documents/TLX/wiki/sources/blogs/msrc")
ROOT.mkdir(parents=True, exist_ok=True)


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")[:120] or "untitled"


def derive_slug(url: str) -> str:
    p = urlparse(url)
    path = p.path.strip("/")
    path = re.sub(r"^en-us-msrc-blog-", "", path.replace("/", "-"))
    return slugify(path)


ANNOUNCEMENT_PATTERNS = [
    r"congratulations-to-the-",
    r"-most-valuable-security-researchers",
    r"-top-msrc-\d{4}-q\d-security-researchers",
    r"a-note-on-patch-tuesday",
    r"submit-your-research-bluehat-call-for-papers",
    r"from-arcades-to-azure",
    r"from-first-report-to-mvr",
    r"research-never-stops",
    r"asem-eleraky",
    r"strengthening-secure-software-global-scale",
    r"in-scope-by-default",
    r"zero-day-quest-\d{4}",
    r"awarded-for-vulnerability-research",
]
ANNOUNCEMENT_RE = re.compile("|".join(ANNOUNCEMENT_PATTERNS), re.I)


def is_announcement(url: str, md: str) -> bool:
    if ANNOUNCEMENT_RE.search(url):
        return True
    # Short bodies = likely announcements
    if len(md.strip()) < 1500:
        return True
    return False


def split(payload_path: str) -> tuple[int, int]:
    obj = json.loads(Path(payload_path).read_text())
    written = 0
    skipped = 0
    for item in obj.get("data", []):
        meta = item.get("metadata", {}) or {}
        url = meta.get("sourceURL") or meta.get("url")
        md = item.get("markdown") or ""
        if not url or not md:
            skipped += 1
            continue
        if is_announcement(url, md):
            skipped += 1
            continue
        title = (meta.get("title") or meta.get("ogTitle") or "").strip()
        title = re.sub(r"\s+", " ", title)
        published = meta.get("article:published_time") or meta.get("publishedTime") or ""
        description = (meta.get("ogDescription") or meta.get("description") or "").strip()
        description = re.sub(r"\s+", " ", description)[:400]
        slug = derive_slug(url)
        out = ROOT / f"{slug}.md"
        front = [
            "---",
            "source: msrc",
            f"source_url: {url}",
            f'title: "{title.replace(chr(34), chr(39))}"',
        ]
        if published:
            front.append(f"published: {published}")
        if description:
            front.append(f'description: "{description.replace(chr(34), chr(39))}"')
        front.append("---")
        out.write_text("\n".join(front) + "\n\n" + md)
        written += 1
    return written, skipped


if __name__ == "__main__":
    p = "/Users/soural/.claude/projects/-Users-soural-Documents-TLX/4f0958b7-b52d-4681-93eb-d27b55cbeab0/tool-results/mcp-firecrawl-firecrawl_crawl-1779180691809.txt"
    w, s = split(p)
    print(f"msrc: wrote={w} skipped={s}")
