# cc-taint-adversarial — Build Plan

> **Audience:** A fresh Claude Code session that has never seen this thread.
> Read this file end-to-end before touching code. Cross-reference
> `CLAUDE.md`, `skills.md`, `memory.md` for workspace rules.

## 1. What this is

A new TLX skill + supporting tooling that performs Claude-Code-driven taint
analysis on the per-target JS callgraph chains, **replacing the existing
`opus-deep-audit` flow for max-quality engagements**.

The existing pipeline (`js_run_audit` / `js_audit_status`) uses Sonnet as
primary auditor with optional Opus consult. It works, but Sonnet decides
~95% of chains. This new path runs full Opus reasoning per chain, with
better evidence and a tighter feedback loop into runtime confirmation.

## 2. Why we're building it

User priority: **quality over speed/cost.**

Status quo (`js_run_audit`):
- Sonnet primary → most verdicts not Opus-quality
- Single context, single pass → no cross-chain anomaly detection
- Hard to extend with adversarial / runtime feedback inline

Originally proposed: two Opus passes (bucketed + isolated) + reconcile
arbiter. **Rejected after external LLM critique** — two passes of the same
model don't give independent opinions; reconcile-as-arbiter manufactures
false certainty. Critique transcript was discussed in the originating
session; key takeaways now baked into the design below.

Lessons applied to current design:
1. **Evidence quality dominates reasoning depth.** Expand snippets before
   reasoning. A bigger / better-bounded snippet beats a second Opus pass.
2. **Sibling context is anomaly evidence, not a verdict input.** Bucketing
   stays, but only to surface "this function sanitizes, sibling doesn't"
   divergences. Not a vote.
3. **Adversarial prompting > naive double-pass.** One Opus subagent runs
   both attacker and skeptic roles in the same call. Prompt asymmetry
   buys variance that "ask again neutrally" does not.
4. **Runtime decides close calls.** Instead of arbitrating between two
   LLM verdicts, queue ambiguous chains into headless browser /
   `mock_run` confirmation earlier than the current pipeline does.
5. **No "forced verdict" arbiter.** Phase D from the original plan is
   deleted. Unresolveds go to runtime, then human queue. No synthetic
   certainty.

## 3. Architecture (4 active phases + queues)

```
chains/dom_reachable.jsonl  (from dom-xss-hunt)
        │
        ▼
[Phase 0] expand_snippet.py
        │   per chain: source fn + sink fn + 2-hop callers
        │   + dominator guards (if/try/role-check above sink)
        │   + framework lifecycle context (React useEffect, Vue setup, etc.)
        │   writes: chains/expanded/<chain_id>.json
        ▼
[Phase A] bucket_anomaly.py
        │   group chains by sink-file
        │   one CC subagent per bucket
        │   output: sibling_divergence, missing_guard_vs_peers,
        │           sanitizer_inconsistency  (NO TP/FP verdict)
        │   writes: chains/anomalies/<bucket>.json
        ▼
[Phase B] cc-taint-adversarial skill (per chain)
        │   one Opus subagent, two-role prompt:
        │     attacker → builds exploit sketch
        │     skeptic  → finds runtime block / counterargument
        │   inputs: expanded snippet + relevant anomalies + chain
        │   output: {exploit_argument, counterargument,
        │            blocking_unknowns[], confidence ∈ {high,med,low},
        │            triage ∈ {runtime, evidence_gap, drop}}
        │   writes: opus/<chain_id>.json
        ▼
[Phase C] triage routing
        │   confidence=high  + triage=runtime  → browser-confirm queue
        │   confidence=med   + triage=runtime  → mock_run queue
        │   triage=evidence_gap                → re-expand snippet loop
        │                                        (cap at 2 retries)
        │   triage=drop                        → FP archive
        │
        ▼
[Phase D] runtime validation
        │   browser-confirm (live) or mock_run (headless)
        │   resolves verdict via real DOM / network effects
        ▼
findings/<id>/confirmed.json  → report-finding skill
```

Anything still unresolved after Phase D → `opus/human_review.jsonl`.

## 4. Prerequisites — code vs verification

**To write the code (Steps 1-5 below): no target needed.** All four bin
scripts and the skill are target-agnostic. They take `--target <name>`
at invocation but the implementations only depend on file layout +
schema, not on real data being present. You can build and unit-test
with synthetic fixtures.

