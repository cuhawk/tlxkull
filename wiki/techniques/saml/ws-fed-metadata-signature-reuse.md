---
title: WS-Federation signed-metadata signature reuse
slug: ws-fed-metadata-signature-reuse
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/saml, technique/auth-bypass, technique/idp-bootstrap]
inbound: []
---

# WS-Federation signed-metadata signature reuse

## Pattern
Every Entra ID / AzureAD tenant silently exposes a **WS-Federation signed
metadata endpoint** (`/federationmetadata/2007-06/federationmetadata.xml`)
even when the consumer SAML/SSO is the only one configured. The XML
returned is signed by the tenant's signing cert. For exploits that need a
*"a valid IdP-signed XML payload to use as a starting point"* — e.g.
[[saml-roundtrip-attribute-mutation]] — this metadata file is the
attacker's free oracle.

PortSwigger's SAMLuel chain bootstrapped the round-trip exploit by pulling
the federation metadata XML and reusing its signature wrapper.

## Preconditions
- IdP is Entra/AzureAD (default behaviour).
- The downstream exploit only needs a signed payload, not a specific
  signed claim set.

## Detection / recon
For any Entra tenant `<tenant>.onmicrosoft.com`:
```
https://login.microsoftonline.com/<tenant-id>/federationmetadata/2007-06/federationmetadata.xml?appid=<appid>
```
returns the signed metadata. The same flow ships for *every* AAD-protected
app.

## Mitigation note
Microsoft cannot easily un-ship this — it's part of the WS-Federation /
SAML interoperability contract. Defense is parser-side: don't combine
signed wrappers with two-parser disconnects (kill the
[[saml-roundtrip-attribute-mutation]] gadget).

## Seen in the wild
- {date: 2025, source: CT Ep 116} — PortSwigger SAMLuel.

## References
- PortSwigger SAMLuel writeup
- Critical Thinking Podcast Ep 116
- Related: [[saml-roundtrip-attribute-mutation]], [[xsw]]
