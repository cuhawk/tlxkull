"""V2 §19 — Corpus-guided pattern intelligence.

Score every chain against a tiny curated archetype catalog. Designed
to be extended over time as confirmed findings get fingerprinted via
``report-finding``.

Off by default; ``JS_ENABLE_CORPUS_PATTERNS=1`` to enable.

Output:
- in-memory ``fingerprint_matches[]`` per chain
- sidecar ``corpus_matches.json`` summarizing breakdown
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "Archetype",
    "ARCHETYPES",
    "match_chain",
    "match_corpus",
]


@dataclass(frozen=True)
class Archetype:
    id: str
    source_kinds: tuple[str, ...]
    sink_kinds: tuple[str, ...]
    framework: str | None = None
    sanitizer_required_absent: bool = False
    notes: str = ""


# Starter corpus. Expand by appending Archetype entries here (no DB / no
# external file dependency — keep this curated by hand).
ARCHETYPES: tuple[Archetype, ...] = (
    Archetype(
        id="fp_dom_xss_hash_innerHTML",
        source_kinds=("location_hash", "URLSearchParams_ctor", "URLSearchParams_get"),
        sink_kinds=("innerHTML_assign", "outerHTML_assign", "insertAdjacentHTML_call",
                    "dangerouslySetInnerHTML", "vue_v_html_sink"),
        sanitizer_required_absent=True,
        notes="Classic DOM XSS via URL fragment / search param into innerHTML.",
    ),
    Archetype(
        id="fp_postmessage_loose_eval",
        source_kinds=("dom_message", "continuation_message_data",
                      "loose_origin_validation", "missing_origin_validation",
                      "message_event_listener"),
        sink_kinds=("eval_call", "new_Function", "setTimeout_string",
                    "innerHTML_assign", "script_text_assign"),
        notes="postMessage handler with loose/missing origin check feeding eval-class sink.",
    ),
    Archetype(
        id="fp_pp_router_redirect",
        source_kinds=("proto_assign_merge", "proto_assign_bracket", "proto_assign_assign"),
        sink_kinds=("location_href_assign", "window_open", "frame_location_assign"),
        framework="router",
        notes="Prototype pollution into router default config → open redirect.",
    ),
    Archetype(
        id="fp_storage_xss_render_react",
        source_kinds=("persistent_localStorage_read", "persistent_sessionStorage_read"),
        sink_kinds=("innerHTML_assign", "dangerouslySetInnerHTML"),
        framework="react",
        notes="Stored DOM XSS via localStorage → React renderer.",
    ),
    Archetype(
        id="fp_cspt_fetch",
        source_kinds=("location_pathname", "URLSearchParams_get", "location_hash"),
        sink_kinds=("fetch_call", "fetch_with_user_input", "xhr_open_call", "axios_call"),
        notes="Client-side path traversal landing in fetch URL (CSPT-2-CSRF candidate).",
    ),
    Archetype(
        id="fp_clobber_innerHTML",
        source_kinds=("dom_clobber_global_read",),
        sink_kinds=("innerHTML_assign", "dangerouslySetInnerHTML", "vue_v_html_sink"),
        notes="DOM clobbering of a global consumed by an HTML sink.",
    ),
    Archetype(
        id="fp_open_redirect_pathname",
        source_kinds=("location_pathname", "location_href_read", "document_referrer"),
        sink_kinds=("location_href_assign", "location_assign_call", "window_open"),
        notes="URL-from-URL feeding navigation; javascript: scheme bypass risk.",
    ),
    Archetype(
        id="fp_broadcast_postmessage_data_leak",
        source_kinds=("localStorage_get", "document_cookie", "persistent_localStorage_read"),
        sink_kinds=("broadcast_postmessage", "postMessage_send"),
        notes="Sensitive value sent via postMessage with broadcast targetOrigin.",
    ),
)


def _normalize(s: str | None) -> str:
    return (s or "").strip()


def match_chain(chain: dict) -> list[dict]:
    """Return a list of ``{archetype_id, similarity, notes}`` records."""
    src_id = _normalize(chain.get("source", {}).get("taxonomy_id"))
    sink_id = _normalize(chain.get("sink", {}).get("taxonomy_id"))
    if not src_id or not sink_id:
        return []
    hits: list[dict] = []
    for arch in ARCHETYPES:
        if src_id not in arch.source_kinds:
            continue
        if sink_id not in arch.sink_kinds:
            continue
        sim = 0.8
        if arch.sanitizer_required_absent and chain.get("sanitized"):
            sim -= 0.4
        sim = max(0.0, min(1.0, sim))
        hits.append({
            "archetype_id": arch.id,
            "similarity": round(sim, 3),
            "notes": arch.notes,
        })
    return hits


def match_corpus(chains: list[dict]) -> dict[str, Any]:
    by_archetype: dict[str, int] = {}
    matched = 0
    for c in chains:
        ms = match_chain(c)
        if ms:
            matched += 1
            c["fingerprint_matches"] = ms
            for m in ms:
                by_archetype[m["archetype_id"]] = by_archetype.get(m["archetype_id"], 0) + 1
    return {
        "chains_total": len(chains),
        "chains_matched": matched,
        "by_archetype": by_archetype,
    }
