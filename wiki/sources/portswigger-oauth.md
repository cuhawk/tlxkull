---
title: PortSwigger — OAuth authentication
slug: portswigger-oauth
url: https://portswigger.net/web-security/oauth
fetched_utc: 2026-05-12T00:00:00Z
kind: article
extracted: true
extract_model: sonnet
tags: [source, technique/oauth, ref/portswigger]
inbound: []
---

# PortSwigger — OAuth authentication

## TL;DR

- OAuth 2.0 is inherently prone to implementation mistakes due to its loose specification; vulnerabilities most commonly arise in how client apps implement the flows.
- Missing or predictable `state` parameter enables CSRF on the authorization endpoint, allowing account hijacking or forced login.
- `redirect_uri` validation flaws (prefix/suffix bypass, parameter pollution, path traversal) allow stealing auth codes and access tokens.
- Scope upgrade attacks let attackers request higher privileges than the user originally authorized.
- Unverified user registration with an OAuth provider allows ATO if email ownership is not confirmed.

## Sub-sections

- What is OAuth?
- How does OAuth 2.0 work?
- OAuth authentication
- How do OAuth authentication vulnerabilities arise?
- Identifying OAuth authentication
- Recon
  - `/.well-known/oauth-authorization-server`
  - `/.well-known/openid-configuration`
- Exploiting OAuth authentication vulnerabilities
  - Vulnerabilities in the client application
  - Improper implementation of the implicit grant type
  - Flawed CSRF protection
  - Leaking authorization codes and access tokens
  - Flawed redirect_uri validation
  - Stealing codes and access tokens via a proxy page
  - Flawed scope validation
  - Scope upgrade: authorization code flow
  - Scope upgrade: implicit flow
  - Unverified user registration
- Extending OAuth with OpenID Connect
- Preventing OAuth authentication vulnerabilities
