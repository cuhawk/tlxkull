---
title: Ep 47 — CSP Research, Iframe Hopping and Client-side Shenanigans
slug: ct-ep-47-csp-iframe-hopping-clientside
url: https://www.youtube.com/watch?v=1J08mouZIk4
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, csp, iframe, dom-xss, recon]
inbound: []
---

# Ep 47 — CSP Research, Iframe Hopping and Client-side Shenanigans

Date: 2023-11-30
video_id: 1J08mouZIk4
Speakers: Justin Gardner (JG), Joel Margolis (JM)

## Summary

Heavy banter episode that nonetheless surfaces a dense block of
client-side primitives in the "news" segment: Johan's open-redirect
double-slash tip, Google VRP's Protobuf Burp extension release, the
"iframe sandwich" cross-tab pattern, JS hoisting recovery for
undefined-call sinks, octagon.net's SOME-via-JSONP CSP bypass, and
Wallarm's classic CSP-bypass via a same-origin iframe that's missing
the CSP header. Discord segment also covers DNS wildcard profiling for
subdomain enumeration and `Thank-You-Next` build-manifest route
extraction.

## Techniques extracted

- [[../../techniques/dom-xss/iframe-sandwich-cross-tab]] — open both attacker and victim pages that iframe the same vulnerable subdomain; pop XSS on attacker side, reach across via `opener` to mutate victim's iframe DOM.
- [[../../techniques/dom-xss/js-hoisting-xss]] — recover from `x.y(1, INJ)` undefined-call TypeError by injecting `function x(){};` to satisfy hoisting.
- [[../../techniques/dom-xss/iframe-without-csp-proxy]] — iframe a same-origin asset that lacks CSP header; load attacker script inside it; talk back to parent.
- [[../../techniques/dom-xss/no-parens-jsonp-callback]] — octagon.net SOME (Same-Origin Method Execution): JSONP callback restricted to `[a-zA-Z.]` still calls `opener.document.querySelector(...).click` after attacker pivots window to victim origin.
- [[../../techniques/csrf/open-redirect-double-slash]] — `//attacker.com` bypasses naive "starts-with-`/` means relative" redirect filters; affects OAuth, SAML, SSRF chains.
- [[../../techniques/recon/dns-wildcard-profile]] — characterize each wildcard by resolving variants and recording the canonical IP-set; surface diamond-in-the-rough subdomains that don't match the wildcard's response.
- [[../../techniques/recon/spa-build-manifest-route-enum]] — Next.js `_buildManifest.js` and webpack lazy-load chunks reveal client-side routes / pages folder; trigger them client-side for state-without-API-knowledge.

## Tools mentioned

- [[../../tools/caido]] — JG's gripe about scope having to be FQDN-rooted vs Burp's freeform regex; collection-based request organization tip; convert-workflows for HMAC signing.
- [[../../tools/browser]] — frame-busting context, X-Frame-Options interplay with CSP omission.

## Quotes

> "Slash slash attacker.com is not a relative domain, but is actually an absolute URL — a lot of simple filters check if the URL is relative by checking if it starts with a slash."
> — Johan Carlson tip relayed by JG.

> "We can only inject characters and dots — but we can build out window.opener.document.body.firstElementChild.click. Same-origin now, so the click fires."
> — JG describing the octagon.net SOME chain.

> "If it's missing the CSP header, it's probably also missing the X-Frame-Options header — those are normally grouped in the same reverse-proxy header rule."
> — JG, on why same-origin no-CSP iframe proxying still works in practice.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
