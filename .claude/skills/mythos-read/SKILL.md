---
name: mythos-read
description: Full-source-tree whole-bundle audit by one big Claude Code subagent, inspired by the Mythos OpenBSD-vuln discovery (Code with Claude London 2026). Complements the chain-based pipeline — catches bugs with no clean data-flow edge (cross-file invariants, prototype-pollution gadgets, crypto misuse, auth-state confusion, dead-code reactivation). Only viable when `targets/<name>/sources/` fits inside a single Opus prompt (default cap 5 MB eligible). Hypotheses get cross-checked against existing chains; novel medium+ confidence ones are emitted as synthetic chains for cc-taint-adversarial follow-up. Trigger: `/mythos-read <target>` OR user says "mythos read", "full-tree audit", "whole-bundle Opus pass", "Mythos-style audit". Run AFTER `sourcemap-explode` (and ideally `js-index` + `chain-triage` so cross-checking against known chains is meaningful).
---

# mythos-read

Whole-source-tree audit. ONE big read-only Claude Code subagent reads the
entire bundled `sources/` tree in a single prompt and emits hypothesised
bugs. Designed as a complement to (not a replacement for) the chain
pipeline: chain analysis follows data-flow edges; mythos catches the
class of bugs where there *is* no edge — cross-file invariants violated,
prototype-pollution gadgets activating dead code, crypto misuse,
auth-state confusion.

Inspiration: the Mythos OpenBSD-vuln discovery talk (Code with Claude
London 2026 — Anthropic Cybersecurity panel), where Opus found a
non-trivial OpenBSD bug by reading the relevant subsystem end-to-end.

This skill is a Claude-Code-driven workflow per CLAUDE.md Rule 7. The
Python helper at `bin/mythos_read.py` does NOT call any LLM SDK — it
only sizes, bundles, validates, and ingests. Claude Code dispatches the
single audit subagent.

## When NOT to run

- Eligible source tree > 5 MB (the default cap). The prepare step
  refuses; recommend chain pipeline (`chain-triage` →
  `cc-taint-adversarial`) instead.
- No `sources/` tree (run `sourcemap-explode` first).
- Single-target only — no cross-target full-reads.

## Inputs

| Path | Required | Produced by |
| --- | --- | --- |
| `targets/<name>/sources/` | required | `sourcemap-explode` |
| `targets/<name>/status.json` | required | `target-init` |
| `targets/<name>/chains/hot.jsonl` | preferred | `chain-triage` |
| `targets/<name>/chains/dom_reachable.jsonl` | preferred | `dom-xss-hunt` |
| `targets/<name>/opus/*.json` | optional | `opus-deep-audit` / `cc-taint-adversarial` |

The chain/opus inputs feed the "already-audited chain id" list embedded
in the prompt so the subagent can flag overlapping hypotheses.

## Pipeline

### Phase 1 — size check

```bash
python3 bin/mythos_read.py size --target <name>
```

Output JSON: `{total_bytes, eligible_bytes, files, eligible_files,
verdict, ...}`. Verdict ∈ `{viable, over-budget, empty}`. Eligible
extensions: `.js .jsx .ts .tsx .mjs .cjs .html .htm .svelte .vue`.
Default excludes: `*.min.js`, `*.map`, `*.json`, `node_modules/`,
`vendor/`, `dist/`, `build/`, leading-underscore, `*.test.*`,
`*.spec.*`.

If `verdict = over-budget`, STOP. Tell the user the chain pipeline is
the right call here.

### Phase 2 — prepare

```bash
python3 bin/mythos_read.py prepare --target <name>
```

Writes `targets/<name>/mythos/_prompt.md` from the template at
`.claude/skills/mythos-read/prompts/full_tree.md`. Substitutions:

- `{{TARGET_NAME}}`
- `{{FILE_TREE}}` — compact path-only listing of eligible files
- `{{SOURCE_BUNDLE}}` — concatenated source bodies with
  `### <relpath>` headers
