---
name: wiki-dream
description: Offline wiki curator — walks recent tail data (autoresearch, findings, audits, podcasts), dispatches subagents to distill candidate patches into wiki-staging/. Non-destructive. Trigger: /wiki-dream, "run wiki dream", "dream over recent findings".
---

# wiki-dream

## Purpose

Anthropic's 2026 "dreaming" pattern: while the operator sleeps, an offline
curator re-reads recent agent memory (tail data) and distills it into
candidate updates for the long-term knowledge store. Applied here, the
"memory" is the union of:

- per-target autoresearch logs (hypotheses + outcomes),
- confirmed TP and failed FP findings,
- opus audit JSON + markdown (especially verifier-downgraded records),
- podcast distill logs (episodes ingested but not yet distilled),
- stale `inbox/*/READY` markers (pending ingest work).

`wiki-dream` reads that tail, fans out Claude-Code subagents per (target,
source-bucket) pair, and writes their JSON diff proposals as
human-readable patches under `wiki-staging/<utc>/`. The user reviews
the summary and promotes selected patches into `wiki/` manually. This
preserves the wiki-lint "append + cross-link only" policy and keeps a
human in the loop for every wiki write.

Every LLM call is a Claude Code subagent — no `ANTHROPIC_API_KEY`,
`google.genai`, or `GeminiEngine` use. Subagents are **read-only**.

## Hard rules

- **Non-destructive.** This skill NEVER edits `wiki/` directly. Only
  writes to `wiki-staging/<utc>/`. The only mutation of `wiki/` happens
  during `promote`, which is human-initiated.
- **Subagents are read-only.** They may `Read`/`Grep`/`Glob` across
  `targets/*/`, `wiki/`, `tlx/`, `plans/`, `notes/`, `inbox/`. The MCP
  call `mcp__tlx__docs_query` with `collection="wiki"` is allowed for
  retrieval. Nothing else. No file writes, no MCP mutations.
- **No Anthropic-API direct calls.** Per `CLAUDE.md` rule 7. The wiki
  RAG collection (`wiki` chroma, 3072d Gemini embeddings) is
  grandfathered for re-embedding *on promote* only — not during dream.
- **Schema enforced on ingest.** `bin/wiki_dream.py ingest` rejects
  proposals missing required keys, proposals that try to delete content
  (additions + cross-refs only), and `action=new` patches whose target
  path does not end in `.md`.
- **Bucket grouping.** Each subagent handles ONE source bucket per
  target. Never mix `coralbug3-syn autoresearch` with
  `netlify-h1 findings` in a single prompt — keeps evidence focused
  and makes patch attribution traceable.
- **Default `--hours = 24`.** Don't run with `--hours > 720` (30 days)
  — too much noise to curate in one pass.
- **Backlog gate.** If `wiki-staging/<latest>/_summary.md` exists and
  was modified more recently than the latest entry in
  `wiki/_ingest_log.jsonl` referencing that run, refuse to start a
  new dream run. The user must drain the backlog (promote or delete)
  first. Override with `--force` only for emergencies.
- **Cross-ref pending allowed.** Cross-refs pointing to non-existent
  wiki pages are kept but flagged `cross_ref_pending` in the patch —
  this is intentional discovery breadcrumbing per wiki-lint policy.

## Inputs

| Source | Required | Why we read it |
| --- | --- | --- |
| `targets/*/autoresearch.jsonl` | optional | New techniques tried, hypotheses dropped, recurring sanitizer patterns |
| `targets/*/findings/*/confirmed.json` | optional | Confirmed TPs not yet in `wiki/_ingest_log.jsonl` |
| `targets/*/findings/*/failed.json` | optional | FPs that taught us why static fired but runtime didn't |
| `targets/*/opus/*.json` | optional | Audit records, especially those with `_verifier_history[]` (downgrades) |
| `targets/*/opus/*.md` | optional | Long-form audit reasoning |
| `targets/*/two_judge/*.json` | optional | Verifier records — surface sloppy audits |
| `wiki/sources/podcasts/*/_distill_log.jsonl` | optional | Episodes ingested but flagged `no_distill` or `needs_review` |
| `inbox/*/READY` | optional | Untouched > 24h — pending ingest work |
| RAG collection `wiki` | optional | Subagent retrieval only (read-only `docs_query`) |
| `wiki/_ingest_log.jsonl` | required | Diff baseline: skip sources already ingested |

## Steps

The skill is **driven by Claude Code in this conversation**. Python
helpers handle file I/O + schema validation; Claude dispatches the
subagents.

### Step 1 — Phase 1: gather

