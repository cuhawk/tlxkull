"""js_analyzer chain-confirmation agent — dedicated audit loop.

Uses an isolated anthropic client with prompt caching. State writes go
through kernel.services for hypothesis persistence and cost reporting,
but the model loop itself does not route through kernel.engine.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic
import structlog

from kernel.engines.claude import price_per_token
from kernel.schema import Message, TextBlock, ToolResultBlock
from kernel.tools import Tool
from modules.js_analyzer.audit_persistence import AuditRun, _open_conn
from modules.js_analyzer.js_analyzer_config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_OPUS_MODEL,
    CONSULT_BUDGET_USD,
    MAX_CONSULTS,
)


def _block_dump(block: Any) -> Any:
    """Best-effort serialization of a content block for audit_turns persistence."""
    if hasattr(block, "model_dump"):
        return block.model_dump()
    if hasattr(block, "dict"):
        return block.dict()
    return str(block)

_logger = structlog.get_logger(__name__)


# Pricing is sourced from kernel.engines.claude.price_per_token —
# single source of truth (May 2026 Anthropic rates).
# Opus 4.7 uses a new tokenizer (~35% more tokens than 4.6 for
# same input). Per-token price dropped (15→5 in, 75→25 out)
# but effective cost per request is roughly comparable.


TOKEN_LIMIT  = 80_000
BUDGET_LIMIT = 2.00
MAX_ITER     = 60


def _resolve_audit_engine(kernel: Any) -> Any:
    """Return a ClaudeEngine for the audit loop.

    If kernel.engine is already a ClaudeEngine on CLAUDE_MODEL, reuse it
    (shared cache hits across shell + audit). Otherwise instantiate a
    fresh one — audit loop is Sonnet-only.
    """
    from kernel.engines.claude import ClaudeEngine
    eng = getattr(kernel, "engine", None)
    if isinstance(eng, ClaudeEngine) and eng.model == CLAUDE_MODEL:
        return eng
    return ClaudeEngine(model=CLAUDE_MODEL)


def _resolve_audit_db_path(kernel: Any) -> Path | None:
    """Locate ~/.tlx/js_analyzer.db via the registered CallGraph service."""
    services = getattr(kernel, "services", None)
    if services is None:
        return None
    cg = services.get("js_analyzer_callgraph")
    if cg is None:
        return None
    db_path = getattr(cg, "db_path", None)
    if db_path is None:
        return None
    return Path(db_path)


JS_CONSULT_OPUS_SCHEMA = {
    "type": "object",
    "properties": {
        "chain_id": {
            "type": "string",
            "description": "ID of the chain you need a second opinion on.",
        },
        "question": {
            "type": "string",
            "description": (
                "Specific question for Opus. Be precise — do not ask "
                "'is this exploitable'; ask 'does jQuery's .html() "
                "auto-escape this template literal'."
            ),
        },
        "confidence_so_far": {
            "type": "string",
            "enum": ["very_low", "low", "medium"],
            "description": (
                "Your current confidence in your hypothesis. Required."
            ),
        },
    },
    "required": ["chain_id", "question", "confidence_so_far"],
}

JS_CONSULT_OPUS_TOOL = {
    "name": "js_consult_opus",
    "description": (
        "Request a second opinion from Opus on a hard chain. "
        "Use ONLY when ALL of the following are true: "
        "(1) you have already called js_examine_chain, "
        "(2) your confidence is very_low or low, "
        "(3) the chain involves prototype-pollution gadgets, "
        "framework-specific sinks (Angular bypassSecurityTrust*, Vue "
        "v-html, React dangerouslySetInnerHTML), non-obvious sanitiser "
        "bypasses, or sourcemap-mediated chains. "
        "Do NOT use for: vanilla DOM XSS with clear source→sink, "
        "sinks already covered by sinks.json descriptions, or to "
        "double-check verdicts you are already confident about. "
        "Hard cap: 5 consults per audit run. Each consult takes "
        "~10-20 seconds and costs ~$0.30."
    ),
    "input_schema": JS_CONSULT_OPUS_SCHEMA,
}


_CONSULT_SYSTEM_PROMPT = """\
You are a senior application security researcher specialising in \
client-side JavaScript vulnerabilities. You are being consulted by a \
junior auditor (Sonnet) on a specific chain it cannot resolve.

