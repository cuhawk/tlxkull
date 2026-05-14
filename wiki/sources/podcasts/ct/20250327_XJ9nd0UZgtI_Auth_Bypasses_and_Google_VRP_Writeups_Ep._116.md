---
title: Ep 116 — Auth Bypasses and Google VRP Writeups
slug: ct-ep-116-auth-bypasses-google-vrp
url: https://www.youtube.com/watch?v=XJ9nd0UZgtI
fetched_utc: 2026-05-14T00:00:00Z
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, saml, oauth, google-vrp, nextjs]
inbound: []
---

# Ep 116 — Auth Bypasses and Google VRP Writeups

Date: 2025-03-27
video_id: XJ9nd0UZgtI
Speakers: Justin Gardner (JG) — solo episode

## Summary

Solo episode walking four pieces of research: PortSwigger's SAMLuel
round-trip bypass landing unauth ATO on GitLab; three recent Google VRP
disclosures (Apps Script `SpreadsheetApp.openById` privilege confusion,
OAuth localhost-redirect chained with an open-redirect in a Google product,
OAuth localhost callback intercepted by a sibling Android app); and zhero-
web-sec's Next.js middleware bypass via the
`x-middleware-subrequest` header. Each segment surfaces a concrete
detection pattern hunters can lift.

## Techniques extracted

- [[../../techniques/saml/saml-roundtrip-attribute-mutation]] — single-quote → double-quote rewrite across REXML + Nokogiri double-parse smuggles a malicious assertion.
- [[../../techniques/saml/ws-fed-metadata-signature-reuse]] — Entra/AzureAD WS-Federation signed metadata endpoint provides a valid signature payload re-usable in the SAML round-trip exploit.
- [[../../techniques/saml/xml-attlist-attribute-hijack]] — `<!ATTLIST>` declaration in the inline `DOCTYPE` injects attributes on signed elements at parse time.
- [[../../techniques/idor/google-appscript-openbyid-bypass]] — `SpreadsheetApp.openById` exposes form/editor metadata the threat model says you shouldn't have.
- [[../../techniques/oauth/localhost-redirect-open-redirect-chain]] — `redirect_uri=http://localhost:PORT` chained with a localhost-bound Google tool that has an open redirect leaks the auth code.
- [[../../techniques/oauth/localhost-redirect-mobile-sibling-app]] — Any Android app can bind unprivileged ports >1024, racing or fronting the legitimate OAuth-callback listener.
- [[../../techniques/server-side/nextjs-middleware-subrequest-bypass]] — `x-middleware-subrequest: pages/_middleware` (or path variants) header lets clients skip Next.js middleware (CVE-2025-29927).

## Tools mentioned

(no specific tool quirk)

## Quotes

> "Sammuel libraries often parse an XML document, store it as a string, and then later reparse it. Anytime there's sort of this double-parsing environment, then there's a chance there'll be discrepancies."
> — JG, on the SAMLuel pattern.

> "WS-Federation provides signed metadata XML endpoints — so we can hit this metadata endpoint that's signed and reuse that signature."
> — JG, on the IdP-bootstrap signature source.

> "The payload right here, X-middleware-subrequest with the value pages/_middleware, was all you needed to bypass any middleware — which is often where authentication or authorization checks are being done."
> — JG, on the Next.js middleware exploit.

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
