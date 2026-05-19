"""Chain confidence — P(chain) computation for best-first traversal.

Plan: plans/ARCHITECTURE_EVOLUTION.md §8.

Multiplicative model:

  P(chain) = P_source × Π P_edge × Π (1 - P_sanitizer) × P_viability
             × P_async_discount × P_dynamic_discount

The result is calibrated against a logistic fit in
``targets/_calibration/confidence_model.json`` (when present) to map raw
probability into P(true_positive). Without the calibration file, the
raw probability is returned.

This module is consumed by ``bin/extract_chains_bestfirst.py`` to drive
heap-ordered traversal, and (later) by ``reporter.py`` for sort order.

Pure function — no IO beyond an optional one-shot read of the
calibration file.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

__all__ = [
    "ChainConfidence",
    "edge_confidence",
    "source_controllability",
    "compute_partial",
    "calibrate",
    "load_calibration",
]


_CALIB_PATH = Path(__file__).resolve().parents[3] / "targets" / "_calibration" / "confidence_model.json"


@dataclass
class ChainConfidence:
    p_source: float
    p_edges: float
    p_unsanitized: float
    p_viability: float
    p_async: float
    p_dynamic: float
    p_raw: float
    p_calibrated: float | None
    breakdown: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "p_source": round(self.p_source, 4),
            "p_edges": round(self.p_edges, 4),
            "p_unsanitized": round(self.p_unsanitized, 4),
            "p_viability": round(self.p_viability, 4),
            "p_async": round(self.p_async, 4),
            "p_dynamic": round(self.p_dynamic, 4),
            "p_raw": round(self.p_raw, 4),
            "p_calibrated": round(self.p_calibrated, 4) if self.p_calibrated is not None else None,
            "breakdown": self.breakdown,
        }


# ── Source controllability ───────────────────────────────────────────────


_SOURCE_CONTROL: dict[str, float] = {
    # DOM — fully attacker-controlled in the URL
    "location_hash":         0.98,
    "location_search":       0.98,
    "URLSearchParams_ctor":  0.95,
    "URLSearchParams_get":   0.95,
    "location_href_read":    0.90,
    "location_pathname":     0.85,
    "document_URL":          0.85,
    "document_referrer":     0.60,
    # postMessage / WebSocket / continuation — attacker-controlled iff origin check missing
    "dom_message":              0.85,
    "onmessage_handler":        0.85,
    "message_event_listener":   0.85,
    "continuation_message_data":     0.80,
    "continuation_websocket_data":   0.75,
    "continuation_event_target_value": 0.55,
    "continuation_mutation_target":  0.50,
    "continuation_observable_emit":  0.50,
    "continuation_promise_resolved": 0.50,
    "continuation_promise_rejected": 0.40,
    "continuation_fetch_body":       0.60,
    # storage — second-order; attacker needs separate write
    "localStorage_get":      0.50,
    "localStorage_bracket":  0.50,
    "sessionStorage_get":    0.50,
    "document_cookie":       0.45,
    # parsed JSON / responses
    "JSON_parse_call":       0.55,
    "xhr_responseText":      0.55,
    # prototype-pollution sources
    "proto_assign_merge":    0.70,
    "proto_assign_bracket":  0.70,
    "proto_assign_assign":   0.70,
    # SvelteKit / Next params
    "sveltekit_params":      0.85,
}


def source_controllability(taxonomy_id: str, tag_confidence: float = 1.0) -> float:
    """Return P(attacker controls this source) ∈ (0, 1]."""
    base = _SOURCE_CONTROL.get(taxonomy_id, 0.35)
    return max(0.02, min(1.0, base * tag_confidence))


# ── Edge confidence ──────────────────────────────────────────────────────


_EDGE_CONF: dict[str, float] = {
    "exact":            1.00,
    "this_cross_file":  0.95,
    "name_match":       0.80,   # may be downgraded by candidate_count
    "prop_shape":       0.70,   # set by future §2 work
    "continuation":     0.85,
    "runtime_observed": 1.00,
    "dynamic":          0.30,
    "dynamic_overapprox": 0.20,
    "unresolved":       0.10,
}


def edge_confidence(resolved_kind: str, candidate_count: int | None = None) -> float:
    base = _EDGE_CONF.get(resolved_kind or "", 0.50)
    if resolved_kind == "name_match" and candidate_count and candidate_count > 1:
        base *= 1.0 / math.sqrt(candidate_count)
    return max(0.02, min(1.0, base))


# ── Sanitizer probability ────────────────────────────────────────────────


def sanitizer_block_p(sanitizer_confidence: float | None) -> float:
    """Convert sanitizer effective-confidence into a P(blocks chain).

    A 1.0-confident sanitizer blocks with 1.0; a 0.4-confident one
    (partial / version-bypassable) blocks with 0.4.
    """
    if sanitizer_confidence is None:
        return 0.0
    return max(0.0, min(1.0, float(sanitizer_confidence)))


# ── Main aggregator ──────────────────────────────────────────────────────


def compute_partial(
    *,
    source_taxonomy_id: str,
    source_tag_confidence: float = 1.0,
    edge_kinds: Iterable[tuple[str, int | None]] = (),
    sanitizer_confidences: Iterable[float] = (),
    viability_factor: float = 1.0,
    continuation_hops: int = 0,
    dynamic_hops: int = 0,
) -> ChainConfidence:
    """Compute P(chain) for the candidate path described by the args.

    ``edge_kinds``: iterable of (resolved_kind, candidate_count) per hop.
    ``sanitizer_confidences``: per-sanitizer effective confidence.
    """
    p_src = source_controllability(source_taxonomy_id, source_tag_confidence)
    p_edges = 1.0
    edge_records = []
    for rk, cc in edge_kinds:
        e = edge_confidence(rk, cc)
        p_edges *= e
        edge_records.append({"resolved_kind": rk, "candidate_count": cc, "confidence": round(e, 4)})

    p_unsan = 1.0
    san_records = []
    for sc in sanitizer_confidences:
        block = sanitizer_block_p(sc)
        p_unsan *= (1.0 - block)
        san_records.append({"sanitizer_confidence": sc, "block_p": round(block, 4)})

    p_viab = max(0.02, min(1.0, viability_factor))
    p_async = 0.95 ** max(0, continuation_hops)
    p_dyn = 0.90 ** max(0, dynamic_hops)
    raw = p_src * p_edges * p_unsan * p_viab * p_async * p_dyn

    calib = load_calibration()
    p_cal = calibrate(raw, calib) if calib else None

    return ChainConfidence(
        p_source=p_src,
        p_edges=p_edges,
        p_unsanitized=p_unsan,
        p_viability=p_viab,
        p_async=p_async,
        p_dynamic=p_dyn,
        p_raw=raw,
        p_calibrated=p_cal,
        breakdown=[
            {"stage": "source", "p": round(p_src, 4)},
            {"stage": "edges", "p": round(p_edges, 4), "hops": edge_records},
            {"stage": "sanitizer", "p": round(p_unsan, 4), "items": san_records},
            {"stage": "viability", "p": round(p_viab, 4)},
            {"stage": "async_discount", "p": round(p_async, 4), "hops": continuation_hops},
            {"stage": "dynamic_discount", "p": round(p_dyn, 4), "hops": dynamic_hops},
        ],
    )


# ── Calibration ──────────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def load_calibration(path: str | None = None) -> dict | None:
    """Load a logistic-fit calibration written by
    ``bin/calibrate_confidence.py``.

    Expected shape:
      ``{"coef": float, "intercept": float, "fit_n": int, "fit_at": iso8601}``

    Returns ``None`` when absent — caller treats raw P(chain) as
    P(true_positive).
    """
    p = Path(path) if path else _CALIB_PATH
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def calibrate(p_raw: float, model: dict | None = None) -> float:
    """Apply a logistic transform: 1 / (1 + exp(-(a*p_raw + b))).

    Falls back to raw when no model is provided.
    """
    if not model:
        return p_raw
    a = float(model.get("coef", 1.0))
    b = float(model.get("intercept", 0.0))
    z = a * p_raw + b
    try:
        return 1.0 / (1.0 + math.exp(-z))
    except OverflowError:
        return 0.0 if z < 0 else 1.0


# ── Adaptive depth ───────────────────────────────────────────────────────


def adaptive_depth(p_partial: float, *, min_depth: int = 3, max_depth: int = 12) -> int:
    """Return the depth budget for a frontier with partial probability
    ``p_partial``. Lower-probability frontiers get shorter budgets so the
    queue is not blown by long shots.
    """
    if p_partial <= 0:
        return min_depth
    raw = 20 - 10 * math.log(1.0 / p_partial)
    return max(min_depth, min(max_depth, int(round(raw))))
