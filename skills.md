# Skills Index

Every skill is a folder under `.claude/skills/<name>/` with a `SKILL.md`
(frontmatter + body). Skills are *small, single-purpose, chainable*.
Claude orchestrates the chain; skills do one thing well.

> **Quality bar.** A skill is good if (a) its frontmatter triggers
> reliably on the right user intent, (b) its body is short enough to
> read in one screen, (c) it writes a structured result block to
> `targets/<name>/status.json` so a future session can resume.

---

## Phase A — Acquisition

### `target-init`
**Trigger:** new `targets/<name>/http.md` exists; OR user says "start
target <name>"; OR `status.json` missing.
**Reads:** `http.md`.
**Writes:** `status.json.scope` (in/out hosts, auth type, notes).
**Tools used:** none (pure parsing).
**Result block:** `{ phase: "init", status: "done|error", scope: {...} }`.

### `recon`
**Trigger:** `status.json.phase >= init` AND `targets/<name>/recon/`
empty; OR user says "recon", "port scan", "subdomain enum", "ferox" on
a target. Multi-region geo check optional.
**Reads:** `http.md` scope (IPs, CIDRs, wildcard domains).
**Writes:** `targets/<name>/recon/<job_id>/` (per-phase artifacts) +
`status.json.recon = {job_id, summary_path, finished_at}`.
**Tools used:** `recon` MCP (`recon_start`, `recon_status`,
`recon_results`, `recon_cancel`, `recon_list_jobs`,
`recon_cleanup_orphans`). Spawns ephemeral DO droplets in parallel and
tears down.
**Result block:** `{ phase: "recon", job_id, hosts_alive: N,
http_endpoints: M, subdomains: S }`.

### `js-harvest`
**Trigger:** `status.json.phase >= init` AND no `raw/` dir.
**Reads:** `status.json.scope`.
**Writes:** `raw/<host>/<path>.js[.map]`.
**Tools used:** `chrome-devtools` MCP (navigate, evaluate, network
requests). Also `bin/sourcemap_recon.py` (T1.5 — hidden Webpack/Vite/
Next/Nuxt map brute + Sentry release-artifact API). Scope-checked.
**Result block:** `{ phase: "harvest", files: N, maps_public: M,
maps_missing: [...] }`.

### `sourcemap-explode`
**Trigger:** `raw/**.js.map` files exist AND no `sources/` dir.
**Reads:** `raw/`.
**Writes:** `sources/**` (original tree) + `sources/_nomap/` (chunks
without maps).
**Tools used:** Python `sourcemap` lib (vendored helper in
`bin/explode_sourcemap.py`).
**Result block:** `{ phase: "explode", original_files: N,
nomap_files: M }`.

### `rag-ingest`
**Trigger:** `sources/` populated AND `status.json.rag_collection`
missing.
**Reads:** `sources/`.
**Writes:** `~/.tlx/chroma/target_<name>` collection.
**Tools used:** `docs_query` (via its ingest path); requires
`GOOGLE_API_KEY` env for the embedder.
**Result block:** `{ phase: "rag", collection: "target_<name>",
chunks: N, model: "text-embedding-004" }`.

---

## Phase B — Static analysis

### `js-index`
**Trigger:** `sources/` populated AND `status.json.index` missing OR
stale (sources mtime > index mtime).
**Tools used:** `js_index_target`. Also `bin/run_jsluice.py` (T1.4 —
URL skeletons + secrets as `node_tags(source='jsluice')`) and
`bin/build_manifest_extract.py` (T2.3 — Next/Vite/Rspack/CRA route
enumeration).
**Writes:** `index/nodes.jsonl`, `index/edges.jsonl`,
`index/frameworks.json`, `index/jsluice.jsonl`,
`index/routes.jsonl`, plus `findings/jsluice_secret_<id>/draft.json`
per leaked-secret hit.
**Result block:** `{ phase: "index", nodes: N, edges: E, tags: T,
frameworks: [...] }` plus `phases.{jsluice, build_manifest}`.

### `chain-triage`
**Trigger:** index ready.
**Tools used:** `js_get_chains(max_chains=200)`.
**Writes:** `chains/all.jsonl`, `chains/hot.jsonl` (top ~20 by
composite score described in `workflow.md > Phase B2`).
**Result block:** `{ phase: "triage", total: N, hot: M,
score_distribution: {...} }`.

