# TLX Pipeline Upgrade — Tier 1, 2, 3 Implementation Brief

**Audience:** a fresh Claude Code session (or `/feature-dev` invocation) that has not seen the prior `/wiki-query` discussion. Self-contained — do not require the prior conversation.

**Goal:** ship 15 concrete additions to the TLX bug-bounty pipeline, ranked by impact/effort. The additions close gaps identified by comparing the current pipeline against state-of-the-art JS-review methodology from the Critical Thinking Podcast (Eps 81/96/111/121/128/137/138/149/170/172), Caleb Gross's "Slice", Justin Gardner's adjacent-function-gap workflow, BishopFox jsluice, Frans Rosén's tooling, and recent (2025-2026) HackerOne write-ups.

The 3 design rationale pages already live in the wiki:
- `wiki/tools/karpathy/js-review-cascade.md` — two-tier triage→analysis cascade
- `wiki/techniques/recon/adjacent-function-gap.md` — inverse-taint prompt + skill spec
- `wiki/tools/tlx/sourcemap-recon.md` — hidden-map + Sentry recon

Read those first. They are the spec; this brief is the build plan.

---

## Non-negotiable constraints

1. **API key whitelist** (per `memory/feedback_api_key_whitelist.md`). `ANTHROPIC_API_KEY` and Gemini chat models (`gemini-2.5-flash-lite`, any Gemini chat) are only allowed inside:
   - `tlx/modules/js_analyzer/*` (callgraph + chain audit + Opus consult)
   - `tlx/modules/rag/*` (Google text-embedding-004 for ingestion only)
   Everything else must run as Claude Code in the user's interactive session. If a step cannot be done from Claude Code, surface "can't do it" — do NOT add new code paths that call `anthropic.Anthropic`, `google.genai` chat, or `GeminiEngine` to fill the gap. Wiki RAG re-embedding via Gemini text-embedding-004 is grandfathered.

2. **Per-target DB isolation** (per project `CLAUDE.md`). All callgraph queries operate against `targets/<name>/db/js_analyzer.db`, not the global `~/.tlx/js_analyzer.db`. New skills must accept a per-target DB path or call `bin/extract_chains.py`-style fresh CallGraph instantiation.

3. **Scope.** Every new skill reads `targets/<name>/http.md` + `status.json` and refuses out-of-scope hosts. Synack `*-syn` targets are reference-only — skip all live actions.

4. **Opus budget.** Track every Sonnet/Opus call in `targets/<name>/status.json.opus_cost`. Hard-cap at `memory.md > opus_budget_per_target_usd`.

5. **Caveman doesn't apply to code, findings, wiki pages, commit messages, or this brief.** Write proper English in artifacts. Caveman is for chat updates only.

6. **No destructive HTTP** without explicit per-request approval. Read-only fuzz (GET/OPTIONS) and shadow-account fuzz allowed when scope permits.

7. **Recon cloud-init ASCII-only** (per `memory/feedback_recon_cloud_init_ascii.md`) — any new shell script rendered into cloud-init user-data must be pure ASCII.

---

## Reading list before coding

- `CLAUDE.md` (project)
- `memory.md`
- `PLAN.md`, `workflow.md`, `skills.md`
- `tlx/modules/js_analyzer/` (`claude_agent.py`, `callgraph.py`, `taint_engine.py`)
- `bin/extract_chains.py`, `bin/export_index.py`, `bin/db-isolate.py`, `bin/explode_sourcemap.py`, `bin/ingest-wiki.py`
- The three new wiki pages above
- `.claude/skills/opus-deep-audit/SKILL.md`, `.claude/skills/js-harvest/SKILL.md`, `.claude/skills/browser-confirm/SKILL.md`

Use `/graphify query` for any "how does X work" question instead of dumping whole modules into context.

---

## Tier 1 — high impact, low effort (build first)

### T1.1 — Adjacent-function gap audit mode

**What:** new skill `opus-gap-audit` (sibling to `opus-deep-audit`) that finds *missing* security controls instead of *existing* taint chains.

**Files to add/modify:**
- `.claude/skills/opus-gap-audit/SKILL.md` (new)
- `tlx/modules/js_analyzer/gap_analyzer.py` (new) — given a control qname, return all callsites + sibling functions that don't call it
- `bin/run_gap_audit.py` (new)
- Extend `tlx/modules/js_analyzer/claude_agent.py` with a `gap_audit_prompt()` builder using the killer prompt template from `wiki/techniques/recon/adjacent-function-gap.md`

