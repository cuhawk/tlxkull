#!/usr/bin/env python3
"""wiki-dream — offline-batch wiki curator (Anthropic "dreaming" pattern).

Per the CLAUDE.md API-key whitelist, this script does NOT call any LLM. It
prepares per-(target, bucket) prompt bodies for read-only Claude Code
subagents, ingests their JSON diff proposals, renders human-readable
patches into ``wiki-staging/<utc>/``, and (optionally, on user
initiation) promotes selected patches into the real wiki.

The skill body (``.claude/skills/wiki-dream/SKILL.md``) is what actually
dispatches the Agent tool. This script only handles file I/O + schema
validation + promote bookkeeping.

Commands:
* ``gather``  — Phase 1. Walk tail data, write per-bucket prompts.
* ``ingest``  — Phase 3. Validate one subagent JSON response, write patches.
* ``summary`` — Phase 4. Aggregate patch files into _summary.{md,json}.
* ``promote`` — Phase 5. Apply selected patches to wiki/ (human-initiated).

Outputs land under ``wiki-staging/<run>/`` where ``<run>`` is the UTC
timestamp produced by ``gather``. ``promote`` is the ONLY path that
mutates ``wiki/`` — and only when invoked manually by the user.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, utcnow  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGING_DIR = ROOT / "wiki-staging"
WIKI_DIR = ROOT / "wiki"
TARGETS_DIR = ROOT / "targets"
INBOX_DIR = ROOT / "inbox"
INGEST_LOG = WIKI_DIR / "_ingest_log.jsonl"

_PROMPT_TEMPLATE_REL = ".claude/skills/wiki-dream/prompts/distill.md"

# Maximum chars of evidence per prompt body — keep distill subagent prompts
# tractable. Most recent items kept on overflow.
PROMPT_EVIDENCE_CHAR_CAP = 6000

# Maximum hours allowed for a single gather pass. Beyond ~30 days the
# curation surface is too large.
MAX_HOURS_WINDOW = 720

# Buckets the gather phase produces. Order is priority order — when an item
# could fit multiple buckets, the first match wins.
BUCKETS = (
    "autoresearch",
    "findings_confirmed",
    "findings_failed",
    "opus",
    "verifier",
    "podcast",
    "inbox_stale",
)

# Keys the ingester strips automatically (verdict-laundering surface +
# deletion-shaped keys; wiki is append-only).
_FORBIDDEN_KEYS = frozenset({
    "tp", "fp", "tps", "fps",
    "true_positive", "false_positive",
    "verdict", "verdicts",
    "classification", "classifications",
    "severity",
    "removal_markdown", "removals", "to_remove", "delete",
})

_REQUIRED_RESPONSE_KEYS = {"bucket", "target", "proposed_patches", "confidence"}

_VALID_CONFIDENCE = {"high", "medium", "med", "low"}
_VALID_ACTION = {"append", "new"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slug(s: str) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "patch"
    if len(base) > 60:
        h = hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]
        base = base[:60] + "-" + h
    return base


def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def _within_window(p: Path, window_secs: float, now: float) -> bool:
    m = _mtime(p)
    return bool(m) and (now - m) <= window_secs


def _read_jsonl_tail(p: Path, n: int = 50) -> list[dict]:
    if not p.exists():
        return []
    try:
        lines = p.read_text(errors="replace").splitlines()
    except OSError:
        return []
    out: list[dict] = []
    for line in lines[-n:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _safe_relative(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _list_targets(only: str | None) -> list[Path]:
    if not TARGETS_DIR.exists():
        return []
    if only:
        cand = TARGETS_DIR / only
        return [cand] if cand.exists() and cand.is_dir() else []
    return sorted(p for p in TARGETS_DIR.iterdir() if p.is_dir())


def _ingested_sources() -> set[str]:
    """Return the set of source_path values already in wiki/_ingest_log.jsonl."""
    out: set[str] = set()
    if not INGEST_LOG.exists():
        return out
    for row in _read_jsonl_tail(INGEST_LOG, n=10_000):
        sp = row.get("source") or row.get("source_dream_patch") or row.get("source_path")
        if sp:
            out.add(str(sp))
        # promoted patch rows reference original target + wiki_page combo
        for key in ("wiki_page", "pages_touched", "pages_created"):
            v = row.get(key)
            if isinstance(v, list):
                out.update(str(x) for x in v)
    return out


# ---------------------------------------------------------------------------
# Phase 1: gather
# ---------------------------------------------------------------------------


def _gather_target_bucket(
    target: Path,
    bucket: str,
    window_secs: float,
    now: float,
    ingested: set[str],
) -> list[dict]:
    """Return a list of item dicts ``{source_path, mtime, excerpt, metadata}``."""
    items: list[dict] = []

    if bucket == "autoresearch":
        p = target / "autoresearch.jsonl"
        if not _within_window(p, window_secs, now):
            return []
        for rec in _read_jsonl_tail(p, n=100):
            if rec.get("judged") is False or rec.get("outcome") == "undetermined":
                # Skip mid-hypothesis chatter — the prompt also re-skips.
                continue
            items.append({
                "source_path": _safe_relative(p),
                "mtime": datetime.fromtimestamp(_mtime(p), tz=timezone.utc).isoformat(),
                "excerpt": json.dumps(rec)[:400],
                "metadata": {
                    "iter": rec.get("iter"),
                    "hypothesis": (rec.get("hypothesis") or "")[:200],
                    "outcome": rec.get("outcome"),
                    "chain_id": rec.get("chain_id"),
                },
            })

    elif bucket == "findings_confirmed":
        findings_dir = target / "findings"
        if not findings_dir.exists():
            return []
        for fid_dir in findings_dir.iterdir():
            if not fid_dir.is_dir():
                continue
            p = fid_dir / "confirmed.json"
            if not _within_window(p, window_secs, now):
                continue
            rel = _safe_relative(p)
            if rel in ingested:
                continue
            try:
                data = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            items.append({
                "source_path": rel,
                "mtime": datetime.fromtimestamp(_mtime(p), tz=timezone.utc).isoformat(),
                "excerpt": json.dumps(data)[:400],
                "metadata": {
                    "finding_id": fid_dir.name,
                    "chain_id": data.get("chain_id"),
                    "sink_kind": data.get("sink_kind"),
                },
            })

    elif bucket == "findings_failed":
        findings_dir = target / "findings"
        if not findings_dir.exists():
            return []
        for fid_dir in findings_dir.iterdir():
            if not fid_dir.is_dir():
                continue
            p = fid_dir / "failed.json"
            if not _within_window(p, window_secs, now):
                continue
            try:
                data = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            items.append({
                "source_path": _safe_relative(p),
                "mtime": datetime.fromtimestamp(_mtime(p), tz=timezone.utc).isoformat(),
                "excerpt": json.dumps(data)[:400],
                "metadata": {
                    "finding_id": fid_dir.name,
                    "reason": data.get("reason"),
                    "chain_id": data.get("chain_id"),
                },
            })

    elif bucket == "opus":
        opus_dir = target / "opus"
        if not opus_dir.exists():
            return []
        for p in opus_dir.glob("*.json"):
            if p.name.startswith("_") or not _within_window(p, window_secs, now):
                continue
            try:
                data = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            items.append({
                "source_path": _safe_relative(p),
                "mtime": datetime.fromtimestamp(_mtime(p), tz=timezone.utc).isoformat(),
                "excerpt": json.dumps({
                    "chain_id": data.get("chain_id"),
                    "triage": data.get("triage"),
                    "confidence": data.get("confidence"),
                    "exploit_argument": (data.get("exploit_argument") or "")[:200],
                })[:400],
                "metadata": {
                    "chain_id": data.get("chain_id"),
                    "triage": data.get("triage"),
                    "confidence": data.get("confidence"),
                    "has_verifier_history": bool(data.get("_verifier_history")),
                },
            })
        # Also surface opus markdown if present.
        for p in opus_dir.glob("*.md"):
            if not _within_window(p, window_secs, now):
                continue
            try:
                head = p.read_text()[:400]
            except OSError:
                continue
            items.append({
                "source_path": _safe_relative(p),
                "mtime": datetime.fromtimestamp(_mtime(p), tz=timezone.utc).isoformat(),
                "excerpt": head,
                "metadata": {"chain_id": p.stem},
            })

    elif bucket == "verifier":
        verifier_dir = target / "two_judge"
        if not verifier_dir.exists():
            return []
        for p in verifier_dir.glob("*.json"):
            if p.name.startswith("_") or not _within_window(p, window_secs, now):
                continue
            try:
                data = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            # Only interesting if the verifier downgraded or flagged flawed.
            if data.get("audit_quality") in ("agree", None):
                continue
            items.append({
                "source_path": _safe_relative(p),
                "mtime": datetime.fromtimestamp(_mtime(p), tz=timezone.utc).isoformat(),
                "excerpt": json.dumps({
                    "chain_id": data.get("chain_id"),
                    "audit_quality": data.get("audit_quality"),
                    "issues_found": data.get("issues_found"),
                })[:400],
                "metadata": {
                    "chain_id": data.get("chain_id"),
                    "audit_quality": data.get("audit_quality"),
                    "recommended_triage": data.get("recommended_triage"),
                },
            })

    return items


def _gather_global_podcast(window_secs: float, now: float) -> list[dict]:
    """Cross-target: podcasts distill logs with no_distill or needs_review tail."""
    items: list[dict] = []
    podcasts_root = WIKI_DIR / "sources" / "podcasts"
    if not podcasts_root.exists():
        return items
    for log in podcasts_root.glob("*/_distill_log.jsonl"):
        if not _within_window(log, window_secs, now):
            continue
        for rec in _read_jsonl_tail(log, n=50):
            if rec.get("no_distill") or rec.get("needs_review"):
                items.append({
                    "source_path": _safe_relative(log),
                    "mtime": rec.get("ts") or datetime.fromtimestamp(
                        _mtime(log), tz=timezone.utc
                    ).isoformat(),
                    "excerpt": json.dumps(rec)[:400],
                    "metadata": {
                        "vid": rec.get("vid"),
                        "base": rec.get("base"),
                        "no_distill": bool(rec.get("no_distill")),
                        "needs_review": bool(rec.get("needs_review")),
                    },
                })
    return items


def _gather_global_inbox_stale(window_secs: float, now: float) -> list[dict]:
    """READY markers older than the window (>24h on default settings)."""
    items: list[dict] = []
    if not INBOX_DIR.exists():
        return items
    for ready in INBOX_DIR.glob("*/*/READY"):
        m = _mtime(ready)
        if not m:
            continue
        # Stale = older than the window's far edge (so default --hours 24
        # surfaces READYs that have been pending > 24h).
        if (now - m) < window_secs:
            continue
        items.append({
            "source_path": _safe_relative(ready),
            "mtime": datetime.fromtimestamp(m, tz=timezone.utc).isoformat(),
            "excerpt": f"stale READY age={(now - m) / 3600:.1f}h",
            "metadata": {
                "source_dir": str(ready.parent.relative_to(ROOT)),
                "stale_hours": round((now - m) / 3600, 1),
            },
        })
    return items


def _grep_wiki_keywords(items: list[dict]) -> dict[str, list[str]]:
    """Cheap keyword extractor + wiki-side hit map.

    Pulls 1-2 word tokens from item excerpts and greps wiki/ for them.
    Returns {keyword: [wiki paths]} truncated to ~10 keywords / 5 hits each.
    """
    text = "\n".join(i.get("excerpt", "") for i in items)
    # Take alphabetic tokens >= 4 chars; dedupe; cap at 10.
    seen: list[str] = []
    for tok in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text):
        low = tok.lower()
        if low in {"true", "false", "null", "from", "this", "with",
                   "json", "text", "data", "item", "name", "path",
                   "chain", "found", "could", "would", "should",
                   "test", "case"}:
            continue
        if low not in [s.lower() for s in seen]:
            seen.append(tok)
        if len(seen) >= 10:
            break

    hits: dict[str, list[str]] = {}
    for kw in seen:
        kw_hits: list[str] = []
        # Lightweight scan — only check techniques/, tools/, targets/, payloads/.
        for sub in ("techniques", "tools", "targets", "payloads", "people"):
            base = WIKI_DIR / sub
            if not base.exists():
                continue
            for p in base.rglob("*.md"):
                if len(kw_hits) >= 5:
                    break
                try:
                    body = p.read_text(errors="replace")
                except OSError:
                    continue
                if kw.lower() in body.lower():
                    kw_hits.append(_safe_relative(p))
            if len(kw_hits) >= 5:
                break
        if kw_hits:
            hits[kw] = kw_hits
    return hits


def _truncate_items(items: list[dict], cap: int) -> list[dict]:
    """Drop oldest items until JSON serialisation fits under ``cap`` chars."""
    items = sorted(items, key=lambda i: i.get("mtime") or "", reverse=True)
    while items and len(json.dumps(items)) > cap:
        items.pop()  # drop the oldest tail
    return items


def _render_prompt_body(
    template: str,
    *,
    target_name: str,
    bucket: str,
    items: list[dict],
    wiki_hits: dict[str, list[str]],
) -> str:
    return (
        template
        .replace("{{TARGET_NAME}}", target_name)
        .replace("{{BUCKET}}", bucket)
        .replace("{{ITEMS}}", json.dumps(items, indent=2))
        .replace("{{EXISTING_WIKI_HITS}}", json.dumps(wiki_hits, indent=2))
    )


def _check_backlog(force: bool) -> tuple[bool, str | None]:
    """Return (ok, message). False if a prior unread summary blocks new run."""
    if force or not STAGING_DIR.exists():
        return True, None
    runs = sorted(
        (p for p in STAGING_DIR.iterdir() if p.is_dir() and (p / "_summary.md").exists()),
        key=lambda p: p.name,
        reverse=True,
    )
    if not runs:
        return True, None
    latest = runs[0]
    summary = latest / "_summary.md"
    summary_mtime = _mtime(summary)

    # Find the most recent promote entry referencing this run id.
    last_promote = 0.0
    if INGEST_LOG.exists():
        for rec in _read_jsonl_tail(INGEST_LOG, n=2000):
            if rec.get("run_id") == latest.name:
                ts = rec.get("ts")
                if ts:
                    try:
                        last_promote = max(
                            last_promote,
                            datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp(),
                        )
                    except ValueError:
                        pass

    if summary_mtime > last_promote:
        return False, (
            f"backlog gate: wiki-staging/{latest.name}/_summary.md is unread "
            f"(no promote entries for this run in wiki/_ingest_log.jsonl). "
            f"Drain first, or re-run with --force."
        )
    return True, None


def cmd_gather(args: argparse.Namespace) -> int:
    hours = float(args.hours)
    if hours <= 0:
        print("error: --hours must be positive", file=sys.stderr)
        return 2
    if hours > MAX_HOURS_WINDOW:
        print(
            f"error: --hours {hours} exceeds {MAX_HOURS_WINDOW}; refusing to curate that much tail",
            file=sys.stderr,
        )
        return 2

    ok, msg = _check_backlog(args.force)
    if not ok:
        print(f"error: {msg}", file=sys.stderr)
        return 2

    window_secs = hours * 3600.0
    now = time.time()

    template_path = ROOT / _PROMPT_TEMPLATE_REL
    if not template_path.exists():
        print(f"error: prompt template missing: {template_path}", file=sys.stderr)
        return 2
    template = template_path.read_text()

    ingested = _ingested_sources()

    # Collect items per (target, bucket) pair.
    bucket_items: dict[tuple[str, str], list[dict]] = {}

    targets = _list_targets(args.target)
    for target in targets:
        for bucket in BUCKETS:
            if bucket in ("podcast", "inbox_stale"):
                continue  # global, handled below
            items = _gather_target_bucket(target, bucket, window_secs, now, ingested)
            if items:
                bucket_items[(target.name, bucket)] = items

    # Global buckets (no per-target attribution).
    if not args.target:
        pod = _gather_global_podcast(window_secs, now)
        if pod:
            bucket_items[("_global", "podcast")] = pod
        stale = _gather_global_inbox_stale(window_secs, now)
        if stale:
            bucket_items[("_global", "inbox_stale")] = stale

    if not bucket_items:
        print(json.dumps({"status": "no items in window", "hours": hours}, indent=2))
        return 0

    run_id = utcnow().replace(":", "").replace("-", "")
    run_dir = STAGING_DIR / run_id
    prompts_dir = run_dir / "_prompts"
    responses_dir = run_dir / "_responses"

    if not args.dry_run:
        prompts_dir.mkdir(parents=True, exist_ok=True)
        responses_dir.mkdir(parents=True, exist_ok=True)

    manifest_prompts: list[dict] = []
    total_items = 0
    for (target_name, bucket), items in sorted(bucket_items.items()):
        items = _truncate_items(items, PROMPT_EVIDENCE_CHAR_CAP)
        if not items:
            continue
        wiki_hits = _grep_wiki_keywords(items)
        bucket_id = f"{target_name}__{bucket}"
        body = _render_prompt_body(
            template,
            target_name=target_name,
            bucket=bucket,
            items=items,
            wiki_hits=wiki_hits,
        )
        prompt_path = prompts_dir / f"{bucket_id}.md"
        response_path = responses_dir / f"{bucket_id}.json"
        if not args.dry_run:
            prompt_path.write_text(body)
        manifest_prompts.append({
            "bucket": bucket_id,
            "target": target_name,
            "source_bucket": bucket,
            "prompt_path": _safe_relative(prompt_path),
            "response_path": _safe_relative(response_path),
            "item_count": len(items),
        })
        total_items += len(items)

    manifest = {
        "run_id": run_id,
        "ts": utcnow(),
        "hours_window": hours,
        "target_filter": args.target,
        "buckets_prepared": len(manifest_prompts),
        "total_items": total_items,
        "prompts": manifest_prompts,
    }

    if not args.dry_run:
        (run_dir / "_manifest.json").write_text(json.dumps(manifest, indent=2))

    summary = {
        "status": "prepared" if not args.dry_run else "dry_run",
        "run_id": run_id,
        "run_dir": _safe_relative(run_dir),
        "buckets_prepared": len(manifest_prompts),
        "total_items": total_items,
        "dry_run": bool(args.dry_run),
    }
    print(json.dumps(summary, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Phase 3: ingest
# ---------------------------------------------------------------------------


def _coerce_json_payload(raw: str) -> dict | None:
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


def _resolve_run_dir(run_id: str | None) -> Path | None:
    if run_id:
        p = STAGING_DIR / run_id
        return p if p.exists() else None
    if not STAGING_DIR.exists():
        return None
    runs = sorted(
        (p for p in STAGING_DIR.iterdir() if p.is_dir()),
        key=lambda p: p.name,
        reverse=True,
    )
    return runs[0] if runs else None


def _strip_forbidden(d: dict) -> tuple[dict, list[str]]:
    dropped = sorted(k for k in d if k.lower() in _FORBIDDEN_KEYS)
    cleaned = {k: v for k, v in d.items() if k.lower() not in _FORBIDDEN_KEYS}
    return cleaned, dropped


def _validate_response(raw: dict, expected_bucket: str) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("response must be a JSON object")

    response, dropped_top = _strip_forbidden(raw)

    missing = _REQUIRED_RESPONSE_KEYS - set(response.keys())
    if missing:
        raise ValueError(f"missing required keys: {sorted(missing)}")

    conf = str(response.get("confidence", "")).lower()
    if conf == "med":
        conf = "medium"
    if conf not in _VALID_CONFIDENCE:
        raise ValueError(f"confidence must be high/medium/low, got: {conf!r}")
    response["confidence"] = conf

    patches = response.get("proposed_patches") or []
    if not isinstance(patches, list):
        raise ValueError("proposed_patches must be a list")

    cleaned_patches: list[dict] = []
    patch_strip_log: list[list[str]] = []
    for idx, patch in enumerate(patches):
        if not isinstance(patch, dict):
            raise ValueError(f"proposed_patches[{idx}] must be an object")
        clean, dropped = _strip_forbidden(patch)
        patch_strip_log.append(dropped)

        wiki_page = str(clean.get("wiki_page", "")).strip()
        if not wiki_page:
            raise ValueError(f"proposed_patches[{idx}].wiki_page required")
        if not wiki_page.endswith(".md"):
            raise ValueError(
                f"proposed_patches[{idx}].wiki_page must end in .md: {wiki_page!r}"
            )
        # Normalise relative paths.
        if not wiki_page.startswith("wiki/"):
            wiki_page = "wiki/" + wiki_page.lstrip("/")
        clean["wiki_page"] = wiki_page

        action = str(clean.get("action", "")).lower()
        if action not in _VALID_ACTION:
            raise ValueError(
                f"proposed_patches[{idx}].action must be append|new, got: {action!r}"
            )
        clean["action"] = action

        addition = str(clean.get("addition_markdown", "")).strip()
        if not addition:
            raise ValueError(
                f"proposed_patches[{idx}].addition_markdown required and non-empty"
            )
        clean["addition_markdown"] = addition

        abs_wiki = ROOT / wiki_page
        page_exists = abs_wiki.exists()
        clean["exists"] = page_exists
        if action == "new" and page_exists:
            raise ValueError(
                f"proposed_patches[{idx}] action=new but page already exists: {wiki_page}"
            )
        if action == "new" and not clean.get("title_if_new"):
            # Synthesize from the slug if missing.
            clean["title_if_new"] = abs_wiki.stem.replace("-", " ").title()

        # Flag cross-refs pointing to non-existent from_page.
        crefs = clean.get("cross_refs_to_add") or []
        if not isinstance(crefs, list):
            crefs = []
        normalised_crefs: list[dict] = []
        for cref in crefs:
            if not isinstance(cref, dict):
                continue
            from_page = str(cref.get("from_page", "")).strip()
            link_text = str(cref.get("link_text", "")).strip()
            link_target = str(cref.get("link_target", "")).strip()
            if not (from_page and link_target):
                continue
            if not from_page.startswith("wiki/"):
                from_page = "wiki/" + from_page.lstrip("/")
            if not link_target.startswith("wiki/"):
                link_target = "wiki/" + link_target.lstrip("/")
            cref_out = {
                "from_page": from_page,
                "link_text": link_text or from_page,
                "link_target": link_target,
                "cross_ref_pending": not (ROOT / from_page).exists(),
            }
            normalised_crefs.append(cref_out)
        clean["cross_refs_to_add"] = normalised_crefs

        cleaned_patches.append(clean)

    response["proposed_patches"] = cleaned_patches
    response["_stripped_top_keys"] = dropped_top
    response["_stripped_patch_keys"] = patch_strip_log
    response["_ts"] = utcnow()
    return response


def _write_patch_file(run_dir: Path, bucket_id: str, patch: dict, idx: int) -> Path:
    wiki_page = patch["wiki_page"]
    action = patch["action"]
    abs_wiki = ROOT / wiki_page

    if patch.get("exists"):
        try:
            current_lines = abs_wiki.read_text(errors="replace").splitlines()[:40]
            current_excerpt = "\n".join(current_lines)
        except OSError:
            current_excerpt = "(failed to read current content)"
    else:
        current_excerpt = "page does not exist"

    cref_lines = []
    for i, cref in enumerate(patch.get("cross_refs_to_add") or [], 1):
        pending = " [cross_ref_pending]" if cref.get("cross_ref_pending") else ""
        cref_lines.append(
            f"{i}. From `{cref['from_page']}`{pending} -> "
            f"`{cref['link_target']}` ({cref['link_text']})"
        )
    if not cref_lines:
        cref_lines.append("(none)")

    ev_lines = []
    for i, ev in enumerate(patch.get("evidence") or [], 1):
        ev_lines.append(
            f"{i}. ({ev.get('source_kind','?')}) `{ev.get('source_path','?')}` "
            f"-- {ev.get('excerpt','')[:200]}"
        )
    if not ev_lines:
        ev_lines.append("(no evidence cited)")

    body = f"""# wiki-dream patch -- {bucket_id} #{idx}

