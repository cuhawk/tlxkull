#!/usr/bin/env python3
"""Phase C of cc-taint-adversarial: route opus/<id>.json records to the
appropriate downstream queue.

Routing rules (per plans/CC_TAINT_ADVERSARIAL.md):

| triage         | confidence | destination |
| -------------- | ---------- | ----------- |
| ``runtime``    | ``high``   | ``findings/_queue_browser_confirm.jsonl`` |
| ``runtime``    | ``medium`` | ``findings/_queue_mock_run.jsonl`` |
| ``runtime``    | ``low``    | ``findings/_queue_mock_run.jsonl`` (low gets mock-only) |
| ``evidence_gap`` | any      | ``chains/_re_expand_queue.jsonl`` (cap ``retries`` ≤ 2) |
| ``drop``       | any        | ``chains/_fp_archive.jsonl`` |

Idempotency: re-running must not duplicate queue entries. Each queue file
is keyed by ``chain_id``; entries already present are skipped (and counted
in ``status.json.phases.cc_taint_route.skipped_existing``).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    pick_chain_input,
    resolve_target_dir,
    utcnow,
    write_status_phase,
)

MAX_RETRIES = 2

QUEUE_BROWSER = "findings/_queue_browser_confirm.jsonl"
QUEUE_MOCK    = "findings/_queue_mock_run.jsonl"
QUEUE_REEXPAND = "chains/_re_expand_queue.jsonl"
ARCHIVE_FP    = "chains/_fp_archive.jsonl"


def _read_chain_map(target: Path, chains_input: str | None) -> dict[str, dict]:
    if chains_input:
        ci = Path(chains_input)
        path = ci.resolve() if ci.is_absolute() else (target / ci).resolve()
    else:
        path = pick_chain_input(target)
    if not path or not Path(path).exists():
        return {}
    out: dict[str, dict] = {}
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = rec.get("id") or rec.get("chain_id")
            if cid is not None:
                out[str(cid)] = rec
    return out


def _read_queue_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = rec.get("chain_id") or rec.get("id")
            if cid is not None:
                out.add(str(cid))
    return out


def _append(path: Path, payload: dict, *, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def _bump_retries(opus_path: Path, dry_run: bool) -> int:
    """Increment ``retries`` on the opus record and return the new count."""
    try:
        rec = json.loads(opus_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return 0
    new = int(rec.get("retries", 0)) + 1
    if not dry_run:
        rec["retries"] = new
        opus_path.write_text(json.dumps(rec, indent=2))
    return new


def _iter_opus_records(opus_dir: Path) -> Iterable[tuple[Path, dict]]:
    for p in sorted(opus_dir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        try:
            yield p, json.loads(p.read_text())
        except json.JSONDecodeError:
            continue


def route(target: Path, *, chains_input: str | None, dry_run: bool) -> dict:
    opus_dir = target / "opus"
    if not opus_dir.exists():
        return {"error": "opus/ dir missing — run cc-taint-adversarial first"}

    chain_map = _read_chain_map(target, chains_input)

    queues = {
        "browser_confirm": target / QUEUE_BROWSER,
        "mock_run":        target / QUEUE_MOCK,
        "re_expand":       target / QUEUE_REEXPAND,
        "fp_archive":      target / ARCHIVE_FP,
    }
    existing = {k: _read_queue_ids(p) for k, p in queues.items()}

    counters: dict[str, int] = {
        "browser_confirm": 0,
        "mock_run": 0,
        "re_expand": 0,
        "fp_archive": 0,
        "retries_exceeded": 0,
        "skipped_existing": 0,
        "missing_chain_payload": 0,
        "considered": 0,
    }

    for opus_path, record in _iter_opus_records(opus_dir):
        counters["considered"] += 1
        cid = str(record.get("chain_id") or opus_path.stem)
        triage = (record.get("triage") or "").lower()
        confidence = (record.get("confidence") or "").lower()
        chain = chain_map.get(cid)

        # All routes need the original chain payload to be useful downstream.
        if chain is None and triage != "evidence_gap":
            counters["missing_chain_payload"] += 1
            chain = {"chain_id": cid}

        payload_base = {
            "chain_id": cid,
            "triage": triage,
            "confidence": confidence,
            "opus_record": str(opus_path.relative_to(target))
            if opus_path.is_relative_to(target) else str(opus_path),
            "queued_at": utcnow(),
        }
        if chain:
            payload_base["chain"] = chain

        if triage == "runtime" and confidence == "high":
            if cid in existing["browser_confirm"]:
                counters["skipped_existing"] += 1
                continue
            _append(queues["browser_confirm"], payload_base, dry_run=dry_run)
            existing["browser_confirm"].add(cid)
            counters["browser_confirm"] += 1
        elif triage == "runtime":
            if cid in existing["mock_run"]:
                counters["skipped_existing"] += 1
                continue
            _append(queues["mock_run"], payload_base, dry_run=dry_run)
            existing["mock_run"].add(cid)
            counters["mock_run"] += 1
        elif triage == "evidence_gap":
            current_retries = int(record.get("retries", 0))
            if current_retries >= MAX_RETRIES:
                counters["retries_exceeded"] += 1
                # Park alongside FP archive so a human can review.
                if cid not in existing["fp_archive"]:
                    parked = {**payload_base, "reason": "evidence_gap_max_retries"}
                    _append(queues["fp_archive"], parked, dry_run=dry_run)
                    existing["fp_archive"].add(cid)
                continue
            if cid in existing["re_expand"]:
                counters["skipped_existing"] += 1
                continue
            new_retries = _bump_retries(opus_path, dry_run=dry_run)
            hint_payload = {
                **payload_base,
                "hint": record.get("blocking_unknowns") or [],
                "retries": new_retries,
                "max_retries": MAX_RETRIES,
            }
            _append(queues["re_expand"], hint_payload, dry_run=dry_run)
            existing["re_expand"].add(cid)
            counters["re_expand"] += 1
        elif triage == "drop":
            if cid in existing["fp_archive"]:
                counters["skipped_existing"] += 1
                continue
            _append(queues["fp_archive"], payload_base, dry_run=dry_run)
            existing["fp_archive"].add(cid)
            counters["fp_archive"] += 1
        else:
            counters.setdefault("unknown_triage", 0)
            counters["unknown_triage"] += 1

    return {
        "counters": counters,
        "queues": {k: str(v.relative_to(target)) if v.is_relative_to(target) else str(v)
                   for k, v in queues.items()},
        "dry_run": dry_run,
    }


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Route opus/ records into runtime + re-expand queues.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--chains-input", help="Default: chains/dom_reachable.jsonl, fallback hot.jsonl")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-status", action="store_true")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    target = resolve_target_dir(args.target)
    summary = route(target, chains_input=args.chains_input, dry_run=args.dry_run)
    print(json.dumps(summary, indent=2))

    if not args.no_status and not args.dry_run and "error" not in summary:
        write_status_phase(
            target,
            "cc_taint_route",
            {
                "status": "done",
                "ts": utcnow(),
                "counters": summary["counters"],
                "queues": summary["queues"],
            },
        )
    return 0 if "error" not in summary else 2


if __name__ == "__main__":
    sys.exit(main())
