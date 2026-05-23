# TLX Bug-Bounty Workspace — Claude Code Instructions

You are the operator of a single-user bug-bounty cockpit. The user is a top
H1 hunter (rank ~2500) and Synack L4. They expect **rigor over speed**;
"late but right" beats "fast but wrong". Optimize for result quality.

> **Read `plans/PLAN.md` first.** Then `skills.md`, then `workflow.md`. Then start. All design/spec docs live under `plans/`.
n
---

## What this folder is

A self-contained workspace that wraps a vendored subset of TLX
(`./tlx/`) with skills, per-target working directories, and a personal
LLM-maintained wiki. Every bug-bounty engagement is a subfolder of
`targets/<name>/`.

## What you do

1. When the user starts work on a target, look for `targets/<name>/http.md`.
   If missing, ask the user to create it (template in
   `.claude/skills/target-init/SKILL.md`).
2. Run the skill chain in `workflow.md` end-to-end OR jump to a single
   skill the user names.
3. Confirm chains dynamically through the browser MCP (real target) or
   `mock_start` + browser MCP (sandbox). Capture replay traffic through
   Caido.
4. Persist verdicts to `targets/<name>/findings/` and update the wiki
   via `wiki-ingest`.
5. When you learn anything generalisable (new technique, target quirk,
   tool gotcha), update the wiki — do not just answer and forget.

## MCP servers (pre-wired in `.claude/settings.json`)

| MCP | Purpose | Used by skills |
| --- | --- | --- |
| `tlx` | js_analyzer + mock_backend + docs_query + session_kv_get (16 tools) | js-index, chain-triage, dom-xss-hunt, browser-confirm, rag-ingest, wiki-* |
| `chrome-devtools` | real Chrome via DevTools protocol — live target + mock_backend confirmation. Carries installed Chrome extensions (DOMLogger++, Caido browser, Wappalyzer, etc.) into every run | browser-confirm (live + mock), caido-capture |
| `playwright` | deprecated for this workflow — kept enabled but no skill calls it | _none_ |
| `caido` | proxy capture + GraphQL replay/diff (local wrapper at `bin/caido-mcp.py`) | caido-capture, caido-replay, caido-idor |

If `tlx` MCP fails to boot, run `cd tlx && python -m mcp_server` once
manually to surface the error. Common causes: missing
`GOOGLE_API_KEY` for embedder, missing `~/.tlx/` writable dir, Python
version <3.11.

## Hard rules — never violate

1. **Scope.** A target's `http.md` defines in-scope hosts. Never send any
   request — automated or manual — to a host outside scope. Caido
   project scope rules are the second line of defense; respect the first
   (the markdown) above all.
2. **Auth secrets.** Auth creds in `http.md` may reference Caido
   workflow IDs or env vars. Never write the raw secret value into any
   file in `targets/` or `wiki/`. Reference only.
3. **Destructive HTTP.** Never send DELETE / PUT / POST that mutates
   production state without explicit per-request user confirmation.
   Read-only fuzz (GET, OPTIONS) and shadow-account fuzz are allowed
   without per-request approval if the program's scope permits.
4. **Wiki edits.** Wiki pages are append-and-cross-link; never delete a
   wiki page without user OK. Lint suggestions go to a report, not to
   auto-deletion.
5. **Opus budget.** `opus-deep-audit` is expensive. Cap at the value in
   `memory.md > opus_budget_per_target` per engagement. Track cost in
   `targets/<name>/status.json.opus_cost`.
6. **Caveman doesn't apply to artifacts.** Findings, reports, wiki
   pages, commit messages — write proper English. Caveman is for chat
   updates back to the user only.
