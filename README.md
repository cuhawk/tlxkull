# TLX Bug-Bounty Cockpit

> A single-operator, LLM-augmented static-plus-dynamic analysis pipeline for
> JavaScript-heavy web targets. Built around a vendored subset of TLX, the
> Caido proxy, the Claude Code agent, and a personal knowledge wiki.

This document is the design / methodology overview, written in the shape of a
short systems paper. It explains how the workflow operates end-to-end, the
ideas it borrows from the literature, and how it compares to the production
static-analysis tools a bug-bounty hunter would otherwise reach for
(CodeQL, Semgrep / Semgrep Pro, Snyk Code, SonarQube, jsluice, DOMLogger++,
Burp Suite, Caido, and the various LLM-only "vibe-audit" prototypes).

---

## Abstract

Modern web targets ship as obfuscated, multi-chunk, sourcemap-stripped
single-page applications. Off-the-shelf SAST tooling — CodeQL, Semgrep,
Snyk Code — is engineered for source repositories the analyst owns. A
bug-bounty hunter rarely has that luxury: the input is a minified bundle
served from a CDN, the framework is inferred not declared, and the most
interesting taint flows cross asynchronous boundaries (`addEventListener`,
`postMessage`, `Promise.then`, service workers) that classical interprocedural
analyzers either model conservatively or skip outright. Dynamic-only tools
(Burp DOM Invader, DOMLogger++, Caido Shift Agents) compensate by observing
the running page, but they cannot tell you *which* of the 8,000 functions in
a webpack chunk are worth instrumenting.

TLX is a personal cockpit that fuses both surfaces. The acquisition layer
reconstructs the original source tree from public sourcemaps, the static
layer builds a framework-aware callgraph with closure-expanded tag
propagation, the LLM layer applies a Sonnet-cascade-into-Opus advisor flow
to a small "hot" subset of taint chains, and the dynamic layer confirms
verdicts in a real Chrome instance proxied through Caido. A wiki RAG store
captures everything that survives a true-positive or instructive
false-positive so each subsequent engagement starts smarter than the last.
The system is rule-bounded (LLM use is whitelisted to two well-defined
paths) and per-target isolated (each engagement gets its own SQLite snapshot
of the analysis DB).

---

## 1. Motivation

The bug-bounty hunter's problem is not "find every defect in this
codebase". It is "given a third-party target and a finite weekend, which
2–3 functions, in which of the 600 JS chunks, deserve a live PoC attempt?"

Existing tools optimize for the wrong question:

- **CodeQL** is precise and language-rich, but query authoring is slow,
  the public query library is server-side-heavy, and DOM-specific sinks
  / framework-specific sources require bespoke models. Useful when you
  own the repo; awkward when you're staring at a bundle.
- **Semgrep / Semgrep Pro** is fast and ergonomic but interprocedural taint
  is shallow on the OSS tier; rule writing is also fundamentally pattern
  matching, not closure-aware propagation. Strong for known-CVE
  re-checks, weaker for novel chain discovery.
- **Snyk Code, SonarQube, Veracode** target enterprise SAST: dashboards,
  pipelines, compliance. None of them prioritize a *single hunter's*
  exploratory loop.
- **jsluice** is a precise URL / secret extractor at the AST level; it has
  no callgraph and no taint. We use it as one tag layer inside TLX.
- **Burp Suite, Caido, DOM Invader, DOMLogger++** are excellent runtime
  surfaces, but provide no static prior over what to instrument first.
- **LLM-only "audit my repo" prototypes** can reason about code but
  hallucinate without ground truth; without a callgraph they cannot
  enumerate *what to ask the LLM about*.

TLX is an attempt at the missing middle: a callgraph-grounded, framework-
aware static prior over JS bundles, paired with an LLM advisor that runs
only on chains the static layer has already shown to be plausibly
reachable, with dynamic confirmation in the same browser the human would
use anyway.

---

## 2. Architecture

