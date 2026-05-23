---
name: ctbb-ingest
description: Critical Thinking Bug-Bounty podcast inbox processor. RAG-ingest transcripts into wiki collection, distill techniques/tools/targets into wiki pages, run wiki-lint. Idempotent. Trigger: /ctbb-ingest or auto-fire by scheduled remote agent.
---

# ctbb-ingest

## Purpose
Convert a freshly-transcribed Critical Thinking podcast episode into:
1. searchable chunks in the `wiki` RAG collection
2. cross-linked wiki pages capturing every technique, tool, target,
   and finding mentioned

Driven from `inbox/ctbb/` markers produced by `bin/ctbb-poll.sh`. All
prose synthesis (distillation) runs as Claude Code in this conversation
— never as an autonomous Sonnet/Flash call. RAG embedding (`wiki`
collection, Gemini 3072d) is grandfathered per the API-key whitelist.

## Inputs
- `inbox/ctbb/<vid>/READY` markers
- `inbox/ctbb/<vid>/base` (the `<YYYYMMDD>_<vid>_<title>` basename)
- `inbox/ctbb/<vid>/transcript.txt` (symlink to the .txt under
  `wiki/sources/podcasts/ct/whisper/transcripts/`)

## Steps

For each `inbox/ctbb/<vid>/READY`:

### 1. RAG ingest
Run:
```
python bin/ingest_ct_transcripts.py
```
The script is idempotent — it skips episodes whose first chunk id
already exists in the `wiki` collection. Capture stdout, append to
`targets/`-style status under `wiki/sources/podcasts/ct/whisper/_rag_log.jsonl`
(handled by the script).

### 2. Selective distill
Read the transcript. In **one Claude pass** per episode, extract:
- **techniques** mentioned with non-trivial substance (e.g., DOM
  clobbering trick, header confusion, OAuth quirk). Skip mere
  name-drops.
- **tools** discussed with operational signal (new feature, gotcha,
  benchmark) — not just "we use Caido".
- **targets / programs** discussed (HackerOne / Bugcrowd / Synack
  program names, BBP scope news).
- **findings** publicly disclosed in the episode (rare but high
  value).

For each extracted item:
- Route to `wiki/techniques/<slug>/`, `wiki/tools/<name>/`,
  `wiki/targets/<program>.md`, or `wiki/findings/<id>.md`.
- Use `wiki-ingest` skill conventions:
  - Create the page if missing (follow `wiki/SCHEMA.md`).
  - Append to "Seen-in-the-wild" / "Notes from the field" with
    source `[CT Ep. NN](wiki://podcasts/ct/<base>)` and a timestamp.
  - Cross-link to at least one existing wiki page.
- Skip items already recorded (search the destination page for the
  same `[CT Ep. NN]` link — if present, do nothing).

Discipline:
- Only fire wiki-ingest sub-steps inline. Do NOT bulk-Claude-summarize
  the whole transcript. The transcript itself is already in RAG.
- If the episode is entirely interview/meta with no technique substance,
  log "no_distill" to `_distill_log.jsonl` and move on.

### 3. Re-embed touched wiki pages
After distill writes are done for the episode, run:
```
python bin/reingest_ct_pages.py
```
so `docs_query` reflects the new state.

### 4. Mark done
- Append to `wiki/sources/podcasts/ct/_distill_log.jsonl`:
  ```json
  {"ts": "...", "vid": "...", "ep": NN, "base": "...",
   "techniques": [...], "tools": [...], "targets": [...],
   "findings": [...], "no_distill": false}
  ```
- Replace `inbox/ctbb/<vid>/READY` with `inbox/ctbb/<vid>/DONE`
  (preserve the rest of the dir for audit).

### 5. After all episodes done
Run wiki-lint exactly once for the batch:
```
python bin/wiki_lint.py
```
or invoke the `wiki-lint` skill if interactive review is wanted.

## Idempotency contract
- Re-running with no new READY markers → no-op.
- Re-running on a vid already in `_distill_log.jsonl` → skip distill,
  still re-run RAG ingest (which is itself idempotent).
- `DONE` markers are never deleted by this skill.

## Failure modes
- Transcript missing or empty → mark `inbox/ctbb/<vid>/ERROR` with the
  reason, surface to user, skip.
- `GOOGLE_API_KEY` missing → fatal; abort with the exact error text.
- Distill produces zero items but Claude judges the episode had substance
  (e.g., truly novel content) → flag as `needs_review` instead of
  `no_distill`.

## Result block
```json
{
  "ts": "...",
  "skill": "ctbb-ingest",
  "episodes_processed": N,
  "pages_touched": [...],
  "pages_created": [...],
  "lint_report": "wiki/_lint_<YYYYMMDD>.md"
}
```
Append to `targets/`-equivalent: `wiki/sources/podcasts/ct/_pipeline_log.jsonl`.
