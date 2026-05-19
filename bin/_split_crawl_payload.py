"""Split firecrawl_crawl JSON payload into per-URL markdown files under wiki/sources/blogs/<src>/."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("/Users/soural/Documents/TLX/wiki/sources/blogs")


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:120] or "untitled"


def derive_slug(url: str) -> str:
    p = urlparse(url)
    path = p.path.strip("/")
    # strip trailing .html or .htm
    path = re.sub(r"\.html?$", "", path)
    path = path.replace("/", "-")
    return slugify(path)


def split(payload_path: str, source: str, url_filter=None) -> tuple[int, int]:
    obj = json.loads(Path(payload_path).read_text())
    out_dir = ROOT / source
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
        if url_filter and not url_filter(url):
            skipped += 1
            continue
        # skip if mostly navigation (< 500 chars body)
        if len(md.strip()) < 500:
            skipped += 1
            continue
        title = (meta.get("title") or meta.get("ogTitle") or "").strip()
        title = re.sub(r"\s+", " ", title)
        published = meta.get("article:published_time") or meta.get("publishedTime") or ""
        author = meta.get("author") or ""
        description = (meta.get("ogDescription") or meta.get("description") or "").strip()
        description = re.sub(r"\s+", " ", description)[:400]
        slug = derive_slug(url)
        out = out_dir / f"{slug}.md"
        front = [
            "---",
            f"source: {source}",
            f"source_url: {url}",
            f'title: "{title.replace(chr(34), chr(39))}"',
        ]
        if author:
            front.append(f'author: "{author.replace(chr(34), chr(39))}"')
        if published:
            front.append(f"published: {published}")
        if description:
            front.append(f'description: "{description.replace(chr(34), chr(39))}"')
        front.append("---")
        out.write_text("\n".join(front) + "\n\n" + md)
        written += 1
    return written, skipped


def main():
    base = "/Users/soural/.claude/projects/-Users-soural-Documents-TLX/4f0958b7-b52d-4681-93eb-d27b55cbeab0/tool-results"

    jobs = [
        (
            f"{base}/mcp-firecrawl-firecrawl_crawl-1779179987248.txt",
            "detectify",
            lambda u: "labs.detectify.com" in u
            and any(x in u for x in ["/writeups/", "/ethical-hacking/", "/how-to/", "/security-guidance/"]),
        ),
        (
            f"{base}/mcp-firecrawl-firecrawl_crawl-1779180125552.txt",
            "p0",
            lambda u: "projectzero.google" in u and re.search(r"/\d{4}/\d{2}/", u),
        ),
        (
            f"{base}/mcp-firecrawl-firecrawl_crawl-1779180370936.txt",
            "bughunters",
            lambda u: "bughunters.google.com/blog/" in u
            and not u.rstrip("/").endswith("/blog"),
        ),
    ]
    for path, src, flt in jobs:
        if not Path(path).exists():
            print(f"SKIP missing: {path}")
            continue
        w, s = split(path, src, flt)
        print(f"{src}: wrote={w} skipped={s}")


if __name__ == "__main__":
    main()
