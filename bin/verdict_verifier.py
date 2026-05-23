#!/usr/bin/env python3
"""Two-judge verifier for cc-taint-adversarial verdicts.

Phase B emits ``opus/<chain_id>.json`` with the first auditor's
(triage, confidence). This script:

1. ``prepare`` — for each opus record where ``triage in {runtime}`` and
   ``confidence in {high, medium}``, render the verifier prompt body
   under ``two_judge/_prompts/<chain_id>.md``. Claude Code then
   dispatches one read-only subagent per prompt.
2. ``ingest`` — accept the subagent's JSON response, validate it, write
   ``two_judge/<chain_id>.json``. If the verifier emitted
   ``audit_quality != agree``, rewrite the opus record's ``triage`` /
   ``confidence`` to the verifier's recommendation AND patch the
   downstream queue file (``findings/_queue_browser_confirm.jsonl`` or
   ``_queue_mock_run.jsonl``) so the chain moves to the correct lane
   (or is dropped from the runtime queue and re-queued as
   ``_re_expand_queue.jsonl`` for evidence_gap).
3. ``finalize`` — roll counters into status.json.

Per the API-key whitelist (CLAUDE.md rule 7), this script does NOT call
any LLM. It only renders prompts + validates ingest payloads.

Reasons-first ordering is enforced in the prompt template
(``.claude/skills/cc-taint-adversarial/prompts/verifier.md``). The
ingest schema is loose on key order (Python dict preserves insertion
but JSON spec doesn't enforce it).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    resolve_target_dir,
    status_lock,
    utcnow,
)

_VERIFIER_TEMPLATE_REL = ".claude/skills/cc-taint-adversarial/prompts/verifier.md"

_REQUIRED_KEYS = {
    "chain_id",
    "issues_found",
    "reasoning",
    "audit_quality",
    "recommended_triage",
    "recommended_confidence",
    "verifier_confidence",
}
_VALID_AUDIT_QUALITY = {"agree", "downgrade", "flawed"}
_VALID_TRIAGE = {"runtime", "evidence_gap", "drop"}
_VALID_CONFIDENCE = {"high", "medium", "med", "low"}
_FORBIDDEN_KEYS = {
    "verdict",
    "tp",
    "fp",
    "true_positive",
    "false_positive",
    "severity",
}
_VALID_ISSUE_KINDS = {
    "exploit_argument_unverifiable_hop",
    "counterargument_strawman",
    "blocking_unknowns_decorative",
    "missing_blocking_unknown",
    "miscalibrated",
    "citation_mismatch",
}

_CONFIDENCE_RANK = {"low": 0, "medium": 1, "med": 1, "high": 2}


def _resolve_template() -> Path:
    return Path(__file__).resolve().parents[1] / _VERIFIER_TEMPLATE_REL


def _load_opus_records(opus_dir: Path) -> list[tuple[Path, dict]]:
    out: list[tuple[Path, dict]] = []
    if not opus_dir.exists():
        return out
    for p in sorted(opus_dir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        try:
            out.append((p, json.loads(p.read_text())))
        except json.JSONDecodeError:
            continue
    return out


def _load_chain_by_id(target: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name in ("chains/dom_reachable.jsonl", "chains/hot.jsonl", "chains/all.jsonl"):
        p = target / name
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                cid = rec.get("id") or rec.get("chain_id")
                if cid is not None and str(cid) not in out:
                    out[str(cid)] = rec
        if out:
            break
    return out


def _load_expanded(target: Path, chain_id) -> dict | None:
    p = target / "chains" / "expanded" / f"{chain_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def _render_prompt(template: str, *, target_name: str, payload: dict) -> str:
    body = template.replace("{{TARGET_NAME}}", target_name)
    return body.replace("{{VERIFIER_PAYLOAD}}", json.dumps(payload, indent=2))


def _is_verifiable(record: dict) -> bool:
    """Verifier runs on runtime/high and runtime/medium. drop/evidence_gap
    are not re-judged — a verifier never invents new TPs and the routing
    already handles those triages.
    """
    triage = (record.get("triage") or "").lower()
    confidence = (record.get("confidence") or "").lower()
    if triage != "runtime":
        return False
    return confidence in {"high", "medium", "med"}


def cmd_prepare(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    opus_dir = target / "opus"
    tj_dir = target / "two_judge"
    prompts_dir = tj_dir / "_prompts"

    template_path = (
        Path(args.prompt_template).resolve() if args.prompt_template else _resolve_template()
    )
    if not template_path.exists():
        print(f"error: verifier template missing: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text()

    chain_map = _load_chain_by_id(target)
    opus_records = _load_opus_records(opus_dir)

    if not opus_records:
        print("warn: no opus records found", file=sys.stderr)

    requested_ids = (
        {s.strip() for s in args.chain_ids.split(",") if s.strip()}
        if args.chain_ids
        else None
    )

    tj_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, dict] = {}
    skipped: list = []
    for opus_path, record in opus_records:
        cid = str(record.get("chain_id") or opus_path.stem)
        if requested_ids and cid not in requested_ids:
            continue
        if not _is_verifiable(record):
            skipped.append({"chain_id": cid, "reason": "non_runtime_or_low_conf"})
            continue

        chain = chain_map.get(cid, {"chain_id": cid})
        expanded = _load_expanded(target, cid) or {}

        payload = {
            "target_name": target.name,
            "chain": chain,
            "expanded": expanded,
            "auditor_record": {
                "exploit_argument": record.get("exploit_argument", ""),
                "counterargument": record.get("counterargument", ""),
                "blocking_unknowns": record.get("blocking_unknowns", []),
                "confidence": record.get("confidence", ""),
                "triage": record.get("triage", ""),
            },
        }
        body = _render_prompt(template, target_name=target.name, payload=payload)
        prompt_path = prompts_dir / f"{cid}.md"
        if not args.dry_run:
            prompt_path.write_text(body)
        manifest[cid] = {
            "chain_id": cid,
            "prompt_path": str(prompt_path.relative_to(target))
            if prompt_path.is_relative_to(target)
            else str(prompt_path),
            "auditor_triage": record.get("triage"),
            "auditor_confidence": record.get("confidence"),
            "status": "ready",
        }

    if not args.dry_run:
        (tj_dir / "_manifest.json").write_text(
            json.dumps(
                {"prepared_at": utcnow(), "chains": manifest, "skipped": skipped},
                indent=2,
            )
        )

    summary = {
        "prepared": len(manifest),
        "skipped": len(skipped),
        "dry_run": bool(args.dry_run),
        "output_dir": str(tj_dir),
    }
    print(json.dumps(summary, indent=2))

    if not args.no_status and not args.dry_run:
        with status_lock(target) as data:
            phases = data.setdefault("phases", {})
            phase = phases.setdefault("two_judge", {})
            phase.update(
                {
                    "status": "prepared",
                    "ts": utcnow(),
                    "prompts_ready": len(manifest),
                    "skipped": len(skipped),
                }
            )
    return 0


def _coerce_json_payload(raw: str) -> dict | None:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    try:
        out = json.loads(text)
        return out if isinstance(out, dict) else None
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            out = json.loads(text[start : end + 1])
            return out if isinstance(out, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _norm_conf(c: str) -> str:
    c = (c or "").lower()
    return "medium" if c == "med" else c


def _coerce_record(raw: dict, *, chain_id: str) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("response must be a JSON object")

    record = {k: v for k, v in raw.items() if k not in _FORBIDDEN_KEYS}
    dropped = sorted(k for k in raw if k in _FORBIDDEN_KEYS)

    record["chain_id"] = chain_id
    missing = _REQUIRED_KEYS - set(record.keys())
    if missing:
        raise ValueError(f"missing required keys: {sorted(missing)}")

    aq = str(record.get("audit_quality", "")).lower()
    if aq not in _VALID_AUDIT_QUALITY:
        raise ValueError(f"audit_quality must be agree/downgrade/flawed, got {aq!r}")
    record["audit_quality"] = aq

    rt = str(record.get("recommended_triage", "")).lower()
    if rt not in _VALID_TRIAGE:
        raise ValueError(f"recommended_triage invalid: {rt!r}")
    record["recommended_triage"] = rt

    rc = _norm_conf(record.get("recommended_confidence", ""))
    if rc not in _VALID_CONFIDENCE - {"med"}:
        raise ValueError(f"recommended_confidence invalid: {rc!r}")
    record["recommended_confidence"] = rc

    vc = _norm_conf(record.get("verifier_confidence", ""))
    if vc not in _VALID_CONFIDENCE - {"med"}:
        raise ValueError(f"verifier_confidence invalid: {vc!r}")
    record["verifier_confidence"] = vc

    issues = record.get("issues_found") or []
    if not isinstance(issues, list):
        raise ValueError("issues_found must be a list")
    cleaned_issues = []
    for it in issues:
        if not isinstance(it, dict):
            continue
        kind = str(it.get("kind", "")).strip()
        note = str(it.get("note", "")).strip()
        if kind not in _VALID_ISSUE_KINDS:
            continue
        cleaned_issues.append({"kind": kind, "note": note})
    record["issues_found"] = cleaned_issues

    record["reasoning"] = str(record.get("reasoning", "")).strip()
    if not record["reasoning"]:
        raise ValueError("reasoning must be non-empty")

    record["_ts"] = utcnow()
    if dropped:
        record["_stripped_keys"] = dropped
    return record


def _enforce_no_escalation(record: dict, auditor: dict) -> dict:
    """A verifier may agree or downgrade — never escalate.

    If audit_quality == agree, force recommended values to match the
    auditor's. If audit_quality != agree, ensure the new triage is not
    'runtime' AND new confidence is <= auditor's.
    """
    a_triage = (auditor.get("triage") or "").lower()
    a_conf = _norm_conf(auditor.get("confidence") or "")

    if record["audit_quality"] == "agree":
        record["recommended_triage"] = a_triage
        record["recommended_confidence"] = a_conf
        return record

    if record["recommended_triage"] == "runtime":
        record["recommended_triage"] = "evidence_gap"
        record.setdefault("_clamped", []).append(
            "triage was 'runtime' under non-agree audit_quality; clamped to evidence_gap"
        )

    a_rank = _CONFIDENCE_RANK.get(a_conf, 0)
    r_rank = _CONFIDENCE_RANK.get(record["recommended_confidence"], 0)
    if r_rank > a_rank:
        record["recommended_confidence"] = a_conf
        record.setdefault("_clamped", []).append(
            f"recommended_confidence > auditor; clamped to {a_conf}"
        )

    if record["audit_quality"] == "flawed" and record["recommended_confidence"] != "low":
        record["recommended_confidence"] = "low"
        record.setdefault("_clamped", []).append(
            "audit_quality=flawed forces recommended_confidence=low"
        )

    return record


def _rewrite_opus(opus_path: Path, verifier_record: dict, *, dry_run: bool) -> None:
    if dry_run:
        return
    try:
        rec = json.loads(opus_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return
    pre_triage = rec.get("triage")
    pre_conf = rec.get("confidence")
    rec["triage"] = verifier_record["recommended_triage"]
    rec["confidence"] = verifier_record["recommended_confidence"]
    history = rec.setdefault("_verifier_history", [])
    history.append(
        {
            "ts": utcnow(),
            "pre_triage": pre_triage,
            "pre_confidence": pre_conf,
            "audit_quality": verifier_record["audit_quality"],
            "issues": [it["kind"] for it in verifier_record["issues_found"]],
            "verifier_confidence": verifier_record["verifier_confidence"],
        }
    )
    opus_path.write_text(json.dumps(rec, indent=2))


def _strip_chain_from_queue(queue_path: Path, chain_id: str, *, dry_run: bool) -> int:
    if not queue_path.exists():
        return 0
    kept: list[str] = []
    removed = 0
    with queue_path.open("r", encoding="utf-8") as f:
        for line in f:
            ls = line.strip()
            if not ls:
                continue
            try:
                rec = json.loads(ls)
            except json.JSONDecodeError:
                kept.append(ls)
                continue
            cid = str(rec.get("chain_id") or rec.get("id") or "")
            if cid == chain_id:
                removed += 1
                continue
            kept.append(ls)
    if removed and not dry_run:
        queue_path.write_text("\n".join(kept) + ("\n" if kept else ""))
    return removed


def _append_queue(queue_path: Path, payload: dict, *, dry_run: bool) -> None:
    if dry_run:
        return
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def cmd_ingest(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    opus_dir = target / "opus"
    tj_dir = target / "two_judge"

    if args.response_file == "-":
        raw_text = sys.stdin.read()
    else:
        raw_text = Path(args.response_file).read_text()
    response = _coerce_json_payload(raw_text)
    if response is None:
        print("error: response is not valid JSON", file=sys.stderr)
        return 2

    auditor_path = opus_dir / f"{args.chain_id}.json"
    if not auditor_path.exists():
        print(f"error: auditor record not found: {auditor_path}", file=sys.stderr)
        return 2
    try:
        auditor = json.loads(auditor_path.read_text())
    except json.JSONDecodeError:
        print(f"error: auditor record not valid JSON: {auditor_path}", file=sys.stderr)
        return 2

    try:
        record = _coerce_record(response, chain_id=args.chain_id)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        append_status_error(target, "two_judge", e, chain_id=args.chain_id)
        return 2

    record = _enforce_no_escalation(record, auditor)

    tj_dir.mkdir(parents=True, exist_ok=True)
    out_path = tj_dir / f"{args.chain_id}.json"
    if not args.dry_run:
        out_path.write_text(json.dumps(record, indent=2))
    print(str(out_path))

    if record["audit_quality"] != "agree":
        _rewrite_opus(auditor_path, record, dry_run=args.dry_run)
        # Strip from runtime queues; re-add to evidence_gap queue if needed.
        q_browser = target / "findings" / "_queue_browser_confirm.jsonl"
        q_mock = target / "findings" / "_queue_mock_run.jsonl"
        q_reexpand = target / "chains" / "_re_expand_queue.jsonl"
        removed_browser = _strip_chain_from_queue(q_browser, args.chain_id, dry_run=args.dry_run)
        removed_mock = _strip_chain_from_queue(q_mock, args.chain_id, dry_run=args.dry_run)
        if record["recommended_triage"] == "evidence_gap":
            payload = {
                "chain_id": args.chain_id,
                "triage": "evidence_gap",
                "confidence": record["recommended_confidence"],
                "queued_at": utcnow(),
                "reason": "two_judge_downgrade",
                "hint": [it["note"] for it in record["issues_found"]][:5],
            }
            _append_queue(q_reexpand, payload, dry_run=args.dry_run)
        print(
            json.dumps(
                {
                    "downgraded": True,
                    "removed_browser_queue": removed_browser,
                    "removed_mock_queue": removed_mock,
                    "audit_quality": record["audit_quality"],
                    "new_triage": record["recommended_triage"],
                    "new_confidence": record["recommended_confidence"],
                },
                indent=2,
            )
        )

    if not args.no_status and not args.dry_run:
        with status_lock(target) as data:
            phases = data.setdefault("phases", {})
            phase = phases.setdefault("two_judge", {})
            counters = phase.setdefault(
                "counters",
                {"ingested": 0, "by_audit_quality": {}, "downgrades": 0},
            )
            counters["ingested"] = int(counters.get("ingested", 0)) + 1
            by_aq = counters.setdefault("by_audit_quality", {})
            by_aq[record["audit_quality"]] = int(by_aq.get(record["audit_quality"], 0)) + 1
            if record["audit_quality"] != "agree":
                counters["downgrades"] = int(counters.get("downgrades", 0)) + 1
            phase["ts"] = utcnow()
            phase["status"] = "ingesting"
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    tj_dir = target / "two_judge"
    if not tj_dir.exists():
        print(json.dumps({"total": 0}, indent=2))
        return 0
    records = []
    for p in sorted(tj_dir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        try:
            records.append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            continue
    summary = {
        "total": len(records),
        "by_audit_quality": {},
        "downgrades": 0,
        "by_recommended_triage": {},
    }
    for r in records:
        aq = r.get("audit_quality", "?")
        summary["by_audit_quality"][aq] = summary["by_audit_quality"].get(aq, 0) + 1
        if aq != "agree":
            summary["downgrades"] += 1
        rt = r.get("recommended_triage", "?")
        summary["by_recommended_triage"][rt] = summary["by_recommended_triage"].get(rt, 0) + 1
    print(json.dumps(summary, indent=2))

    if not args.no_status:
        with status_lock(target) as data:
            phases = data.setdefault("phases", {})
            phase = phases.setdefault("two_judge", {})
            phase.update(
                {"status": "done", "ts": utcnow(), "final_summary": summary}
            )
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Two-judge verifier for cc-taint-adversarial verdicts."
    )
    ap.add_argument("--target", required=True)
    ap.add_argument("--no-status", action="store_true")
    ap.add_argument("--dry-run", action="store_true")

    sub = ap.add_subparsers(dest="mode", required=True)

    prep = sub.add_parser("prepare", help="Render verifier prompts")
    prep.add_argument(
        "--chain-ids",
        help="Comma-separated subset of chain ids to verify (default: all runtime/high+medium)",
    )
    prep.add_argument("--prompt-template", help="Override verifier prompt template path")

    ing = sub.add_parser(
        "ingest", help="Validate + persist a verifier response for one chain"
    )
    ing.add_argument("--chain-id", required=True)
    ing.add_argument("--response-file", required=True, help="Path or '-' for stdin")

    sub.add_parser("finalize", help="Roll counters into status.json + print summary")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.mode == "prepare":
        return cmd_prepare(args)
    if args.mode == "ingest":
        return cmd_ingest(args)
    if args.mode == "finalize":
        return cmd_finalize(args)
    print(f"error: unknown mode {args.mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
