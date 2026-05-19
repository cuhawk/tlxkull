#!/usr/bin/env python3
"""
h1-hacktivity-fetch.py — Fetch HackerOne Hacktivity into wiki/sources/hacktivity/

H1's Hacktivity uses the `HacktivitySearchQuery` GraphQL operation on the
`search(index: CompleteHacktivityReportIndex, ...)` field with an
Elasticsearch-style query string. The endpoint requires a valid session cookie
(HttpOnly — not extractable by JS) plus a CSRF token.

TWO MODES:

  1. Browser-cookie mode (default in CLI — requires manual cookie):
       export H1_SESSION="__Host-session=<value from DevTools>"
       export H1_CSRF="<value from DevTools>"
       python3 bin/h1-hacktivity-fetch.py --weakness dom-xss idor --limit 200

  2. Stdin-json mode (used when called from Claude Code with browser results):
       python3 bin/h1-hacktivity-fetch.py --from-json /tmp/h1_batch.json

Usage:
    python3 bin/h1-hacktivity-fetch.py [options]

Options:
    --limit N               Max reports (default: 200)
    --size N                Page size per request (default: 25, max: 100)
    --since YYYY-MM-DD      Only reports disclosed after date
    --weakness CLASS...     Filter by wiki class (see CWE_TO_CLASS)
    --min-severity LEVEL    none|low|medium|high|critical (default: medium)
    --program HANDLE        Single H1 program handle (adds team.handle: filter)
    --query STRING          Raw H1 query string override (e.g. "disclosed:true severity:critical")
    --out DIR               Output dir (default: wiki/sources/hacktivity)
    --delay SECS            Delay between requests (default: 0.4)
    --dry-run               Print what would be written, don't write
    --from-json FILE        Read pre-fetched JSON (list of node dicts) instead of fetching

Environment:
    H1_SESSION   Full cookie header value e.g. "__Host-session=abc123"
    H1_CSRF      X-CSRF-Token header value
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# CWE → wiki technique class mapping
# ---------------------------------------------------------------------------
CWE_TO_CLASS: dict[str, list[str]] = {
    "CWE-79":   ["dom-xss"],
    "CWE-80":   ["dom-xss"],
    "CWE-83":   ["dom-xss"],
    "CWE-84":   ["dom-xss"],
    "CWE-116":  ["dom-xss"],
    "CWE-1321": ["prototype-pollution"],
    "CWE-915":  ["prototype-pollution"],
    "CWE-352":  ["csrf"],
    "CWE-918":  ["server-side"],
    "CWE-611":  ["server-side"],
    "CWE-22":   ["server-side"],
    "CWE-89":   ["server-side"],
    "CWE-78":   ["server-side"],
    "CWE-94":   ["server-side"],
    "CWE-502":  ["server-side"],
    "CWE-284":  ["idor"],
    "CWE-285":  ["idor"],
    "CWE-639":  ["idor"],
    "CWE-863":  ["idor"],
    "CWE-862":  ["idor"],
    "CWE-200":  ["idor"],
    "CWE-287":  ["oauth"],
    "CWE-306":  ["oauth"],
    "CWE-303":  ["oauth"],
    "CWE-384":  ["oauth"],
    "CWE-362":  ["race-conditions"],
    "CWE-367":  ["race-conditions"],
    "CWE-601":  ["server-side"],
    "CWE-347":  ["jwt"],
    "CWE-346":  ["postmessage"],
    "CWE-1021": ["xs-leaks"],
}

WEAKNESS_NAME_HINTS: list[tuple[str, str]] = [
    ("cross-site scripting",   "dom-xss"),
    ("xss",                    "dom-xss"),
    ("prototype",              "prototype-pollution"),
    ("csrf",                   "csrf"),
    ("cross-site request",     "csrf"),
    ("server-side request",    "server-side"),
    ("ssrf",                   "server-side"),
    ("sql injection",          "server-side"),
    ("path traversal",         "server-side"),
    ("code injection",         "server-side"),
    ("insecure direct",        "idor"),
    ("idor",                   "idor"),
    ("improper access",        "idor"),
    ("authorization",          "idor"),
    ("authentication",         "oauth"),
    ("oauth",                  "oauth"),
    ("open redirect",          "server-side"),
    ("race condition",         "race-conditions"),
    ("time-of-check",          "race-conditions"),
    ("postmessage",            "postmessage"),
    ("message channel",        "postmessage"),
    ("xs-leak",                "xs-leaks"),
    ("side-channel",           "xs-leaks"),
    ("jwt",                    "jwt"),
    ("json web token",         "jwt"),
]

# Mapping from our wiki weakness class to H1 query-string severity tokens
CLASS_TO_H1_CWE_QUERY: dict[str, str] = {
    "dom-xss":             "weakness.external_id:CWE-79",
    "prototype-pollution": "(weakness.external_id:CWE-1321 OR weakness.external_id:CWE-915)",
    "csrf":                "weakness.external_id:CWE-352",
    "idor":                "(weakness.external_id:CWE-284 OR weakness.external_id:CWE-285 OR weakness.external_id:CWE-639 OR weakness.external_id:CWE-863 OR weakness.external_id:CWE-862)",
    "server-side":         "(weakness.external_id:CWE-918 OR weakness.external_id:CWE-89 OR weakness.external_id:CWE-22 OR weakness.external_id:CWE-611)",
    "oauth":               "(weakness.external_id:CWE-287 OR weakness.external_id:CWE-306 OR weakness.external_id:CWE-384)",
    "race-conditions":     "(weakness.external_id:CWE-362 OR weakness.external_id:CWE-367)",
    "jwt":                 "weakness.external_id:CWE-347",
    "postmessage":         "weakness.external_id:CWE-346",
    "xs-leaks":            "weakness.external_id:CWE-1021",
}

SEVERITY_ORDER = ["none", "low", "medium", "high", "critical"]

HACKTIVITY_QUERY = """
query HacktivitySearchQuery($queryString: String!, $from: Int, $size: Int, $sort: SortInput!) {
  search(
    index: CompleteHacktivityReportIndex
    query_string: $queryString
    from: $from
    size: $size
    sort: $sort
  ) {
    __typename
    total_count
    nodes {
      __typename
      ... on HacktivityDocument {
        id
        _id
        reporter { id username name }
        cve_ids
        cwe
        severity_rating
        public
        report {
          id
          databaseId: _id
          title
          substate
          url
          disclosed_at
          report_generated_content { id hacktivity_summary }
        }
        votes
        team { id handle name url currency }
        total_awarded_amount
        latest_disclosable_activity_at
        submitted_at
        disclosed
      }
    }
  }
}
"""


def build_query_string(args: argparse.Namespace) -> str:
    if args.query:
        return args.query

    parts = ["disclosed:true"]

    if args.weakness:
        cwe_parts = []
        for cls in args.weakness:
            if cls in CLASS_TO_H1_CWE_QUERY:
                cwe_parts.append(CLASS_TO_H1_CWE_QUERY[cls])
        if cwe_parts:
            parts.append(f"({' OR '.join(cwe_parts)})")

    if args.min_severity and args.min_severity != "none":
        min_idx = SEVERITY_ORDER.index(args.min_severity)
        sev_vals = SEVERITY_ORDER[min_idx:]
        if len(sev_vals) < len(SEVERITY_ORDER):
            parts.append(f"severity:({' OR '.join(sev_vals)})")

    if args.since:
        parts.append(f"disclosed_at:[{args.since} TO *]")

    if args.program:
        parts.append(f"team.handle:{args.program}")

    return " AND ".join(parts)


def graphql_via_http(query: str, variables: dict, session: str, csrf: str,
                     delay: float = 0.4) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://hackerone.com/graphql",
        data=payload,
        headers={
            "Content-Type":  "application/json",
            "Accept":        "application/json",
            "Cookie":        session,
            "X-CSRF-Token":  csrf,
            "User-Agent":    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/124.0.0.0 Safari/537.36",
            "Origin":        "https://hackerone.com",
            "Referer":       "https://hackerone.com/hacktivity",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"H1 GraphQL HTTP {e.code}: {body[:400]}") from e
    if "errors" in data:
        raise RuntimeError(f"H1 GraphQL errors: {data['errors']}")
    time.sleep(delay)
    return data


def classify(node: dict) -> list[str]:
    cwe_raw = node.get("cwe") or ""
    classes: list[str] = []
    for cwe_id in re.findall(r"CWE-\d+", cwe_raw.upper()):
        classes.extend(CWE_TO_CLASS.get(cwe_id, []))
    if not classes:
        # fallback to name hints from cwe field text
        cwe_lower = cwe_raw.lower()
        for hint, cls in WEAKNESS_NAME_HINTS:
            if hint in cwe_lower:
                classes.append(cls)
                break
    return list(dict.fromkeys(classes))


def slug_for(report_id: str, title: str) -> str:
    safe = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    return f"{report_id}-{safe}"


def render_source(node: dict, fetched_utc: str) -> str:
    report   = node.get("report") or {}
    team     = node.get("team") or {}
    reporter = (node.get("reporter") or {}).get("username", "unknown")
    classes  = classify(node)

    title     = report.get("title", "(untitled)")
    url       = report.get("url", "")
    disclosed = (report.get("disclosed_at") or "")[:10]
    substate  = report.get("substate", "")
    summary   = ((report.get("report_generated_content") or {}).get("hacktivity_summary") or "").strip()
    severity  = node.get("severity_rating") or "none"
    cwe       = node.get("cwe") or ""
    bounty    = node.get("total_awarded_amount")
    currency  = team.get("currency", "USD")
    bounty_str = f"{bounty:.0f} {currency}" if bounty else "undisclosed"
    program   = team.get("name", "")
    handle    = team.get("handle", "")
    votes     = node.get("votes", 0)
    rid       = str(node.get("_id") or node.get("id", "unknown"))

    technique_tags = " ".join(f"technique/{c}" for c in classes)
    tags = f"[source, hacktivity{', ' + technique_tags if technique_tags else ''}]"

    lines = [
        "---",
        f"title: \"H1 #{rid} — {title}\"",
        f"slug: h1-{slug_for(rid, title)}",
        f"url: {url}",
        f"fetched_utc: {fetched_utc}",
        "kind: thread",
        "extracted: false",
        f"tags: {tags}",
        "inbound: []",
        "---",
        "",
        f"# H1 #{rid} — {title}",
        "",
        "## Metadata",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Program | [{program}](https://hackerone.com/{handle}) |",
        f"| Reporter | {reporter} |",
        f"| Severity | {severity} |",
        f"| Bounty | {bounty_str} |",
        f"| Weakness | {cwe} |",
        f"| Wiki class | {', '.join(classes) if classes else 'uncategorised'} |",
        f"| Disclosed | {disclosed} |",
        f"| Substate | {substate} |",
        f"| Votes | {votes} |",
        "",
    ]

    if summary:
        lines += ["## AI Summary", "", summary, ""]

    lines += [
        "## Report",
        "",
        f"Full writeup: <{url}>",
        "",
        "<!-- extraction-pass: populate Seen-in-the-wild + technique cross-links -->",
    ]
    return "\n".join(lines) + "\n"


def fetch_all_http(args: argparse.Namespace, session: str, csrf: str) -> list[dict]:
    query_string = build_query_string(args)
    print(f"  query_string: {query_string}", file=sys.stderr)

    nodes: list[dict] = []
    page_size = min(args.size, 100)
    sort = {"field": "latest_disclosable_activity_at", "direction": "DESC"}

    from_offset = 0
    while len(nodes) < args.limit:
        batch = min(page_size, args.limit - len(nodes))
        print(f"  → from={from_offset} size={batch} (total so far: {len(nodes)})",
              file=sys.stderr)
        data = graphql_via_http(
            HACKTIVITY_QUERY,
            {"queryString": query_string, "from": from_offset, "size": batch, "sort": sort},
            session, csrf, delay=args.delay,
        )
        search = data.get("data", {}).get("search") or {}
        batch_nodes = [n for n in (search.get("nodes") or [])
                       if n.get("__typename") == "HacktivityDocument"]
        if not batch_nodes:
            break
        nodes.extend(batch_nodes)
        total = search.get("total_count", 0)
        from_offset += len(batch_nodes)
        if from_offset >= total:
            break

    return nodes


def write_sources(nodes: list[dict], out_dir: Path, dry_run: bool,
                  fetched_utc: str) -> tuple[int, int]:
    written = skipped = 0
    for node in nodes:
        rid = str(node.get("_id") or node.get("id", "unknown"))
        outfile = out_dir / f"{rid}.md"
        if outfile.exists():
            skipped += 1
            continue
        content = render_source(node, fetched_utc)
        if dry_run:
            report = node.get("report") or {}
            print(f"\n--- {outfile} [{node.get('severity_rating')}] ---", file=sys.stderr)
            print(f"    {report.get('title','')[:80]}", file=sys.stderr)
            print(f"    cwe={node.get('cwe','')} classes={classify(node)}", file=sys.stderr)
        else:
            outfile.write_text(content, encoding="utf-8")
        written += 1
    return written, skipped


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch H1 Hacktivity into wiki/sources/hacktivity/")
    parser.add_argument("--limit",        type=int,   default=200)
    parser.add_argument("--size",         type=int,   default=25)
    parser.add_argument("--since",        type=str,   default=None)
    parser.add_argument("--weakness",     nargs="+",  default=None)
    parser.add_argument("--min-severity", dest="min_severity", default="medium",
                        choices=SEVERITY_ORDER)
    parser.add_argument("--program",      type=str,   default=None)
    parser.add_argument("--query",        type=str,   default=None,
                        help="Raw H1 query string override")
    parser.add_argument("--out",          type=Path,
                        default=Path("wiki/sources/hacktivity"))
    parser.add_argument("--delay",        type=float, default=0.4)
    parser.add_argument("--dry-run",      action="store_true")
    parser.add_argument("--from-json",    type=Path,  default=None,
                        help="Read pre-fetched node list JSON instead of fetching")
    args = parser.parse_args()

    if not args.dry_run:
        args.out.mkdir(parents=True, exist_ok=True)

    fetched_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if args.from_json:
        nodes = json.loads(args.from_json.read_text())
        print(f"Loaded {len(nodes)} nodes from {args.from_json}", file=sys.stderr)
    else:
        session = os.environ.get("H1_SESSION", "")
        csrf    = os.environ.get("H1_CSRF", "")
        if not session or not csrf:
            print(
                "ERROR: H1_SESSION and H1_CSRF env vars required for HTTP mode.\n"
                "Get them from DevTools → Application → Cookies (__Host-session)\n"
                "and Network → any GraphQL request → X-CSRF-Token header.\n"
                "Or use --from-json to load pre-fetched results.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(
            f"Fetching (limit={args.limit}, min_severity={args.min_severity}, "
            f"weakness={args.weakness}, since={args.since}, program={args.program})",
            file=sys.stderr,
        )
        nodes = fetch_all_http(args, session, csrf)
        print(f"Fetched {len(nodes)} nodes.", file=sys.stderr)

    written, skipped = write_sources(nodes, args.out, args.dry_run, fetched_utc)
    print(f"Done. written={written} skipped={skipped}", file=sys.stderr)


if __name__ == "__main__":
    main()
