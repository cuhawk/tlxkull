---
title: oauth2-proxy skip-auth regex anchor bypass
slug: oauth2-proxy-regex-anchor
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/oauth, technique/auth-bypass]
inbound: []
---

# oauth2-proxy skip-auth regex anchor bypass (CVE-2025-54576)

## Pattern
`oauth2-proxy`'s skip-auth regex matches against the entire request URI
(path + query), not path-only. Append a query parameter whose value matches
the configured skip-regex → full auth bypass on protected paths.

## Preconditions
- Target uses oauth2-proxy with a `skip_auth_regex` or
  `skip_auth_routes` config that allowlists a public route.
- The regex isn't anchored to start-of-path.

## Detection
- Inspect `oauth2-proxy.cfg` for `skip_auth_regex` / `skip_auth_routes`.
- Test: append `?bypass_pattern=<allowlisted-pattern>` to a protected URL,
  see if auth bypassed.

## Triggering
```
GET /admin/api?bypass_pattern=publicRoute HTTP/1.1
```
where `publicRoute` matches the configured allowlist regex (e.g.
`/healthz`, `/public/.*`).

## Generalisation
Any framework where allowlist regexes match request URI rather than
path-only:
- nginx `if ($request_uri ~ ...)` configs.
- Spring Security path patterns where the matcher reads URI.
- Custom auth middleware in Express that does `req.url.match(regex)`.

## Bypasses
- Properly anchored regex `^/<path>(/|$)` defeats this.

## Seen in the wild
- {date: 2025, CVE: CVE-2025-54576}.
- Discussed Critical Thinking Podcast Ep 169 (OAuth changes / MCP / PKCE).

## References
- CVE-2025-54576
- Critical Thinking Podcast Ep 169
- See also: [[jwt-unknown-alg-fail-open]] for adjacent fail-open class.
