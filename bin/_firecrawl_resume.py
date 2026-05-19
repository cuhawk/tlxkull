"""Resume firecrawl crawls for the 11 personal blogs still uncovered after
the firecrawl-credit interruption + fallback-crawler partial run.

Uses Firecrawl v2 HTTP API directly (avoids the 3 req/min MCP cap; works
around tool-output size limits by streaming straight to disk).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

API_KEY = "fc-e4e746b14d83419dafc6cb831099a0a4"
API = "https://api.firecrawl.dev/v2"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

ROOT = Path("/Users/soural/Documents/TLX/wiki/sources/blogs/personal")
ROOT.mkdir(parents=True, exist_ok=True)

# (host_url, source_slug, optional includePaths regex list)
JOBS = [
    ("https://joaxcar.com", "johan-carlsson", None),
    ("https://matanber.com", "matanber", None),
    ("https://nickcopi.site", "nick-copi", None),
    ("https://avlidienbrunn.se", "mathias-karlsson", None),
    ("https://fromdayzerotozeroday.com", "spaceraccoon-book", None),
    ("https://cspbypass.com", "renniepak-csp", None),
    ("https://blog.long.lat", "daniel-thatcher", None),
    ("https://blog.jr0ch17.com", "jr0ch17", None),
    ("https://dday.us", "douglas-day", None),
    ("https://naglinagli.github.io", "naglinagli-gh", None),
    ("https://cablej.io", "jack-cable", None),
    # Kettle's old personal blog still publishes occasional posts:
    ("https://www.skeletonscribe.net", "skeletonscribe-kettle", None),
    # Heyes' old blog:
    ("https://www.thespanner.co.uk", "thespanner-heyes", None),
    # gal-nagli secondary site:
    ("https://galnagli.com", "gal-nagli", None),
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


def start_crawl(host: str, include_paths: list[str] | None) -> str | None:
    body = {
        "url": host,
        "limit": 80,
        "maxDiscoveryDepth": 4,
        "deduplicateSimilarURLs": True,
        "ignoreQueryParameters": True,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
    }
    if include_paths:
        body["includePaths"] = include_paths
    for attempt in range(6):
        r = requests.post(f"{API}/crawl", json=body, headers=HEADERS, timeout=30)
        if r.status_code == 429:
            try:
                msg = r.json().get("error", "")
            except Exception:
                msg = r.text
            m = re.search(r"retry after (\d+)", msg)
            wait = int(m.group(1)) + 3 if m else 30
            print(f"  RATE-LIMIT {host} sleeping {wait}s (attempt {attempt+1})", flush=True)
            time.sleep(wait)
            continue
        if r.status_code >= 400:
            print(f"  START FAIL {host}: {r.status_code} {r.text[:300]}", flush=True)
            return None
        data = r.json()
        return data.get("id") or data.get("jobId")
    print(f"  START GAVE UP {host} after 6 retries", flush=True)
    return None


def poll(job_id: str, max_wait: int = 600) -> dict | None:
    start = time.time()
    next_cursor: str | None = None
    out_docs: list[dict] = []
    status_url_base = f"{API}/crawl/{job_id}"
    while True:
        url = status_url_base if not next_cursor else next_cursor
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code >= 400:
            print(f"  POLL FAIL {job_id}: {r.status_code} {r.text[:300]}", flush=True)
            return None
        d = r.json()
        out_docs.extend(d.get("data", []))
        status = d.get("status")
        next_cursor = d.get("next")
        if status == "completed":
            return {"status": "completed", "completed": d.get("completed"), "total": d.get("total"), "data": out_docs}
        if status in ("failed", "cancelled"):
            return {"status": status, "error": d.get("error"), "data": out_docs}
        if time.time() - start > max_wait:
            return {"status": "timeout", "data": out_docs}
        if next_cursor is None:
            # poll same URL after sleep
            pass
        time.sleep(5)


def write_post(doc: dict, source_slug: str, host_filter: str | None = None) -> bool:
    meta = doc.get("metadata", {}) or {}
    url = meta.get("sourceURL") or meta.get("url") or meta.get("og:url")
    md = doc.get("markdown") or ""
    if not url or not md:
        return False
    if host_filter and host_filter not in url:
        return False
    if len(md.strip()) < 500:
        return False
    if re.search(r"/(tag|tags|category|categories|page|archive|author)/", url, re.I):
        return False
    out_dir = ROOT / source_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    title = (meta.get("title") or meta.get("ogTitle") or "").strip()
    title = re.sub(r"\s+", " ", title).replace('"', "'")
    pub = meta.get("article:published_time") or meta.get("publishedTime") or ""
    desc = (meta.get("ogDescription") or meta.get("description") or "").strip()
    desc = re.sub(r"\s+", " ", desc)[:400].replace('"', "'")
    post_slug = derive_slug(url)
    out = out_dir / f"{post_slug}.md"
    front = [
        "---",
        f"source: {source_slug}",
        f"source_url: {url}",
        f'title: "{title}"',
    ]
    if pub:
        front.append(f"published: {pub}")
    if desc:
        front.append(f'description: "{desc}"')
    front.append("---")
    out.write_text("\n".join(front) + "\n\n" + md)
    return True


def main():
    results = []
    for host, slug, include in JOBS:
        out_dir = ROOT / slug
        existing = list(out_dir.glob("*.md")) if out_dir.exists() else []
        if len(existing) >= 3:
            print(f"[{slug}] SKIP (already has {len(existing)} posts)", flush=True)
            continue
        print(f"[{slug}] starting crawl {host}", flush=True)
        jid = start_crawl(host, include)
        if not jid:
            results.append({"slug": slug, "host": host, "error": "start_failed"})
            continue
        res = poll(jid, max_wait=900)
        if not res:
            results.append({"slug": slug, "host": host, "error": "poll_failed"})
            continue
        docs = res.get("data", [])
        host_filter = urlparse(host).netloc
        wrote = sum(1 for d in docs if write_post(d, slug, host_filter))
        skipped = len(docs) - wrote
        print(f"[{slug}] status={res.get('status')} docs={len(docs)} wrote={wrote} skipped={skipped}", flush=True)
        results.append({"slug": slug, "host": host, "status": res.get("status"), "docs": len(docs), "wrote": wrote, "skipped": skipped})
        # Polite pause between crawls
        time.sleep(3)
    Path("/tmp/firecrawl_resume_results.json").write_text(json.dumps(results, indent=2))
    total = sum(r.get("wrote", 0) for r in results)
    print(f"\nDONE. total_wrote={total}")
    for r in sorted(results, key=lambda x: -x.get("wrote", 0)):
        print(f"  {r.get('slug',''):25} wrote={r.get('wrote', '-'):>3} docs={r.get('docs','-'):>3} status={r.get('status','err')}")


if __name__ == "__main__":
    main()