Your job:
1. Read the chain, snippets, taxonomy entries, and framework context.
2. Answer the auditor's specific question.
3. State a verdict: exploitable | not_exploitable | needs_more_data.
4. If exploitable, briefly note the attack pattern.
5. If not, name the specific reason (sanitiser, framework escape, \
context mismatch).

Constraints:
- Do not request more information. Use what you are given.
- Be concise — under 400 words.
- Do not write PoC code. The auditor only needs your verdict + reasoning.
"""


_CONSULT_USER_TEMPLATE = """\
Auditor confidence: {confidence}
Framework context: {framework}

Chain:
{chain_repr}

Code snippets:
{snippets}

Taxonomy:
{taxonomy}

Auditor's question:
{question}
"""


@dataclass
class _RunContext:
    """Per-audit-run state for js_consult_opus.

    Local to one analyse_chains_async invocation. Never module-global —
    counters reset each run.
    """
    consults_used: int = 0
    consults_cost_usd: float = 0.0
    consult_logs: list[dict] = field(default_factory=list)


_SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parent / "prompts" / "system" / "claude_analyst.md"
)

_LOOP_INSTRUCTIONS = """
## How to work

You have tools prefixed with js_. Use them. Do NOT analyse everything in
one reply.

For every chain in the overview:
  1. Call js_get_hypothesis(chain_id) — skip dead ends immediately
  2. Call js_examine_chain(chain_id) — get path and snippets
  3. Trace unsanitised flow source → sink
  4. Call js_submit_finding() with your verdict
  5. Move to the next chain

When every chain_id has a submitted finding, call js_generate_report().
Never call js_generate_report() before all chains are reviewed.

## Hypothesis memory