```
                 ┌─────────────────────────────┐
                 │   Claude Code  (operator)   │   single conversational surface
                 │   reads CLAUDE.md / skills  │   orchestrates the pipeline
                 └────────────┬────────────────┘
                              │ MCP stdio
   ┌──────────────────────────┼──────────────────────────┐
   ▼                          ▼                          ▼
 ┌──────────────┐      ┌──────────────┐           ┌──────────────┐
 │ tlx-mcp      │      │ chrome-devt. │           │ caido-mcp    │
 │ js_analyzer  │      │ real Chrome  │           │ proxy + API  │
 │ mock_backend │      │ + extensions │           │ replay/diff  │
 │ docs_query   │      │ (DOMLogger++,│           │              │
 │ session_kv   │      │  Caido, etc) │           │              │
 └──────┬───────┘      └──────┬───────┘           └──────┬───────┘
        │                     │ HTTPS                    │
        │                     ▼                          │
        │             ┌──────────────┐                   │
        │             │ Target site  │◀──── proxied ─────┘
        │             └──────────────┘
        ▼
 ┌──────────────┐      ┌──────────────┐
 │ Gemini       │      │ Anthropic    │
 │ text-emb-004 │      │ Sonnet→Opus  │   advisor pipeline
 │   (RAG only) │      │ (audit only) │   restricted by whitelist
 └──────────────┘      └──────────────┘
```

Claude Code is the only operator. Three MCP servers expose tooling: the
TLX analyzer (16 tools spanning callgraph, mock backend, RAG, session
KV), real Chrome via chrome-devtools, and Caido via a local GraphQL
wrapper at `bin/caido-mcp.py`. Two backend LLMs are invoked through
TLX's internal advisor flow — never directly by the user — and only for
two whitelisted purposes (callgraph audit, RAG embedding of source).
Everything else, including all prose synthesis, wiki distillation,
hypothesis generation in the autoresearch loop, and report drafting,
runs as the Claude Code session in front of the user.

---

## 3. Pipeline

Each engagement is one folder under `targets/<name>/`. The folder is the
unit of reproducibility — scope, raw inputs, indexed callgraph, opus
transcripts, exploit PoCs, SARIF reports, screenshots, and status all
live in it. A skill is the smallest unit of orchestration; Claude Code
chains them, never the other way around.

### 3.1 Phase A — Acquisition

| Skill              | Purpose                                                                 |
|--------------------|-------------------------------------------------------------------------|
| `target-init`      | Parse `http.md` (scope, auth, notes) into `status.json`.                |
| `recon`            | Ephemeral DigitalOcean droplets run subdomain + port + httpx + ferox.   |
| `js-harvest`       | Crawl in-scope hosts; download every `<script src>`, dynamic `import`, sourcemap. |
| `sourcemap-explode`| Decode `.js.map` artifacts into an original-source tree under `sources/`. |
| `rag-ingest`       | Embed `sources/` into a per-target ChromaDB collection (`text-embedding-004`). |
| `sourcemap-recon`  | Brute Webpack / Vite / Next / Nuxt hidden map paths + Sentry release API. |

### 3.2 Phase B — Static analysis

| Skill                 | Purpose                                                                                       |
|-----------------------|-----------------------------------------------------------------------------------------------|
| `js-index`            | Build callgraph, framework detection, taxonomy-driven node tags; merge jsluice + route enum.  |
| `async-edges`         | Add asynchronous continuation edges (Promise, setTimeout, addEventListener, RxJS, postMessage). |
| `implicit-tags`       | Closure-expand source/sink tags along the callgraph with hop-decayed confidence.              |
| `naming-heuristic`    | Function-name regex seeder (opt-in, low confidence) for un-obfuscated bundles.                |
| `bucket-inversion`    | When N≥3 sibling methods share a taxonomy tag, seed the remaining siblings as implicit sinks. |
| `chain-triage`        | Rank chains by (source × sink severity, path length, framework match); emit `hot.jsonl`.      |
| `chain-bestfirst`     | Confidence-driven best-first chain extractor; partial chain probability with pruning.         |
| `dom-xss-hunt`        | Extract DOM sinks + handlers via `mock_extract`; filter `hot.jsonl` to `dom_reachable.jsonl`.  |
| `sanitizer-on-path`   | Strict-dominance sanitizer check; splits chains into `sanitized` vs `clean`.                  |
| `browser-context-infer` | Infer CSP, Trusted Types, SSR/CSR, framework, sandbox iframes into `browser_context.json`.  |
| `v2-pipeline`         | Persistent-storage taint, origin trust, DOM clobbering, prototype-pollution gadgets, parser context, deobfuscation, corpus matching, lifecycle, auth/state, workers. |
| `opus-deep-audit`     | Per-hot-chain Sonnet cascade gate → Opus advisor; verdict + reasoning + proposed PoC.         |
| `opus-gap-audit`      | Adjacent-function-gap: sibling functions in the same module that omit a control their peers call. |
| `cspt-csrf`           | Client-side path-traversal landing in fetch/XHR/axios URLs (Doyensec playbook).               |
| `patch-diff`          | `npm pack` two versions of a dependency; diff control-call counts to localize the fix.        |
| `cc-taint-adversarial`| Per-chain Claude-Code adversarial dual-role audit (attacker + skeptic) — research alternative to opus-deep-audit. |

