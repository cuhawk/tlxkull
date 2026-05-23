#!/usr/bin/env python3
"""Dashboard walk (v0.2 minimal): visit per-platform program-list pages
using injected session cookies, snapshot HTML for diff.

Two jobs:
  1. New-program detection: diff snapshot HTML against
     known_programs/<platform>_<utc>.html.
  2. Scope drift: per existing `targets/<slug>/`, fetch program detail
     page and diff against `targets/<slug>/http.md`.

v0.2 limits: HTML snapshot only. Per-platform DOM parsers + scope-diff
arrive in v0.3. Existing run produces a runtime artifact tree under
runtime/<utc>/ for visual review.

Usage:
    python3 dashboard_walk.py                 # all platforms
    python3 dashboard_walk.py --platform h1   # one
    python3 dashboard_walk.py --dry-run       # log only, no fetch
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROUTINE_DIR = Path(__file__).resolve().parent
COOKIES_DIR = ROUTINE_DIR / "cookies"
RUNTIME_DIR = ROUTINE_DIR / "runtime"
LOG = ROUTINE_DIR / "_log.jsonl"

PLATFORMS = {
    "hackerone": {
        "cookie_file": "hackerone.json",
        "dashboard_urls": [
            "https://hackerone.com/invitations",
            "https://hackerone.com/opportunities/all/search?type=team",
        ],
        "selector_program_links": "a[href^='/'][data-testid*='program']",
    },
    "intigriti": {
        "cookie_file": "intigriti.json",
        "dashboard_urls": [
            "https://app.intigriti.com/researcher/programs",
        ],
        "selector_program_links": "a[href*='/researcher/programs/']",
    },
    "bugcrowd": {
        "cookie_file": "bugcrowd.json",
        "dashboard_urls": [
            "https://bugcrowd.com/user/dashboard/engagements",
        ],
        "selector_program_links": "a[href^='/engagements/']",
    },
    "synack": {
        "cookie_file": "synack.json",
        "dashboard_urls": [
            "https://platform.synack.com/targets",
        ],
        "selector_program_links": "[data-testid*='target']",
    },
}


def log(record: dict) -> None:
    record = {"ts": datetime.now(timezone.utc).isoformat(),
              "skill": "dashboard_walk", **record}
    print(json.dumps(record))
    with open(LOG, "a") as f:
        f.write(json.dumps(record) + "\n")


def load_cookies(cookie_file: Path) -> list[dict]:
    """Load + normalize Cookie-Editor JSON for playwright."""
    if not cookie_file.exists():
        return []
    cookies = json.loads(cookie_file.read_text())
    normalized = []
    now = time.time()
    for c in cookies:
        domain = c.get("domain") or ""
        if not domain:
            continue
        if c.get("expirationDate", float("inf")) < now:
            continue
        normalized.append({
            "name": c["name"],
            "value": c["value"],
            "domain": domain,
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "sameSite": {"no_restriction": "None", "lax": "Lax",
                         "strict": "Strict"}.get(
                             c.get("sameSite", "lax"), "Lax"),
        })
    return normalized


def walk_platform(platform: str, cfg: dict, out_dir: Path,
                  dry_run: bool) -> dict:
    cookie_file = COOKIES_DIR / cfg["cookie_file"]
    cookies = load_cookies(cookie_file)
    if not cookies:
        return {"platform": platform, "action": "skipped_no_cookies",
                "cookie_file": str(cookie_file)}

    if dry_run:
        return {"platform": platform, "action": "dry_run",
                "would_fetch": cfg["dashboard_urls"],
                "cookie_count": len(cookies)}

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"platform": platform, "action": "playwright_missing",
                "hint": "pip install playwright && playwright install chromium"}

    plat_dir = out_dir / platform
    plat_dir.mkdir(parents=True, exist_ok=True)
    snapshots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        ctx.add_cookies(cookies)
        for url in cfg["dashboard_urls"]:
            page = ctx.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=30_000)
                html = page.content()
                fname = url.rsplit("/", 1)[-1].split("?", 1)[0] or "index"
                snap = plat_dir / f"{fname}.html"
                snap.write_text(html)
                snapshots.append({"url": url, "snapshot": str(snap),
                                  "size": len(html)})
            except Exception as exc:
                snapshots.append({"url": url, "error": str(exc)})
            finally:
                page.close()
        browser.close()

    return {"platform": platform, "action": "snapshot_taken",
            "snapshots": snapshots}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=list(PLATFORMS),
                    help="only this platform (default: all)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = RUNTIME_DIR / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    platforms = [args.platform] if args.platform else list(PLATFORMS)
    results = []
    for plat in platforms:
        try:
            res = walk_platform(plat, PLATFORMS[plat], out_dir, args.dry_run)
        except Exception as exc:
            res = {"platform": plat, "action": "error",
                   "error": f"{type(exc).__name__}: {exc}"}
        log(res)
        results.append(res)

    summary = {"action": "summary", "results": results,
               "out_dir": str(out_dir)}
    log(summary)


if __name__ == "__main__":
    main()
