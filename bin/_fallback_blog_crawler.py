"""Firecrawl-free fallback crawler for the 22 personal blogs queued in
wiki/sources/blogs/_pending_crawls.md.

For each blog:
  1. Try sitemap.xml + sitemap_index.xml + feed.xml/atom.xml/index.xml to
     enumerate post URLs.
  2. Fallback: scrape index page, take internal links that look like posts
     (path depth >= 1, no obvious nav/tag/category in URL).
  3. Fetch each post; run trafilatura.extract(..., output_format='markdown',
     include_links=True, include_images=False) to get clean body.
  4. Write `wiki/sources/blogs/personal/<slug>/<post-slug>.md` with
     frontmatter (source/source_url/title/published/description).

Polite: per-host 0.5s sleep, global ThreadPool concurrency 6, total cap of
80 posts per blog.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    import trafilatura
    from trafilatura.settings import use_config
except ImportError:
    print("trafilatura missing — install via: uv pip install --python tlx/.venv/bin/python trafilatura markdownify")
    sys.exit(2)

ROOT = Path("/Users/soural/Documents/TLX/wiki/sources/blogs/personal")
ROOT.mkdir(parents=True, exist_ok=True)

UA = "Mozilla/5.0 (compatible; TLX-wiki-ingest/1.0; +https://github.com/soural)"
HEADERS = {"User-Agent": UA, "Accept": "*/*"}
PER_BLOG_LIMIT = 80
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 25

# (root_url, slug, optional URL-allow regex)
BLOGS: list[tuple[str, str, str | None]] = [
    ("https://garethheyes.co.uk", "gareth-heyes", None),
    ("https://jameskettle.com", "james-kettle", None),
    ("https://danielmiessler.com", "daniel-miessler", r"/blog/"),
    ("https://josephthacker.com", "rez0-thacker", None),
    ("https://corben.io", "corben-leo", None),
    ("https://galnagli.com", "gal-nagli", None),
    ("https://joaxcar.com", "johan-carlsson", None),
    ("https://matanber.com", "matanber", None),
    ("https://nickcopi.site", "nick-copi", None),
    ("https://inti.io", "inti", None),
    ("https://avlidienbrunn.se", "mathias-karlsson", None),
    ("https://fromdayzerotozeroday.com", "spaceraccoon-book", None),
    ("https://blog.slonser.info", "slonser", None),
    ("https://blog.ajxchapman.com", "alex-chapman", None),
    ("https://cspbypass.com", "renniepak-csp", None),
    ("https://blog.long.lat", "daniel-thatcher", None),
    ("https://brownfinesecurity.com", "matt-brown", None),
    ("https://blog.jr0ch17.com", "jr0ch17", None),
    ("https://blog.erbbysam.com", "sam-erb", None),
    ("https://dday.us", "douglas-day", None),
    ("https://naglinagli.github.io", "naglinagli-gh", None),
    ("https://cablej.io", "jack-cable", None),
]

NAV_RE = re.compile(
    r"(/tag/|/tags/|/category/|/categories/|/author/|/authors/|/page/\d|/feed|"
    r"/rss|/index\.xml|/sitemap|/about|/contact|/login|/signup|/search|/archive|"
    r"\.xml$|\.json$|\.css$|\.js$|\.png$|\.jpg$|\.jpeg$|\.gif$|\.svg$|\.pdf$|"
    r"\.ico$|\.webp$|#)",
    re.I,
)


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


def fetch(url: str, expect_xml: bool = False) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), allow_redirects=True)
        if r.status_code >= 400:
            return None
        return r.text
    except Exception:
        return None


def urls_from_sitemap(host: str) -> list[str]:
    out: list[str] = []
    for path in ("/sitemap.xml", "/sitemap_index.xml", "/sitemap-posts.xml", "/sitemap-1.xml"):
        body = fetch(host.rstrip("/") + path, expect_xml=True)
        if not body:
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            continue
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        # sitemapindex → recurse
        for sm in root.findall("sm:sitemap", ns):
            loc = sm.findtext("sm:loc", default="", namespaces=ns).strip()
            if loc:
                inner = fetch(loc, expect_xml=True)
                if inner:
                    try:
                        ir = ET.fromstring(inner)
                        for u in ir.findall("sm:url", ns):
                            lo = u.findtext("sm:loc", default="", namespaces=ns).strip()
                            if lo:
                                out.append(lo)
                    except ET.ParseError:
                        pass
        for u in root.findall("sm:url", ns):
            lo = u.findtext("sm:loc", default="", namespaces=ns).strip()
            if lo:
                out.append(lo)
        if out:
            return out
    return out


def urls_from_feed(host: str) -> list[str]:
    out: list[str] = []
    for path in ("/feed.xml", "/atom.xml", "/feed/", "/index.xml", "/rss.xml", "/feed"):
        body = fetch(host.rstrip("/") + path, expect_xml=True)
        if not body:
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            continue
        # Atom
        for ent in root.iter():
            if ent.tag.endswith("}entry") or ent.tag == "entry":
                for child in ent.iter():
                    if child.tag.endswith("}link") or child.tag == "link":
                        href = child.attrib.get("href") or ""
                        if href:
                            out.append(href)
                            break
            elif ent.tag.endswith("}item") or ent.tag == "item":
                for child in ent.iter():
                    if child.tag.endswith("}link") or child.tag == "link":
                        if child.text:
                            out.append(child.text.strip())
                            break
        if out:
            return out
    return out


def urls_from_index(host: str) -> list[str]:
    html = fetch(host)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    host_netloc = urlparse(host).netloc
    out = []
    for a in soup.find_all("a", href=True):
        absu = urljoin(host, a["href"])
        p = urlparse(absu)
        if p.netloc != host_netloc:
            continue
        if NAV_RE.search(absu):
            continue
        if absu.rstrip("/") == host.rstrip("/"):
            continue
        out.append(absu.split("#", 1)[0])
    return out


def discover(host: str, allow_re: str | None) -> list[str]:
    cands: list[str] = []
    for fn in (urls_from_sitemap, urls_from_feed, urls_from_index):
        cands = fn(host)
        if cands:
            break
    # filter by allow_re + dedupe + same host + drop trailing slashes + nav
    host_netloc = urlparse(host).netloc
    seen: set[str] = set()
    out: list[str] = []
    pat = re.compile(allow_re) if allow_re else None
    for u in cands:
        u2 = u.split("#", 1)[0].rstrip("/")
        if u2 in seen:
            continue
        seen.add(u2)
        if urlparse(u2).netloc != host_netloc:
            continue
        if NAV_RE.search(u2):
            continue
        if pat and not pat.search(u2):
            continue
        if u2.rstrip("/") == host.rstrip("/"):
            continue
        out.append(u2)
    return out[:PER_BLOG_LIMIT]


def extract_meta_html(html: str) -> tuple[str, str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.text.strip() if soup.title else "").strip()
    desc = ""
    pub = ""
    for tag in soup.find_all("meta"):
        name = (tag.get("name") or tag.get("property") or "").lower()
        c = (tag.get("content") or "").strip()
        if not c:
            continue
        if name in ("og:description", "twitter:description", "description"):
            desc = desc or c
        if name in ("article:published_time", "datepublished", "publication_date", "og:updated_time"):
            pub = pub or c
    return title, desc, pub


def scrape_post(url: str, slug_dir: Path, source_slug: str) -> bool:
    html = fetch(url)
    if not html or len(html) < 500:
        return False
    md = trafilatura.extract(
        html,
        output_format="markdown",
        include_links=True,
        include_images=False,
        include_comments=False,
        favor_precision=True,
    )
    if not md or len(md.strip()) < 400:
        return False
    title, desc, pub = extract_meta_html(html)
    post_slug = derive_slug(url)
    out = slug_dir / f"{post_slug}.md"
    front = [
        "---",
        f"source: {source_slug}",
        f"source_url: {url}",
        f'title: "{re.sub(r"\\s+", " ", title).replace(chr(34), chr(39))}"',
    ]
    if pub:
        front.append(f"published: {pub}")
    if desc:
        front.append(f'description: "{re.sub(r"\\s+", " ", desc)[:400].replace(chr(34), chr(39))}"')
    front.append("---")
    out.write_text("\n".join(front) + "\n\n" + md)
    return True


def crawl_one(host: str, slug: str, allow_re: str | None) -> dict:
    print(f"[{slug}] discover urls...", flush=True)
    urls = discover(host, allow_re)
    print(f"[{slug}] discovered {len(urls)} candidate posts", flush=True)
    out_dir = ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    failed = 0
    for u in urls:
        ok = scrape_post(u, out_dir, slug)
        if ok:
            written += 1
        else:
            failed += 1
        time.sleep(0.4)
    print(f"[{slug}] wrote={written} failed={failed}", flush=True)
    return {"slug": slug, "host": host, "discovered": len(urls), "written": written, "failed": failed}


def main():
    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(crawl_one, h, s, a) for (h, s, a) in BLOGS]
        for f in as_completed(futs):
            try:
                results.append(f.result())
            except Exception as exc:
                results.append({"error": str(exc)})
    Path("/tmp/fallback_crawler_results.json").write_text(json.dumps(results, indent=2))
    total_written = sum(r.get("written", 0) for r in results)
    print(f"\nDONE. total_written={total_written}")
    for r in sorted(results, key=lambda x: -x.get("written", 0)):
        print(f"  {r.get('slug',''):25} disc={r.get('discovered',0):3} wrote={r.get('written',0):3} fail={r.get('failed',0):3}")


if __name__ == "__main__":
    main()
