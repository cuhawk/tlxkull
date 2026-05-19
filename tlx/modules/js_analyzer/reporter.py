"""Phase 3 reporter — bridges Gemini's call-graph findings to Claude Sonnet.

Responsibilities:
1. extract_findings()  — re-queries the live call graph to build a structured
                         payload (the data contract defined in CLAUDE.md).
                         Returns None when no paths were found.
2. build_payload()     — pure helper that constructs the dict from raw parts.
3. handoff_to_claude() — calls claude_agent.analyse_chains() and returns the
                         Markdown report string.

Architecture notes:
- This module calls callgraph_tools directly (not via the Gemini tool surface).
  The tools are already wired by main.py via set_callgraph().
- Claude receives structured JSON only — no raw JS file content.
- snippets are populated by get_function_source for every unique qname that
  appears in any confirmed chain.
"""

import os
import re
from typing import Any

import structlog

from modules.js_analyzer.callgraph_tools import (
    find_pp_chains_tool,
    find_sinks,
    get_function_source,
    list_entry_points,
    trace_to_sink,
)
from modules.js_analyzer.js_analyzer_config import (
    ENABLE_SANITIZER_REALITY,
    ENABLE_SINK_VIABILITY,
    SANITIZER_CONFIDENCE_FLOOR,
    VIABILITY_DROP_THRESHOLD,
)

logger = structlog.get_logger(__name__)


MAX_CHAINS_TO_CLAUDE = int(os.environ.get("MAX_CHAINS", "20"))


# ── helpers ─────────────────────────────────────────────────────────────


def _reported_line(meta: dict) -> int:
    """Return original_line when available (source-map remapped), else line."""
    return meta.get("original_line") or meta.get("line", 0)


def _collect_source_meta(sources: list[dict]) -> dict[str, dict]:
    """Return a qname→source-record mapping for fast lookup."""
    return {s["qname"]: s for s in sources}


def _collect_sink_meta(sinks: list[dict]) -> dict[str, dict]:
    """Return a qname→sink-record mapping for fast lookup."""
    return {s["qname"]: s for s in sinks}


def _extract_qnames_from_gemini_reply(reply: str) -> set[str]:
    """Best-effort extraction of qnames mentioned in Gemini's text reply.

    Matches patterns like:
        dom_xss_lab.js::vulnerable
        dom_xss_lab.js::Renderer.eatMessage
        chunk-028fcc8d.5a0f231f.js::075d

    Used only to prioritise snippet fetching; not used for chain construction.
    """
    pattern = r"[\w.\-]+\.js::[\w.]+"
    return set(re.findall(pattern, reply))


# ── Scoring ──────────────────────────────────────────────────────────────

_SINK_SEVERITY: dict[str, int] = {
    # high = 40 pts
    "innerHTML_assign": 40, "outerHTML_assign": 40,
    "insertAdjacentHTML_call": 40, "document_write": 40,
    "document_writeln": 40, "eval_call": 40, "new_Function": 40,
    "setTimeout_string": 40, "setInterval_string": 40,
    "srcdoc_assign": 40, "dangerouslySetInnerHTML": 40,
    "jquery_html": 40, "document_domain_assign": 40,
    "event_handler_attr_assign": 40, "setAttribute_dangerous_attr": 40,
    "jquery_parseHTML": 40, "jquery_selector_with_user_input": 40,
    "jquery_attr_dangerous": 40, "angular_legacy_trustAs": 40,
    "angular_modern_bypassSecurityTrust": 40, "vue_compile": 40,
    "angular_compile": 40, "iframe_srcdoc_assign": 40,
    "createContextualFragment": 40, "vm_runIn_family": 40,
    "vm_Script_ctor": 40, "child_process_exec": 40,
    "setImmediate_string": 40, "eval_indirect": 40,
    "execScript_legacy": 40, "lodash_merge_set": 40,
    "jquery_extend_deep": 40, "object_setPrototypeOf": 40,
    "reflect_setPrototypeOf": 40, "computed_proto_assign": 40,
    # medium = 25 pts
    "location_href_assign": 25, "location_assign_call": 25,
    "location_replace_call": 25, "window_open": 25,
    "postMessage_send": 25, "jquery_append": 25,
    "jquery_before": 25, "jquery_after": 25,
    "fetch_call": 25, "jquery_prepend": 25,
    "jquery_replaceWith": 25, "jquery_replaceAll": 25,
    "jquery_wrap_family": 25, "jquery_insertBefore_after": 25,
    "script_src_assign": 25, "script_text_assign": 25,
    "require_dynamic": 25, "location_bare_assign": 25,
    "frame_location_assign": 25, "window_navigate_legacy": 25,
    "trusted_types_create_policy": 25, "dom_clobbering_or_fallback": 25,
}

