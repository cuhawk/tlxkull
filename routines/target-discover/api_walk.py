#!/usr/bin/env python3
"""API-driven program-list walker for H1 / Intigriti / Bugcrowd.

Replaces playwright dashboard_walk for these three platforms — hits
each platform's own JSON API with saved session cookies. Faster, no
Chrome, no playwright deps. Writes inbox/invites/<plat>/<slug>/ seeds
for new programs not yet in targets/.

Stdlib only — uses urllib.

Usage:
    python3 api_walk.py                 # all 3
    python3 api_walk.py --platform hackerone
    python3 api_walk.py --dry-run       # print discovered, write nothing
"""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROUTINE_DIR = Path(__file__).resolve().parent
COOKIES_DIR = ROUTINE_DIR / "cookies"
AUTH_DIR = ROUTINE_DIR / "auth_state"
INBOX_ROOT = ROUTINE_DIR.parents[1] / "inbox" / "invites"
TARGETS_DIR = ROUTINE_DIR.parents[1] / "targets"
LOG = ROUTINE_DIR / "_log.jsonl"

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/148.0.0.0 Safari/537.36")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def load_cookies(plat: str) -> str:
    path = COOKIES_DIR / f"{plat}.json"
    if not path.exists():
        raise FileNotFoundError(f"missing cookies for {plat}: {path}")
    cookies = json.loads(path.read_text())
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies)


def load_auth(plat: str) -> dict:
    path = AUTH_DIR / f"{plat}.json"
    if not path.exists():
        raise FileNotFoundError(f"missing auth_state for {plat}: {path}")
    return json.loads(path.read_text())


def existing_target_slugs() -> set[str]:
    if not TARGETS_DIR.exists():
        return set()
    return {p.name for p in TARGETS_DIR.iterdir() if p.is_dir()}


def request(url: str, *, method: str = "GET", headers: dict | None = None,
            body: bytes | None = None, timeout: int = 20) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, method=method,
                                 headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


# ---- HackerOne ------------------------------------------------------------

H1_QUERY = """query DiscoveryQuery($query: OpportunitiesQuery!, $filter: QueryInput!, $from: Int, $size: Int, $sort: [SortInput!], $post_filters: OpportunitiesFilterInput) {
  opportunities_search(query: $query, filter: $filter, from: $from, size: $size, sort: $sort, post_filters: $post_filters) {
    nodes {
      ... on OpportunityDocument {
        id handle name state team_type launched_at last_updated_at
        offers_bounties minimum_bounty_table_value maximum_bounty_table_value
        currency submission_state h1_clear gold_standard idv
        __typename
      }
    }
    total_count
  }
}
"""


def h1_discover(only_mine: bool = False, size: int = 50) -> list[dict]:
    auth = load_auth("hackerone")
    cookies = load_cookies("hackerone")
    payload = {
        "operationName": "DiscoveryQuery",
        "variables": {
            "size": size, "from": 0,
            "query": {},
            "filter": {"bool": {"filter": [
                {"bool": {"must_not": {"term": {"team_type": "Engagements::Assessment"}}}},
                None,
            ]}},
            "sort": [{"field": "launched_at", "direction": "DESC"}],
            "post_filters": {"my_programs": only_mine, "bookmarked": False,
                             "campaign_teams": False},
            "product_area": "opportunity_discovery",
            "product_feature": "search",
        },
        "query": H1_QUERY,
    }
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": auth["origin"],
        "referer": "https://hackerone.com/opportunities/all/search?ordering=Newest+programs",
        "user-agent": USER_AGENT,
        auth["csrf_header"]: auth["csrf_token"],
        "cookie": cookies,
        "x-product-area": "opportunity_discovery",
        "x-product-feature": "search",
    }
    status, body = request(auth["graphql_url"], method="POST",
                           headers=headers,
                           body=json.dumps(payload).encode())
    if status != 200:
        raise RuntimeError(f"H1 GraphQL {status}: {body[:300]!r}")
    data = json.loads(body)
    nodes = (data.get("data", {}) or {}).get("opportunities_search", {}).get("nodes", []) or []
    return [
        {"platform": "hackerone", "slug": f"{slugify(n['handle'])}-h1",
         "program": n["name"], "handle": n["handle"],
         "state": n.get("state"), "team_type": n.get("team_type"),
         "launched_at": n.get("launched_at"),
         "bounty_low": n.get("minimum_bounty_table_value"),
         "bounty_high": n.get("maximum_bounty_table_value"),
         "currency": n.get("currency"),
         "url": f"https://hackerone.com/{n['handle']}"}
        for n in nodes if "handle" in n
    ]


# ---- Bugcrowd -------------------------------------------------------------

