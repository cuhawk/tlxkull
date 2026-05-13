# Pipeline Performance Optimizations — Implementation Prompt

You are picking up a planning conversation from a previous session. The user
wants to speed up three pipeline phases in this TLX bug-bounty workspace:
`rag-ingest`, `wiki-ingest`, and `js-index`. They also want to reduce
Claude Code session-limit burn during long engagements.

**Read first:** `PLAN.md`, `CLAUDE.md`, `skills.md`, `memory.md`.

**Hard rule reminder (CLAUDE.md):** `ANTHROPIC_API_KEY` and Gemini chat
models may only be used by `tlx/modules/js_analyzer/*` (audit) and
`tlx/modules/rag/` (ingestion). Do NOT add new code paths that invoke
those APIs to "fill the gap". Everything else runs as Claude Code.

---

## 1. rag-ingest — concurrent embedder calls + multi-key rotation

**File:** `bin/rag_ingest.py` (helper invoked by the rag-ingest skill).

**Current bottleneck:** Single GOOGLE_API_KEY, sequential embedder calls
into `gemini-embedding-001` / `text-embedding-004`. ChromaDB writer is
single-threaded.

**Change A — async concurrent embed:**
- Refactor file walk → batch → embedder call to use `asyncio.gather`
  with a semaphore (default N=8).
- Each worker calls the embedder independently; results pushed into a
  single Chroma writer (Chroma collection writes must stay serialized).
- Tunable via env: `TLX_RAG_CONCURRENCY` (default 8).
- Expected speedup: 5–10x on embedder phase.

**Change B — multi-key rotation:**
- Read `GOOGLE_API_KEY_1`, `GOOGLE_API_KEY_2`, ... (or comma-separated
  `GOOGLE_API_KEYS`) from env.
- Each must belong to a **distinct GCP project** with Generative
  Language API enabled — same project = same quota bucket = no win.
- Round-robin worker → key. Use a thread-local client per key.
- Cache key for dedup must be **content-hash**, not per-key, so workers
  don't re-embed the same chunk.
- Falls back cleanly to single `GOOGLE_API_KEY` when only one set.
- Expected additional speedup: linear in number of distinct projects,
  capped by Chroma writer throughput (diminishing returns past 4–5).

**Skill update:** Append to `.claude/skills/rag-ingest/SKILL.md` a note
about the new env vars and concurrency knob.

**Verify:**
- Run on a target with ~2000 source files, confirm chunk count matches
  the prior single-key run.
- `docs_query(collection="target_<name>", query="...")` returns the
  same top hits as before.

---

## 2. js-index — process-pool parallel AST extraction

**Files:**
- `tlx/modules/js_analyzer/ast_bridge.py` (AST extract + deobfuscate)
- `tlx/modules/js_analyzer/callgraph.py` (SQLite writer)
- `tlx/modules/js_analyzer/module.py` (orchestration in
  `_index_target_payload`)

**Profile of current pipeline:**

| Phase | Cost | Current behavior |
|-------|------|------------------|
| walk + sha256 | tiny | single thread |
| framework_detect | small | single thread |
| AST extract (Babel via Node) | **largest** | sequential batches of 100 |
| deobfuscate (webcrack) | large (if on) | one file at a time |
| index_batch (SQLite writes) | medium | single writer |
| interprocedural taint | medium | pure Python |

**Change A — parallel AST extract (biggest win):**
- In `ast_bridge.py:extract()` (around line 140), the `for i in range(0, len(candidates), AST_BATCH_SIZE)`
  loop calls `_run_batch` sequentially. Each batch invokes a Node
  subprocess and is fully independent — no shared state.
- Replace with `concurrent.futures.ProcessPoolExecutor` (or
  `ThreadPoolExecutor`, since subprocess calls release the GIL).
- `max_workers = os.cpu_count()`; cap via env `TLX_JS_INDEX_WORKERS`.
- Consider lowering `AST_BATCH_SIZE` from 100 → 50 so load balances
  better across workers.
- Expected speedup: ~Nx on AST phase (5k JS files ~3min → ~30s on
  8 cores).

**Change B — parallel deobfuscate:**
- In `ast_bridge.py:_deobfuscate_batch()` (around line 205), the
  `for i, entry in enumerate(candidates)` loop spawns one webcrack
  subprocess per file sequentially.
- Convert to ProcessPool/ThreadPool with same worker cap.
- Webcrack is CPU-bound V8 isolate; process pool scales linearly with
  cores.

**Change C — SQLite WAL mode:**
- In `callgraph.py` Callgraph init, add
  `self.conn.execute("PRAGMA journal_mode=WAL")`.
- Improves concurrent reads during indexing. Writers stay serialized
  by design.

**Change D — producer/consumer for index_batch (optional, only if
profiling shows SQLite is the new bottleneck after A+B):**
- Parallel AST workers push results to an `asyncio.Queue` /
  `multiprocessing.Queue`.
- Single consumer drains and calls `cg.index_batch` on chunks.
- Keeps writer serialized while overlapping parse + write.

**Do not parallelize:**
- `interprocedural_taint` — pure Python graph walk, requires bigger
  rework. Skip unless a future profile shows it hot.

**Multi-agent (Task subagents)?** No. js-index makes zero LLM calls.
It is Node + SQLite + Python. Use `concurrent.futures`, not subagents.

**Verify:**
- After parallel changes, re-index a target with a known prior result;
  compare `nodes`, `edges`, `tags` counts in `status.json.phases.index`.
  Must match (deterministic).
- Confirm no SQLite "database is locked" errors in logs.

---

## 3. wiki-ingest — optional map/reduce batch mode

