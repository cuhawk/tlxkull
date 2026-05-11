---
name: js-harvest
description: Crawl an in-scope target and download every JS file plus public sourcemap. Use after target-init when targets/<name>/raw/ is missing. Reads scope from status.json. Walks pages via chrome-devtools MCP, enumerates <script src=>, dynamic imports, and webpack chunks, fetches the assets, and discovers .js.map siblings via sourceMappingURL pragma / X-SourceMap header / common relative paths.
---

# js-harvest

## Purpose
Acquire every JavaScript asset the target ships, plus every sourcemap
that is publicly accessible, so later phases can analyze original
sources rather than minified bundles.

## Inputs
- `targets/<name>/status.json` with `scope.in` populated.

## Steps
1. Read scope. For each in-scope host, queue the bare host root as the
   first URL.
2. Use `chrome-devtools` MCP `navigate_page`, then
   `list_network_requests` and `evaluate_script` to enumerate:
   - every `<script src>` (including async/defer)
   - every dynamic `import()` (regex pass on inline JS as fallback)
   - every webpack chunk URL referenced by the first script
3. For each JS URL, fetch through chrome-devtools (so cookies + proxy
   apply). Save under `targets/<name>/raw/<host>/<path>.js`.
4. Sourcemap discovery for each JS:
   - `//# sourceMappingURL=...` pragma at file end
   - `SourceMap` / `X-SourceMap` response header
   - try `<url>.map` if pragma/header absent
5. Save discovered maps as siblings: `<path>.js.map`. If a map is
   referenced but returns 4xx, log to `status.json.harvest.missing_maps[]`.
6. Crawl follow-ups: respect a depth limit (default 2 hops on
   in-scope hosts only). Do not follow out-of-scope links — log them
   to `status.json.harvest.out_of_scope_skipped[]`.

## Outputs
- `targets/<name>/raw/<host>/<path>.js[.map]`
- updated `status.json.phases.harvest`

## Failure modes
- chrome-devtools MCP not responding → suggest `chrome-devtools-mcp:troubleshooting`.
- Auth-walled site (login redirect) → load Caido auth workflow first
  (`caido_login(workflow_id=...)`), then re-run.
- Hitting rate limits → back off; log; resume.

## Result block
```json
"phases": { "harvest": { "status": "done", "ts": "<iso>",
  "files": N, "maps_public": M, "maps_missing": K,
  "hosts_seen": [...], "out_of_scope_skipped": [...] } }
```
