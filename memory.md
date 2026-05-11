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

- **Current target:** _none_ (update when starting a target).
- **Last touched target:** _none_.
- **Wiki last linted:** _never_.

## Long-running learnings (cross-target)

_(Append items here only when they are workflow-relevant, not
technique-relevant. Technique items go to `wiki/techniques/`.)_

- (none yet)

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

---

> Append to this file whenever (a) the user states a workflow preference,
> (b) a budget number is hit and adjusted, (c) a target's phase changes
> meaningfully. Don't append technical findings or per-target intel.
