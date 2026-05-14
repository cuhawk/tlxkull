---
title: Bcrypt 72-byte Input Truncation in Concatenated Hash Schemes
slug: bcrypt-72-byte-truncation
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/crypto, technique/auth-bypass]
inbound: []
---

# Bcrypt 72-byte Input Truncation in Concatenated Hash Schemes

## Pattern

Bcrypt silently truncates inputs longer than 72 bytes before hashing. When
application code concatenates multiple values (e.g. `username + password +
padding`) into a single bcrypt input, a sufficiently long prefix component
can push the password (or another secret component) out of the truncation
window. The resulting hash depends only on the prefix bytes - auth-bypass:
any password (or even empty) hashes to the same stored value.

The October 2024 Okta CVE is the canonical example: accounts with usernames
>= 52 characters (52 + password + ~20-byte padding) could authenticate with
any password.

## Preconditions

- Application uses bcrypt for password hashing.
- The bcrypt input is a **concatenation** containing user-controlled data
  AND the secret/password, in that order (or with the secret near the tail).
- The user-controlled component can be made long enough that the secret
  falls past the 72-byte boundary.
- No HMAC/SHA pre-hash that would compress the input to a fixed size before
  bcrypt.

## Detection

- Whitebox: look for `bcrypt.hashpw(username + password)`,
  `bcrypt.hashpw(f"{user.email}:{password}")`,
  `bcrypt.compare(req.body.user + req.body.pass, stored)`, or any pattern
  that builds a bcrypt input from multiple fields without pre-hashing.
- Length test: create an account with a >= 72-byte username/email. Attempt
  login with random passwords. If any password works, confirmed.
- Read source documentation (PHP, bcryptjs, py-bcrypt) - most explicitly
  warn about the 72-byte limit.

## Triggering

1. Identify whether registration accepts long usernames or emails (some
   targets cap at 64; some allow 254 RFC 5321 max).
2. Register a victim-style account or shadow account with a >= 72-byte
   primary identifier.
3. Log in with any password.
4. If bypass occurs only on accounts above a specific threshold (e.g. 52
   chars), the application is appending fixed padding - compute the exact
   threshold by varying username length one byte at a time.

## Bypasses

Not applicable - this is itself a bypass of password authentication.

## Seen in the wild

- {date: 2024-11-14, source: CT Ep 97} - Okta disclosed an internally-discovered bcrypt truncation in their authentication path: usernames >= 52 characters allowed login with any password. Fix: switched to PBKDF2.

## References

- Okta security advisory (Oct 2024) - bcrypt truncation auth bypass.
- PHP.net `password_hash` docs - explicit 72-byte warning.
- Critical Thinking Podcast Ep 97 - <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- Related: [[../jwt/none-algorithm-bypass]] - another "trust the library blindly" auth bypass class.
- [Server-side SUMMARY](SUMMARY.md)
