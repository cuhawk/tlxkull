# TLX Use Cases

Practical playbook for the TLX bug-bounty cockpit. Companion to
`PLAN.md` (architecture) and `workflow.md` (skill ordering).

This file answers: **"I'm sitting down to hunt. What do I actually
type?"**

---

## 0. One-time setup checks

Run these once per machine. Idempotent.

```bash
# venv + key
ls tlx/.venv/bin/python                # must exist
echo $GOOGLE_API_KEY                   # must be set (or export in shell rc)

# tlx mcp boot test (surfaces real errors if any)
cd tlx && .venv/bin/python -m mcp_server
```

If the MCP boots clean, restart Claude Code so the `mcp__tlx__*` tools
load. After that the table at the bottom of this file applies.

---

## 1. Query the wiki — three flavors

### 1a. `/wiki-query <question>` (recommended in-session)

Invokes the `wiki-query` skill. RAG search + grep fallback + optional
new-page draft if results are weak.

```
/wiki-query how to bypass PKCE on OAuth 2.1
/wiki-query Vue 3 constructor chain XSS
/wiki-query Dutch bank scope quirks
/wiki-query single-packet race condition
```

### 1b. `docs_query` MCP tool (direct, programmatic)

When you want raw RAG output from inside a longer reasoning chain.

```python
docs_query(collection="wiki", query="prototype pollution gadget jQuery", k=8)
```

Returns top-k chunks with source paths and similarity scores.

### 1c. Grep (free, no MCP)

For exact-string lookups across the wiki *and* the vendored OSS repos
(`_external/`) which are deliberately NOT in the RAG collection.

```bash
rg -ti md "PKCE" wiki/techniques wiki/payloads wiki/sources
rg -i "redirect_uri.*bypass" wiki/_external/payloads-all-the-things/
rg -l "PKCE" wiki/_external/hacktricks/src/
```

---

## 2. Phase-by-phase target hunt

Standard skill chain after a target's `http.md` is written. Each phase
has a wiki-query you should fire before kicking off the skill — it
surfaces prior intel and biases the heuristic toward known patterns.

| Phase | Skill | Pre-phase query | Why |
| --- | --- | --- | --- |
| Init | `/target-init <name>` | `/wiki-query <program> prior findings` | Pull dossier if you've hunted here before |
| Harvest | `/js-harvest` | `/wiki-query <framework> source maps` | Framework chunk patterns (Webpack, Vite, Next.js) |
| Decode | `/sourcemap-explode` | — | Mechanical step, no query needed |
| Index | `/rag-ingest` + `/js-index` | — | Builds the per-target RAG + callgraph |
| Triage | `/chain-triage` | per chain: `/wiki-query <sink_kind> heuristics` | Boost score on sink types with prior TPs |
| Mock filter | `/dom-xss-hunt` | — | Cheap reachability filter |
| Deep audit | `/opus-deep-audit` | auto-runs `docs_query` inside the Opus prompt builder | Opus sees relevant technique pages = better verdicts |
| Loop | `/loop <minutes>` | per iter: auto-query | Karpathy autoresearch w/ wiki-grounded hypotheses |
| Confirm | `/browser-confirm` | `/wiki-query <sink_kind> trigger payload` | Pick exact payload from 40 dom-xss families |
| Report | `/report-finding` | `/wiki-query <pattern> writeup` | Reuse prior writeup structure |
| Ingest | `/wiki-ingest` | — | Adds the finding back to the wiki for next time |

---

## 3. Use-case recipes

### 3a. Fresh target — never hunted this program before

```
# 1. write targets/<name>/http.md (use _TEMPLATE_http.md as base)
# 2. cold-start queries
/wiki-query <program-name> snapshot
/wiki-query <industry> auth flow                  # e.g. "banking OAuth"
/wiki-query <adjacent-program> prior findings     # competitor with similar stack

# 3. pipeline
/target-init <name>
/js-harvest
/sourcemap-explode
/rag-ingest
/js-index
/chain-triage
/dom-xss-hunt
/opus-deep-audit
```

### 3b. Returning to a program with prior findings

```
/wiki-query <program> prior findings              # dossier
/wiki-query <program> auth quirks                 # session lifetime, 2FA flow
/status <name>                                    # where the pipeline left off
# resume from the phase status.json points at
```

### 3c. You saw a CVE / blog post / podcast — want it in the wiki

```
# manual drop one of:
- new URL  -> Claude fetches + distills via Sonnet subagent
- .vtt / pdf / md / txt -> /wiki-ingest <path>
- "ingest this: <pasted text>" -> Sonnet distills into matching technique page
```

The distill ALWAYS:
1. Creates/updates `wiki/techniques/<class>/<pattern>.md` (or `tools/`,
   `findings/`).
2. Back-links to the source page in `wiki/sources/`.
3. Re-embeds touched pages into the `wiki` RAG collection (run
   `bin/ingest-wiki.py`).

### 3d. Live confirmation — picking a payload

You have a candidate DOM-XSS chain. The sink is `innerHTML`. Framework
is Vue 3. The source is `location.hash`.

```
/wiki-query Vue 3 innerHTML XSS hash source
```

Returns the technique page (`framework-vectors-vue.md`) and the
payload family pages (`vue3-component-is-script.md`,
`vue3-constructor-chain.md`). Pick one, fire via `browser-confirm`.

If none match: `rg -l "v-html\|innerHTML" wiki/_external/hacktricks/` for
deeper hunt — HackTricks isn't in RAG so it needs grep.

### 3e. Autoresearch overnight loop

```
/loop 240          # 4 hours
```

Each iter (12/hr):
1. Pick highest-score un-probed chain.
2. Opus generates exploit hypothesis (sees wiki RAG hits as context).
3. Run cheapest viable test (mock | live | caido).
4. Opus judges verdict.
5. Append jsonl line.

