---
title: Vertical privilege escalation via access control bypass
slug: vertical-idor
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/idor, technique/access-control, sink/admin-function]
inbound: []
---

# Vertical privilege escalation via access control bypass

## Pattern

A lower-privileged user accesses a higher-privileged function or resource by directly requesting an unprotected URL, manipulating a user-controllable parameter (`?admin=true`, `?role=1`), using a header override (`X-Original-URL`), changing the HTTP method, or exploiting path normalization. The access control enforcement is either missing, client-side only, or bypassable at the platform/framework layer.

## Preconditions

- Administrative or elevated-privilege endpoints exist at predictable or discoverable URLs.
- The server enforces access control at the application layer but not at the platform layer, OR enforcement is entirely absent on some endpoints.
- The attacker can issue arbitrary HTTP requests (authenticated as a normal user or unauthenticated).

## Detection

- Discover admin paths: `robots.txt`, JS bundles, error messages, forced browsing (`/admin`, `/administrator`, `/management`, `/internal`).
- Parameter tampering: intercept login response or page-load request — look for `admin`, `role`, `isAdmin`, `privilege` in cookies, hidden fields, or query params.
- Header override: add `X-Original-URL: /admin/deleteUser` to a normal request to `/` — if the server honors it, platform-level bypass is present.
- HTTP method variation: send `GET` to a `POST`-only restricted endpoint; try `POSTX` if the framework normalizes unknown methods to `GET`.
- Path normalization: try `/admin/deleteUser.anything`, `/ADMIN/deleteUser`, `/admin/deleteUser/` — case-insensitive or extension-ignoring routers may bypass ACL patterns.
- Multi-step process: identify multi-stage flows (step 1 checks role, step 2 does not) — jump directly to step 2.

## Triggering

Unprotected admin URL:
```
https://insecure-website.com/admin
https://insecure-website.com/administrator-panel-yb556
```

Parameter-based role escalation:
```
https://insecure-website.com/login/home.jsp?admin=true
https://insecure-website.com/login/home.jsp?role=1
```

Header override (platform-level bypass):
```
POST / HTTP/1.1
Host: insecure-website.com
X-Original-URL: /admin/deleteUser
```

Path normalization bypass:
```
/admin/deleteUser.anything
/admin/deleteUser/
/ADMIN/DELETEUSER
```

Referer spoofing (Referer-based access control):
```
GET /admin/deleteUser?username=victim HTTP/1.1
Referer: https://insecure-website.com/admin
```

## Bypasses

- WAF/platform enforces on `/admin` but not `/Admin` (case) or `/admin/` (trailing slash).
- `X-Rewrite-URL` header on some Apache/IIS setups has the same effect as `X-Original-URL`.
- Role stored in JWT without signature verification — modify `role` claim without updating signature if `alg: none` accepted.
- Horizontal-to-vertical escalation: gain access to another user's account (horizontal IDOR) who happens to be an admin → vertical privilege via their session.

## Seen-in-the-wild

(none yet)

## References

- [PortSwigger Access control vulnerabilities](../../sources/portswigger-access-control.md) — vertical privilege escalation, parameter tampering, header override sections
- [IDOR SUMMARY](SUMMARY.md)
- [Horizontal BOLA](horizontal-bola.md)
