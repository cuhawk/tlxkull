"""Trusted Types policy body analyzer.

Plan: plans/ARCHITECTURE_EVOLUTION.md §9 (Sanitizer reality + Trusted
Types coupling).

The static taxonomy already tags every ``trustedTypes.createPolicy``
call with ``trusted_types_create_policy``. That tells us *where* a
policy is defined; it tells us nothing about *what* the policy's
``createHTML`` / ``createScript`` / ``createScriptURL`` handlers
actually do.

This module classifies each handler body into one of:

  identity        — handler returns its input unchanged (or after a
                    trivial pass-through). Effective block_p = 0.10.
  regex_only      — handler returns input only if a regex matches.
                    block_p = 0.20.
  substring_check — startsWith / includes / endsWith gate, no rewrite.
                    block_p = 0.25.
  string_replace  — handler runs `.replace(/.../, '')` patterns.
                    block_p = 0.30.
  reject_all      — handler returns null / throws unconditionally.
                    block_p = 0.99.
  dompurify       — handler delegates to DOMPurify.sanitize.
                    block_p = 0.95 (further tuned by sanitizer_registry).
  sanitize_html   — handler delegates to sanitize-html / xss libs.
                    block_p = 0.92.
  unknown         — none of the above; opaque (perhaps async fetch).
                    block_p = 0.40.

The output is persisted to the ``tt_policies`` table (added in
v2_schema.py at schema_version=3). One row per (node_id, handler).

The analyzer is regex-based against snippets, deliberately not AST-
based: in heavily-minified bundles the AST tree is not stable and
regex on the *original* source range gives high recall. False
positives are dampened by the conservative block_p mapping above.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


__all__ = [
    "TTPolicyVerdict",
    "classify_handler",
    "discover_and_persist",
    "BLOCK_P",
]


# Effective block-probability per body class. Public so other modules
# (chain_v2_wiring.score_sink) can adjust the chain confidence.
BLOCK_P = {
    "identity": 0.10,
    "regex_only": 0.20,
    "substring_check": 0.25,
    "string_replace": 0.30,
    "reject_all": 0.99,
    "dompurify": 0.95,
    "sanitize_html": 0.92,
    "unknown": 0.40,
}


@dataclass
class TTPolicyVerdict:
    node_id: int
    policy_name: str | None
    handler: str            # 'createHTML' | 'createScript' | 'createScriptURL'
    body_class: str
    block_p: float
    rationale: str
    file: str | None = None
    line: int | None = None


_HANDLER_NAMES = ("createHTML", "createScript", "createScriptURL")

# Outer policy body: trustedTypes.createPolicy('name', { ... })
# We extract the object-literal body so we can locate the handlers.
_POLICY_RE = re.compile(
    r"trustedTypes\.createPolicy\s*\(\s*"
    r"(['\"]?)(?P<name>[^'\"\),]*)\1\s*,\s*"
    r"(?P<body>\{[\s\S]*?\}\s*\))",
    re.MULTILINE,
)

# Per-handler: createHTML: (s) => <body> or createHTML(s) { ... } or
# createHTML: function(s) { ... }. We rely on a non-greedy block match
# and arrow-vs-brace dispatch.
def _handler_pattern(handler: str) -> re.Pattern:
    return re.compile(
        rf"\b{handler}\s*[:=]\s*"
        rf"(?:(?:function\s*)?\(\s*(?P<arg>[\w$]+)\s*\)|(?P<arg2>[\w$]+))"
        rf"\s*(?:=>\s*)?"
        rf"(?P<body>(?:\{{(?:[^{{}}]|\{{[^{{}}]*\}}){{0,3000}}\}})|(?:[^,;\n]+))",
        re.DOTALL,
    )


# Identity: arrow returns the argument directly, or function body
# does ``return <arg>;`` with nothing else.
def _is_identity(body: str, arg: str) -> bool:
    body = body.strip()
    # arrow: `(s) => s`
    if body == arg:
        return True
    if re.fullmatch(rf"\{{\s*return\s+{re.escape(arg)}\s*;?\s*\}}", body):
        return True
    return False


def _is_reject_all(body: str) -> bool:
    body = body.strip()
    if body in ("null", "''", '""', "undefined"):
        return True
    if re.fullmatch(r"\{\s*(?:return\s+(?:null|''|\"\"|undefined)\s*;?\s*)?\}", body):
        return True
    if re.search(r"\bthrow\b", body) and not re.search(r"\breturn\b", body):
        return True
    return False


def _delegates_to(body: str, lib_re: re.Pattern) -> bool:
    return bool(lib_re.search(body))


_DOMPURIFY_RE = re.compile(r"\bDOMPurify(?:\.[\w$]+)*\s*\(", re.IGNORECASE)
_SANITIZE_HTML_RE = re.compile(
    r"\b(?:sanitize[-_]?html|xss|sanitizeHtml|sanitize)\s*\(", re.IGNORECASE
)
_REGEX_TEST_RE = re.compile(
    r"\.\s*test\s*\(|\.\s*match\s*\(", re.IGNORECASE
)
_SUBSTRING_RE = re.compile(
    r"\.\s*(?:startsWith|endsWith|includes|indexOf)\s*\(", re.IGNORECASE
)
_REPLACE_RE = re.compile(r"\.\s*replace\s*\(", re.IGNORECASE)


def classify_handler(body: str, arg: str | None = None) -> tuple[str, str]:
    """Return (body_class, rationale)."""
    arg = arg or "s"
    body = body.strip()
    if _is_identity(body, arg):
        return "identity", "handler returns its argument unchanged"
    if _is_reject_all(body):
        return "reject_all", "handler returns null/empty unconditionally"
    if _delegates_to(body, _DOMPURIFY_RE):
        return "dompurify", "handler delegates to DOMPurify"
    if _delegates_to(body, _SANITIZE_HTML_RE):
        return "sanitize_html", "handler delegates to sanitize-html / xss lib"
    if _REGEX_TEST_RE.search(body):
        return "regex_only", "handler gate uses .test() / .match() — no rewrite"
    if _SUBSTRING_RE.search(body):
        return "substring_check", "handler gate uses startsWith/includes/indexOf"
    if _REPLACE_RE.search(body):
        return "string_replace", "handler relies on .replace() — bypass-prone"
    return "unknown", "handler body did not match any classifier signal"


# ---------------------------------------------------------------------------
# Discovery: pull every trusted_types_create_policy site and classify
# ---------------------------------------------------------------------------


def _read_snippet(file: str | None, line: int | None, *, window: int = 120) -> str | None:
    """Read ``[line - window/2 .. line + window/2]`` of ``file``.

    Best-effort. Returns None if the file is missing or unreadable. We
    deliberately don't sandbox the path: js_analyzer already restricts
    indexing to in-scope sources, so this is the same file the AST
    extractor already consumed.
    """
    if not file or not line:
        return None
    try:
        text = Path(file).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    lines = text.splitlines()
    start = max(0, line - window // 2)
    end = min(len(lines), line + window // 2)
    return "\n".join(lines[start:end])


def discover(
    conn: sqlite3.Connection, *, snippet_window_lines: int = 120
) -> list[TTPolicyVerdict]:
    """Find every ``trusted_types_create_policy`` site, slice its
    surrounding snippet, and classify each of createHTML / createScript
    / createScriptURL.

    Returns one verdict per (node, handler) pair found.
    """
    try:
        rows = conn.execute(
            "SELECT n.id, n.qualified_name, n.file, t.line "
            "FROM node_tags t JOIN nodes n ON n.id = t.node_id "
            "WHERE t.taxonomy_id = 'trusted_types_create_policy'"
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    out: list[TTPolicyVerdict] = []
    for node_id, qname, file, line in rows:
        snippet = _read_snippet(file, line, window=snippet_window_lines)
        if not snippet:
            continue
        for m in _POLICY_RE.finditer(snippet):
            policy_name = (m.group("name") or "").strip("'\" ") or None
            body = m.group("body") or ""
            for handler in _HANDLER_NAMES:
                hpat = _handler_pattern(handler)
                hm = hpat.search(body)
                if not hm:
                    continue
                arg = hm.group("arg") or hm.group("arg2") or "s"
                h_body = hm.group("body") or ""
                body_class, rationale = classify_handler(h_body, arg)
                out.append(
                    TTPolicyVerdict(
                        node_id=int(node_id),
                        policy_name=policy_name,
                        handler=handler,
                        body_class=body_class,
                        block_p=BLOCK_P[body_class],
                        rationale=rationale,
                        file=file,
                        line=line,
                    )
                )
    return out


def persist(conn: sqlite3.Connection, verdicts: Iterable[TTPolicyVerdict]) -> int:
    cur = conn.cursor()
    n = 0
    for v in verdicts:
        cur.execute(
            "INSERT INTO tt_policies "
            "  (node_id, policy_name, handler, body_class, block_p, "
            "   rationale, file, line) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(node_id, handler) DO UPDATE SET "
            "  policy_name = excluded.policy_name, "
            "  body_class = excluded.body_class, "
            "  block_p = excluded.block_p, "
            "  rationale = excluded.rationale",
            (
                v.node_id, v.policy_name, v.handler, v.body_class,
                float(v.block_p), v.rationale, v.file, v.line,
            ),
        )
        n += 1
    return n


def discover_and_persist(conn: sqlite3.Connection) -> dict:
    verdicts = discover(conn)
    saved = persist(conn, verdicts)
    conn.commit()
    return {
        "verdicts": [
            {
                "node_id": v.node_id,
                "policy_name": v.policy_name,
                "handler": v.handler,
                "body_class": v.body_class,
                "block_p": v.block_p,
            }
            for v in verdicts
        ],
        "saved": saved,
    }
