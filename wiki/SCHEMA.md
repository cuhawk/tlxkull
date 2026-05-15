# wiki/SCHEMA.md — llmwiki Structure

This is the schema document for the personal LLM-maintained wiki. It
implements Karpathy's llmwiki pattern (see
`https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`):
raw sources → wiki pages → schema-doc. **This file is the
schema-doc.** The LLM consults it whenever it edits the wiki.

---

## Layout

```
wiki/
├── SCHEMA.md           # this file — never auto-edit
├── _ingest_log.jsonl   # append-only log of wiki-ingest invocations
├── _lint_<YYYYMMDD>.md # wiki-lint reports (one per run)
├── _external/          # vendored OSS knowledge bases (git submodules / clones)
│                       # NOT in `wiki` RAG collection. Indexed separately as
│                       # `external` collection if embedded at all. .gitignore'd.
├── sources/            # raw inbox — articles, podcasts, videos, gists
│   └── podcasts/<show>/ # transcripts grouped by show
├── payloads/           # canonical payload library by sink_kind
│   └── <sink_kind>/<slug>.md
├── targets/            # per-bounty-program intel (NOT engagement work dirs)
├── techniques/         # bug-class patterns
├── tools/              # caido, tlx, browser, karpathy
├── people/             # researcher/hunter dossiers (blog index, handles, focus)
└── findings/           # past confirmed findings, cross-linked
```

### Naming

- All page filenames are `kebab-case.md`.
- All slugs are stable. Renames are explicit; lint will flag
  dangling links.
- Findings use the same id as `targets/<name>/findings/<id>/` so
  cross-links work both ways.

### Frontmatter (every wiki page)

```markdown
---
title: <human title>
slug: <kebab-case-slug>
created_utc: <iso>
updated_utc: <iso>
tags: [tag1, tag2, ...]
inbound: [path/to/page1.md, path/to/page2.md]   # maintained by wiki-lint
---
```

`inbound` is a derived field. Don't hand-edit; `wiki-lint` rebuilds it.

---

## Per-folder conventions

### `wiki/targets/<program>.md`

A living dossier for one bounty program. Sections (in this order):

1. **Snapshot** — payout range, rate-limit history, payout speed.
2. **Scope quirks** — anything non-obvious about scope.
3. **Auth quirks** — login flow, 2FA, session lifetime.
4. **Prior findings** — bullet list of `[id](../findings/<id>.md)`.
5. **Prior FPs that taught us something** — bullet list.
6. **Sub-targets** — child pages if program is huge.

Tags: `target/<program-name>`.

### `wiki/techniques/<class>/<pattern>.md`

A specific exploit pattern within a bug class. Sections:

1. **Pattern** — the high-level abstract.
2. **Preconditions** — what must be true for this to apply.
3. **Detection** — how to spot it statically (js_analyzer hints).
4. **Triggering** — how to actually fire it dynamically.
5. **Bypasses** — known bypasses for common defenses.
6. **Seen-in-the-wild** — append-only list of `{date, target, finding_id}`.
7. **References** — external links, CVEs.

Tags: `technique/<class>`, `technique/<pattern>`.

### `wiki/tools/<tool>/<note>.md`

Practical notes on a tool. Format is free; keep one tool per page if
possible. Examples:
- `wiki/tools/caido/cert-trust.md`
- `wiki/tools/caido/graphql-quirks.md`
- `wiki/tools/tlx/framework-overrides.md`
- `wiki/tools/browser/proxy-setup.md`
- `wiki/tools/karpathy/llmwiki.md` (canonical Karpathy notes)
- `wiki/tools/karpathy/autoresearch.md`

Tags: `tool/<tool>`.

### `wiki/sources/<slug>.md`

Raw inbox entry. One file per ingested external source (article, gist,
talk, podcast episode, video). Preserved verbatim — Karpathy's "raw
sources" layer. Skills (`wiki-ingest`) extract patterns into
`techniques/` / `tools/` and back-link to the source.

Frontmatter MUST include:
- `url` — canonical URL fetched from.
- `fetched_utc` — ISO timestamp of fetch.
- `kind` — one of `article | gist | podcast | video | thread | repo-snippet`.
- `extracted` — `true | false` (set by `wiki-ingest` when extraction pass done).
- `extract_model` — `sonnet | opus | manual` when extracted.

Body: cleaned markdown of the source. For podcasts/videos: full transcript.

Tags: `source`, plus topic tags.