### 3.3 Phase C — Dynamic confirmation

| Skill              | Purpose                                                                                     |
|--------------------|---------------------------------------------------------------------------------------------|
| `caido-capture`    | Ensure Caido is running; route the browser MCP through Caido as proxy; ensure a project.    |
| `browser-confirm`  | Real Chrome (extensions loaded) navigates target or `mock_start` URL; injects DOMLogger++ + event-listener enum payloads; records sink observation + screenshots. |
| `caido-replay`     | Replay a captured request with mutations; diff against baseline.                            |
| `caido-idor`       | Generic IDOR / BAC sweep — pattern-driven ID-shape detection across path/query/header/body, auth-swap variants, response parity diff. |
| `caido-shift`      | (stub) Open-redirect / IDOR-rotation / JS-asset-diff micro-agents inside the Caido wrapper. |
| `parser-pipeline-fuzz` | (stub) Vendor DOMPurify / parse5 / JSXSS at the target's pinned version and fuzz the local pipeline. |
| `passive-listen`   | Accumulate live evidence (DOMLogger++ + postMessage tracker + Gecko store + Caido) while the user browses normally. |

### 3.4 Phase D — Knowledge + loop

| Skill                | Purpose                                                                                |
|----------------------|----------------------------------------------------------------------------------------|
| `autoresearch-loop`  | Karpathy-style time-budgeted hypothesize → test → judge loop over open chains.         |
| `wiki-ingest`        | Distill confirmed TPs and instructive FPs into `wiki/{techniques,targets,tools,findings}` with cross-links. |
| `wiki-query`         | RAG retrieval against the wiki collection; optionally draft a new page when a gap is found. |
| `wiki-lint`          | Find orphans, contradictions, dead cross-refs, stale entries; surface as a report.     |
| `report-finding`     | Generate SARIF + markdown writeup + PoC bundle for a confirmed TP.                     |
| `bbre-ingest` / `ctbb-ingest` | Distill BBRE + Critical Thinking podcast transcripts into the wiki.            |

---

## 4. Design ideas worth naming

Several of the choices below are not novel in isolation; the contribution is
that they cohere into one workflow.

1. **Sourcemap-first acquisition.** Most analyzers ingest source repos.
   TLX assumes you only get the bundle. `js-harvest` plus
   `sourcemap-explode` plus `sourcemap-recon` reconstructs the original
   tree where the developer left maps public, deliberately or otherwise.
   This is the single largest lift relative to running CodeQL on a
   webpack chunk (which is a no-op).

2. **Per-target DB isolation.** The TLX analyzer ships a global SQLite
   at `~/.tlx/js_analyzer.db`. Without isolation, every previous
   engagement contaminates `js_get_chains` for the current target. The
   workflow snapshots the global DB to `targets/<name>/db/`, filters
   rows whose `nodes.file` doesn't match the in-scope host prefix, and
   runs all chain extraction against that snapshot. Each engagement is a
   first-class, archivable artifact.

3. **Implicit-tag closure expansion.** The static taxonomy
   (`extra_sinks.json`, `extra_sources.json`, `extra_runtime_surfaces.json`)
   is fixed; real codebases hide sinks behind two or three wrapper
   functions. The `implicit-tags` skill propagates a tag along callgraph
   edges with `0.7^hop` confidence decay. `bucket-inversion` and
   `naming-heuristic` add two more recovery passes for cases the
   taxonomy and closure both miss.

