---
title: Server-side cookie-clear path confusion via malformed request URI
slug: cookie-clear-path-confusion
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/cookie, technique/session-fixation]
inbound: []
---

# Server-side cookie-clear path confusion via malformed request URI

## Pattern

When a server detects "you have two cookies with the same name and they
disagree" (a classic sign of in-progress attack or stale tab), some
applications respond by issuing a `Set-Cookie` with empty value + a
matching `Path` and `Domain` to *clear* the offending cookie. To pick
the right `Path` for the clear, the server reads the *request URI* —
the path of the current request — and reflects it into the
`Set-Cookie` header.

If the server doesn't sanitize the request URI before reflection,
attacker can supply a request to:
```
GET /a;domain=;
```
The server's clear-cookie logic builds:
```
Set-Cookie: session=; Path=/a;domain=; ; Domain=target.com
```
The browser parses this loosely; the result is that **neither** cookie
gets cleared — instead the attacker's session-fixation cookie survives
where the victim's was supposed to be removed.

This unlocks classic session fixation against apps that issue
`__Host-` prefixed cookies (which JS can't set, but server can be
tricked into preserving the attacker's value).

## Preconditions

- Server has cookie-conflict detection logic that issues a
  `Set-Cookie` clear with `Path` derived from the request URI.
- The reflection of the URI into `Set-Cookie` is not sanitized
  for `;` / `=` / whitespace.
- A separate session-fixation primitive exists (control over at
  least one of the conflicting cookies, typically via subdomain XSS or
  cross-origin POST with `SameSite=None`).

## Detection

- Send two cookies with different values for the same name from a
  subdomain XSS gadget.
- Observe the server's response: a `Set-Cookie: name=; Path=...` line.
- If the `Path` value mirrors the request URI verbatim, the
  reflection vulnerability is present.

## Triggering

Force a request to a malformed URI from the XSS gadget or a CSRF form:
```
GET /a;domain=; HTTP/1.1
Host: target.com
Cookie: session=attacker_value; session=victim_value
```
Server response (broken clear):
```
Set-Cookie: session=; Path=/a;domain=; ; Domain=target.com
```
Browser fails to apply the clear; attacker's `session` survives.

For `__Host-` prefixed counterpart: trigger the login flow without
sending the cookie; many apps respond with `Set-Cookie:
__Host-session=<value>` because they assume "first-time login, set
this cookie" — combine with the attacker's chosen session value.

## Bypasses

- Server may normalize `;` in request URI on some routes — find a
  route where it doesn't.
- Some applications check the cookie path is "under" the request
  path; chain with [[path-scoped-cookie-bypass]] for further leverage.

## Seen in the wild

- {date: 2025-02-20, source: CT Ep 111} — Kevin Mizu's chained ATO: the
  server tried to clear conflicting cookies by reading the request URI;
  Mizu supplied `/a;domain=;` to break the clear logic and survive
  fixation despite a one-year-expiry priority on the victim's existing
  cookie.

## References

- mizu.re — chained ATO writeup
- Critical Thinking Podcast Ep 111
- Related: [[path-scoped-cookie-bypass]]
