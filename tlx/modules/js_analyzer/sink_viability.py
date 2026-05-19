"""Sink viability scoring — multiplicative semantic adjustment to chain
severity using CSP / Trusted Types / parser context / framework
overrides.

Plan: plans/ARCHITECTURE_EVOLUTION.md §4.

The current scorer (``reporter.score_chain``) is additive over coarse
sink severity. That ignores that ``el.innerHTML = userData`` is RCE on
a no-CSP page, dangling-markup only on ``script-src 'none'``, and inert
under enforced Trusted Types. ``compute()`` returns a factor in
[0.05, 1.0] that the reporter multiplies into its score.

Failure mode: any missing input degrades to factor 1.0 (no change).
Behind a feature flag (``ENABLE_SINK_VIABILITY``); off by default.

Pure function — no IO once the sidecar JSON is loaded once per process.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from modules.js_analyzer.browser_context import BrowserContext, CSPDirectives

__all__ = [
    "compute",
    "viability_breakdown",
    "load_capabilities",
]

_DEFAULT_CAPS_PATH = (
    Path(__file__).resolve().parent / "taxonomies" / "sink_capabilities.json"
)


@lru_cache(maxsize=1)
def load_capabilities(path: str | None = None) -> dict:
    """Load sink_capabilities.json. Cached per-process. Returns ``{}`` on
    error so the scorer can degrade gracefully."""
    p = Path(path) if path else _DEFAULT_CAPS_PATH
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    # Strip the leading underscore-prefixed schema keys.
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _csp_neutralization_factor(cap: dict, csp: CSPDirectives) -> float:
    """How thoroughly does the observed CSP neutralize this sink?

    Returns 1.0 when CSP is absent / permissive, 0.05–0.3 when CSP is
    strict against the sink's primary capability.
    """
    if not csp.raw:
        return 1.0
    # Report-only policies tell the browser to fire violation reports
    # but never block execution. They must NOT downgrade chain
    # severity — a chain that lands in production through a
    # report-only CSP fires for real.
    if csp.report_only:
        return 1.0

    exec_ctx = cap.get("exec_context", "")
    script_exec = cap.get("script_exec", "none")
    script_set = {s.lower().strip("'\"") for s in (csp.script_src or csp.default_src or [])}
    # Empty allowlist → CSP has no script-src direction → treat as permissive.
    if not script_set:
        return 1.0

    # Sinks that don't execute script at all are untouched by script-src.
    if script_exec == "none":
        return 1.0

    # Hard guard: script-src 'none' kills any JS-execution path.
    if "'none'" in script_set or "none" in script_set:
        # Sinks via attribute / HTML still have non-script effects (CSS
        # injection, dangling-markup token leak) — keep a small residual.
        if exec_ctx in ("html_parser", "attribute"):
            return 0.20
        if exec_ctx in ("js_eval",) and not csp.unsafe_eval_allowed:
            return 0.05
        if exec_ctx == "url" and script_exec == "via_script_tag":
            # javascript: URI requires inline/eval grant; under 'none' likely blocked.
            return 0.10
        return 0.10

    # eval-class sinks gated by unsafe-eval.
    if exec_ctx == "js_eval":
        return 1.0 if csp.unsafe_eval_allowed else 0.10

    # html_parser / attribute paths that need an inline script or inline
    # event handler.
    if script_exec in ("direct", "via_event_handler", "via_script_tag"):
        if csp.unsafe_inline_allowed:
            return 1.0
        if csp.strict_dynamic:
            # strict-dynamic keeps inline OFF unless the script was
            # injected by a nonce-trusted script. From data-flow alone
            # we can't assume the attacker controls a nonce-script.
            return 0.30
        if exec_ctx in ("html_parser", "attribute"):
            return 0.30
        if exec_ctx == "url":
            # javascript: URI still works unless navigate-to / form-action
            # restricts; that's rare — keep at 0.6 to flag.
            return 0.60

    return 1.0


def _trusted_types_factor(cap: dict, ctx: BrowserContext) -> float:
    """If Trusted Types is enforced and the sink is TT-guarded, the sink
    is inert unless the chain *creates* the TT policy itself."""
    if not cap.get("trusted_types_guarded"):
        return 1.0
    if not ctx.trusted_types.enforced:
        return 1.0
    # Enforced + guarded: the sink is rejected at runtime unless a
    # policy returns a TrustedHTML. A 0.05 leaves enough signal that the
    # chain still appears if scoring is barely-positive elsewhere, but
    # demotes it out of the hot list.
    return 0.05


def _parser_context_factor(cap: dict) -> float:
    """Per parser context, small bias against the very-noisy contexts.

    text and dom_property sinks rarely execute script directly without
    a separate sink down the chain.
    """
    pc = cap.get("parser_context", "")
    if pc == "text":
        return 0.30
    if pc == "url":
        # URL sinks aren't always XSS — many are open-redirect at most.
        # Don't depress too much; downstream taxonomies separate already.
        return 0.85
    return 1.0


def _framework_override_factor(cap: dict, ctx: BrowserContext) -> float:
    """Apply framework-aware multipliers.

    Examples:
      * angular_bypass_trust_html under Angular: keep 1.0 (explicit opt-out).
      * angular_inner_html_binding under Angular without bypass: 0.4 (Angular auto-sanitizes).
      * dangerouslySetInnerHTML under React: 1.0 (explicit opt-out).
    """
    overrides = cap.get("framework_overrides") or {}
    fw = (ctx.rendering.framework or "").lower()
    if not fw or fw not in overrides:
        return 1.0
    note = (overrides[fw] or "").lower()
    if "blocked unless" in note or "sanitizes by default" in note:
        # Sink is normally blocked; depend on a separate "bypass" tag in
        # the chain. Conservative 0.4 — caller can override.
        return 0.4
    if "explicit" in note:
        # Explicit opt-outs are the default-unsafe path frameworks
        # advertise (dangerouslySetInnerHTML, v-html, bypassSecurityTrustHtml).
        return 1.0
    return 1.0


def compute(
    sink_taxonomy_id: str,
    ctx: BrowserContext,
    *,
    capabilities: dict | None = None,
) -> float:
    """Return viability factor in (0, 1] for this sink under this context.

    Multiply this into ``score_chain`` output. 1.0 = no change.
    """
    caps_all = capabilities if capabilities is not None else load_capabilities()
    cap = caps_all.get(sink_taxonomy_id)
    if not cap:
        # Unknown sink: do nothing (don't penalize what we don't know).
        return 1.0

    factor = (
        _csp_neutralization_factor(cap, ctx.csp)
        * _trusted_types_factor(cap, ctx)
        * _parser_context_factor(cap)
        * _framework_override_factor(cap, ctx)
    )
    # Clamp to a small floor so deeply-negated chains still report.
    return max(0.02, min(1.0, factor))


def viability_breakdown(
    sink_taxonomy_id: str,
    ctx: BrowserContext,
    *,
    capabilities: dict | None = None,
) -> dict[str, Any]:
    """Same as compute() but emit each factor separately. Used by the
    reporter to attach an explanation to the chain JSON so the LLM /
    operator can see WHY a chain was demoted."""
    caps_all = capabilities if capabilities is not None else load_capabilities()
    cap = caps_all.get(sink_taxonomy_id, {})
    csp_f = _csp_neutralization_factor(cap, ctx.csp) if cap else 1.0
    tt_f = _trusted_types_factor(cap, ctx) if cap else 1.0
    pc_f = _parser_context_factor(cap) if cap else 1.0
    fw_f = _framework_override_factor(cap, ctx) if cap else 1.0
    total = max(0.02, min(1.0, csp_f * tt_f * pc_f * fw_f)) if cap else 1.0
    return {
        "sink_taxonomy_id": sink_taxonomy_id,
        "known_capability": bool(cap),
        "factors": {
            "csp_neutralization": round(csp_f, 4),
            "trusted_types": round(tt_f, 4),
            "parser_context": round(pc_f, 4),
            "framework_override": round(fw_f, 4),
        },
        "factor_total": round(total, 4),
        "exec_context": cap.get("exec_context") if cap else None,
        "trusted_types_guarded": bool(cap.get("trusted_types_guarded")) if cap else False,
        "csp_observed": bool(ctx.csp.raw),
        "csp_report_only": bool(ctx.csp.report_only),
        "csp_enforced": bool(ctx.csp.raw and not ctx.csp.report_only),
        "trusted_types_enforced": bool(ctx.trusted_types.enforced),
        "framework": ctx.rendering.framework or None,
    }
