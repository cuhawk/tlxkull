---
title: Intercom widget identity bypass — read victim chats
slug: intercom-widget-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/idor, technique/auth-bypass]
inbound: []
---

# Intercom widget identity bypass

Douglas Day (Archangel) — d-day.us blog Nov 2021.

## Pattern
When Intercom widget is embedded without `identity_verification`, attacker
can call `Intercom('boot', {email: 'victim@x'})` or
`Intercom('update', {email: 'victim@x'})` from browser console to load
the support session of any other user, reading their chat history.
Sales-team-installed widgets miss the verification ~10–20% of the time.

Test emails like `test@test.com` often hit a real prior sales chat.

Bug-bounty platform vendor used Intercom widget; via boot-as-user attacker
viewed support chats containing PII (SSNs/addresses) and got a hardcoded
temp password (e.g. `summer123`) reset to take over researcher accounts.

## Preconditions
- Target embeds Intercom widget without `identity_verification`.

## Detection
- Open DevTools → check `window.Intercom` is defined and accepting
  `boot()`/`update()` without HMAC.
- `Intercom('boot', {email:'test@test.com'})` — if loads chat history,
  vulnerable.

## Triggering
```js
Intercom('boot', {email: 'victim@example.com'});
// open Intercom panel, read chat history
```

## Related
- [[match-replace-admin-flag]] — Douglas Day match-and-replace
  endpoint discovery.

## Seen in the wild
- Bug-bounty platform vendor (referenced anon by Douglas).
- Critical Thinking Podcast Ep 35.

## References
- d-day.us — Intercom write-up Nov 2021
- Douglas Day "100 Very Short Bug Bounty Rules" Twitter thread
- Critical Thinking Podcast Ep 35
