#!/usr/bin/env python3
"""mythos-read helper — full-source-tree audit pipeline (no LLM SDK).

Per CLAUDE.md Rule 7 this script does NOT call any LLM. It only:

1. Sizes the per-target `sources/` tree (size sub-command).
2. Bundles eligible source files into a single Claude-Code prompt body
   that the skill dispatches as ONE big read-only subagent (prepare).
3. Validates + ingests the subagent's JSON response, writes the
   timestamped record, and emits novel-hypothesis rows to
   `chains/_mythos_synthetic.jsonl` for downstream curation (ingest).
4. Aggregates all ingested records into a status.json digest (summary).

Companion artifacts:
* `targets/<name>/mythos/_prompt.md`              — bundled prompt body
* `targets/<name>/mythos/_size.json`              — last size-check
* `targets/<name>/mythos/<utc>.json`              — ingested records
* `targets/<name>/chains/_mythos_synthetic.jsonl` — synthetic chain feed
* `targets/<name>/status.json.phases.mythos`      — running counters

Prior art deliberately complemented (not duplicated):
* `bin/source_token_count.py` — long-context T1.3 probe; sizes the tree
  and emits a thin `opus/whole_tree_prompt.md`. mythos-read is the full
  pipeline that dispatches the audit and ingests structured output.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    ROOT,
    append_status_error,
    resolve_target_dir,
    status_lock,
    utcnow,
)

_PROMPT_TEMPLATE_REL = ".claude/skills/mythos-read/prompts/full_tree.md"

# Defaults
_DEFAULT_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_DEFAULT_INCLUDE_EXT = (
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".html", ".htm", ".svelte", ".vue",
)
_DEFAULT_EXCLUDE_GLOBS = (
    "*.min.js", "*.map", "*.json",
    "*.test.*", "*.spec.*",
)
_EXCLUDE_DIR_NAMES = {"node_modules", "vendor", "dist", "build"}

# Schema
_VALID_CONFIDENCE = {"high", "medium", "med", "low"}
_VALID_CLASS = {
    "auth_state_confusion",
    "prototype_pollution_gadget",
    "crypto_misuse",
    "cross_file_invariant",
    "dead_code_reactivation",
    "race_condition",
    "path_traversal",
    "ssrf",
    "sqli",
    "xss_no_flow",
    "other",
}
_FORBIDDEN_KEYS = {
    "verdict", "tp", "fp", "true_positive", "false_positive", "severity",
}
_REQUIRED_TOP = {"target", "audited_at", "hypotheses"}
_REQUIRED_HYP = {
    "id", "title", "class", "root_cause_files", "reasoning",
    "confidence",
}

_SLUG_RE = re.compile(r"[^a-z0-9-]+")


# ---------------------------------------------------------------------------
# File-tree walking
# ---------------------------------------------------------------------------

def _is_excluded_path(rel: Path, exclude_globs: list[str]) -> tuple[bool, str]:
    parts = rel.parts
    if any(p in _EXCLUDE_DIR_NAMES for p in parts):
        for p in parts:
            if p in _EXCLUDE_DIR_NAMES:
                return True, f"dir_{p}"
    if parts and parts[-1].startswith("_"):
        return True, "leading_underscore"
    name = rel.name
    for pat in exclude_globs:
        if fnmatch.fnmatch(name, pat):
            return True, f"glob_{pat}"
    return False, ""


def _walk_eligible(
    sources_root: Path,
    include_ext: tuple[str, ...],
    exclude_globs: list[str],
) -> tuple[list[Path], dict, dict]:
    """Return (eligible_files, totals, skip_reasons)."""
    eligible: list[Path] = []
    totals = {
        "total_bytes": 0,
        "eligible_bytes": 0,
        "total_files": 0,
        "eligible_files": 0,
        "by_ext": {},
    }
    skip: dict[str, int] = {}
    for p in sources_root.rglob("*"):
        if not p.is_file():
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        totals["total_files"] += 1
        totals["total_bytes"] += size
        rel = p.relative_to(sources_root)
        ext = p.suffix.lower()
        if ext not in include_ext:
            skip[f"ext_{ext or 'noext'}"] = skip.get(f"ext_{ext or 'noext'}", 0) + 1
            continue
        excluded, reason = _is_excluded_path(rel, exclude_globs)
        if excluded:
            skip[reason] = skip.get(reason, 0) + 1
            continue
        eligible.append(p)
        totals["eligible_files"] += 1
        totals["eligible_bytes"] += size
        totals["by_ext"][ext] = totals["by_ext"].get(ext, 0) + size
    eligible.sort()
    return eligible, totals, skip


def _verdict(totals: dict, max_bytes: int) -> str:
    if totals["eligible_files"] == 0:
        return "empty"
    if totals["eligible_bytes"] > max_bytes:
        return "over-budget"
    return "viable"


# ---------------------------------------------------------------------------
# size sub-command
# ---------------------------------------------------------------------------

def cmd_size(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    sources_root = target / "sources"
    if not sources_root.exists():
        result = {
            "status": "skipped",
            "ts": utcnow(),
            "reason": "sources/ missing — run sourcemap-explode first",
            "verdict": "empty",
            "target": target.name,
        }
        print(json.dumps(result, indent=2))
        return 0

    exclude_globs = _parse_exclude_globs(args.exclude_glob)
    include_ext = _parse_include_ext(args.include_ext)

    eligible, totals, skip = _walk_eligible(
        sources_root, include_ext, exclude_globs
    )
    max_bytes = args.max_bytes
    verdict = _verdict(totals, max_bytes)

    result = {
        "target": target.name,
        "ts": utcnow(),
        "verdict": verdict,
        "max_bytes": max_bytes,
        "include_ext": list(include_ext),
        "exclude_globs": exclude_globs,
        **totals,
        "skip_reasons": skip,
    }

    mythos_dir = target / "mythos"
    mythos_dir.mkdir(parents=True, exist_ok=True)
    (mythos_dir / "_size.json").write_text(json.dumps(result, indent=2))

    print(json.dumps(result, indent=2))

    if not args.no_status:
        with status_lock(target) as data:
            phase = data.setdefault("phases", {}).setdefault("mythos", {})
            phase.update({
                "status": "sized",
                "ts": result["ts"],
                "eligible_bytes": totals["eligible_bytes"],
                "files": totals["eligible_files"],
                "max_bytes": max_bytes,
                "verdict": verdict,
            })
    return 0


# ---------------------------------------------------------------------------
# prepare sub-command
# ---------------------------------------------------------------------------

def _resolve_template() -> Path:
    return ROOT / _PROMPT_TEMPLATE_REL


def _collect_known_chain_ids(target: Path) -> list:
    ids: set = set()
    for rel in ("chains/hot.jsonl", "chains/dom_reachable.jsonl"):
        p = target / rel
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = row.get("id") or row.get("chain_id")
            if cid is not None:
                ids.add(cid)
    opus_dir = target / "opus"
    if opus_dir.exists():
        for p in opus_dir.glob("*.json"):
            if p.name.startswith("_"):
                continue
            try:
                rec = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
            cid = rec.get("chain_id") or rec.get("id")
            if cid is not None:
                ids.add(cid)
    return sorted(ids, key=lambda v: (str(type(v).__name__), v))


def _build_file_tree(eligible: list[Path], sources_root: Path) -> str:
    lines = []
    for p in eligible:
        rel = p.relative_to(sources_root)
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        lines.append(f"- {rel} ({size}B)")
    return "\n".join(lines)


def _build_source_bundle(eligible: list[Path], sources_root: Path) -> str:
    parts: list[str] = []
    for p in eligible:
        rel = p.relative_to(sources_root)
        try:
            body = p.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            body = f"# unreadable: {e}\n"
        parts.append(f"### {rel}\n\n```\n{body}\n```\n")
    return "\n".join(parts)


def cmd_prepare(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    sources_root = target / "sources"
    if not sources_root.exists():
        print("error: sources/ missing — run sourcemap-explode first", file=sys.stderr)
        return 2

    exclude_globs = _parse_exclude_globs(args.exclude_glob)
    include_ext = _parse_include_ext(args.include_ext)

    eligible, totals, skip = _walk_eligible(
        sources_root, include_ext, exclude_globs
    )
    verdict = _verdict(totals, args.max_bytes)
    if verdict != "viable":
        print(
            json.dumps({
                "error": "refuse_to_prepare",
                "verdict": verdict,
                "eligible_bytes": totals["eligible_bytes"],
                "max_bytes": args.max_bytes,
                "recommendation": "use the chain pipeline (chain-triage → cc-taint-adversarial) instead",
            }, indent=2),
            file=sys.stderr,
        )
        return 2

    template_path = _resolve_template()
    if not template_path.exists():
        print(f"error: prompt template missing: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text()

    file_tree = _build_file_tree(eligible, sources_root)
    bundle = _build_source_bundle(eligible, sources_root)
    known_ids = _collect_known_chain_ids(target)

    body = (
        template
        .replace("{{TARGET_NAME}}", target.name)
        .replace("{{FILE_TREE}}", file_tree)
        .replace("{{SOURCE_BUNDLE}}", bundle)
        .replace("{{KNOWN_CHAIN_IDS}}", json.dumps(known_ids))
    )

    mythos_dir = target / "mythos"
    mythos_dir.mkdir(parents=True, exist_ok=True)
    out_path = mythos_dir / "_prompt.md"
    if not args.dry_run:
        out_path.write_text(body)

    summary = {
        "target": target.name,
        "ts": utcnow(),
        "prompt_path": str(out_path.relative_to(target)) if out_path.is_relative_to(target) else str(out_path),
        "eligible_files": totals["eligible_files"],
        "eligible_bytes": totals["eligible_bytes"],
        "max_bytes": args.max_bytes,
        "known_chain_ids": len(known_ids),
        "skip_reasons": skip,
        "dry_run": bool(args.dry_run),
    }
    print(json.dumps(summary, indent=2))

    if not args.no_status and not args.dry_run:
        with status_lock(target) as data:
            phase = data.setdefault("phases", {}).setdefault("mythos", {})
            phase.update({
                "status": "prepared",
                "ts": summary["ts"],
                "eligible_bytes": totals["eligible_bytes"],
                "files": totals["eligible_files"],
                "max_bytes": args.max_bytes,
                "prompt_path": summary["prompt_path"],
            })
    return 0


# ---------------------------------------------------------------------------
# ingest sub-command
# ---------------------------------------------------------------------------

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
            out = json.loads(text[start: end + 1])
            return out if isinstance(out, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _slugify(s: str, fallback: str) -> str:
    s = (s or "").strip().lower()
    s = _SLUG_RE.sub("-", s).strip("-")
    return s[:48] or fallback


def _coerce_hypothesis(h: dict, idx: int) -> tuple[dict, list[str]]:
    """Return (coerced_hyp, stripped_keys)."""
    if not isinstance(h, dict):
        raise ValueError(f"hypothesis #{idx} is not an object")
    stripped = sorted(k for k in h if k in _FORBIDDEN_KEYS)
    clean = {k: v for k, v in h.items() if k not in _FORBIDDEN_KEYS}

    missing = _REQUIRED_HYP - set(clean.keys())
    if missing:
        raise ValueError(f"hypothesis #{idx} missing required keys: {sorted(missing)}")

    cls = str(clean.get("class", "")).strip().lower()
    if cls not in _VALID_CLASS:
        clean.setdefault("_coerced", {})["class"] = cls or "<missing>"
        cls = "other"
    clean["class"] = cls

    conf = str(clean.get("confidence", "")).strip().lower()
    if conf == "med":
        conf = "medium"
    if conf not in _VALID_CONFIDENCE:
        raise ValueError(
            f"hypothesis #{idx} confidence must be high/medium/low, got: {conf!r}"
        )
    clean["confidence"] = conf

    rcf = clean.get("root_cause_files") or []
    if not isinstance(rcf, list):
        raise ValueError(f"hypothesis #{idx} root_cause_files must be a list")
    clean["root_cause_files"] = [str(x) for x in rcf if x]

    bu = clean.get("blocking_unknowns") or []
    if not isinstance(bu, list):
        raise ValueError(f"hypothesis #{idx} blocking_unknowns must be a list")
    clean["blocking_unknowns"] = [str(x) for x in bu if x]

    clean["title"] = str(clean.get("title", "")).strip()
    clean["reasoning"] = str(clean.get("reasoning", "")).strip()
    clean["exploit_sketch"] = str(clean.get("exploit_sketch", "")).strip()
    if not clean["reasoning"]:
        raise ValueError(f"hypothesis #{idx} reasoning must be non-empty")

    # id: keep if present, else derive from title
    hid = str(clean.get("id", "")).strip()
    if not hid.startswith("mythos-"):
        hid = "mythos-" + _slugify(clean["title"], fallback=f"hyp-{idx}")
    clean["id"] = hid

    overlap = clean.get("overlap_with_chain_id")
    if isinstance(overlap, str) and overlap.lower() in ("", "null", "none"):
        overlap = None
    clean["overlap_with_chain_id"] = overlap

    return clean, stripped


def _coerce_record(raw: dict, target_name: str) -> tuple[dict, list[str]]:
    if not isinstance(raw, dict):
        raise ValueError("response must be a JSON object")

    missing = _REQUIRED_TOP - set(raw.keys())
    if missing:
        raise ValueError(f"missing required top-level keys: {sorted(missing)}")

    stripped_top = sorted(k for k in raw if k in _FORBIDDEN_KEYS)
    record = {k: v for k, v in raw.items() if k not in _FORBIDDEN_KEYS}

    record["target"] = target_name  # force-overwrite
    record["audited_at"] = str(record.get("audited_at") or utcnow())

    hyps = record.get("hypotheses") or []
    if not isinstance(hyps, list):
        raise ValueError("hypotheses must be a list")

    coerced: list[dict] = []
    all_stripped: list[str] = list(stripped_top)
    for idx, h in enumerate(hyps):
        ch, st = _coerce_hypothesis(h, idx)
        coerced.append(ch)
        all_stripped.extend(st)
    record["hypotheses"] = coerced

    rc = record.get("review_coverage")
    if not isinstance(rc, dict):
        rc = {}
    record["review_coverage"] = rc

    record["_ts"] = utcnow()
    if all_stripped:
        record["_stripped_keys"] = sorted(set(all_stripped))

    return record, sorted(set(all_stripped))


def _emit_synthetic_chains(target: Path, record: dict) -> int:
    """Append novel medium+ hypotheses to chains/_mythos_synthetic.jsonl."""
    chains_dir = target / "chains"
    chains_dir.mkdir(parents=True, exist_ok=True)
    out = chains_dir / "_mythos_synthetic.jsonl"

    emitted = 0
    ts = utcnow()
    with out.open("a", encoding="utf-8") as f:
        for h in record["hypotheses"]:
            if h.get("overlap_with_chain_id") is not None:
                continue
            conf = h.get("confidence")
            if conf not in ("high", "medium"):
                continue
            row = {
                "id": h["id"],
                "source_kind": "mythos",
                "title": h.get("title", ""),
                "class": h.get("class", "other"),
                "files": h.get("root_cause_files", []),
                "exploit_sketch": h.get("exploit_sketch", ""),
                "confidence": conf,
                "queued_at": ts,
                "ready_for_audit": True,
            }
            f.write(json.dumps(row) + "\n")
            emitted += 1
    return emitted


def cmd_ingest(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)

    if args.response_file == "-":
        raw_text = sys.stdin.read()
    else:
        raw_text = Path(args.response_file).read_text()

    payload = _coerce_json_payload(raw_text)
    if payload is None:
        print("error: response is not valid JSON (no JSON object detected)", file=sys.stderr)
        return 2

    try:
        record, stripped = _coerce_record(payload, target.name)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        append_status_error(target, "mythos-read", e)
        return 2

    mythos_dir = target / "mythos"
    mythos_dir.mkdir(parents=True, exist_ok=True)
    ts_slug = utcnow().replace(":", "").replace("-", "")
    out_path = mythos_dir / f"{ts_slug}.json"
    if out_path.exists():
        # Extreme edge: same-second re-ingest. Bump.
        i = 1
        while (mythos_dir / f"{ts_slug}-{i}.json").exists():
            i += 1
        out_path = mythos_dir / f"{ts_slug}-{i}.json"
    out_path.write_text(json.dumps(record, indent=2))

    novel = sum(1 for h in record["hypotheses"] if h.get("overlap_with_chain_id") is None)
    overlap = len(record["hypotheses"]) - novel
    emitted = _emit_synthetic_chains(target, record)

    summary = {
        "record_path": str(out_path.relative_to(target)) if out_path.is_relative_to(target) else str(out_path),
        "total_hypotheses": len(record["hypotheses"]),
        "novel_count": novel,
        "overlap_count": overlap,
        "synthetic_rows_emitted": emitted,
        "stripped_keys": stripped,
    }
    print(json.dumps(summary, indent=2))

    if not args.no_status:
        with status_lock(target) as data:
            phase = data.setdefault("phases", {}).setdefault("mythos", {})
            counters = phase.setdefault("counters", {
                "ingested": 0,
                "by_class": {},
                "by_confidence": {},
                "novel_total": 0,
                "overlap_total": 0,
                "synthetic_emitted": 0,
            })
            counters["ingested"] = int(counters.get("ingested", 0)) + 1
            counters["novel_total"] = int(counters.get("novel_total", 0)) + novel
            counters["overlap_total"] = int(counters.get("overlap_total", 0)) + overlap
            counters["synthetic_emitted"] = int(counters.get("synthetic_emitted", 0)) + emitted
            by_cls = counters.setdefault("by_class", {})
            by_conf = counters.setdefault("by_confidence", {})
            for h in record["hypotheses"]:
                cls = h.get("class", "other")
                conf = h.get("confidence", "low")
                by_cls[cls] = int(by_cls.get(cls, 0)) + 1
                by_conf[conf] = int(by_conf.get(conf, 0)) + 1
            phase["ts"] = utcnow()
            phase["status"] = "ingesting"
            phase["last_run"] = record["audited_at"]
    return 0


# ---------------------------------------------------------------------------
# summary sub-command
# ---------------------------------------------------------------------------

def cmd_summary(args: argparse.Namespace) -> int:
    target = resolve_target_dir(args.target)
    mythos_dir = target / "mythos"
    if not mythos_dir.exists():
        print(json.dumps({"error": "no mythos/ dir", "target": target.name}, indent=2))
        return 0

    records: list[dict] = []
    for p in sorted(mythos_dir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        try:
            records.append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            continue

    total_hyps = 0
    by_class: dict[str, int] = {}
    by_confidence: dict[str, int] = {}
    novel = 0
    overlap = 0
    for r in records:
        for h in r.get("hypotheses", []) or []:
            total_hyps += 1
            by_class[h.get("class", "other")] = by_class.get(h.get("class", "other"), 0) + 1
            by_confidence[h.get("confidence", "low")] = by_confidence.get(h.get("confidence", "low"), 0) + 1
            if h.get("overlap_with_chain_id") is None:
                novel += 1
            else:
                overlap += 1

    summary = {
        "target": target.name,
        "runs": len(records),
        "total_hypotheses": total_hyps,
        "by_class": by_class,
        "by_confidence": by_confidence,
        "novel_count": novel,
        "overlap_count": overlap,
        "ts": utcnow(),
    }
    print(json.dumps(summary, indent=2))

    if not args.no_status:
        with status_lock(target) as data:
            phase = data.setdefault("phases", {}).setdefault("mythos", {})
            phase.update({
                "status": "done",
                "ts": summary["ts"],
                "final_summary": {
                    "total_hypotheses": total_hyps,
                    "by_class": by_class,
                    "by_confidence": by_confidence,
                    "novel_count": novel,
                    "overlap_count": overlap,
                    "runs": len(records),
                },
            })
    return 0


# ---------------------------------------------------------------------------
# arg parsing
# ---------------------------------------------------------------------------

def _parse_exclude_globs(arg: str | None) -> list[str]:
    if not arg:
        return list(_DEFAULT_EXCLUDE_GLOBS)
    return [g.strip() for g in arg.split(",") if g.strip()]


def _parse_include_ext(arg: str | None) -> tuple[str, ...]:
    if not arg:
        return _DEFAULT_INCLUDE_EXT
    items = []
    for tok in arg.split(","):
        tok = tok.strip().lower()
        if not tok:
            continue
        if not tok.startswith("."):
            tok = "." + tok
        items.append(tok)
    return tuple(items)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="mythos-read full-tree audit helper (prepare + ingest + summary).")
    ap.add_argument("mode", choices=("size", "prepare", "ingest", "summary"))
    ap.add_argument("--target", required=True)
    ap.add_argument("--no-status", action="store_true")

    ap.add_argument("--max-bytes", type=int, default=_DEFAULT_MAX_BYTES,
                    help="Eligibility cap (default 5MB)")
    ap.add_argument("--exclude-glob",
                    help="Comma-separated filename globs to exclude (overrides default).")
    ap.add_argument("--include-ext",
                    help="Comma-separated file extensions to include (overrides default).")

    ap.add_argument("--dry-run", action="store_true",
                    help="prepare: don't write _prompt.md")
    ap.add_argument("--response-file",
                    help="ingest: path to subagent JSON response file, or '-' for stdin")

    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.mode == "size":
        return cmd_size(args)
    if args.mode == "prepare":
        return cmd_prepare(args)
    if args.mode == "ingest":
        if not args.response_file:
            print("error: --response-file is required for ingest", file=sys.stderr)
            return 2
        return cmd_ingest(args)
    if args.mode == "summary":
        return cmd_summary(args)
    print(f"error: unknown mode {args.mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
