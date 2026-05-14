---
title: COOP same-origin-allow-popups callback re-entrancy
slug: coop-allow-popups-callback
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/coop-bypass, technique/postmessage]
inbound: []
---

# COOP `same-origin-allow-popups` callback re-entrancy

## Pattern
`Cross-Origin-Opener-Policy: same-origin-allow-popups` is a middle ground:
attacker → COOP'd page severs the opener relationship as usual, but the
COOP'd page itself **can open a popup to a cross-origin URL and keep the
back-reference**. From the popup's perspective, `window.opener` points
back at the COOP'd page — same-origin reach restored.

Exploit shape: get the COOP'd page to open a popup pointing at your
attacker domain. Use a stored gadget, an open-redirect endpoint that
opens its result via `window.open`, or any anchor with
`target="_blank"` plus a clickjacking lure.

Rarely available in the wild because the target page must intentionally
issue the popup, but worth checking when COOP is `allow-popups` instead
of pure `same-origin`.

## Preconditions
- Target has `Cross-Origin-Opener-Policy: same-origin-allow-popups`.
- A gadget on the COOP'd page opens a new window/tab to attacker-
  controlled URL (or an open redirect within attacker reach).

## Detection
- Inspect every COOP'd page's outbound `window.open` / `<a target=_blank>` /
  navigation paths.
- Hunt for "share" / "preview" / "export to PDF in new window" flows.

## Triggering
Attacker provides a URL that, when opened by the COOP'd page, lands on
attacker.com. Attacker page reads `window.opener` and posts messages,
triggers `opener.location = ...`, etc.

## Related
- [[coop-iframe-injection-bypass]] — the more common workaround for the
  stricter `same-origin` setting.

## Seen in the wild
- {date: 2025-01-23, source: CT Ep 107} — JG flags it as theoretical /
  rare in practice but worth checking.

## References
- Andrew Lock — "Understanding cross-origin security headers"
- Critical Thinking Podcast Ep 107