**Inputs:** target name + control qname (e.g. `RequireRole`, `csrf.verify`, `DOMPurify.sanitize`). Sibling-selection heuristic: same `nodes.file`, same parent module, same React component boundary.

**Output:** `targets/<name>/chains/gap_<control_slug>.jsonl` + cascade-audited verdicts under `targets/<name>/opus/gap_<control>/<sibling_qname>.md`.

**Acceptance:**
- Skill runs end-to-end against an existing target with a known control (pick a target that has either a `RequireRole`-style decorator or a `DOMPurify.sanitize` callsite).
- Cascade-audits top 20 gaps via T1.2 (Sonnet → Opus), respects Opus budget.
- Output JSON schema documented in SKILL.md.

### T1.2 — Two-tier audit cascade

**What:** wire Sonnet primary as a *gate* (reject-if-FP), not just a primary judge. Only survivors reach Opus.

**Files:**
- `tlx/modules/js_analyzer/claude_agent.py` — add `sonnet_triage()` that returns `reject | escalate` with a rubric (rubric draft in `wiki/tools/karpathy/js-review-cascade.md` § "Cheap-stage rubric")
- `tlx/modules/js_analyzer/audit_pipeline.py` (new or extend existing) — orchestrate triage → consult
- `.claude/skills/opus-deep-audit/SKILL.md` — document new control flow

**Acceptance:**
- On a known-good test target, ≥80% of chains rejected by Sonnet match a previously-recorded FP in `targets/<name>/opus/`.
- Opus call count drops ≥5x vs current pipeline on the same chain set.
- Per-chain cost logged to `status.json.opus_cost`.

### T1.3 — Long-context fallback for small bundles

**What:** detection + branch in `opus-deep-audit` flow. If `targets/<name>/sources/` token count ≤ 800k (heuristic: total chars ÷ 4), skip `docs_query` retrieval and read the whole tree into the audit prompt directly.

**Files:**
- `tlx/modules/js_analyzer/audit_pipeline.py` — token budget helper
- `bin/source_token_count.py` (new)
- `.claude/skills/opus-deep-audit/SKILL.md` — document branch

**Constraint:** per API-key whitelist, this MUST be invoked from Claude Code conversation context (1M Claude window) — not a new Gemini code path. The branch logs "small-bundle mode" and emits a `whole_tree_prompt.md` artifact the user can paste into a Claude Code subagent if needed.

**Acceptance:**
- Auto-detects sub-800k targets.
- Emits artifact + a clear instruction line in the audit output: "long-context mode active; if you want to run the whole-bundle adjacent-gap pass, dispatch via `/feature-dev` with `<prompt>`."

### T1.4 — jsluice tag layer