```bash
python3 bin/wiki_dream.py gather --hours 24
```

Or scoped:

```bash
python3 bin/wiki_dream.py gather --hours 168 --target coralbug3-syn
```

`gather` walks the source list above within the `--hours` window
(by file mtime), groups items by `(target, bucket)` where bucket is
one of `autoresearch | findings_confirmed | findings_failed | opus |
verifier | podcast | inbox_stale`. For each non-empty (target, bucket)
pair, it writes a prompt body to
`wiki-staging/<utc>/_prompts/<target>__<bucket>.md`, capping evidence
at ~6000 chars (most recent items kept on overflow).

`_manifest.json` is also written to the run dir listing every prompt
and its expected response path.

### Step 2 — Phase 2: fan out subagents

For each prompt in `wiki-staging/<run>/_manifest.json`, Claude
dispatches ONE read-only subagent. Example dispatch:

```
Agent(
  subagent_type="general-purpose",
  description="wiki-dream distill <target>::<bucket>",
  prompt=<contents of wiki-staging/<run>/_prompts/<target>__<bucket>.md>,
)
```

Subagent constraints (already in the prompt body, but the runner
reminds Claude here too):

- Read-only. No file writes. No MCP mutations.
- Allowed: `Read`, `Grep`, `Glob` against `targets/*/`, `wiki/`,
  `tlx/`, `plans/`, `notes/`, `inbox/`. Allowed MCP:
  `mcp__tlx__docs_query` with `collection="wiki"`. Nothing else.
- Output JSON only matching the schema in `prompts/distill.md`.

Capture each subagent JSON response to a temp file, e.g.
`wiki-staging/<run>/_responses/<target>__<bucket>.json`.

### Step 3 — Phase 3: ingest each response

```bash
python3 bin/wiki_dream.py ingest \
    --bucket <target>__<bucket> \
    --response-file wiki-staging/<run>/_responses/<target>__<bucket>.json
```

`ingest` validates the JSON schema (see below), then for each entry in
`proposed_patches[]` writes a human-readable patch file:

```
wiki-staging/<run>/<bucket>__<safe-slug>.patch.md
```

Each patch file shows:

- target wiki page path
- action (`append` | `new`)
- current content excerpt (first 40 lines if page exists; otherwise
  `"page does not exist"`)
