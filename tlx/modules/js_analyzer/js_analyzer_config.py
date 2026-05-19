"""js_analyzer config constants.

Holds env-derived model/key constants and ALLOWED_ROOTS
used by callgraph_tools. ALLOWED_ROOTS is set at module
register time via callgraph_tools.set_callgraph(base_paths=…)
from kernel.sandbox roots. Empty default is intentional
(fail-closed if set_callgraph never runs).
"""
from __future__ import annotations

import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY    = os.environ.get("GOOGLE_API_KEY", "")
CLAUDE_MODEL      = "claude-sonnet-4-6"
CLAUDE_OPUS_MODEL = os.environ.get("CLAUDE_OPUS_MODEL", "claude-opus-4-7")

# callgraph_tools imports ALLOWED_ROOTS at module top. Real roots come
# from kernel.sandbox via ct.set_callgraph(base_paths=...) at register
# and slash-handler time; this empty default just satisfies the import.
ALLOWED_ROOTS: list = []

# js_consult_opus bounds — per-audit-run caps for the second-opinion tool
MAX_CONSULTS       = int(os.environ.get("JS_MAX_CONSULTS", "5"))
CONSULT_BUDGET_USD = float(os.environ.get("JS_CONSULT_BUDGET_USD", "1.50"))


# ── Sprint A feature flags (plans/ARCHITECTURE_EVOLUTION.md §4-§5) ──────
# Each flag is off by default so the new viability + sanitizer-reality
# scoring lands as a strictly additive layer. Turn on by setting the env
# var to "1" / "true" / "yes".

def _flag(name: str, default: bool = False) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


# §4 — multiply chain.score by sink viability (CSP / Trusted Types /
#       parser context / framework override). Off by default; when on,
#       chains with viability < VIABILITY_DROP_THRESHOLD are demoted out
#       of the hot list rather than dropped entirely.
ENABLE_SINK_VIABILITY    = _flag("JS_ENABLE_SINK_VIABILITY", default=False)
VIABILITY_DROP_THRESHOLD = float(os.environ.get("JS_VIABILITY_DROP_THRESHOLD", "0.10"))

# §5 — apply DOMPurify / sanitize-html / xss / he version + config
#       awareness when judging sanitizer adequacy. Off by default.
ENABLE_SANITIZER_REALITY = _flag("JS_ENABLE_SANITIZER_REALITY", default=False)
# A sanitizer with effective confidence below this value is NOT treated
# as having "cleared" the chain — chain stays in clean.jsonl with a
# partial_sanitizer note.
SANITIZER_CONFIDENCE_FLOOR = float(os.environ.get("JS_SANITIZER_CONFIDENCE_FLOOR", "0.50"))

# When both are on, the reporter emits viability_score, sanitizer
# effective confidence, and a viability_factor breakdown alongside the
# existing chain.score field, leaving downstream consumers unaffected
# unless they opt in.

# §3 — async continuation edges. When on, callers that pass through
#       producer detectors (addEventListener, .then, postMessage, etc.)
#       can route taint into handler bodies via the per-target DB's
#       continuations table. Best-first extractor honors this by
#       default unless --no-continuation is set.
ENABLE_CONTINUATION_EDGES = _flag("JS_ENABLE_CONTINUATION_EDGES", default=True)

# §8 — confidence-driven best-first traversal. When on, downstream
#       sort/rank uses calibrated P(chain) when available.
ENABLE_CONFIDENCE_RANKING = _flag("JS_ENABLE_CONFIDENCE_RANKING", default=False)

# §11 — LLM stage refactor. Builds ChainIR (canonical IR + window
#       snippets) and routes Sonnet to verdict-only mode. Off by default
#       until A/B verdict comparison validates parity / improvement.
ENABLE_LLM_CHAIN_IR = _flag("JS_ENABLE_LLM_CHAIN_IR", default=False)


# ── V2 feature flags (plans/ARCHITECTURE_EVOLUTION_V2.md §11-§24) ───────
# Every V2 subsystem ships behind a flag and is additive over the V1
# pipeline. Off by default; turn on per-target via env or per-engagement
# memory.md.

# V2 §11 — persistent client-side state taint (storage_events table,
#          synthetic write→read edges). Adds storage hops to chain BFS.
ENABLE_PERSISTENT_TAINT = _flag("JS_ENABLE_PERSISTENT_TAINT", default=False)
PERSISTENT_TAINT_MAX_HOPS = int(os.environ.get("JS_PERSISTENT_TAINT_MAX_HOPS", "1"))

