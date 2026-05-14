---
title: Service-Worker-Allowed root-scope hijack
slug: service-worker-allowed-scope-hijack
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/service-worker, technique/persistence]
inbound: []
---

# `Service-Worker-Allowed` root-scope hijack

## Pattern
By default a Service Worker is scoped to the directory containing its
JS file: `/uploads/user-123/sw.js` can only intercept fetches under
`/uploads/user-123/`. Attackers with file upload but no root-level JS
control are sandboxed.

The `Service-Worker-Allowed` HTTP **response header** on the JS file
overrides this. `Service-Worker-Allowed: /` registers a SW with site-wide
scope — full origin-wide network interception, persistent across reloads,
i.e. permanent in-browser XSS.

Vectors to inject the header:

1. **CRLF injection** in any endpoint that reflects user input into the
   response status line / headers. JS file upload + CRLF = root SW.
2. **Reverse-proxy / app-proxy features** that forward attacker-controlled
   headers from a third-party origin into the trusted origin's response.
   Example: **Shopify app proxies** forward responses from an attacker's
   server back into the merchant origin — and `Service-Worker-Allowed`
   is on Shopify's *disallow list*, which makes it a beautiful tickle to
   smuggle around (CT bounty hint).

## Preconditions
- File upload (JS + HTML, or just JS + an existing XSS to register it).
- A way to control the *response header* of the JS file, not just its
  body. CRLF, response-splitting, app-proxy/reverse-proxy abuse, edge
  worker misconfiguration.

## Detection
- Confirm uploaded file MIME is `application/javascript` (browsers only
  accept SW registration on JS).
- Probe each upload pipeline for response-header injection.
- Inventory any feature labeled "app proxy", "function URL", "reverse
  proxy back to merchant domain" — that's the architecture pattern.

## Triggering
JS file at `/uploads/me/sw.js` with response:
```
Content-Type: application/javascript
Service-Worker-Allowed: /
```
Then:
```js
// In any XSS or HTML upload at the same origin:
navigator.serviceWorker.register('/uploads/me/sw.js', {scope: '/'});
```
The browser checks `Service-Worker-Allowed: /` and grants root scope.

SW body intercepts every fetch in the origin:
```js
self.addEventListener('fetch', (e) => {
  // exfil cookies-in-flight, inject XSS payload into HTML responses,
  // proxy to attacker, etc.
});
```

## Bypasses / hardening
- Strip `Service-Worker-Allowed` (and `Service-Worker` request header)
  at the edge for any user-uploaded asset path.
- Frans Rosén and Matan Berkovich have shown SW abuse for signed-URL leak
  and PII exfil — both worth reading.

## Seen in the wild
- {date: 2025-01-23, source: CT Ep 107} — JG flags Shopify app proxies
  as a high-value target if the disallow-list can be smuggled past.

## References
- Critical Thinking Podcast Ep 107
- Frans Rosén — Service Worker abuse research
- MDN — `Service-Worker-Allowed` header
- Related: [[iframe-without-csp-proxy]]
