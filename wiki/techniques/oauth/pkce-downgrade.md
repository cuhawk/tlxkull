---
title: PKCE Downgrade Attack
slug: pkce-downgrade
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/oauth, technique/pkce-downgrade]
inbound: []
---

# PKCE Downgrade Attack

## Pattern

PKCE (Proof Key for Code Exchange, RFC 7636) is mandatory under OAuth 2.1. A
downgrade attack strips or nullifies the `code_challenge` parameter from the
initial authorization request. If the server accepts the authorization request
without it, the resulting authorization code can be exchanged for tokens by
any client that possesses the code — without ever supplying a `code_verifier`.
This enables authorization-code interception → account takeover.

Two concrete mechanisms:

1. **Strip `code_challenge`**: Remove `code_challenge` and
   `code_challenge_method` from the `/authorize` request. Server must reject
   per OAuth 2.1 §4.1, but many do not during 2.0→2.1 migration.
2. **Send verifier against a challenge-free code**: Authorization server
   accepted the code, so any arbitrary `code_verifier` value (or none at all)
   will be accepted at the `/token` endpoint — because there is no stored
   challenge to compare against.

## Preconditions

- Target uses OAuth 2.0 or is mid-migration to 2.1 (compatibility shim in
  place).
- The authorization server does not enforce mandatory `code_challenge`
  rejection on the `/authorize` endpoint.
- Attacker can intercept or inject authorization codes (e.g. via open-redirect
  in `redirect_uri`, referrer leak, or malicious app).

## Detection

- `code_challenge` and `code_challenge_method` present in captured
  `/authorize` request → test removal.
- Framework advertising "OAuth 2.1 compliant" in docs or headers — check
  whether the compliance is partial (common during transitions).
- Look for compatibility shims: server processes both `code_challenge` and
  non-`code_challenge` authorize requests.

```
GET /authorize?response_type=code
  &client_id=<id>
  &redirect_uri=<uri>
  &scope=openid
  # NO code_challenge — server should 400; if it 302 redirects, it's vulnerable
```

## Triggering

1. Initiate a normal PKCE flow; capture the `/authorize` request.
2. Replay `/authorize` with `code_challenge` and `code_challenge_method`
   removed.
3. If the server issues an authorization code, exchange it at `/token` —
   either with no `code_verifier`, or an arbitrary string.
4. Successful token response confirms the downgrade.

```http
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=<stolen_code>
&redirect_uri=<registered_uri>
&client_id=<id>
# code_verifier omitted — or set to anything
```

## Bypasses

- **Partial enforcement**: server enforces `code_challenge` presence but not
  method validity — supply `code_challenge_method=plain` with a trivial value.
- **Transition shim**: server routes challenge-less requests to legacy 2.0
  handler that skips PKCE entirely.
- **Framework bug (Cloudflare Workers OAuth, 2025)**: accepted a
  `code_verifier` even when the initial request omitted `code_challenge` —
  no stored challenge, arbitrary verifier accepted. CVE details in References.

## Seen-in-the-wild

| date | target / library | notes |
|---|---|---|
| 2025 | Django OAuth Toolkit | ZeroPath — mutable `preferred_username` claim used as account UID; combined with PKCE issues → ATO. 4 provider integrations affected (Okta, NetIQ). 2M monthly downloads. |
| 2025 | Cloudflare Workers OAuth (community package) | Accepted `code_verifier` even when initial `/authorize` had no `code_challenge`. All CF Worker OAuth implementations affected. |
| 2025 | Harbor (JWT `alg:none` variant) | Any unknown algorithm or `none` bypassed signature check — `algorithm=banana` worked. CVE-2026-23993 by PentesterLab. |

## References

- Episode source: `../../sources/podcasts/ct/20260409_mo9LoNHmDhI_OAuth_changes_MCP_Authorization_PKCE_Downgrades_Ep._169.en.vtt`
- Podcast: "OAuth changes, MCP Authorization, & PKCE Downgrades (Ep. 169)" — <https://www.youtube.com/watch?v=mo9LoNHmDhI>
- RFC 7636 — PKCE: <https://datatracker.ietf.org/doc/html/rfc7636>
- OAuth 2.1 draft: <https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1>
- ZeroPath Django OAuth write-up: referenced in episode (7 vulns, account impersonation)
- [OAuth SUMMARY](SUMMARY.md)
