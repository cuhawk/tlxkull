---
title: Account pre-creation by email on guest checkout
slug: account-precreate-guest-checkout
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/idor, technique/auth-bypass]
inbound: []
---

# Account pre-creation by email on guest checkout

## Pattern
Many shop sites: guest checkout creates an account keyed on email. Later
signup with the same email + no email validation = access to other
people's orders. Chain with self-stored XSS for ATO.

## Preconditions
- Guest-checkout flow that persists an account keyed on email.
- Self-signup flow that re-uses or upgrades the same email-keyed account
  without re-verification.

## Detection
- Place an order as guest with `victim@gmail.com`.
- Self-signup with `victim@gmail.com` → check if you receive prior
  order history.

## Triggering
1. Guest checkout with victim email.
2. Sign up with same email → if no email-confirmation, you inherit the
   account.

## Related
- Yelp self-XSS → ATO via cookie-bridge + cookie-bombing (Ep 62, H1
  #2089042).

## Seen in the wild
- Critical Thinking Podcast Ep 8.

## References
- Critical Thinking Podcast Ep 8
