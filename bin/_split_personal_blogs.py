"""Generic per-source splitter for firecrawl_crawl payloads of personal/research blogs.

Reads a hard-coded list of (payload_file, source_slug, host_filter) and writes
clean per-URL markdown under wiki/sources/blogs/personal/<source_slug>/.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("/Users/soural/Documents/TLX/wiki/sources/blogs/personal")
RESULTS = Path("/Users/soural/.claude/projects/-Users-soural-Documents-TLX/4f0958b7-b52d-4681-93eb-d27b55cbeab0/tool-results")

# (payload_filename, source_slug, host_substr_filter)
JOBS = [
    ("mcp-firecrawl-firecrawl_crawl-1779181753376.txt", "portswigger-research", "portswigger.net/research"),
    ("mcp-firecrawl-firecrawl_crawl-1779182002309.txt", "embracethered", "embracethered.com"),
    ("mcp-firecrawl-firecrawl_crawl-1779182134412.txt", "assetnote", "blog.assetnote.io"),
    ("mcp-firecrawl-firecrawl_crawl-1779182227899.txt", "orange-tsai", "blog.orange.tw"),
    ("mcp-firecrawl-firecrawl_crawl-1779182336955.txt", "zlz-buerhaus", "buer.haus"),
    ("mcp-firecrawl-firecrawl_crawl-1779182371158.txt", "sam-curry", "samcurry.net"),
    ("mcp-firecrawl-firecrawl_crawl-1779182511136.txt", "kevin-mizu", "mizu.re"),
    ("mcp-firecrawl-firecrawl_crawl-1779182582413.txt", "securitum-research", "securitum.com"),
    ("mcp-firecrawl-firecrawl_crawl-1779182666089.txt", "spaceraccoon", "spaceraccoon.dev"),
    ("mcp-firecrawl-firecrawl_crawl-1779182706425.txt", "oversecured", "oversecured.com"),
]


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")[:120] or "untitled"


def derive_slug(url: str) -> str:
    p = urlparse(url)
    path = p.path.strip("/").rstrip("/")
    path = re.sub(r"\.html?$", "", path)
    path = path.replace("/", "-")
    return slugify(path) or "index"


def is_listing(url: str, md: str) -> bool:
    """Skip tag/category/page-N navigation indexes."""
    if re.search(r"/(page|tag|category|tags|categories|archive)/", url, re.I):
        return True
    if re.search(r"[?&](page|paged|p)=\d+", url):
        return True
    if len(md.strip()) < 500:
        return True
    return False


def split(payload_path: Path, slug: str, host_filter: str) -> tuple[int, int]:
    obj = json.loads(payload_path.read_text())
    out_dir = ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    for item in obj.get("data", []):
        meta = item.get("metadata", {}) or {}
        url = meta.get("sourceURL") or meta.get("url") or meta.get("og:url")
        md = item.get("markdown") or ""
        if not url or not md:
            skipped += 1
            continue
        if host_filter not in url:
            skipped += 1
            continue
        if is_listing(url, md):
            skipped += 1
            continue
        title = (meta.get("title") or meta.get("ogTitle") or "").strip()
        title = re.sub(r"\s+", " ", title)
        published = meta.get("article:published_time") or meta.get("publishedTime") or ""
        author = meta.get("author") or meta.get("article:author") or ""
        description = (meta.get("ogDescription") or meta.get("description") or "").strip()
        description = re.sub(r"\s+", " ", description)[:400]
        post_slug = derive_slug(url)
        out = out_dir / f"{post_slug}.md"
        front = [
            "---",
            f"source: {slug}",
            f"source_url: {url}",
            f'title: "{title.replace(chr(34), chr(39))}"',
        ]
        if author:
            front.append(f'author: "{str(author).replace(chr(34), chr(39))}"')
        if published:
            front.append(f"published: {published}")
        if description:
            front.append(f'description: "{description.replace(chr(34), chr(39))}"')
        front.append("---")
        out.write_text("\n".join(front) + "\n\n" + md)
        written += 1
    return written, skipped


def main():
    total_w = 0
    total_s = 0
    for fname, slug, host in JOBS:
        path = RESULTS / fname
        if not path.exists():
            print(f"SKIP missing: {path}")
            continue
        w, s = split(path, slug, host)
        print(f"{slug:25} files={w} skipped={s}")
        total_w += w
        total_s += s
    print(f"TOTAL: files={total_w} skipped={total_s}")


if __name__ == "__main__":
    main()
