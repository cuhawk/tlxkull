#!/usr/bin/env python3
"""Planner + collector for the per-finding-session skill.

Reads ``targets/<name>/findings/_queue_browser_confirm.jsonl``, dedupes
against already-confirmed / already-failed chains, emits a dispatch
plan for Claude Code to fan out one read-write subagent per pending
finding. After subagents run, ``collect`` updates status.json + prunes
the queue.

Per the API-key whitelist (CLAUDE.md rule 7), this script does NOT
call any LLM. It only renders plans + collects subagent outputs.
"""
from __future__ import annotations

import argparse
import json
import secrets
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import resolve_target_dir, status_lock, utcnow  # noqa: E402

DEFAULT_MAX_PARALLEL = 3
SCRATCH_TEMPLATE = "findings/{chain_id}/"

LIVE_SENSITIVE_KEYWORDS = ("synack", "-syn", "live-sensitive", "synack-l4")


def _read_queue(target: Path) -> list[dict]:
    p = target / "findings" / "_queue_browser_confirm.jsonl"
    if not p.exists():
        return []
    out = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            out.append(rec)
    return out


def _is_already_processed(target: Path, chain_id: str) -> tuple[bool, bool]:
    confirmed = target / "findings" / chain_id / "confirmed.json"
    failed = target / "findings" / chain_id / "failed.json"
    return confirmed.exists(), failed.exists()


def _detect_mode(target: Path) -> str:
    """Default mode: live unless target name suggests live-sensitive."""
    name = target.name.lower()
    for kw in LIVE_SENSITIVE_KEYWORDS:
        if kw in name:
            return "mock"
    return "live"


def _make_canary(chain_id: str) -> str:
    suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    safe_cid = "".join(c if c.isalnum() else "_" for c in str(chain_id))[:20]
    return f"TLX_XSS_CANARY_{safe_cid}_{suffix}"


def cmd_plan(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    queue = _read_queue(target)
    mode = args.mode or _detect_mode(target)

    pending = []
    skipped = []
    for entry in queue:
        cid = str(entry.get("chain_id") or entry.get("id") or "")
        if not cid:
            continue
        confirmed, failed = _is_already_processed(target, cid)
        if confirmed or failed:
            skipped.append(
                {"chain_id": cid, "already_confirmed": confirmed, "already_failed": failed}
            )
            continue
        pending.append(
            {
                "chain_id": cid,
                "triage": entry.get("triage"),
                "confidence": entry.get("confidence"),
                "scratch_dir": SCRATCH_TEMPLATE.format(chain_id=cid),
                "verify_canary": _make_canary(cid),
                "queued_at": entry.get("queued_at"),
                "opus_record_path": entry.get("opus_record"),
            }
        )

    plan = {
        "ts": utcnow(),
        "target": target.name,
        "mode": mode,
        "queue_size": len(queue),
        "pending": pending,
        "skipped": skipped,
        "max_parallel": args.max_parallel,
        "estimated_minutes_per_finding": 8,
    }

    out_path = target / "findings" / "_dispatch_plan.json"
    if not args.dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(plan, indent=2))
    print(json.dumps(plan, indent=2))
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    findings_dir = target / "findings"
    confirmed_ids = []
    failed_ids = []
    csp_blocked_ids = []
    for sub in sorted(findings_dir.glob("*")):
        if not sub.is_dir() or sub.name.startswith("_"):
            continue
        cid = sub.name
        c = sub / "confirmed.json"
        f = sub / "failed.json"
        if c.exists():
            confirmed_ids.append(cid)
            continue
        if f.exists():
            try:
                rec = json.loads(f.read_text())
                if (rec.get("outcome") or "").lower() == "csp_blocked":
                    csp_blocked_ids.append(cid)
                else:
                    failed_ids.append(cid)
            except json.JSONDecodeError:
                failed_ids.append(cid)

    # Prune queue
    queue_path = findings_dir / "_queue_browser_confirm.jsonl"
    drained = 0
    if queue_path.exists():
        processed = set(confirmed_ids) | set(failed_ids) | set(csp_blocked_ids)
        kept = []
        with queue_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                ls = line.strip()
                if not ls:
                    continue
                try:
                    rec = json.loads(ls)
                except json.JSONDecodeError:
                    kept.append(ls)
                    continue
                cid = str(rec.get("chain_id") or rec.get("id") or "")
                if cid in processed:
                    drained += 1
                    continue
                kept.append(ls)
        if drained and not args.dry_run:
            queue_path.write_text("\n".join(kept) + ("\n" if kept else ""))

    summary = {
        "ts": utcnow(),
        "target": target.name,
        "confirmed": confirmed_ids,
        "failed": failed_ids,
        "csp_blocked": csp_blocked_ids,
        "drained_from_queue": drained,
    }
    print(json.dumps(summary, indent=2))

    if not args.no_status and not args.dry_run:
        with status_lock(target) as data:
            phases = data.setdefault("phases", {})
            bc = phases.setdefault("browser_confirm", {})
            existing_c = set(bc.get("confirmed_ids", []))
            existing_f = set(bc.get("failed_ids", []))
            bc["confirmed_ids"] = sorted(existing_c | set(confirmed_ids))
            bc["failed_ids"] = sorted(existing_f | set(failed_ids))
            bc["csp_blocked_ids"] = sorted(set(bc.get("csp_blocked_ids", [])) | set(csp_blocked_ids))
            bc["ts"] = utcnow()

            phase = phases.setdefault("per_finding_session", {})
            phase.update(
                {
                    "status": "draining" if drained else "done",
                    "ts": utcnow(),
                    "confirmed": confirmed_ids,
                    "failed": failed_ids,
                    "csp_blocked": csp_blocked_ids,
                    "drained_from_queue": drained,
                }
            )
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="per-finding-session planner / collector")
    ap.add_argument("--target", required=True)
    ap.add_argument("--no-status", action="store_true")
    ap.add_argument("--dry-run", action="store_true")

    sub = ap.add_subparsers(dest="mode_cmd", required=True)

    plan = sub.add_parser("plan", help="Plan a dispatch batch")
    plan.add_argument("--mode", choices=("live", "mock"), help="Override default mode")
    plan.add_argument("--max-parallel", type=int, default=DEFAULT_MAX_PARALLEL)

    sub.add_parser("collect", help="Collect subagent outputs + prune queue")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.mode_cmd == "plan":
        return cmd_plan(args)
    if args.mode_cmd == "collect":
        return cmd_collect(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
