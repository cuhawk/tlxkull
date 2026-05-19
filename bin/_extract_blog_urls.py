"""Extract blog/personal-site URLs from wiki/people/*.md, dedupe by domain,
filter out social/profile/aggregator URLs. Emit a queue for firecrawl ingest."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

PEOPLE = Path("/Users/soural/Documents/TLX/wiki/people")

# Domains we already ingested OR that aren't blogs
SKIP_DOMAINS = {
    # already done
    "labs.detectify.com",
    "projectzero.google",
    "googleprojectzero.blogspot.com",
    "bughunters.google.com",
    "msrc.microsoft.com",
    "www.microsoft.com",  # MSRC mirror
    # social / profile / aggregator (no blog content)
    "x.com",
    "twitter.com",
    "linkedin.com",
    "www.linkedin.com",
    "github.com",
    "hackerone.com",
    "bugcrowd.com",
    "intigriti.com",
    "app.intigriti.com",
    "speakerdeck.com",
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "podcasts.apple.com",
    "open.spotify.com",
    "twitch.tv",
    "discord.com",
    "discord.gg",
    "mastodon.social",
    "infosec.exchange",
    "ctbb.show",
    "criticalthinkingpodcast.io",
    "podcast.criticalthinkingpodcast.io",
    "facebook.com",
    "instagram.com",
    "t.me",
    # paid/wall or commerce
    "leanpub.com",
    "amazon.com",
    "www.amazon.com",
    "store.steampowered.com",
    # tool/product pages (not blog corpora)
    "shift.security",  # tool
    "caido.io",
    "burp.com",
    "portswigger.net",  # has blog/research subtree — handle specially below
}

# Domains where ONLY a specific subpath holds blog/research content
PATH_PREFIX = {
    "portswigger.net": "/research",  # PortSwigger Research blog
    "blog.assetnote.io": "",
    "embracethered.com": "",
    "rhynorater.github.io": "",
    "ramimac.me": "",
    "samcurry.net": "",
    "samerb.com": "",
    "spaceraccoon.dev": "",
    "voiderror.com": "",
}

URL_RE = re.compile(r"https?://[^\s)>\"']+", re.I)
SOCIAL_PATH_HINTS = ("/@", "/in/", "/profile/", "/u/")


def is_skip(url: str) -> bool:
    p = urlparse(url)
    host = p.netloc.lower()
    if host in SKIP_DOMAINS:
        return True
    if any(h in host for h in ("hackerone.com", "bugcrowd.com", "linkedin.com", "twitter.com", "x.com")):
        return True
    if any(h in p.path.lower() for h in SOCIAL_PATH_HINTS):
        return True
    return False


def classify(url: str) -> str | None:
    """Return canonical 'site root' for crawling, or None to skip."""
    p = urlparse(url)
    host = p.netloc.lower()
    if not host:
        return None
    if is_skip(url):
        return None
    # Skip in-tree docs anchors
    if "#" in url and url.split("#", 1)[1]:
        url = url.split("#", 1)[0]
    # If host is a known research-subpath host, return host+prefix
    if host == "portswigger.net":
        return "https://portswigger.net/research"
    if host == "msrc.microsoft.com" or host == "www.microsoft.com":
        return None
    # Skip plain root paths to docs/aggregators
    if any(host.endswith(s) for s in ("anthropic.com", "openai.com", "huggingface.co")):
        return None
    return f"https://{host}"


def main():
    by_host: dict[str, dict] = {}
    for md in sorted(PEOPLE.glob("*.md")):
        if md.name.startswith("_"):
            continue
        text = md.read_text(errors="ignore")
        slug = md.stem
        for raw in URL_RE.findall(text):
            url = raw.rstrip(".,);]")
            site = classify(url)
            if not site:
                continue
            by_host.setdefault(site, {"hosts": set(), "people": set(), "sample_urls": set()})
            by_host[site]["people"].add(slug)
            by_host[site]["sample_urls"].add(url)

    out = []
    for site, info in sorted(by_host.items()):
        out.append({
            "site": site,
            "people_count": len(info["people"]),
            "people": sorted(info["people"]),
            "sample_urls": sorted(info["sample_urls"])[:5],
        })
    Path("/tmp/people_blog_queue.json").write_text(json.dumps(out, indent=2))
    # Summary
    print(f"Distinct sites: {len(out)}")
    for row in out:
        print(f"  [{row['people_count']:2}] {row['site']}  ({', '.join(row['people'][:3])}{'...' if len(row['people'])>3 else ''})")


if __name__ == "__main__":
    main()
