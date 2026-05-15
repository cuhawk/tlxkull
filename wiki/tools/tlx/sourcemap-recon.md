---
title: Hidden sourcemap recon (Sentry + filename brute)
slug: tlx-sourcemap-recon
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [tool/tlx, tool/recon, technique/recon, javascript]
inbound: []
---

# Hidden sourcemap recon

## Why bother

TLX's `js-harvest` already follows `sourceMappingURL` comments and
the `X-SourceMap` header. That misses two common cases:

1. **Webpack `devtool: 'hidden-source-map'`** — strips the
   `sourceMappingURL` comment but still emits the `.map` to disk.
   The map ships to CDN by accident (or for Sentry upload). No
   inline marker, but the file is at the predictable path next to
   the bundle.
2. **Sentry release-artifact API** — self-hosted and many
   misconfigured cloud Sentry instances expose
   `/api/0/projects/{org}/{proj}/releases/{ver}/files/?token=...`
   world-readable. Maps live there even if `.js.map` paths return
   404 at the CDN.

Together these unlock unminified source on a meaningful fraction of
targets where TLX currently falls back to minified analysis.

## Filename brute list

Append after the standard `sourceMappingURL` pass:

```text
# next to each bundled .js, try:
<basename>.js.map
<basename>.<8-hex>.js.map        # webpack content hash
<basename>.min.js.map

# common static-asset roots:
assets/index-<8-hex>.js.map      # vite default
assets/index.js.map
static/js/main.<8-hex>.chunk.js.map   # CRA
static/js/main.chunk.js.map
static/js/bundle.js.map

# next.js:
_next/static/chunks/<id>.js.map
_next/static/chunks/pages/<page>-<hash>.js.map
_next/static/<buildId>/_buildManifest.js.map

# nuxt:
_nuxt/<entry>.js.map

# rspack / turbopack:
.next/build/chunks/<id>.js.map
.turbo/chunks/<id>.js.map

# legacy:
debug.js.map
app.js.map
main.js.map
vendor.js.map
runtime.js.map
polyfills.js.map
```

## Sentry artifact pull

```bash
# detect Sentry:
grep -RhoE 'https://[^"'"'"']*sentry[^"'"'"']*' targets/<name>/raw/ \
  | sort -u

# if any DSN or self-hosted host found, try:
curl -s "https://<sentry-host>/api/0/projects/<org>/<proj>/releases/" \
  | jq '.[].version'
# for each release version:
curl -s "https://<sentry-host>/api/0/projects/<org>/<proj>/releases/<ver>/files/?per_page=100" \
  | jq -r '.[] | select(.name|endswith(".map")) | .name'
# then:
curl -s "https://<sentry-host>/api/0/projects/<org>/<proj>/releases/<ver>/files/<id>/?download=1" \
  > targets/<name>/raw/<name>.js.map
```

Common-public Sentry self-hosted endpoints (Helm chart defaults):

- `sentry.<corp>.com`
- `errors.<corp>.com`
- `tracking.<corp>.com`

## Detection bits worth caching

- DSN in any bundle (`https://<key>@<host>/<id>`) — strip secret,
  keep host + project id for the artifact API.
- `__SENTRY__` global in the bundle's runtime.
- `release: <ver>` literal — gives the exact release tag to query.

## TLX integration

Drop into `js-harvest` after the sourceMappingURL pass. Outline:

```python
# bin/js-harvest extension (sketch)
def hidden_map_recon(target_dir):
    for js in target_dir.glob("raw/**/*.js"):
        for candidate in BRUTE_PATHS_FOR(js):
            if fetch_quiet(candidate):
                save(candidate, target_dir / "raw")
    for host, org, proj in detect_sentry(target_dir):
        for ver in list_releases(host, org, proj):
            for f in list_release_files(host, org, proj, ver):
                if f.endswith(".map"):
                    save(download_release_file(...), target_dir / "raw")
```

Then `sourcemap-explode` picks the new `.map` files up automatically
on next run.

## Caveats

- Rate-limit aware — keep brute list per-bundle, not per-target;
  most CDNs serve 404 cheaply, but some 429 after ~50 missed
  requests.
- Stay in scope. Sentry instances are often subdomains of the
  primary target; check `http.md` before pulling. If Sentry is
  *out* of scope, do not query the artifact API.
- Respect `unwebpack-sourcemap` license if porting code; Apache 2.0.

## Related

- [[../karpathy/source-code-review]] — Phase 1, "obtain source"
  ranks sourcemap as #3 priority.
- [[../tlx/ai-whitebox-workflow]].
- [[../../techniques/recon/ai-whitebox-source-review]] —
  downstream skill that needs unminified bodies.

## Sources

- Sentry "Abusing Exposed Sourcemaps" — <https://blog.sentry.security/abusing-exposed-sourcemaps/>
- `rarecoil/unwebpack-sourcemap` — <https://github.com/rarecoil/unwebpack-sourcemap>
- CT Ep 137 — hidden-source-map mentioned as Claude Code's own
  release accident.