Before examining any chain, call js_get_hypothesis(chain_id). If status
is 'dead_end', submit false_positive immediately without examining.
If 'confirmed', submit true_positive immediately. After forming a
hypothesis, call js_update_hypothesis() to persist reasoning.
"""


def _load_system_prompt() -> str:
    if _SYSTEM_PROMPT_PATH.exists():
        raw = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        if raw.startswith("---"):
            try:
                end = raw.index("---", 3)
                raw = raw[end + 3:].lstrip("\n")
            except ValueError:
                pass
        return raw + _LOOP_INSTRUCTIONS
    return _LOOP_INSTRUCTIONS


_TOOL_SPECS: list[tuple[str, str, dict]] = [
    (
        "js_examine_chain",
        (
            "Get full details for a specific chain: source node, sink node, "
            "call path, and source-code snippet for every function in the path."
        ),
        {
            "type": "object",
            "properties": {"chain_id": {"type": "integer"}},
            "required": ["chain_id"],
        },
    ),
    (
        "js_get_snippet",
        "Return source code for any function by qualified name.",
        {
            "type": "object",
            "properties": {"qname": {"type": "string"}},
            "required": ["qname"],
        },
    ),
    (
        "js_submit_finding",
        (
            "Record verdict for a chain. Call exactly once per chain "
            "after examining evidence."
        ),
        {
            "type": "object",
            "properties": {
                "chain_id":   {"type": "integer"},
                "verdict":    {"type": "string",
                               "enum": ["true_positive", "false_positive"]},
                "severity":   {"type": "string",
                               "enum": ["high", "medium", "low", "n/a"]},
                "vuln_class": {"type": "string"},
                "proof":      {"type": "string"},
            },
            "required": ["chain_id", "verdict", "proof"],
        },
    ),
    (
        "js_update_hypothesis",
        (
            "Record or update working hypothesis for a chain. "
            "Persists across loop iterations."
        ),
        {
            "type": "object",
            "properties": {
                "chain_id":    {"type": "integer"},
                "status": {
                    "type": "string",
                    "enum": ["open", "dead_end", "confirmed", "needs_more_data"],
                },
                "note":        {"type": "string"},
                "confidence":  {"type": "number"},
                "tested_path": {"type": "string"},
            },
            "required": ["chain_id"],
        },
    ),
    (
        "js_get_hypothesis",
        (
            "Return current hypothesis for a chain. Call at start of "
            "examining any chain to skip dead ends from prior runs."
        ),
        {
            "type": "object",
            "properties": {"chain_id": {"type": "integer"}},
            "required": ["chain_id"],
        },
    ),
    (
        "js_generate_report",
        (
            "Build final Markdown security report from all submitted findings. "
            "Call ONLY after every chain has been reviewed."
        ),
        {
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    (
        JS_CONSULT_OPUS_TOOL["name"],
        JS_CONSULT_OPUS_TOOL["description"],
        JS_CONSULT_OPUS_SCHEMA,
    ),
]


def _make_tools(
    findings: dict,
    state: Any,
    kernel: Any,
    ctx: _RunContext,
) -> list[Tool]:
    """Build per-run Tool objects with handlers bound to this audit context."""
    def _bind(name: str):
        def handler(**kwargs: Any) -> str:
            return _dispatch(name, kwargs, findings, state, kernel, ctx)
        return handler

    return [
        Tool(name=name, description=desc, params=schema, handler=_bind(name))
        for name, desc, schema in _TOOL_SPECS
    ]


def _examine_chain(chain_id: int, findings: dict) -> dict:
    chain = next((c for c in findings["chains"] if c["id"] == chain_id), None)
    if not chain:
        return {
            "error": f"chain {chain_id} not found",
            "valid_ids": [c["id"] for c in findings["chains"]],
        }
    snippets = {
        q: findings["snippets"].get(q, "<unavailable>")
        for q in chain["path"]
    }
    return {"chain": chain, "snippets": snippets}


def _get_snippet(qname: str, findings: dict) -> dict:
    snippet = findings["snippets"].get(qname)
    if snippet is None:
        available = list(findings["snippets"].keys())[:10]
        return {"error": f"no snippet for {qname!r}",
                "available_sample": available}
    return {"qname": qname, "source": snippet}


def _submit_finding(args: dict, state: Any, kernel: Any) -> dict:
    from modules.js_analyzer.module import (
        _persist_hypotheses,
        _save_verdicts_kv,
    )

    chain_id = args["chain_id"]
    state.verdicts[chain_id] = {
        "chain_id":   chain_id,
        "verdict":    args["verdict"],
        "severity":   args.get("severity", "n/a"),
        "vuln_class": args.get("vuln_class", ""),
        "proof":      args["proof"],
    }
    state.reviewed.add(chain_id)
    remaining = state.total_chains - len(state.reviewed)
    _persist_hypotheses(kernel, state)
    _save_verdicts_kv(kernel, state.verdicts)
    return {
        "ok": True,
        "verdict_recorded": args["verdict"],
        "chains_remaining": remaining,
    }


def _update_hypothesis(args: dict, state: Any, kernel: Any) -> dict:
    from modules.js_analyzer.module import _persist_hypotheses

    chain_id    = args["chain_id"]
    status      = args.get("status", "open")
    note        = args.get("note", "")
    confidence  = float(args.get("confidence", 0.5))
    tested_path = args.get("tested_path", "")

    existing = state.hypotheses.get(chain_id, {
        "status": "open", "notes": [], "tested_paths": [], "confidence": 0.5,
    })
    existing["status"]     = status
    existing["confidence"] = max(0.0, min(1.0, confidence))
    if note:
        existing["notes"].append(note)
    if tested_path and tested_path not in existing["tested_paths"]:
        existing["tested_paths"].append(tested_path)
    state.hypotheses[chain_id] = existing
    _persist_hypotheses(kernel, state)
    return {"ok": True, "chain_id": chain_id, "hypothesis": existing}


def _get_hypothesis(chain_id: int, state: Any) -> dict:
    return state.hypotheses.get(chain_id, {
        "status": "open", "notes": [], "tested_paths": [], "confidence": 0.5,
    })


def _generate_report(state: Any, findings: dict, kernel: Any | None = None) -> dict:
    by_id = {c["id"]: c for c in findings["chains"]}
    tp = {cid: v for cid, v in state.verdicts.items()
          if v["verdict"] == "true_positive"}
    fp = {cid: v for cid, v in state.verdicts.items()
          if v["verdict"] == "false_positive"}

    lines = [
        "# Security Analysis Report",
        f"**Target:** {findings['target_folder']}",
        (f"**Chains analysed:** {state.total_chains}  |  "
         f"**True positives:** {len(tp)}  |  "
         f"**False positives:** {len(fp)}"),
        "",
        "---",
    ]
    for severity in ("high", "medium", "low"):
        bucket = [v for v in tp.values() if v.get("severity") == severity]
        lines.append(f"\n## {severity.capitalize()} Severity\n")
        if not bucket:
            lines.append("_No findings._")
            continue
        for v in bucket:
            chain = by_id.get(v["chain_id"], {})
            src  = chain.get("source", {})
            sink = chain.get("sink", {})
            path = " → ".join(chain.get("path", []))
            lines += [
                f"### [CHAIN-{v['chain_id']}] {v['vuln_class']} — "
                f"{src.get('file','')}:{src.get('line','')}",
                f"**Source:** `{src.get('qname','')}` at "
                f"`{src.get('file','')}:{src.get('line','')}`",
                f"**Sink:**   `{sink.get('qname','')}` at "
                f"`{sink.get('file','')}:{sink.get('line','')}`",
                f"**Path:** `{path}`",
                f"**Proof:** {v['proof']}",
                "",
                "---",
            ]
    lines.append("\n## False Positives\n")
    if not fp:
        lines.append("_None._")
    else:
        for v in fp.values():
            lines.append(f"### [CHAIN-{v['chain_id']}] {v['proof']}")

    consult_log = list(getattr(state, "last_consult_log", []) or [])
    if consult_log:
        consult_total = float(getattr(state, "last_consult_cost_usd", 0.0))
        lines.append("\n## Opus consultations\n")
        lines.append("| # | Chain | Confidence | Tokens | Cost |")
        lines.append("|---|-------|------------|--------|------|")
        for i, entry in enumerate(consult_log, 1):
            tok = entry.get("tokens_in", 0) + entry.get("tokens_out", 0)
            lines.append(
                f"| {i} | {entry.get('chain_id','?')} | "
                f"{entry.get('confidence','?')} | {tok} | "
                f"${entry.get('cost_usd', 0.0):.4f} |"
            )
        lines.append(f"\n**Consult total:** ${consult_total:.4f}")

    report = "\n".join(lines)
    state.last_report  = report
    state.audit_status = "done"
    if kernel is not None:
        from modules.js_analyzer.module import _clear_verdicts_kv
        _clear_verdicts_kv(kernel)
    return {"report": report, "ok": True}


def _find_chain(findings: dict, chain_id: Any) -> dict | None:
    """Locate a chain by id. Accepts int or str id (Sonnet may pass either)."""
    chains = findings.get("chains", [])
    try:
        cid_int = int(chain_id)
    except (TypeError, ValueError):
        cid_int = None
    for c in chains:
        if c.get("id") == chain_id or (cid_int is not None and c.get("id") == cid_int):
            return c
    return None


def _gather_chain_snippets(findings: dict, chain: dict) -> str:
    snippets_map = findings.get("snippets", {}) or {}
    parts: list[str] = []
    for q in chain.get("path", []):
        src = snippets_map.get(q, "<unavailable>")
        parts.append(f"// {q}\n{src}")
    return "\n\n".join(parts) if parts else "<no snippets>"


def _gather_taxonomy_context(chain: dict) -> str:
    src = chain.get("source", {}) or {}
    sink = chain.get("sink", {}) or {}
    return (
        f"source taxonomy: {src.get('taxonomy_id', '?')}\n"
        f"sink taxonomy:   {sink.get('taxonomy_id', '?')}"
    )


def _render_chain_for_opus(chain: dict) -> str:
    src = chain.get("source", {}) or {}
    sink = chain.get("sink", {}) or {}
    path = " → ".join(chain.get("path", [])) or "(empty)"
    return (
        f"id: {chain.get('id')}\n"
        f"source: {src.get('qname','')} @ {src.get('file','')}:{src.get('line','')}\n"
        f"sink:   {sink.get('qname','')} @ {sink.get('file','')}:{sink.get('line','')}\n"
        f"depth:  {chain.get('depth', '?')}\n"
        f"path:   {path}"
    )


# ---------------------------------------------------------------------------
# Two-tier audit cascade — Sonnet triage gate (T1.2)
# ---------------------------------------------------------------------------

_TRIAGE_SYSTEM_PROMPT = """\
You are a security triage filter for a JavaScript taint-analysis pipeline.
Your job is to REJECT chains that are obvious false positives so the
flagship-model auditor (Opus) only sees chains that warrant deep review.

