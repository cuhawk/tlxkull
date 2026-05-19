"""Parser-context inference for HTML / URL / JS / CSS sinks.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §15.

A taint chain that reaches ``innerHTML = userInput`` is dangerous *only
if* the resulting string is parsed in a context that permits the
attacker's intended primitive — script execution, attribute injection,
URL navigation. ~40% of LLM-confirmed FPs come from chains whose final
parser context can't execute the assumed payload.

This module is **deterministic** and **pure** (single dict lookup
per sink). It infers three orthogonal facts per sink:

  1. ``context_class``     — the parser context the value lands in
                              (html_body, html_attr_quoted, url_attr,
                              event_handler_attr, srcdoc, svg_body,
                              json_in_script, css_url, ...).
  2. ``encoding_state``    — how the value has been encoded along the
                              chain path (raw, html-entities,
                              attr-quoted, url-encoded, json-stringified,
                              css-escaped, unknown).
  3. ``execution_viable``  — coarse classification of what a payload
                              *can* do in this (context, state) pair
                              (js, js-event, css-data-uri, html-only,
                              inert).

Consumers:
  - reporter.score_chain multiplies severity by ``viability_multiplier``.
  - audit_pipeline emits all three into ChainIR for LLM consumption.
  - SARIF properties include the breakdown for analyst inspection.

Behind ``JSAnalyzerConfig.ENABLE_PARSER_CONTEXT`` (default ON — fully
additive, no traversal cost, deterministic).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable

__all__ = [
    "ParserContext",
    "EncodingTransform",
    "infer_sink_context",
    "propagate_encoding",
    "classify_viability",
    "viability_multiplier",
    "score_chain",
    "Wrapper",
    "WRAPPERS",
    "SINK_CONTEXTS",
]


# ──────────────────────────────────────────────────────────────────────
# Coarse taxonomies (§15.5)
# ──────────────────────────────────────────────────────────────────────

CONTEXT_CLASSES: Final = frozenset((
    "html_body",
    "html_attr_quoted",
    "html_attr_unquoted",
    "url_attr",
    "event_handler_attr",
    "srcdoc",
    "svg_body",
    "svg_attr",
    "mathml",
    "template_inert",
    "json_in_script",
    "css_property",
    "css_url",
    "xml",
    # Non-DOM contexts kept here for chain scoring symmetry:
    "js_eval",
    "js_function_body",
    "unknown",
))

ENCODING_STATES: Final = frozenset((
    "raw",
    "html-entities",
    "attr-quoted",          # surrounding quotes intact; raw inside
    "attr-quoted-strict",   # quotes + & escapes
    "url-encoded",
    "json-stringified",
    "css-escaped",
    "partial-entities-bypassable",
    "unknown",
))

EXECUTION_VIABLE: Final = frozenset((
    "js",                   # full XSS — script execution achievable
    "js-event",             # event-handler attribute; XSS in many cases
    "css-data-uri",         # css/url-context — open redirect / data-URL XSS
    "html-only",            # markup injection but no script
    "inert",                # encoded enough that no payload runs
    "unknown",
))


# ──────────────────────────────────────────────────────────────────────
# Sink → parser context map (canonical taxonomy lookup)
# Keyed by ``taxonomy_id`` matching tlx/.../taxonomies/sinks.json.
# Unknown taxonomy IDs default to ``unknown`` — no penalty.
# ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ParserContext:
    """The static parser-context judgement attached to one sink node."""
    context_class: str
    encoding_state: str = "raw"
    execution_viable: str = "js"
    rationale: str | None = None


# Pragmatic catalog covering the high-traffic sinks our taxonomies
# already tag. Names mirror taxonomies/sinks.json IDs and the V1
# sink_capabilities.json layout. Add entries as new tags ship.
SINK_CONTEXTS: Final[dict[str, ParserContext]] = {
    # Plain HTML body parser ─ innerHTML, outerHTML, insertAdjacentHTML.
    "innerHTML_assign":               ParserContext("html_body"),
    "outerHTML_assign":               ParserContext("html_body"),
    "insertAdjacentHTML":             ParserContext("html_body"),
    "document_write":                 ParserContext("html_body",
                                                    rationale="document.write triggers full HTML parsing"),
    "document_writeln":               ParserContext("html_body"),
    "range_createContextualFragment": ParserContext("html_body"),
    "DOMParser_parseFromString":      ParserContext("html_body"),
    "jquery_html":                    ParserContext("html_body"),
    "react_dangerouslySetInnerHTML":  ParserContext("html_body",
                                                    rationale="React opt-out; raw HTML"),
    "vue_v_html":                     ParserContext("html_body"),
    "angular_inner_html_binding":     ParserContext("html_body"),

    # Attribute-level — quoted/unquoted matters for break-out characters.
    "setAttribute_dynamic":           ParserContext("html_attr_quoted"),
    "node_attribute_assign":          ParserContext("html_attr_quoted"),

    # URL-bearing attributes (href, src, action, formaction, ...).
    "href_assign":                    ParserContext("url_attr"),
    "src_assign":                     ParserContext("url_attr"),
    "action_assign":                  ParserContext("url_attr"),
    "formaction_assign":              ParserContext("url_attr"),
    "location_assign":                ParserContext("url_attr",
                                                    rationale="navigation; javascript: URI candidate"),
    "location_href_assign":           ParserContext("url_attr"),
    "window_open":                    ParserContext("url_attr"),

    # Event handler attributes — ANY break-out is JS execution.
    "onclick_assign":                 ParserContext("event_handler_attr"),
    "onmouseover_assign":             ParserContext("event_handler_attr"),
    "node_event_handler_assign":      ParserContext("event_handler_attr"),

    # iframe srcdoc — full document parsing.
    "iframe_srcdoc_assign":           ParserContext("srcdoc"),

    # SVG / MathML — rich script-execution surface in many browsers.
    "svg_innerHTML":                  ParserContext("svg_body"),
    "svg_use_href":                   ParserContext("svg_attr"),

    # JS execution sinks (eval / Function / setTimeout(string) / setInterval(string)).
    "eval_call":                      ParserContext("js_eval"),
    "function_constructor":           ParserContext("js_function_body"),
    "settimeout_string":              ParserContext("js_eval"),
    "setinterval_string":             ParserContext("js_eval"),
    "execScript":                     ParserContext("js_eval"),
    "script_text_assign":             ParserContext("js_eval"),

    # JSON-in-script (Next/Nuxt initial state hydration).
    "next_initial_data":              ParserContext("json_in_script",
                                                    rationale="__NEXT_DATA__ hydration"),
    "nuxt_state":                     ParserContext("json_in_script"),

    # CSS contexts.
    "style_assign":                   ParserContext("css_property"),
    "style_url":                      ParserContext("css_url"),
    "css_text_assign":                ParserContext("css_property"),
}


# ──────────────────────────────────────────────────────────────────────
# Encoding wrappers (§15.6) — each wrapper transforms the encoding_state
# attached to the value as it flows from caller's argument to callee's
# return.
# ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Wrapper:
    qname_or_name: str
    transform_to: str                # output encoding_state
    invariant_under: tuple[str, ...] = ()
    # When wrapper is a sanitizer, mark the contexts where it actually
    # provides safety (for context-aware viability adjustment).
    safe_in: tuple[str, ...] = ()


def _w(qname: str, to: str, *, safe_in: tuple[str, ...] = ()) -> Wrapper:
    return Wrapper(qname_or_name=qname, transform_to=to, safe_in=safe_in)


WRAPPERS: Final[dict[str, Wrapper]] = {
    # Standard library encodings.
    "JSON.stringify":              _w("JSON.stringify",        "json-stringified",
                                       safe_in=("json_in_script",)),
    "encodeURIComponent":          _w("encodeURIComponent",    "url-encoded",
                                       safe_in=("url_attr", "css_url")),
    "encodeURI":                   _w("encodeURI",             "url-encoded",
                                       safe_in=("url_attr",)),
    "escape":                      _w("escape",                "url-encoded"),

    # Common HTML escapers.
    "escapeHTML":                  _w("escapeHTML",            "html-entities",
                                       safe_in=("html_body", "html_attr_quoted")),
    "escapeHtml":                  _w("escapeHtml",            "html-entities",
                                       safe_in=("html_body", "html_attr_quoted")),
    "_.escape":                    _w("_.escape",              "html-entities",
                                       safe_in=("html_body", "html_attr_quoted")),
    "he.encode":                   _w("he.encode",             "html-entities",
                                       safe_in=("html_body", "html_attr_quoted")),
    "validator.escape":            _w("validator.escape",      "html-entities",
                                       safe_in=("html_body", "html_attr_quoted")),

    # Attribute-quoted escapers (entities + " ' & < >).
    "escapeAttribute":             _w("escapeAttribute",       "attr-quoted-strict",
                                       safe_in=("html_attr_quoted",)),
    "encodeForHTMLAttribute":      _w("encodeForHTMLAttribute","attr-quoted-strict",
                                       safe_in=("html_attr_quoted",)),

    # CSS escapers.
    "CSS.escape":                  _w("CSS.escape",            "css-escaped",
                                       safe_in=("css_property", "css_url")),

    # Sanitizers — treat as html-entities by default; the
    # sanitizer-reality module handles version/config-aware refinement.
    "DOMPurify.sanitize":          _w("DOMPurify.sanitize",    "html-entities",
                                       safe_in=("html_body", "srcdoc", "svg_body",
                                                "html_attr_quoted")),
    "sanitizeHtml":                _w("sanitizeHtml",          "html-entities",
                                       safe_in=("html_body", "srcdoc",
                                                "html_attr_quoted")),
    "xss":                         _w("xss",                   "html-entities",
                                       safe_in=("html_body",)),
}


# Helper: aliases the AST extractor records as ``call_name``. We accept
# any of the three forms so we don't depend on which qname the
# wrapper resolver picked.
_WRAPPER_ALIAS: Final[dict[str, str]] = {
    "stringify":             "JSON.stringify",
    "escapeHtml":            "escapeHTML",
    "html_escape":           "escapeHTML",
    "htmlEscape":            "escapeHTML",
    "sanitize":              "DOMPurify.sanitize",
    "dompurify":             "DOMPurify.sanitize",
    "DOMPurify":             "DOMPurify.sanitize",
    "escape_html":           "escapeHTML",
    "encodeURIComponent":    "encodeURIComponent",
}


def _wrapper_for(qname: str | None) -> Wrapper | None:
    if not qname:
        return None
    if qname in WRAPPERS:
        return WRAPPERS[qname]
    alias = _WRAPPER_ALIAS.get(qname)
    if alias and alias in WRAPPERS:
        return WRAPPERS[alias]
    # Last-name fallback — methods like ``escapeHTML`` referenced via a
    # default import keep the same trailing name.
    tail = qname.rsplit(".", 1)[-1]
    if tail in WRAPPERS:
        return WRAPPERS[tail]
    alias = _WRAPPER_ALIAS.get(tail)
    if alias and alias in WRAPPERS:
        return WRAPPERS[alias]
    return None


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────

def infer_sink_context(taxonomy_id: str | None) -> ParserContext:
    """Static lookup; unknowns default to ``unknown`` with raw state."""
    if not taxonomy_id:
        return ParserContext("unknown", "raw", "unknown",
                             rationale="no taxonomy_id")
    pc = SINK_CONTEXTS.get(taxonomy_id)
    if pc:
        return pc
    return ParserContext("unknown", "raw", "unknown",
                         rationale=f"taxonomy_id={taxonomy_id} not in SINK_CONTEXTS")


@dataclass(frozen=True)
class EncodingTransform:
    """Outcome of walking a chain's wrappers from source to sink."""
    final_state: str
    visited: tuple[str, ...]
    safe_wrapper_seen: bool