**To verify each step's gate: a test-bed target is required.** Each
verification command needs a target with the upstream pipeline
finished. Required artifacts in the test-bed dir:

| File / artifact | Produced by |
| --- | --- |
| File / artifact | Required? | Produced by |
| --- | --- | --- |
| `targets/<name>/status.json` | required | `target-init` |
| `targets/<name>/sources/` | required | `sourcemap-explode` |
| `targets/<name>/db/js_analyzer.db` (per-target snapshot) | required | `db-isolate snapshot` |
| `targets/<name>/index/{nodes,edges}.jsonl` | required | `js-index` + `export_index.py` |
| `targets/<name>/chains/dom_reachable.jsonl` | required | `dom-xss-hunt` |
| `targets/<name>/rag` chroma collection | **optional** (see below) | `rag-ingest` |

**On RAG vs CC native retrieval.** Earlier draft over-stated rag-ingest
as required. Correction: the subagent has two ways to pull framework /
technique context.

- **With rag-ingest:** subagent calls `mcp__tlx__docs_query` against the
  per-target chroma collection. Embedding-based semantic match.
  Necessary when the target ships **minified** bundles where variable
  names are mangled (`a`, `b`, `_0x4f2a`) and `Grep` is useless.
- **Without rag-ingest:** subagent uses CC native tools — `Grep` over
  `targets/<name>/sources/`, `Read` on wiki technique pages, `Glob` for
  file patterns. Works fine when sources are readable (sourcemaps gave
  us original code) and the technique question is keyword-shaped.

Decision rule per target:
1. If `targets/<name>/sources/` was produced by `sourcemap-explode` and
   contains real readable code → **rag-ingest optional**. CC native
   retrieval is sufficient.
2. If the target ships minified-only (no sourcemaps recovered) →
   **rag-ingest recommended**. Without it, the subagent will miss
   semantic patterns hidden behind mangled identifiers.

Either way, build the code first and decide rag-ingest per engagement.

**Picking a test-bed target.** As of writing, no target has the full
upstream pipeline complete. Two options:

1. **Smoke test only — use `axinite-w005-syn`** (db snapshot exists,
   4 chains in `hot.jsonl`, dom_reachable empty). Synack restriction
   means Phase D is mock-only via `mock_run`. Fine for plumbing,
   inadequate for accuracy validation.
2. **Real validation — build up a non-syn target first.** Pick a
   live-bountied target with an existing `http.md`, run the full
   upstream chain (`target-init → js-harvest → sourcemap-explode →
   rag-ingest → js-index → db-isolate → chain-triage →
   dom-xss-hunt`). Hours of work, but enables Phase D against live
   browser through Caido.

