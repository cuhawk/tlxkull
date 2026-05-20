# caido-cache-smug

Single-host CLI that sweeps Caido-captured requests for web cache poisoning, web cache deception, HTML smuggling, and optionally HTTP request smuggling.

## Install

```bash
git clone <repo>
cd caido-cache-smug
npm install
npm run build
npm link
```

## Use

```bash
export CAIDO_API_TOKEN=<your-PAT>
caido-cache-smug --host api.acme.example --project acme-2026 --rps 5
```

Output lands at `./out/<host>/<ts>/`:
- `findings.json` — schema_version 1 (see SPEC.md)
- `report.md` — grouped by confidence
- `raw/` — every request and response

## Modules

- **cache-poison** — unkeyed-header, parameter cloaking, URL-parser discrepancy, Cloudflare cache-key header overflow, CDN quirks.
- **cache-deception** — path-append, delimiter discrepancy, cache-buster parameter trick, traversal in cache key, CSPT passive leads.
- **html-smuggling** — Blob/download primitives, form attribute smuggling, URL-credential smuggling, well-known data-type smuggling.
- **smuggling** (flag-gated) — CL.TE, TE.CL, TE.TE, hop-by-hop, H2 downgrade. Requires `--aggressive-smuggling`.

## Rules of engagement

- GET/HEAD only. PURGE is detection-only.
- `--rps` default 5; `--aggressive-smuggling` forces ≤1 rps.
- Pre-flight `y/N` confirmation required for aggressive mode or `--rps > 20`.
- Auth cookies redacted in `report.md`/`findings.json`. Raw transcripts under `raw/` retain originals.

## Spec & plan

- [SPEC.md](SPEC.md)
- [PLAN.md](PLAN.md)
