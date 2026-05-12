---
title: OAuth state parameter CSRF
slug: state-csrf
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/oauth, technique/csrf, sink/account-linking]
inbound: []
---

# OAuth state parameter CSRF

## Pattern

The OAuth `state` parameter binds an authorization request to a user session, preventing CSRF. When `state` is absent, static, or predictable, an attacker can initiate an authorization flow and force the victim's browser to complete it, hijacking account linking or silently logging the victim in under the attacker's identity.

## Preconditions

- The application uses OAuth for login or account linking.
- `state` is missing from the authorization request, or is static/guessable (e.g. always `"csrf"`, a timestamp, or the user's `userId`).
- The attacker can trigger the victim to visit the callback URL with the attacker's `code` parameter.

## Detection

- Proxy the initial `GET /oauth/authorize` request — inspect whether `state` is present, unguessable, and tied to the session.
- Compare `state` across multiple login attempts: if it repeats or is absent, the flow is vulnerable.
- Callback endpoint: does it validate `state` before exchanging the code? Drop `state` from the callback and see if the flow completes.
- Check account-linking flows separately from login — linking is often CSRF-vulnerable even when login is protected.

## Triggering

CSRF attack (force victim to link attacker's OAuth identity):
1. Attacker starts OAuth flow on the client app, obtains a `code` from their own OAuth provider account.
2. Attacker drops their callback before the exchange completes, captures the URL: `https://client-app.com/oauth/callback?code=ATTACKER_CODE&state=...`
3. Attacker tricks victim into visiting that URL (iframe, redirect, email link).
4. If no state validation, client app exchanges ATTACKER_CODE and links attacker's OAuth identity to victim's account → ATO.

Missing state in authorization request:
```
GET /authorization?client_id=12345&redirect_uri=https://client-app.com/callback&response_type=token&scope=openid%20profile HTTP/1.1
Host: oauth-authorization-server.com
```
(No `state=` parameter — immediately suspicious.)

## Bypasses

- Some apps validate `state` only on login flow but not on "Connect social account" flow — test both separately.
- Static state (`state=csrf`) — the server accepts any matching string; supply the static value in the CSRF PoC.
- `state` present but not validated server-side — modify it to anything and confirm the callback still succeeds.

## Seen-in-the-wild

(none yet)

## References

- [PortSwigger OAuth authentication](../../sources/portswigger-oauth.md)
- [OAuth SUMMARY](SUMMARY.md)
