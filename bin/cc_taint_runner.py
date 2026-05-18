#!/usr/bin/env python3
"""Phase B helper for cc-taint-adversarial.

Per the API-key whitelist, this script does NOT call any LLM. It (a)
renders the adversarial prompt body per chain, (b) ingests the subagent
response and validates the schema before persisting to ``opus/<id>.json``.

The skill body (``.claude/skills/cc-taint-adversarial/SKILL.md``) is the
piece that actually dispatches the Agent tool — see that file for the
end-to-end flow.

Outputs:
* ``opus/_prompts/<chain_id>.md``     — per-chain prompt body
* ``opus/_manifest.json``             — chain id -> {prompt_path, status}
* ``opus/<chain_id>.json``            — final adversarial record, post-ingest
* ``status.json.phases.cc_taint_adversarial`` — running counters
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    pick_chain_input,
    resolve_target_dir,
    status_lock,
    utcnow,
)

_PROMPT_TEMPLATE_REL = ".claude/skills/cc-taint-adversarial/prompts/adversarial.md"
_REQUIRED_KEYS = {
    "chain_id", "exploit_argument", "counterargument",
    "blocking_unknowns", "confidence", "triage",
}
_VALID_CONFIDENCE = {"high", "medium", "med", "low"}
_VALID_TRIAGE = {"runtime", "evidence_gap", "drop"}

# Forbidden keys (verdict-laundering surface — would defeat the design).
_FORBIDDEN_KEYS = {
    "verdict", "tp", "fp", "true_positive", "false_positive",
    "classification", "severity",
}


def _resolve_template() -> Path:
    return Path(__file__).resolve().parents[1] / _PROMPT_TEMPLATE_REL


def _load_expanded(target: Path, chain_id) -> dict | None:
    p = target / "chains" / "expanded" / f"{chain_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def _load_anomalies(target: Path) -> dict[str, list[dict]]:
    """Return ``{chain_id_str: [anomaly, ...]}`` for chains referenced in any
    anomaly file under ``chains/anomalies/``.
    """
    out: dict[str, list[dict]] = {}
    anomalies_dir = target / "chains" / "anomalies"
    if not anomalies_dir.exists():
        return out
    for p in anomalies_dir.glob("*.json"):
        if p.name.startswith("_"):
            continue
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        for a in data.get("anomalies", []):
            for cid in a.get("affected_chains") or []:
                out.setdefault(str(cid), []).append(a)
    return out


def _iter_chains(input_path: Path) -> Iterable[dict]:
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _render_prompt(
    template: str,
    *,
    target_name: str,
    target_dir: str,
    chain: dict,
    expanded: dict,
    anomalies: list[dict],
) -> str:
    payload = {
        "target_name": target_name,
        "target_dir": target_dir,
        "chain": chain,
        "expanded": expanded,
        "anomalies": anomalies,
    }
    return template.replace("{{EVIDENCE_PAYLOAD}}", json.dumps(payload, indent=2))


def _filter_subset(chains: list[dict], wanted: list[str]) -> list[dict]:
    if not wanted:
        return chains
    want = {str(w) for w in wanted}
    return [c for c in chains if str(c.get("id") or c.get("chain_id")) in want]


def cmd_prepare(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)

    if args.chains_input:
        ci = Path(args.chains_input)
        chains_path = ci.resolve() if ci.is_absolute() else (target / ci).resolve()
    else:
        chains_path = pick_chain_input(target)
    if not chains_path or not Path(chains_path).exists():
        print("error: no chains input found", file=sys.stderr)
        return 2

    template_path = Path(args.prompt_template).resolve() if args.prompt_template else _resolve_template()
    if not template_path.exists():
        print(f"error: prompt template missing: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text()

    chains = _filter_subset(
        list(_iter_chains(Path(chains_path))),
        args.chain_ids.split(",") if args.chain_ids else [],
    )
    if not chains:
        print("warn: no chains to prepare", file=sys.stderr)

    opus_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else target / "opus"
    )
    prompts_dir = opus_dir / "_prompts"
    opus_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    anomalies_by_chain = _load_anomalies(target)
    manifest: dict[str, dict] = {}
    missing_expanded: list = []
    for chain in chains:
        cid = chain.get("id") or chain.get("chain_id")
        snip = _load_expanded(target, cid)
        if snip is None:
            missing_expanded.append(cid)
            continue
        anomalies = anomalies_by_chain.get(str(cid), [])
        body = _render_prompt(
            template,
            target_name=target.name,
            target_dir=str(target),
            chain=chain,
            expanded=snip,
            anomalies=anomalies,
        )
        prompt_path = prompts_dir / f"{cid}.md"
        if not args.dry_run:
            prompt_path.write_text(body)
        manifest[str(cid)] = {
            "chain_id": cid,
            "prompt_path": str(prompt_path.relative_to(target))
            if prompt_path.is_relative_to(target) else str(prompt_path),
            "anomaly_count": len(anomalies),
            "status": "ready",
        }

    if not args.dry_run:
        (opus_dir / "_manifest.json").write_text(
            json.dumps({"prepared_at": utcnow(), "chains": manifest}, indent=2)
        )

    summary = {
        "prepared": len(manifest),
        "missing_expanded": missing_expanded,
        "dry_run": bool(args.dry_run),
        "output_dir": str(opus_dir),
    }
    print(json.dumps(summary, indent=2))

    if not args.no_status and not args.dry_run:
        with status_lock(target) as data:
            phases = data.setdefault("phases", {})
            phase = phases.setdefault("cc_taint_adversarial", {})
            phase.update(
                {
                    "status": "prepared",
                    "ts": utcnow(),
                    "prompts_ready": len(manifest),
                    "missing_expanded": missing_expanded[:20],
                }
            )
    return 0


def _coerce_json_payload(raw: str) -> dict | None:
    """Accept plain JSON, ```json``` fenced JSON, or a JSON object embedded
    in prose. Returns parsed dict or None."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text[: -3]
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