**Caveat:** Only worth it for **batch ingest of ≥5 sources at once**.
Single-source ingest stays as-is.

**New skill (do not modify existing wiki-ingest):**
`.claude/skills/wiki-ingest-batch/SKILL.md`

**Pattern:**
1. **Map phase** — dispatch N general-purpose subagents (via Task),
   each handles one source file (`findings/<id>/<id>.md` or
   `opus/<chain_id>.md`). Each subagent returns a structured page-diff
   JSON, *no file writes*. Parallel-safe because nothing touches disk.
2. **Reduce phase** — main agent merges all diffs sequentially:
   - Deduplicate page touches (multiple sources touching
     `techniques/dom-xss/postmessage.md` collapse into one merged
     append).
   - Resolve cross-link references.
   - Write all pages.
   - Single re-embed pass over the wiki RAG collection.

**Why this shape:** Wiki pages overlap. Two parallel writers on the
same `techniques/<sink>.md` page would race. Map/reduce avoids
write conflicts and keeps the re-embed pass cheap.

**Cost note:** Subagents are full Claude Code conversations under the
hood. Each one consumes context. Worth it only for batch ≥5 sources;
otherwise the orchestration overhead outweighs the parallelism gain.

**Skill body should include:**
- Trigger: user says "ingest these N sources" or
  `findings/` + `opus/` together exceed a threshold (e.g. 5).
- Inputs: list of source paths.
- Output: standard wiki-ingest result block per source, plus a batch
  summary.

---

## 4. Claude Code session-limit burn — reduce context consumption

**Background:** Prompt caching is already auto-enabled in Claude Code
(Anthropic SDK marks system prompt + tool defs + conv history with
`cache_control`). 5-min TTL, refreshed each turn. Cache reduces billing
~10x but does not shrink context window.

**Where the burn actually comes from in this workspace:**
1. Reading huge tool outputs into main conversation (full file reads,
   `js_get_chains` dumps).
2. Long-running loops where each turn re-reads the conversation.
3. Sub-5-min idle gaps that drop the cache mid-task.

**Improvements to make:**

**A. Verify Anthropic SDK cache_control breakpoints in audit path:**
- Read `tlx/modules/js_analyzer/claude_agent.py` and
  `tlx/modules/js_analyzer/exploit_agent.py`.
- Confirm `cache_control: {type: "ephemeral"}` is set on the system
  prompt + tool defs + any large stable context blocks passed to
  Sonnet/Opus.
- If missing, add it. This is the audit pipeline's biggest API cost
  (per CLAUDE.md — `js_run_audit` uses Sonnet primary, Opus via
  `js_consult_opus`).

**B. Skill discipline (no code changes — documentation only):**
Add a section to `skills.md` titled "Context discipline":
- Skills must return structured JSON result blocks, never dump raw
  file contents into the conversation.
- For wide reads, always use `Read offset/limit` after the graph
  points to specific lines.
- Use `Task` subagents for bulk reads, graphify queries, and
  autoresearch-loop iterations — parent gets back small result block,
  never sees the noise.
- Call `/compact` before context fills with stale tool output, not
  after.

**C. Cache-aware pacing in autoresearch-loop:**
- Edit `.claude/skills/autoresearch-loop/SKILL.md` to note: between
  iterations, stay <5min (keep cache warm) or commit to >20min
  (amortize the cache miss). Mid-range (5–15min) is the worst case.

**D. status.json as persistent memory (already used, expand it):**
- Each skill writes its result block under `status.json.phases.<skill>`.
- Next session reads small JSON instead of recomputing or re-reading
  source files.
- Audit which skills currently dump full results vs structured blocks;
  shrink any that dump.

---

## Execution order (recommended)

1. **js-index AST parallel** (1A) — biggest local win, no API risk,
   deterministic verify path. Patch `ast_bridge.py`, run on a known
   target, compare counts.
2. **js-index deobfuscate parallel** (2B) — same shape, same risk
   profile.
3. **rag-ingest async concurrency** (1A) — sizable speedup with single
   key; multi-key is optional.
4. **SQLite WAL** (2C) — one-liner, low risk.
5. **claude_agent.py cache_control audit** (4A) — verify, patch if
   missing.
6. **rag-ingest multi-key** (1B) — only if user has multiple GCP
   projects ready.
7. **wiki-ingest-batch skill** (3) — only if user wants it; not on the
   critical path.
8. **skills.md context discipline** (4B) + **autoresearch pacing** (4C)
   — documentation pass.

## What to ask the user before starting

1. AST batch size: keep at 100 or drop to 50? (50 = better load
   balance, slightly more subprocess overhead.)
2. Worker cap default: `os.cpu_count()` or `os.cpu_count() - 1`
   (leave one core for the OS)?
3. Multi-key rotation: do they already have multiple GCP projects, or
   skip 1B for now?
4. wiki-ingest-batch: build it now, or wait until the user actually
   hits a 5+ source batch?

## Verification checklist before claiming done

- [ ] `js_index_target` on a known target produces identical
  `nodes`/`edges`/`tags` counts (parallel ≠ different output).
- [ ] rag-ingest produces the same chunk count and `docs_query` top
  hits as the prior single-key run.
- [ ] No SQLite "database is locked" errors during a full re-index.
- [ ] Cache hit rate measurable in Anthropic API logs (audit path)
  after `cache_control` confirmation.
- [ ] `status.json.phases.<skill>` entries stay small and structured.

## Out of scope

- Adding new external API integrations (per CLAUDE.md API-key
  whitelist).
- Rewriting interprocedural taint analysis for parallelism.
- Replacing ChromaDB with a different vector store.
- Touching the wiki RAG collection's existing 3072d Gemini embeddings
  (grandfathered).