### `dom-xss-hunt`
**Trigger:** `chains/hot.jsonl` exists.
**Tools used:** `mock_extract`, `mock_run` (headless reachability).
**Writes:** `chains/dom_reachable.jsonl`.
**Result block:** `{ phase: "dom_hunt", reachable: N }`.

### `opus-deep-audit`
**Trigger:** per chain in `chains/hot.jsonl` (skill iterates).
**Tools used:** `js_examine_chain`, `js_get_snippet`,
`js_run_audit`, `js_audit_status`.
**Writes:** `opus/<chain_id>.md` (transcript + verdict + reasoning +
proposed PoC).
**Result block:** `{ phase: "opus", chains_audited: N, tp: X, fp: Y,
undetermined: Z, opus_cost_usd: ... }`.
**Budget:** capped by `memory.md > opus_budget_per_target`.
**T1.2/T1.3 (2026-05-15):** Steps 1a (long-context probe via
`bin/source_token_count.py`) and 1b (cascade gate via
`bin/run_cascade.py`) run before per-chain audit. Cascade Sonnet cost
tracked separately in `status.json.cascade_cost_usd`.

### `opus-gap-audit` *(2026-05-15, T1.1)*
**Trigger:** user names a control qname (e.g. `auth.RequireRole`) AND
js-index is complete.
**Tools used:** `bin/run_gap_audit.py` (wraps gap_analyzer + cascade).
**Writes:** `chains/gap_<slug>.jsonl`,
`opus/gap_<slug>/<sibling>.md`.
**Result block:** `{ phase: "gap_<slug>", callers_found, gaps_found,
cascade: {...} }`.

### `cspt-csrf` *(2026-05-15, T2.2)*
**Trigger:** after `dom-xss-hunt` writes `chains/dom_reachable.jsonl`.
**Tools used:** `bin/cspt_csrf_scan.py` (reads per-target DB for
path-traversal tags; warns to stderr if absent).
**Writes:** `chains/cspt_csrf.jsonl`.
**Result block:** `{ phase: "cspt_csrf", chains_scanned,
matched_cspt_sink, candidates_written }`.

### `patch-diff` *(2026-05-15, T3.1)*
**Trigger:** target ships an npm package version with a known fix.
**Tools used:** `bin/npm_version_diff.py` (requires `npm`).
**Writes:** `diffs/<package>_<old>_<new>.md` — control-call delta table.
**Result block:** `{ phase: "patch_diff_<package>", control_changes }`.

### `parser-pipeline-fuzz` *(stub — 2026-05-15, T3.3)*
Vendored DOMPurify/parse5 fuzzing. SKILL.md scaffolded; bin/parser_fuzz/
deferred until per-target need.

---

## Phase C — Dynamic confirmation

### `browser-confirm`
**Trigger:** `opus/<id>.md` with `verdict: true_positive` AND no
`findings/<id>/confirmed.json`.
**Tools used:** `chrome-devtools` MCP (live mode) OR `playwright` MCP
+ `mock_start` + `mock_confirm` (mock mode). Claude picks based on
target sensitivity (asks user if unsure).
**Writes:** `findings/<id>/confirmed.json` + screenshots.
**Result block:** `{ phase: "browser_confirm", id, mode:
"live|mock", confirmed: bool, evidence: [...] }`.

### `caido-capture`
**Trigger:** start of any live session (chrome-devtools mode).
**Tools used:** `caido` MCP (`caido_project_ensure`, `caido_proxy_url`).
**Writes:** Caido project `<target>-<YYYYMMDD>` populated as user
browses. Mirror summary to `caido/captured.jsonl`.
**Result block:** `{ phase: "caido_capture", project, requests: N }`.

### `caido-replay`
**Trigger:** user names a request; OR
`caido-idor`/`autoresearch-loop` calls it programmatically.
**Tools used:** `caido` MCP (`caido_replay`, `caido_diff`).
**Writes:** `caido/replays/<request_id>/diffs.json`.
**Result block:** `{ phase: "replay", req_id, variants: N,
interesting_diffs: M }`.

### `caido-idor`
**Trigger:** user says "idor sweep" OR
`memory.md > auto_idor_on_capture: true`.
**Tools used:** `caido` MCP for batch replay with auth swaps.
**Writes:** `caido/idor/<request_id>.json` + summary in
`findings/idor-candidates.md`.
**Result block:** `{ phase: "idor", requests_swept: N, candidates: M }`.

