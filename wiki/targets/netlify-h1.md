---
title: Netlify (HackerOne)
slug: target-netlify-h1
created_utc: 2026-05-18T16:00:00Z
updated_utc: 2026-05-18T16:00:00Z
tags: [target/netlify, target/ci-cd, target/static-hosting, target/h1, platform/hackerone]
inbound: []
---

# Netlify (HackerOne)

## Snapshot

- Platform: HackerOne — https://hackerone.com/netlify
- Type: BBP
- Bounty range: Low $200 / Medium $500 / High $2,500 / Critical $6,000
- Average bounty paid (historical): $200–$250
- Response efficiency: 66%
- Total paid (lifetime, as of 2026-05): $198,879
- Last scope update: 2023-03-22
- Triaged by HackerOne: yes

## Scope quirks

In-scope (per `http.md`):

**Wildcards (max: critical)**

- `*.services.netlify.com`
- `*.services-prod.nsvcs.net`
- `*.infra-prod.nsvcs.net`
- `*.ops.netlify.com`

**Wildcards (max: high)**

- `*.onegraph.com`

**Specific URLs (max: critical)**

- `app.netlify.com`
- `api.netlify.com`
- `internal.netlify.com`
- `netlify-cdp-loader.netlify.app`

**Specific URLs (max: medium)**

- `screenshot-proxy.netlify.app`
- `netlify-rum.netlify.app`
- `list-v2--netlify-plugins.netlify.app`
- `internal-docs.netlify.com`
- `supportal.netlify.app`

**Specific URL (max: low, no bounty)**

- `www.netlifycms.org`

**Explicitly out-of-scope**

- `*.netlify.app` (the entire customer-site wildcard — only the
  enumerated specific subdomains are in-scope)
- `*.netlify.com` (the wildcard — only the enumerated specific
  subdomains are in-scope)
- `*.netlifycms.org`
- `www.netlify.com`
- `webpop.com`, `docs.netlify.com`, `answers.netlify.com`
- `https://github.com/netlify/`
- All Netlify customers' sites

**Scope trap**: the `*.netlify.app` exclusion is wide. Customer sites
hosted on netlify.app are NOT in-scope, even though they share
infrastructure. Always verify the specific subdomain is on the
explicit-include list before sending any probe.

## Auth quirks

- Type: session (web)
- Cred ref: `env:H1_SESSION_TOKEN` (template default — likely needs a
  Netlify-specific cred for live testing, the H1_SESSION_TOKEN is the
  HackerOne platform token, not the Netlify dashboard)
- Dashboard origin: `app.netlify.com`
- SSO: appears to support Google (gsi/client loaded on landing), plus
  email/password and GitHub OAuth (typical for git-platform CI/CD)

## Architecture fingerprints (from 2026-05-18 scout)

- Frontend: React + Relay (`relayRouterRedux.vendor.bundle.js`)
- Bundle hosting: same-origin `app.netlify.com/*.bundle.js`
- Notable runtime bundles loaded on landing:
  `runtime`, `monitoring.vendor`, `containers`, `ui`, `lodash.vendor`,
  `highcharts.vendor`, `helpers`, `buildInfo.vendor`, `lib`,
  `actions`, `markdown.vendor`, `graphiql.vendor` (← GraphiQL is
  shipped), `relayRouterRedux.vendor`, `reactUiUtilities.vendor`
- 3rd-party scripts on landing: Hubspot analytics, Segment, Google
  reCAPTCHA Enterprise, Stripe.js v3, Google GSI client, Amplitude,
  Sift
- 5 postMessage listeners register on Window during landing page
  load (unauthenticated). Sources unreadable via DOMLogger probe (MCP
  sanitizer masked).

## Prior findings

_(none yet)_

## Prior FPs that taught us something

- **auth_dashboard_xss_sweep — stored XSS + URL/hash chains under auth
  (FP batch, high confidence)** (2026-05-18)
  Authenticated as regular user (soural1417@gmail.com). Tested four
  user-controllable text fields with XSS canary payloads:
  - OAuth application name + description + redirect URI
    (via /user/applications/new flow) — observed across list,
    accordion-detail, edit form, AND OAuth consent screen rendering.
  - Personal Access Token description (via
    /user/applications/personal flow) — observed in list view.
  Additionally probed authenticated URL params on `/login` and
  location.hash on `/teams/<x>/projects`. All canaries land in text
  nodes (React JSX createTextNode); zero payload executions across
  three onload/onerror trip-wires. Consent screen — the highest-impact
  surface (would XSS any user authorizing a malicious app) — also
  clean.
  GraphiQL surface: `graphiql.vendor.bundle.js` (1882 lines, webpack
  module 6187) ships in the regular-user bundle but no accessible
  mount route as regular user. /apps/api, /graphiql, /admin/graphql all
  404. Lazy-import callsite worth tracing to find the actual route
  (likely admin/enterprise-only feature flag).
  Mutating actions: created and deleted 1 OAuth app + 1 personal
  access token; visited consent screen without authorizing.
  Details:
  [`findings/auth_dashboard_xss_sweep/confirmed.json`](../../targets/netlify-h1/findings/auth_dashboard_xss_sweep/confirmed.json).
  **Caveats**: regular-user role only; integrations / audit log /
  deploy-detail render paths untested; claude-in-chrome MCP can't
  initScript-inject so page-load-time sinks missed on every auth
  route.

