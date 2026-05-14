---
title: Path-Based CSP Whitelist Bypass via Redirect
slug: path-csp-redirect-bypass
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/csp, technique/csp-bypass, technique/redirect]
inbound: []
---

# Path-Based CSP Whitelist Bypass via Redirect

## Pattern

Content-Security-Policy `script-src` values support a path component:

```
Content-Security-Policy: script-src https://example.com/safe/
```

The browser's CSP enforcer evaluates the **initial** request against the
policy. If the script URL matches, the request proceeds. Any **redirect**
that follows is NOT re-checked against the path component - only the
host. So `https://example.com/safe/foo.js -> 302 ->
https://example.com/user-upload/evil.js` executes `evil.js` despite
`user-upload/` not being in the policy.

The classic exploit pattern:

1. Find an open redirect or controllable redirect within the
   `script-src`-allowed origin's allowed path.
2. Target the redirect to a path on the same host that the attacker can
   write JavaScript to (often a user-uploaded-asset path).
3. The browser executes the redirected script, satisfying CSP because the
   *initial* fetch was inside the allowed path.

Johan Carlsson surfaced this as part of his XSS challenge.

## Preconditions

- Target CSP `script-src` has a path component (not just host).
- The same host has either an open redirect or controllable-content path
  that returns JavaScript.
- The allowed path serves at least one resource that 3xx-redirects.

## Detection

- Read the deployed CSP header (`document.head`, response headers).
- Identify the host(s) in `script-src` with path components.
- For each, scan for `?redirect=`, `?next=`, `?url=` parameters or other
  open-redirect primitives.
- For each, check whether the same host hosts user-controlled content
  (uploads, GitHub-pages-style paths, etc.).

## Triggering

```
CSP: script-src https://cdn.example.com/safe/
```

Open redirect at `https://cdn.example.com/safe/redirect?to=...` lets:

```html
<script src="https://cdn.example.com/safe/redirect?to=https://cdn.example.com/uploads/evil.js"></script>
```

Browser sends initial fetch to `/safe/redirect`, CSP passes,
30x -> `/uploads/evil.js`, executes.

## Bypasses

- Strict-CSP / nonce-based - defeats this technique (each script element
  needs the response nonce in addition to the host match).
- Reverse proxy normalization that strips redirects before browsing -
  rare in practice.

## Seen in the wild

- {date: 2024-05-30, source: CT Ep 73} - Johan Carlsson XSS challenge used this technique against a path-scoped `script-src`.

## References

- Critical Thinking Podcast Ep 73 - <https://www.youtube.com/watch?v=uHOxsmdsXUA>
- W3C CSP3 - script-src redirect semantics.
- Related: [[../dom-xss/jsonp-callback-csp-bypass]]
