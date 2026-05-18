#!/usr/bin/env python3
"""Phase A of cc-taint-adversarial: bucket chains by sink file and prepare
prompt bundles for a Claude Code subagent.

Per CLAUDE.md API-key whitelist, this script does NOT call any LLM. It
prepares per-bucket prompts (snippets + sibling-function list from the
per-target DB) and ingests subagent JSON responses, stripping any verdict
keys to enforce the "anomalies are not verdicts" contract.

Outputs:
* ``chains/anomalies/_prompts/<slug>.md``    — the per-bucket prompt body
* ``chains/anomalies/_manifest.json``        — bucket -> {slug, chains, prompt_path}
* ``chains/anomalies/<slug>.json``           — final anomaly record, post-ingest

Flow (driven by the cc-taint-adversarial skill):
1. ``--prepare`` reads ``chains/dom_reachable.jsonl`` (or override via
   ``--chains-input``) and ``chains/expanded/<id>.json`` for each chain.
2. Skill iterates buckets, dispatches one subagent per bucket with the
   prompt body, captures the JSON response.
3. ``--ingest --bucket <slug> --response-file <path>`` strips verdict keys
   and writes the final anomaly JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    per_target_db,
    pick_chain_input,
    resolve_target_dir,
    utcnow,
    write_status_phase,
)

# Forbidden top-level keys in a Phase A anomaly record. The bucket subagent
# must surface divergence, never verdicts. Anything matching these patterns
# in a response payload is dropped before the file is persisted.
_VERDICT_KEYS = frozenset({
    "verdict", "verdicts",
    "tp", "fp", "tps", "fps",
    "classification", "classifications",
    "true_positive", "false_positive",
    "confidence", "severity",
    "triage",
})

_ALLOWED_ANOMALY_TYPES = frozenset({
    "missing_guard_vs_peers",
    "sanitizer_inconsistency",
    "auth_gap",
    "copy_paste_drift",
    "sibling_divergence",
})

_PROMPT_TEMPLATE_REL = ".claude/skills/cc-taint-adversarial/prompts/bucket_anomaly.md"


def _slug(s: str) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "bucket"
    if len(base) > 60:
        h = hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]
        base = base[:60] + "-" + h
    return base


def _connect_ro(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _siblings_for_file(conn: sqlite3.Connection, file_rel: str) -> list[dict]:
    rows = conn.execute(
        "SELECT qualified_name, name, kind, start_line, end_line"
        " FROM nodes WHERE file = ? AND kind IN ('function','method','arrow','program')"
        " ORDER BY start_line",
        (file_rel,),
    ).fetchall()
    return [
        {
            "qname": r["qualified_name"],
            "name": r["name"],
            "kind": r["kind"],
            "lines": [r["start_line"], r["end_line"]],
        }
        for r in rows
    ]


def _load_expanded(target: Path, chain_id) -> dict | None:
    p = target / "chains" / "expanded" / f"{chain_id}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def _bucket_chains(chains: Iterable[dict]) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = {}
    for c in chains:
        sink = c.get("sink") or {}
        file_rel = sink.get("file") or "_no_file"
        buckets.setdefault(file_rel, []).append(c)
    return buckets


def _resolve_template(target: Path) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    p = repo_root / _PROMPT_TEMPLATE_REL
    return p


def _render_prompt(
    template: str,
    *,
    bucket_file: str,
    chains: list[dict],
    expanded: list[dict],
    siblings: list[dict],
    byte_budget: int,
) -> str:
    payload = {
        "bucket_file": bucket_file,
        "chain_ids": [c.get("id") or c.get("chain_id") for c in chains],
        "expanded_snippets": expanded,
        "siblings": siblings,
    }
    block = json.dumps(payload, indent=2)
    if len(block) > byte_budget:
        # Trim caller bodies in the expanded snippets to fit. Keep source/sink
        # full-fidelity; this mirrors expand_snippet._apply_budget's strategy.
        trimmed = []
        for snip in expanded:
            new = dict(snip)
            new_callers = []
            for c in new.get("callers", []):
                nc = dict(c)
                nc["code"] = (c.get("code", "")[:300]).rstrip() + "\n  /* elided */"
                new_callers.append(nc)
            new["callers"] = new_callers
            trimmed.append(new)
        payload["expanded_snippets"] = trimmed
        block = json.dumps(payload, indent=2)
    return template.replace("{{BUCKET_PAYLOAD}}", block)


def _coerce_json_payload(raw: str) -> dict | None:
    """Accept either a plain JSON object or a markdown-fenced one. Returns
    the parsed dict, or None if no top-level object is recoverable."""
    text = raw.strip()
    # Strip a leading ```json (or ```) fence if present.
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
    # Last resort: find the first balanced { ... } block.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            out = json.loads(text[start : end + 1])
            return out if isinstance(out, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _strip_verdicts(response: dict, *, bucket: str) -> dict:
    """Drop any verdict-flavoured keys and enforce schema.

    Returns: ``{bucket, chains_seen, anomalies[]}``.
    """
    chains_seen = response.get("chains_seen") or []
    anomalies_in = response.get("anomalies") or []
    anomalies_out: list[dict] = []
    dropped: list[str] = []

    def _clean(d: dict) -> dict:
        clean = {}
        for k, v in d.items():
            if k.lower() in _VERDICT_KEYS:
                dropped.append(k)
                continue
            clean[k] = v
        return clean

    for raw in anomalies_in:
        if not isinstance(raw, dict):
            continue
        a = _clean(raw)
        a_type = a.get("type") or a.get("kind")
        if a_type not in _ALLOWED_ANOMALY_TYPES:
            a["type"] = "sibling_divergence"
        elif "type" not in a:
            a["type"] = a_type
        evidence = a.get("evidence") or a.get("description") or ""
        affected = a.get("affected_chains") or []
        anomalies_out.append(
            {
                "type": a["type"],
                "evidence": str(evidence)[:1000],
                "affected_chains": [x for x in affected if x],
            }
        )

    out = {
        "bucket": response.get("bucket") or bucket,
        "chains_seen": chains_seen,
        "anomalies": anomalies_out,
    }
    if dropped:
        out["_stripped_keys"] = sorted(set(dropped))
    return out


def cmd_prepare(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    db_path = Path(args.db).resolve() if args.db else per_target_db(target)

    if args.chains_input:
        ci = Path(args.chains_input)
        chains_path = ci.resolve() if ci.is_absolute() else (target / ci).resolve()
    else:
        chains_path = pick_chain_input(target)
    if not chains_path or not Path(chains_path).exists():
        print("error: no chains input (dom_reachable.jsonl / hot.jsonl)", file=sys.stderr)
        return 2

    with Path(chains_path).open("r", encoding="utf-8") as f:
        all_chains = [json.loads(line) for line in f if line.strip()]
    if not all_chains:
        print("warn: no chains in input", file=sys.stderr)

    buckets = _bucket_chains(all_chains)
    if not buckets:
        print(json.dumps({"buckets": 0, "chains": 0}))
        return 0

    template_path = Path(args.prompt_template).resolve() if args.prompt_template else _resolve_template(target)
    template = template_path.read_text() if template_path.exists() else (
        "Bucket anomaly prompt template missing.\n\nPayload:\n{{BUCKET_PAYLOAD}}\n"
    )

    out_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else target / "chains" / "anomalies"
    )
    prompts_dir = out_dir / "_prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)

    conn = _connect_ro(db_path)
    manifest: dict[str, dict] = {}
    missing_expanded: list = []
    try:
        for file_rel, chains in sorted(buckets.items()):
            slug = _slug(file_rel)
            chain_ids = [c.get("id") or c.get("chain_id") for c in chains]
            expanded = []
            for cid in chain_ids:
                snip = _load_expanded(target, cid)
                if snip is None:
                    missing_expanded.append(cid)
                else:
                    expanded.append(snip)
            siblings = _siblings_for_file(conn, file_rel)
            body = _render_prompt(
                template,
                bucket_file=file_rel,
                chains=chains,
                expanded=expanded,
                siblings=siblings,
                byte_budget=args.byte_budget,
            )
            prompt_path = prompts_dir / f"{slug}.md"
            if not args.dry_run:
                prompt_path.write_text(body)
            manifest[file_rel] = {
                "slug": slug,
                "chains": chain_ids,
                "chain_count": len(chain_ids),
                "siblings_count": len(siblings),
                "expanded_loaded": len(expanded),
                "prompt_path": str(prompt_path.relative_to(target))
                if prompt_path.is_relative_to(target)
                else str(prompt_path),
            }
    finally:
        conn.close()

    if not args.dry_run:
        (out_dir / "_manifest.json").write_text(
            json.dumps({"prepared_at": utcnow(), "buckets": manifest}, indent=2)
        )

    summary = {
        "buckets": len(manifest),
        "chains": sum(b["chain_count"] for b in manifest.values()),
        "missing_expanded": missing_expanded,
        "dry_run": bool(args.dry_run),
        "output_dir": str(out_dir),
    }
    print(json.dumps(summary, indent=2))

    if not args.no_status and not args.dry_run:
        write_status_phase(
            target,
            "cc_taint_bucket_prep",
            {
                "status": "done",
                "ts": utcnow(),
                "buckets": summary["buckets"],
                "chains": summary["chains"],
                "missing_expanded": missing_expanded[:20],
            },
        )
    return 0 if not missing_expanded else 0


def cmd_ingest(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    out_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else target / "chains" / "anomalies"
    )

    if args.response_file == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.response_file).read_text()
    response = _coerce_json_payload(raw)
    if response is None:
        print("error: response is not valid JSON (no JSON object detected)", file=sys.stderr)
        return 2

    if not isinstance(response, dict):
        print("error: response must be a JSON object", file=sys.stderr)
        return 2

    cleaned = _strip_verdicts(response, bucket=args.bucket or response.get("bucket") or "")
    slug = _slug(cleaned.get("bucket") or args.bucket or "bucket")
    out_path = out_dir / f"{slug}.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cleaned, indent=2))
    print(str(out_path))

    if not args.no_status:
        write_status_phase(
            target,
            "cc_taint_bucket_anomalies",
            {
                "status": "appending",
                "ts": utcnow(),
                "last_bucket": slug,
                "stripped_keys": cleaned.get("_stripped_keys") or [],
            },
        )
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Bucket chains by sink file and prep/ingest anomaly prompts.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--db", help="Per-target js_analyzer.db (default: per-target snapshot)")
    ap.add_argument("--chains-input")
    ap.add_argument("--output-dir")
    ap.add_argument("--prompt-template", help="Path to bucket_anomaly.md prompt template")
    ap.add_argument("--byte-budget", type=int, default=40000, help="Soft cap on per-bucket prompt payload size")
    ap.add_argument("--no-status", action="store_true")

    sub = ap.add_subparsers(dest="mode", required=False)

    prep = sub.add_parser("prepare", help="Build per-bucket prompts (default mode)")
    prep.add_argument("--dry-run", action="store_true")

    ing = sub.add_parser("ingest", help="Strip verdicts and persist a subagent response")
    ing.add_argument("--bucket", help="Bucket slug or sink file path")
    ing.add_argument("--response-file", required=True, help="Path to JSON file or '-' for stdin")

    # Backwards-compat alias for the verify gate.
    ap.add_argument("--dry-run", action="store_true", help="Equivalent to 'prepare --dry-run'")

    args = ap.parse_args(argv)
    if args.mode is None:
        args.mode = "prepare"
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if args.mode == "prepare":
            return cmd_prepare(args)
        if args.mode == "ingest":
            return cmd_ingest(args)
        print(f"error: unknown mode {args.mode}", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        target_arg = getattr(args, "target", None)
        if target_arg:
            try:
                append_status_error(resolve_target_dir(target_arg), "cc-taint-bucket", e)
            except Exception:
                pass
        return 2


if __name__ == "__main__":
    sys.exit(main())