- target wiki page: `{wiki_page}`
- action: **{action}**
- run_id: `{run_dir.name}`
- bucket: `{bucket_id}`
{f"- title_if_new: {patch.get('title_if_new', '')}" if action == "new" else ""}

## Current content excerpt

```markdown
{current_excerpt}
```

## Proposed addition

```markdown
{patch['addition_markdown']}
```

## Cross-refs to add

{chr(10).join(cref_lines)}

## Evidence

{chr(10).join(ev_lines)}

## Rationale

{patch.get('rationale', '(none provided)')}
"""
    slug = _slug(Path(wiki_page).stem)
    out_path = run_dir / f"{bucket_id}__{slug}__{idx:02d}.patch.md"
    out_path.write_text(body)
    return out_path


def cmd_ingest(args: argparse.Namespace) -> int:
    bucket_id = args.bucket
    run_dir = _resolve_run_dir(args.run)
    if run_dir is None:
        print("error: no wiki-staging run found", file=sys.stderr)
        return 2

    if args.response_file == "-":
        raw_text = sys.stdin.read()
    else:
        raw_text = Path(args.response_file).read_text()

    response = _coerce_json_payload(raw_text)
    if response is None:
        print("error: response is not valid JSON", file=sys.stderr)
        return 2

    try:
        validated = _validate_response(response, expected_bucket=bucket_id)
    except ValueError as e:
        err_path = run_dir / "_errors.jsonl"
        err_row = {"ts": utcnow(), "bucket": bucket_id, "error": str(e)}
        with err_path.open("a") as f:
            f.write(json.dumps(err_row) + "\n")
        print(f"error: {e}", file=sys.stderr)
        return 2

    # Persist the cleaned response.
    cleaned_path = run_dir / "_responses" / f"{bucket_id}.cleaned.json"
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_path.write_text(json.dumps(validated, indent=2))

    # Render one patch file per proposed_patch.
    written: list[str] = []
    for idx, patch in enumerate(validated.get("proposed_patches") or [], 1):
        out = _write_patch_file(run_dir, bucket_id, patch, idx)
        written.append(_safe_relative(out))

    print(json.dumps({
        "status": "ingested",
        "bucket": bucket_id,
        "patches_written": len(written),
        "patch_paths": written,
        "stripped_top_keys": validated.get("_stripped_top_keys") or [],
    }, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Phase 4: summary
# ---------------------------------------------------------------------------


def _load_patch_meta(patch_path: Path) -> dict:
    """Parse a patch.md back into bucket / wiki_page / action / rationale.

    This is intentionally line-oriented so the format stays
    human-friendly while remaining machine-readable.
    """
    out = {
        "patch_path": str(patch_path),
        "bucket": "",
        "wiki_page": "",
        "action": "",
        "rationale": "",
    }
    try:
        body = patch_path.read_text()
    except OSError:
        return out
    for line in body.splitlines():
        m = re.match(r"^- target wiki page: `([^`]+)`", line)
        if m:
            out["wiki_page"] = m.group(1)
        m = re.match(r"^- action: \*\*([^*]+)\*\*", line)
        if m:
            out["action"] = m.group(1).strip()
        m = re.match(r"^- bucket: `([^`]+)`", line)
        if m:
            out["bucket"] = m.group(1)
    # Rationale is the last section ("## Rationale\n\n<text>").
    if "## Rationale" in body:
        out["rationale"] = body.split("## Rationale", 1)[1].strip()
    return out


def cmd_summary(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run)
    if run_dir is None:
        print("error: no wiki-staging run found", file=sys.stderr)
        return 2

    patches = sorted(p for p in run_dir.glob("*.patch.md"))
    if not patches:
        print("warn: no patch files in run", file=sys.stderr)

    meta = [_load_patch_meta(p) for p in patches]

    by_bucket: dict[str, int] = {}
    by_target: dict[str, int] = {}
    by_action: dict[str, int] = {}
    for m in meta:
        by_bucket[m["bucket"]] = by_bucket.get(m["bucket"], 0) + 1
        target = m["bucket"].split("__", 1)[0] if "__" in m["bucket"] else "?"
        by_target[target] = by_target.get(target, 0) + 1
        by_action[m["action"]] = by_action.get(m["action"], 0) + 1

    manifest = {}
    mf = run_dir / "_manifest.json"
    if mf.exists():
        try:
            manifest = json.loads(mf.read_text())
        except json.JSONDecodeError:
            pass

    overview = (
        f"wiki-dream run `{run_dir.name}` produced **{len(meta)} candidate patches** "
        f"from {manifest.get('total_items', '?')} tail items across "
        f"{len(by_target)} target(s) and {len(by_bucket)} bucket(s). "
        f"Append vs new: {by_action.get('append', 0)} / {by_action.get('new', 0)}."
    )

    lines = [f"# wiki-dream run {run_dir.name}", "", overview, "", "## Proposed patches", ""]
    for i, m in enumerate(meta, 1):
        rationale = (m.get("rationale") or "").splitlines()[0][:80]
        lines.append(
            f"{i}. `{m['bucket']}` -> `{m['wiki_page']}` ({m['action']}) -- {rationale}"
        )
    lines += [
        "",
        "## Promote with",
        "",
        "```bash",
        f"python3 bin/wiki_dream.py promote --run {run_dir.name} --patches <comma-ids>",
        f"python3 bin/wiki_dream.py promote --run {run_dir.name} --all",
        "```",
        "",
    ]
    (run_dir / "_summary.md").write_text("\n".join(lines))

    summary_json = {
        "run_id": run_dir.name,
        "hours_window": manifest.get("hours_window"),
        "buckets_prepared": manifest.get("buckets_prepared"),
        "patches_generated": len(meta),
        "by_action": by_action,
        "by_bucket": by_bucket,
        "by_target": by_target,
        "errors": (run_dir / "_errors.jsonl").exists() and (run_dir / "_errors.jsonl").stat().st_size or 0,
    }
    (run_dir / "_summary.json").write_text(json.dumps(summary_json, indent=2))

    print(json.dumps(summary_json, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Phase 5: promote (manual)
# ---------------------------------------------------------------------------


def _append_to_wiki_page(page: Path, addition_markdown: str) -> None:
    page.parent.mkdir(parents=True, exist_ok=True)
    sep = "\n\n" if page.exists() and page.read_text().strip() else ""
    with page.open("a") as f:
        f.write(f"{sep}{addition_markdown.rstrip()}\n")


def _create_wiki_page(page: Path, title: str, addition_markdown: str) -> None:
    page.parent.mkdir(parents=True, exist_ok=True)
    body = f"# {title}\n\n{addition_markdown.rstrip()}\n"
    page.write_text(body)


def _append_cross_ref(from_page: Path, link_text: str, link_target: str) -> bool:
    """Append a link line to ``from_page``'s ``## Related`` section.

    Returns True if the link was added, False if the from_page doesn't
    exist (cross_ref_pending).
    """
    if not from_page.exists():
        return False
    body = from_page.read_text()
    link_line = f"- [{link_text}]({link_target})"
    if link_line in body:
        return True  # already present, no-op
    if "## Related" in body:
        # Insert after the heading.
        parts = body.split("## Related", 1)
        head, tail = parts[0], parts[1]
        # Find the first blank line after the heading; insert before it
        # (or at the very end of the section).
        tail_lines = tail.splitlines(keepends=True)
        insert_idx = len(tail_lines)
        for i, line in enumerate(tail_lines[1:], 1):
            if line.startswith("## "):
                insert_idx = i
                break
        new_tail = "".join(tail_lines[:insert_idx]) + link_line + "\n" + "".join(tail_lines[insert_idx:])
        from_page.write_text(head + "## Related" + new_tail)
    else:
        sep = "" if body.endswith("\n") else "\n"
        from_page.write_text(body + sep + "\n## Related\n\n" + link_line + "\n")
    return True


def _parse_patch_file(patch_path: Path) -> dict | None:
    """Reconstruct a patch dict from the rendered .patch.md.

    The cleaned JSON for the bucket lives alongside the patches under
    `_responses/<bucket>.cleaned.json`; we prefer reading from there so
    the full structured data is preserved.
    """
    meta = _load_patch_meta(patch_path)
    bucket = meta["bucket"]
    wiki_page = meta["wiki_page"]
    action = meta["action"]
    cleaned = patch_path.parent / "_responses" / f"{bucket}.cleaned.json"
    if not cleaned.exists():
        return None
    try:
        data = json.loads(cleaned.read_text())
    except json.JSONDecodeError:
        return None
    for patch in data.get("proposed_patches") or []:
        if patch.get("wiki_page") == wiki_page and patch.get("action") == action:
            return {
                "bucket": bucket,
                "target": data.get("target"),
                "patch": patch,
                "patch_path": str(patch_path),
            }
    return None


def cmd_promote(args: argparse.Namespace) -> int:
    run_dir = _resolve_run_dir(args.run)
    if run_dir is None:
        print("error: no wiki-staging run found", file=sys.stderr)
        return 2

    summary_path = run_dir / "_summary.md"
    if not summary_path.exists():
        print("error: _summary.md missing; run `summary` first", file=sys.stderr)
        return 2

    patches = sorted(p for p in run_dir.glob("*.patch.md"))
    if not patches:
        print("warn: no patches to promote", file=sys.stderr)
        return 0

    # Resolve selection.
    if args.all:
        selected_idxs = list(range(1, len(patches) + 1))
    elif args.patches:
        try:
            selected_idxs = [int(x.strip()) for x in args.patches.split(",") if x.strip()]
        except ValueError:
            print("error: --patches must be a comma-separated list of integers", file=sys.stderr)
            return 2
    else:
        print("error: pass --patches <ids> or --all", file=sys.stderr)
        return 2

    promoted: list[dict] = []
    skipped: list[dict] = []

    for idx in selected_idxs:
        if idx < 1 or idx > len(patches):
            skipped.append({"idx": idx, "reason": "out_of_range"})
            continue
        patch_path = patches[idx - 1]
        parsed = _parse_patch_file(patch_path)
        if parsed is None:
            skipped.append({"idx": idx, "reason": "patch_metadata_unresolved"})
            continue
        patch = parsed["patch"]
        wiki_page = patch["wiki_page"]
        action = patch["action"]
        abs_wiki = ROOT / wiki_page

        if action == "append":
            _append_to_wiki_page(abs_wiki, patch["addition_markdown"])
        elif action == "new":
            if abs_wiki.exists():
                skipped.append({"idx": idx, "reason": "new_but_exists"})
                continue
            _create_wiki_page(abs_wiki, patch.get("title_if_new") or abs_wiki.stem, patch["addition_markdown"])
        else:
            skipped.append({"idx": idx, "reason": f"bad_action_{action}"})
            continue

        # Cross-refs.
        cref_results = []
        for cref in patch.get("cross_refs_to_add") or []:
            from_page = ROOT / cref["from_page"]
            ok = _append_cross_ref(from_page, cref.get("link_text") or wiki_page, cref["link_target"])
            cref_results.append({
                "from_page": cref["from_page"],
                "link_target": cref["link_target"],
                "applied": ok,
                "cross_ref_pending": not ok,
            })

        log_row = {
            "ts": utcnow(),
            "run_id": run_dir.name,
            "bucket": parsed["bucket"],
            "target": parsed.get("target"),
            "wiki_page": wiki_page,
            "action": action,
            "source_dream_patch": _safe_relative(patch_path),
            "cross_refs": cref_results,
        }
        INGEST_LOG.parent.mkdir(parents=True, exist_ok=True)
        with INGEST_LOG.open("a") as f:
            f.write(json.dumps(log_row) + "\n")
        promoted.append({"idx": idx, "wiki_page": wiki_page, "action": action})

    print(json.dumps({
        "status": "promoted",
        "run_id": run_dir.name,
        "promoted_count": len(promoted),
        "skipped_count": len(skipped),
        "promoted": promoted,
        "skipped": skipped,
    }, indent=2))
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="wiki-dream — offline-batch wiki curator")
    sub = ap.add_subparsers(dest="mode", required=True)

    g = sub.add_parser("gather", help="Phase 1: walk tail data, write per-bucket prompts")
    g.add_argument("--hours", default="24", help="Window in hours (default 24, max 720)")
    g.add_argument("--target", help="Scope to a single target name (default: all)")
    g.add_argument("--force", action="store_true",
                   help="Override backlog gate (prior unread summary)")
    g.add_argument("--dry-run", action="store_true",
                   help="Print plan without writing prompts or manifest")

    i = sub.add_parser("ingest", help="Phase 3: validate one subagent JSON response")
    i.add_argument("--bucket", required=True, help="Bucket id, e.g. <target>__<bucket>")
    i.add_argument("--response-file", required=True, help="Path to JSON file or '-' for stdin")
    i.add_argument("--run", help="Run id (default: latest)")

    s = sub.add_parser("summary", help="Phase 4: aggregate patches into _summary.md")
    s.add_argument("--run", help="Run id (default: latest)")

    p = sub.add_parser("promote", help="Phase 5: apply selected patches to wiki/")
    p.add_argument("--run", help="Run id (default: latest)")
    p.add_argument("--patches", help="Comma-separated patch ordinals from _summary.md")
    p.add_argument("--all", action="store_true", help="Promote every patch in the run")

    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.mode == "gather":
        return cmd_gather(args)
    if args.mode == "ingest":
        return cmd_ingest(args)
    if args.mode == "summary":
        return cmd_summary(args)
    if args.mode == "promote":
        return cmd_promote(args)
    print(f"error: unknown mode {args.mode}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
