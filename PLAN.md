# TLX Bug-Bounty Workspace — Master Plan

> Personal bug-bounty cockpit. Claude Code is the operator; TLX (vendored
> subset) is the analyzer; Caido is the network surface; Playwright /
> chrome-devtools are the browser arms; Karpathy's llmwiki + autoresearch
> patterns are the memory and the loop.

## 1. Goals

1. **One folder, one workflow.** Everything a bug-bounty session needs lives
   here — vendored analyzer, skills, per-target dirs, personal wiki.
2. **Results > speed.** Late beats wrong. The pipeline is allowed to take
   minutes per chain if it materially improves verdict quality.
3. **Compounding knowledge.** Every finding (true *and* false positive)
   feeds back into the llmwiki + the per-target `notes.md`.
4. **Reproducible per engagement.** A target subfolder is a single
   self-contained artifact (scope, raw inputs, indexed graphs, opus
   transcripts, exploit POCs, SARIF, screenshots).

## 2. Operating model

```
                   ┌─────────────────────────────┐
                   │   Claude Code (operator)    │
                   │  reads CLAUDE.md / skills   │
                   └────────────┬────────────────┘
                                │ MCP stdio
        ┌───────────────────────┼──────────────────────────────┐
        ▼                       ▼                              ▼
  ┌──────────────┐       ┌──────────────┐              ┌──────────────┐
  │ tlx-mcp      │       │ browser-mcp  │              │ caido-mcp    │
  │ js_analyzer  │       │ chrome-dev / │              │ proxy + API  │
  │ mock_backend │       │ playwright   │              │ replay / diff│
  │ docs_query   │       └──────┬───────┘              └──────┬───────┘
  │ session_kv   │              │                             │
  └──────┬───────┘              │ HTTP/HTTPS                  │
         │                      ▼                             │
         │              ┌──────────────┐                      │
         │              │ Target site  │◀─────── proxied ─────┘
         │              └──────────────┘
         ▼
  ┌──────────────┐       ┌──────────────┐
  │ Gemini       │       │ Anthropic    │
  │ text-emb-004 │       │ Opus 4.x     │
  │ (RAG)        │       │ (deep audit) │
  └──────────────┘       └──────────────┘
```

Claude Code is the only conversational surface. All three MCP servers expose
tools; Claude orchestrates. The two LLM backends (Gemini for embeddings,
Anthropic Opus for deep analysis) are invoked through tlx's internal advisor
pipeline (Sonnet executor → Opus advisor) — not directly from Claude Code.

## 3. What we vendor from TLX

User mandate: copy only what we need; keep the folder clean; do not install
TLX as a dependency.

| TLX subtree | Why kept | Lines (approx) |
| --- | --- | --- |
| `kernel/` (sans `engines/claude.py` UI bits) | Tool model, sandbox, session SQLite, embedder service, services registry, plugin loader stub | ~3k |
| `kernel/embedders/` | Google `text-embedding-004` adapter for RAG | ~300 |
| `kernel/engines/gemini.py` + `engines/anthropic.py` + `engines/advisor.py` | Sonnet→Opus advisor for audit loop | ~800 |
| `modules/js_analyzer/` | Callgraph, taint, ITP, AST bridge, sourcemap, framework detect, PP chains, template analyzer, audit loop, exploit agent, SARIF | full |
| `modules/mock_backend/` | Mock server + sink hooks + browser confirmation + OpenAPI/ffuf/Burp scope export | full |
| `modules/rag/` | ChromaDB RAG (`docs_query` is *the* tool; folder renamed from `docs/` for clarity, tool names kept) | full |
| `mcp_server/` | stdio MCP transport + `allowlist.py` | full |
| `prompts/base_system.md` | System prompt foundation for advisor engine | full |
| `pyproject.toml` + `uv.lock` (subset) | Runtime deps; strip ui_server / playwright module deps | trimmed |

**Dropped** (Claude Code natives or unused on this surface):
`ui_server/`, `modules/playwright/`, `modules/files/`, `modules/web/`,
`modules/crawler/`, `cli/`, `ui/` (React), `tests/` (kept only the ones
that cover js_analyzer + mock_backend so we can verify after copy), all
plugins except `caveman_wire.py` if installed globally.

## 4. Skills (the operator's hands)

Each lives in `.claude/skills/<name>/SKILL.md` with progressive-disclosure
frontmatter. Skills are *small* and *single-purpose*; chaining is Claude's
job, not the skill's.

### Phase A — Acquisition
| Skill | Trigger | Output |
| --- | --- | --- |
| `target-init` | new `targets/<name>/http.md` exists | normalized scope, in-scope hosts, auth notes |
| `js-harvest` | `target-init` done | `targets/<name>/raw/*.js` + `*.js.map` |
| `sourcemap-explode` | sourcemaps present | `targets/<name>/sources/**` original tree |
| `rag-ingest` | sources exploded | docs_query collection populated |

### Phase B — Static analysis
| Skill | Trigger | Output |
| --- | --- | --- |
| `js-index` | sources ready | callgraph nodes/edges/tags + frameworks |
| `chain-triage` | index done | ranked chain list, hot subset for Opus |
| `opus-deep-audit` | per hot chain | verdict + reasoning + proposed POC |
| `dom-xss-hunt` | always after triage | DOM sink subset (mock_backend extract) |

### Phase C — Dynamic confirmation
| Skill | Trigger | Output |
| --- | --- | --- |
| `browser-confirm` | TP-candidate chain | sink observation on real target (Playwright) |
| `caido-capture` | live target session start | requests captured to Caido project |
| `caido-replay` | request of interest | modified replay + diff against baseline |
| `caido-idor` | authn'd request captured | role-matrix fuzz + diff to detect IDOR/BAC |

