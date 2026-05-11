"""Caveman output compression — inline implementation, no external dep."""
from __future__ import annotations

import re

import structlog

_VALID_MODES = frozenset({"on", "off", "lite", "full", "ultra"})

_logger = structlog.get_logger(__name__)

_FILLER_PHRASES = re.compile(
    r"\b(just|basically|essentially|simply|really|very|quite|rather|somewhat|"
    r"i would say|it is worth noting|it is important to note|"
    r"feel free to|don't hesitate to|hope this helps|"
    r"let me know if|happy to help|certainly|of course|sure[,!]?)\b",
    re.IGNORECASE,
)

_ARTICLES = re.compile(r"\b(a |an |the )", re.IGNORECASE)


def compress(text: str, mode: str = "lite") -> str:
    if mode not in _VALID_MODES:
        raise ValueError(
            f"invalid caveman mode: {mode!r}. Must be one of {_VALID_MODES}"
        )
    if mode == "off":
        return text
    out = _FILLER_PHRASES.sub("", text)
    if mode in {"on", "full", "ultra"}:
        out = _ARTICLES.sub("", out)
    out = re.sub(r"  +", " ", out)
    return out.strip()


def maybe_compress(text: str, mode: str) -> str:
    """Best-effort compress: invalid mode falls back to 'lite', errors swallowed."""
    if not text:
        return text
    effective = mode if mode in _VALID_MODES else "lite"
    if effective != mode:
        _logger.warning("caveman_compress_invalid_mode", mode=mode)
    try:
        return compress(text, effective)
    except Exception as e:
        _logger.warning("caveman_compress_failed", error=str(e), mode=effective)
        return text