Bias toward escalation when uncertain — false negatives are far more
expensive than false positives. Never reject on intuition; reject only
when one of the explicit disqualifiers fires.

REJECT a chain if ANY of these disqualifiers fires:

1. literal_constant_source
   The source argument is a literal constant in every callsite of the
   source function (no user-controlled value flows in).

2. wrapped_safe_sanitizer
   The sink is wrapped in a known-safe sanitizer call WITHIN the same
   function body. Known-safe set:
   - DOMPurify.sanitize
   - encodeURIComponent (only when the sink expects URL-component context)
   - JSON.stringify before innerHTML/outerHTML
   - Trusted Types policy.createHTML

3. pure_intermediates_only
   Every intermediate node in the chain is a pure function: no taint
   propagation, no side effects, no dynamic dispatch.

4. short_length_gate
   The source-to-sink path is gated by a length check `< 8` (or any
   constant under 12) characters before reaching the sink.

If NONE fire, output verdict='escalate'.

Respond ONLY with a single JSON object — no markdown fences, no prose:
{
  "verdict": "reject" | "escalate",
  "rubric_hits": {
    "literal_constant_source": bool,
    "wrapped_safe_sanitizer": bool,
    "pure_intermediates_only": bool,
    "short_length_gate": bool
  },
  "reason": "one short sentence"
}
"""

_TRIAGE_USER_TEMPLATE = """\
CHAIN:
{chain_repr}