def bc_discover() -> list[dict]:
    auth = load_auth("bugcrowd")
    cookies = load_cookies("bugcrowd")
    headers = {
        "accept": "application/vnd.bugcrowd.v4+json, application/json",
        "user-agent": USER_AGENT,
        "cookie": cookies,
        "referer": "https://bugcrowd.com/user/dashboard/engagements",
    }
    # Bugcrowd researcher engagements API — guess; fallback to HTML scrape if 404
    candidates = [
        "https://bugcrowd.com/engagements.json",
        "https://bugcrowd.com/user/dashboard/engagements.json",
        "https://bugcrowd.com/api/researcher/engagements",
    ]
    for url in candidates:
        status, body = request(url, headers=headers)
        if status == 200 and body.strip().startswith((b"{", b"[")):
            try:
                data = json.loads(body)
                items = data.get("engagements") or data.get("data") or data
                if isinstance(items, list):
                    out = []
                    for it in items:
                        # briefUrl = "/engagements/<code>"
                        brief = it.get("briefUrl") or ""
                        code = brief.rsplit("/", 1)[-1] if brief else (
                            it.get("code") or it.get("slug") or "")
                        if not code:
                            continue
                        out.append({"platform": "bugcrowd",
                                    "slug": f"{slugify(code)}-bc",
                                    "program": it.get("name") or "?",
                                    "tagline": it.get("tagline"),
                                    "industry": it.get("industryName"),
                                    "is_private": it.get("isPrivate"),
                                    "access_status": it.get("accessStatus"),
                                    "engagement_type": (it.get("productEngagementType") or {}).get("label"),
                                    "reward_summary": (it.get("rewardSummary") or {}).get("summary"),
                                    "url": f"https://bugcrowd.com{brief}",
                                    "_endpoint": url})
                    return out
            except json.JSONDecodeError:
                continue
    return [{"_error": "no working bc endpoint; tried", "_tried": candidates}]


# ---- Intigriti ------------------------------------------------------------

def int_discover() -> list[dict]:
    auth = load_auth("intigriti")
    cookies = load_cookies("intigriti")
    headers = {
        "accept": "application/json, text/plain, */*",
        "user-agent": USER_AGENT,
        "cookie": cookies,
        "referer": "https://app.intigriti.com/researcher",
        auth["csrf_header"]: auth["csrf_token"],
    }
    # Map Intigriti status enum to lifecycle
    STATUS_MAP = {1: "active", 2: "active", 3: "active", 4: "paused",
                  5: "retired", 6: "active"}
    for url in auth["programs_candidates"]:
        status, body = request(url, headers=headers)
        if status == 200 and body.strip().startswith((b"{", b"[")):
            try:
                data = json.loads(body)
                items = data if isinstance(data, list) else (
                    data.get("data") or data.get("items") or [])
                if not isinstance(items, list):
                    continue
                out = []
                for it in items:
                    ch = it.get("companyHandle") or ""
                    h = it.get("handle") or ""
                    if not (ch and h):
                        continue
                    out.append({"platform": "intigriti",
                                "slug": f"{slugify(h)}-intigriti",
                                "program": it.get("name"),
                                "company": it.get("companyName"),
                                "company_handle": ch, "handle": h,
                                "industry": it.get("industry"),
                                "status_code": it.get("status"),
                                "lifecycle_hint": STATUS_MAP.get(it.get("status"), "active"),
                                "bounty_low": (it.get("minBounty") or {}).get("value"),
                                "bounty_high": (it.get("maxBounty") or {}).get("value"),
                                "currency": it.get("currency"),
                                "two_factor_required": it.get("twoFactorRequired"),
                                "allow_collaboration": it.get("allowCollaboration"),
                                "asset_types": [a["name"] for a in it.get("assetTypes", [])],
                                "invite_accepted_at": it.get("inviteAcceptedAt"),
                                "launched_at": it.get("launchedAt"),
                                "url": f"https://app.intigriti.com/researcher/programs/{ch}/{h}/detail",
                                "_endpoint": url})
                return out
            except json.JSONDecodeError:
                continue
    return [{"_error": "no working intigriti endpoint; tried",
             "_tried": auth["programs_candidates"]}]


# ---- main -----------------------------------------------------------------

def log(record: dict) -> None:
    record = {"ts": datetime.now(timezone.utc).isoformat(),
              "skill": "api_walk", **record}
    print(json.dumps(record, default=str))
    with open(LOG, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def write_seed(item: dict, dry_run: bool, existing: set[str]) -> str:
    slug = item.get("slug")
    plat = item.get("platform")
    if not slug or not plat:
        return "unparsed"
    out_dir = INBOX_ROOT / plat / slug
    if out_dir.exists():
        return "already_in_inbox"
    if slug in existing:
        action = "duplicate"
    else:
        action = "created"
    if dry_run:
        return action
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "channel": "api_walk", **item,
        "lifecycle": "active" if action == "created" else "duplicate",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    marker = "DUPLICATE" if action == "duplicate" else "READY"
    (out_dir / marker).write_text(meta["discovered_at"])
    return action


PLATFORMS = {"hackerone": h1_discover, "bugcrowd": bc_discover,
             "intigriti": int_discover}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=list(PLATFORMS))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    targets = [args.platform] if args.platform else list(PLATFORMS)
    existing = existing_target_slugs()
    summary = {"platforms": {}}
    for plat in targets:
        try:
            items = PLATFORMS[plat]()
        except Exception as exc:
            log({"platform": plat, "error": f"{type(exc).__name__}: {exc}"})
            summary["platforms"][plat] = {"error": str(exc)}
            continue
        counts = {"created": 0, "duplicate": 0, "already_in_inbox": 0,
                  "unparsed": 0}
        samples = []
        for it in items[:5]:
            samples.append({"slug": it.get("slug"),
                            "program": it.get("program")})
        for it in items:
            counts[write_seed(it, args.dry_run, existing)] += 1
        summary["platforms"][plat] = {**counts, "total": len(items),
                                       "sample": samples}
        log({"platform": plat, "found": len(items), **counts})
    log({"summary": summary, "dry_run": args.dry_run})


if __name__ == "__main__":
    main()
