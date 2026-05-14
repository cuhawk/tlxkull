---
title: Ep 107 — Bypassing Cross-Origin Browser Headers
slug: ct-ep-107-bypassing-cross-origin-headers
url: https://www.youtube.com/watch?v=qd08UBNpu7k
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, browser, coop, coep, corp, service-worker, oauth]
inbound: []
---

# Ep 107 — Bypassing Cross-Origin Browser Headers

Date: 2025-01-23
video_id: qd08UBNpu7k
Speakers: Justin Gardner (JG), Joseph Thacker (Joseph, new permanent co-host)

## Summary

JG walks through the cross-origin-isolation header suite (COOP, COEP,
CORP), and the practical attacker workarounds the Critical Thinking
Research Lab developed for COOP — most notably the COOP-iframe-injection
technique that severs/reattaches frame references via a no-COOP
same-origin page. Bonus segment: Service-Worker scope hijacking via
`Service-Worker-Allowed` (CRLF injection or Shopify app-proxy style
reverse-proxies), and `X-Content-Type-Options: nosniff` duplicate-header
bypass. Plus shorter coverage of the Truffle Sec OAuth research on
re-registered defunct-startup domains as an ATO/SSO bypass class.

## Techniques extracted

- [[../../techniques/dom-xss/coop-iframe-injection-bypass]] — COOP severs `window.opener` for top-level navigations; iframe the COOP'd page from a no-COOP same-origin page and the relationship survives.
- [[../../techniques/dom-xss/coop-allow-popups-callback]] — `Cross-Origin-Opener-Policy: same-origin-allow-popups` lets the COOP'd page open a popup that retains the back-reference; if you can trigger that popup you get a `window.opener` to message back.
- [[../../techniques/dom-xss/service-worker-allowed-scope-hijack]] — `Service-Worker-Allowed: /` response header overrides the JS-file path scope, granting root-scope persistence in the victim's browser.
- [[../../techniques/dom-xss/x-content-type-options-double-header]] — duplicate `X-Content-Type-Options` headers cause browsers to discard both and resume MIME-sniffing (CRLF chain).
- [[../../techniques/oauth/defunct-domain-sso-takeover]] — buy a defunct startup's expired domain, claim its Google-SSO'd accounts at downstream SaaS tools (Truffle Sec research).

## Tools mentioned

- [[../../tools/browser]] — `crossOriginIsolated` Boolean, COOP/COEP/CORP triad reference.
- [[../../tools/caido]] — Bevix's `SSRF-CVS-Advisor` collaborator-replacement is mentioned earlier; here just the Kaido `auth-swap` plugin context.

## Quotes

> "COOP is the freaking bane of my existence — it's like one of the worst things for an attacker that's ever happened to browser security."
> — JG.

> "Coop only affects top-level pages. If you can get www.site.com iframed into a same-origin page that does not have a COOP header, the COOP is ignored for that frame — and you can still post-message it from your attacker page."
> — JG explaining the Research-Lab workaround.

> "I just want to remind you that if you have a tab open and you opened up a new website, you can always redirect that tab unless COOP has severed the connection."
> — JG, on the still-useful top-level-redirect primitive.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
