"""Corpus post-confirmation hook.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §19.2b + §19.8.

When a chain is confirmed as a true positive (e.g. by ``browser-confirm``
or analyst sign-off via ``report-finding``), we want to add it to the
local corpus so future scans pattern-match against the same shape.

This module exposes one public entry point:

  record_confirmation(chain, target_dir) — derive a Fingerprint from
  *chain*, persist as ``corpus/fingerprints/fp_<id>.json``, and append
  provenance metadata so re-confirming the same chain on a different
  target bumps the provenance count without duplicating the fingerprint.

Decay (§19.8) is applied passively: fingerprints whose provenance
list grows over time get a small weight boost (cap 0.95); fingerprints
older than ``DECAY_AFTER_DAYS`` without new provenance entries are
linearly downweighted to a floor of 0.30.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from modules.js_analyzer.corpus import (  # noqa: E402
    FINGERPRINT_DIR,
    Fingerprint,
    add_fingerprint,
    load_fingerprints,
)


__all__ = [
    "record_confirmation",
    "decay_corpus_weights",
    "FINGERPRINT_DIR",
]


DECAY_AFTER_DAYS = 180
DECAY_FLOOR = 0.30


# ---------------------------------------------------------------------------
# Fingerprint synthesis
# ---------------------------------------------------------------------------


def _hash_id(source_kind: str, sink_kind: str, framework: str | None) -> str:
    parts = [source_kind, sink_kind, framework or ""]
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{source_kind}__{sink_kind}__{h}"


def _derive_fingerprint(chain: dict, frameworks: list[str]) -> Fingerprint:
    src_kind = (chain.get("source") or {}).get("taxonomy_id") \
        or (chain.get("source") or {}).get("kind", "unknown")
    sink_kind = (chain.get("sink") or {}).get("taxonomy_id") \
        or (chain.get("sink") or {}).get("kind", "unknown")
    fw = next((f.lower() for f in frameworks or ()), None)
    path_len = int(chain.get("depth", len(chain.get("path") or [])) or 0)
    # Confidence shapes the seed weight; higher chain score → higher
    # seed weight, capped at 0.85 so post-confirm fingerprints never
    # outweigh hand-curated archetypes.
    score = float(chain.get("score") or 0.0) / 100.0
    weight = round(min(0.85, 0.5 + 0.35 * score), 3)
    fp = Fingerprint(
        id=_hash_id(src_kind, sink_kind, fw),
        source_kinds=(src_kind,),
        sink_kinds=(sink_kind,),
        required_path_features=({"kind": "no_sanitizer_on_path"},)
            if not chain.get("sanitized") else (),
        forbidden_features=(),
        framework_any_of=tuple(f.lower() for f in (frameworks or ())),
        min_path_length=max(1, path_len - 2),
        max_path_length=path_len + 4,
        archetype_md="",
        weight=weight,
        provenance_count=0,
    )
    return fp


def _provenance_entry(chain: dict, target_name: str) -> dict:
    src = chain.get("source") or {}
    sink = chain.get("sink") or {}
    return {
        "target": target_name,
        "chain_id": chain.get("id") or chain.get("chain_id"),
        "source": f"{src.get('qname')}@{src.get('file')}:{src.get('line')}",
        "sink": f"{sink.get('qname')}@{sink.get('file')}:{sink.get('line')}",
        "score": chain.get("score"),
        "p_chain": chain.get("p_chain"),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def record_confirmation(
    chain: dict,
    target_dir: Path | str,
    *,
    frameworks: list[str] | None = None,
    fingerprint_dir: Path | None = None,
) -> Path:
    """Persist or update the fingerprint corresponding to *chain*.

    Returns the path of the on-disk JSON. Idempotent: re-recording the
    same target/chain pair appends to ``provenance`` rather than
    duplicating the row.
    """
    fpdir = fingerprint_dir or FINGERPRINT_DIR
    fpdir.mkdir(parents=True, exist_ok=True)

    frameworks = frameworks or []
    fp = _derive_fingerprint(chain, frameworks)
    out = fpdir / f"fp_{fp.id}.json"
    existing: dict
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    else:
        existing = {}

    payload: dict = {
        "id": fp.id,
        "source_kinds": list(fp.source_kinds),
        "sink_kinds": list(fp.sink_kinds),
        "required_path_features": list(fp.required_path_features),
        "forbidden_features": list(fp.forbidden_features),
        "framework_any_of": list(fp.framework_any_of),
        "min_path_length": int(fp.min_path_length),
        "max_path_length": int(fp.max_path_length),
        "archetype_md": existing.get("archetype_md", ""),
        "weight": max(fp.weight, float(existing.get("weight") or fp.weight)),
        "provenance": list(existing.get("provenance") or []),
    }
    target_name = Path(target_dir).name
    entry = _provenance_entry(chain, target_name)
    if not any(
        p.get("target") == entry["target"]
        and p.get("chain_id") == entry["chain_id"]
        for p in payload["provenance"]
    ):
        payload["provenance"].append(entry)
        # Provenance bump: +0.03 per new entry, capped 0.95.
        payload["weight"] = round(min(0.95, payload["weight"] + 0.03), 3)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    # Invalidate the load_fingerprints cache.
    load_fingerprints.cache_clear()
    return out


# ---------------------------------------------------------------------------
# Decay
# ---------------------------------------------------------------------------


def decay_corpus_weights(
    fingerprint_dir: Path | None = None,
    *,
    now: float | None = None,
    after_days: int = DECAY_AFTER_DAYS,
    floor: float = DECAY_FLOOR,
) -> dict:
    """Walk every fingerprint and downweight the ones whose most recent
    provenance entry is older than ``after_days``. Hand-curated archetypes
    (provenance empty AND archetype_md set) are exempt.

    Returns ``{path: (old_weight, new_weight)}`` for each adjusted file.
    """
    fpdir = fingerprint_dir or FINGERPRINT_DIR
    if not fpdir.exists():
        return {}
    now = now or time.time()
    changes: dict[str, tuple[float, float]] = {}
    for f in sorted(fpdir.glob("fp_*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        prov = data.get("provenance") or []
        archetype_md = data.get("archetype_md") or ""
        if not prov and archetype_md:
            continue
        last = 0.0
        for p in prov:
            ts = p.get("recorded_at")
            if not ts:
                continue
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except ValueError:
                continue
            last = max(last, t)
        if not last:
            continue
        age_days = (now - last) / 86400
        if age_days < after_days:
            continue
        old_weight = float(data.get("weight", 0.5))
        # Linear decay: weight loses 0.02 per 30 days beyond threshold.
        excess = (age_days - after_days) / 30.0
        new_weight = max(floor, round(old_weight - 0.02 * excess, 3))
        if new_weight < old_weight:
            data["weight"] = new_weight
            f.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
            changes[str(f)] = (old_weight, new_weight)
    if changes:
        load_fingerprints.cache_clear()
    return changes
