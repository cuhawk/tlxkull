"""Response normalisation + body-parity diff for IDOR/BAC classification.

Pure-Python, no I/O. Consumed by ``idor_sweep.py`` to decide whether a
variant response indicates an authorization gap.

Classification taxonomy (returned by ``classify_variant``):

- ``idor_candidate``     — variant returned ≥ ``parity_threshold`` of
                           baseline body after normalization AND status
                           class is 2xx. This is the IDOR signal.
- ``bac_candidate``      — variant returned ≥ ``parity_threshold`` of
                           baseline AND auth was *removed* from the
                           variant. The "no-auth" version of IDOR.
- ``leak_partial``       — body parity in 0.4..parity_threshold, but
                           variant contains PII regexes (email/phone/
                           credit-card patterns) not present in a
                           4xx/5xx baseline.
- ``access_denied``      — variant 4xx/5xx while baseline 2xx (expected
                           defense).
- ``error_match``        — both error-class. Boring.
- ``noisy``              — status/body diverge but not in a way that
                           looks like a leak.

The diff intentionally normalizes (drops) per-request volatility
(timestamps, request-ids, csrf tokens, ETags, dates, signed urls) so
two valid responses for the same logical resource don't trip the
parity threshold downward.

Tuning knobs:

- ``parity_threshold`` (default 0.8) — SequenceMatcher ratio above
  which two normalized bodies are treated as "same data".
- ``ignore_regexes`` — list of compiled patterns whose matches are
  redacted before diffing. Defaults cover the common volatility list;
  callers can add per-target overrides.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any, Iterable


__all__ = [
    "DEFAULT_IGNORE_REGEXES",
    "PII_REGEXES",
    "DiffResult",
    "VariantClassification",
    "normalize_body",
    "body_parity",
    "diff_response",
    "classify_variant",
]


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

DEFAULT_IGNORE_REGEXES: list[re.Pattern[str]] = [
    # ISO-8601 timestamps and unix epochs.
    re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?"),
    re.compile(r"\b1[5-9]\d{8}\b"),  # 10-digit epoch seconds
    re.compile(r"\b1[5-9]\d{11}\b"), # 13-digit epoch ms
    # UUIDs and request ids.
    re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
               r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"),
    re.compile(r'"(?:request[-_]?id|trace[-_]?id|correlation[-_]?id|'
               r"etag|nonce|csrf[-_]?token|x[-_]?csrf[-_]?token)"
               r'"\s*:\s*"[^"]*"',
               re.IGNORECASE),
    # Signed-URL signature params (s3, gcs, cloudfront).
    re.compile(r"(?:X-Amz-Signature|Signature|sig|hmac)=[A-Za-z0-9%_+\-/=.]+",
               re.IGNORECASE),
    # base64-shaped opaque tokens of 24+ chars.
    re.compile(r'"(?:cursor|next_?token|page_?token|continuation)"\s*:\s*'
               r'"[A-Za-z0-9+/=_-]{12,}"',
               re.IGNORECASE),
]


PII_REGEXES: list[re.Pattern[str]] = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),  # candidate credit-card (loose; Luhn check below)
    re.compile(r'"(?:ssn|social[_-]?security)"\s*:\s*"[\d-]+"', re.IGNORECASE),
]


def normalize_body(
    body: str | bytes | None,
    ignore_regexes: Iterable[re.Pattern[str]] = (),
    pretty_json: bool = True,
) -> str:
    """Return a normalized string suitable for diffing.

    - Bytes are decoded as UTF-8 (errors='replace').
    - JSON bodies are re-serialized with sorted keys + indent for
      stable diffing.
    - Each regex in ``ignore_regexes`` (plus the defaults) is replaced
      with a placeholder so per-request volatility doesn't lower
      parity.
    """
    if body is None:
        return ""
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    if not isinstance(body, str):
        body = str(body)
    text = body.strip()

    if pretty_json and text and text[0] in "[{":
        try:
            obj = json.loads(text)
            text = json.dumps(obj, sort_keys=True, indent=2, default=str)
        except (ValueError, TypeError):
            pass

    for pat in DEFAULT_IGNORE_REGEXES:
        text = pat.sub("<REDACTED>", text)
    for pat in ignore_regexes:
        text = pat.sub("<REDACTED>", text)
    return text


def body_parity(
    baseline: str | bytes | None,
    variant: str | bytes | None,
    ignore_regexes: Iterable[re.Pattern[str]] = (),
) -> float:
    """Return SequenceMatcher ratio of normalized bodies (0.0..1.0)."""
    a = normalize_body(baseline, ignore_regexes)
    b = normalize_body(variant, ignore_regexes)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


# ---------------------------------------------------------------------------
# PII / leak detection
# ---------------------------------------------------------------------------

def _luhn_valid(num_str: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", num_str)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def pii_hits(text: str) -> list[str]:
    """Return short labels of PII patterns found in ``text``.

    Credit-card candidates are validated via Luhn to drop false hits
    on random numeric runs.
    """
    if not text:
        return []
    hits: list[str] = []
    if PII_REGEXES[0].search(text):
        hits.append("email")
    if PII_REGEXES[1].search(text):
        hits.append("phone")
    cc_candidates = PII_REGEXES[2].findall(text)
    if any(_luhn_valid(c) for c in cc_candidates):
        hits.append("credit_card")
    if PII_REGEXES[3].search(text):
        hits.append("ssn")
    return hits


# ---------------------------------------------------------------------------
# Diff + classification
# ---------------------------------------------------------------------------

@dataclass
class DiffResult:
    parity: float
    baseline_status: int
    variant_status: int
    baseline_len: int
    variant_len: int
    pii: list[str] = field(default_factory=list)


def diff_response(
    baseline: dict,
    variant: dict,
    ignore_regexes: Iterable[re.Pattern[str]] = (),
) -> DiffResult:
    """Return a structured diff of two HTTP responses.

    Each response dict expects ``{"status": int, "body": str|bytes}``.
    Extra keys (headers, timings) are ignored here.
    """
    a = baseline.get("body") or ""
    b = variant.get("body") or ""
    return DiffResult(
        parity=body_parity(a, b, ignore_regexes),
        baseline_status=int(baseline.get("status", 0)),
        variant_status=int(variant.get("status", 0)),
        baseline_len=len(a if isinstance(a, (str, bytes)) else str(a)),
        variant_len=len(b if isinstance(b, (str, bytes)) else str(b)),
        pii=pii_hits(
            normalize_body(b)
            if not isinstance(b, dict)
            else json.dumps(b, default=str)
        ),
    )


@dataclass
class VariantClassification:
    category: str         # see module docstring
    confidence: float     # 0..1
    rationale: str
    diff: DiffResult


def _is_2xx(status: int) -> bool:
    return 200 <= status < 300


def _is_error(status: int) -> bool:
    return status == 0 or status >= 400


def classify_variant(
    baseline: dict,
    variant: dict,
    *,
    variant_name: str = "",
    auth_dropped: bool = False,
    parity_threshold: float = 0.8,
    ignore_regexes: Iterable[re.Pattern[str]] = (),
) -> VariantClassification:
    """Apply the IDOR / BAC taxonomy.

    ``auth_dropped`` should be True for variants that removed all auth
    headers (no-auth probe). The classifier elevates parity matches in
    that case to ``bac_candidate``.
    """
    diff = diff_response(baseline, variant, ignore_regexes)
    bs, vs = diff.baseline_status, diff.variant_status

    if _is_2xx(bs) and _is_error(vs):
        return VariantClassification(
            category="access_denied",
            confidence=0.9,
            rationale=f"baseline 2xx → variant {vs} (defense in place)",
            diff=diff,
        )

    if _is_error(bs) and _is_error(vs):
        return VariantClassification(
            category="error_match",
            confidence=0.6,
            rationale=f"both error class ({bs}/{vs})",
            diff=diff,
        )

    if diff.parity >= parity_threshold and _is_2xx(vs) and _is_2xx(bs):
        if auth_dropped:
            return VariantClassification(
                category="bac_candidate",
                confidence=min(0.99, 0.5 + diff.parity / 2),
                rationale=(
                    f"unauthenticated variant ({variant_name}) returned "
                    f"{diff.parity:.2f} parity body — broken access control"
                ),
                diff=diff,
            )
        return VariantClassification(
            category="idor_candidate",
            confidence=min(0.99, 0.5 + diff.parity / 2),
            rationale=(
                f"swapped identity variant ({variant_name}) returned "
                f"{diff.parity:.2f} parity body — IDOR"
            ),
            diff=diff,
        )

    if 0.4 <= diff.parity < parity_threshold and _is_2xx(vs) and diff.pii:
        return VariantClassification(
            category="leak_partial",
            confidence=0.6 + 0.1 * len(diff.pii),
            rationale=(
                f"partial body match ({diff.parity:.2f}) with PII fields "
                f"present: {','.join(diff.pii)}"
            ),
            diff=diff,
        )

    if _is_2xx(vs) and not _is_2xx(bs):
        return VariantClassification(
            category="noisy",
            confidence=0.3,
            rationale=(
                f"variant returned {vs} while baseline {bs} — unusual "
                "but may indicate hidden default route"
            ),
            diff=diff,
        )

    return VariantClassification(
        category="noisy",
        confidence=0.1,
        rationale=(
            f"no auth-bypass signal (parity {diff.parity:.2f}, "
            f"{bs}→{vs})"
        ),
        diff=diff,
    )
