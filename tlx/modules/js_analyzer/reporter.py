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


def score_chain(chain: dict, snippets: dict) -> float:
    """Score a chain 0–100. Higher = more likely to be exploitable.

    Pure function: no I/O, no global state mutation.

    Components (additive):
      sink_severity    0–40   high sink taxonomy → 40, medium → 25, else 10
      source_sens      0–20   attacker-controlled sources score higher
      path_directness  0–20   shorter call paths are more reliable
      sanitiser_penalty −30   subtract if known sanitiser pattern found in any snippet
      snippet_available 0–10  all path nodes have snippets → more confident
      async_bonus      0–10   async patterns are harder to spot manually
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
    if _SANITISER_PATTERNS.search(combined):
        penalty = -30

    # snippet_available: all path qnames have non-empty snippet
    snip_pts = 10 if path and all(snippets.get(q, "") for q in path) else 0

    # async_bonus: any snippet contains async API
    async_pts = 10 if _ASYNC_PATTERNS.search(combined) else 0

    total = sink_pts + src_pts + dir_pts + penalty + snip_pts + async_pts
    return max(0.0, min(100.0, float(total)))


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

    # ── 4. Score, sort, cap ───────────────────────────────────────────────
    for chain in chains:
        if chain.get("vuln_class_hint") == "Prototype Pollution gadget chain":
            # PP chains carry their own intrinsic score (0.7–1.0); scale to 0-100
            # so they sort comparably alongside taint-flow chains.
            chain["score"] = float(chain.get("score", 0.8)) * 100.0
        else:
            chain["score"] = score_chain(chain, snippets)

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