- `{{KNOWN_CHAIN_IDS}}` — JSON list of chain ids drawn from
  `chains/hot.jsonl` + `chains/dom_reachable.jsonl` + any audited
  records under `opus/*.json` (used so the subagent can flag
  overlap)

Overrides:

- `--max-bytes 5242880` (default; bytes, raise with care)
- `--exclude-glob '*.min.js,*.map,*custom.js'` (comma-separated)
- `--include-ext '.js,.ts'` (default covers the standard frontend set)

Re-running `prepare` overwrites `_prompt.md` (idempotent).

### Phase 3 — dispatch (Claude Code, in this conversation)

You read `targets/<name>/mythos/_prompt.md` and dispatch ONE
general-purpose subagent with the prompt body. The subagent gets the
entire source tree inline:

```
Agent(
  subagent_type="general-purpose",
  description="mythos-read full-tree audit: <name>",
  prompt=<contents of targets/<name>/mythos/_prompt.md>,
)
```

Subagent constraints (also in the prompt body):

- Read-only. No file writes. No MCP mutations.
- Allowed tools: `Read`, `Grep`, `Glob` against
  `targets/<name>/sources/`, `wiki/`. Allowed MCP:
  `mcp__tlx__docs_query` against `target_<name>` if the collection
  exists.
- Output **JSON only** matching the schema embedded in the prompt.
  No prose preamble, no code fences.
- Single response — no follow-up turns. Audit budget is the one prompt
  + one response.

Capture the JSON response to a temp file (e.g.
`targets/<name>/mythos/_response.json`) for the next step.

### Phase 4 — ingest

```bash
python3 bin/mythos_read.py ingest --target <name> \
    --response-file targets/<name>/mythos/_response.json
```

Validates the schema, strips forbidden keys (see below), coerces the
`class` enum, then writes:

- `targets/<name>/mythos/<utc>.json` — full audited record (timestamped;
  re-ingest never overwrites)
- `targets/<name>/chains/_mythos_synthetic.jsonl` — append-only feed of
  novel hypotheses (no overlap with known chain) with confidence ≥
  medium

The synthetic chain row is NOT auto-fed into `cc-taint-adversarial`.
That's intentional: hypothesis quality varies, and you should hand-pick
which rows are worth a per-chain audit. To promote one into the
chain-audit pipeline, copy its row into `targets/<name>/chains/hot.jsonl`
(or a custom JSONL) and pass that via
`cc_taint_runner.py prepare --chains-input <path>`.

### Phase 5 — summary

```bash
python3 bin/mythos_read.py summary --target <name>
```

Aggregates every `targets/<name>/mythos/*.json` into a digest and
updates `status.json.phases.mythos`. Prints
`{total_hypotheses, by_class, by_confidence, novel_count,
overlap_count}`.

## JSON response schema (the subagent's output)

```json
{
  "target": "<name>",
  "audited_at": "<UTC iso>",
  "hypotheses": [
    {
      "id": "mythos-<short-slug>",
      "title": "<one-line>",
      "class": "auth_state_confusion | prototype_pollution_gadget | crypto_misuse | cross_file_invariant | dead_code_reactivation | race_condition | path_traversal | ssrf | sqli | xss_no_flow | other",
      "root_cause_files": ["<relative path>:<line range>", ...],
      "reasoning": "<3-8 sentences>",
      "exploit_sketch": "<3-6 sentences if confidence>=medium; empty string if low>",
      "overlap_with_chain_id": "<existing chain id if this matches a chain already in pipeline; null otherwise>",
      "confidence": "high | medium | low",
      "blocking_unknowns": []
    }
  ],
  "review_coverage": {
    "files_reviewed": N,
    "files_skipped": N,
    "skip_reasons": {"minified": N, "vendor": N, ...}
  }
}
```

Forbidden keys (stripped by ingest): `verdict`, `tp`, `fp`,
`true_positive`, `false_positive`, `severity`. `confidence` is the only
score field. Class enum is closed — invalid values coerce to `other`.