# V2 §12 — origin / postMessage trust modeling. Surfaces
#          origin_validation kind into chain trust_score.
ENABLE_ORIGIN_TRUST = _flag("JS_ENABLE_ORIGIN_TRUST", default=False)

# V2 §13 — DOM clobbering candidate detection. Off by default; emits
#          chains/clobber.jsonl when on.
ENABLE_DOM_CLOBBER = _flag("JS_ENABLE_DOM_CLOBBER", default=False)

# V2 §14 — prototype-pollution gadget linkage (implicit_lookups +
#          pp_gadgets catalog). Off by default; emits chains/pp.jsonl.
ENABLE_PP_GADGETS = _flag("JS_ENABLE_PP_GADGETS", default=False)

# V2 §15 — parser-context / encoding-state / execution viability per
#          HTML-sink. Multiplies into chain viability factor. SAFE TO
#          DEFAULT ON; deterministic and additive.
ENABLE_PARSER_CONTEXT = _flag("JS_ENABLE_PARSER_CONTEXT", default=True)

# V2 §16 — obfuscation-aware normalization pre-pass. Off by default;
#          adds 30-60s cold AST build cost.
ENABLE_DEOBFUSCATION_NORMALIZE = _flag("JS_ENABLE_DEOBFUSCATION_NORMALIZE", default=False)

# V2 §17 — query DSL (no runtime effect; opt-in for analyst CLI).
ENABLE_QUERY_DSL = _flag("JS_ENABLE_QUERY_DSL", default=True)

# V2 §18 — delta / incremental scans. Off by default; opt-in via CLI.
ENABLE_DELTA_SCAN = _flag("JS_ENABLE_DELTA_SCAN", default=False)

# V2 §19 — corpus-guided pattern intelligence. Off by default; emits
#          fingerprint_matches[] into chain rows when on.
ENABLE_CORPUS_PATTERNS = _flag("JS_ENABLE_CORPUS_PATTERNS", default=False)

# V2 §20 — chain compression / canonicalization for LLM ingestion.
#          SAFE TO DEFAULT ON; cuts Sonnet/Opus token cost ~40-60%.
ENABLE_CHAIN_COMPRESSION = _flag("JS_ENABLE_CHAIN_COMPRESSION", default=True)

# V2 §21 — multi-target correlation. Off by default; opt-in per target.
ENABLE_MULTI_TARGET_CORR = _flag("JS_ENABLE_MULTI_TARGET_CORR", default=False)

# V2 §22 — sink reachability validation (route map + lifecycle +
#          feature flags). Off by default.
ENABLE_SINK_REACHABILITY = _flag("JS_ENABLE_SINK_REACHABILITY", default=False)
REACHABILITY_DEAD_THRESHOLD = float(os.environ.get("JS_REACHABILITY_DEAD_THRESHOLD", "0.05"))

# V2 §23 — client-side auth/state abuse expansion. Off by default; new
#          chain class.
ENABLE_AUTH_ABUSE = _flag("JS_ENABLE_AUTH_ABUSE", default=False)

# V2 §24 — worker / service-worker semantic modeling. Off by default.
ENABLE_WORKER_SEMANTICS = _flag("JS_ENABLE_WORKER_SEMANTICS", default=False)


def v2_summary() -> dict[str, bool]:
    """Snapshot of every V2 flag for status.json + audit logs."""
    return {
        "persistent_taint":         ENABLE_PERSISTENT_TAINT,
        "origin_trust":             ENABLE_ORIGIN_TRUST,
        "dom_clobber":              ENABLE_DOM_CLOBBER,
        "pp_gadgets":               ENABLE_PP_GADGETS,
        "parser_context":           ENABLE_PARSER_CONTEXT,
        "deobfuscation_normalize":  ENABLE_DEOBFUSCATION_NORMALIZE,
        "query_dsl":                ENABLE_QUERY_DSL,
        "delta_scan":               ENABLE_DELTA_SCAN,
        "corpus_patterns":          ENABLE_CORPUS_PATTERNS,
        "chain_compression":        ENABLE_CHAIN_COMPRESSION,
        "multi_target_corr":        ENABLE_MULTI_TARGET_CORR,
        "sink_reachability":        ENABLE_SINK_REACHABILITY,
        "auth_abuse":               ENABLE_AUTH_ABUSE,
        "worker_semantics":         ENABLE_WORKER_SEMANTICS,
    }
