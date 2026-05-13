---
title: Iframe sandwich cross-tab — out-of-scope XSS to in-scope impact
slug: iframe-sandwich-cross-tab
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/iframe-hopping]
inbound: []
---

# Iframe sandwich cross-tab

## Pattern
Two same-tab-group windows: attacker page and victim page. Both iframe the
*same* same-origin URL on `vuln.victim.com`. Attacker iframe gets XSS; via
`window.opener` on the second tab, reach into the iframe in the victim tab
and rewrite its DOM. Same-origin → no SOP barrier. Promotes an out-of-scope
subdomain XSS into in-scope main-domain content tampering / token leak.

## Preconditions
- An XSS sink on `vuln.victim.com` (often an out-of-scope subdomain).
- A same-origin page on `victim.com` (or any in-scope domain) that iframes
  `vuln.victim.com` — common for analytics, support widgets, error pages.
- Attacker controls the initial `window.open`.

## Detection
- Map every page on the main domain that iframes a subdomain. Use
  PostMessage Tracker (Frans Rosén) to surface listeners.
- Check `frame-ancestors` and `X-Frame-Options` on each candidate.

## Triggering
```html
<!-- attacker.com -->
<iframe src="https://vuln.victim.com/xss-sink?p=PAYLOAD"></iframe>
<script>
  // Open victim page in second tab AFTER XSS lands in attacker iframe.
  const victimTab = window.open('https://victim.com/page-with-vuln-iframe');

  // XSS payload (executed in attacker's iframe) reaches across via opener:
  // window.opener (victim tab) → its iframe to vuln.victim.com → rewrite DOM.
</script>
```

Inside payload (attacker's iframe, same-origin with victim tab's iframe):
```js
const victimIframe = opener.window.document.querySelector(
  'iframe[src*="vuln.victim.com"]'
);
victimIframe.contentDocument.body.innerHTML = '<phishing form>';
```

## Bypasses
- Cross-origin between attacker iframe and victim iframe: blocked by SOP.
  Sandwich works precisely because BOTH iframes are same-origin with each
  other (both on `vuln.victim.com`).

## Seen in the wild
- {date: 2023-11-30, target: undisclosed} — Ep 47 CSP research.
- {date: 2024-01-04, target: best of 2023 recap} — Ep 52.

## References
- Critical Thinking Podcast Eps 47, 52
- Yusuf Sammouda — variations across Meta family