Read progress: `tail -f targets/<name>/autoresearch.jsonl`.
Post-run summary: `autoresearch_summary_<run_id>.md`.

### 3f. Reporting a finding

```
# finding has been browser-confirmed, screenshots in findings/<id>/
/wiki-query <pattern> writeup template            # reuse prior structure
/report-finding <id>                              # generates SARIF + writeup
/wiki-ingest targets/<name>/findings/<id>/<id>.md # adds to wiki
```

The wiki-ingest step touches ≥3 pages:
- `wiki/findings/<id>.md` (new, distilled).
- `wiki/techniques/<class>/<pattern>.md` (Seen-in-the-wild entry).
- `wiki/targets/<program>.md` (Prior findings entry).

---

## 4. Maintenance ops

### Re-embed wiki after edits

```bash
export GOOGLE_API_KEY=<key>
tlx/.venv/bin/python bin/ingest-wiki.py
```

Idempotent — skips unchanged files via SHA256.

### Lint

```
/wiki-lint
```

Writes `wiki/_lint_<YYYYMMDD>.md`. Reports orphans, dangling links,
frontmatter problems, stale entries. Does **not** auto-fix.

### Refresh vendored OSS repos

```bash
cd wiki/_external/payloads-all-the-things && git pull --depth=1
cd wiki/_external/hacktricks && git pull --depth=1
```

### Add new CT podcast episodes (when transcripts available)

```bash
cd wiki/sources/podcasts/ct
yt-dlp --write-auto-sub --skip-download --sub-lang en --sub-format vtt \
  --output "%(upload_date)s_%(id)s_%(title)s.%(ext)s" \
  --restrict-filenames --no-warnings --ignore-errors \
  "https://www.youtube.com/@criticalthinkingpodcast/videos"
```

Then on-demand: `/wiki-ingest wiki/sources/podcasts/ct/<file>.vtt` to
distill via Sonnet.

---

## 5. RAG collection — what's in it

437 chunks indexed in the `wiki` Chroma collection
(`~/.tlx/chroma`, embedder `gemini-embedding-001`).

| Source | Pages | Chunks (approx) |
| --- | --- | --- |
| `wiki/techniques/dom-xss/` | 12 | ~90 |
| `wiki/techniques/{oauth,idor,prototype-pollution,race-conditions,server-side,postmessage}/` | 19 | ~100 |
| `wiki/payloads/dom-xss/` | 40 | ~120 |
| `wiki/sources/portswigger-*.md` | 6 | ~25 |
| `wiki/sources/podcasts/ct/README.md` | 1 | 3 |
| `wiki/tools/` | 5 | ~25 |
| `wiki/SCHEMA.md` | 1 | 10 |

**NOT in RAG** (intentional):
- `wiki/_external/payloads-all-the-things/` — grep only.
- `wiki/_external/hacktricks/` — grep only.
- Raw `.vtt`, `.html`, `.pdf` artifacts — grep / Read only.

---

## 6. Tool inventory

| Layer | Tool | When |
| --- | --- | --- |
| RAG | `mcp__tlx__docs_query` | semantic search the wiki |
| Static | `mcp__tlx__js_index_target`, `js_get_chains`, `js_examine_chain`, `js_get_snippet` | callgraph + chain inspection |
| Static | `mcp__tlx__js_run_audit`, `js_audit_status` | Opus advisor pipeline |
| Dynamic mock | `mcp__tlx__mock_start`, `mock_extract`, `mock_run`, `mock_confirm`, `mock_stop` | headless sink confirmation |
| Reporting | `mcp__tlx__js_export_findings`, `js_submit_finding` | SARIF + submission |
| Proxy | `caido` MCP | live request capture + replay |
| Browser | `chrome-devtools` MCP | real Chrome via DevTools Protocol |
| Browser | `playwright` MCP | headless for mock confirm |
| Docs | `context7` MCP | up-to-date library/framework docs |

---

## 7. Hard rules reminder

From `CLAUDE.md` — never violate even when wiki-query suggests
otherwise:

1. **Scope**: a target's `http.md` is the source of truth. Caido scope
   rules are second line of defense.
2. **Auth secrets**: never write raw cred values into `targets/` or
   `wiki/`. Reference Caido workflow IDs or env vars only.
3. **Destructive HTTP**: no DELETE / PUT / POST that mutates prod state
   without per-request confirmation.
4. **Opus budget**: `opus-deep-audit` capped at
   `memory.md > opus_budget_per_target`. Track in
   `status.json.opus_cost`.
5. **Wiki edits**: append-and-cross-link; never delete a wiki page
   without OK.

---

## 8. Quick reference — slash commands

| Command | What |
| --- | --- |
| `/status [target]` | pipeline phase pointer |
| `/budget [target]` | Opus + Caido spend so far |
| `/wiki-query <q>` | search the wiki |
| `/wiki-lint` | wiki health check |
| `/loop <minutes>` | autoresearch on current target |
| `/replay <id> [variant]` | re-run a Caido replay batch |
| `/snippet <qname>` | fetch source for a function by qualified name |
| `/graphify ...` | knowledge graph over tlx/ + skills/ + wiki/ |

Skills available (invoke via name in conversation, no slash needed
unless wired):

`target-init`, `js-harvest`, `sourcemap-explode`, `rag-ingest`,
`js-index`, `chain-triage`, `dom-xss-hunt`, `opus-deep-audit`,
`autoresearch-loop`, `browser-confirm`, `report-finding`,
`wiki-ingest`, `wiki-query`, `wiki-lint`, `caido-capture`,
`caido-replay`, `caido-idor`.