- **chain 188 — URLSearchParams → innerHTML (post-beautify FP on unauth
  routes, medium confidence)** (2026-05-18)
  After beautify+reindex (see [[../techniques/recon/beautify-before-index]]),
  the 20-chain hot.jsonl rebuilt from real DOM-XSS shapes: URLSearchParams
  / location.* sources flowing into innerHTML / setTimeout-string /
  event-handler-attr / etc. Chain 188 was the first audited:
  `app.bundle.js::t_ → 6932.bundle.js::stringify` (URLSearchParams_ctor →
  innerHTML_assign, depth=1 cross-file).
  Live probe via chrome-devtools MCP `initScript` pre-load DOMLogger
  injection on `/` and `/login` with canary URL params + hash. 73 sink
  invocations captured, ZERO canary fires. URL params land in safe
  contexts only: URL-encoded inside `<a href="/sso?redirect=...">` (SSO
  redirect) and inside sandboxed `js.stripe.com/v3/m-outer-*.html#url=`
  iframe. innerHTML sinks all carry static templates (grecaptcha widget,
  jQuery feature-detect, gtm.js mustache placeholders).
  Details: [`findings/188/confirmed.json`](../../targets/netlify-h1/findings/188/confirmed.json).
  **Caveats**: unauth only; authenticated routes
  (/sites/<id>, /teams, /admin, GraphiQL) likely activate different
  innerHTML paths.
  Seeded [[../techniques/recon/initscript-pre-load-injection]] —
  chrome-devtools `initScript` for page-load-time sink capture
  (claude-in-chrome can't do this).

- **20-chain hot.jsonl batch — postMessage / proto-merge self-flows on
  6932.bundle.js (FP, pipeline noise)** (2026-05-18)
  Hot chains 25574–25581 (proto_assign_merge → various PP sinks) and
  35589–35600 (onmessage_handler / proto_assign_merge → various sinks)
  all flagged minified functions `$.set`, `$.validate`, `$1`, `$V` in
  `app.netlify.com/6932.bundle.js` at line=1. Bundle was indexed
  without beautification, function-boundary detection collapsed.
  Live probe against app.netlify.com unauthenticated: 5 postMessage
  listeners on Window, 11 attacker-shape payloads sent (string,
  object, `__proto__`, redux-action, react-devtools, graphiql,
  webpack-message), ZERO sinks fired from listener paths, ZERO
  prototype pollution. Diagnosed as static-analyzer artifact from
  missing beautify phase.
  Details:
  [`findings/35589/confirmed.json`](../../targets/netlify-h1/findings/35589/confirmed.json).
  Seeded [[../techniques/recon/beautify-before-index]] — pipeline
  fix to add beautify between js-harvest and js-index.
  **Caveat**: tested unauthenticated only. Authenticated re-test
  recommended before fully closing.

## Sub-targets / surfaces worth poking later

- `app.netlify.com` authenticated — deploy UI, team settings,
  GraphiQL explorer (graphiql.vendor.bundle.js is loaded), Relay
  subscriptions
- `api.netlify.com` — REST API surface, IDOR candidates
- `internal.netlify.com` — internal tooling, smaller attack surface
  but higher payout potential
- `netlify-cdp-loader.netlify.app` — CDP loader, max critical
- `*.onegraph.com` — GraphQL aggregator, max high
- `*.services.netlify.com` / `*.services-prod.nsvcs.net` /
  `*.infra-prod.nsvcs.net` / `*.ops.netlify.com` — service mesh
  wildcards, recon-target territory
- `netlify-rum.netlify.app` — real-user monitoring endpoint, max
  medium but interesting for log/event injection

## Pipeline status (2026-05-18)

- `init` done 2026-05-12
- `js-harvest` / `js-index` / `db-isolate` / `chains` — populated
  (`chains/hot.jsonl` has 20 entries) but status.json doesn't track
  these phases explicitly. Run pre-2026-05-17.
- **`beautify` phase MISSING** — root cause of the 20-chain FP batch
- `cc_taint_bucket_prep` done 2026-05-17
- `cc_taint_bucket_anomalies` status=appending (incomplete)
- `cc_taint_adversarial` status=prepared (prompts ready, never
  executed — Opus/Sonnet audit pass never ran)
- `cc_taint_expand` done 2026-05-17
- `hot_chain_live_confirm_batch` done 2026-05-18 — this finding

## Next-best actions

1. **Beautify and re-index** before any more chain work. See
   [[../techniques/recon/beautify-before-index]] for recipe.
   Expected outcome: 20-chain hot.jsonl drops to ~0–5 self-flows,
   real cross-function chains appear in their place.
2. After re-index, run `cc-taint-adversarial` on the new hot chains.
3. Authenticated re-test of `app.netlify.com` to enumerate handlers
   in deploy/settings/GraphiQL routes.
4. Recon sweep on the four service wildcards
   (`*.services.netlify.com` etc.) — these have wide attack surface
   and max-critical payout.

## Notes / hunting strategy

- High-payout focus: `app.netlify.com` (dashboard auth bypass / IDOR
  / RCE in build pipelines) and `api.netlify.com` (org-level IDOR).
- GraphiQL is shipped in production bundle — verify whether it's
  gated behind auth/admin role or accessible in some state. If
  reachable unauthenticated or with low-priv account, that's a
  finding.
- Build pipelines: Netlify's USP is git-driven static deploys.
  Build-config injection or build-script-execution via PR-from-fork
  scenarios is the classic high-impact bug class here.
- The `Last scope update: 2023-03-22` is old — recon may surface
  newer subdomains the program hasn't formally added. Worth a sweep
  before relying on the published list.