TAXONOMY:
{taxonomy}

ADJACENT SNIPPETS:
{snippets}
"""


def sonnet_triage(
    *,
    chain: dict,
    findings: dict,
    model: str | None = None,
    max_tokens: int = 512,
) -> dict:
    """One-shot cheap-stage triage. Implements the rubric in
    `wiki/tools/karpathy/js-review-cascade.md`.

    Returns a dict with keys:
      - verdict:       "reject" | "escalate"
      - rubric_hits:   per-disqualifier booleans
      - reason:        single-sentence rationale from the model
      - cost_usd:      cost of the triage call
      - tokens_in:     int
      - tokens_out:    int
      - duration_ms:   wall-clock for the call
      - error:         present iff parse failed; verdict defaults to escalate
    """
    import time as _time

    model = model or CLAUDE_MODEL
    user_msg = _TRIAGE_USER_TEMPLATE.format(
        chain_repr=_render_chain_for_opus(chain),
        taxonomy=_gather_taxonomy_context(chain),
        snippets=_gather_chain_snippets(findings, chain),
    )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    t0 = _time.perf_counter()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=[
            {
                "type": "text",
                "text": _TRIAGE_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )
    duration_ms = int((_time.perf_counter() - t0) * 1000)

    in_p, out_p = price_per_token(model)
    in_tok = getattr(resp.usage, "input_tokens", 0)
    out_tok = getattr(resp.usage, "output_tokens", 0)
    cache_write = int(getattr(resp.usage, "cache_creation_input_tokens", 0) or 0)
    cache_read = int(getattr(resp.usage, "cache_read_input_tokens", 0) or 0)
    cost = (
        in_tok * in_p
        + cache_write * in_p * 1.25
        + cache_read * in_p * 0.10
        + out_tok * out_p
    )

    text = "\n".join(b.text for b in resp.content if hasattr(b, "text")).strip()
    out: dict = {
        "verdict": "escalate",
        "rubric_hits": {
            "literal_constant_source": False,
            "wrapped_safe_sanitizer": False,
            "pure_intermediates_only": False,
            "short_length_gate": False,
        },
        "reason": "",
        "cost_usd": cost,
        "tokens_in": in_tok,
        "tokens_out": out_tok,
        "duration_ms": duration_ms,
    }
    if not text:
        out["error"] = "empty model response; defaulting to escalate"
        return out
    try:
        first = text.find("{")
        last = text.rfind("}")
        if first < 0 or last < first:
            raise ValueError("no JSON object in response")
        parsed = json.loads(text[first : last + 1])
    except (json.JSONDecodeError, ValueError) as e:
        out["error"] = f"parse failed ({e}); defaulting to escalate"
        return out

    verdict = parsed.get("verdict")
    if verdict not in ("reject", "escalate"):
        out["error"] = f"invalid verdict {verdict!r}; defaulting to escalate"
        return out
    out["verdict"] = verdict
    rh = parsed.get("rubric_hits") or {}
    for k in out["rubric_hits"]:
        out["rubric_hits"][k] = bool(rh.get(k, False))
    out["reason"] = (parsed.get("reason") or "")[:240]
    return out


def _consult_opus(
    args: dict,
    findings: dict,
    state: Any,
    kernel: Any,
    ctx: _RunContext,
) -> str:
    """Single-shot Opus second-opinion call. Returns string for Sonnet."""
    if ctx.consults_used >= MAX_CONSULTS:
        return (
            f"[js_consult_opus] consult limit reached "
            f"({MAX_CONSULTS}/{MAX_CONSULTS}). Decide without "
            f"further consultation."
        )

    if ctx.consults_cost_usd >= CONSULT_BUDGET_USD:
        return (
            f"[js_consult_opus] consult budget reached "
            f"(${ctx.consults_cost_usd:.2f}/${CONSULT_BUDGET_USD:.2f}). "
            f"Decide without further consultation."
        )

    chain_id = args.get("chain_id", "")
    question = (args.get("question", "") or "").strip()
    confidence = args.get("confidence_so_far", "")

    if confidence not in ("very_low", "low", "medium"):
        return "[js_consult_opus] invalid confidence_so_far"
    if confidence == "medium":
        return (
            "[js_consult_opus] confidence='medium' — consult declined. "
            "Only consult on very_low or low. Decide using existing "
            "evidence."
        )
    if not question:
        return "[js_consult_opus] empty question"

    chain = _find_chain(findings, chain_id)
    if chain is None:
        return f"[js_consult_opus] chain_id '{chain_id}' not in findings"

    snippets = _gather_chain_snippets(findings, chain)
    taxonomy_ctx = _gather_taxonomy_context(chain)
    framework = findings.get("framework_tags", [])

    user_msg = _CONSULT_USER_TEMPLATE.format(
        question=question,
        confidence=confidence,
        chain_repr=_render_chain_for_opus(chain),
        snippets=snippets,
        taxonomy=taxonomy_ctx,
        framework=", ".join(framework) or "vanilla",
    )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=CLAUDE_OPUS_MODEL,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": _CONSULT_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )

    in_p, out_p = price_per_token(CLAUDE_OPUS_MODEL)
    in_tok = getattr(resp.usage, "input_tokens", 0)
    out_tok = getattr(resp.usage, "output_tokens", 0)
    cache_write = int(getattr(resp.usage, "cache_creation_input_tokens", 0) or 0)
    cache_read = int(getattr(resp.usage, "cache_read_input_tokens", 0) or 0)
    cost = (
        in_tok * in_p
        + cache_write * in_p * 1.25
        + cache_read * in_p * 0.10
        + out_tok * out_p
    )

    ctx.consults_used += 1
    ctx.consults_cost_usd += cost
    ctx.consult_logs.append({
        "chain_id":   chain_id,
        "question":   question,
        "confidence": confidence,
        "tokens_in":  in_tok,
        "cache_write_tokens": cache_write,
        "cache_read_tokens":  cache_read,
        "tokens_out": out_tok,
        "cost_usd":   cost,
    })

    text_parts = [b.text for b in resp.content if hasattr(b, "text")]
    answer = "\n".join(text_parts).strip() or "[opus returned no text]"

    return (
        f"[js_consult_opus] (consult {ctx.consults_used}/{MAX_CONSULTS}, "
        f"${cost:.3f}, total ${ctx.consults_cost_usd:.3f})\n\n{answer}"
    )


def _dispatch(name: str, inp: dict, findings: dict, state: Any,
              kernel: Any, ctx: _RunContext) -> str:
    if name == "js_examine_chain":
        result: Any = _examine_chain(inp["chain_id"], findings)
    elif name == "js_get_snippet":
        result = _get_snippet(inp["qname"], findings)
    elif name == "js_submit_finding":
        result = _submit_finding(inp, state, kernel)
    elif name == "js_generate_report":
        if state is not None:
            state.last_consult_log      = list(ctx.consult_logs)
            state.last_consult_cost_usd = ctx.consults_cost_usd
            state.last_consults_used    = ctx.consults_used
        result = _generate_report(state, findings, kernel)
    elif name == "js_update_hypothesis":
        result = _update_hypothesis(inp, state, kernel)
    elif name == "js_get_hypothesis":
        result = _get_hypothesis(inp["chain_id"], state)
    elif name == "js_consult_opus":
        return _consult_opus(inp, findings, state, kernel, ctx)
    else:
        result = {"error": f"unknown tool: {name}"}
    return json.dumps(result)


async def analyse_chains_async(
    findings: dict, kernel: Any, *, external_run_id: str | None = None,
) -> str:
    """Run the chain-confirmation loop with an isolated anthropic client.

    Uses kernel only for state access (services + session_store KV).
    The model loop runs through anthropic.Anthropic directly so the audit
    surface is independent of the live shell engine.
    """
    from modules.js_analyzer.module import (
        _chain_signature,
        _clear_verdicts_kv,
        _load_hypotheses_kv,
        _load_verdicts_kv,
    )

    state = kernel.services.get("js_analyzer_state")
    if state is None:
        return "js_analyzer: state service missing"

    state.audit_status = "running"
    state.total_chains = len(findings["chains"])

    sigs_by_id = {c["id"]: _chain_signature(c) for c in findings["chains"]}
    state.sigs_by_id = sigs_by_id

    stored_hyps = _load_hypotheses_kv(kernel)  # sig → hyp
    state.hypotheses = {
        cid: stored_hyps[sigs_by_id[cid]]
        for cid in sigs_by_id
        if sigs_by_id[cid] in stored_hyps
    }

    chain_ids = set(sigs_by_id.keys())
    persisted_verdicts = _load_verdicts_kv(kernel)
    if persisted_verdicts and set(persisted_verdicts.keys()).issubset(chain_ids):
        state.verdicts = persisted_verdicts
        state.reviewed = set(persisted_verdicts.keys())
    else:
        if persisted_verdicts:
            _clear_verdicts_kv(kernel)
        state.verdicts = {}
        state.reviewed = set()

    overview = {
        "target_folder": findings["target_folder"],
        "index_stats":   findings["index_stats"],
        "total_chains":  state.total_chains,
        "chain_ids":     [c["id"] for c in findings["chains"]],
        "hypotheses":    {str(k): v for k, v in state.hypotheses.items()},
    }

    engine = _resolve_audit_engine(kernel)
    system_prompt = _load_system_prompt()
    ctx = _RunContext()
    tools = _make_tools(findings, state, kernel, ctx)

    initial_user = (
        "Analyse the following findings and produce a security report.\n\n"
        f"Overview:\n```json\n{json.dumps(overview, indent=2)}\n```\n\n"
        "Use js_examine_chain() for each chain ID, js_submit_finding() "
        "after each, then js_generate_report() when all chains are done."
    )
    messages: list[Message] = [Message(role="user", content=initial_user)]

    db_path = _resolve_audit_db_path(kernel)
    audit_conn = _open_conn(db_path) if db_path is not None else None
    audit_run: AuditRun | None = None
    if audit_conn is not None:
        audit_run = AuditRun(
            audit_conn,
            shell_session_id=str(getattr(kernel, "session_id", "unknown")),
            target_folder=str(findings.get("target_folder", "")),
            external_run_id=external_run_id,
        )
        try:
            audit_run.start()
            audit_run.append_turn("user", initial_user)
        except Exception as exc:
            _logger.warning("js_analyzer.audit_persist_start_failed",
                            error=str(exc))
            audit_run = None
            audit_conn.close()
            audit_conn = None

    total_tokens = 0
    total_cost   = 0.0
    stop_reason  = "completed"
    failure_reason: str | None = None
    hit_cap = False

    progress_fn = getattr(kernel, "report_progress", None)

    try:
        for _iteration in range(MAX_ITER):
            if state.audit_status == "done":
                break

            if total_tokens >= TOKEN_LIMIT:
                hit_cap = True
                stop_reason = (
                    f"token limit reached ({total_tokens:,} / {TOKEN_LIMIT:,})"
                )
                break

            if total_cost + ctx.consults_cost_usd >= BUDGET_LIMIT:
                hit_cap = True
                stop_reason = (
                    f"budget reached "
                    f"(audit ${total_cost:.4f} + consults "
                    f"${ctx.consults_cost_usd:.4f} / ${BUDGET_LIMIT:.2f})"
                )
                break

            if callable(progress_fn):
                try:
                    progress_fn(
                        "js_analyzer.audit",
                        f"turn {_iteration + 1}/{MAX_ITER}, "
                        f"${total_cost:.2f} spent",
                    )
                except Exception:
                    pass

            resp = await engine.respond(
                messages, tools, system_prompt, max_tokens=4096,
            )

            total_tokens += resp.usage.input_tokens + resp.usage.output_tokens
            total_cost   += resp.cost.total

            messages.append(Message(role="assistant", content=resp.content))
            if audit_run is not None:
                try:
                    audit_run.append_turn(
                        "assistant",
                        [_block_dump(b) for b in resp.content],
                        tokens_in=resp.usage.input_tokens,
                        tokens_out=resp.usage.output_tokens,
                        cost_usd=resp.cost.total,
                    )
                except Exception as exc:
                    _logger.warning("js_analyzer.audit_persist_turn_failed",
                                    error=str(exc))

            if total_tokens > int(TOKEN_LIMIT * 0.6):
                compactor = getattr(kernel, "compactor", None)
                if compactor is not None:
                    try:
                        new_messages, _ = await compactor.compact(messages)
                        messages = new_messages
                        if audit_run is not None:
                            audit_run.append_turn("system", "[compacted]")
                    except Exception as exc:
                        _logger.warning(
                            "js_analyzer.audit_compact_failed",
                            error=str(exc),
                        )

            if not resp.tool_calls:
                text_parts = [
                    b.text for b in resp.content if isinstance(b, TextBlock)
                ]
                text = "\n".join(text_parts) or "[js_analyzer: no output]"
                if state is not None:
                    state.last_audit_cost_usd   = total_cost
                    state.last_audit_tokens     = total_tokens
                    state.last_consult_log      = list(ctx.consult_logs)
                    state.last_consult_cost_usd = ctx.consults_cost_usd
                    state.last_consults_used    = ctx.consults_used
                return text

            tool_results: list[ToolResultBlock] = []
            for call in resp.tool_calls:
                args = call.args if isinstance(call.args, dict) else {}
                result_str = _dispatch(
                    call.name, args, findings, state, kernel, ctx,
                )
                tool_results.append(ToolResultBlock(
                    tool_use_id=call.id,
                    content=result_str,
                ))
            messages.append(Message(role="user", content=tool_results))
            if audit_run is not None:
                try:
                    audit_run.append_turn(
                        "tool_result",
                        [
                            {"type": "tool_result",
                             "tool_use_id": tr.tool_use_id,
                             "content": tr.content}
                            for tr in tool_results
                        ],
                    )
                except Exception as exc:
                    _logger.warning("js_analyzer.audit_persist_turn_failed",
                                    error=str(exc))
        else:
            stop_reason = f"iteration limit ({MAX_ITER})"
            hit_cap = True

        if state is not None:
            state.last_audit_cost_usd  = total_cost
            state.last_audit_tokens    = total_tokens
            state.last_consult_log     = list(ctx.consult_logs)
            state.last_consult_cost_usd = ctx.consults_cost_usd
            state.last_consults_used   = ctx.consults_used

        if state.last_report:
            return state.last_report

        partial = _generate_report(state, findings)
        note = (
            f"\n\n---\n> ⚠️ **Partial report** — loop stopped early: "
            f"{stop_reason}. {len(state.reviewed)}/"
            f"{state.total_chains} chains reviewed."
        )
        return partial.get("report", "") + note
    except Exception as exc:
        failure_reason = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        if audit_run is not None:
            if failure_reason is not None:
                final_status = "failed"
            elif hit_cap:
                final_status = "cap_exceeded"
            else:
                final_status = "completed"
            try:
                audit_run.finish(
                    final_status, total_tokens, total_cost,
                    ctx.consults_used, ctx.consults_cost_usd,
                    failure_reason=failure_reason,
                )
            except Exception as exc:
                _logger.warning("js_analyzer.audit_persist_finish_failed",
                                error=str(exc))
        if audit_conn is not None:
            audit_conn.close()


def analyse_chains(findings: dict) -> str:  # pragma: no cover
    raise RuntimeError(
        "analyse_chains() removed in Session B. "
        "Use analyse_chains_async(findings, kernel) instead."
    )