def propagate_encoding(
    path_qnames: Iterable[str],
    sink_context: ParserContext,
) -> EncodingTransform:
    """Walk ``path_qnames`` (in order from source toward sink) and update
    the encoding_state. Concatenation in the path resets a *segment* to
    raw — we model conservatively per-chain (not per-segment) by treating
    any wrapper hit as advancing the global state; if no wrapper is hit
    the state stays ``raw``.

    A wrapper whose ``safe_in`` includes the sink's context is recorded
    via ``safe_wrapper_seen``.
    """
    state = "raw"
    safe = False
    visited: list[str] = []
    for q in path_qnames:
        w = _wrapper_for(q)
        if not w:
            continue
        visited.append(w.qname_or_name)
        state = w.transform_to
        if sink_context.context_class in w.safe_in:
            safe = True
    return EncodingTransform(
        final_state=state,
        visited=tuple(visited),
        safe_wrapper_seen=safe,
    )


def classify_viability(context_class: str, encoding_state: str) -> str:
    """Decision table from §15.8. Conservative defaults: anything unknown
    falls to ``unknown`` (caller leaves score unchanged).
    """
    if context_class == "unknown":
        return "unknown"

    if encoding_state == "unknown":
        return "unknown"

    # Hard-inert regardless of context.
    if encoding_state == "url-encoded" and context_class not in (
        "js_eval", "js_function_body", "event_handler_attr"
    ):
        return "inert"

    if context_class in ("js_eval", "js_function_body"):
        # Eval-class: any raw / unencoded value executes code.
        if encoding_state in ("raw", "json-stringified"):
            # JSON.stringify around an eval still gives the attacker the
            # full string literal — they can inject closers.
            return "js"
        return "inert"

    if context_class == "event_handler_attr":
        # onclick="..." — break-out via "; ..." or similar.
        if encoding_state in ("raw", "html-entities", "partial-entities-bypassable"):
            return "js-event"
        if encoding_state == "attr-quoted-strict":
            return "inert"
        return "inert"

    if context_class == "html_body":
        if encoding_state in ("raw", "partial-entities-bypassable"):
            return "js"
        if encoding_state == "html-entities":
            return "html-only"
        return "inert"

    if context_class == "srcdoc":
        if encoding_state == "raw":
            return "js"
        return "html-only"

    if context_class == "svg_body":
        if encoding_state == "raw":
            return "js"
        return "html-only"

    if context_class == "svg_attr":
        if encoding_state == "raw":
            return "js-event"  # several SVG attrs run JS
        return "inert"

    if context_class == "html_attr_quoted":
        if encoding_state in ("raw", "partial-entities-bypassable"):
            return "js"
        if encoding_state == "html-entities":
            # Entity-encoded ` ' " < > inside a quoted attribute is
            # generally safe for plain attributes, but still markup-only
            # for special ones (style, srcdoc) — the catalog rerouted
            # those to their own sink_context entries already.
            return "inert"
        return "inert"

    if context_class == "html_attr_unquoted":
        # Even with entities, an unquoted attribute is broken by a space.
        if encoding_state == "raw":
            return "js"
        return "html-only"

    if context_class == "url_attr":
        if encoding_state == "raw":
            return "css-data-uri"
        if encoding_state == "url-encoded":
            return "inert"
        return "inert"

    if context_class == "css_url":
        if encoding_state in ("raw",):
            return "css-data-uri"
        return "inert"

    if context_class == "css_property":
        if encoding_state == "raw":
            return "html-only"
        return "inert"

    if context_class == "json_in_script":
        # If JSON.stringify ran, the value is safely embedded — but
        # closing-script-tag injection (</script>) remains the well-
        # known break-out.
        if encoding_state == "json-stringified":
            return "html-only"
        if encoding_state == "raw":
            return "js"
        return "inert"

    if context_class == "template_inert":
        return "inert"

    return "unknown"


