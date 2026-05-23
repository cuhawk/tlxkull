"""Static audit of TLX skills + bin scripts for Anthropic prompt-cache-busting.

Pure static scan — no LLM calls. Flags patterns that perturb the cached
prefix of every Claude request (datetime/random/uuid interpolation into
prompt bodies, oversize skill descriptions, template tokens at the top
of skill files, timestamps at the head of prompt files).

CLI:
    python3 bin/cache_audit.py --report   # JSON to stdout
    python3 bin/cache_audit.py --md       # markdown to stdout
    python3 bin/cache_audit.py --md --out audit.md
    python3 bin/cache_audit.py --paths .claude/skills bin tlx/modules

Severity:
    high  — datetime/random/uuid call inside a prompt-render scope, or
            template token / timestamp at the top of a skill / prompt file.
    med   — skill frontmatter ``description:`` over 250 chars.
    low   — time.time() / random.random() found outside a clear prompt
            scope (still worth a look — context may be heuristic).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ROOT, utcnow  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_ROOTS = [
    ".claude/skills",
    "bin",
    "tlx/prompts",
    "tlx/kernel/prompts",
    "tlx/modules/js_analyzer/prompts",
]

EXCLUDE_DIRS = {
    "__pycache__",
    "node_modules",
    ".venv",
    ".git",
    "targets",
    "wiki",
    "inbox",
    "graphify-out",
}

MAX_FILE_BYTES = 500_000

# Cache-busting call names we look for in Python prompt-render scopes.
BUSTING_CALLS = {
    "datetime.now",
    "datetime.utcnow",
    "time.time",
    "time.localtime",
    "os.getcwd",
    "uuid.uuid4",
    "uuid.uuid1",
    "random.random",
    "random.randint",
}
# secrets.token_* — wildcard via prefix
BUSTING_PREFIXES = ("secrets.token_",)

# Variable / function names that imply "we are building a prompt here".
PROMPT_NAMES = ("prompt", "_prompt", "body", "template", "system_prompt")

# Filename hints for Python prompt builders.
PROMPT_BUILDER_SUFFIXES = ("_runner.py", "_route.py", "_audit.py")

# Skill template tokens (top-of-file region).
TEMPLATE_TOKEN_RE = re.compile(r"(\{\{\s*NOW\s*\}\}|\{date\}|\$\{TIMESTAMP\})")

# Timestamp-shape patterns for prompts/*.md head region.
TIMESTAMP_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}|\bnow:\s|\bgenerated_at\b)")

# Frontmatter description threshold.
DESC_MAX = 250


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _snip(s: str, n: int = 120) -> str:
    s = s.strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def _walk(root: Path):
    if not root.exists():
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        # exclude by any path component
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        # ensure inside repo root
        try:
            path.relative_to(ROOT)
        except ValueError:
            continue
        yield path


# ---------------------------------------------------------------------------
# Python AST scan
# ---------------------------------------------------------------------------


def _call_qname(node: ast.Call) -> str | None:
    """Return ``module.attr`` style qname for ``Call`` whose func is an Attribute."""
    f = node.func
    parts: list[str] = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
        return ".".join(reversed(parts))
    return None


def _is_busting(qname: str) -> bool:
    if qname in BUSTING_CALLS:
        return True
    return any(qname.startswith(pfx) for pfx in BUSTING_PREFIXES)


def _enclosing_prompt_scope(node: ast.AST, parents: dict[int, ast.AST]) -> str | None:
    """Walk up parents — return the prompt-ish name we hit, else None.

    Considers: enclosing FunctionDef name, enclosing Assign target name(s).
    """
    cur: ast.AST | None = node
    seen_lines = 0
    while cur is not None and seen_lines < 100:
        parent = parents.get(id(cur))
        if parent is None:
            break
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = parent.name.lower()
            if any(p in name for p in PROMPT_NAMES):
                return f"function:{parent.name}"
        if isinstance(parent, ast.Assign):
            for tgt in parent.targets:
                tname = _target_name(tgt)
                if tname and any(p in tname.lower() for p in PROMPT_NAMES):
                    return f"assign:{tname}"
        if isinstance(parent, ast.AnnAssign):
            tname = _target_name(parent.target)
            if tname and any(p in tname.lower() for p in PROMPT_NAMES):
                return f"assign:{tname}"
        cur = parent
        seen_lines += 1
    return None


def _target_name(t: ast.AST) -> str | None:
    if isinstance(t, ast.Name):
        return t.id
    if isinstance(t, ast.Attribute):
        return t.attr
    return None


def _build_parents(tree: ast.AST) -> dict[int, ast.AST]:
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent
    return parents


def _line_snippet(src_lines: list[str], lineno: int) -> str:
    if 1 <= lineno <= len(src_lines):
        return _snip(src_lines[lineno - 1])
    return ""


def _has_nearby_prompt_marker(src_lines: list[str], lineno: int) -> bool:
    """Look backward up to 100 lines for a prompt-name token."""
    start = max(0, lineno - 100)
    region = "\n".join(src_lines[start:lineno]).lower()
    return any(p in region for p in PROMPT_NAMES)


def scan_python(path: Path, issues: list[dict]) -> None:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return
    parents = _build_parents(tree)
    src_lines = src.splitlines()

    is_prompt_builder = path.name.endswith(PROMPT_BUILDER_SUFFIXES) or (
        "_prompts" in src
    )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        qname = _call_qname(node)
        if not qname or not _is_busting(qname):
            continue
        scope = _enclosing_prompt_scope(node, parents)
        in_prompt_scope = scope is not None or _has_nearby_prompt_marker(
            src_lines, node.lineno
        )
        if in_prompt_scope or is_prompt_builder:
            issues.append(
                {
                    "file": _rel(path),
                    "kind": "datetime_in_prompt",
                    "line": node.lineno,
                    "snippet": _line_snippet(src_lines, node.lineno),
                    "severity": "high",
                    "fix_hint": (
                        f"Move `{qname}(...)` outside the cached prompt prefix "
                        "or pin it to a stable value."
                    ),
                }
            )
        else:
            issues.append(
                {
                    "file": _rel(path),
                    "kind": "time_call_no_context",
                    "line": node.lineno,
                    "snippet": _line_snippet(src_lines, node.lineno),
                    "severity": "low",
                    "fix_hint": (
                        f"`{qname}(...)` flagged heuristically — confirm it does "
                        "not feed an LLM prompt body."
                    ),
                }
            )

    # f-string interpolation of datetime/time/uuid inside a prompt-shaped string.
    for node in ast.walk(tree):
        if not isinstance(node, ast.JoinedStr):
            continue
        # Need a sibling string-section that looks prompt-ish OR an enclosing
        # prompt-name scope.
        text_chunks = [
            v.value for v in node.values if isinstance(v, ast.Constant) and isinstance(v.value, str)
        ]
        looks_prompty = any(
            re.search(r"prompt|system|user_message|<task>|assistant", t, re.I)
            for t in text_chunks
        )
        if not looks_prompty:
            continue
        for v in node.values:
            if not isinstance(v, ast.FormattedValue):
                continue
            inner = v.value
            for sub in ast.walk(inner):
                if isinstance(sub, ast.Call):
                    q = _call_qname(sub)
                    if q and _is_busting(q):
                        issues.append(
                            {
                                "file": _rel(path),
                                "kind": "datetime_in_prompt",
                                "line": getattr(sub, "lineno", node.lineno),
                                "snippet": _line_snippet(
                                    src_lines, getattr(sub, "lineno", node.lineno)
                                ),
                                "severity": "high",
                                "fix_hint": (
                                    f"f-string interpolates `{q}(...)` into prompt body "
                                    "— bind once outside the cached prefix."
                                ),
                            }
                        )


# ---------------------------------------------------------------------------
# Markdown skill scan
# ---------------------------------------------------------------------------


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[3:end], text[end + 4 :]


def _frontmatter_field(fm: str, name: str) -> tuple[str, int] | None:
    """Return (value, line-within-fm) for a single-line ``name: value`` field.

    Handles ``name: |`` and ``name: >`` block scalars by joining following
    indented lines.
    """
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"\s*{re.escape(name)}\s*:\s*(.*)", line)
        if not m:
            continue
        value = m.group(1).strip()
        if value in ("|", ">", "|-", ">-"):
            block: list[str] = []
            for j in range(i + 1, len(lines)):
                nxt = lines[j]
                if nxt and not nxt.startswith((" ", "\t")):
                    break
                block.append(nxt.strip())
            value = " ".join(b for b in block if b)
        # +1 for the discarded leading '---' line in the original file
        return value, i + 1
    return None


def scan_skill_md(path: Path, issues: list[dict]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    fm, body = _split_frontmatter(text)

    # Long description in frontmatter.
    if fm:
        got = _frontmatter_field(fm, "description")
        if got:
            value, line = got
            if len(value) > DESC_MAX:
                issues.append(
                    {
                        "file": _rel(path),
                        "kind": "long_description",
                        "line": line + 1,  # +1 for opening '---'
                        "snippet": _snip(value),
                        "severity": "med",
                        "fix_hint": (
                            f"description is {len(value)} chars; trim to "
                            f"<={DESC_MAX} (loaded eagerly into system block)."
                        ),
                    }
                )

    # Template tokens in the cache-key prefix region (top ~30% of file).
    lines = text.splitlines()
    cutoff = max(10, int(len(lines) * 0.30))
    for i, line in enumerate(lines[:cutoff], start=1):
        m = TEMPLATE_TOKEN_RE.search(line)
        if m:
            issues.append(
                {
                    "file": _rel(path),
                    "kind": "template_token",
                    "line": i,
                    "snippet": _snip(line),
                    "severity": "high",
                    "fix_hint": (
                        f"Template token `{m.group(0)}` in top of skill body — "
                        "interpolation will bust the system-prompt cache."
                    ),
                }
            )


# ---------------------------------------------------------------------------
# Prompt-file (*.md) scan
# ---------------------------------------------------------------------------


def scan_prompt_md(path: Path, issues: list[dict]) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    lines = text.splitlines()
    if not lines:
        return
    cutoff = max(5, int(len(lines) * 0.30))
    for i, line in enumerate(lines[:cutoff], start=1):
        m = TIMESTAMP_RE.search(line)
        if m:
            issues.append(
                {
                    "file": _rel(path),
                    "kind": "timestamp_in_prompt_file",
                    "line": i,
                    "snippet": _snip(line),
                    "severity": "high",
                    "fix_hint": (
                        f"Timestamp-shaped string `{m.group(0)}` in top {cutoff} lines — "
                        "move below the stable prefix or strip entirely."
                    ),
                }
            )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def _is_skill_md(path: Path) -> bool:
    return path.name == "SKILL.md" and ".claude/skills/" in str(path).replace("\\", "/")


def _is_prompt_md(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    return path.suffix == ".md" and ("/prompts/" in s or "/_prompts/" in s)


def run_scan(roots: list[Path]) -> tuple[list[dict], int]:
    issues: list[dict] = []
    scanned = 0
    seen: set[Path] = set()
    for root in roots:
        for path in _walk(root):
            if path in seen:
                continue
            seen.add(path)
            scanned += 1
            if path.suffix == ".py":
                scan_python(path, issues)
            elif _is_skill_md(path):
                scan_skill_md(path, issues)
                # also subject to prompt-file timestamp scan
                scan_prompt_md(path, issues)
            elif _is_prompt_md(path):
                scan_prompt_md(path, issues)
    # stable sort: severity (high < med < low), then file, then line
    sev_order = {"high": 0, "med": 1, "low": 2}
    issues.sort(key=lambda x: (sev_order.get(x["severity"], 9), x["file"], x["line"]))
    return issues, scanned


def render_markdown(payload: dict) -> str:
    out: list[str] = []
    out.append("# Prompt cache audit")
    out.append("")
    out.append(f"- audited_at: `{payload['audited_at']}`")
    out.append(f"- files_scanned: **{payload['files_scanned']}**")
    out.append(f"- issues: **{len(payload['issues'])}**")
    if payload["by_severity"]:
        sev_bits = ", ".join(
            f"{k}: {v}" for k, v in sorted(payload["by_severity"].items())
        )
        out.append(f"- by_severity: {sev_bits}")
    if payload["by_kind"]:
        kind_bits = ", ".join(
            f"{k}: {v}" for k, v in sorted(payload["by_kind"].items())
        )
        out.append(f"- by_kind: {kind_bits}")
    out.append("")

    by_sev: dict[str, list[dict]] = defaultdict(list)
    for issue in payload["issues"]:
        by_sev[issue["severity"]].append(issue)

    for sev in ("high", "med", "low"):
        rows = by_sev.get(sev, [])
        if not rows:
            continue
        out.append(f"## {sev} ({len(rows)})")
        out.append("")
        for r in rows:
            out.append(f"- **{r['kind']}** — `{r['file']}:{r['line']}`")
            if r.get("snippet"):
                out.append(f"  - snippet: `{r['snippet']}`")
            out.append(f"  - fix: {r['fix_hint']}")
        out.append("")
    if not payload["issues"]:
        out.append("_No issues found._")
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="JSON to stdout")
    ap.add_argument("--md", action="store_true", help="markdown to stdout")
    ap.add_argument("--out", type=Path, help="write markdown to this file")
    ap.add_argument(
        "--paths",
        nargs="+",
        default=None,
        help="override default scan roots (paths relative to repo root or absolute)",
    )
    args = ap.parse_args(argv)

    if args.paths:
        roots = [
            (Path(p) if Path(p).is_absolute() else ROOT / p).resolve()
            for p in args.paths
        ]
    else:
        roots = [(ROOT / p).resolve() for p in DEFAULT_ROOTS]

    issues, scanned = run_scan(roots)
    by_kind = dict(Counter(i["kind"] for i in issues))
    by_severity = dict(Counter(i["severity"] for i in issues))

    payload = {
        "audited_at": utcnow(),
        "files_scanned": scanned,
        "issues": issues,
        "by_kind": by_kind,
        "by_severity": by_severity,
    }

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render_markdown(payload), encoding="utf-8")
        return 0
    if args.md:
        sys.stdout.write(render_markdown(payload))
        if not render_markdown(payload).endswith("\n"):
            sys.stdout.write("\n")
        return 0
    # default + --report
    sys.stdout.write(json.dumps(payload, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