- proposed addition (raw markdown block, clearly fenced)
- cross-refs to add (numbered list, with `cross_ref_pending` flag if
  the `from_page` doesn't exist)
- evidence (numbered list, source path + excerpt)
- rationale (1-3 sentences from the subagent)

Schema validation rejects:

- missing required keys (`bucket`, `target`, `proposed_patches`,
  `confidence`)
- `wiki_page` that doesn't end in `.md`
- `action == "new"` for a path that already exists in `wiki/`
- any attempt to "remove" content (no `removal_markdown` key, only
  `addition_markdown`)
- any verdict-laundering keys (`tp`, `fp`, `true_positive`,
  `verdict`, `classification`) — stripped automatically

Schema failures append to `wiki-staging/<run>/_errors.jsonl` and
return exit 2. Do not retry by hammering the subagent — surface to
user.

### Step 4 — Phase 4: summary

```bash
python3 bin/wiki_dream.py summary --run <utc>
```

Writes `wiki-staging/<run>/_summary.md`:

```markdown
# wiki-dream run <utc>

<one-paragraph overview: counts by bucket + target, total patches,
new pages vs append, confidence distribution>

## Proposed patches

1. <bucket>::<target> -> <wiki_page> (action) - <rationale[:80]>
2. ...

## Promote with

python3 bin/wiki_dream.py promote --run <utc> --patches <comma-ids>
```

### Step 5 — Phase 5: promote (manual, human-initiated)

The user reads the summary, decides which patches to apply. Then:

```bash
python3 bin/wiki_dream.py promote --run <utc> --patches 1,3,5
```

Or to promote everything:

```bash
python3 bin/wiki_dream.py promote --run <utc> --all
```

`promote` for each named patch:

- `action=append`: append the `addition_markdown` section to the
  named wiki page (creating intermediate dirs if needed).
- `action=new`: create the page with the addition_markdown as full
  body. Patch must include `title_if_new`.
- `cross_refs_to_add[]`: for each entry, locate `from_page` and
  append the link near the bottom, in a `## Related` section if one
  exists; otherwise create that section. If `from_page` doesn't
  exist, log `cross_ref_pending` to the ingest log and skip the link
  (the wiki-lint pass will surface it later).
- Append one row to `wiki/_ingest_log.jsonl`:
  `{ts, run_id, bucket, target, wiki_page, action, source_dream_patch}`.

After promote, run `wiki-lint` (manually or via the next cron) to
detect new orphans / dangling links introduced by the additions.

## Subagent dispatch — Phase 2 example

```
manifest = json.loads(Path("wiki-staging/<run>/_manifest.json").read_text())
for entry in manifest["prompts"]:
    bucket = entry["bucket"]
    prompt_path = entry["prompt_path"]
    response_path = entry["response_path"]

    # Dispatch ONE subagent per bucket. Read-only, JSON-only output.
    response = Agent(
        subagent_type="general-purpose",
        description=f"wiki-dream distill {bucket}",
        prompt=Path(prompt_path).read_text(),
    )
    Path(response_path).write_text(response)

    # Ingest immediately so partial progress is not lost on crash.
    subprocess.run([
        "python3", "bin/wiki_dream.py", "ingest",
        "--bucket", bucket,
        "--response-file", response_path,
    ], check=True)
```

## Subagent JSON response schema

```json
{
  "bucket": "<bucket name>",
  "target": "<source target>",
  "proposed_patches": [
    {
      "wiki_page": "<relative path under wiki/, e.g. wiki/techniques/dom-xss/foo.md>",
      "exists": true,
      "action": "append",
      "title_if_new": "<only when action=new>",
      "addition_markdown": "<the actual markdown to add - full section>",
      "cross_refs_to_add": [
        {"from_page": "<existing wiki page>",
         "link_text": "<text>",
         "link_target": "<wiki/path.md>"}
      ],
      "evidence": [
        {"source_kind": "autoresearch|finding|opus|verifier|podcast|inbox",
         "source_path": "<path>",
         "excerpt": "<<=200 chars>"}
      ],
      "rationale": "<1-3 sentences why this should be added>"
    }
  ],
  "skipped_items": [
    {"item": "<short identifier>", "reason": "<short reason>"}
  ],
  "confidence": "high | medium | low",
  "blocking_unknowns": []
}
```

## Outputs

- `wiki-staging/<run>/_prompts/<bucket>.md` — per-bucket prompt bodies
- `wiki-staging/<run>/_manifest.json` — bucket -> {prompt_path, response_path, item_count}
- `wiki-staging/<run>/_responses/<bucket>.json` — captured subagent responses
- `wiki-staging/<run>/<bucket>__<slug>.patch.md` — human-readable patches
- `wiki-staging/<run>/_summary.md` — overview + numbered patch list
- `wiki-staging/<run>/_errors.jsonl` — schema/ingest failures
- `wiki/_ingest_log.jsonl` — appended one row per promoted patch

## Failure modes

| Symptom | Action |
| --- | --- |
| Subagent emits prose instead of JSON | Re-issue the prompt once with `Output JSON only — do not prefix any commentary.` appended. If still bad, log to `_errors.jsonl` and skip. |
| Subagent proposes deletion (e.g. emits `removal_markdown`) | Ingest strips the key automatically and logs to `_stripped_keys`. |
| Subagent proposes `action=new` for an existing path | Ingest rejects with exit 2; user must inspect manually. |
| `action=new` path doesn't end in `.md` | Ingest rejects with exit 2. |
| Cross-ref `from_page` doesn't exist | Kept in patch with `cross_ref_pending` flag; surfaced later by wiki-lint. |
| Backlog gate triggers (prior summary unread) | Drain first, or pass `--force` if user confirms. |
| `--hours > 720` | Reject with exit 2; the curation surface is too large. |
| No items found in the window | Exit 0 with `"no items in window"` message; no run dir created. |

## Result block

`wiki-staging/<run>/_summary.md` is the primary artifact. A machine
counterpart lives in `wiki-staging/<run>/_summary.json`:

```json
{
  "run_id": "<utc>",
  "hours_window": 24,
  "buckets_prepared": N,
  "patches_generated": K,
  "by_action": {"append": ..., "new": ...},
  "by_confidence": {"high": ..., "medium": ..., "low": ...},
  "by_bucket": {"autoresearch": ..., "findings_confirmed": ..., ...},
  "errors": M
}
```

Promote operations append to `wiki/_ingest_log.jsonl` and print a
final count of pages_touched / pages_created.

## When to run

- Nightly remote agent (scheduled), `--hours 24`.
- After a burst of audit/confirm activity on a single target,
  `--hours 48 --target <name>`.
- Weekly catch-up over `--hours 168` after sustained engagement.

Skip on days where no autoresearch / findings / opus activity
occurred — `gather` will exit 0 with `no items in window` and no
run directory is created.
