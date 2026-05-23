---
name: cc-taint-adversarial
description: Per-chain adversarial taint audit via CC subagents. Trigger: /cc-taint-adversarial <target>, "adversarial taint audit", "cc taint audit", "deep-audit with subagents". Run after dom-xss-hunt (or chain-triage if dom_reachable empty).
---

# cc-taint-adversarial

Drives the Phase 0 → Phase B flow of `plans/CC_TAINT_ADVERSARIAL.md`. Every
LLM call is a Claude Code subagent — no `ANTHROPIC_API_KEY` /
`google.genai` / `GeminiEngine` use. Subagents are **read-only**: they may
`Grep`, `Read`, `Glob`, and `mcp__tlx__docs_query` (when a per-target RAG
collection exists), but never write files or call mutating MCPs. All writes
go through the bin/ helpers.

## Purpose

Replace `opus-deep-audit` for max-quality runs with:

1. **Phase 0** — expand each chain into a snippet bundle (source/sink fn
   bodies, callers up to 2 hops, dominator guards, framework lifecycle).
2. **Phase A** — bucket-level anomaly hints (per sink file). Surfaces
   sibling divergence ("renderSafe sanitizes, renderRaw doesn't") as
   auxiliary evidence — **never** as verdicts.
3. **Phase B** — per-chain adversarial audit. One subagent plays
   `[ATTACKER]` and `[SKEPTIC]` in the same response, returning a JSON
   record with `triage ∈ {runtime, evidence_gap, drop}` and
   `confidence ∈ {high, medium, low}`.
4. **Phase C/D** — routing + runtime confirmation (handled by
   `cc-taint-route` and `browser-confirm` skills).

## Inputs (per target)

| Path | Required | Produced by |
| --- | --- | --- |
| `targets/<name>/status.json` | required | `target-init` |
| `targets/<name>/sources/` | required (readable) | `sourcemap-explode` |
| `targets/<name>/db/js_analyzer.db` | required | `db-isolate snapshot` |
| `targets/<name>/index/{nodes,edges}.jsonl` | required | `js-index` |
| `targets/<name>/chains/dom_reachable.jsonl` | preferred (else hot.jsonl) | `dom-xss-hunt` |
| RAG collection `target_<name>` | optional | `rag-ingest` (only needed if bundle is minified-only) |

## Steps

The skill is **driven by Claude Code in this conversation**. Python helpers
do the file I/O and schema validation; Claude dispatches the subagents.

### Step 1 — Phase 0: expand snippets

Run once per target. Reads `chains/dom_reachable.jsonl` (or `hot.jsonl` if
the user requested it via `--chains-input chains/hot.jsonl`).

```bash
python3 bin/expand_snippet.py --target <name> --all
```

Result: `targets/<name>/chains/expanded/<chain_id>.json` per chain.

### Step 2 — Phase A: prepare bucket anomaly prompts

```bash
python3 bin/bucket_anomaly.py --target <name> prepare
```

Writes per-bucket prompt bodies under `chains/anomalies/_prompts/<slug>.md`
and a `_manifest.json`. Then, for each bucket in the manifest, Claude
dispatches one subagent:

```
Agent(
  subagent_type="general-purpose",
  description="cc-taint bucket anomaly: <bucket_file>",
  prompt=<contents of chains/anomalies/_prompts/<slug>.md>,
)
```

The subagent is **read-only**. Required output: JSON only, schema in the
prompt. Capture the agent's JSON response to a temp file (e.g.
`chains/anomalies/_responses/<slug>.json`) and ingest:

```bash
python3 bin/bucket_anomaly.py --target <name> ingest \
    --bucket <bucket_file> --response-file chains/anomalies/_responses/<slug>.json
```

The ingest step strips any verdict keys (`tp`, `fp`, `verdict`,
`classification`, `confidence`, `severity`, `triage`) and writes the
sanitised record to `chains/anomalies/<slug>.json`.

### Step 3 — Phase B: per-chain adversarial audit

```bash
python3 bin/cc_taint_runner.py --target <name> prepare
```

Writes per-chain prompt bodies under `opus/_prompts/<chain_id>.md`. Each
prompt embeds the expanded snippet AND any anomalies whose
`affected_chains` includes this chain id.