_SOURCE_SENSITIVITY: dict[str, int] = {
    "location_hash":        20,
    "location_search":      20,
    "location_href_read":   18,
    "location_pathname":    15,
    "document_URL":         15,
    "message_event_listener": 18,
    "onmessage_handler":    18,
    "localStorage_get":     12,
    "sessionStorage_get":   12,
    "document_cookie":      10,
    "document_referrer":    8,
    "URLSearchParams_ctor": 15,
}

_SANITISER_PATTERNS = re.compile(
    r"DOMPurify|escapeHtml|encodeURI|\.sanitize\s*\(|innerHTML\s*=\s*.*escape",
    re.IGNORECASE,
)

_ASYNC_PATTERNS = re.compile(
    r"addEventListener|postMessage|fetch\(|XMLHttpRequest",
)


def score_chain(
    chain: dict,
    snippets: dict,
    *,
    runtime_confirmed_sinks: set[str] | None = None,
    browser_context: Any = None,
    target_dir: str | None = None,
) -> float:
    """Score a chain 0–100. Higher = more likely to be exploitable.

    Pure function: no I/O, no global state mutation.

    Components (additive):
      sink_severity    0–40   high sink taxonomy → 40, medium → 25, else 10
      source_sens      0–20   attacker-controlled sources score higher
      path_directness  0–20   shorter call paths are more reliable
      sanitiser_penalty −30   subtract if known sanitiser pattern found in any snippet
      snippet_available 0–10  all path nodes have snippets → more confident
      async_bonus      0–10   async patterns are harder to spot manually
      runtime_confirm  0/+15  sink fired in a headless-browser run

    Sprint-A additions (plans/ARCHITECTURE_EVOLUTION.md §4, §5):
      * When ``ENABLE_SINK_VIABILITY`` and a BrowserContext is provided,
        the returned score is multiplied by the sink's viability factor
        (CSP / Trusted Types / parser context / framework override).
        Off by default.
      * When ``ENABLE_SANITIZER_REALITY``, the −30 sanitizer penalty is
        only applied when the matched sanitizer's effective confidence
        clears ``SANITIZER_CONFIDENCE_FLOOR``. Otherwise the chain stays
        un-penalized and gets a ``partial_sanitizer`` note.
    """
    sink_id    = chain.get("sink", {}).get("taxonomy_id", "")
    source_id  = chain.get("source", {}).get("taxonomy_id", "")
    depth      = chain.get("depth", len(chain.get("path", [])) - 1)
    path       = chain.get("path", [])

    # sink_severity
    sink_pts = _SINK_SEVERITY.get(sink_id, 10)

    # source_sensitivity
    src_pts = _SOURCE_SENSITIVITY.get(source_id, 5)

    # path_directness
    if depth <= 1:
        dir_pts = 20
    elif depth == 2:
        dir_pts = 15
    elif depth <= 4:
        dir_pts = 10
    elif depth <= 7:
        dir_pts = 5
    else:
        dir_pts = 0

    # sanitiser_penalty: check all snippets for path nodes
    penalty = 0
    path_snippets = [snippets.get(q, "") for q in path]
    combined = "\n".join(path_snippets)
    sanitizer_hit = _SANITISER_PATTERNS.search(combined)
    if sanitizer_hit:
        if ENABLE_SANITIZER_REALITY:
            # Evaluate the matched sanitizer for adequacy.
            sv = _evaluate_path_sanitizer(
                sink_id=sink_id,
                combined_snippet=combined,
                sanitizer_match=sanitizer_hit.group(0),
                target_dir=target_dir,
            )
            if sv is not None and sv.confidence >= SANITIZER_CONFIDENCE_FLOOR:
                penalty = -30
            else:
                penalty = 0  # partial sanitizer — keep chain in play
                chain.setdefault("annotations", []).append({
                    "kind": "partial_sanitizer",
                    "sanitizer_verdict": sv.to_dict() if sv is not None else None,
                })
        else:
            penalty = -30

    # snippet_available: all path qnames have non-empty snippet
    snip_pts = 10 if path and all(snippets.get(q, "") for q in path) else 0

    # async_bonus: any snippet contains async API
    async_pts = 10 if _ASYNC_PATTERNS.search(combined) else 0

    # runtime_confirm: sink was observed firing in a headless-browser run.
    # Strong reachability proof — bumps the chain past most heuristic
    # ceilings so reviewer attention follows.
    runtime_pts = 0
    if runtime_confirmed_sinks and chain.get("sink", {}).get("qname") in runtime_confirmed_sinks:
        runtime_pts = 15

    total = sink_pts + src_pts + dir_pts + penalty + snip_pts + async_pts + runtime_pts
    total = max(0.0, min(100.0, float(total)))

    # ── Viability multiplicative adjustment (§4) ─────────────────────────
    if ENABLE_SINK_VIABILITY and browser_context is not None and sink_id:
        try:
            from modules.js_analyzer.sink_viability import compute as _viab, viability_breakdown as _vb
            factor = _viab(sink_id, browser_context)
            if factor < 1.0:
                breakdown = _vb(sink_id, browser_context)
                chain["viability_factor"] = factor
                chain["viability_breakdown"] = breakdown
                total = max(0.0, min(100.0, total * factor))
            else:
                # Surface a benign breakdown so downstream consumers can
                # tell viability ran (vs. silently no-op).
                chain["viability_factor"] = 1.0
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("sink_viability_failed", sink_id=sink_id, error=str(exc))

    return total


