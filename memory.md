# Memory — Auto-Loaded Session State

This file is read by Claude Code at the start of every session for this
workspace. Keep it short — long memory files are noise. Append new
durable facts; remove stale ones.

> Personal **technique/tool knowledge** belongs in `wiki/`, not here.
> Engagement-specific intermediate state belongs in
> `targets/<name>/status.json`, not here. Memory is for *workflow
> preferences, budgets, and cross-session pointers*.

---

## User profile

- **Identity:** soural1417@gmail.com. Full-time bug hunter.
- **Standing:** HackerOne ~rank 2500; Synack L4.
- **Trained:** Anthropic Skilljar courses (familiar with skills,
  subagents, MCP, prompt caching).
- **Working style:** results > speed; "late but right" > "fast but
  wrong". Welcomes long-running pipelines if they materially raise TP
  rate.

## Workflow preferences

- **Default browser MCP for live targets:** `chrome-devtools` (real
  Chrome through Caido proxy).
- **Default browser MCP for mock confirmation:** `playwright`.
- **Default Caido mode:** proxy capture + GraphQL replay (both).
- **Caveman intensity:** `full` for chat updates; OFF for artifacts
  (findings, reports, wiki, commits — write proper English).
- **Skill discoverability:** load all skills at boot via
  progressive disclosure; never bulk-inject bodies.

## Budgets (defaults — override per target in `status.json`)

- `opus_budget_per_target_usd`: 25
- `opus_max_chains_per_target`: 30
- `caido_replay_budget_per_target`: 5000 requests
- `autoresearch_default_minutes`: 60
- `autoresearch_iter_max_minutes`: 5 (per Karpathy spec)

## Cross-session pointers

- **Current target:** coralbug3-syn (full pipeline run 2026-05-13; 0 TP, 1 undetermined surface — Angular [innerHTML] bindings flagged for live retest if access becomes available).
- **Last touched target:** coralbug3-syn.
- **Wiki last linted:** _never_.
- **Wiki people/ bulk ingest:** 2026-05-15 — 56 dossiers + PSW Top 10 index written by 47 parallel agents (CT podcast hosts + guests Ep 1-174 + PortSwigger researchers). See `wiki/people/_index.md`.

## Long-running learnings (cross-target)

_(Append items here only when they are workflow-relevant, not
technique-relevant. Technique items go to `wiki/techniques/`.)_

### Pipeline upgrades 2026-05-15 (IMPL_TIER123.md)

15 additions land per [IMPL_TIER123.md](IMPL_TIER123.md). Build order
followed brief recommendation: T1.5 → T1.4 → T1.2 → T1.1 → T1.3 → T2.x → T3.x.

- **T1.2 cascade gate** is the cost-saver — every `opus-deep-audit` run
  now passes through `bin/run_cascade.py` first. Sonnet triage cost
  lives in `status.json.cascade_cost_usd` (separate from
  `opus_cost_usd`). Target: ≥5x Opus call drop on identical chain set.
- **T1.1 gap audit** (`opus-gap-audit` skill, `bin/run_gap_audit.py`,
  `tlx/modules/js_analyzer/gap_analyzer.py`). Per-control sibling
  enumeration. De-duped by fn_gap by default to keep Opus budget tight
  (`--no-dedupe` for full evidence matrix).
- **T1.3 long-context probe** (`bin/source_token_count.py`). For
  bundles ≤ 800k tokens, writes `opus/whole_tree_prompt.md` for
  manual `/feature-dev` long-context dispatch. Per API-key whitelist,
  the long-context audit runs as Claude Code, not autonomous AI.
- **T1.4 jsluice tag layer** (`bin/run_jsluice.py`). Requires
  `jsluice` binary; degrades with `status: skipped` if missing. Tags
  go into `node_tags` with `source='jsluice'`; secrets draft into
  `findings/jsluice_secret_<id>/draft.json` (no auto-submit).
