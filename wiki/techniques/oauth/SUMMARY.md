---
title: OAuth — summary
slug: oauth-summary
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/oauth, summary, index]
inbound: []
---

# OAuth — summary

## What this class is

OAuth 2.0 misconfiguration vulnerabilities arise from flaws in the authorization flow between a client app, authorization server, and resource server. Common failure modes include: unconstrained `redirect_uri` allowing token theft, missing or predictable `state` parameter enabling CSRF on the authorization endpoint, PKCE downgrade attacks, open redirect chaining to exfiltrate codes, and account-linking confusion across providers. When exploited, these typically yield account takeover or privilege escalation.

## When to suspect

- Login or "Connect account" flows using `/oauth/authorize`, `/auth/callback`, `code=` in query params
- `redirect_uri` parameter present — test for prefix/suffix bypass, open redirect chains
- Absent or static `state` parameter — CSRF on authorization endpoint
- PKCE (`code_challenge`, `code_verifier`) — check for downgrade to implicit or none
- Multiple identity providers (Google, GitHub, Facebook) with account-linking flows — test cross-provider confusion
- JWT access/ID tokens with `alg: none` or weak signing keys
- Token leakage in `Referer` header when `redirect_uri` lands on a page with third-party resources
- `js_analyzer`: `location.search` parsed for `code=` or `token=` in SPA OAuth callback handlers
- Endpoints accepting `access_token` in GET params (logged by proxies/servers)

## External references

| Topic | PayloadsAllTheThings path | HackTricks path | PortSwigger |
|---|---|---|---|
| OAuth misconfiguration | `../../_external/payloads-all-the-things/OAuth Misconfiguration/` | `../../_external/hacktricks/src/pentesting-web/oauth-to-account-takeover.md` | [portswigger-oauth](../../sources/portswigger-oauth.md) |
| JWT attacks | `../../_external/payloads-all-the-things/JSON Web Token/` | `../../_external/hacktricks/src/pentesting-web/hacking-jwt-json-web-tokens.md` | — |
| Account takeover chains | `../../_external/payloads-all-the-things/Account Takeover/` | `../../_external/hacktricks/src/pentesting-web/account-takeover.md` | — |
| Open redirect (redirect_uri chain) | `../../_external/payloads-all-the-things/Open Redirect/` | — | [portswigger-oauth](../../sources/portswigger-oauth.md) |
| CSRF bypass (state bypass) | `../../_external/payloads-all-the-things/Cross-Site Request Forgery/` | `../../_external/hacktricks/src/pentesting-web/csrf-cross-site-request-forgery.md` | [portswigger-oauth](../../sources/portswigger-oauth.md) |

## Related local pages

- [IDOR SUMMARY](../idor/SUMMARY.md) — OAuth tokens that grant IDOR access to other users' resources
- [postMessage SUMMARY](../postmessage/SUMMARY.md) — OAuth popups sometimes communicate tokens via postMessage; origin validation matters
- (none yet)

## Sub-patterns to expand

- [x] `redirect-uri-bypass.md` — open redirect / prefix/suffix bypass to steal auth code
- [x] `state-csrf.md` — missing or reused state parameter
- [ ] `pkce-downgrade.md` — forcing flow without code_challenge
- [ ] `implicit-flow-token-leak.md` — token in fragment leaks to Referer/history
- [ ] `account-linking-confusion.md` — cross-provider identity confusion yields ATO
- [ ] `jwt-none-alg.md` — alg:none or weak HMAC key in bearer tokens
- [ ] `token-in-get-param.md` — access_token passed as query parameter, logged