For each chain id in `opus/_manifest.json`, Claude dispatches a subagent:

```
Agent(
  subagent_type="general-purpose",
  description="cc-taint adversarial chain <id>",
  prompt=<contents of opus/_prompts/<chain_id>.md>,
)
```

Subagent constraints (already in the prompt body, but the runner reminds
Claude here too):

- Read-only. No file writes. No MCP mutations.
- May `Grep`/`Read`/`Glob` against `targets/<name>/sources/`, `wiki/`,
  `targets/<name>/index/`. May `mcp__tlx__docs_query` against
  `target_<name>` collection if one exists. Nothing else.
- Output is JSON only matching the schema in
  `prompts/adversarial.md`.

Capture the agent's JSON response, then ingest:

```bash
python3 bin/cc_taint_runner.py --target <name> ingest \
    --chain-id <id> --response-file <temp_path>
```

Validation rules enforced by `_coerce_record()`:

- Required keys: `chain_id, exploit_argument, counterargument,
  blocking_unknowns, confidence, triage`.
- Forbidden keys (stripped): `verdict, tp, fp, true_positive,
  false_positive, classification, severity`.
- `confidence ∈ {high, medium, low}`, `triage ∈ {runtime,
  evidence_gap, drop}`.
- `chain_id` is overwritten with the manifest id (subagent can't
  forge a different one).

A failing schema check raises `error:` to stderr, appends to
`status.json.errors`, and returns exit 2. **Do not retry by hammering the
subagent.** If a chain fails, log it and move on; surface to user at the
end.

### Step 4 — finalize Phase B

```bash
python3 bin/cc_taint_runner.py --target <name> finalize
```

Rolls counters into `status.json.phases.cc_taint_adversarial.final_summary`
and prints `{total, by_triage, by_confidence}`.

### Step 4.5 — two-judge verifier (per runtime/high + runtime/medium chain)

Second-opinion pass on every chain the auditor flagged as
`runtime` + `high|medium`. Reasoning: per the 2026 prompting playbook
(Code with Claude London), a single LLM judge over-justifies its
first scored token. A fresh-context verifier subagent reading only
the auditor's reasoning catches strawman counterarguments,
mis-cited line numbers, and miscalibrated confidence — before any
browser/mock budget is spent.

