#!/usr/bin/env python3
"""Parse Gmail invite threads (JSON blobs from the Gmail MCP) into
inbox/invites/<platform>/<slug>/{email.json, meta.json, READY|DUPLICATE|REINVITE}.

Idempotent: re-running with the same input produces the same output.
Never overwrites an existing meta.json — only creates new ones.

Input format: NDJSON, one JSON object per line, where each object is
either a top-level {"threads": [...]} response from `search_threads` or
a single thread dict.

Usage:
    python parse_invites.py < gmail_dump.ndjson
    python parse_invites.py --input gmail_dump.ndjson --targets-dir targets/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[2]
INBOX_ROOT = REPO_ROOT / "inbox" / "invites"
TARGETS_DIR = REPO_ROOT / "targets"
SWEEP_LOG = INBOX_ROOT / "_sweep_log.jsonl"

H1_RE = re.compile(r"^(.+?)\s+has invited you to their HackerOne program$", re.I)
INTIGRITI_APP_RE = re.compile(r"application for (.+?) was accepted by (.+?)\.", re.I)
INTIGRITI_INVITE_SUBJ_RE = re.compile(r"\[ intigriti \] You have been invited to join (.+)$", re.I)
INTIGRITI_INVITE_BODY_RE = re.compile(r"^([^\n]+?)\s+has invited you", re.I)
SYNACK_RE = re.compile(r"^You have been onboarded on target (.+)$", re.I)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def iter_threads(stream) -> Iterator[dict]:
    """Yield individual thread dicts from NDJSON of MCP responses."""
    for raw in stream:
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"skip line: {exc}", file=sys.stderr)
            continue
        if "threads" in obj:
            yield from obj["threads"]
        elif "id" in obj and "messages" in obj:
            yield obj


def parse_thread(thread: dict) -> dict | None:
    """Return {platform, slug, program, company, sender, subject, sent_at,
    invite_url, thread_id} or None if no recognized pattern."""
    msgs = thread.get("messages", [])
    if not msgs:
        return None
    msg = msgs[0]
    sender = msg.get("sender", "")
    subject = msg.get("subject", "")
    snippet = msg.get("snippet", "")
    sent_at = msg.get("date", "")
    thread_id = thread.get("id", "")

    base = {
        "sender": sender,
        "subject": subject,
        "snippet": snippet,
        "sent_at": sent_at,
        "thread_id": thread_id,
        "invite_url": f"https://mail.google.com/mail/u/0/#all/{thread_id}",
    }

    if "no-reply@hackerone.com" in sender:
        m = H1_RE.match(subject)
        if not m:
            return None
        program = m.group(1).strip()
        program = re.sub(r"^\[HackerOne Clear\]\s*", "", program).strip()
        return {**base, "platform": "hackerone",
                "slug": f"{slugify(program)}-h1",
                "program": program, "company": program,
                "lifecycle": "invited-pending"}

    if "noreply@intigriti.com" in sender:
        if "Application accepted" in subject:
            m = INTIGRITI_APP_RE.search(snippet)
            if not m:
                return None
            program, company = m.group(1).strip(), m.group(2).strip()
        else:
            m = INTIGRITI_INVITE_SUBJ_RE.match(subject)
            if not m:
                return None
            program = m.group(1).strip()
            mb = INTIGRITI_INVITE_BODY_RE.match(snippet)
            company = mb.group(1).strip() if mb else program
        return {**base, "platform": "intigriti",
                "slug": f"{slugify(company)}_{slugify(program)}-intigriti",
                "program": program, "company": company,
                "lifecycle": "invited-pending"}

    if "support@bugcrowd.com" in sender:
        return {**base, "platform": "bugcrowd",
                "slug": f"_unparsed_bc_{thread_id}-bc",
                "program": None, "company": None,
                "needs_body_fetch": True,
                "lifecycle": "invited-pending"}

    if "support@synack.com" in sender:
        m = SYNACK_RE.match(subject)
        if not m:
            return None
        code = m.group(1).strip()
        return {**base, "platform": "synack",
                "slug": f"{slugify(code)}-syn",
                "program": code, "company": "synack",
                "tracking_only": True,
                "lifecycle": "synack-tracked-only"}

    return None


def existing_target_slugs(targets_dir: Path) -> set[str]:
    if not targets_dir.exists():
        return set()
    return {p.name for p in targets_dir.iterdir() if p.is_dir()}


def write_seed(meta: dict, raw_thread: dict, inbox_root: Path,
               existing_targets: set[str], dry_run: bool) -> str:
    """Return action: created | duplicate | reinvite | skipped."""
    plat = meta["platform"]
    slug = meta["slug"]
    out_dir = inbox_root / plat / slug
    if out_dir.exists():
        return "skipped"

    target_dir_name = slug
    action = "created"
    if target_dir_name in existing_targets:
        action = "duplicate"

    if dry_run:
        return action

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "email.json").write_text(json.dumps(raw_thread, indent=2))
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    marker = {"duplicate": "DUPLICATE", "reinvite": "REINVITE"}.get(action, "READY")
    (out_dir / marker).write_text(datetime.now(timezone.utc).isoformat())
    return action


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=None,
                    help="NDJSON file (default: stdin)")
    ap.add_argument("--inbox-root", type=Path, default=INBOX_ROOT)
    ap.add_argument("--targets-dir", type=Path, default=TARGETS_DIR)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    stream = open(args.input) if args.input else sys.stdin
    existing = existing_target_slugs(args.targets_dir)
    counts = {"created": 0, "duplicate": 0, "reinvite": 0,
              "skipped": 0, "unparsed": 0}

    for thread in iter_threads(stream):
        meta = parse_thread(thread)
        if not meta:
            counts["unparsed"] += 1
            continue
        action = write_seed(meta, thread, args.inbox_root, existing,
                            args.dry_run)
        counts[action] += 1

    summary = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "skill": "target-discover.parse_invites",
        "dry_run": args.dry_run,
        **counts,
    }
    print(json.dumps(summary))
    if not args.dry_run:
        args.inbox_root.mkdir(parents=True, exist_ok=True)
        with open(SWEEP_LOG, "a") as f:
            f.write(json.dumps(summary) + "\n")


if __name__ == "__main__":
    main()