### `wiki/payloads/<sink_kind>/<slug>.md`

Canonical payload registry. One payload (or tight family) per file.

Sections:
1. **Payload** — the exact string(s), code-fenced.
2. **Context** — when this fires (sink type, framework, sanitizer in play).
3. **Provenance** — which `sources/` page or finding it came from.
4. **Linked techniques** — links to `techniques/<class>/<pattern>.md`.

Tags: `payload`, `sink/<sink_kind>`.

### `wiki/_external/<repo>/`

Vendored OSS knowledge bases (e.g. PayloadsAllTheThings, HackTricks).
Cloned in-place. Treat as read-only — do not edit upstream files.

- NOT auto-embedded into `wiki` RAG collection (too noisy + license
  concerns).
- `wiki/_external/<repo>/INDEX.md` (created by `wiki-ingest`) holds a
  one-paragraph summary + pointers to high-value subtrees + links from
  our `techniques/` pages.
- Cross-link FROM our techniques INTO `_external/...` using relative
  paths.

### `wiki/people/<slug>.md`

Researcher / hunter dossier. One page per person we track (CT podcast
hosts + guests, PortSwigger researchers, anyone whose blog/research we
ingest). Use real-name slug when known, else handle.

Sections (in this order):

1. **Identity** — real name, primary handle, role (host | hunter | researcher | vendor-eng).
2. **Focus areas** — 2-5 bullet tags (e.g. `client-side`, `oauth`, `mobile`, `IoT`).
3. **Online presence** — bullet list of `[label](url)`: blog, X/Twitter,
   GitHub, talks, company. Use raw URLs only — no auth secrets.
4. **Key research / posts** — 3-10 bullet items. Each: title + URL + 1-line takeaway.
   Cross-link to `wiki/techniques/<class>/<pattern>.md` when the post seeded a wiki technique page.
5. **CT podcast appearances** — bullet list `[YYYY-MM-DD Ep N — title](../sources/podcasts/ct/<file>.en.vtt)`.
6. **Notes** — free-form: collab style, signature techniques, recurring themes.

Frontmatter MUST include:
- `handles` — list of known online handles (lowercase).
- `role` — one of `host | hunter | researcher | vendor-eng | dual`.
- `primary_focus` — single tag from focus areas list.

Tags: `person`, `role/<role>`, plus each focus tag (`focus/client-side` etc.).

Index file: `wiki/people/_index.md` — one-line-per-person table with
slug, real name, handle, role, focus, CT-eps-count. Maintained by
`wiki-ingest` when a new people page is added.

### `wiki/findings/<id>.md`

The wiki-side mirror of an engagement finding. Distilled — full
writeup stays in `targets/<name>/findings/<id>/`. Sections:

1. **One-paragraph distilled story.**
2. **Pattern slug** — link to `techniques/<class>/<pattern>.md`.
3. **Target** — link to `targets/<program>.md`.
4. **Tools used** — links to `tools/...`.
5. **Lesson learned** — single sentence that applies beyond this
   one bug.

Tags: `finding`, plus the technique + target tags.

---

## Cross-link rules

1. Every new finding page MUST link to: one technique page, one
   target page, and ≥1 tool page.
2. Every new technique page MUST be linked-from ≥1 existing
   technique or finding page within 24 hours of creation. `wiki-lint`
   surfaces orphans daily.
3. Cross-links use relative paths, not URLs.
4. Backlinks (`inbound:` in frontmatter) are computed by `wiki-lint`;
   never hand-maintain.

## Editing protocol (`wiki-ingest`)

- One source → multiple pages → single ingest transaction.
- Idempotent: re-ingesting the same source updates `updated_utc` and
  may add new cross-refs, but never duplicates a "Seen-in-the-wild"
  entry that already has the same `{date, finding_id}`.
- Always append the source path to `wiki/_ingest_log.jsonl` so the
  full audit trail is reconstructable.

## Lint protocol (`wiki-lint`)

- Reports never auto-delete. They surface candidates; user decides.
- Orphans older than 30 days get flagged again at higher priority.
- Contradiction detection uses a single-shot LLM judge on candidate
  page pairs that share entity tags.

## Out-of-scope content

- Raw Opus transcripts → stay in `targets/<name>/opus/`. Not in wiki.
- Per-engagement intermediate state → stays in `targets/<name>/`.
- Secrets / cookies / tokens → never in any wiki page. Use Caido
  workflow references only.