Verifier may **agree** or **downgrade**. Never escalate. Never invent
a new `drop` verdict (a verifier doesn't create FPs).

```bash
python3 bin/verdict_verifier.py --target <name> prepare
```

Writes `two_judge/_prompts/<chain_id>.md` for each eligible chain
(triage=runtime, confidence in {high, medium}) and a
`two_judge/_manifest.json`. Records skipped chains and their reason.

For each chain in the manifest, Claude dispatches a subagent:

```
Agent(
  subagent_type="general-purpose",
  description="cc-taint two-judge verifier <id>",
  prompt=<contents of two_judge/_prompts/<chain_id>.md>,
)
```

The verifier prompt
(`.claude/skills/cc-taint-adversarial/prompts/verifier.md`) embeds:

- The chain + expanded snippet (same evidence the auditor saw).
- The auditor's `exploit_argument`, `counterargument`,
  `blocking_unknowns`, `confidence`, `triage`.
- Reasons-first key ordering for the JSON response
  (`issues_found` + `reasoning` BEFORE `audit_quality` /
  recommended fields).

Subagent constraints (in the prompt body):

- Read-only. No file writes. No MCP mutations.
- Allowed: `Grep`, `Read`, `Glob` against `targets/<name>/sources/`,
  `wiki/`, `tlx/`. Allowed MCP: `mcp__tlx__docs_query` against
  `target_<name>`, `mcp__tlx__js_get_snippet`,
  `mcp__tlx__js_examine_chain`.
- Output JSON only matching the schema. No prose preamble.

Capture each response and ingest:

```bash
python3 bin/verdict_verifier.py --target <name> ingest \
    --chain-id <id> --response-file <temp_path>
```

Side effects on `audit_quality != agree`:

- Rewrite `opus/<chain_id>.json` `triage` + `confidence` to the
  verifier's recommendation. Old values stored under
  `_verifier_history[]`.
- Strip the chain from `findings/_queue_browser_confirm.jsonl` and
  `findings/_queue_mock_run.jsonl` if present (no-op if not yet
  queued — verifier should run BEFORE route in normal flow).
- If `recommended_triage == evidence_gap`, append the chain to
  `chains/_re_expand_queue.jsonl` with `reason: two_judge_downgrade`
  and the verifier's blocking_unknowns as `hint`.

Verifier ingest enforces:

- `audit_quality ∈ {agree, downgrade, flawed}`.
- Recommended values can only equal or downgrade the auditor's.
  Escalation attempts get clamped.
- `audit_quality=flawed` forces `recommended_confidence=low`.

Then roll up:

```bash
python3 bin/verdict_verifier.py --target <name> finalize
```

Prints `{total, by_audit_quality, downgrades, by_recommended_triage}`
and writes `status.json.phases.two_judge.final_summary`.

**Skip the verifier only when**: time-pressed, OR the engagement is
explicit "speed over precision". Default = always run.

### Step 5 — route

```bash
python3 bin/cc_taint_route.py --target <name>
```

Triggers the `cc-taint-route` flow: high/runtime → `browser-confirm`
queue, medium/runtime → `mock_run` queue, evidence_gap → re-expand loop
(retry cap 2), drop → FP archive. Route MUST run AFTER the two-judge
verifier; otherwise verified-downgraded chains stay on the browser
queue.

## Run modes

- **All chains** (default): every chain in `chains/dom_reachable.jsonl`.
- **Subset for verification:** `prepare --chain-ids 1,2,3` then dispatch
  only those.
- **Smoke target (`axinite-w005-syn`):** `dom_reachable.jsonl` is empty.
  Pass `--chains-input chains/hot.jsonl` to both `expand_snippet.py`,
  `bucket_anomaly.py`, and `cc_taint_runner.py prepare`.

## Outputs

- `targets/<name>/chains/expanded/<id>.json` — Phase 0 evidence bundles.
- `targets/<name>/chains/anomalies/<slug>.json` — Phase A divergence
  notes per sink-file bucket.
- `targets/<name>/opus/<chain_id>.json` — Phase B adversarial records.
  May contain `_verifier_history[]` if the two-judge verifier
  downgraded the verdict.
- `targets/<name>/two_judge/<chain_id>.json` — Phase 4.5 verifier
  records (per runtime/high + runtime/medium chain).
- `targets/<name>/status.json.phases.cc_taint_adversarial` — counters:
  `prompts_ready`, `subagent_count`, `by_triage`, `by_confidence`,
  `final_summary`.
- `targets/<name>/status.json.phases.two_judge` — counters:
  `prompts_ready`, `ingested`, `by_audit_quality`, `downgrades`,
  `final_summary`.

## Cost tracking

Subagent count is the only meter on a CC seat. Each
`cc_taint_runner.py ingest` increments
`phases.cc_taint_adversarial.subagent_count`. Compare against the
`opus_budget_per_target_usd` field in `memory.md` only as a rough
budgetary heuristic — the conversion factor is engagement-dependent.

## Failure modes

| Symptom | Action |
| --- | --- |
| Subagent emits prose instead of JSON | Re-issue the prompt once with `Output JSON only — do not prefix any commentary.` appended. If still bad, mark chain as `evidence_gap` and skip. |
| Subagent emits `verdict` / `tp` / `fp` keys | Runner strips them automatically and logs to `_stripped_keys`. No retry. |
| Snippet expansion missing for a chain | `cc_taint_runner.py prepare` records it under `missing_expanded`. Re-run `expand_snippet.py --chain-id <id>` after fixing the underlying cause. |
| Schema validation error | Logged to `status.json.errors`. Do not retry blindly; inspect the subagent output. |

## Result block

`status.json.phases.cc_taint_adversarial`:

```json
{
  "status": "prepared | ingesting | done",
  "ts": "...",
  "prompts_ready": N,
  "subagent_count": K,
  "counters": {
    "ingested": K,
    "by_triage":    {"runtime": ..., "evidence_gap": ..., "drop": ...},
    "by_confidence": {"high": ..., "medium": ..., "low": ...}
  },
  "final_summary": {"total": K, "by_triage": {...}, "by_confidence": {...}}
}
```
