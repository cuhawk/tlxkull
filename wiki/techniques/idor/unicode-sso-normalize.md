---
title: Unicode email-normalization SSO confusion
slug: unicode-sso-normalize
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/idor, technique/auth-bypass, technique/unicode]
inbound: []
---

# Unicode SSO normalization

## Pattern
Register `adminª@gmail.com` (ª = U+00AA Feminine Ordinal Indicator)
on app A. SSO/identity layer normalizes `ª`→`a` when handing identity to
app B → log in as `admin@gmail.com` on app B.

Per-service email validation differs from SSO normalization.

## Preconditions
- SSO between two services where:
  - App A's signup validation accepts the lookalike Unicode char.
  - SSO/identity handoff or App B's lookup normalizes (NFKC, etc.) → strips
    the diacritic and matches victim email.

## Detection
- Register account with various Unicode lookalikes (ª, à, ñ, ı for i,
  full-width chars).
- Traverse SSO endpoints across all subdomains until one normalizes.

## Triggering
1. Register `adminª@gmail.com` on app A.
2. Verify own email (lookalike address you control via catch-all or via
   gmail-doesnt-exist trick).
3. SSO into app B → identity claim sent as `admin@gmail.com`.

## Related
- TLD regex dot-wildcard `.*\.co\.jp$` matches `whatevercojp` (Ep 44).
- Backslash userinfo URL bypass (Ep 44).

## Seen in the wild
- Critical Thinking Podcast Ep 16 — Hacker's Toolkit.

## References
- Critical Thinking Podcast Ep 16
- Unicode Standard NFKC normalization
