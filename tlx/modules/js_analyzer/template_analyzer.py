"""Template analysis for Vue / Angular markup.

Babel does not parse `.vue` single-file components or `.html` Angular template
files, so the AST extractor never sees `v-html="..."` or `[innerHTML]="..."`
bindings. This module fills that gap with stdlib regex and emits tag dicts in
the same shape as `ast_extractor.js` produces (`rule_id`, `kind`, `line`,
`severity`, `col`, `context`).

Public API:

    analyze_template(file_path: str, content: str, frameworks: set[str])
        -> list[dict]

Returns one dict per match. Caller is expected to merge these into the
`node_tags` table the same way AST tags are merged.
"""

from __future__ import annotations

import re
from pathlib import Path

_VUE_V_HTML_RE         = re.compile(r"""v-html\s*=\s*(['"])(.*?)\1""")
_NG_INNER_HTML_RE      = re.compile(
    r"""\[(innerHTML|outerHTML)\]\s*=\s*(['"])(.*?)\2""",
)
_NG_BYPASS_TRUST_RE    = re.compile(
    r"""\bbypassSecurityTrust(Html|Script|ResourceUrl|Style|Url)\s*\(""",
)
_STRING_LITERAL_BIND_RE = re.compile(r"""^['"][^'"]*['"]\s*$""")


def _line_of(text: str, offset: int) -> int:
    """1-based line number for a char offset in `text`."""
    if offset <= 0:
        return 1
    # count newlines up to offset, +1 for 1-based
    return text.count("\n", 0, offset) + 1


def _emit(rule_id: str, kind: str, severity: str, line: int,
          context: dict) -> dict:
    return {
        "rule_id": rule_id,
        "kind":    kind,
        "severity": severity,
        "line":    line,
        "col":     0,
        "context": context,
    }


def analyze_template(
    file_path: str,
    content: str,
    frameworks: set[str] | frozenset[str] | None,
) -> list[dict]:
    """Scan a `.vue` / `.html` / `.ts` file for framework template sinks.

    `frameworks` gates which rules fire — passing None / empty disables
    everything. Returns a flat list of tag dicts (possibly empty).
    """
    if not content:
        return []
    fws = set(frameworks or ())
    if not fws:
        return []

    suffix = Path(file_path).suffix.lower()
    out: list[dict] = []

    # Vue v-html — only meaningful for .vue templates
    if "vue" in fws and suffix == ".vue":
        for m in _VUE_V_HTML_RE.finditer(content):
            expr = m.group(2).strip()
            if not expr:
                continue
            # Skip plain string literal bindings — `v-html="'<b>hi</b>'"`
            if _STRING_LITERAL_BIND_RE.match(expr):
                continue
            out.append(_emit(
                "vue_v_html_sink", "sink", "high",
                _line_of(content, m.start()),
                {"expression": expr},
            ))

    # Angular [innerHTML] / [outerHTML] — typically lives in .html templates
    if "angular" in fws and suffix in (".html", ".htm"):
        for m in _NG_INNER_HTML_RE.finditer(content):
            expr = m.group(3).strip()
            if not expr:
                continue
            out.append(_emit(
                "angular_inner_html_binding", "sink", "high",
                _line_of(content, m.start()),
                {"binding": m.group(1), "expression": expr},
            ))

    # Angular bypassSecurityTrust* in component .ts files
    if "angular" in fws and suffix in (".ts", ".tsx", ".js"):
        for m in _NG_BYPASS_TRUST_RE.finditer(content):
            out.append(_emit(
                "angular_bypass_trust_html", "sink", "critical",
                _line_of(content, m.start()),
                {"variant": m.group(1)},
            ))

    return out
