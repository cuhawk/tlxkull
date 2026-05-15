---
title: cPanel / WHM
slug: target-cpanel
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [target/cpanel, target/hosting, target/perl]
inbound: []
---

# cPanel / WHM

## What it is

Legacy server-management control panel used by shared-hosting
providers worldwide. **Perl-based**. WebHost Manager (WHM) is the
admin-tier sibling. Session state is written to flat files on disk.

## Attack-surface highlights

- **Session files on disk** at `/var/cpanel/sessions/raw/<session_id>`
  (and analogous paths). `\r\n`-delimited key/value records. Anything
  that smuggles `\r\n` into a value becomes an attribute-injection
  primitive. See
  [[../techniques/server-side/cpanel-crlf-session-injection]].
- **Multiple auth channels** — cookie auth, header auth, sometimes
  URL-token auth — feed the same session record without joint
  normalisation. Combine them to bypass per-channel sanitization.
- **Cache vs disk** — session reads often hit an in-memory cache. Any
  on-disk injection requires a second primitive that forces cache
  reload before exploitation.
- **Three management ports, not two.** WHM exposes a reverse-proxy
  port that proxies into the backend management ports. Patches that
  only block the obvious management ports leave this third surface
  open.
- **Perl legacy comments** in patches are unusually verbose and often
  name the primitive directly. Always read the patch diff comments
  first.

## Prior findings

- **2026-03 — pre-auth bypass.** CRLF injection into the on-disk
  session record via combined cookie+header auth. Reverse-engineered
  from the patch by Watchtower; independent writeup + detection
  script from Searchlight Cyber.
  Source: [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).

## Triage signal

- Whenever cPanel ships a patch, **read the patch's source-level
  comments**. Perl maintainers tend to write commentary that
  describes the exact primitive being fixed.
- Look at every auth input that gets written into the session record
  — they're frequently sanitised in isolation but not jointly.
- Cache-vs-disk priority: when an on-disk injection fails to take
  effect, look for a second endpoint that forces a cache reload.

## Related

- [[../techniques/server-side/cpanel-crlf-session-injection]]
