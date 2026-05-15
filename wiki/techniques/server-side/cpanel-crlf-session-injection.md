---
title: cPanel CRLF Session-File Injection → Auth Bypass
slug: cpanel-crlf-session-injection
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [technique/server-side, technique/auth-bypass, technique/crlf, target/cpanel]
inbound: []
---

# cPanel CRLF Session-File Injection → Auth Bypass

## Class

CRLF injection into an on-disk session record. Session file is
`\r\n`-delimited; injecting `\r\n` adds attacker-controlled attributes
(e.g., escalates a pre-auth invalid-credential session to a logged-in
session).

## Target shape

- **Perl** application writing session state to a flat file at
  `/var/cpanel/sessions/raw/<session_id>` (or analogous path).
- Record format is **key\tvalue\r\n** style — one line per attribute.
- Two distinct auth channels writing into the same session record
  without joint normalization: e.g., one path takes input from a
  **cookie**, the other from an **auth header**. Each is sanitized in
  isolation; their concatenation is not.

## Patch comment that gave it away

Look at the public patch / changelog text. The cPanel disclosure
included a comment along the lines of:

> *"filter against \r\n from values before writing — kills the CRLF
> injection primitive against the on-disk key-value record for the
> session."*

That sentence essentially names the primitive. **Always read patch
comments — they leak the bug class.**

## Exploitation outline

1. Trigger an **invalid-credential** login to create a *pre-auth*
   session record on disk (the system writes even unauthenticated
   attempts to track them).
2. Send a request that combines **cookie auth** + **auth-header auth**
   simultaneously. The header path lets you smuggle a value containing
   raw `\r\n`.
3. The smuggled `\r\n` terminates one record and injects new key/value
   lines into the session file.
4. Inject the attributes that mark the session as authenticated
   (typically a "user", "verified", or equivalent flag).

## Roadblocks the original chain hit

- **Cache-vs-disk priority.** The endpoint reads from an in-memory
  cache of the session file, not the disk. Forcing a cache reload
  required finding a separate primitive that invalidated the cached
  entry.
- **Defense-in-depth password recheck.** Some endpoints re-validate
  the password against the session's stored credential. Bypassed by
  injecting an attribute that satisfied or skipped that second check.
- **Three access ports, not two.** WHM exposes a third reverse-proxy
  port that routes into the same management backend. Searchlight Cyber's
  detection script added this as a third probe surface — blocking the
  two "obvious" management ports doesn't patch the bug.

## Seen in the wild

- **2026-03 (patched) — cPanel auth bypass.** Reverse-engineered from
  the patch by **Watchtower** ("Why are we always treated so badly?")
  and independently by **Searchlight Cyber** (who released a
  high-fidelity scanner script — they do this consistently and it's
  worth pulling whenever they ship one). Source:
  [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).

## Hunting checklist (generalised)

- Whenever auth state is **written to a file on disk** (vs DB), assume
  injection-into-format primitives.
- Look for **multiple authentication paths** that merge into one
  record without joint sanitization (cookie + header + URL token).
- Greppable smell: `\r\n`, `chomp`, line-based parsers, key=value
  storage, `tie` / `flock` on session files.
- After patch is public, **read the patch comment first** — Perl/PHP
  legacy patches leak the primitive in plain English more often than
  you'd think.

## Related

- [[../../techniques/server-side/SUMMARY]]
- General CRLF/header-injection notes live alongside SSRF & smuggling
  pages.
