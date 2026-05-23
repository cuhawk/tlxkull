#!/usr/bin/env python3
"""Pipeline Auto driver — classifies scope, fans out lanes, halts at audit boundary.

Spec: plans/PIPELINE_AUTO.md.

Usage:
    python3 bin/pipeline_run.py <target_name> [--dry-run] [--max-parallel N]
                                              [--masscan-mode {local,droplet}]
                                              [--ports {web,full}]
                                              [--lanes url,wildcard,ip_cidr]

The driver never invokes opus-deep-audit / cc-taint-adversarial / opus-gap-audit
/ autoresearch-loop. It stops once every lane has reached its audit boundary
and writes `targets/<name>/_audit_queue.jsonl` for the user to trigger audit
manually.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ROOT / "targets"

URL_RE = re.compile(r"^https?://", re.I)
WILDCARD_RE = re.compile(r"^\*\.[a-z0-9.-]+\.[a-z]{2,}$", re.I)
APEX_RE = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$", re.I)
IP_RANGE_RE = re.compile(r"^\s*([\d.]+)\s*-\s*([\d.]+)\s*$")

# target-init populates scope[].type. Map those to lanes; fall back to regex
# classification for legacy targets that only have plain strings.
TYPE_TO_LANE = {
    "url": "url",
    "domain": "url",
    "api": "url",
    "wildcard": "wildcard",
    "cidr": "ip_cidr",
    "ip": "ip_cidr",
    "ip_range": "ip_cidr",
    # everything below has no JS/HTTP pipeline path
    "ios_app": "skip",
    "android_app": "skip",
    "other_apk": "skip",
    "other_ipa": "skip",
    "testflight": "skip",
    "windows_app_store_app_id": "skip",
    "repo": "skip",
    "downloadable_executables": "skip",
    "firmware": "skip",
    "other": "skip",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_status(target_dir: Path) -> dict:
    p = target_dir / "status.json"
    if not p.is_file():
        sys.exit(f"status.json missing — run target-init on {target_dir.name} first")
    return json.loads(p.read_text())


def save_status(target_dir: Path, status: dict) -> None:
    p = target_dir / "status.json"
    p.write_text(json.dumps(status, indent=2, sort_keys=True))


def classify_entry(entry) -> tuple[str, str]:
    """Return (lane, value-string) for a scope entry (dict or bare string)."""
    if isinstance(entry, dict):
        t = (entry.get("type") or "").lower()
        v = (entry.get("value") or "").strip()
        if t in TYPE_TO_LANE:
            lane = TYPE_TO_LANE[t]
            # target-init marks path-globs (e.g. "host.example.com/*/login") as
            # type=wildcard. Those are URL lane against the bare host, not a
            # host-wildcard for subdomain enum.
            if lane == "wildcard" and "/" in v and not v.startswith("*."):
                host = v.split("/", 1)[0]
                return "url", host
            return lane, v
        # fall through to regex on the value when type is unknown
        entry = v
    s = (entry or "").strip()
    if not s:
        return "skip", s
    if URL_RE.match(s):
        return "url", s
    if WILDCARD_RE.match(s):
        return "wildcard", s
    if IP_RANGE_RE.match(s):
        return "ip_cidr", s
    if "/" in s:
        try:
            ipaddress.ip_network(s, strict=False)
            return "ip_cidr", s
        except ValueError:
            pass
    try:
        ipaddress.ip_address(s)
        return "ip_cidr", s
    except ValueError:
        pass
    if APEX_RE.match(s):
        # bare apex is auto-promoted to wildcard per recon skill contract
        return "wildcard", s
    return "unknown", s


def classify_scope(status: dict) -> list[dict]:
    scope_in = status.get("scope", {}).get("in", [])
    classified: list[dict] = []
    for entry in scope_in:
        lane, value = classify_entry(entry)
        classified.append({"entry": value, "lane": lane})
    return classified


def mark_phase(status: dict, phase: str, fields: dict) -> None:
    phases = status.setdefault("phases", {})
    phases[phase] = {**phases.get(phase, {}), **fields, "heartbeat_utc": now_utc()}


# ---------------------------------------------------------------------------
# Lane runners — each returns a dict the driver appends to _audit_queue.jsonl
# ---------------------------------------------------------------------------


def run_url_lane(target_dir: Path, host: str, status: dict, args: argparse.Namespace) -> dict:
    """Run js-harvest → ... → dom-xss-hunt for a single host. Stops at audit boundary."""
    name = target_dir.name
    mark_phase(status, f"url:{host}", {"status": "running", "started_utc": now_utc()})
    save_status(target_dir, status)

    # Real implementation should shell into each skill via Claude Code subagents
    # OR call the MCP tools directly. For now we record the lane plan and let
    # the operator (Claude session) trigger each skill — the driver focuses on
    # classification, parallelism, and the pause boundary.
    plan = [
        "js-harvest",
        "sourcemap-explode",
        "rag-ingest",
        "js-index",
        "db-isolate",
        "implicit-tags",
        "async-edges",
        "browser-context-infer",
        "chain-bestfirst",
        "sanitizer-on-path",
        "chain-triage",
        "dom-xss-hunt",
    ]
    chains_file = target_dir / "chains" / "dom_reachable.jsonl"
    # Placeholder: real driver will execute each skill and only mark done after
    # `chains_file` materializes. For now write the plan into status so the
    # session can pick it up.
    mark_phase(
        status,
        f"url:{host}",
        {"status": "queued", "plan": plan, "expected_output": str(chains_file.relative_to(target_dir))},
    )
    save_status(target_dir, status)
    return {
        "target": name,
        "lane": "url",
        "host": host,
        "chains_file": str(chains_file.relative_to(target_dir)),
        "ready_utc": now_utc(),
        "next": f"/cc-taint-adversarial {name}",
        "plan": plan,
    }


def run_wildcard_lane(target_dir: Path, wildcard: str, status: dict, args: argparse.Namespace) -> list[dict]:
    """Subdomain enum → resolve → masscan → httpx → per-live-host url-lane."""
    name = target_dir.name
    mark_phase(status, f"wildcard:{wildcard}", {"status": "running", "started_utc": now_utc()})
    save_status(target_dir, status)

    enum_out = target_dir / "recon" / f"subs_{wildcard.replace('*.', '')}.txt"
    resolved = target_dir / "recon" / f"resolved_{wildcard.replace('*.', '')}.jsonl"
    live_web = target_dir / "recon" / f"live_web_{wildcard.replace('*.', '')}.jsonl"

    plan = {
        "enum": f"recon MCP recon_start (targets=['{wildcard}'])",
        "resolve": f"dnsx → {resolved}",
        "masscan": f"bin/masscan_run.py --hosts {resolved} --ports {args.ports} --mode {args.masscan_mode}",
        "httpx": f"bin/httpx_probe.py --input <masscan-open> --output {live_web}",
        "per_host": "spawn url-lane for every live_web host where js_detected == true",
    }

    mark_phase(
        status,
        f"wildcard:{wildcard}",
        {"status": "queued", "plan": plan, "outputs": {"enum": str(enum_out), "live_web": str(live_web)}},
    )
    save_status(target_dir, status)

    # Spawned sub-lanes append individual rows once live_web is populated; for
    # the scaffold we emit a single placeholder row pointing at live_web.
    return [
        {
            "target": name,
            "lane": "wildcard",
            "wildcard": wildcard,
            "live_web_file": str(live_web.relative_to(target_dir)),
            "ready_utc": now_utc(),
            "next": "driver re-entry after live_web.jsonl populated",
            "plan": plan,
        }
    ]


def run_ip_cidr_lane(target_dir: Path, entries: list[str], status: dict, args: argparse.Namespace) -> list[dict]:
    """Masscan over IP/CIDR set → httpx → per-live-host url-lane."""
    name = target_dir.name
    mark_phase(status, "ip_cidr", {"status": "running", "started_utc": now_utc(), "entries": entries})
    save_status(target_dir, status)

    expanded = target_dir / "recon" / "ip_cidr_expanded.txt"
    masscan_out = target_dir / "recon" / "masscan.jsonl"
    live_web = target_dir / "recon" / "live_web_ip.jsonl"

    plan = {
        "expand": f"bin/scope_expand_ips.py (or pre-staged) → {expanded}",
        "masscan": f"bin/masscan_run.py --hosts {expanded} --ports {args.ports} --mode {args.masscan_mode} --output {masscan_out}",
        "httpx": f"bin/httpx_probe.py --input {masscan_out} --output {live_web}",
        "per_host": "spawn url-lane per live_web host with js_detected == true",
    }
    mark_phase(status, "ip_cidr", {"status": "queued", "plan": plan, "outputs": {"masscan": str(masscan_out), "live_web": str(live_web)}})
    save_status(target_dir, status)

    return [
        {
            "target": name,
            "lane": "ip_cidr",
            "entries": entries,
            "live_web_file": str(live_web.relative_to(target_dir)),
            "ready_utc": now_utc(),
            "next": "driver re-entry after live_web.jsonl populated",
            "plan": plan,
        }
    ]


# ---------------------------------------------------------------------------
# Audit queue writer
# ---------------------------------------------------------------------------


def write_audit_queue(target_dir: Path, rows: Iterable[dict]) -> Path:
    q = target_dir / "_audit_queue.jsonl"
    # dedup by (lane, host|wildcard|entries)
    existing: dict[str, dict] = {}
    if q.exists():
        for line in q.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                key = f"{obj.get('lane')}::{obj.get('host') or obj.get('wildcard') or json.dumps(obj.get('entries'))}"
                existing[key] = obj
            except json.JSONDecodeError:
                continue
    for row in rows:
        key = f"{row.get('lane')}::{row.get('host') or row.get('wildcard') or json.dumps(row.get('entries'))}"
        existing[key] = row
    q.write_text("\n".join(json.dumps(v, sort_keys=True) for v in existing.values()) + "\n")
    return q


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="target name under targets/")
    ap.add_argument("--dry-run", action="store_true", help="classify scope and print plan; do nothing else")
    ap.add_argument("--max-parallel", type=int, default=4)
    ap.add_argument("--masscan-mode", choices=["local", "droplet"], default="local")
    ap.add_argument("--ports", choices=["web", "full"], default="web")
    ap.add_argument(
        "--lanes",
        default="url,wildcard,ip_cidr",
        help="comma-separated subset to run (default all)",
    )
    args = ap.parse_args()

    target_dir = TARGETS / args.target
    if not target_dir.is_dir():
        sys.exit(f"no such target dir: {target_dir}")

    status = load_status(target_dir)
    classified = classify_scope(status)
    status["scope_classified"] = classified
    save_status(target_dir, status)

    wanted_lanes = set(args.lanes.split(","))

    by_lane: dict[str, list[str]] = {"url": [], "wildcard": [], "ip_cidr": [], "unknown": [], "skip": []}
    seen: dict[str, set[str]] = {k: set() for k in by_lane}
    for row in classified:
        lane, value = row["lane"], row["entry"]
        if not value or value in seen[lane]:
            continue
        seen[lane].add(value)
        by_lane[lane].append(value)

    print(f"[pipeline_run] target={args.target}")
    for lane, entries in by_lane.items():
        if entries:
            print(f"  {lane}: {len(entries)} entries")
            for e in entries[:5]:
                print(f"    - {e}")
            if len(entries) > 5:
                print(f"    ... ({len(entries) - 5} more)")
    if by_lane["unknown"]:
        print("WARN: unknown-lane entries — manual classification needed")

    if args.dry_run:
        print("(dry-run) exiting")
        return

    audit_rows: list[dict] = []

    if "url" in wanted_lanes and by_lane["url"]:
        with ThreadPoolExecutor(max_workers=args.max_parallel) as pool:
            futs = {pool.submit(run_url_lane, target_dir, host, status, args): host for host in by_lane["url"]}
            for fut in as_completed(futs):
                audit_rows.append(fut.result())

    if "wildcard" in wanted_lanes and by_lane["wildcard"]:
        for wc in by_lane["wildcard"]:
            audit_rows.extend(run_wildcard_lane(target_dir, wc, status, args))

    if "ip_cidr" in wanted_lanes and by_lane["ip_cidr"]:
        audit_rows.extend(run_ip_cidr_lane(target_dir, by_lane["ip_cidr"], status, args))

    q = write_audit_queue(target_dir, audit_rows)
    status["phase"] = "ready_for_audit"
    status.setdefault("phases", {})["pipeline_run"] = {
        "status": "done",
        "ts": now_utc(),
        "audit_queue": str(q.relative_to(target_dir)),
        "lanes_run": sorted(wanted_lanes),
    }
    save_status(target_dir, status)

    print(f"\n[pipeline_run] PAUSED at audit boundary")
    print(f"  audit_queue → {q}")
    print(f"  next        → /cc-taint-adversarial {args.target}   (or /opus-deep-audit {args.target})")


if __name__ == "__main__":
    main()