**What:** run BishopFox `jsluice` (https://github.com/BishopFox/jsluice) against `targets/<name>/raw/` + `sources/` and merge URL skeletons + secret hits into the `js_analyzer.tags` table as an orthogonal axis.

**Files:**
- `bin/run_jsluice.py` (new) — wraps the jsluice binary, parses JSON output
- `tlx/modules/js_analyzer/tag_ingest.py` (new or extend) — write `jsluice_url`, `jsluice_secret` rows into per-target db
- `.claude/skills/js-index/SKILL.md` — append jsluice pass after callgraph build

**Output:** new tag rows queryable via existing `js_get_chains` filters; `targets/<name>/index/jsluice.jsonl` audit trail.

**Acceptance:**
- jsluice URL skeletons with `EXPR` placeholders surface as separate finding candidates in `chain-triage` (new score axis).
- Secret hits trigger a finding draft directly into `targets/<name>/findings/` with `kind: leaked_secret` for human review (no auto-submit).

### T1.5 — Sentry + hidden-sourcemap brute in `js-harvest`

**What:** extend harvest with brute-force of common Webpack/Vite hidden-map filenames and Sentry release-artifact API pulls.

**Files:**
- `.claude/skills/js-harvest/SKILL.md` — append phase
- `bin/sourcemap_recon.py` (new) — implements brute list from `wiki/tools/tlx/sourcemap-recon.md` and Sentry API client
- `bin/js-harvest` or its existing skill body — call the new phase after the standard sourceMappingURL pass

**Scope rules:** Sentry instances often live on subdomains of the primary target. The new phase MUST consult `targets/<name>/http.md` scope before querying any Sentry host. Out-of-scope = skip.

**Acceptance:**
- Brute list lifts at least one `.js.map` on a target where the standard pass found none (validate against a known target with `hidden-source-map` config).
- Sentry detection (DSN, `__SENTRY__` global) triggers artifact-API enumeration when Sentry host is in scope.
- Rate-limited: per-bundle attempt cap, 429 backoff.

---

## Tier 2 — high impact, medium effort

### T2.1 — DOMLogger++ auto-injection in `browser-confirm`

**What:** inject MatanBer's DOMLogger++ payload (or equivalent source+sink hook) before navigation, capture source/sink events passively while the user interacts.

**Files:**
- `bin/domlogger_payload.js` (new) — vendored or rewritten hook script for: `url.searchParams`, `window.location.href`, `history.pushState`, `postMessage`, `innerHTML`, `eval`, `setTimeout(string)`, `Function`, `document.write`
- `.claude/skills/browser-confirm/SKILL.md` — inject via chrome-devtools `evaluate_script` before any navigation
- `targets/<name>/findings/<id>/domlogger.jsonl` capture output

**Acceptance:** during a `browser-confirm` run on a known DOM-XSS chain, the log captures the source assignment and the sink call within 5s of triggering. Output queryable via `/snippet` for cross-reference with the static chain.

### T2.2 — CSPT-2-CSRF skill

**What:** scan `chains/dom_reachable.jsonl` for path-traversal sinks that land in `fetch`/`XHR` URLs; flag every cookie-authed mutation endpoint as a CSRF candidate per Doyensec's CSPT2CSRF playbook.

**Files:**
- `.claude/skills/cspt-csrf/SKILL.md` (new)
- `bin/cspt_csrf_scan.py` (new)
- `tlx/modules/js_analyzer/sink_taxonomy.py` — add `cspt` sink kind

**Acceptance:** produces `targets/<name>/chains/cspt_csrf.jsonl` with at least the LINE H1 #2473862-style chain shape captured. False-positive rate measured on one known target.

### T2.3 — Build-manifest extractor

**What:** parse `_buildManifest.js` (Next.js), `routes-manifest.json`, `rspack.client.json`, Vite `manifest.json` to enumerate all SPA routes including hidden admin paths. Feed routes back into `js-harvest` for re-crawl.

**Files:**
- `bin/build_manifest_extract.py` (new)
- `.claude/skills/js-index/SKILL.md` — append phase
- Output: `targets/<name>/index/routes.jsonl`

**Acceptance:** discovers ≥1 route beyond what the initial crawl found on a Next.js or Vite target.

### T2.4 — Inline-handler + `getEventListeners` enum

**What:** one-shot console probe injected during `browser-confirm` that enumerates inline event handlers and (when running in preview mode) `getEventListeners(window)` for postMessage handlers.

**Files:**
- `bin/eventlistener_enum.js` (new) — payload string
- `.claude/skills/browser-confirm/SKILL.md` — invoke after navigation

**Probe:**
```js
[...document.querySelectorAll('[onclick],[onerror],[onload],[onmouseover],[onfocus],[oninput]')]
  .map(e => ({ tag: e.tagName, attrs: [...e.attributes].map(a => [a.name, a.value]) }))
```

**Acceptance:** output appended to `findings/<id>/event_handlers.json`; cross-referenced with static-chain handler list to spot static-only or runtime-only handlers.

---

## Tier 3 — interesting, higher effort

### T3.1 — Patch-diffing skill

**What:** for libraries with version history (npm, git tags), diff a target version against the previous; flag added/removed security control invocations.

**Files:**
- `.claude/skills/patch-diff/SKILL.md` (new)
- `bin/npm_version_diff.py` (new)
- Output: `targets/<name>/diffs/<package>_<old>_<new>.md`

**Trigger:** matches a `package.json` entry to a known npm package; user runs `/patch-diff <package>`.

### T3.2 — DOM-clobbering AST automation (Hulk-style)

**What:** port Jack-fromeast's Hulk hook list + AST taint to `js_analyzer`. Specifically for webpack/rspack/vite/astro frameworks already represented in the 500-CVE Hulk corpus.

**Files:**
- `tlx/modules/js_analyzer/dom_clobbering.py` (new) — list of clobberable properties + AST hook list
- `bin/dom_clobbering_scan.py` (new)

**Pre-check:** before flagging a finding, grep public CVE/issue lists for the same framework version to avoid re-finding known bugs.

### T3.3 — Parser-pipeline local fuzzing (DOMPurify/parse5/JSXSS)

**What:** new skill `parser-pipeline-fuzz`. For targets using DOMPurify + dynamic HTML, build local pipeline (DOMPurify version pinned from bundle), fuzz inputs, and surface a single survivor to live test.

**Files:**
- `.claude/skills/parser-pipeline-fuzz/SKILL.md`
- `bin/parser_fuzz/` (directory with vendored pinned sanitizer versions)
- Output: `targets/<name>/fuzz/parser_pipeline.jsonl`

### T3.4 — Service-worker / cache-poison surface tagger

**What:** new `js_analyzer` tag: any chain endpoint reached by a function registered via `navigator.serviceWorker.register`. Persistent XSS surface.

**Files:**
- `tlx/modules/js_analyzer/sw_tagger.py`
- Extend `chain-triage` weights to upscore SW-endpoint chains

### T3.5 — Web Worker + Blob taint pattern

**What:** new `js_analyzer` proximity tag: presence of `new Worker(...)` + `new Blob([...], {type:'text/html'})` + `dataTransfer.setData(...)` within the same module. 2025 Chrome chain class.

**Files:**
- `tlx/modules/js_analyzer/worker_blob_tagger.py`

### T3.6 — Caido Shift Agents integration

**What:** replicate Shift Agents-style passive proxy passes inside the existing `caido-replay`/`caido-idor` flow. Wrap micro-agents for open-redirect, IDOR-by-id-rotation, and JS-asset map inside the Caido MCP wrapper at `bin/caido-mcp.py`.

**Files:**
- `bin/caido-mcp.py` extension (sub-tools)
- `.claude/skills/caido-shift/SKILL.md` (new)

---

## Build sequence and dependencies

```
T1.2 cascade           → must land before T1.1 (gap audit uses it)
                       → must land before T1.3 (long-context audit reuses cascade rubric)
T1.4 jsluice           → independent
T1.5 sourcemap-recon   → independent; landing first improves all downstream T1.x audit quality
T2.1 DOMLogger         → independent
T2.2 cspt-csrf         → depends on T1.4 (jsluice URL skeletons feed CSPT candidate generation)
T2.3 build-manifest    → independent
T2.4 handler enum      → can ship with T2.1 (same skill body)
T3.x                   → independent of each other; pick by target need
```

Recommended order: **T1.5 → T1.2 → T1.1 → T1.3 → T1.4 → T2.3 → T2.1 → T2.4 → T2.2 → T3.x by need.**

Use the `superpowers:writing-plans` skill to draft a per-tier plan and `superpowers:executing-plans` to run it with review checkpoints. Use `superpowers:test-driven-development` for each module. Use `superpowers:dispatching-parallel-agents` for the independent items (T1.4, T1.5, T2.3 can all run in parallel agents during T1).

---

## Test plan

Set up two test targets:

1. **`targets/_test-hidden-map/`** — vendored OSS app with `devtool: 'hidden-source-map'` (e.g. a small Next.js demo) for T1.5 validation.
2. **`targets/_test-cascade/`** — existing target with ≥50 hot chains and known FP set under `opus/` for T1.2 + T1.1 validation.

Per skill, verify:
- Acceptance criteria above.
- `targets/<name>/status.json` updated.
- Costs tracked in `status.json.opus_cost`.
- No out-of-scope HTTP issued (audit `caido` history for unexpected hosts).
- No autonomous AI calls outside the API-key whitelist (`grep -rn "anthropic.Anthropic\|google.genai\|GeminiEngine" tlx/ bin/` should not show new hits outside the whitelisted modules).

For each tier, before merging:
- Run `wiki-lint` — surface any new dangling links from skill docs.
- Run `/graphify <path> --update` on the changed `tlx/` modules.
- Run `superpowers:verification-before-completion` checklist.

---

## Out of scope for this brief

- Replacing the existing `mock_backend` confirmation layer (still serves its purpose).
- Migrating from Chroma to another vector store.
- Adding new authentication tooling.
- Rewriting Caido MCP from scratch (only T3.6 extends it).

---

## When done

1. Append session learnings to `memory.md` under a new "Pipeline upgrades 2026-05-15" section, with key absolute dates.
2. Update `PLAN.md` and `skills.md` to reference the new skills and their place in the workflow.
3. Run `wiki-ingest` on any new technique discovered during implementation.
4. Surface a one-screen summary to the user with the diff of pipeline behavior (before/after) on the test targets.
