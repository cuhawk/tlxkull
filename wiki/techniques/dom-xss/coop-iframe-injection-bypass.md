---
title: COOP bypass via same-origin iframe injection
slug: coop-iframe-injection-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/coop-bypass, technique/postmessage]
inbound: []
---

# COOP bypass via same-origin iframe injection

CT Research Lab workaround for `Cross-Origin-Opener-Policy: same-origin`.

## Pattern
COOP severs the `window.opener` relationship when the popup is a different
origin **and the popup is a top-level page**. Crucially, COOP is only
evaluated for top-level browsing contexts. If you can get the
COOP-protected page *iframed* inside another same-origin page that
**doesn't carry the COOP header**, you preserve the postMessage
relationship from attacker → no-COOP same-origin parent → COOP'd
iframe.

Sketched flow:

1. Find a same-origin page on the target (`a.target.com`) that lacks the
   COOP header.
2. Pop XSS on `support.target.com` (or any same-origin page you can
   inject HTML on) — see [[iframe-without-csp-proxy]].
3. From `attacker.com` iframe `support.target.com` and open a top-level
   navigation to `a.target.com` (the no-COOP page) — keep the window
   reference.
4. Use the XSS in `support.target.com` (same-origin with `a.target.com`)
   to redirect the iframe inside the victim tab to the COOP-protected
   `www.target.com`. Because the COOP'd page is now an iframe inside a
   no-COOP parent, its frame reference survives.
5. postMessage between the attacker iframe and the new COOP'd iframe via
   `window.opener`.

JG: "It's a little convoluted, but it really does work and it's the best
way I've found to get around COOP headers."

## Preconditions
- COOP value is `same-origin` (or default `unsafe-none` doesn't apply).
- A same-origin page on the target that **does not** ship the COOP
  header.
- An XSS or HTML-injection primitive on a same-origin page (often
  reachable on subdomain-level scope: `support.target.com`).
- The COOP page is not also protected by `frame-ancestors: 'self'` —
  worth verifying.

## Detection
- Map every endpoint on the target's primary origin; diff
  `Cross-Origin-Opener-Policy` header presence.
- Flag application segments that historically forget the
  COOP/COEP/CSP/XFO middleware (analytics, support iframes, static
  upload paths, error pages).

## Bypasses / hardening
- Ship COOP at the edge for *all* same-origin URLs, including statics and
  uploads.
- Set `Cross-Origin-Embedder-Policy: require-corp` to additionally
  reject mixed-origin embedding.

## Seen in the wild
- {date: 2025-01-23, source: CT Ep 107} — Critical Thinking Research Lab
  workaround.

## References
- Andrew Lock — "Understanding cross-origin security headers" (3-part).
- Critical Thinking Podcast Ep 107
- Related: [[coop-allow-popups-callback]], [[iframe-without-csp-proxy]]
