---
name: wiki-lint
description: Karpathy llmwiki periodic health check. Scan wiki/ for orphans (pages with no inbound links), contradictions (claims that conflict across pages), gaps (cross-refs to pages that don't exist), and stale entries (techniques unseen in N months). Writes wiki/_lint_<YYYYMMDD>.md and surfaces actionable items to user. Trigger: /wiki-lint or weekly cron.
---

# wiki-lint

## Purpose
Maintain wiki hygiene. Karpathy's third llmwiki operation: contradicts,
orphans, gaps. Lint *reports*; user *decides*. Lint never auto-deletes.

## Inputs
- `wiki/**`

## Steps
1. Build link graph: every `[text](path)` in markdown.
2. Detect:
   - **Orphans** — pages with zero inbound links (excluding
     `SCHEMA.md` and `findings/<id>.md` which are leaves by design).
   - **Dangling links** — `[text](path)` where `path` doesn't exist.
   - **Contradictions** — for any two pages claiming the same
     fact about the same entity, flag if claims differ. Use an
     LLM judge call (single-shot, cheap model) to detect.
   - **Stale entries** — `techniques/*` with no recent
     `Seen-in-the-wild` entry in >180 days.
3. Write report to `wiki/_lint_<YYYYMMDD>.md`:
   ```markdown
   # Wiki lint — YYYY-MM-DD

   ## Orphans (N)
   - wiki/.../foo.md — last touched YYYY-MM-DD

   ## Dangling links (N)
   - wiki/.../bar.md → "missing.md"

   ## Contradictions (N)
   - claim: "..." — page A says X, page B says Y

   ## Stale (N)
   - wiki/techniques/.../stale.md — last seen YYYY-MM-DD
   ```
4. Surface a one-screen summary to the user; full report stays in file.

## Outputs
- `wiki/_lint_<YYYYMMDD>.md`

## Failure modes
- LLM judge call exceeds local cost cap → skip contradiction
  detection; report only structural issues.
- Wiki very large → batch the link-graph pass; this is cheap.

## Resolution flow
User reads report → either edits pages manually OR asks Claude to
"fix orphan X by adding inbound link from <page>". Lint never edits.

## Tooling

- `bin/wiki_lint.py` — structural pass (orphans / dangling / stale).
  Contradictions skipped — LLM call not in CLAUDE.md API whitelist.
- `bin/wiki_backlink_people.py` — appends auto-managed
  `## Ingested blog posts` block (markers `<!-- sources:auto:start/end -->`)
  to `people/<x>.md` for every mapped blog dir under
  `sources/blogs/personal/<dir>/`. Idempotent — re-runs replace the block
  in place.
- `bin/wiki_index_sources.py` — generates `_index.md` in each org/multi-author
  source bucket (hacktivity, p0, bughunters, etc.) + top-level
  `sources/_index.md`. Overwrites only `_index.md` files.
- `bin/wiki_index_categories.py` — generates `_index.md` per subdir under
  `techniques/`, `payloads/`, `tools/`, plus `people/_index.md`,
  `targets/_index.md`, and root `wiki/README.md`.

Routine maintenance order:
```
python3 bin/wiki_backlink_people.py
python3 bin/wiki_index_sources.py
python3 bin/wiki_index_categories.py
python3 bin/wiki_lint.py
```
Re-run after any bulk ingest (CTBB, PortSwigger-TV, blog crawl). All four
are idempotent and safe.
