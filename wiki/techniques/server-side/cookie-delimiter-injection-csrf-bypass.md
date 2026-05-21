---
title: Cookie Delimiter Injection — CSRF Double-Submit Bypass
slug: cookie-delimiter-injection-csrf-bypass
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/csrf, technique/cookie-injection, technique/framework-quirk]
inbound: []
---

# Cookie Delimiter Injection — CSRF Double-Submit Bypass

## Pattern

Some web frameworks (notably older Django + Python) accept characters
such as `[` and `]` as cookie header delimiters in addition to the
standard `;`. Browsers do not encode these characters when sending cookies.
If an attacker can inject a `[` into the value of a Google Analytics cookie
(GA stores the attacker-controlled referrer URL path unencoded), they can
synthesize an arbitrary cookie in the victim's browser from the server's
perspective, bypassing double-submit CSRF protection.

## Preconditions

- Server uses Django (or similar framework) with non-standard cookie parsing.
- Application uses double-submit cookie CSRF protection (CSRF token value
  compared in cookie vs. request body).
- Google Analytics (or similar) is active and stores the referrer path in a
  cookie without filtering `[` / `]`.
- Attacker can trick the victim to visit a URL such as
  `attacker.com/path[;csrftoken=ATTACKER_VALUE;]/`.

## Detection

- Test whether the target server treats `[` or `]` in the Cookie header as
  a separator (send `Cookie: foo[bar=baz` and check if server sees two cookies).
- Check whether GA-style cookies include unfiltered referrer path data.

## Triggering

1. Register a path on attacker's domain that contains `[csrftoken=EVIL;path=/;`.
2. When victim visits this link, GA writes this path into its cookie value.
3. Browser sends the cookie as a single value but server parses it as
   two separate cookies, including the injected CSRF token.
4. Attacker submits a CSRF form with the same token value in the body.
5. Server's double-submit check passes.

## Bypasses

N/A — this is itself a bypass technique.

## Seen in the wild

- 2014 (disclosed 2020) — Django + Google Analytics, $1,000. Reported by
  Sergei Bobrov. Affected any site using Django with GA and double-submit
  CSRF. Google also paid a separate bounty for the GA cookie injection vector.
  [BBRE](https://www.youtube.com/watch?v=4mMPpcpVqgA)

## References

- Django CVE for non-standard cookie delimiter
- Double-submit cookie CSRF pattern (OWASP)
- See also: [../csrf/_index.md](../csrf/_index.md)
