---
title: HEAD Method CSRF Bypass — State Change via Safe-Method Endpoint
slug: head-method-csrf-bypass
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/csrf, technique/server-side, technique/method-confusion]
inbound: []
---

# HEAD Method CSRF Bypass — State Change via Safe-Method Endpoint

## Pattern

HTTP HEAD is semantically a "safe" (read-only) method. CSRF protections
and SameSite cookie policies often exempt HEAD requests from token checks
because the assumption is they cannot cause state changes. When a server
framework routes HEAD requests to the same handler as GET (which may itself
trigger side effects, or when the handler serves state-changing functionality
accessible via GET/HEAD), CSRF protection is absent or bypassable.

In the GitHub ATO case: an endpoint that accepted GET/HEAD to register/link
accounts did not require a CSRF token for HEAD requests. A cross-site form
submission using `method="HEAD"` caused the victim's browser to send a HEAD
request (with cookies, because the SameSite constraint was either `None` or
the endpoint was same-site adjacent), triggering account linkage.

## Preconditions

- Framework maps HEAD to GET handler (default in many MVC frameworks).
- The GET handler performs or enables a state-mutating action (account link,
  OAuth grant, subscription, etc.).
- CSRF token check only covers POST/PUT/DELETE, not HEAD/GET.
- Session cookies are sent cross-site (no SameSite=Strict).

## Detection

- Identify state-changing GET endpoints (account link, email change initiation,
  logout, subscription toggle).
- Try issuing the same request as HEAD; check whether the state change occurs.
- Inspect CSRF middleware configuration for method exemptions.

## Triggering

```html
<form action="https://target.example/account/link?provider=attacker" method="HEAD">
  <input type="submit" value="Click me">
</form>
```

Submit cross-origin. Browser sends HEAD with victim's cookies. Server routes
HEAD to GET handler, executes account linkage.

## Bypasses

- If SameSite=Lax is set, HEAD requests are only sent on top-level navigations
  (link clicks, form submits that navigate). Forms with `method="HEAD"` may
  still be treated as top-level navigations in some browsers.
- Combine with `fetch(..., {method: 'HEAD', credentials: 'include'})` when
  SameSite is absent.

## Seen in the wild

- 2022 — GitHub, $25,000. HEAD-method CSRF on an account linking or OAuth flow
  endpoint. Attacker could link a victim's GitHub account to an attacker-controlled
  OAuth application, enabling ATO. Reported in BBRE.
  [BBRE](https://www.youtube.com/watch?v=GLXMGinQyFk)

## References

- RFC 9110 §9.3.2 — HEAD method semantics
- OWASP CSRF prevention cheat sheet — method exemptions
- See also: [../csrf/_index.md](../csrf/_index.md)