- **T1.5 sourcemap-recon** (`bin/sourcemap_recon.py`). Brute-force
  hidden-map filenames + Sentry release-artifact API per
  [wiki/tools/tlx/sourcemap-recon.md](wiki/tools/tlx/sourcemap-recon.md).
  Always honours scope (`status.json.scope.in`).
- **T2.1 + T2.4 browser-confirm extensions** (`bin/domlogger_payload.js`,
  `bin/eventlistener_enum.js`). Inject via `evaluate_script`; output
  to `findings/<id>/{domlogger.jsonl,event_handlers.json}`.
- **T2.2 cspt-csrf** (`bin/cspt_csrf_scan.py` + `extra_cspt.json`
  taxonomy). Surfaces fetch/XHR/axios URL constructions with
  path-traversal markers as CSRF candidates per Doyensec playbook.
- **T2.3 build-manifest** (`bin/build_manifest_extract.py`). Parses
  Next/Vite/Rspack/CRA manifests under `raw/` to surface hidden
  routes; output goes to `index/routes.jsonl`.
- **T3.1 patch-diff** (`bin/npm_version_diff.py`). Runs `npm pack`
  for two versions, diffs control-call counts. Tarballs extract via
  `filter='data'` (Python 3.12+) to block traversal.
- **T3.2/T3.4/T3.5 surface taxonomies**
  (`taxonomies/extra_runtime_surfaces.json`). Service-worker, blob
  worker, dom-clobbering regex sinks added — auto-loaded by
  `taxonomy.load_default()`.
- **T3.3 + T3.6 stubs**: `parser-pipeline-fuzz` + `caido-shift` SKILL.md
  scaffolds with explicit Implementation TODO sections. Build per
  target need.
- **`bin/_lib.py`** is the new shared module: `status_lock`,
  `write_status_phase`, `append_status_error`, `read_scope`,
  `host_in_scope` (port-stripped), `pick_chain_input`,
  `resolve_target_dir`, `per_target_db`, `tlx_sys_path`. All new
  bin scripts go through it. Existing bin scripts can migrate
  opportunistically.
- **API-key whitelist preserved** — only
  `tlx/modules/js_analyzer/claude_agent.py` (new
  `sonnet_triage()`) calls Anthropic. No new bin/ script imports
  `anthropic` or `google.genai`.

## Failure-mode reminders

- If `js-index` reports zero nodes but `sources/` has files, it almost
  always means TLX didn't recognize the framework. Set
  `kv_set("target_<name>:framework_override", "<react|vue|angular|svelte|next|nuxt|vanilla>")`
  and re-index.
- If Caido proxy refuses connection, GUI must be open and API enabled
  in settings → other → API.
- If the embedder errors with `PERMISSION_DENIED`, the `GOOGLE_API_KEY`
  env var is unset or the key lacks Generative Language API. Fix
  before any `rag-ingest`.

## Don't-do list (sticky rules from past course corrections)

- Don't run `js-harvest` against an out-of-scope host even if the user
  asks; surface the conflict and demand scope edit in `http.md` first.
- Don't write Opus transcripts into the wiki — they go in
  `targets/<name>/opus/`. Wiki is for distilled patterns, not raw
  audit chatter.
- Don't auto-submit findings to HackerOne / Synack. Submission is
  always a human step.
- Don't auto-invoke `ANTHROPIC_API_KEY` or Gemini chat models
  (`gemini-2.5-flash-lite` etc.) outside the two whitelisted paths
  in `CLAUDE.md` rule 7: (1) `js_analyzer` callgraph/chain audit,
  (2) JS source RAG ingestion. Wiki distillation, autoresearch
  orchestration, prose synthesis, summarization — all run as
  Claude Code in this conversation. If a task can't be done from
  Claude Code, say "can't do it" and stop. Never add a Python
  shim that calls `anthropic.Anthropic` to fill a gap.

---

> Append to this file whenever (a) the user states a workflow preference,
> (b) a budget number is hit and adjusted, (c) a target's phase changes
> meaningfully. Don't append technical findings or per-target intel.