Recommend option 1 first (verify the new code doesn't crash), then
option 2 (verify accuracy on real chains).

## 5. Build steps

Tackle in order. Each step ends with a verification command — do not
proceed past a failed check.

### Step 1 — Snippet expander

**File:** `bin/expand_snippet.py`

**Scope:**
- Takes `(target, chain_id)` or stdin JSON.
- Reads `targets/<target>/db/js_analyzer.db` (per-target snapshot).
- Loads the source fn + sink fn nodes from the chain.
- Walks callers up to 2 hops via `edges` table; collects their source.
- Extracts dominator guards: walks the AST upward from sink, captures any
  `if (...)`, `try`, role-check function call, framework-specific guard
  (e.g. `if (isSafe)`). Use the qname tags in `nodes.tags`.
- Detects framework lifecycle: if source fn matches a React hook /
  Vue lifecycle / Angular handler, add a `framework_context` field.
- Writes `targets/<target>/chains/expanded/<chain_id>.json`:

```json
{
  "chain_id": "...",
  "source": {"qname": "...", "file": "...", "lines": [...], "code": "..."},
  "sink":   {"qname": "...", "file": "...", "lines": [...], "code": "..."},
  "callers": [
    {"qname": "...", "file": "...", "code": "...", "hop": 1},
    ...
  ],
  "dominator_guards": [
    {"kind": "if|try|fn_call", "expr": "...", "covers_sink": true|false}
  ],
  "framework_context": {"framework": "react", "lifecycle": "useEffect", ...} | null,
  "byte_budget": 12000
}
```

Soft cap output at ~12 KB; if a function body blows the budget, summarise
the bodies of intermediate callers (signature + first 5 lines) and keep
the source/sink/dominators full-fidelity.

**Verification:**
```bash
python3 bin/expand_snippet.py --target <known-good-target> --chain-id <id> | jq '.source.qname, .dominator_guards | length'
```
Expect: source qname matches `js_get_snippet`'s, ≥0 guards listed.

### Step 2 — Bucket anomaly detector

**File:** `bin/bucket_anomaly.py`

**Scope:**
- Reads `targets/<target>/chains/dom_reachable.jsonl`.
- Groups by `sink.file`. Buckets with only one chain are still processed
  (their "siblings" come from `nodes` table — all fns in the same file).
- Per bucket: dispatch ONE Claude Code subagent (use `Agent` tool,
  subagent_type=`general-purpose`).
- Subagent prompt (template at
  `.claude/skills/cc-taint-adversarial/prompts/bucket_anomaly.md`)
  loads the expanded snippets for all chains in the bucket + the file's
  full sibling-function list (signatures via `nodes`).
- Subagent returns JSON only:
```json
{
  "bucket": "src/components/X.tsx",
  "chains_seen": ["chain_id_a", ...],
  "anomalies": [
    {
      "type": "missing_guard_vs_peers" | "sanitizer_inconsistency" | "auth_gap" | "copy_paste_drift",
      "evidence": "fn foo() at line 42 calls sanitize() but sibling bar() at line 88 hits the same sink raw",
      "affected_chains": ["chain_id_b"]
    }
  ]
}
```
- Writes to `targets/<target>/chains/anomalies/<bucket-slug>.json`.

**Hard constraint:** anomaly subagent MUST NOT output verdicts. The
prompt should explicitly state "do not classify TP/FP, only describe
divergence." If the subagent slips into verdicts, drop them in
post-processing — the Phase B prompt should not see them anyway.

**Verification:**
```bash
python3 bin/bucket_anomaly.py --target <name> --dry-run
# inspect a sample anomaly file; ensure no verdict keys present
```

### Step 3 — Adversarial audit skill

**Dir:** `.claude/skills/cc-taint-adversarial/`

**Files:**
- `SKILL.md` — frontmatter `name`, `description`, trigger. Body explains
  the per-chain dispatch flow.
- `prompts/adversarial.md` — two-role prompt template. Skeleton:

```
You are auditing a JS taint chain for client-side XSS / CSPT.

EVIDENCE
--------
<expanded snippet JSON>

ANOMALY HINTS (auxiliary, not verdicts)
--------------------------------------
<matched anomalies for this chain, if any>

TASK
----
Play two roles. Do not summarize the chain — go straight to argument.

[ATTACKER]
Build the exploit sketch. Be concrete:
- the user-controlled value that flows in
- the exact transformation path
- the payload that would reach the sink without sanitization
- the trust boundary you're crossing

[SKEPTIC]
Find the reason this won't work in practice. Be concrete:
- runtime guards that block the payload
- framework escaping you assumed didn't apply
- missing evidence in the snippet that could change the verdict

OUTPUT (JSON only, no prose preamble)
{
  "exploit_argument": "...",
  "counterargument": "...",
  "blocking_unknowns": ["..."],
  "confidence": "high|medium|low",
  "triage": "runtime|evidence_gap|drop"
}
```

- `prompts/bucket_anomaly.md` — see Step 2.
- `runner.py` (or inline in skill body) — iterates
  `chains/dom_reachable.jsonl`, dispatches one subagent per chain via the
  `Agent` tool, persists `opus/<chain_id>.json`, appends progress to
  `status.json.phases.cc_taint_adversarial`.

**Hard constraint:** the subagent must be told it's read-only — no file
writes, no MCP mutations. Use `Agent` tool's read-only style. The runner
itself does the writes.

**Verification:**
- Pick 3 known-good chains from a past engagement.
- Run skill on those 3 only via `--chains <id1>,<id2>,<id3>` arg.
- Confirm each `opus/<id>.json` parses and contains all five required
  keys.

### Step 4 — Triage routing

**File:** `bin/cc_taint_route.py`

**Scope:**
- Reads `opus/*.json`.
- For each:
  - `triage=runtime` + `confidence=high` → append chain to
    `findings/_queue_browser_confirm.jsonl`
  - `triage=runtime` + `confidence=medium` → append to
    `findings/_queue_mock_run.jsonl`
  - `triage=evidence_gap` → re-queue into Phase 0 with a hint about what
    to expand (cap retries at 2; store retry count in
    `opus/<id>.json.retries`)
  - `triage=drop` → move chain to `chains/_fp_archive.jsonl`
- Idempotent: re-running shouldn't duplicate queue entries.

**Verification:**
```bash
python3 bin/cc_taint_route.py --target <name> --dry-run
# inspect queue files; ensure no chain appears twice
```

### Step 5 — Wiring to runtime skills

No new code — just confirm:
- `browser-confirm` skill picks up `findings/_queue_browser_confirm.jsonl`
  (may need a minor update to its trigger pattern).
- `mock_run` invocations via `mcp__tlx__mock_run` are reachable from the
  skill prompt in `browser-confirm`.

If `browser-confirm` doesn't read the new queue file, update its SKILL.md
to do so. Don't refactor it.

## 6. Verification checklist (end-to-end)

After all 5 steps, run on a single known-good target:

```bash
# Replace <name> with the target dir name
python3 bin/expand_snippet.py --target <name> --all
python3 bin/bucket_anomaly.py --target <name>
# Skill dispatched via Claude Code conversation, not a CLI call:
# in a CC session, run: /cc-taint-adversarial <name>
python3 bin/cc_taint_route.py --target <name>
# Then the existing browser-confirm skill processes the new queues.
```

Success criteria:
- `opus/` populated with one JSON per chain in `dom_reachable.jsonl`
- `findings/_queue_browser_confirm.jsonl` non-empty (if any high-conf TPs)
- No chain stuck in retry loop (retries ≤ 2)
- `status.json.phases.cc_taint_adversarial` reflects completion

## 7. Open questions / risks

1. **Snippet byte budget vs accuracy.** 12 KB might be tight for
   minified bundles where one function spans many lines. May need to
   raise to 24 KB or implement smarter elision. Decide after first
   real-target run.
2. **Subagent rate limits.** Dispatching N subagents in parallel may
   hit CC's concurrency cap. Start serial; parallelize only if step 3
   verification shows wall-clock is the bottleneck.
3. **Anomaly relevance ranking.** Phase A may produce many anomalies
   per bucket; Phase B prompt has limited room. Need a relevance score
   (overlap of `affected_chains` ∩ current chain) before pasting into
   the adversarial prompt.
4. **`framework_context` extraction depth.** First version can be
   regex/heuristic (`useEffect(`, `setup(`, `addEventListener(`). If
   that's too lossy, hook into `frameworks.json` per-target.
5. **Cost tracking.** No API meter on CC seat. Track Opus subagent
   count + estimated tokens per run in
   `status.json.phases.cc_taint_adversarial.subagent_count` so we can
   compare with budgeted `opus_budget_per_target_usd` (memory.md).
   Approximate, not exact.

## 8. Out of scope (do not build now)

- New symbolic-execution layer. Dominator-guard extraction is the
  ceiling for evidence quality in v1. Full constraint solving = months.
- A separate "judge" model. Avoid by design (the critique called this
  certainty-laundering).
- Replacing `js_run_audit`. Both pipelines coexist; pick per-engagement
  via memory.md / skill flag.
- Cross-target chain comparison. Per-target only.

## 9. Kickoff command for the new session

Paste this into the new CC session:

```
Read plans/CC_TAINT_ADVERSARIAL.md end-to-end. Then read CLAUDE.md, skills.md, memory.md. Start at Step 1 (bin/expand_snippet.py). Each step has a verification gate — do not skip past a failed check. The code is target-agnostic; you can develop without a target. For verification, the plan documents two test-bed options (smoke vs real validation). Pick smoke first to flush plumbing bugs, then escalate. Confirm with me before running the real-validation upstream pipeline — that takes hours and picks an engagement.
```

## 10. References

- Wiki technique: `wiki/techniques/recon/adjacent-function-gap.md`
- Existing pipeline: `tlx/modules/js_analyzer/claude_agent.py`,
  `exploit_agent.py`
- Existing skills consumed: `dom-xss-hunt`, `browser-confirm`,
  `rag-ingest`, `js-index`, `db-isolate`
- DB schema: `tlx/modules/js_analyzer/db.py`
- Memory rule on Opus vs Sonnet:
  `~/.claude/projects/-Users-soural-Documents-TLX/memory/feedback_opus_vs_sonnet.md`
- API-key whitelist (this skill complies — no new ANTHROPIC_API_KEY use):
  `~/.claude/projects/-Users-soural-Documents-TLX/memory/feedback_api_key_whitelist.md`
