---
title: Cloudflare /cdn-cgi/* attack surface
slug: cloudflare-cdn-cgi
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [tool/cloudflare, technique/recon]
inbound: []
---

# Cloudflare /cdn-cgi/* attack surface

## Endpoints (always present on Cloudflare-fronted hosts)
- `/cdn-cgi/trace` — text/plain request info reflection.
- `/cdn-cgi/image/...` — SVG-in/out → CSP `default-src 'none'` bypass
  vector. `/cdn-cgi/image/onerror=redirect,...` 307 cross-subdomain
  (same apex) preserves method+body — C-Surf hijack vector. Requires
  Cloudflare Image Optimization on target's domain.
- `/cdn-cgi/email-decode` — auto-replaces tags with `data-cfemail="<hex>"`
  via innerHTML on every Cloudflare site → payload-obfuscation /
  smuggling primitive.
- Bot-management JS endpoints.

## Recon
BigQuery `httparchive` for every unique `/cdn-cgi/*` URL across the public
web. **Cost trap:** `SELECT * ON *` billed $14K once. Scope queries.

## Payload smuggling via email-decode
Hex-encode payload as `data-cfemail` attr; Cloudflare decodes server-side;
payload appears post-load. Combine with DOMPurify permissive `data-*`
handling — see [[dompurify-pi-bypass]].

```html
<svg><script><svg data-cfemail="<hex>"></svg></script></svg>
```
(Masato Kinugawa CFE-mail XSS-Auditor bypass tweet — current Cloudflare
deployments still hex-decode attr.)

## Related
- [[oauth-userinfo-question-bypass]]
- [[htmx-csp-bypass]] — `cdn-cgi/image/onerror=redirect` 307 chained with
  HTMX.

## Seen in the wild
- Cross-subdomain CSurf (Mathias/Frans).
- Critical Thinking Podcast Eps 64, 66, 68.

## References
- Critical Thinking Podcast Eps 64, 66, 68
- Masato Kinugawa CFE-mail XSS bypass tweet
- Hans-Machine `onformdata` XSS-cheatsheet entry
