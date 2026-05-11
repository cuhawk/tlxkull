# Workflow — End-to-End Bug-Bounty Pipeline

This is the narrative version of the pipeline. Skills are the steps;
this file is the story that tells Claude (and the user) how the steps
fit together. Read once per engagement.

---

## TL;DR — the golden path

```
http.md → target-init → js-harvest → sourcemap-explode → rag-ingest
       → js-index → chain-triage → dom-xss-hunt → opus-deep-audit (hot chains)
       → browser-confirm | caido-capture → caido-replay | caido-idor
       → autoresearch-loop (open chains, time-budgeted)
       → report-finding → wiki-ingest
```

Each arrow is a single skill invocation. Each skill writes its output
into `targets/<name>/` and updates `status.json` so a future session
can resume from the last successful phase.

---

## Phase A — Acquisition

You give the workspace a target by creating
`targets/<name>/http.md`. That's the seed. Everything else is
derivable.

### Step A1 — `target-init`

Reads `http.md`. Normalizes scope (in/out hosts), auth type,
working notes into `status.json.scope`. Aborts if scope is empty or
auth type is unknown.

### Step A2 — `js-harvest`

Crawls the in-scope hosts (Claude drives the browser MCP), enumerates
every `<script src=>` and dynamic `import()` call, downloads every JS
asset *and* its sibling `.js.map` (sourcemap) when public. Output:
`raw/<host>/<path>.js[.map]`.

Heuristics for sourcemap discovery: `//# sourceMappingURL=` header,
`X-SourceMap` HTTP header, well-known relative path
(`./*.js.map`). When sourcemap is private but referenced, log to
`status.json.acquisition.missing_maps[]`.

### Step A3 — `sourcemap-explode`

For every `.js.map` in `raw/`, decode and write the original tree
under `sources/`. Preserve original directory structure exactly so
js_analyzer's path-relative tagging works. If a chunk has no sourcemap,
emit the minified JS as-is into `sources/_nomap/`.

### Step A4 — `rag-ingest`

Push every file under `sources/` through the `docs_query` tool's
ingest path (Google `text-embedding-004` via the kernel embedder).
Creates a target-scoped collection named `target_<name>`. From here
the LLM can `docs_query(collection="target_<name>", query="...")` to
retrieve relevant source chunks during analysis.

---

## Phase B — Static analysis

### Step B1 — `js-index`

Invokes `js_index_target(target_folder="targets/<name>/sources/")`.
Returns nodes/edges/tags/frameworks. Persists callgraph + framework
detection to TLX's `~/.tlx/sessions.db`.

Common gotchas:
- Framework detection drives sink models. If wrong, override via
  `kv_set("target_<name>:framework_override", "<name>")` and re-index.
- Path traversal between minified and exploded chunks: js-harvest's
  output path must equal sourcemap's `sourcesContent[i]` root. The
  skill enforces this; if it errors, fix harvest and re-run.

### Step B2 — `chain-triage`

Calls `js_get_chains(max_chains=200)`. Reads chains.jsonl. Ranks by:

1. Source × sink severity (DOM XSS sink × user-controlled source > 
   prototype pollution gadget × config-only source).
2. Path length (shorter = lower noise = often higher TP rate).
3. Framework match (a React `dangerouslySetInnerHTML` sink with a
   Redux-store source is a higher-confidence candidate than a generic
   `innerHTML`).

Splits output into `chains/all.jsonl` and `chains/hot.jsonl` (top
~20 by composite score). Hot chains go to Opus; cold chains stay
queued for `autoresearch-loop`.

### Step B3 — `dom-xss-hunt`

Calls `mock_extract` to extract DOM-side sinks and event handlers,
plus `mock_run` against a candidate sub-batch in headless mode for
quick reachability filtering. Output:
`chains/dom_reachable.jsonl`.

### Step B4 — `opus-deep-audit` (per hot chain)

For each chain in `chains/hot.jsonl`:

1. `js_examine_chain(chain_id=...)` to get full source/sink/path.
2. `js_get_snippet(qname=...)` for adjacent functions.
3. `js_run_audit(target_folder=...)` for the project as a whole if not
   already running — the audit loop is the gate that routes the chain
   to Opus internally via TLX's advisor.
4. Wait on `js_audit_status(run_id=...)` until done.
5. Read verdict + proof. Persist to `opus/<chain_id>.md`.
6. If `verdict == true_positive`, copy the proposed PoC into a stub
   `findings/<chain_id>/poc.html` and mark for confirmation.

---

## Phase C — Dynamic confirmation

The static layer narrows the search. The dynamic layer proves it.

