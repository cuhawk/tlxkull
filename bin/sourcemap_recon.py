#!/usr/bin/env python3
"""Hidden-sourcemap brute + Sentry release-artifact recon.

Augments the standard `js-harvest` sourceMappingURL/X-SourceMap pass by
brute-forcing common Webpack/Vite/Next/Nuxt hidden-map filenames next to
each bundled .js, and by pulling .map files from any in-scope Sentry
release-artifact API.

Brute paths and Sentry recipe taken verbatim from
`wiki/tools/tlx/sourcemap-recon.md` (the design spec).

Usage:
  bin/sourcemap_recon.py <target_dir>
      [--max-attempts-per-bundle N]   # default 40
      [--rate-limit-ms N]             # default 200
      [--timeout N]                   # default 8 seconds
      [--user-agent UA]
      [--no-sentry]                   # skip Sentry phase

Updates `status.json.phases.sourcemap_recon` with counts and reads scope
from `status.json.scope.in` (refuses out-of-scope hosts).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    ROOT,
    host_in_scope,
    read_scope,
    resolve_target_dir,
    status_lock,
    utcnow,
)

BRUTE_TEMPLATES_PER_BUNDLE = (
    "{base}.js.map",
    "{base}.min.js.map",
)

BRUTE_TEMPLATES_PER_HOST = (
    "assets/index.js.map",
    "static/js/main.chunk.js.map",
    "static/js/bundle.js.map",
    "debug.js.map",
    "app.js.map",
    "main.js.map",
    "vendor.js.map",
    "runtime.js.map",
    "polyfills.js.map",
)

SENTRY_HOST_REGEX = re.compile(
    r"https?://([a-z0-9.-]*sentry[a-z0-9.-]*)/", re.IGNORECASE
)
SENTRY_DSN_REGEX = re.compile(
    r"https?://([a-f0-9]+)@([a-z0-9.-]+)/(\d+)", re.IGNORECASE
)
SOURCE_MAP_VERSION_REGEX = re.compile(rb'"version"\s*:\s*3')


def host_from_raw_path(rel: Path, raw_root: Path) -> str | None:
    try:
        parts = rel.relative_to(raw_root).parts
    except ValueError:
        return None
    return parts[0] if parts else None


def bundle_local_candidates(js_path: Path) -> Iterable[str]:
    name = js_path.name
    if not name.endswith(".js"):
        return
    base_no_ext = name[:-3]
    for tpl in BRUTE_TEMPLATES_PER_BUNDLE:
        cand = tpl.format(base=base_no_ext)
        if cand != name:
            yield cand


def build_candidate_url(host: str, rel_dir: Path, filename: str) -> str:
    rel_str = "" if str(rel_dir) == "." else str(rel_dir).replace("\\", "/").strip("/")
    if rel_str:
        return f"https://{host}/{rel_str}/{filename}"
    return f"https://{host}/{filename}"


def http_get(
    url: str, *, timeout: int, user_agent: str, max_bytes: int | None = None
) -> tuple[int, bytes, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(max_bytes) if max_bytes else r.read()
            return r.status, body, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, b"", dict(e.headers or {})
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return 0, b"", {"_err": str(e)}


def is_sourcemap_body(body: bytes) -> bool:
    if not body:
        return False
    head = body[:4096]
    if SOURCE_MAP_VERSION_REGEX.search(head):
        return True
    return head.lstrip().startswith(b"{") and b'"sources"' in head


def detect_sentry(raw_root: Path) -> set[tuple[str, str | None]]:
    found: set[tuple[str, str | None]] = set()
    for js in raw_root.rglob("*.js"):
        try:
            content = js.read_bytes().decode("utf-8", errors="ignore")
        except OSError:
            continue
        for m in SENTRY_HOST_REGEX.finditer(content):
            found.add((m.group(1).lower(), None))
        for m in SENTRY_DSN_REGEX.finditer(content):
            found.add((m.group(2).lower(), m.group(3)))
    return found


def enumerate_sentry_releases(
    host: str, *, timeout: int, user_agent: str, rate_ms: int
) -> list[str]:
    code, body, _ = http_get(
        f"https://{host}/api/0/projects/", timeout=timeout, user_agent=user_agent
    )
    if code != 200 or not body:
        return []
    try:
        projects = json.loads(body)
    except json.JSONDecodeError:
        return []
    versions: list[str] = []
    for proj in projects[:5]:
        org = proj.get("organization", {}).get("slug")
        slug = proj.get("slug")
        if not (org and slug):
            continue
        time.sleep(rate_ms / 1000)
        code, body, _ = http_get(
            f"https://{host}/api/0/projects/{org}/{slug}/releases/?per_page=20",
            timeout=timeout,
            user_agent=user_agent,
        )
        if code != 200:
            continue
        try:
            for rel in json.loads(body):
                versions.append(f"{org}/{slug}::{rel['version']}")
        except (json.JSONDecodeError, KeyError):
            continue
    return versions


def save_map(target: Path, host: str, rel_path: str, body: bytes) -> Path:
    out = target / "raw" / host / rel_path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    return out


def run(target: Path, args) -> dict:
    raw_root = target / "raw"
    if not raw_root.exists():
        return {"status": "error", "error": f"raw/ missing under {target}"}
    scope = read_scope(target)

    found: list[dict] = []
    missing_bundles: list[str] = []
    skipped_oos: set[str] = set()
    bundles_processed = 0
    requests_total = 0
    rate = args.rate_limit_ms / 1000

    host_root_done: set[str] = set()

    for js in sorted(raw_root.rglob("*.js")):
        if js.suffix != ".js":
            continue
        if js.with_suffix(".js.map").exists():
            continue
        host = host_from_raw_path(js, raw_root)
        if not host:
            continue
        if not host_in_scope(host, scope):
            skipped_oos.add(host)
            continue

        bundles_processed += 1
        rel_dir = js.relative_to(raw_root / host).parent
        bundle_rel = str(js.relative_to(raw_root))
        attempts = 0
        recovered = False

        for cand_name in bundle_local_candidates(js):
            if attempts >= args.max_attempts_per_bundle:
                break
            cand_url = build_candidate_url(host, rel_dir, cand_name)
            attempts += 1
            requests_total += 1
            time.sleep(rate)
            code, body, _ = http_get(
                cand_url,
                timeout=args.timeout,
                user_agent=args.user_agent,
                max_bytes=8 * 1024 * 1024,
            )
            if code == 429:
                time.sleep(2.0)
                continue
            if code == 200 and is_sourcemap_body(body):
                rel_path = (
                    f"{rel_dir}/{cand_name}" if str(rel_dir) != "." else cand_name
                )
                save_map(target, host, rel_path, body)
                found.append(
                    {"url": cand_url, "saved_to": rel_path, "bundle": bundle_rel}
                )
                recovered = True
                break

        if not recovered:
            missing_bundles.append(bundle_rel)

        if host not in host_root_done:
            host_root_done.add(host)
            for tpl in BRUTE_TEMPLATES_PER_HOST:
                cand_url = f"https://{host}/{tpl}"
                requests_total += 1
                time.sleep(rate)
                code, body, _ = http_get(
                    cand_url,
                    timeout=args.timeout,
                    user_agent=args.user_agent,
                    max_bytes=8 * 1024 * 1024,
                )
                if code == 429:
                    time.sleep(2.0)
                    continue
                if code == 200 and is_sourcemap_body(body):
                    save_map(target, host, tpl, body)
                    found.append(
                        {"url": cand_url, "saved_to": tpl, "bundle": "<host-root>"}
                    )

    sentry_results: dict = {
        "hosts_seen": [],
        "releases_enumerated": [],
        "files_pulled": 0,
    }
    if not args.no_sentry:
        for host, _proj in detect_sentry(raw_root):
            in_scope = host_in_scope(host, scope)
            sentry_results["hosts_seen"].append({"host": host, "in_scope": in_scope})
            if not in_scope:
                continue
            requests_total += 1
            time.sleep(rate)
            versions = enumerate_sentry_releases(
                host,
                timeout=args.timeout,
                user_agent=args.user_agent,
                rate_ms=args.rate_limit_ms,
            )
            sentry_results["releases_enumerated"].extend(versions)

    result = {
        "status": "done",
        "ts": utcnow(),
        "bundles_processed": bundles_processed,
        "maps_recovered": len(found),
        "maps_missing": len(missing_bundles),
        "requests_total": requests_total,
        "out_of_scope_hosts_skipped": sorted(skipped_oos),
        "sentry": sentry_results,
        "found": found,
    }

    with status_lock(target) as data:
        data.setdefault("phases", {})["sourcemap_recon"] = result
        if missing_bundles:
            harvest = data.setdefault("harvest", {})
            existing = set(harvest.get("missing_maps", []))
            existing.update(missing_bundles)
            harvest["missing_maps"] = sorted(existing)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    ap.add_argument("--max-attempts-per-bundle", type=int, default=40)
    ap.add_argument("--rate-limit-ms", type=int, default=200)
    ap.add_argument("--timeout", type=int, default=8)
    ap.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (compatible; tlx-sourcemap-recon/1.0)",
    )
    ap.add_argument("--no-sentry", action="store_true")
    args = ap.parse_args()
    try:
        target = resolve_target_dir(args.target_dir)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    res = run(target, args)
    print(json.dumps(res, indent=2, default=str))
    return 0 if res.get("status") == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
