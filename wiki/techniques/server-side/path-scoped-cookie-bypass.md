---
title: Path-Scoped Cookie Bypass via Uppercase Path Variant
slug: path-scoped-cookie-bypass
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/cookie, technique/bypass]
inbound: []
---

# Path-Scoped Cookie Bypass via Uppercase Path Variant

## Pattern

Browsers send cookies whose `Path` attribute matches the request path using a
**case-sensitive** comparison. Many HTTP back-ends route paths
**case-insensitively** (IIS by default; many Node/Go/Java frameworks
optionally). This mismatch means:

- Cookie `Path=/abc` → browser sends cookie on `GET /abc` but NOT on
  `GET /ABC` or `GET /Abc`.
- Back-end processes `GET /ABC` identically to `GET /abc`.

An attacker can therefore send a request to the uppercase variant of a
path to make the browser withhold specific path-scoped cookies while keeping
session cookies scoped to `/` — selectively dropping one cookie from the
request without needing to intercept or modify it client-side.

**Concrete exploit pattern (from CT Ep. 171):**  
A vulnerability on endpoint `/abc` only fires when a specific path-scoped
protection cookie is absent. CSRF/clickjacking to `/ABC` delivers the request
without that cookie, triggering the vulnerability, while session cookies (scoped
to `/`) are still sent normally.

## Preconditions

- A sensitive endpoint at a path like `/foo/bar`.
- A protection mechanism (CSRF token, feature flag, anti-replay cookie)
  delivered as a cookie with `Path=/foo/bar` (or any sub-path).
- Back-end treats `/FOO/BAR` as equivalent to `/foo/bar`.
- No equivalent uppercase enforcement at the reverse proxy layer.

## Detection

- Identify path-scoped cookies in captured responses: `Set-Cookie: _prot=...; Path=/foo/bar`.
- Test: send the same request with one character uppercased.
- Confirm: the protection cookie is absent from the upstream request log while
  session cookies are still present.
- Also useful for: bypassing SameSite protections on path-scoped cookies,
  skipping per-path rate-limit tokens.

## Triggering

1. Identify the protected endpoint and the specific cookie whose absence
   enables the vulnerability.
2. URL-encode or capitalize one or more characters in the path (start with
   last segment, then try each character).
3. Send request to the uppercase variant. Verify protection cookie is absent
   in Caido capture.
4. If the vulnerability requires a user gesture (e.g. CSRF), construct a form
   that POSTs to the uppercase path:

```html
<form method="POST" action="https://target.com/Abc/sensitive">
  <input type="hidden" name="action" value="delete_account">
  <input type="submit" value="Click here">
</form>
```

5. Combine with clickjacking if direct navigation is needed:
   - Use `Ctrl+click` inside an iframe to open a new tab (top-level
     navigation) while the iframe is constrained to that path variant.

## Bypasses

- **Reverse proxy normalization**: Nginx/HAProxy may normalize paths to
  lowercase before forwarding — test the production environment, not just
  a local copy.
- **Cookie path prefix matching quirks**: some browsers match prefixes only, so
  `Path=/foo` would still match `/FOO` — test per browser.
- **Encoding tricks**: `%61bc` (URL-encoded `abc`) is a further variant if
  the back-end decodes before routing but the browser doesn't decode the
  `Path` attribute for comparison.

## Seen-in-the-wild

| date | target | notes |
|---|---|---|
| 2026 | (undisclosed program) | Justin Gardner (CT Ep. 171): found multiple bypasses using uppercase letters in paths over two months; uppercase path variant suppressed a path-scoped protection cookie, enabling vulnerability that required the cookie's absence. |

- {date: 2026-04-23, source: CT Ep 171} — Justin Gardner: "capital letters are really overpowered" — at least three vulns found via uppercase path variants in the past two months; primary case used to suppress a path-scoped protection cookie and trigger a vuln that required its absence.

## References

- Episode source: `../../sources/podcasts/ct/20260423_l5fs7Okdj3o_Path-Scoped_Cookie_Hacks_with_Uppercase_Post-based_Raw_Protobuf_XSS_Ep_171.en.vtt`
- Podcast: "Path-Scoped Cookie Hacks with Uppercase & Post-based Raw Protobuf XSS (Ep. 171)" — <https://www.youtube.com/watch?v=l5fs7Okdj3o>
- [Server-side SUMMARY](SUMMARY.md)