def _coerce_record(raw: dict, *, chain_id) -> dict:
    """Validate + normalise a subagent response into an opus record."""
    if not isinstance(raw, dict):
        raise ValueError("response must be a JSON object")

    record = {k: v for k, v in raw.items() if k not in _FORBIDDEN_KEYS}
    dropped = sorted(k for k in raw if k in _FORBIDDEN_KEYS)

    # Force chain_id to match the manifest.
    record["chain_id"] = chain_id

    missing = _REQUIRED_KEYS - set(record.keys())
    if missing:
        raise ValueError(f"missing required keys: {sorted(missing)}")

    conf = str(record.get("confidence", "")).lower()
    if conf == "med":
        conf = "medium"
    if conf not in _VALID_CONFIDENCE:
        raise ValueError(f"confidence must be one of high/medium/low, got: {conf!r}")
    record["confidence"] = conf

    triage = str(record.get("triage", "")).lower()
    if triage not in _VALID_TRIAGE:
        raise ValueError(f"triage must be one of runtime/evidence_gap/drop, got: {triage!r}")
    record["triage"] = triage

    bu = record.get("blocking_unknowns") or []
    if not isinstance(bu, list):
        raise ValueError("blocking_unknowns must be a list")
    record["blocking_unknowns"] = [str(x) for x in bu if x]

    record["exploit_argument"] = str(record.get("exploit_argument", "")).strip()
    record["counterargument"] = str(record.get("counterargument", "")).strip()
    if not record["exploit_argument"] or not record["counterargument"]:
        raise ValueError("exploit_argument and counterargument must be non-empty strings")

    record["_ts"] = utcnow()
    if dropped:
        record["_stripped_keys"] = dropped
    return record


def cmd_ingest(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    opus_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else target / "opus"
    )

    if args.response_file == "-":
        raw_text = sys.stdin.read()
    else:
        raw_text = Path(args.response_file).read_text()
    response = _coerce_json_payload(raw_text)
    if response is None:
        print("error: response is not valid JSON (no JSON object detected)", file=sys.stderr)
        return 2

    try:
        record = _coerce_record(response, chain_id=args.chain_id)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        append_status_error(target, "cc-taint-adversarial", e, chain_id=args.chain_id)
        return 2

    opus_dir.mkdir(parents=True, exist_ok=True)
    out_path = opus_dir / f"{args.chain_id}.json"
    out_path.write_text(json.dumps(record, indent=2))
    print(str(out_path))

    if not args.no_status:
        with status_lock(target) as data:
            phases = data.setdefault("phases", {})
            phase = phases.setdefault("cc_taint_adversarial", {})
            counters = phase.setdefault(
                "counters", {"ingested": 0, "by_triage": {}, "by_confidence": {}}
            )
            counters["ingested"] = int(counters.get("ingested", 0)) + 1
            by_triage = counters.setdefault("by_triage", {})
            by_triage[record["triage"]] = int(by_triage.get(record["triage"], 0)) + 1
            by_conf = counters.setdefault("by_confidence", {})
            by_conf[record["confidence"]] = int(by_conf.get(record["confidence"], 0)) + 1
            phase["ts"] = utcnow()
            phase["status"] = "ingesting"
            phase["subagent_count"] = int(phase.get("subagent_count", 0)) + 1
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    opus_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else target / "opus"
    )
    records = []
    for p in opus_dir.glob("*.json"):
        if p.name.startswith("_"):
            continue
        try:
            records.append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            continue
    summary = {"total": len(records), "by_triage": {}, "by_confidence": {}}
    for r in records:
        summary["by_triage"][r.get("triage", "?")] = (
            summary["by_triage"].get(r.get("triage", "?"), 0) + 1
        )
        summary["by_confidence"][r.get("confidence", "?")] = (
            summary["by_confidence"].get(r.get("confidence", "?"), 0) + 1
        )
    print(json.dumps(summary, indent=2))

    if not args.no_status:
        with status_lock(target) as data:
            phases = data.setdefault("phases", {})
            phase = phases.setdefault("cc_taint_adversarial", {})
            phase.update(
                {
                    "status": "done",
                    "ts": utcnow(),
                    "final_summary": summary,
                }
            )
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="cc-taint-adversarial runner (prep + ingest helpers).")
    ap.add_argument("--target", required=True)
    ap.add_argument("--output-dir", help="Override opus/ output dir")
    ap.add_argument("--no-status", action="store_true")

    sub = ap.add_subparsers(dest="mode", required=True)

    prep = sub.add_parser("prepare", help="Render per-chain prompts")
    prep.add_argument("--chains-input", help="Default: chains/dom_reachable.jsonl, fallback hot.jsonl")
    prep.add_argument("--chain-ids", help="Comma-separated subset of chain ids to prep")
    prep.add_argument("--prompt-template", help="Override adversarial prompt template path")
    prep.add_argument("--dry-run", action="store_true")

    ing = sub.add_parser("ingest", help="Validate + persist a subagent response for one chain")
    ing.add_argument("--chain-id", required=True)
    ing.add_argument("--response-file", required=True, help="Path to JSON file or '-' for stdin")

    sub.add_parser("finalize", help="Roll counters into status.json and print summary")
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