### Step C1 — `browser-confirm` (real target OR mock)

Two modes:

**Real-target mode** (default for live bounty work):
- chrome-devtools MCP navigates to the page that loads the vulnerable
  chunk.
- Skill injects the candidate payload via the URL, form, or
  `postMessage` channel identified in the chain.
- Skill watches `list_console_messages` + `list_network_requests` for
  sink firing (e.g. an outbound HTTP to attacker-controlled host, or a
  DOM mutation matching the expected XSS pattern).

**Mock mode** (preferred when target is large or rate-limited):
- `mock_start(session_id="...", target_folder="targets/<name>/sources")`
  spins a local FastAPI mock with rewritten sources + sink hooks.
- playwright MCP exercises the mock page.
- `mock_confirm(session_id, chain_id)` observes sink event and writes
  a confirmed-finding row.

### Step C2 — `caido-capture`

Ensures Caido is running locally and the browser MCP traffic is
proxied through it. Two ways:

- chrome-devtools-mcp: launch Chrome with `--proxy-server=127.0.0.1:8080`.
- playwright: pass `proxy: { server: 'http://127.0.0.1:8080' }`.

Captures land in a Caido project named `<target>-<YYYYMMDD>`. The
skill creates the project via Caido's GraphQL API if missing.

### Step C3 — `caido-replay`

For any request of interest (captured by C2 or named by the user),
replay through Caido API with a list of modifications. Diff the
response against the baseline. Use cases:

- Try the request without auth cookie.
- Swap session cookie to a second-account cookie.
- Mutate IDs, sort keys, scope filters.
- Inject XSS / SSRF / SQLi payloads at each parameter.

Output: `caido/replays/<request_id>/diffs.json`.

### Step C4 — `caido-idor` / access-control

A guided role-matrix fuzz. Requires two authenticated sessions
(usually user-A and user-B) referenced from `http.md`. For every
captured request:

1. Replay with each session.
2. Replay with no session.
3. For requests with numeric/UUID IDs, replay swapping a known
   peer-owned ID.
4. Compute response diffs; any case where response size/status
   parity unexpectedly returns peer data is a candidate IDOR.

Output: `caido/idor/<request_id>.json` + a summary in
`findings/idor-candidates.md`.

---

## Phase D — Loop and memory

### Step D1 — `autoresearch-loop`

Karpathy-style. After hot chains are processed, the remaining open
chain set + new chains discovered during dynamic confirmation feed
into a time-budgeted loop:

```
for iter in time_budget:
    chain = pick_chain_with_highest_marginal_information_gain()
    hyp   = generate_exploit_hypothesis(chain)        # opus
    test  = run_minimum_viable_test(hyp)              # mock | live | caido
    score = judge(hyp, test)                          # opus
    log_iter(chain, hyp, test, score)
    update_chain_state(chain, score)
```

Each iter writes one JSONL line to `autoresearch.jsonl`. After the
budget expires, summarize the run to `autoresearch_summary_<run_id>.md`
and surface to user.

### Step D2 — `report-finding`

For each confirmed TP:
1. Generate SARIF via `js_export_findings(format="sarif")`.
2. Compose a writeup using the template in
   `.claude/skills/report-finding/templates/writeup.md`.
3. Bundle PoC HTML/curl/burp request into `findings/<id>/`.
4. Update `status.json.findings[]`.

The skill stops short of submitting. Submission is a human step.

### Step D3 — `wiki-ingest`

On every confirmed finding *and* on every false positive that taught
us something:

1. Decide which wiki pages to touch (technique, target, tool).
2. Append cross-linked summary to each.
3. Add to `wiki/findings/<id>.md` with backlinks to the engagement.
4. Optionally fire `wiki-lint` to check the new pages didn't introduce
   contradictions.

---

## Resumption protocol

When a session starts and the user names a target:

1. Read `targets/<name>/status.json`.
2. Find the highest phase marked `status: done`.
3. Resume at the next phase. Don't re-run completed ones unless the
   user says "redo" or `status.json.invalidated_after: <phase>` is set.

If `status.json` doesn't exist or is malformed, start at Phase A1
and ask the user to confirm before overwriting any pre-existing
files.

---

## Cross-phase tools the user can invoke anytime

- `/wiki-query "<question>"` — RAG query against the wiki collection.
- `/snippet <qname>` — fetch source for a function by qualified name
  (`js_get_snippet`).
- `/replay <request_id>` — re-run a caido replay batch.
- `/status` — show `status.json` for current target.
- `/budget` — show opus + caido replay cost so far.

(These slash commands live in `.claude/commands/`.)