7. **External API keys — restricted whitelist.** `ANTHROPIC_API_KEY`
   and Google Gemini API keys (`GOOGLE_API_KEY`, especially anything
   using `gemini-2.5-flash-lite` or other Gemini chat models) may
   ONLY be auto-used by these two code paths:
   - **Callgraph analysis / chain audit** — `tlx/modules/js_analyzer/*`
     (`claude_agent.py`, `exploit_agent.py`, `js_run_audit`,
     `js_audit_status`, `js_consult_opus`). Uses `ANTHROPIC_API_KEY`.
   - **JS source ingestion** — `tlx/modules/rag/` calls that embed
     `targets/<name>/sources/` (post-`sourcemap-explode`) into the
     per-target Chroma collection. Uses `GOOGLE_API_KEY` for
     `gemini-embedding-001`.

   Everything else — wiki ingestion/distillation, autoresearch loop
   orchestration, hypothesis generation, judging, prose synthesis,
   compaction, summarization — runs as **Claude Code (this
   conversation)**. If a task cannot be done from Claude Code, say
   "can't do it" and stop. Do NOT add new code paths or skills that
   invoke `anthropic.Anthropic`, `google.genai` chat models, or
   `GeminiEngine`/Flash-Lite to fill the gap. Existing whitelisted
   paths are the only exception.

   The wiki RAG `wiki` collection (3072d Gemini embeddings) is
   grandfathered — re-embedding on update is allowed because the
   collection is already provisioned and the cost is per-write only.
   But do NOT add new pipelines that bulk-embed external corpora
   into `wiki` without user OK per ingest.

## 2026-05-23 additions

Skills added in the [plans/IMPLEMENTATION_2026-05-23.md](plans/IMPLEMENTATION_2026-05-23.md) batch:

- **tlx-investigate** — Clue-pattern NL investigation per target. Plan
  → execute → cite → recommend. Output under
  `targets/<name>/investigations/<utc>/`.
- **wiki-dream** — Offline curator. Walks recent tail data, distills
  candidate wiki patches into `wiki-staging/<utc>/`. Non-destructive.
  Manual promote.
- **mythos-read** — Full-source-tree audit. Only viable when sources
  ≤5 MB (default cap). Hypotheses emitted as
  `chains/_mythos_synthetic.jsonl`.
- **per-finding-session** — Fan-out browser-confirm queue draining.
  One subagent per finding, capped at 3 parallel.

cc-taint-adversarial now has a Step 4.5 — the **two-judge verifier**.
Every chain the auditor flagged `runtime` + `high|medium` gets a
second-opinion subagent that may agree or downgrade (never escalate).
On downgrade, the chain is rewritten + stripped from runtime queues
and re-queued to `_re_expand_queue.jsonl`. Drives FP-rate down before
browser-confirm budget gets spent.

browser-confirm + report-finding now emit a **DOM verification
contract** (`data-verify-*` attributes + `bin/poc_verify_contract.js`
reader). Deterministic verification of exploit firing, replaces the
older screenshot+LLM-judge pattern.

**Eval set:** `evals/chain_audit/{control,edge,boundary}.jsonl` +
`bin/run_chain_eval.py`. Buckets are empty by design — populate from
real audited engagements. Re-run after any cc-taint logic change.

**Audit tools** (advisory only): `bin/cache_audit.py` for prompt-cache
hygiene; `bin/skill_hygiene_audit.py` for stale-instruction +
description-shape checks.

**Billing rule (post 2026-06-15):** only *interactive* Claude Code in
terminal/desktop/web draws from your Max subscription. Headless
`claude -p`, Agent SDK, and scheduled / routine sessions draw from a
separate $200/mo Agent SDK credit pool (on Max 20x). Do not migrate
the autoresearch loop to headless or CMA without checking spend
projections — see `plans/IMPLEMENTATION_2026-05-23.md` for the math.

## Skill discipline

- Trigger by phase per `skills.md`. Don't skip phases unless the user says
  so.
- Each skill returns a structured result block; skill bodies define the
  shape. Append every result to `targets/<name>/status.json` under that
  skill's key. This is how Claude resumes a half-done target on a new
  session.
- If a skill prompt says "ask Opus", that means use the TLX advisor flow
  (`js_run_audit` triggers it internally; for off-pipeline questions use
  `js_examine_chain` first then route through the same advisor — there
  is no direct Opus-call skill at the surface).

## Per-target DB isolation (REQUIRED)

The TLX js_analyzer SQLite at `~/.tlx/js_analyzer.db` and the chroma store
at `~/.tlx/chroma/` are *global* — without isolation, every target's
nodes/edges/tags/chains pile up in the same tables and contaminate
`js_get_chains`, `js_run_audit`, and `docs_query` for the active target.

