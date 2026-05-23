#!/usr/bin/env python3
"""Audit `.claude/skills/**/SKILL.md` for hygiene issues.

Pure static scan -- no LLM calls. Catches stale prompting patterns that
the May 2026 Claude prompting guidance flags:

1. Old thinking-toggle artifacts (adaptive thinking replaces them).
2. `IMPORTANT:` / `NEVER:` / `DO NOT:` instructions without a date marker
   -- undated absolutes overfit to the moment they were written and rot.
3. One-sided cost statements (mentions "expensive" / "$" / "budget" with
   no counterweight clause).
4. General exhortations ("be thorough", "think step by step") that don't
   name a concrete tool/skill -- capability comes from tools, not pep
   talks.
5. Description frontmatter shape -- length and trigger-phrase presence.
6. Frontmatter health -- missing `name:` / `description:` / name-vs-dir
   mismatch.
7. Long skills (>250 lines) with no level-2 headers (soft signal that
   the skill should be restructured).

CLI mirrors `cache_audit.py` (parallel work): `--report` for JSON,
`--md` for markdown, `--out <path>` to write to a file, `--paths` to
override the default scan root (defaults to `.claude/skills`).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, utcnow  # noqa: E402

# ---------------------------------------------------------------------------
# Severity ladder

SEVERITY = {
    "stale_thinking_toggle": "high",
    "missing_frontmatter": "high",
    "name_mismatch": "high",
    "undated_important": "med",
    "one_sided_cost": "med",
    "long_description": "med",
    "no_trigger_phrase_in_description": "med",
    "general_exhortation": "low",
    "no_headers_long_skill": "low",
}

MAX_PER_KIND = 50

# ---------------------------------------------------------------------------
# Patterns

# 1. stale thinking toggles
THINKING_PATTERNS = [
    r"--no-thinking",
    r"thinking\s*:\s*off",
    r"thinking_off",
    r"disable\s+thinking",
    r"no\s+thinking\s+mode",
    r"set\s+thinking\s+to\s+false",
    r"thinking\s*=\s*false",
]
THINKING_RE = re.compile("|".join(THINKING_PATTERNS), re.IGNORECASE)

# 2. dated marker -- ISO date OR (YYYY-MM) / (YYYY-Qn)
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
LOOSE_DATE_RE = re.compile(r"\(\s*\d{4}-(?:\d{2}|Q[1-4])\s*\)", re.IGNORECASE)
IMPORTANT_PREFIX_RE = re.compile(
    r"^\s*(?:[#*\-]\s*)*(?:\*\*)?(?:IMPORTANT|NEVER|DO\s*NOT)\b[: ]",
    re.IGNORECASE,
)

# 3. one-sided cost
COST_TOKENS = re.compile(
    r"(?:\bexpensive\b|\bcostly\b|\bbudget\b|\$\d|\bpricey\b)", re.IGNORECASE
)
NEG_ACTION = re.compile(
    r"\b(?:skip|avoid|don't|do\s*not|never|drop|disable)\b", re.IGNORECASE
)
COUNTERWEIGHT = re.compile(
    r"\b(?:but|however|tradeoff|trade-off|miss|wrong|fp\b|tp\b|fail|risk|"
    r"unless|except|otherwise)\b",
    re.IGNORECASE,
)

# 4. general exhortations
EXHORTATION_RE = re.compile(
    r"\b(?:always\s+reason\s+carefully|be\s+thorough|think\s+(?:step\s*by\s*step|"
    r"carefully|hard)|reason\s+deeply|use\s+your\s+best\s+judgment|"
    r"take\s+your\s+time|don't\s+rush)\b",
    re.IGNORECASE,
)
# concrete tool/skill mention -- backticks, slash-commands, MCP tool, .py,
# or known capability verbs paired with names.
CONCRETE_TOOL_RE = re.compile(
    r"(?:`[^`]+`|/[a-z][\w-]+|mcp__\w+|\b[a-z_][\w-]*\.py\b|"
    r"\b(?:run|call|invoke|dispatch)\s+(?:the\s+)?[`a-z][\w./-]*)",
    re.IGNORECASE,
)

# 5. description trigger phrases
TRIGGER_PHRASES = [
    "use when",
    "trigger:",
    "run after",
    "run when",
    "use this skill",
]


# ---------------------------------------------------------------------------
# Frontmatter parsing


def parse_frontmatter(text: str) -> tuple[dict, int]:
    """Return (fields, body_start_line_index). Manual YAML -- no PyYAML dep.

    Supports `key: value` and folded continuations (next line begins with
    whitespace). Empty dict if no frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, 0

    fields: dict[str, str] = {}
    current_key: str | None = None
    for raw in lines[1:end_idx]:
        if not raw.strip():
            continue
        if (raw.startswith(" ") or raw.startswith("\t")) and current_key:
            fields[current_key] = (fields[current_key] + " " + raw.strip()).strip()
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", raw)
        if m:
            current_key = m.group(1)
            fields[current_key] = m.group(2).strip()
    return fields, end_idx + 1