def _evaluate_path_sanitizer(
    *,
    sink_id: str,
    combined_snippet: str,
    sanitizer_match: str,
    target_dir: str | None,
):
    """Map the regex-matched sanitizer fragment to a taxonomy id and run
    the registry. Returns ``SanitizerVerdict`` or None when we can't
    classify.

    Cheap fragment→id table — matches the well-known sanitizer ids in
    ``taxonomies/sanitizers.json``.
    """
    from modules.js_analyzer.sanitizer_registry import evaluate

    frag = sanitizer_match.lower()
    if "dompurify" in frag:
        sid = "sanitizer_dompurify"
    elif ".sanitize(" in frag:
        sid = "sanitizer_dompurify_namespaced"
    elif "encodeuri" in frag:
        sid = "sanitizer_encodeURIComponent"
    elif "escapehtml" in frag or frag.endswith(".escape("):
        sid = "sanitizer_lodash_escape"
    elif "createhtml" in frag:
        sid = "sanitizer_trustedtypes_createHTML"
    else:
        return None
    try:
        return evaluate(
            sid,
            call_snippet=combined_snippet,
            target_dir=target_dir,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("sanitizer_evaluate_failed", sid=sid, error=str(exc))
        return None


# ── main API ─────────────────────────────────────────────────────────────


def extract_findings(
    gemini_reply: str,
    target_folder: str,
    callgraph,
    severity: str = "high",
) -> dict | None:
    """Re-query the call graph to build a structured findings payload.

    Walks the same discovery path the Gemini agent used:
      find_sinks → list_entry_points → trace_to_sink per source

    Args:
        gemini_reply:  Gemini's final text reply (used to cross-reference
                       and to enrich the snippets set with any qnames
                       Gemini explicitly mentioned).
        target_folder: The folder path passed to --target.
        callgraph:     The live CallGraph instance (already set_callgraph'd).
        severity:      Sink severity filter ('high', 'medium', 'low', or None).

    Returns:
        A findings dict conforming to the data contract, or None if no
        source→sink paths were found.
    """
    # ── 1. Census ────────────────────────────────────────────────────────
    sinks_result   = find_sinks(severity=severity)
    sources_result = list_entry_points()

    sinks_by_qname   = _collect_sink_meta(sinks_result.get("sinks", []))
    sources_by_qname = _collect_source_meta(sources_result.get("sources", []))

    if not sources_by_qname or not sinks_by_qname:
        return None

    index_stats = {
        "nodes": callgraph.node_count() if callgraph else 0,
        "edges": callgraph.edge_count() if callgraph else 0,
        "tags":  callgraph.tag_count()  if callgraph else 0,
    }

    # ── 2. Trace every source → sink ─────────────────────────────────────
    chains: list[dict] = []
    chain_id = 0

    for src_qname, src_meta in sources_by_qname.items():
        result = trace_to_sink(from_qname=src_qname, severity=severity)
        for path_obj in result.get("paths", []):
            nodes = path_obj.get("nodes", [])
            if not nodes:
                continue

            sink_qname = nodes[-1]
            sink_meta  = sinks_by_qname.get(sink_qname, {})

            chain_id += 1
            chains.append({
                "id":     chain_id,
                "source": {
                    "qname":       src_qname,
                    "file":        src_meta.get("original_file") or src_meta.get("file", ""),
                    "line":        _reported_line(src_meta),
                    "taxonomy_id": src_meta.get("taxonomy_id", ""),
                },
                "sink": {
                    "qname":       sink_qname,
                    "file":        sink_meta.get("original_file") or sink_meta.get("file", ""),
                    "line":        _reported_line(sink_meta),
                    "taxonomy_id": sink_meta.get("taxonomy_id", ""),
                },
                "depth": path_obj.get("depth", len(nodes) - 1),
                "path":  nodes,
                "sanitisers_in_path": path_obj.get("sanitisers_in_path", []),
            })

    # ── 2b. Merge prototype-pollution gadget chains ──────────────────────
    pp_result = find_pp_chains_tool(max_depth=8)
    pp_chains = pp_result.get("chains", []) if isinstance(pp_result, dict) else []
    for c in pp_chains:
        chain_id += 1
        c["id"] = chain_id
        c["vuln_class_hint"] = "Prototype Pollution gadget chain"
        # Ensure source.taxonomy_id exists for downstream consumers
        if "source" in c and "taxonomy_id" not in c["source"]:
            c["source"]["taxonomy_id"] = "proto_assign"
        chains.append(c)

    if not chains:
        return None

    # ── 3. Fetch snippets for every unique qname ─────────────────────────
    all_qnames: set[str] = set()
    for chain in chains:
        all_qnames.update(chain["path"])

    # Also include any qnames Gemini explicitly named in its reply —
    # these may not appear in a chain path but were referenced for context.
    all_qnames.update(_extract_qnames_from_gemini_reply(gemini_reply))

    snippets: dict[str, str] = {}
    for qname in sorted(all_qnames):
        src_result = get_function_source(qname=qname)
        if "source" in src_result:
            snippets[qname] = src_result["source"]

    # Runtime evidence: load qnames of sinks observed firing in a
    # headless-browser run (mock_backend sink_monitor merge). Best-effort
    # — table may not exist on older DBs.
    runtime_confirmed_sinks: set[str] = set()
    try:
        if callgraph and getattr(callgraph, "conn", None) is not None:
            rows = callgraph.conn.execute(
                "SELECT DISTINCT n.qualified_name FROM runtime_sink_hits r "
                "JOIN nodes n ON n.id = r.sink_node_id "
                "WHERE r.sink_node_id IS NOT NULL"
            ).fetchall()
            runtime_confirmed_sinks = {r[0] for r in rows if r and r[0]}
    except Exception:
        runtime_confirmed_sinks = set()

    # Sprint-A (§4): load BrowserContext for this target if present.
    # Fully optional — absence yields ``None`` and viability scoring is
    # skipped. The skill driver ``bin/infer_browser_context.py`` writes
    # this file.
    browser_context = None
    if ENABLE_SINK_VIABILITY and target_folder:
        try:
            from modules.js_analyzer.browser_context import load as _bctx_load
            browser_context = _bctx_load(target_folder)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("browser_context_load_failed", error=str(exc))

    # ── 4. Score, sort, cap ───────────────────────────────────────────────
    for chain in chains:
        if chain.get("vuln_class_hint") == "Prototype Pollution gadget chain":
            # PP chains carry their own intrinsic score (0.7–1.0); scale to 0-100
            # so they sort comparably alongside taint-flow chains.
            chain["score"] = float(chain.get("score", 0.8)) * 100.0
        else:
            chain["score"] = score_chain(
                chain, snippets,
                runtime_confirmed_sinks=runtime_confirmed_sinks,
                browser_context=browser_context,
                target_dir=target_folder,
            )
        if chain.get("sink", {}).get("qname") in runtime_confirmed_sinks:
            chain["runtime_confirmed"] = True

    # Sprint-A (§4): when viability runs, demote chains under the drop
    # threshold so they fall out of the hot list — but keep them in the
    # full chain set for downstream review.
    if ENABLE_SINK_VIABILITY:
        for chain in chains:
            vf = chain.get("viability_factor", 1.0)
            if vf < VIABILITY_DROP_THRESHOLD:
                chain["score"] = min(chain.get("score", 0.0), 5.0)
                chain.setdefault("annotations", []).append({
                    "kind": "viability_demoted",
                    "factor": vf,
                    "threshold": VIABILITY_DROP_THRESHOLD,
                })

    chains.sort(key=lambda c: c["score"], reverse=True)

    total_chains = len(chains)
    chains = chains[:MAX_CHAINS_TO_CLAUDE]

    if total_chains > 0:
        logger.info(
            "reporter_chains_scored",
            total=total_chains,
            sent=len(chains),
            highest=round(chains[0]["score"], 1),
            lowest=round(chains[-1]["score"], 1),
        )

    return build_payload(target_folder, index_stats, chains, snippets)


def build_payload(
    target_folder: str,
    index_stats: dict,
    chains: list[dict],
    snippets: dict[str, str],
) -> dict:
    """Construct the data-contract payload (pure, no side-effects).

    The payload shape matches CLAUDE.md §Data contract (Gemini → Claude).
    """
    return {
        "target_folder": target_folder,
        "index_stats":   index_stats,
        "chains":        chains,
        "snippets":      snippets,
    }


async def handoff_to_claude_async(findings: dict, kernel: Any) -> str:
    """Drive the chain-confirmation loop through kernel.engine.

    Args:
        findings: dict from extract_findings() / build_payload().
        kernel:   tlx Kernel instance.

    Returns:
        Markdown security report string.
    """
    from modules.js_analyzer.claude_agent import analyse_chains_async
    return await analyse_chains_async(findings, kernel)


def handoff_to_claude(findings: dict) -> str:  # pragma: no cover
    raise RuntimeError(
        "handoff_to_claude() removed in Session B. "
        "Use handoff_to_claude_async(findings, kernel)."
    )
