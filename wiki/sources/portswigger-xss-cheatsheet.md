---
title: PortSwigger XSS Cheat Sheet (2026 ed.)
slug: portswigger-xss-cheatsheet
url: https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
fetched_utc: 2026-05-12T00:00:00Z
kind: article
extracted: true
extract_model: sonnet
tags: [source, technique/xss, ref/portswigger]
inbound: []
---

# PortSwigger XSS Cheat Sheet (2026 ed.)

## What it is

PortSwigger's continuously updated XSS reference. Per-tag/per-event-handler
payload matrix with browser compatibility notes. Includes recent additions
on framework-specific (Vue, Angular), prototype-pollution vectors,
client-side template injection, scriptless attacks, WAF bypass.

## Stored locally

- HTML: `wiki/sources/portswigger-xss-cheatsheet.html` (~1.3MB)
- PDF: `wiki/sources/portswigger-xss-cheatsheet.pdf` (~27MB, official)

## Why it matters

When chain triage hits a DOM-XSS sink, this is the first stop for
candidate payloads that fit the exact tag/event-handler the sink renders.
Pair with `wiki/_external/payloads-all-the-things/XSS Injection/`.

## Extraction TODO

Run `wiki-ingest` (with Sonnet, per memory) to distill into
`wiki/techniques/dom-xss/` sub-pages:
- `event-handler-matrix.md` — table of working event handlers vs browser
  (no body copy — link to PDF page numbers).
- `framework-vectors-vue.md` / `framework-vectors-angular.md`.
- `csp-bypass-via-script-gadgets.md`.
- `client-side-template-injection.md`.
- `mxss-mutation-vectors.md`.
- `waf-bypass.md` — only patterns we've personally verified.

Each new page links back here under "References".