4. **Async edges as first-class taint paths.** Real DOM-XSS chains
   cross continuation boundaries (`addEventListener`, `Promise.then`,
   `MutationObserver`, `postMessage`, WebSocket `onmessage`, RxJS
   `subscribe`, service-worker `fetch`). The `async-edges` skill walks
   these into the per-target snapshot DB before chain extraction, so the
   interprocedural taint search reaches handler bodies. This is exactly
   where Semgrep OSS taint and most hand-written CodeQL queries lose
   the trail.

5. **Confidence-bounded best-first chain extraction.** Beyond the
   default DFS-style extractor, `chain-bestfirst` orders the frontier by
   the product of per-edge probabilities, sink viability under the
   inferred browser context (CSP, Trusted Types, SSR/CSR), and async or
   dynamic-dispatch discounts. Frontiers below a `--p-cutoff` are
   pruned. This is the practical analogue of weighted symbolic
   execution at the callgraph layer.

6. **LLM use is rule-bounded.** Anthropic and Gemini API keys are
   whitelisted to two paths only: the TLX advisor flow (chain audit,
   Sonnet cascade → Opus deep audit) and the Google
   `text-embedding-004` ingest of `sources/`. Wiki distillation, the
   autoresearch loop, hypothesis generation, judging, prose synthesis,
   and report drafting all run as the Claude Code session. This is what
   makes the system auditable: there is no shadow LLM call.

7. **Knowledge accumulates.** The wiki at `wiki/` is the long-term
   memory: per-technique, per-program, per-tool, per-finding pages with
   cross-links. Every confirmed TP and every instructive FP feeds it
   via `wiki-ingest`; `wiki-lint` periodically surfaces contradictions
   and orphans; `wiki-query` is the retrieval surface. Combined with
   the BBRE and Critical Thinking podcast distillations, this is the
   `karpathy/llmwiki` pattern applied to bug-bounty research.

8. **Karpathy-style autoresearch loop.** After hot chains are
   processed, the residual open-chain set feeds a time-budgeted loop
   (default 60 minutes wall clock, 5 minutes per iter per the Karpathy
   spec). Each iter generates a hypothesis, runs the minimum-viable
   test (mock, live browser, or Caido replay), judges, and writes one
   append-only JSONL line to `autoresearch.jsonl`. The loop is
   reviewable and replayable.

9. **Dynamic confirmation in *one* browser.** Both live and mock
   confirmation run in real Chrome via chrome-devtools MCP. Installed
   extensions (DOMLogger++, the Caido browser extension, Wappalyzer)
   are loaded for both modes. This sidesteps the Playwright/Chromium
   gap and matches the human workflow.

10. **Caido as the network ground truth.** Every live request is
    proxied through Caido; every replay (`caido-replay`, `caido-idor`)
    happens via Caido's GraphQL API. The proxy is the durable artifact
    of a session; the replay diffs become evidence in reports.

---

## 5. Comparison to existing tools

The table below grades each tool on dimensions that matter for a single
hunter working bug-bounty bundles, not for enterprise SAST in CI. "Y" =
strong, "p" = partial / requires significant work, "—" = not applicable.

| Dimension                              | CodeQL | Semgrep / Pro | Snyk Code | SonarQube | jsluice | Burp + DOMLogger | Caido + Shift | LLM-only audit | **TLX** |
|----------------------------------------|--------|---------------|-----------|-----------|---------|------------------|---------------|----------------|---------|
| Reads a webpack bundle, not a repo     | p (manual) | p          | —         | —         | Y       | Y                | Y             | p              | **Y**   |
| Sourcemap-aware acquisition            | —      | —             | —         | —         | —       | —                | —             | —              | **Y**   |
| Framework detection drives sink models | p (queries) | p        | p         | p         | —       | —                | —             | p              | **Y**   |
| Interprocedural taint with closures    | Y      | p (Pro)       | Y         | p         | —       | —                | —             | p              | **Y**   |
| Async-edge taint (Promise, postMsg, …) | p      | —             | p         | —         | —       | runtime only     | runtime only  | p              | **Y**   |
| Confidence-bounded chain ranking       | p      | p             | p         | p         | —       | —                | —             | —              | **Y**   |
| LLM verdict on top-N chains, rule-bounded | —   | —             | p         | —         | —       | —                | p             | Y              | **Y**   |
| Dynamic confirmation in the same workflow | —   | —             | —         | —         | —       | Y                | Y             | —              | **Y**   |
| Persistent per-engagement state        | p      | p             | Y         | Y         | —       | p                | Y             | —              | **Y**   |
| Knowledge accumulating across targets  | —      | p (rule reuse)| —         | —         | —       | —                | —             | p              | **Y**   |
| Per-target DB isolation                | Y      | Y             | Y         | Y         | —       | —                | Y             | —              | **Y**   |
| Auditable LLM-use boundary             | —      | —             | —         | —         | —       | —                | —             | —              | **Y**   |
| CI / multi-user                        | Y      | Y             | Y         | Y         | p       | p                | p             | varies         | **—**   |
| Free for unlimited use                 | Y      | Y (OSS)       | freemium  | Y (CE)    | Y       | Burp pro paid    | Caido pro paid | API cost      | API cost |
| Mature, vendor-supported               | Y      | Y             | Y         | Y         | p       | Y                | Y             | —              | personal |