## Synthetic chain row schema (chains/_mythos_synthetic.jsonl)

```json
{
  "id": "mythos-<slug>",
  "source_kind": "mythos",
  "title": "<from hypothesis>",
  "class": "<from hypothesis>",
  "files": [...],
  "exploit_sketch": "<from hypothesis>",
  "confidence": "<from hypothesis>",
  "queued_at": "<utc>",
  "ready_for_audit": true
}
```

`cc-taint-adversarial` does NOT natively consume
`_mythos_synthetic.jsonl` today. To feed one into the chain-audit
pipeline, manually copy the row(s) you care about into
`chains/hot.jsonl` (or another JSONL) and pass that via
`cc_taint_runner.py prepare --chains-input <path>`. Future work:
explicit consumer that picks rows by class + confidence.

## Hard rules

- 5 MB eligibility cap by default — refuse to prepare otherwise. The
  whole point is the audit happens in one prompt; spilling into chunks
  defeats the cross-file-invariant mission.
- Per-target only. No cross-target full-reads (a Mythos pass on
  multiple targets is N separate skill invocations).
- Read-only subagent. JSON-only output. Schema enforced on ingest.
- No Anthropic-API direct call from the bin script (per CLAUDE.md
  Rule 7 — `bin/mythos_read.py` never imports `anthropic`).
- Idempotent. `prepare` overwrites `_prompt.md`; `ingest` writes a new
  timestamped `<utc>.json` (history preserved across runs).
- Synthetic chains aren't auto-audited. They wait for human curation
  → `cc-taint-adversarial`.

## Outputs

- `targets/<name>/mythos/_prompt.md` — bundled prompt body
- `targets/<name>/mythos/_size.json` — last size-check result
- `targets/<name>/mythos/<utc>.json` — per-run ingested record
- `targets/<name>/chains/_mythos_synthetic.jsonl` — append-only synthetic
  chain feed
- `targets/<name>/status.json.phases.mythos` — counters + last summary

## Result block

`status.json.phases.mythos`:

```json
{
  "status": "sized | prepared | done",
  "ts": "...",
  "eligible_bytes": N,
  "files": N,
  "max_bytes": N,
  "last_run": "<utc of latest ingested record>",
  "final_summary": {
    "total_hypotheses": K,
    "by_class": {...},
    "by_confidence": {...},
    "novel_count": K,
    "overlap_count": K
  }
}
```

## Failure modes

| Symptom | Action |
| --- | --- |
| `verdict: over-budget` | Recommend chain pipeline; do not retry with a higher cap unless user explicitly OKs. The audit quality degrades with prompt size. |
| Subagent emits prose instead of JSON | Re-issue once with `Output JSON only — no prose, no fences.` appended. If still bad, abort and surface to user. |
| Subagent emits forbidden keys | Runner strips them silently and notes them under `_stripped_keys`. No retry. |
| Invalid `class` value | Coerced to `other`. Logged but not fatal. |
| `sources/` missing | Hard error — re-run `sourcemap-explode` first. |

## Relationship to other skills

- **vs `source_token_count.py` (T1.3)** — the long-context probe sized
  the tree and wrote a thin "hand to Opus" prompt. mythos-read is the
  full pipeline that ACTUALLY dispatches the subagent and ingests its
  output. `source_token_count.py`'s 800k-token threshold maps to
  roughly 3.2 MB at 4 chars/token; mythos-read defaults to 5 MB but
  enforces schema-validated output, so the two complement each other.
- **vs `opus-deep-audit`** — per-chain Sonnet→Opus advisor over a
  pre-computed chain. mythos-read runs once over the whole tree.
- **vs `cc-taint-adversarial`** — per-chain adversarial JSON record.
  mythos-read emits hypotheses; promote interesting novel ones into
  the chain queue manually.
- **vs `opus-gap-audit`** — adjacent-function-gap. mythos-read covers
  this class (cross-file invariants), but `opus-gap-audit` is
  cheaper when you have a specific control qname.
