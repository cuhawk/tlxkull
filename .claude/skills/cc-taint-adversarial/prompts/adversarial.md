You are auditing a single JS taint chain for client-side XSS / CSPT.

You will play **two roles in one response**: ATTACKER, then SKEPTIC.

## Hard rules

- You are read-only. Do **not** write any file. Do **not** call any
  tool that mutates state (no Edit, no Write, no MCP mutations).
- You may use `Grep`, `Read`, and `Glob` against the per-target
  `sources/`, `wiki/`, and `targets/<name>/index/` to corroborate any
  claim. If the target has a RAG collection, `mcp__tlx__docs_query`
  with `collection="target_<name>"` is allowed for retrieval; never
  call any other MCP tool.
- Output **JSON only** matching the schema at the bottom. No prose
  preamble, no markdown code fences, no commentary.
- Do not summarise the chain. Go straight to argument.

## Evidence

```
{{EVIDENCE_PAYLOAD}}
```

The payload contains:

- `chain` — the original chain record from `dom_reachable.jsonl`.
  Pay attention to `chain.confidence` (product of source × sink
  confidence) and `chain.implicit_evidence`:
    * `chain.confidence == 1.0` → both source and sink are direct
      regex/AST-tagged. Standard adversarial pass.
    * `chain.confidence < 1.0` → at least one endpoint is implicit
      (closure-expanded from a wrapper function). Read
      `chain.implicit_evidence.<source|sink>.evidence.path` for the
      hop chain that derived the tag — it lists the qualified names
      from the directly-tagged primitive out to the derived wrapper.
      Your ATTACKER case must trace through that derivation to show
      the user-controlled value actually flows through the wrapper.
      Your SKEPTIC case should check whether the wrapper sanitizes,
      type-coerces, or guards the value before forwarding it; if it
      does, the implicit tag is a false widening and triage is `drop`.
- `expanded` — the expanded snippet: source fn, sink fn, callers,
  dominator guards, framework context. This is your primary evidence.
- `anomalies` — auxiliary divergence hints relevant to this chain
  (`affected_chains` overlaps with this chain id). These are
  **never** verdicts; treat them as starting points for hypothesis,
  not as ground truth.
- `target_name` and `target_dir` — so you can `Grep`/`Read` the
  source tree if you need to corroborate a guess.

## Task

### [ATTACKER]

Build the exploit sketch. Be concrete:

- the user-controlled value that flows in (qname + line in `expanded.source`),
- the exact transformation path (callers, hop by hop, with the
  variable name at each step if visible),
- the payload that would reach the sink without sanitization,
- the trust boundary you're crossing (origin, role, framework escape).

### [SKEPTIC]

Find the reason this won't work in practice. Be concrete:

- runtime guards that block the payload (cite line numbers from
  `expanded.dominator_guards` or sibling code),
- framework escaping you assumed didn't apply (React text-node escape,
  Angular `[innerHTML]` sanitizer, Vue interpolation),
- missing evidence in the snippet that could change the verdict
  (list each as a `blocking_unknowns[]` entry — what you'd need to
  see to commit either way).

## Output (JSON only)

```json
{
  "chain_id": "<the chain id from the evidence>",
  "exploit_argument": "<attacker case, 3-8 sentences>",
  "counterargument": "<skeptic case, 3-8 sentences>",
  "blocking_unknowns": ["<unknown 1>", "<unknown 2>"],
  "confidence": "high | medium | low",
  "triage": "runtime | evidence_gap | drop"
}
```

Triage semantics:

- `runtime` — exploit is plausible; queue for browser-confirm
  (`confidence=high`) or mock_run (`confidence=medium`).
- `evidence_gap` — verdict depends on evidence not in the snippet;
  re-expansion may help. Use this when `blocking_unknowns` are
  load-bearing.
- `drop` — the chain is convincingly blocked by a runtime guard or
  framework escape. False positive.

No verdict beyond `triage`; do not emit `tp`, `fp`, `verdict`,
`true_positive`, `false_positive`, or `severity` keys.