### Pros vs each named alternative

- **vs CodeQL.** TLX trades CodeQL's precision and language breadth for
  JS-specific depth (frameworks, sourcemaps, async edges, DOM sinks),
  LLM verdicts on a small chain subset, dynamic confirmation in the
  same workflow, and a knowledge layer that compounds. CodeQL is the
  better choice if you control the repo and want repeatable queries in
  CI; TLX is the better choice if you do not.
- **vs Semgrep / Semgrep Pro.** Semgrep is faster and easier to author
  against. TLX's advantage is closure-expanded interprocedural taint
  across async edges and an LLM advisor — the kinds of chain a
  Semgrep pattern systematically loses. Semgrep is excellent for the
  known-CVE re-check that follows a TLX-discovered novel chain.
- **vs Snyk Code / SonarQube / Veracode.** Enterprise SAST is built
  around dashboards, compliance, and CI integration. None of that is
  useful for a single hunter; TLX is.
- **vs jsluice.** No conflict — TLX runs jsluice and ingests its
  output as one tag layer (`source='jsluice'`).
- **vs Burp / DOMLogger++ / DOM Invader.** TLX prepends a static
  prior so the dynamic surface is pointed at the right pages,
  payloads, and listeners. The dynamic surface itself is still Burp /
  DOMLogger++ — we drive them from the same Chrome instance.
- **vs Caido + Shift Agents.** TLX uses Caido as the proxy and the
  GraphQL replay backend. Shift Agents are the closest peer to TLX's
  agentic layer; TLX adds the callgraph-grounded chain selection that
  Shift lacks, and Shift adds passive observation that TLX is now
  copying via `caido-shift`.
- **vs LLM-only "audit my code" prototypes.** Without a callgraph,
  an LLM cannot enumerate what to think about. TLX is the
  callgraph + framework + taint layer that makes the LLM verdict
  load-bearing.

### Honest limitations

- **JS-only.** Server-side PHP / Python / Go is not in scope. If the
  bug is in the API, TLX is the wrong tool; reach for CodeQL or Semgrep.
- **Sourcemap dependence.** Without public maps, the analyzer runs on
  the minified bundle and tag accuracy degrades. Naming-heuristic is
  off by default precisely because minified one-letter names defeat it.
- **LLM cost.** Opus deep-audit is capped per target
  (`opus_budget_per_target_usd` in `memory.md`, default $25). The
  Sonnet cascade gate is the cost-saver; expect ≥5× Opus call
  reduction on the same chain set.
- **Single operator.** No multi-user, no CI. The workflow assumes one
  human at one machine, with Caido running locally.
- **Caido GUI dependency.** Replay and IDOR sweep require the Caido
  GUI to be open with the API enabled.
- **Stubs.** `parser-pipeline-fuzz` and `caido-shift` are scaffolded;
  per-agent implementations are deferred to per-target need.
- **Personal artifact.** This is a research cockpit, not a product. It
  has rough edges that an enterprise tool would not.

---

## 6. Capability matrix — what you can do with this

The following table is the practical surface: each row is a thing a
hunter actually wants to do during an engagement, and the column points
to the skill or skill chain that does it.

