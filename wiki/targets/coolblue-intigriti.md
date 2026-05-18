---
title: Coolblue (Intigriti)
slug: target-coolblue-intigriti
created_utc: 2026-05-18T15:00:00Z
updated_utc: 2026-05-18T15:00:00Z
tags: [target/coolblue, target/ecommerce, target/intigriti, platform/intigriti]
inbound: []
---

# Coolblue (Intigriti)

## Snapshot

- Platform: Intigriti — public BBP, open
- Bounty (Tier 1): Low €250 / Medium €750 / High €1,337 / Critical
  €2,500 / Exceptional €2,500
- Bounty (Tier 2): Low €125 / Medium €375 / High €669 / Critical
  €1,250
- Rate limit: 2 req/sec for NL/BE/DE webshops; 0.3 req/sec elsewhere
- Hosted on AWS — respect AWS pentest policy
- Focus areas (program-stated): infrastructure access, order-process
  exploits (free/discounted products), customer password/data exposure

## Scope quirks

In-scope (per `http.md`):

- `www.coolblue.nl` (Tier 1)
- `www.coolblue.be` (Tier 1)
- `www.coolblue.de` (Tier 1)
- `eu.coolblue.shop` Android app (Tier 2)
- iOS app id `1174047097` (Tier 2)
- `mobile-api.coolblue-production.eu` (Tier 2)

**Out-of-scope traps** (frequently harvested by `js-harvest` but NOT
in scope):

- `assets.coolblue.de` — primary CDN for `www.coolblue.*` JS bundles
  (incl. Optimizely STM, microfrontend chunks). 5 of 11 audited
  chains landed sinks here in the 2026-05-18 run. Always verify sink
  host before live-confirm — see
  [[../techniques/recon/scope-aware-chain-triage]].
- `assets.coolblue.nl` — sibling CDN, same caveat.
- `assets.accounts.coolblue.nl` — accounts CDN.
- `accounts.coolblue.de` — auth host (OIDC, client_id=`Webshop`).
  Not in scope unless explicitly added.

NL/BE/DE webshops share a high % of source code. Program policy:
**submit once per vuln** that reproduces across all three.

Explicit out-of-scope (program-stated):

- Appointments / UUID findings
- No-captcha login
- No password length requirement

## Auth quirks

- Type: session
- Cred ref: `env:INTIGRITI_SESSION_TOKEN`
- Self-register at `www.coolblue.nl/registreren` using `@intigriti.me`
  address; always communicate testing IP
- OIDC auth host: `accounts.coolblue.de`, client_id = `Webshop`

## Architecture fingerprints (from 2026-05-15 harvest)

- Frontend: React + Next.js microfrontends
  - `pre-cart-microfrontend` (build hash
    `aa3ce13b731b88582f331a3c13f8f1182378d89c`)
  - `checkout-microfrontend`
  - `accounts` — UNMINIFIED ES modules + Web Components (readable
    source — rare and valuable)
- Telemetry: first-party `mimir` + `stm` bundles
- A/B testing: Optimizely Preview SDK
  (`assets.coolblue.de/js/stm/6689543890403328.js`)
- Sourcemaps: 0 available (all `*.js.map` → 403 from AmazonS3)
- Minification: chunks fully minified, accounts modules readable

## Prior findings

_(none yet — engagement in static-audit phase)_

## Prior FPs that taught us something

- **chain 12 — Optimizely Preview SDK client-side RCE (FP at gate 3,
  endpoint missing)** (2026-05-18)
  Static `cc-taint-adversarial` flagged `new Function(n.responseText)()`
  at line 9297 of `6689543890403328.js`, triggered by
  `/dist/preview_data.js?token=<x>` XHR with attacker-controllable
  token query param. Static verdict: `evidence_gap`, medium
  confidence.
  Earlier session archived as `out_of_scope_sink` based on file-host
  (`assets.coolblue.de` not in `http.md`). Wrong: JS executes in
  `www.coolblue.de` origin via `<script src=>`. Revived per program
  scope guidance ("test is on www.coolblue.*, only the files are on
  cdn").
  Live-confirm verdict: **false_positive (high confidence)**. Gate 3
  fails unconditionally: every path under `assets.coolblue.de/dist/`
  returns 403 application/xml, including `/dist/preview_data.js`.
  Endpoint is not deployed. Token reflection impossible — XHR success
  path never reached. See
  [`findings/12/confirmed.json`](../../targets/coolblue-intigriti/findings/12/confirmed.json)
  and `notes.md`. Seeded
  [[../techniques/recon/scope-aware-chain-triage]] — refined to
  distinguish execution origin from file host.
- **chains 33, 56, 57, 78 — prototype pollution gadget chains in same
  STM bundle** (2026-05-18, status: pending_revisit)
  Cross-file PP chains with sources in pre-cart-microfrontend
  (`assets.coolblue.nl`) and sinks in Optimizely STM bundle
  (`assets.coolblue.de`). Originally archived `drop` by
  `cc-taint-route`. Under refined scope policy these are in-scope by
  execution origin (load into www.coolblue.de). Worth a batch
  re-audit — gate 3 still applies (need to find an in-scope action
  that actually mutates the polluted path reaching the gadget).

## Sub-targets / surfaces worth poking later

- `mobile-api.coolblue-production.eu` — only API host in scope and
  least-touched in current audit. Worth a Caido-replay sweep when
  the mobile-app traffic capture is loaded.
- `www.coolblue.de` German shop — primary focus host per
  `status.json`.

## Notes / hunting strategy

- E-commerce: focus on order-process exploits (cart manipulation,
  price tampering, discount stacking) and IDOR (customer
  password/data exposure). Program text explicitly lists these.
- Wayback param surface: 308 in-scope URLs with params saved at
  `targets/coolblue-intigriti/wayback_param_urls.txt`. Interesting
  classes: open-redirect (`?link=`, `?landing=`, `?ref=`), reflected
  XSS (`?query=`, `?searchPath=`, `?pagina=`), IDOR/SSRF
  (`?imageId=`, `?tid=`, `?specificationid=`), cart manipulation
  (`?add=`, `?items=`, `?locatie=`, `?shopid=`).
- The unminified `accounts` Web Components are the highest-value
  static-review surface. Read line-by-line before chain-triage burns
  budget.
