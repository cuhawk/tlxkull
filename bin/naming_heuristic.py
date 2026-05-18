#!/usr/bin/env python3
"""Phase 4: Function-name-based heuristic seeder for implicit sinks/sources.

When a function name contains a security-relevant verb pattern (e.g.
``renderHTML``, ``unsafeInject``, ``readQuery``), seed it as a derived
sink or source with low confidence (~0.3-0.4). This catches custom
wrappers that the regex taxonomy misses AND that implicit-closure
expansion can't reach (because the function doesn't call a known
primitive — it IS the primitive at the call-site level).

OFF BY DEFAULT. Heuristic naming is noisy; the user opts in per
engagement with ``--enable``. When enabled, confidence is intentionally
lower than implicit-closure (~0.49 at hop 2) so the chain-triage
scoring patch buries these in `all.jsonl` and they only rank into
`hot.jsonl` when no higher-confidence chain is available.

Output: appends rows to ``targets/<name>/tags_discovered.jsonl`` and
to the per-target ``node_tags`` table with ``source='implicit_naming'``.
Idempotent — re-running clears prior ``source='implicit_naming'`` rows
before inserting.

Per CLAUDE.md API-key whitelist: no LLM calls. Pure regex + DB I/O.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    per_target_db,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


# Heuristic rules. (pattern, kind, taxonomy_id, severity, confidence,
# matched_category). Patterns are anchored against the *bare* function
# name (last segment after ``.``), case-insensitive. Severity is what
# we'd assign if the function were a real sink/source; downstream
# scoring already multiplies by confidence so low-confidence sinks
# can't outrank direct ones.
@dataclass(frozen=True)
class _Rule:
    name: str
    pattern: re.Pattern
    kind: str             # 'sink' | 'source'
    taxonomy_id: str
    severity: str         # 'high' | 'medium' | 'low'
    confidence: float
    note: str


def _ci(p: str) -> re.Pattern:
    return re.compile(p, re.IGNORECASE)


_HEURISTIC_RULES: tuple[_Rule, ...] = (
    # SINK heuristics — fns whose name announces unsafe HTML/JS handling.
    _Rule(
        name="render_html",
        pattern=_ci(r"^(render|set|append|inject|write)(Raw)?(Html|HTML|Markup)$"),
        kind="sink", taxonomy_id="naming_render_html",
        severity="high", confidence=0.4,
        note="Function name implies raw HTML output (renderHTML, setHTML, etc.)",
    ),
    _Rule(
        name="unsafe_html",
        pattern=_ci(r"unsafe.*(html|markup|inject)|raw.*(html|markup)"),
        kind="sink", taxonomy_id="naming_unsafe_html",
        severity="high", confidence=0.35,
        note="Function name signals explicit unsafe-HTML handling",
    ),
    _Rule(
        name="dangerous_eval",
        pattern=_ci(r"^(run|exec|eval)(User|Raw|Dynamic|Custom)?(Code|Script|Expression)?$"),
        kind="sink", taxonomy_id="naming_dynamic_exec",
        severity="high", confidence=0.3,
        note="Function name implies dynamic code execution",
    ),
    _Rule(
        name="redirect_to",
        pattern=_ci(r"^(redirect|navigate|goTo|open)(To)?(Url|Page|External)?$"),
        kind="sink", taxonomy_id="naming_redirect",
        severity="medium", confidence=0.3,
        note="Function name implies URL navigation — open-redirect candidate",
    ),
    # SOURCE heuristics — fns whose name implies they return untrusted data.
    _Rule(
        name="read_query",
        pattern=_ci(r"^(get|read|parse|extract).*(Query|Param|Hash|Search|Url)Param?$"),
        kind="source", taxonomy_id="naming_url_input",
        severity="high", confidence=0.4,
        note="Function name implies returning URL-derived user input",
    ),
    _Rule(
        name="user_input",
        pattern=_ci(r"^(get|read).*(User|External|Raw|Untrusted)(Input|Data|Value)$"),
        kind="source", taxonomy_id="naming_user_input",
        severity="medium", confidence=0.35,
        note="Function name implies returning user / external input",
    ),
    _Rule(
        name="from_storage",
        pattern=_ci(r"^(read|load|get|restore).*(LocalStorage|SessionStorage|Cookie|Hash|Fragment)$"),
        kind="source", taxonomy_id="naming_storage_input",
        severity="medium", confidence=0.3,
        note="Function name implies reading from client storage / URL fragment",
    ),
    _Rule(
        name="from_message",
        pattern=_ci(r"^(handle|on|process).*(Message|PostMessage|Event)(Data)?$"),
        kind="source", taxonomy_id="naming_message_input",
        severity="medium", confidence=0.3,
        note="Function name implies handling cross-frame message data",
    ),
)


_BARE_NAME_RE = re.compile(r"[^.]+$")


def _bare_name(qname: str | None) -> str:
    if not qname:
        return ""
    last = qname.rsplit("::", 1)[-1]
    m = _BARE_NAME_RE.search(last)
    return m.group(0) if m else last


@dataclass
class HeuristicTag:
    node_id: int
    qname: str
    file: str
    line: int
    taxonomy_id: str
    kind: str
    severity: str
    source: str
    confidence: float
    rule_name: str
    note: str
    evidence: dict = field(default_factory=dict)


def _load_function_nodes(
    conn: sqlite3.Connection,
) -> list[tuple[int, str, str, int]]:
    return conn.execute(
        "SELECT id, qualified_name, file, start_line FROM nodes "
        "WHERE kind IN ('function','arrow','method')"
    ).fetchall()


def _existing_direct_keys(conn: sqlite3.Connection) -> set[tuple[int, str]]:
    return {
        (nid, tid)
        for nid, tid in conn.execute(
            "SELECT node_id, taxonomy_id FROM node_tags "
            "WHERE source NOT LIKE 'implicit_naming%'"
        )
    }


def discover(
    conn: sqlite3.Connection,
    *,
    enabled_rules: Iterable[str] | None = None,
    min_confidence: float = 0.0,
) -> list[HeuristicTag]:
    """Return heuristic tags. Pure — does not write to DB.

    ``enabled_rules`` defaults to ALL rules. Pass a subset to scope
    the run (e.g. ``["render_html", "unsafe_html"]`` for HTML-only).
    """
    enabled = (
        {r.name for r in _HEURISTIC_RULES}
        if enabled_rules is None
        else set(enabled_rules)
    )
    active_rules = [r for r in _HEURISTIC_RULES
                    if r.name in enabled and r.confidence >= min_confidence]
    if not active_rules:
        return []

    skip = _existing_direct_keys(conn)
    out: list[HeuristicTag] = []
    for nid, qname, file, start_line in _load_function_nodes(conn):
        name = _bare_name(qname)
        if not name:
            continue
        for rule in active_rules:
            if not rule.pattern.search(name):
                continue
            if (nid, rule.taxonomy_id) in skip:
                continue
            out.append(HeuristicTag(
                node_id=nid,
                qname=qname,
                file=file or "",
                line=int(start_line) if start_line is not None else 0,
                taxonomy_id=rule.taxonomy_id,
                kind=rule.kind,
                severity=rule.severity,
                source="implicit_naming",
                confidence=round(rule.confidence, 4),
                rule_name=rule.name,
                note=rule.note,
                evidence={"matched_name": name, "rule": rule.name,
                          "pattern": rule.pattern.pattern},
            ))
    return out


def persist(
    conn: sqlite3.Connection,
    tags: list[HeuristicTag],
    *,
    clear_existing: bool = True,
) -> dict:
    stats = {"cleared": 0, "inserted": 0, "duplicate": 0}
    cur = conn.cursor()
    if clear_existing:
        before = conn.total_changes
        cur.execute(
            "DELETE FROM node_tags WHERE source = 'implicit_naming'"
        )
        stats["cleared"] = conn.total_changes - before
    for t in tags:
        evidence_json = json.dumps(t.evidence, separators=(",", ":"))
        before = conn.total_changes
        cur.execute(
            "INSERT OR IGNORE INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source, "
            " confidence, evidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (t.node_id, t.taxonomy_id, t.kind, t.severity, t.line,
             t.source, t.confidence, evidence_json),
        )
        if conn.total_changes > before:
            stats["inserted"] += 1
        else:
            stats["duplicate"] += 1
    conn.commit()
    return stats


def _append_jsonl(out_path: Path, tags: list[HeuristicTag]) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("a", encoding="utf-8") as f:
        for t in tags:
            f.write(json.dumps(asdict(t), separators=(",", ":")) + "\n")
            n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument(
        "--enable",
        action="store_true",
        help="Required: run the heuristic. Default is dry-run-only.",
    )
    ap.add_argument(
        "--rules",
        default=None,
        help="Comma-separated subset of rule names to enable. Default: all.",
    )
    ap.add_argument("--min-confidence", type=float, default=0.0)
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    tlx_sys_path()

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db_path.exists():
        print(f"error: per-target DB missing: {db_path}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "naming-heuristic",
                                FileNotFoundError(str(db_path)))
        return 2

    t0 = time.monotonic()
    enabled_rules = (
        [r.strip() for r in args.rules.split(",") if r.strip()]
        if args.rules else None
    )

    conn = sqlite3.connect(str(db_path))
    try:
        # Migrate snapshot if necessary (older DBs lack confidence column).
        cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
        if "confidence" not in cols:
            conn.execute(
                "ALTER TABLE node_tags ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0"
            )
        if "evidence" not in cols:
            conn.execute(
                "ALTER TABLE node_tags ADD COLUMN evidence TEXT"
            )
        if "source" not in cols:
            conn.execute(
                "ALTER TABLE node_tags ADD COLUMN source TEXT NOT NULL DEFAULT 'regex'"
            )
        conn.commit()

        tags = discover(
            conn,
            enabled_rules=enabled_rules,
            min_confidence=args.min_confidence,
        )

        by_rule: dict[str, int] = {}
        by_kind = {"sink": 0, "source": 0}
        for t in tags:
            by_rule[t.rule_name] = by_rule.get(t.rule_name, 0) + 1
            by_kind[t.kind] = by_kind.get(t.kind, 0) + 1

        persist_stats = {"cleared": 0, "inserted": 0, "duplicate": 0}
        appended = 0
        jsonl_path = target / "tags_discovered.jsonl"
        if args.enable:
            persist_stats = persist(conn, tags, clear_existing=True)
            appended = _append_jsonl(jsonl_path, tags)

        elapsed_s = round(time.monotonic() - t0, 3)
        summary = {
            "target": target.name,
            "db": str(db_path),
            "enabled": bool(args.enable),
            "rules_requested": enabled_rules or "all",
            "candidate_count": len(tags),
            "by_kind": by_kind,
            "by_rule": by_rule,
            "persist": persist_stats,
            "jsonl_path": str(jsonl_path),
            "jsonl_appended": appended,
            "elapsed_s": elapsed_s,
        }
        print(json.dumps(summary, indent=2))

        if not args.no_status and args.enable:
            write_status_phase(
                target,
                "naming_heuristic",
                {
                    "status": "done",
                    "ts": utcnow(),
                    "candidate_count": len(tags),
                    "by_kind": by_kind,
                    "by_rule": by_rule,
                    "inserted": persist_stats["inserted"],
                    "cleared": persist_stats["cleared"],
                    "elapsed_s": elapsed_s,
                    "rules_enabled": enabled_rules or sorted(
                        {r.name for r in _HEURISTIC_RULES}
                    ),
                },
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
