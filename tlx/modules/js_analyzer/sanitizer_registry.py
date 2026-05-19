"""Sanitizer reality registry — version + config awareness for sanitizers.

Plan: plans/ARCHITECTURE_EVOLUTION.md §5.

The static taxonomy (taxonomies/sanitizers.json) already marks calls
that *might* sanitize. This module asks two further questions:

1. Is the *library version* used in this target known to have an open
   bypass?  (e.g. DOMPurify < 2.0.17 = mXSS.)
2. Are any of the call's *config options* known to weaken its guarantee?
   (e.g. ``DOMPurify.sanitize(s, {ALLOWED_TAGS: ['*']})``.)

The output is a multiplicative ``sanitizer_confidence`` factor in
[0.0, 1.0]. The sanitizer-on-path stage multiplies this into its
verdict: a chain is only moved to ``sanitized.jsonl`` when the
effective confidence ≥ ``SANITIZER_CONFIDENCE_FLOOR`` (see
``js_analyzer_config``).

Pure module. Reads two sidecars (sanitizer_metadata.json,
target/library_versions.json) plus a snippet of source around the call
site to detect config flags. No LLM / network / DB writes.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

__all__ = [
    "SanitizerVerdict",
    "evaluate",
    "load_metadata",
    "load_library_versions",
    "version_in_range",
]

_DEFAULT_METADATA_PATH = (
    Path(__file__).resolve().parent / "taxonomies" / "sanitizer_metadata.json"
)


@dataclass
class SanitizerVerdict:
    sanitizer_id: str
    confidence: float                       # 0.0 = ineffective, 1.0 = nominal
    clears: list[str] = field(default_factory=list)   # flavors actually cleared at the observed call
    reasons: list[str] = field(default_factory=list)  # why confidence is < 1.0
    config_flags_observed: dict[str, Any] = field(default_factory=dict)
    library_version: str | None = None
    bypass_match: dict | None = None        # set if a known-bypass version range hit

    def is_effective(self, floor: float = 0.5) -> bool:
        return self.confidence >= floor

    def to_dict(self) -> dict:
        return {
            "sanitizer_id": self.sanitizer_id,
            "confidence": round(self.confidence, 4),
            "clears": self.clears,
            "reasons": self.reasons,
            "config_flags_observed": self.config_flags_observed,
            "library_version": self.library_version,
            "bypass_match": self.bypass_match,
        }


# ── Sidecar loaders ───────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def load_metadata(path: str | None = None) -> dict:
    p = Path(path) if path else _DEFAULT_METADATA_PATH
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    raw = {k: v for k, v in data.items() if not k.startswith("_")}
    # Resolve "inherit_from" references one level (idempotent).
    out: dict[str, dict] = {}
    for sid, meta in raw.items():
        if not isinstance(meta, dict):
            continue
        resolved = dict(meta)
        parent_id = resolved.pop("config_options_inherit_from", None)
        if parent_id and parent_id in raw:
            resolved.setdefault("config_options", [])
            resolved["config_options"] = list(raw[parent_id].get("config_options") or []) + list(resolved.get("config_options") or [])
        parent_id2 = resolved.pop("known_bypass_versions_inherit_from", None)
        if parent_id2 and parent_id2 in raw:
            resolved.setdefault("known_bypass_versions", [])
            resolved["known_bypass_versions"] = list(raw[parent_id2].get("known_bypass_versions") or []) + list(resolved.get("known_bypass_versions") or [])
        out[sid] = resolved
    return out


def load_library_versions(target_dir: str | Path) -> dict:
    """Read ``targets/<name>/library_versions.json`` if present.

    Shape (best-effort, all keys optional):
      ``{ "<library>": { "version": str, "evidence": str, "confidence": float } }``
    """
    p = Path(target_dir) / "library_versions.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── Version range matching ───────────────────────────────────────────────


_RANGE_RE = re.compile(r"^\s*([<>]=?|=|==|~|\^)?\s*([0-9]+(?:\.[0-9]+){0,2})\s*$")


def _split_version(v: str) -> tuple[int, ...]:
    parts = re.split(r"[.\-+]", v.strip().lstrip("v"))
    out: list[int] = []
    for p in parts:
        if p.isdigit():
            out.append(int(p))
        else:
            break
    return tuple(out) or (0,)


def version_in_range(version: str, expr: str) -> bool:
    """Tiny semver-ish matcher. Supports a single comparator:
       ``<2.4``, ``<=2.4.0``, ``>=3.0.6``, ``=3.1.3``, ``~2.4``, ``^3``.

    Returns False on parse error rather than raising — version data is
    best-effort.
    """
    if not version or not expr:
        return False
    m = _RANGE_RE.match(expr)
    if not m:
        return False
    op = m.group(1) or "="
    rhs = _split_version(m.group(2))
    lhs = _split_version(version)
    # Pad to equal length.
    width = max(len(lhs), len(rhs))
    lhs_p = lhs + (0,) * (width - len(lhs))
    rhs_p = rhs + (0,) * (width - len(rhs))
    if op in ("=", "=="):
        return lhs_p == rhs_p
    if op == "<":
        return lhs_p < rhs_p
    if op == "<=":
        return lhs_p <= rhs_p
    if op == ">":
        return lhs_p > rhs_p
    if op == ">=":
        return lhs_p >= rhs_p
    if op == "~":
        # ~X.Y allows >=X.Y, <X.(Y+1)
        if len(rhs) < 2:
            return lhs_p[0] == rhs_p[0]
        return lhs_p[0] == rhs_p[0] and lhs_p[1] == rhs_p[1] and lhs_p >= rhs_p
    if op == "^":
        return lhs_p[0] == rhs_p[0] and lhs_p >= rhs_p
    return False


# ── Config-flag detection (regex over the snippet around the call) ──────


_OBJECT_KV_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*("
    r"(?:'[^']*'|\"[^\"]*\"|`[^`]*`|true|false|null|\d+(?:\.\d+)?|\[[^\]]*\]|\{[^{}]*\})"
    r")"
)


def _parse_options_object(snippet: str) -> dict[str, str]:
    """Return ``{flag_name: raw_value_string}`` for the first
    ObjectExpression found inside ``snippet``.

    Cheap regex parser — we don't try to be JS-correct, just good
    enough for the common ``sanitize(s, { FLAG: value })`` shape.
    """
    # Capture body of the first `{ ... }` block whose nesting we can
    # follow with a simple counter.
    start = snippet.find("{")
    if start < 0:
        return {}
    depth = 0
    end = -1
    for i in range(start, len(snippet)):
        ch = snippet[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end < 0:
        return {}
    body = snippet[start + 1: end]
    out: dict[str, str] = {}
    for m in _OBJECT_KV_RE.finditer(body):
        out[m.group(1)] = m.group(2).strip()
    return out


def _flag_weakens(flag_value_raw: str, weakens_when: str) -> bool:
    """Best-effort literal-vs-rule comparison.

    The metadata's ``weakens_when`` strings are informal — we read them
    with a tiny vocabulary:
      * ``"true"`` / ``"false"`` → strict equality on JS literal
      * ``"contains 'x'"`` or ``"contains x"`` → substring check
      * ``"contains '*'"`` → wildcard literal
      * ``"contains on*"`` → regex ``on[A-Za-z]+``
      * multiple clauses joined with ``" or "`` → any clause matching
        triggers a downgrade (OR semantics)
      * clauses joined with ``" and "`` → all clauses must match
      * ``"missing common ..."`` → can't evaluate cheaply; return False
    """
    if not flag_value_raw or not weakens_when:
        return False
    w = weakens_when.strip().lower()

    # Multi-clause OR (most common shape in our metadata).
    if " or " in w:
        return any(_flag_weakens(flag_value_raw, sub) for sub in w.split(" or "))
    # Multi-clause AND.
    if " and " in w:
        return all(_flag_weakens(flag_value_raw, sub) for sub in w.split(" and "))

    v = flag_value_raw.strip()
    if w in ("true", "false"):
        return v.lower() == w
    if w.startswith("contains "):
        needle = w[len("contains "):].strip()
        needle_low = needle.lower().strip("'\"")
        if needle_low == "*":
            return "*" in v
        if needle_low == "on*":
            return bool(re.search(r"\b['\"]?on[A-Za-z]+['\"]?", v))
        return needle_low in v.lower()
    if "(empty" in w or "{}" in w:
        return v.strip("()") in ("{}", "[]", "")
    return False


# ── Top-level evaluator ──────────────────────────────────────────────────


def evaluate(
    sanitizer_id: str,
    *,
    call_snippet: str = "",
    target_dir: str | Path | None = None,
    explicit_version: str | None = None,
    base_clears: list[str] | None = None,
    metadata: dict | None = None,
) -> SanitizerVerdict:
    """Score a single sanitizer call.

    Args:
        sanitizer_id:     The taxonomy id (e.g. ``sanitizer_dompurify``).
        call_snippet:     Source code around the call (used to detect
                          config flags). Pass at least the call line
                          plus the next 4 lines; more is fine.
        target_dir:       Target folder. Used to look up
                          ``library_versions.json``.
        explicit_version: If provided, overrides the version detected
                          from ``library_versions.json``.
        base_clears:      The default ``clears`` list from
                          ``sanitizers.json``. We don't try to expand
                          beyond it.

    Returns:
        SanitizerVerdict with confidence and explanatory reasons.
    """
    md = (metadata if metadata is not None else load_metadata()).get(sanitizer_id, {})
    base_clears = list(base_clears or md.get("default_config_clears") or [])
    confidence = 1.0
    reasons: list[str] = []
    flags_observed: dict[str, Any] = {}
    bypass_match: dict | None = None

    # 1) Library version handling.
    library_version: str | None = explicit_version
    if not library_version and target_dir and md.get("library"):
        versions = load_library_versions(target_dir)
        entry = versions.get(md["library"])
        if isinstance(entry, dict):
            library_version = entry.get("version")

    if library_version:
        for bp in md.get("known_bypass_versions") or []:
            rng = bp.get("version_range") or ""
            if version_in_range(library_version, rng):
                downgrade = float(bp.get("downgrade_to", 0.6))
                confidence = min(confidence, downgrade)
                bypass_match = bp
                reasons.append(
                    f"version {library_version} matches known bypass range {rng} "
                    f"({bp.get('bypass', 'unknown bypass')}; downgrade={downgrade})"
                )
                break  # one bypass match is enough

    # 2) Config-flag handling.
    if call_snippet and md.get("config_aware"):
        flags = _parse_options_object(call_snippet)
        for opt in md.get("config_options") or []:
            flag_name = opt.get("flag")
            if not flag_name or flag_name not in flags:
                continue
            flags_observed[flag_name] = flags[flag_name]
            if _flag_weakens(flags[flag_name], opt.get("weakens_when", "")):
                downgrade = float(opt.get("downgrade_to", 0.5))
                confidence = min(confidence, downgrade)
                reasons.append(
                    f"config flag {flag_name}={flags[flag_name]} weakens sanitizer "
                    f"({opt.get('behaviour', '')}; downgrade={downgrade})"
                )

    # 3) Context sensitivity (used for downstream consumer reasoning).
    if md.get("context_sensitivity"):
        reasons.append(
            "sanitizer is context-sensitive: only clears in "
            f"{md['context_sensitivity']}"
        )

    # 4) Policy-body weakness for Trusted Types createHTML.
    if md.get("policy_body_weakness_heuristic") and call_snippet:
        # Look at the createPolicy body if it appears in the snippet.
        if _is_identity_policy(call_snippet):
            confidence = min(confidence, 0.2)
            reasons.append("policy createHTML body appears to be identity / regex-only — fake sanitizer")

    # 5) Regex weakness heuristic (origin checks).
    if md.get("regex_weakness_heuristic") and call_snippet:
        if _is_substring_origin_check(call_snippet):
            confidence = min(confidence, 0.3)
            reasons.append("origin check uses substring/startsWith — bypassable by prefix/suffix origin")

    return SanitizerVerdict(
        sanitizer_id=sanitizer_id,
        confidence=round(confidence, 4),
        clears=base_clears,
        reasons=reasons,
        config_flags_observed=flags_observed,
        library_version=library_version,
        bypass_match=bypass_match,
    )


# ── Sub-heuristics --------------------------------------------------------


_IDENTITY_POLICY_RE = re.compile(
    r"createHTML\s*[:(]\s*\(?\s*([A-Za-z_$][\w$]*)\s*\)?\s*=>\s*\1\b"
)
_IDENTITY_RETURN_RE = re.compile(
    r"createHTML\s*\([^)]*\)\s*\{\s*return\s+[A-Za-z_$][\w$]*\s*;?\s*\}"
)
_SINGLE_REPLACE_RE = re.compile(
    r"createHTML\b[^{}]*\breturn\s+[A-Za-z_$][\w$]*\.replace\s*\([^)]*\)\s*;?\s*\}",
    re.DOTALL,
)


def _is_identity_policy(snippet: str) -> bool:
    return bool(
        _IDENTITY_POLICY_RE.search(snippet)
        or _IDENTITY_RETURN_RE.search(snippet)
        or _SINGLE_REPLACE_RE.search(snippet)
    )


_SUBSTR_ORIGIN_RE = re.compile(
    r"\b(origin|e\.origin|event\.origin|msg\.origin|message\.origin|ev\.origin)\s*\.(startsWith|endsWith|includes|indexOf)\s*\(",
)


def _is_substring_origin_check(snippet: str) -> bool:
    return bool(_SUBSTR_ORIGIN_RE.search(snippet))