### Phase D — Knowledge loop
| Skill | Trigger | Output |
| --- | --- | --- |
| `autoresearch-loop` | open chain set + time budget | iterates hypothesis → test → judge; logs each iter |
| `wiki-ingest` | new finding / new technique observed | wiki page(s) created or updated |
| `wiki-query` | any question Claude can't answer from current files | wiki retrieval + possibly new page |
| `wiki-lint` | weekly / on demand | contradictions, orphans, gaps report |
| `report-finding` | confirmed bug | SARIF + writeup + PoC bundle ready for submission |

That's **17 skills**. Index + when-to-fire matrix lives in `skills.md`.

## 5. Per-target folder shape

```
targets/<name>/
├── http.md          # YOU write this. scope, auth, notes. seed of pipeline.
├── raw/             # js-harvest output. *.js + *.js.map.
├── sources/         # sourcemap-explode output. original src tree.
├── index/           # js-index output. nodes.jsonl, edges.jsonl, tags.jsonl, frameworks.json
├── chains/          # chain-triage output. chains.jsonl + hot.jsonl
├── opus/            # opus-deep-audit transcripts. chain_<id>.md
├── caido/           # captured + replayed requests. *.har + diffs/
├── findings/        # confirmed bugs. <id>.sarif + <id>.md + <id>/poc.html
├── notes.md         # working notes (Claude appends; you edit)
└── status.json      # pipeline state (which phases done, last run, counts)
```

## 6. `http.md` schema (target seed)

```markdown
# <target name>

## Scope
- in:   <host or regex>
- out:  <host or regex>

## Auth
- type: <session | bearer | none>
- creds: <path to caido login workflow id OR header to inject>

## Notes
- <free text — any intel you already have>
```

Every skill reads this first. `target-init` normalizes it into
`status.json.scope` so downstream skills don't re-parse.

## 7. Wiki shape (Karpathy llmwiki applied to bug bounty)

```
wiki/
├── SCHEMA.md           # what pages exist, naming, cross-link rules
├── targets/            # per-program intel (NOT engagement working dirs)
│   └── <program>.md    # rate limits, payout history, scope quirks, prior bugs
├── techniques/         # bug-class patterns
│   ├── dom-xss/...
│   ├── prototype-pollution/...
│   ├── idor/...
│   └── ...
├── tools/              # caido tricks, mcp quirks, browser flags
└── findings/           # all your past confirmed (TP and FP) findings, cross-linked
```

Operations: **ingest** (new source → wiki edits), **query** (RAG retrieval +
possibly new page), **lint** (find contradictions / orphans). All three are
skills.

## 8. Autoresearch loop (Karpathy autoresearch applied)

`.claude/skills/autoresearch-loop/SKILL.md` runs:

```
for iter in budget(minutes=N):
    chain  = pick_next_open_chain()
    hyp    = generate_hypothesis(chain)         # opus
    test   = run_test(hyp)                      # mock_confirm | browser-confirm | caido-replay
    score  = judge(hyp, test)                   # opus
    log(iter, chain, hyp, test, score)
    update_chain_state(chain, score)
```

Single-file scope mirror: each iter writes one append-only line to
`targets/<name>/autoresearch.jsonl`. Reviewable, replayable. Time budget
default 5 min per iter (Karpathy's spec); user-tunable per target.

## 9. MCP server roster (`.claude/settings.json`)

| name | command | purpose |
| --- | --- | --- |
| `tlx` | `python -m mcp_server` (cwd: `./tlx`) | 16 tools (js_analyzer + mock_backend + docs_query + session_kv_get) |
| `chrome-devtools` | (already installed) | live target browsing + Caido proxy host |
| `playwright` | (already installed) | mock_confirm sink observation |
| `caido` | wrapper script in `./bin/caido-mcp.py` (new) | GraphQL replay + project capture |

The `caido-mcp.py` wrapper is the only new MCP we write. Thin: it exposes
`caido_replay(request, mods)`, `caido_diff(req_a, req_b)`,
`caido_project_export(project)`, `caido_login(workflow_id)`. Talks to
Caido's local GraphQL endpoint.

## 10. Build sequence

1. Write foundation docs (this turn): PLAN.md, CLAUDE.md, workflow.md,
   skills.md, memory.md.
2. Scaffold folder tree (this turn): `.claude/skills/<each>/`, `targets/`,
   `wiki/`, `tlx/`, `bin/`.
3. Stub all 17 SKILL.md files (this turn or next).
4. Clone TLX shallow to `/tmp/tlx-src`, copy approved subtree into `./tlx/`,
   adjust imports (next turn).
5. Write `.claude/settings.json` with all four MCP servers (next turn).
6. Write `bin/caido-mcp.py` thin wrapper (next turn).
7. Sanity: `cd tlx && python -m mcp_server` boots, `docs_query` answers a
   trivial query, `mock_extract` runs on a known target. Fix until green.
8. Ingest llmwiki gist + autoresearch README into `wiki/tools/karpathy/`
   for offline reference (final turn).

## 11. Non-goals

- No re-implementing js_analyzer in Claude Code. TLX does it; we call it.
- No invention of new bug-class detectors in skills — they orchestrate, they
  don't analyze.
- No support for multiple operators per target. Single-user.
- No CI/CD. This is a personal cockpit.

## 12. Open questions (parked, not blocking)

- Caido API auth: token vs session cookie. Resolve when writing
  `caido-mcp.py`.
- Whether to run TLX MCP server as long-lived daemon (one boot per workday)
  vs per-session (spawned by Claude Code). Default: per-session; revisit if
  embedder warmup hurts.
- Wiki backing: pure markdown for now. If query latency becomes a problem,
  index into `docs_query` collection `wiki/`.