# ---------------------------------------------------------------------------
# Sentence-ish splitter


def sentences(line: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", line.strip())
    return [p for p in parts if p]


# ---------------------------------------------------------------------------
# Issue helpers


def make_issue(
    kind: str, path: Path, line: int, text: str, **extra
) -> dict:
    rel = str(path.relative_to(ROOT)) if path.is_absolute() else str(path)
    return {
        "kind": kind,
        "severity": SEVERITY[kind],
        "file": rel,
        "line": line,
        "text": text.strip()[:220],
        **extra,
    }


def has_dated_marker(
    lines: list[str], idx: int, window: int = 3
) -> bool:
    """True if line idx or any of the next `window` lines carries a date."""
    end = min(len(lines), idx + 1 + window)
    for j in range(idx, end):
        if ISO_DATE_RE.search(lines[j]) or LOOSE_DATE_RE.search(lines[j]):
            return True
    return False


# ---------------------------------------------------------------------------
# Per-file scan


def scan_file(path: Path) -> list[dict]:
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    issues: list[dict] = []

    fields, body_start = parse_frontmatter(text)

    # ----- 6. frontmatter health
    if not fields:
        issues.append(make_issue("missing_frontmatter", path, 1, "no YAML frontmatter block"))
    else:
        if "name" not in fields or not fields.get("name"):
            issues.append(make_issue("missing_frontmatter", path, 1, "frontmatter missing `name:`"))
        if "description" not in fields or not fields.get("description"):
            issues.append(
                make_issue("missing_frontmatter", path, 1, "frontmatter missing `description:`")
            )
        # name vs dir
        if fields.get("name"):
            dir_name = path.parent.name
            if fields["name"].strip() != dir_name:
                issues.append(
                    make_issue(
                        "name_mismatch",
                        path,
                        1,
                        f"name={fields['name']!r} but parent dir={dir_name!r}",
                        skill_name=fields["name"],
                        dir_name=dir_name,
                    )
                )

    # ----- 5. description shape
    desc = (fields.get("description") or "").strip()
    if desc:
        if len(desc) > 350:
            issues.append(
                make_issue(
                    "long_description",
                    path,
                    1,
                    f"description is {len(desc)} chars (>350)",
                    length=len(desc),
                )
            )
        low = desc.lower()
        if not any(tp in low for tp in TRIGGER_PHRASES):
            issues.append(
                make_issue(
                    "no_trigger_phrase_in_description",
                    path,
                    1,
                    "description lacks any of: 'Use when' / 'Trigger:' / "
                    "'Run after' / 'Run when' / 'Use this skill'",
                )
            )

    # ----- 1, 2, 3, 4 require per-line scan over the *body* (and desc too --
    # stale toggles in the description count). Scan whole file for thinking
    # toggles; restrict the other checks to body to avoid double-flagging
    # frontmatter description text.
    for i, line in enumerate(lines, start=1):
        # 1. thinking toggles -- scan everywhere
        if THINKING_RE.search(line):
            issues.append(make_issue("stale_thinking_toggle", path, i, line))

    body_lines = lines[body_start:]
    for offset, line in enumerate(body_lines):
        i = body_start + offset + 1  # 1-indexed line number in file

        # 2. undated IMPORTANT / NEVER / DO NOT
        if IMPORTANT_PREFIX_RE.search(line):
            if not has_dated_marker(lines, i - 1, window=3):
                issues.append(make_issue("undated_important", path, i, line))

        # 3. one-sided cost -- per sentence
        for sent in sentences(line):
            if COST_TOKENS.search(sent) and NEG_ACTION.search(sent):
                if not COUNTERWEIGHT.search(sent):
                    issues.append(make_issue("one_sided_cost", path, i, sent))

        # 4. general exhortation without concrete tool
        if EXHORTATION_RE.search(line):
            # Look at the sentence containing the exhortation plus the next
            # line, in case the concrete tool is on the following line.
            window_text = line
            if offset + 1 < len(body_lines):
                window_text += " " + body_lines[offset + 1]
            if not CONCRETE_TOOL_RE.search(window_text):
                issues.append(make_issue("general_exhortation", path, i, line))

    # ----- 7. no headers in long skill
    if len(lines) > 250:
        if not any(re.match(r"^##\s+\S", ln) for ln in lines):
            issues.append(
                make_issue(
                    "no_headers_long_skill",
                    path,
                    1,
                    f"{len(lines)}-line skill has no level-2 (##) headers",
                    line_count=len(lines),
                )
            )

    return issues


# ---------------------------------------------------------------------------
# Walk


def iter_skill_files(roots: Iterable[Path]) -> Iterable[Path]:
    skip_parts = {"__pycache__", "node_modules", ".venv"}
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("SKILL.md"):
            if any(part in skip_parts for part in p.parts):
                continue
            yield p


# ---------------------------------------------------------------------------
# Aggregate


def cap_issues(issues: list[dict]) -> list[dict]:
    """Keep at most MAX_PER_KIND issues per kind. Stable order."""
    counts: dict[str, int] = {}
    out: list[dict] = []
    for iss in issues:
        k = iss["kind"]
        if counts.get(k, 0) >= MAX_PER_KIND:
            continue
        counts[k] = counts.get(k, 0) + 1
        out.append(iss)
    return out


def build_report(roots: list[Path]) -> dict:
    skill_files = sorted(iter_skill_files(roots))
    all_issues: list[dict] = []
    for f in skill_files:
        all_issues.extend(scan_file(f))

    by_kind: dict[str, int] = {}
    by_severity: dict[str, int] = {"high": 0, "med": 0, "low": 0}
    by_file: dict[str, int] = {}
    for iss in all_issues:
        by_kind[iss["kind"]] = by_kind.get(iss["kind"], 0) + 1
        by_severity[iss["severity"]] = by_severity.get(iss["severity"], 0) + 1
        by_file[iss["file"]] = by_file.get(iss["file"], 0) + 1

    return {
        "audited_at": utcnow(),
        "skills_scanned": len(skill_files),
        "issues": cap_issues(all_issues),
        "issues_total": len(all_issues),
        "by_kind": by_kind,
        "by_severity": by_severity,
        "by_file": by_file,
    }


# ---------------------------------------------------------------------------
# Markdown rendering


def render_markdown(report: dict) -> str:
    out: list[str] = []
    out.append("# Skill Hygiene Audit")
    out.append("")
    out.append(f"- audited_at: `{report['audited_at']}`")
    out.append(f"- skills_scanned: **{report['skills_scanned']}**")
    out.append(f"- issues_total: **{report['issues_total']}**")
    out.append(
        f"- by_severity: high={report['by_severity'].get('high', 0)}, "
        f"med={report['by_severity'].get('med', 0)}, "
        f"low={report['by_severity'].get('low', 0)}"
    )
    out.append("")

    out.append("## By kind")
    out.append("")
    out.append("| kind | severity | count |")
    out.append("| --- | --- | --- |")
    for kind in sorted(report["by_kind"], key=lambda k: -report["by_kind"][k]):
        out.append(
            f"| {kind} | {SEVERITY.get(kind, '?')} | {report['by_kind'][kind]} |"
        )
    out.append("")

    out.append("## Worst offenders (by file)")
    out.append("")
    out.append("| file | issues |")
    out.append("| --- | --- |")
    ranked = sorted(report["by_file"].items(), key=lambda kv: -kv[1])[:10]
    for f, n in ranked:
        out.append(f"| `{f}` | {n} |")
    out.append("")

    # Group issues by kind for the detail dump
    by_kind_issues: dict[str, list[dict]] = {}
    for iss in report["issues"]:
        by_kind_issues.setdefault(iss["kind"], []).append(iss)

    out.append("## Issues")
    out.append("")
    out.append(f"(capped at {MAX_PER_KIND} per kind)")
    out.append("")
    for kind in sorted(by_kind_issues, key=lambda k: (SEVERITY.get(k, "z"), k)):
        items = by_kind_issues[kind]
        out.append(f"### {kind} _(sev={SEVERITY.get(kind, '?')}, n={len(items)})_")
        out.append("")
        for iss in items:
            snippet = iss["text"].replace("|", "\\|")
            out.append(f"- `{iss['file']}:{iss['line']}` — {snippet}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


# ---------------------------------------------------------------------------
# CLI


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--paths",
        nargs="*",
        default=[".claude/skills"],
        help="One or more directories to scan (default: .claude/skills).",
    )
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument("--report", action="store_true", help="Emit JSON (default).")
    fmt.add_argument("--md", action="store_true", help="Emit markdown.")
    ap.add_argument("--out", help="Write output to this file instead of stdout.")
    args = ap.parse_args()

    roots = [Path(p) if Path(p).is_absolute() else (ROOT / p) for p in args.paths]
    report = build_report(roots)

    if args.md:
        rendered = render_markdown(report)
    else:
        rendered = json.dumps(report, indent=2, default=str) + "\n"

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered)
        print(f"wrote {out_path} ({len(rendered)} bytes)")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