Required workflow on every target after `js-index` + `rag-ingest` complete:

1. **Snapshot to per-target DB files.** Identify the in-scope host
   prefix(es) for the target (e.g. `eu1.dev.ict.dematic.dev/`). Run:
   ```
   python3 bin/db-isolate.py snapshot targets/<name> <host-prefix-1> [<host-prefix-2> ...]
   ```
   This copies `~/.tlx/js_analyzer.db` → `targets/<name>/db/js_analyzer.db`
   then deletes every row whose `nodes.file` does NOT start with one of the
   given host prefixes. It also copies the chroma collection
   `target_<name>` (segment dirs + filtered `chroma.sqlite3`) into
   `targets/<name>/db/chroma/`. The global DBs are not modified.

2. **Re-export the index from the snapshot:**
   ```
   python3 bin/export_index.py <name> targets/<name>/index \
       --frameworks '[...]' --db targets/<name>/db/js_analyzer.db
   ```
   The default `--db` reads the global DB and will contain other targets'
   data — always pass `--db <per-target-snapshot>`.

3. **Run chain extraction against the snapshot, not via `js_get_chains`:**
   ```
   python3 bin/extract_chains.py targets/<name>
   ```
   `js_get_chains` is bound to the global MCP-loaded CallGraph and returns
   chains from every target ever indexed. `bin/extract_chains.py`
   instantiates a fresh CallGraph against the per-target snapshot.

4. Never run `db-isolate.py wipe-foreign` or `wipe-target` against the
   global `~/.tlx/js_analyzer.db` without explicit user confirmation —
   those subcommands destroy other engagements' analysis data.

## Failure handling

- Tool errors: log to `targets/<name>/status.json.errors[]`, surface to
  user with the exact error text. Do not silently retry.
- Stuck chain: mark as `verdict: undetermined` with a reason; move on.
  Stuck chains are revisited by `autoresearch-loop`.
- MCP transport drop: restart the affected MCP via the suggested command
  in `skills.md > troubleshooting`. Don't fall back to manual HTTP.

## Memory protocol

`memory.md` (next to this file) is the only auto-loaded memory file. It
holds: user profile, budgets, current target pointer, recent
session-spanning learnings. Update it whenever:

- The user states a preference about workflow.
- A budget number is hit and adjusted.
- A target's pipeline phase changes (so next session knows where to
  resume).

The personal global memory at `~/.claude/projects/-Users-soural-...` is
separate. Per-project knowledge that's *general* (technique, gotcha,
tool quirk) goes in the **wiki**, not memory.md.

## Graphify — codebase context retrieval

`graphify-out/` holds a knowledge graph of this repo (tlx/, wiki/, skills,
bin/). Built with [safishamsi/graphify](https://github.com/safishamsi/graphify).
`.graphifyignore` excludes `targets/*/raw|sources|index|chains|opus|caido/`
so target downloads (HTML/CSS/JS) never enter the graph.

**Use the graph instead of dumping whole files.** Tools have grown large;
reading entire modules into context wastes tokens and triggers
hallucination. Default to retrieval-mode:

1. For any "how does X work / where is Y / what calls Z" question about
   tlx, skills, or wiki internals — first run:
   ```
   /graphify query "<question>" --budget 1500
   ```
   Use BFS for broad context, `--dfs` for tracing a specific path.
2. For a named symbol/concept — `/graphify explain "<name>"`.
3. For dependency chains between two concepts — `/graphify path "<A>" "<B>"`.
4. Only `Read` a specific file (with `offset`/`limit` on the relevant
   lines) AFTER the graph points you to it. Never blanket-read a tlx
   module to "see what's there".
5. After code changes in tlx/ or skills/, run `/graphify <path> --update`
   so the graph stays current. Code-only changes skip the LLM step.

Exception: target work (`targets/<name>/`) bypasses graphify and uses
the TLX MCP (`js_analyzer`, `docs_query`, `session_kv_get`) — that data
is intentionally outside the graph.

## When you're unsure

Read PLAN.md again. Then skills.md. Then ask the user *one* tight
question with concrete options. Don't paraphrase; cite the section.
