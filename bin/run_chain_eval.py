#!/usr/bin/env python3
"""Chain audit eval runner.

Two-phase runner for `evals/chain_audit/{control,edge,boundary}.jsonl`.
Same prepare/ingest pattern as cc-taint-adversarial — Python renders
prompts and validates responses; Claude Code dispatches the subagents.

Phases:
* ``prepare`` — render the adversarial prompt for every eval entry to
  ``evals/chain_audit/_runs/<utc>/_prompts/<bucket>__<name>.md``.
* ``score``   — read JSON responses from
  ``_runs/<utc>/_responses/<bucket>__<name>.json``, compare to expected
  triage + confidence, emit ``score.json`` + ``score.md`` plus a delta
  vs the previous run.

Per API-key whitelist, this script does NOT call any LLM.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, utcnow  # noqa: E402

EVAL_DIR = ROOT / "evals" / "chain_audit"
BUCKETS = ("control", "edge", "boundary")
_PROMPT_TEMPLATE_REL = ".claude/skills/cc-taint-adversarial/prompts/adversarial.md"

_VALID_TRIAGE = {"runtime", "evidence_gap", "drop"}
_VALID_CONFIDENCE = {"high", "medium", "med", "low"}
_CONFIDENCE_RANK = {"low": 0, "medium": 1, "med": 1, "high": 2}


def _resolve_template() -> Path:
    return ROOT / _PROMPT_TEMPLATE_REL


def _load_bucket(name: str) -> list[dict]:
    p = EVAL_DIR / f"{name}.jsonl"
    if not p.exists():
        return []
    entries = []
    for line_no, line in enumerate(p.read_text().splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(
                f"warn: {name}.jsonl:{line_no} invalid JSON ({e}); skipped",
                file=sys.stderr,
            )
    return entries


def _validate_entry(entry: dict, bucket: str) -> list[str]:
    errs = []
    for k in ("name", "chain", "expanded", "expected_triage", "expected_confidence"):
        if k not in entry:
            errs.append(f"missing key: {k}")
    if "expected_triage" in entry and entry["expected_triage"] not in _VALID_TRIAGE:
        errs.append(f"expected_triage invalid: {entry['expected_triage']}")
    if "expected_confidence" in entry and entry["expected_confidence"] not in _VALID_CONFIDENCE:
        errs.append(f"expected_confidence invalid: {entry['expected_confidence']}")
    # Bucket consistency checks
    if not errs:
        et = entry["expected_triage"]
        if bucket == "control" and et != "runtime":
            errs.append(f"control bucket entry should expect runtime, got {et}")
        elif bucket == "edge" and et != "drop":
            errs.append(f"edge bucket entry should expect drop, got {et}")
        elif bucket == "boundary" and et != "evidence_gap":
            errs.append(f"boundary bucket entry should expect evidence_gap, got {et}")
    return errs


def _render_prompt(template: str, *, entry: dict) -> str:
    payload = {
        "target_name": entry.get("source_target", "eval"),
        "target_dir": "evals/chain_audit",
        "chain": entry["chain"],
        "expanded": entry["expanded"],
        "anomalies": entry.get("anomalies", []),
    }
    return template.replace("{{EVIDENCE_PAYLOAD}}", json.dumps(payload, indent=2))


def cmd_prepare(args: argparse.Namespace) -> int:
    template_path = _resolve_template()
    if not template_path.exists():
        print(f"error: prompt template missing: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text()

    buckets = list(BUCKETS) if args.bucket == "all" else [args.bucket]
    run_id = utcnow().replace(":", "").replace("-", "")
    run_dir = EVAL_DIR / "_runs" / run_id
    prompts_dir = run_dir / "_prompts"
    if not args.dry_run:
        prompts_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, dict] = {}
    issues: list[str] = []
    for bucket in buckets:
        entries = _load_bucket(bucket)
        for entry in entries:
            errs = _validate_entry(entry, bucket)
            if errs:
                issues.extend([f"{bucket}::{entry.get('name', '?')}: {e}" for e in errs])
                continue
            body = _render_prompt(template, entry=entry)
            stem = f"{bucket}__{entry['name']}"
            prompt_path = prompts_dir / f"{stem}.md"
            if not args.dry_run:
                prompt_path.write_text(body)
            manifest[stem] = {
                "bucket": bucket,
                "name": entry["name"],
                "source_target": entry.get("source_target"),
                "expected_triage": entry["expected_triage"],
                "expected_confidence": entry["expected_confidence"],
                "prompt_path": str(prompt_path.relative_to(EVAL_DIR.parent.parent))
                if prompt_path.is_relative_to(EVAL_DIR.parent.parent)
                else str(prompt_path),
                "notes": entry.get("notes", ""),
            }

    if not args.dry_run:
        (run_dir / "_manifest.json").write_text(
            json.dumps(
                {
                    "prepared_at": utcnow(),
                    "run_id": run_id,
                    "buckets": buckets,
                    "entries": manifest,
                    "issues": issues,
                },
                indent=2,
            )
        )

    summary = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "prepared": len(manifest),
        "skipped_with_issues": len(issues),
        "dry_run": bool(args.dry_run),
    }
    if issues and args.verbose:
        summary["issues"] = issues
    print(json.dumps(summary, indent=2))
    return 0


def _norm_conf(c: str) -> str:
    c = (c or "").lower()
    return "medium" if c == "med" else c


def _read_response(run_dir: Path, stem: str) -> dict | None:
    p = run_dir / "_responses" / f"{stem}.json"
    if not p.exists():
        return None
    try:
        raw = json.loads(p.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(raw, dict):
        return None
    return raw


def _grade(expected_triage: str, expected_conf: str, response: dict) -> dict:
    got_triage = (response.get("triage") or "").lower()
    got_conf = _norm_conf(response.get("confidence") or "")
    triage_ok = got_triage == expected_triage
    # For confidence: control + edge are strict; boundary allows any
    # confidence as long as triage matches (it's about refusal, not
    # high/medium specifically).
    if expected_triage == "evidence_gap":
        conf_ok = True
    else:
        conf_ok = got_conf == _norm_conf(expected_conf)
    return {
        "got_triage": got_triage,
        "got_confidence": got_conf,
        "triage_ok": triage_ok,
        "confidence_ok": conf_ok,
        "pass": triage_ok and conf_ok,
    }


def _latest_prior_run(run_dir: Path) -> Path | None:
    parent = run_dir.parent
    candidates = sorted(
        [p for p in parent.iterdir() if p.is_dir() and p.name != run_dir.name and (p / "score.json").exists()]
    )
    return candidates[-1] if candidates else None


def cmd_score(args: argparse.Namespace) -> int:
    run_dir = EVAL_DIR / "_runs" / args.run
    if not run_dir.exists():
        print(f"error: run not found: {run_dir}", file=sys.stderr)
        return 2
    manifest_path = run_dir / "_manifest.json"
    if not manifest_path.exists():
        print(f"error: manifest missing: {manifest_path}", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text())

    by_bucket: dict[str, dict] = {b: {"total": 0, "passed": 0, "missing": 0, "entries": []} for b in BUCKETS}
    for stem, meta in manifest.get("entries", {}).items():
        bucket = meta["bucket"]
        by_bucket[bucket]["total"] += 1
        response = _read_response(run_dir, stem)
        if response is None:
            by_bucket[bucket]["missing"] += 1
            by_bucket[bucket]["entries"].append(
                {
                    "name": meta["name"],
                    "missing": True,
                    "expected_triage": meta["expected_triage"],
                    "expected_confidence": meta["expected_confidence"],
                }
            )
            continue
        grade = _grade(meta["expected_triage"], meta["expected_confidence"], response)
        if grade["pass"]:
            by_bucket[bucket]["passed"] += 1
        by_bucket[bucket]["entries"].append(
            {
                "name": meta["name"],
                **grade,
                "expected_triage": meta["expected_triage"],
                "expected_confidence": meta["expected_confidence"],
            }
        )

    summary = {
        "run_id": args.run,
        "scored_at": utcnow(),
        "by_bucket": {
            b: {
                "total": by_bucket[b]["total"],
                "passed": by_bucket[b]["passed"],
                "missing": by_bucket[b]["missing"],
                "pass_rate": (by_bucket[b]["passed"] / by_bucket[b]["total"])
                if by_bucket[b]["total"]
                else 0.0,
            }
            for b in BUCKETS
        },
    }

    # Delta vs prior run
    prior_dir = _latest_prior_run(run_dir)
    if prior_dir:
        try:
            prior_summary = json.loads((prior_dir / "score.json").read_text())
            summary["delta_vs"] = prior_dir.name
            summary["deltas"] = {}
            for b in BUCKETS:
                cur = summary["by_bucket"][b]["pass_rate"]
                pri = prior_summary.get("by_bucket", {}).get(b, {}).get("pass_rate", 0.0)
                summary["deltas"][b] = round(cur - pri, 4)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    score_path = run_dir / "score.json"
    score_path.write_text(json.dumps({**summary, "by_bucket_detail": by_bucket}, indent=2))

    # Markdown summary
    md = ["# Chain audit eval — run " + args.run, ""]
    for b in BUCKETS:
        d = summary["by_bucket"][b]
        md.append(
            f"- **{b}** — {d['passed']}/{d['total']} pass ({d['pass_rate']:.0%}), missing: {d['missing']}"
        )
    if "deltas" in summary:
        md.append("")
        md.append("## Delta vs " + summary["delta_vs"])
        for b in BUCKETS:
            arrow = "↑" if summary["deltas"][b] > 0 else ("↓" if summary["deltas"][b] < 0 else "→")
            md.append(f"- {b}: {arrow} {summary['deltas'][b]:+.0%}")
    md.append("")
    md.append("## Failures")
    any_fail = False
    for b in BUCKETS:
        for e in by_bucket[b]["entries"]:
            if e.get("missing") or not e.get("pass", False):
                any_fail = True
                if e.get("missing"):
                    md.append(f"- {b}/{e['name']}: response missing")
                else:
                    md.append(
                        f"- {b}/{e['name']}: expected {e['expected_triage']}/{e['expected_confidence']}, got {e['got_triage']}/{e['got_confidence']}"
                    )
    if not any_fail:
        md.append("- _(none)_")
    (run_dir / "score.md").write_text("\n".join(md) + "\n")

    print(json.dumps(summary, indent=2))
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Chain audit eval runner.")
    sub = ap.add_subparsers(dest="mode", required=True)

    prep = sub.add_parser("prepare", help="Render eval prompts")
    prep.add_argument(
        "--bucket",
        default="all",
        choices=("all",) + BUCKETS,
        help="Which bucket(s) to render (default: all)",
    )
    prep.add_argument("--dry-run", action="store_true")
    prep.add_argument("--verbose", action="store_true")

    score = sub.add_parser("score", help="Grade responses from a prepared run")
    score.add_argument("--run", required=True, help="Run id from prepare (the UTC stem)")

    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.mode == "prepare":
        return cmd_prepare(args)
    if args.mode == "score":
        return cmd_score(args)
    print(f"error: unknown mode {args.mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