def viability_multiplier(execution_viable: str) -> float:
    """Multiplicative weight applied to chain severity. ``unknown`` keeps
    the chain unchanged so we never punish what we don't understand.
    """
    return {
        "js":            1.00,
        "js-event":      1.00,
        "css-data-uri":  0.60,
        "html-only":     0.20,
        "inert":         0.05,
        "unknown":       1.00,
    }.get(execution_viable, 1.00)


def score_chain(
    sink_taxonomy_id: str | None,
    path_qnames: Iterable[str],
) -> dict:
    """Single entry-point — call from the chain scorer.

    Returns a dict with all the fields ChainIR / SARIF expect. Pure
    function; no IO. ``factor`` is the multiplier you apply to the base
    severity.
    """
    ctx = infer_sink_context(sink_taxonomy_id)
    enc = propagate_encoding(path_qnames, ctx)
    viable = classify_viability(ctx.context_class, enc.final_state)
    factor = viability_multiplier(viable)
    if enc.safe_wrapper_seen and viable in ("js", "js-event"):
        # A context-appropriate sanitizer is on the path; depress severity
        # without hiding the chain entirely. The sanitizer-reality module
        # may override this if it knows the sanitizer is bypassable.
        factor *= 0.20
    return {
        "context_class":   ctx.context_class,
        "encoding_state":  enc.final_state,
        "execution_viable": viable,
        "wrappers_visited": list(enc.visited),
        "safe_wrapper_seen": enc.safe_wrapper_seen,
        "rationale":        ctx.rationale,
        "factor":           round(factor, 4),
    }