### `caido-shift` *(stub — 2026-05-15, T3.6)*
Shift Agents-style passive open-redirect / IDOR-rotation / asset-diff
micro-agents inside `bin/caido-mcp.py`. SKILL.md scaffolded; per-agent
implementations deferred.

### `browser-confirm` extensions *(2026-05-15, T2.1 + T2.4)*
Step 2a injects `bin/domlogger_payload.js` (URL/postMessage/innerHTML
hooks); Step 2b injects `bin/eventlistener_enum.js` (inline-handler
enumeration). Outputs to `findings/<id>/{domlogger.jsonl,event_handlers.json}`.

---

## Phase D — Loop, knowledge, reporting

### `autoresearch-loop`
**Trigger:** user says "loop <target> <minutes>"; OR after all hot
chains processed AND there are still open chains AND user opted in.
**Tools used:** all of the above, plus internal Opus advisor.
**Writes:** `targets/<name>/autoresearch.jsonl` (append-only) +
`autoresearch_summary_<run_id>.md`.
**Result block:** `{ phase: "autoresearch", iters: N, budget_min: B,
new_findings: M }`.

### `wiki-ingest`
**Trigger:** any confirmed finding; any FP that taught us something;
or user says "ingest this".
**Tools used:** Read/Edit/Write on `wiki/`.
**Writes:** wiki pages (technique, target, tool, findings) with
cross-links.
**Result block:** `{ phase: "wiki_ingest", pages_touched: [...] }`.

### `wiki-query`
**Trigger:** Claude can't answer from current target files; OR user
says "search wiki".
**Tools used:** `docs_query(collection="wiki")` AND/OR direct Read on
`wiki/`.
**Returns:** list of relevant excerpts + suggested follow-up.

### `wiki-lint`
**Trigger:** user says `/wiki-lint`; OR weekly cron (if user wires
one).
**Tools used:** Read across `wiki/`, plus an internal LLM judge call.
**Writes:** `wiki/_lint_<YYYYMMDD>.md` (contradictions, orphans,
gaps).

### `report-finding`
**Trigger:** `findings/<id>/confirmed.json` exists AND no
`findings/<id>/<id>.md`.
**Tools used:** `js_export_findings(format="sarif")`,
`js_export_findings(format="md")`.
**Writes:** `findings/<id>/<id>.sarif`, `findings/<id>/<id>.md`,
`findings/<id>/poc.html`.
**Result block:** `{ phase: "report", id, files: [...], ready: bool }`.

---

## Skill discoverability

Claude Code's progressive-disclosure model: only frontmatter
(name + description + triggers) is loaded into the system prompt at
boot. The body is loaded when the skill is invoked. **Therefore:**

- Keep every SKILL.md `description:` field crisp and trigger-rich —
  it's what auto-fires the skill.
- Keep bodies < 500 lines. If a skill needs more, split it.

---

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `tlx` MCP times out at boot | `cd tlx && python -m mcp_server` manually; read stderr. Usually missing `GOOGLE_API_KEY` or `~/.tlx` perms. |
| `js_index_target` says "no JS files" | `sourcemap-explode` either failed or wrote to `_nomap/` only. Inspect `raw/` for `.js.map` count. |
| `docs_query` returns empty | `rag-ingest` not run for this collection. Run it; verify count in `status.json.rag.chunks > 0`. |
| `mock_confirm` doesn't observe sink | The page didn't navigate through the right entry. Check `mock_start` URL matches; check sink hooks installed for detected framework. |
| `caido` MCP "connection refused" | Caido GUI not running OR GraphQL endpoint off. Open Caido → settings → enable API. |
| Opus budget exceeded | Skill aborts with explicit error; user must raise `memory.md > opus_budget_per_target` or skip that chain. |

---

## Skill authoring rules (when adding new skills)

1. One folder per skill: `.claude/skills/<name>/SKILL.md` (+ optional
   `templates/`, `scripts/`).
2. Frontmatter: `name`, `description` (trigger-rich one-liner), and
   *optional* `triggers:` list.
3. Body sections: **Purpose** · **Inputs** · **Steps** · **Outputs** ·
   **Failure modes**.
4. Every skill writes a result block to `status.json` under its name.
5. No skill calls another skill directly — Claude orchestrates.
6. No skill embeds business logic that belongs in TLX. If the skill
   wants behavior TLX doesn't expose, extend TLX (carefully) and
   re-import; don't reimplement in markdown.