| You want to …                                                | Skill chain                                                                 |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|
| Start a new target from scope notes                          | `target-init`                                                               |
| Enumerate subdomains, ports, HTTP services                   | `recon`                                                                     |
| Pull every JS asset and sourcemap from a target              | `js-harvest` + `sourcemap-recon`                                            |
| Get a real source tree out of a minified bundle              | `sourcemap-explode`                                                         |
| Search the target's own source by natural language           | `rag-ingest` → `docs_query(collection="target_<name>")`                     |
| Build a callgraph + framework profile + tag table            | `js-index`                                                                  |
| Walk async / event / Promise edges into the taint graph      | `async-edges`                                                               |
| Propagate sink/source tags through wrapper functions         | `implicit-tags` + `bucket-inversion` + `naming-heuristic`                   |
| Get the top-N highest-value taint chains                     | `chain-triage` + `chain-bestfirst`                                          |
| Filter chains by DOM-sink reachability in a headless mock    | `dom-xss-hunt`                                                              |
| Drop chains a sanitizer already dominated                    | `sanitizer-on-path`                                                         |
| Infer CSP + Trusted Types + framework before scoring         | `browser-context-infer`                                                     |
| Run persistent-storage taint + origin trust + DOM clobbering | `v2-pipeline`                                                               |
| Get an LLM verdict on the hot chains                         | `opus-deep-audit`                                                           |
| Find sibling functions that skip a security control          | `opus-gap-audit`                                                            |
| Find client-side path traversal landing in fetch URLs        | `cspt-csrf`                                                                 |
| Localize the fix between two npm versions                    | `patch-diff`                                                                |
| Run an attacker / skeptic dual-role audit per chain          | `cc-taint-adversarial`                                                      |
| Confirm a candidate in a real browser, extensions loaded     | `browser-confirm` (live mode)                                               |
| Confirm a candidate in a sandbox                             | `browser-confirm` (mock mode) + `mock_start` / `mock_confirm`               |
| Capture every browser request to Caido                       | `caido-capture`                                                             |
| Replay a captured request with mutations                     | `caido-replay`                                                              |
| Sweep captured requests for IDOR / BAC                       | `caido-idor`                                                                |
| Accumulate live evidence while browsing manually             | `passive-listen`                                                            |
| Loop on open chains for N minutes                            | `autoresearch-loop`                                                         |
| Write a SARIF + markdown + PoC bundle for a confirmed TP     | `report-finding`                                                            |
| Persist a finding (TP or instructive FP) to the wiki         | `wiki-ingest`                                                               |
| Ask the wiki a question                                      | `wiki-query`                                                                |
| Distill a BBRE or CT podcast episode into the wiki           | `bbre-ingest` / `ctbb-ingest`                                               |
| Find contradictions or orphans in the wiki                   | `wiki-lint`                                                                 |

Slash commands (`/status`, `/snippet`, `/replay`, `/budget`, `/loop`,
`/wiki-query`, `/wiki-lint`, `/audit-gap`) live in `.claude/commands/`
and wrap the most common skills with positional arguments.

---

## 7. Reproducibility and data hygiene

A bug-bounty target is also a legal artifact. The workflow is built
around five hard rules — all enforced in `CLAUDE.md` and read at session
start by Claude Code:

1. **Scope first.** Every target carries an `http.md` with explicit
   in-scope and out-of-scope host lists. Skills refuse to touch a
   host that isn't in scope, even when the user asks. The Caido
   project scope rules are the second line of defense.
2. **Auth secrets are never written to disk in `targets/` or `wiki/`.**
   Credentials are referenced by Caido workflow ID or env var only.
3. **Destructive HTTP is per-request confirmed.** Read-only fuzz
   (GET, OPTIONS) is allowed without per-request approval; mutating
   verbs require explicit confirmation if the program does not
   sanction them.
4. **Wiki edits are append-and-cross-link.** `wiki-lint` reports
   anomalies; deletion is a manual step.
5. **API-key whitelist.** As described in section 4 (item 6). Any
   future skill that would call Anthropic or a Gemini chat model
   outside the whitelisted paths must instead run as Claude Code or
   be flagged "can't do it".

Each engagement is reproducible from its target folder alone: `http.md`
+ `raw/` + `sources/` + `index/` + `chains/` + `opus/` + `caido/` +
`findings/` + `status.json` is the complete record.

---

## 8. Related work and inspirations

