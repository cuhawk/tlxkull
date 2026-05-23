You are auditing the FULL source tree of one bug-bounty target in a
single pass. This is the "Mythos" mode: complement to per-chain taint
analysis. Your job is to surface bugs the chain pipeline cannot see
because there is no clean data-flow edge — cross-file invariants,
prototype-pollution gadgets activating dead code, crypto misuse,
auth-state confusion, race conditions, dead-code reactivation.

Inspiration: Code with Claude London 2026 — Anthropic Cybersecurity
panel — Opus found a real OpenBSD vulnerability by reading the
relevant subsystem end-to-end.

Target: `{{TARGET_NAME}}`

## Hard rules

- You are read-only. Do NOT write any file. Do NOT call any tool that
  mutates state (no Edit, no Write, no MCP mutations).
- Allowed tools: `Read`, `Grep`, `Glob` against
  `targets/{{TARGET_NAME}}/sources/` and `wiki/`. Allowed MCP:
  `mcp__tlx__docs_query` against `target_{{TARGET_NAME}}` if the
  collection exists.
- Output **JSON only** matching the schema at the bottom. No prose
  preamble, no markdown code fences outside the JSON, no commentary.
- The entire source bundle is embedded inline below. You can re-Read
  individual files if you want larger context, but every eligible file
  is in this prompt.
- This is a single-turn audit. You get one response — no follow-up
  turns, no "let me check that and get back to you". Commit to what
  the evidence supports.

## Reasons-first, score-last

In each hypothesis object, emit `reasoning` BEFORE `confidence` and
emit `exploit_sketch` BEFORE `confidence`. Auto-regressive sampling
anchors on the first token of each value; if you write the score
first, you'll then justify whatever score was sampled, regardless of
the underlying evidence. Reasons first.

## Audit focus — what to LOOK for

Classes the chain pipeline is BAD at, and you are GOOD at:

1. **auth_state_confusion** — A check happens against the wrong
   identity. Common shape: `req.user` validated, but the privileged
   call uses `req.params.user` / a stale closure / a session id from
   a different context. The chain pipeline only sees the data flow,
   not the identity mismatch.
2. **prototype_pollution_gadget** — A code path becomes reachable
   only when `Object.prototype.X` is set. Find the gadget end:
   property reads that trigger code execution, sink calls, or
   privilege checks. Pair with any reachable polluter.
3. **crypto_misuse** — IV reuse, ECB mode, predictable seed, missing
   `verify()`, hashed-equality timing leaks, JWT alg confusion, no
   `kid` allowlist.
4. **cross_file_invariant** — One file assumes a property holds
   that another file violates. Common shape: "module A assumes
   input is sanitized by module B", but B's sanitizer was removed
   in a refactor.
5. **dead_code_reactivation** — Code labeled `if (DEBUG)` or
   `if (false)` that flips on under attacker-influenced config /
   feature-flag / URL parameter.
6. **race_condition** — Time-of-check / time-of-use; cache
   invalidation between two reads; an async path that doesn't await
   a critical write.
7. **path_traversal**, **ssrf**, **sqli**, **xss_no_flow**, **other**
   — generic categories. `xss_no_flow` means an injection sink that
   isn't reachable by a clean source→sink chain but is reachable in
   practice (e.g. via prototype pollution, postMessage indirection,
   storage shim).

If you don't have a high-confidence hypothesis in any of these
classes, do NOT pad the response. Return an empty `hypotheses` list
with a clear `review_coverage` block. A short honest negative result
beats a long fabricated positive one.

## Cross-check against known chains

Chains already audited (or queued) for this target:

```json
{{KNOWN_CHAIN_IDS}}
```

For every hypothesis you emit:

- Set `overlap_with_chain_id` to the existing chain id if your
  hypothesis is the SAME bug the chain pipeline already found.
- Set `overlap_with_chain_id: null` if the hypothesis is genuinely
  novel (i.e., the chain pipeline did not surface it).

The novel hypotheses are the high-value output. Overlap hypotheses
still go in the JSON — they validate the chain pipeline — but they
won't be queued for follow-up.

## File tree (eligible files only)

```
{{FILE_TREE}}
```

## Source bundle

Each file appears as `### <relative path>` followed by its raw
contents. Files are concatenated in path-sorted order.

{{SOURCE_BUNDLE}}

## Output (JSON only) — REASONS-FIRST KEY ORDER

```json
{
  "target": "{{TARGET_NAME}}",
  "audited_at": "<UTC iso timestamp at time of writing>",
  "hypotheses": [
    {
      "id": "mythos-<short-slug-derived-from-title>",
      "title": "<one-line summary>",
      "class": "auth_state_confusion | prototype_pollution_gadget | crypto_misuse | cross_file_invariant | dead_code_reactivation | race_condition | path_traversal | ssrf | sqli | xss_no_flow | other",
      "root_cause_files": ["<relative path>:<line range>", "..."],
      "reasoning": "<3-8 sentences. The mechanism. Why it fires. What invariant is violated.>",
      "exploit_sketch": "<3-6 sentences if confidence>=medium. Concrete steps an attacker would take. Empty string if confidence=low.>",
      "overlap_with_chain_id": "<integer chain id if this matches a known chain; null otherwise>",
      "confidence": "high | medium | low",
      "blocking_unknowns": ["<unknown 1>", "<unknown 2>"]
    }
  ],
  "review_coverage": {
    "files_reviewed": <int>,
    "files_skipped": <int>,
    "skip_reasons": {"<reason>": <int>, "...": <int>}
  }
}
```

Do NOT emit keys: `verdict`, `tp`, `fp`, `true_positive`,
`false_positive`, `severity`. `confidence` is the only score field;
the ingest helper will strip any forbidden keys you emit anyway.

`class` MUST be from the closed enum above. Any other value will be
coerced to `other`.

Emit the JSON object as your entire response — nothing before, nothing
after.
