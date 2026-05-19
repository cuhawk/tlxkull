"""Regression tests for two FP-rate bugs in reporter.py.

BUG-1: sanitisers_in_path entries did not carry a per-instance
``confidence`` value. ``extract_findings`` defaulted to 1.0, which
flowed into ``compute_partial`` as ``(1 - 1.0) = 0`` and zeroed out
P(chain) for every chain that touched any sanitizer.

BUG-2: the taxonomy id → bypass-corpus library mapping was a naive
``replace("_", "-")``, which dropped the bypass entries for
``sanitizer_dompurify_namespaced`` and ``sanitizer_xss_lib``.
"""
from modules.js_analyzer.reporter import (
    _SANITIZER_DEFAULT_CONFIDENCE,
    _SANITIZER_NOMINAL_CONFIDENCE,
    _TAXONOMY_TO_BYPASS_LIB,
    _bypass_corpus_for_chains,
    _resolve_sanitizer_confidence,
)


# ── BUG-1 ────────────────────────────────────────────────────────────────


def test_resolve_sanitizer_confidence_prefers_explicit_value():
    entry = {"taxonomy_id": "sanitizer_dompurify", "confidence": 0.4}
    assert _resolve_sanitizer_confidence(entry) == 0.4


def test_resolve_sanitizer_confidence_clamps_explicit_value():
    assert _resolve_sanitizer_confidence({"confidence": 1.5}) == 1.0
    assert _resolve_sanitizer_confidence({"confidence": -0.3}) == 0.0


def test_resolve_sanitizer_confidence_uses_taxonomy_table():
    entry = {"taxonomy_id": "sanitizer_dompurify"}
    assert _resolve_sanitizer_confidence(entry) == _SANITIZER_NOMINAL_CONFIDENCE[
        "sanitizer_dompurify"
    ]


def test_resolve_sanitizer_confidence_falls_back_to_partial_default():
    entry = {"taxonomy_id": "sanitizer_made_up_thing"}
    assert _resolve_sanitizer_confidence(entry) == _SANITIZER_DEFAULT_CONFIDENCE


def test_resolve_sanitizer_confidence_never_silently_returns_one():
    """Empty / malformed entries must NOT default to 1.0, otherwise the
    chain-confidence aggregator collapses every sanitized chain to 0.
    """
    assert _resolve_sanitizer_confidence({}) < 1.0
    assert _resolve_sanitizer_confidence({"taxonomy_id": None}) < 1.0
    assert _resolve_sanitizer_confidence({"confidence": None}) < 1.0


# ── BUG-2 ────────────────────────────────────────────────────────────────


def test_bypass_corpus_picks_up_namespaced_dompurify():
    chains = [{
        "sanitisers_in_path": [
            {"taxonomy_id": "sanitizer_dompurify_namespaced"}
        ]
    }]
    out = _bypass_corpus_for_chains(chains)
    assert out, "expected bypass entries for window.DOMPurify"
    assert all(b["library"] == "dompurify" for b in out)


def test_bypass_corpus_picks_up_xss_lib_taxonomy():
    chains = [{
        "sanitisers_in_path": [
            {"taxonomy_id": "sanitizer_xss_lib"}
        ]
    }]
    out = _bypass_corpus_for_chains(chains)
    assert out, "expected bypass entries for leizongmin/xss"
    assert all(b["library"] == "xss" for b in out)


def test_bypass_corpus_still_picks_up_plain_dompurify():
    chains = [{
        "sanitisers_in_path": [
            {"taxonomy_id": "sanitizer_dompurify"}
        ]
    }]
    out = _bypass_corpus_for_chains(chains)
    assert out and all(b["library"] == "dompurify" for b in out)


def test_bypass_corpus_skips_chains_without_known_sanitizer():
    chains = [{
        "sanitisers_in_path": [
            {"taxonomy_id": "sanitizer_textContent_assign"}
        ]
    }]
    assert _bypass_corpus_for_chains(chains) == []


def test_taxonomy_to_bypass_lib_table_covers_known_libraries():
    """Every library that has a bypass entry in the corpus must be
    reachable from at least one taxonomy id; otherwise the mapping
    table silently drops the bypass on the floor.
    """
    from modules.js_analyzer.sanitizer_bypass_corpus import ALL_BYPASSES
    corpus_libs = {b.library for b in ALL_BYPASSES}
    mapped_libs = set(_TAXONOMY_TO_BYPASS_LIB.values())
    missing = corpus_libs - mapped_libs
    assert not missing, (
        f"bypass libraries with no taxonomy mapping: {sorted(missing)}"
    )