- **CodeQL** (GitHub Security Lab). Reference design for query-based
  taint and dataflow.
- **Semgrep** and **Semgrep Pro Engine** (r2c / Semgrep). Pattern-first
  with a Pro interprocedural taint mode.
- **jsluice** (BishopFox). AST-level URL and secret extraction; ingested
  here as one tag layer.
- **DOMLogger++** (kevin-mizu). Runtime instrumentation of DOM XSS
  surfaces, source / sink / event-handler logging.
- **Caido** (Caido team). The proxy and GraphQL replay backend; Shift
  Agents inspired the `caido-shift` agentic stub.
- **karpathy / llmwiki** and **karpathy / autoresearch**. The wiki shape
  (per-technique / target / tool / finding pages with cross-links) and
  the 5-minute-per-iter time-budgeted loop are taken directly from
  these projects.
- **PortSwigger Research** and **BBRE / Critical Thinking podcasts**.
  Distilled into the wiki via the corresponding ingest skills.
- **Doyensec's CSPT-2-CSRF playbook.** Implemented in `cspt-csrf`.
- **Anthropic Skills + MCP**. The orchestration model — small skills,
  progressive disclosure, MCP transports — is the substrate.

---

## 9. Status

- 36 skills installed under `.claude/skills/`. ~17 core + research add-ons
  spanning best-first extraction, async edges, implicit tags, sanitizer
  dominance, browser context inference, V2 pipeline (origin trust,
  storage taint, DOM clobbering, parser context), CSPT-CSRF, patch
  diff, adversarial taint, autoresearch loop, wiki ingest / query /
  lint, podcast distillation, recon.
- The TLX vendored subtree is at `tlx/` and boots via
  `cd tlx && python -m mcp_server`.
- The Caido wrapper lives at `bin/caido-mcp.py`.
- The wiki is at `wiki/` and currently includes per-technique,
  per-target, per-tool, per-people, per-finding pages plus periodic
  lint reports.
- Per-target work happens under `targets/<name>/`; the
  `_TEMPLATE_http.md` seed shows the expected schema.

---

## 10. How to use this on a real engagement

1. Create `targets/<name>/http.md` (copy `_TEMPLATE_http.md`). Fill in
   scope, auth, working notes.
2. Tell Claude Code in this workspace: "start target `<name>`". The
   `target-init` skill normalizes scope; subsequent skills auto-fire
   per `workflow.md`.
3. Let the static pipeline run to `chain-triage` and `dom-xss-hunt`.
4. Open Caido locally with the API enabled. Tell Claude Code:
   "caido capture". From here, your manual browsing of the target is
   captured.
5. Inspect `chains/hot.jsonl` and ask Claude Code to run
   `opus-deep-audit` on the chains you care about — or let the
   default flow run them all up to budget.
6. For each true-positive verdict, run `browser-confirm` (live or
   mock); for each captured request worth probing, run `caido-replay`
   or `caido-idor`.
7. When a TP is confirmed, run `report-finding` for the SARIF +
   writeup + PoC bundle. Submission to the platform is a human step.
8. After the engagement, run `wiki-ingest` for each finding and any
   instructive false positive. Periodically run `wiki-lint`.

That is the cockpit. The intent is that next month's engagement starts
with a strictly larger prior than this month's.

---

*This document describes the workspace as of 2026-05-20. The skills and
ideas above were assembled by one operator (the maintainer of this
repo) on top of the vendored TLX analyzer, the Caido proxy, the Claude
Code agent, and the published research cited in section 8. Everything
in this directory exists to make a single hunter materially better at
the same problem, one engagement at a time.*

# WORKFLOW

http.md → target-init → recon → js-harvest (+sourcemap_recon T1.5) → sourcemap-explode → rag-ingest
       → js-index (+jsluice T1.4 + build_manifest T2.3) → db-isolate snapshot
       → implicit-tags → naming-heuristic → bucket-inversion → async-edges → browser-context-infer
       → chain-triage (or chain-bestfirst) → sanitizer-on-path → dom-xss-hunt → cspt-csrf
       → cc-taint-adversarial  (or legacy opus-deep-audit w/ cascade T1.2/T1.3)
       → browser-confirm (live via Caido OR mock_backend) → caido-capture/replay/idor
       → autoresearch-loop → report-finding → wiki-ingest