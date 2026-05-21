---
name: bbre-ingest
description: Bug Bounty Reports Explained (BBRE) YouTube inbox processor. For every READY marker under inbox/bbre/<vid>/, run RAG ingest of the transcript into the wiki collection, then distill techniques/tools/targets/findings mentioned into the appropriate wiki pages (Claude-Code-driven, no autonomous AI calls), then run wiki-lint. Idempotent — skips videos already ingested (txt id already in wiki collection) and skips distill if vid already recorded in wiki/sources/podcasts/bbre/_distill_log.jsonl. Trigger: /bbre-ingest or auto-fire by bbre-poll.sh.
---

# bbre-ingest

## Purpose
Convert a freshly-transcribed BBRE (gregxsunday) video into:
1. searchable chunks in the `wiki` RAG collection
2. cross-linked wiki pages capturing every technique, tool, target,
   and finding mentioned

Driven from `inbox/bbre/` markers produced by `bin/bbre-poll.sh`. All
prose synthesis (distillation) runs as Claude Code in this conversation
— never as an autonomous Sonnet/Flash call. RAG embedding (`wiki`
collection, Gemini 3072d) is grandfathered per the API-key whitelist.

BBRE differs from CT in that nearly every episode is technically dense
(writeup walkthroughs, CVE breakdowns, methodology) — far higher
signal-per-minute than CT's interview-heavy format. Default to *aggressive*
distill: assume each episode has at least one technique worth recording.

## Inputs
- `inbox/bbre/<vid>/READY` markers
- `inbox/bbre/<vid>/base` (the `<YYYYMMDD>_<vid>_<title>` basename)
- `inbox/bbre/<vid>/transcript.txt` (symlink to the .txt under
  `wiki/sources/podcasts/bbre/whisper/transcripts/`)

## Steps

For each `inbox/bbre/<vid>/READY`:

### 1. RAG ingest
Run:
```
tlx/.venv/bin/python bin/ingest_bbre_transcripts.py
```
The script is idempotent — it skips videos whose first chunk id
already exists in the `wiki` collection. ID prefix `bbre:`, source
metadata `bbre_youtube`.

### 2. Selective distill
Read the transcript. In **one Claude pass** per video, extract:
- **techniques** mentioned with non-trivial substance (CVE walkthroughs,
  novel primitives, sanitizer bypass tricks, methodology). BBRE
  baseline = at least one technique per video.
- **tools** discussed with operational signal (new tool releases,
  configuration tips, gotchas).
- **targets / programs** discussed (HackerOne / Bugcrowd / Synack
  program names, BBP scope news, vendor disclosures).
- **findings** publicly disclosed in the video (BBRE specializes in
  this — most videos walk through 1+ public report).

For each extracted item:
- Route to `wiki/techniques/<slug>/`, `wiki/tools/<name>/`,
  `wiki/targets/<program>.md`, or `wiki/findings/<id>.md`.
- Use `wiki-ingest` skill conventions:
  - Create the page if missing (follow `wiki/SCHEMA.md`).
  - Append to "Seen-in-the-wild" / "Notes from the field" with
    source `[BBRE](wiki://podcasts/bbre/<base>)` and a timestamp.
  - Cross-link to at least one existing wiki page.
- Skip items already recorded (search the destination page for the
  same `[BBRE]` link with the same `<base>` — if present, do nothing).

Discipline:
- Only fire wiki-ingest sub-steps inline. Do NOT bulk-Claude-summarize
  the whole transcript. The transcript itself is already in RAG.
- If the video is entirely meta/announcement with no technique
  substance, log "no_distill" to `_distill_log.jsonl` and move on.
- For CVE-walkthrough videos, the CVE id + affected vendor/product +
  root cause is the *minimum* extraction.

### 3. Re-embed touched wiki pages
After distill writes are done for the video, run:
```
tlx/.venv/bin/python bin/reingest_ct_pages.py
```
(the existing reingest script now includes `wiki/sources/podcasts/bbre`
in its target list) so `docs_query` reflects the new state.

### 4. Mark done
- Append to `wiki/sources/podcasts/bbre/_distill_log.jsonl`:
  ```json
  {"ts": "...", "vid": "...", "base": "...",
   "techniques": [...], "tools": [...], "targets": [...],
   "findings": [...], "no_distill": false}
  ```
- Replace `inbox/bbre/<vid>/READY` with `inbox/bbre/<vid>/DONE`
  (preserve the rest of the dir for audit).

### 5. After all videos done
Run wiki-lint exactly once for the batch:
```
tlx/.venv/bin/python bin/wiki_lint.py
```
or invoke the `wiki-lint` skill if interactive review is wanted.

## Idempotency contract
- Re-running with no new READY markers → no-op.
- Re-running on a vid already in `_distill_log.jsonl` → skip distill,
  still re-run RAG ingest (which is itself idempotent).
- `DONE` markers are never deleted by this skill.

## Failure modes
- Transcript missing or empty → mark `inbox/bbre/<vid>/ERROR` with the
  reason, surface to user, skip.
- `GOOGLE_API_KEY` missing → fatal; abort with the exact error text.
- Distill produces zero items but Claude judges the video had substance
  → flag as `needs_review` instead of `no_distill`.

## Result block
```json
{
  "ts": "...",
  "skill": "bbre-ingest",
  "videos_processed": N,
  "pages_touched": [...],
  "pages_created": [...],
  "lint_report": "wiki/_lint_<YYYYMMDD>.md"
}
```
Append to `wiki/sources/podcasts/bbre/_pipeline_log.jsonl`.
