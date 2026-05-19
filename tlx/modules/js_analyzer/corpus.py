"""Corpus-guided pattern intelligence.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §19.

Curated, hand-maintained fingerprints of historically-exploitable
chain shapes. NOT machine-learned. Lives on disk under
``corpus/fingerprints/*.json`` and is loaded once per process.

Usage::

    from modules.js_analyzer.corpus import match

    for fp, score in match(chain):
        chain.setdefault("fingerprint_matches", []).append({
            "id":         fp.id,
            "score":      score,
            "archetype":  fp.archetype_md,
        })

Behind ``ENABLE_CORPUS_PATTERNS``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

__all__ = [
    "Fingerprint",
    "load_fingerprints",
    "match",
    "add_fingerprint",
    "FINGERPRINT_DIR",
]


FINGERPRINT_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "corpus" / "fingerprints"
)


@dataclass(frozen=True)
class Fingerprint:
    id: str
    source_kinds:        tuple[str, ...]
    sink_kinds:          tuple[str, ...]
    required_path_features: tuple[dict, ...] = field(default_factory=tuple)
    forbidden_features:  tuple[dict, ...] = field(default_factory=tuple)
    framework_any_of:    tuple[str, ...]   = field(default_factory=tuple)
    min_path_length:     int = 1
    max_path_length:     int = 12
    archetype_md:        str = ""
    weight:              float = 0.5
    provenance_count:    int = 0


@lru_cache(maxsize=1)
def load_fingerprints(path: str | None = None) -> tuple[Fingerprint, ...]:
    p = Path(path) if path else FINGERPRINT_DIR
    if not p.exists():
        return ()
    out: list[Fingerprint] = []
    for f in sorted(p.glob("fp_*.json")):
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        out.append(Fingerprint(
            id                     = raw.get("id") or f.stem,
            source_kinds           = tuple(raw.get("source_kinds", ())),
            sink_kinds             = tuple(raw.get("sink_kinds", ())),
            required_path_features = tuple(raw.get("required_path_features", ())),
            forbidden_features     = tuple(raw.get("forbidden_features", ())),
            framework_any_of       = tuple(raw.get("framework_any_of", ())),
            min_path_length        = int(raw.get("min_path_length", 1)),
            max_path_length        = int(raw.get("max_path_length", 12)),
            archetype_md           = raw.get("archetype_md", ""),
            weight                 = float(raw.get("weight", 0.5)),
            provenance_count       = len(raw.get("provenance", ()) or ()),
        ))
    return tuple(out)


def _has_feature(chain: dict, feature: dict) -> bool:
    """Generic predicate: feature dict either matches a chain top-level
    key/value pair or matches any hop on the chain's path."""
    if not feature:
        return True
    kind = feature.get("kind")
    value = feature.get("value")
    # Top-level scalar feature.
    if kind in chain and (value is None or chain[kind] == value):
        return True
    # Per-hop boolean feature.
    if kind == "no_sanitizer_on_path":
        return not chain.get("sanitized", False)
    if kind == "trusted_types_required":
        for hop in chain.get("path", []):
            if hop.get("trusted_types_required"):
                return True
        return False
    # Path scan for matching key/value.
    for hop in chain.get("path", []):
        if value is None and hop.get(kind):
            return True
        if value is not None and hop.get(kind) == value:
            return True
    return False


def _score(chain: dict, fp: Fingerprint, framework_set: set[str]) -> float:
    if chain.get("source", {}).get("kind") not in fp.source_kinds:
        if fp.source_kinds:
            return 0.0
    if chain.get("sink", {}).get("kind") not in fp.sink_kinds:
        if fp.sink_kinds:
            return 0.0
    path_len = len(chain.get("path", []))
    if path_len < fp.min_path_length or path_len > fp.max_path_length:
        return 0.0
    if fp.framework_any_of and not (framework_set & set(fp.framework_any_of)):
        # Reduce, don't drop, if framework set isn't fully known.
        framework_match = 0.5 if not framework_set else 0.0
        if framework_match == 0.0:
            return 0.0
    else:
        framework_match = 1.0
    # Required features.
    total_req = len(fp.required_path_features)
    missing = sum(
        0 if _has_feature(chain, feat) else 1
        for feat in fp.required_path_features
    )
    if total_req and missing:
        ratio = 1 - (missing / total_req)
    else:
        ratio = 1.0
    # Forbidden features drop the chain entirely.
    for feat in fp.forbidden_features:
        if _has_feature(chain, feat):
            return 0.0
    return round(ratio * framework_match * fp.weight, 4)


def match(
    chain: dict,
    *,
    framework_set: Iterable[str] = (),
    fingerprints: Iterable[Fingerprint] | None = None,
    min_score: float = 0.5,
) -> list[tuple[Fingerprint, float]]:
    """Return matching fingerprints with score ≥ ``min_score``, sorted
    descending. Top-3 results are typically all the LLM prompt wants.
    """
    fps = tuple(fingerprints) if fingerprints is not None else load_fingerprints()
    fwset = set(framework_set)
    results: list[tuple[Fingerprint, float]] = []
    for fp in fps:
        s = _score(chain, fp, fwset)
        if s >= min_score:
            results.append((fp, s))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def add_fingerprint(fp: Fingerprint, *, dir_path: Path | None = None) -> Path:
    """Persist a new fingerprint (for the post-confirmation hook)."""
    target_dir = dir_path or FINGERPRINT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / f"{fp.id}.json"
    out.write_text(json.dumps({
        "id":                      fp.id,
        "source_kinds":            list(fp.source_kinds),
        "sink_kinds":              list(fp.sink_kinds),
        "required_path_features":  list(fp.required_path_features),
        "forbidden_features":      list(fp.forbidden_features),
        "framework_any_of":        list(fp.framework_any_of),
        "min_path_length":         fp.min_path_length,
        "max_path_length":         fp.max_path_length,
        "archetype_md":            fp.archetype_md,
        "weight":                  fp.weight,
        "provenance":              [],
    }, indent=2), encoding="utf-8")
    load_fingerprints.cache_clear()
    return out
