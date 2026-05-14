---
title: Ep 169 - OAuth changes, MCP Authorization, PKCE Downgrades
slug: 20260409-oauth-changes-mcp-authorization-pkce-downgrades-ep-169
url: https://www.youtube.com/watch?v=mo9LoNHmDhI
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, oauth, oauth-2-1, pkce, mcp, ssrf, token-exchange, agent-auth]
inbound: []
---

# Ep 169 - OAuth changes, MCP Authorization, PKCE Downgrades

- Date: 2026-04-09
- video_id: mo9LoNHmDhI
- Speakers: Brandon (solo)

## Summary

Brandon walks through three OAuth-shaped attack surfaces showing up in
2026 LHE work. The OAuth 2.1 standard mandates PKCE, removes implicit and
password-credentials flows, requires exact-string redirect-URI matching,
and prohibits bearer tokens in URIs. Frameworks mid-migration (2.0->2.1)
ship compatibility shims that route challenge-less authorize requests to
legacy handlers - **PKCE downgrade** is the resulting attack class. The
MCP Authorization spec layers on top of OAuth 2.1 + RFC 8414 + RFC 7591
and introduces the Client Identity Metadata Document (CIMD) - the
authorization server fetches a client-supplied `client.json` URI for
validation. Top-level + nested `logo_uri` and `jwks_uri` fetches each
form an SSRF primitive. Brandon also covers RFC 8693 token exchange and
its role in reducing agent-to-agent scope creep. Three CVE shoutouts:
ZeroPath's Django OAuth Toolkit findings (mutable `preferred_username` ->
ATO), Cloudflare Workers OAuth accepting a `code_verifier` against a
challenge-less code, and Harbor's "any unknown algorithm = bypass" JWT
flaw (CVE-2026-23993). The latter is the funniest of the bunch - set
algorithm to `banana` and it fails open.

## Techniques extracted

- [[../../techniques/oauth/pkce-downgrade]] - strip `code_challenge` from `/authorize`; legacy 2.0 handler accepts; arbitrary verifier on `/token`.
- [[../../techniques/oauth/mcp-cimd-ssrf]] - MCP CIMD fetch creates SSRF at the manifest URI and nested `logo_uri`/`jwks_uri`.
- [[../../techniques/oauth/mutable-claim-ato]] - Django OAuth Toolkit used `preferred_username` (mutable) as account UID - ATO via IdP self-service username change.
- [[../../techniques/oauth/oauth2-proxy-regex-anchor]] - OAuth2 Proxy regex skip-auth list matched against full request URI including query string; auth bypass by adding the regex as a query parameter.
- [[../../techniques/jwt/none-algorithm-bypass]] - Harbor: any unknown algorithm (literally `banana`) or `none` bypasses JWT signature check. CVE-2026-23993.

## Tools mentioned

- (none new in this episode)

## Quotes

> "The MCP authorization spec builds on top of OAuth 2.1 - that uses RFC 8414 and RFC 7591 - server metadata discovery and dynamic client registration."

> "If this becomes a standard, which I think it will be and slowly is, it actually opens up some more attack surface because we have a little bit more to play with."

> "I didn't know that Harbor existed as a language. Set the algorithm to banana - fails open."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
