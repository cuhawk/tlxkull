---
title: CBC IV Recovery via 8-Byte Null Block + Known-Plaintext Brute Force
slug: cbc-iv-recovery-null-block
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [technique/crypto, technique/cbc, technique/server-side]
inbound: []
---

# CBC IV Recovery via 8-Byte Null Block

## What this is

A primitive for recovering the **IV** of an unauthenticated CBC-mode
ciphertext when you know the **format** (not necessarily exact bytes)
of the first plaintext block. With the IV in hand, the first block
decrypts trivially, the rest of the ciphertext follows by chaining,
and bit-flipping attacks become fully directed instead of blind.

## When to use

- App returns CBC ciphertext in a URL parameter, cookie, or token.
- No MAC / authentication tag — bit-flipping doesn't 500 or 403.
- You have a Stack Overflow / docs / leaked sample of the plaintext
  **shape** (e.g., `{"emailId":<int>,"region":"<2-letter>",...}` or
  pipe-delimited fields).
- You see "junk" characters in decoded output when you flip bits — a
  reliable tell that the engine is unauthenticated CBC.

## The primitive

CBC decryption of block-1:

```
P1 = D(C1) XOR IV
```

Pad the start of the ciphertext with **8 null bytes** so the first
block `C1` decrypts to `D(0...0)` — an unknown but deterministic
value. The output of the decryption function gets XORed with the IV
to produce the first plaintext block.

Then for each **byte** (or bit) of the IV:

1. Guess the byte.
2. Submit; the second block's decryption now depends on the IV
   recovery state.
3. Examine the response — does the *second* plaintext block (which is
   the original first block XORed against your candidate) match a
   byte position of the known plaintext format?
4. If yes, that IV byte is recovered. Move to next byte.

Iterating across a handful of valid IDs and re-running the brute force,
the IV is fully recovered. Decrypt the first block, then continue with
standard CBC bit-flipping for everything downstream.

## Tooling

- [[../../tools/padre/notes]] (Padre) — padding-oracle / CBC framework.
  Extensible. Handles the bit-flipping book-keeping.
- A small Python harness that submits candidates and parses response
  shape is usually enough once you've nailed the oracle signal.

## Confirmation signals

- **Junk character substitution** — flipping bits in C1 causes random
  characters (often `?` or unicode replacements) to appear at predictable
  offsets of the rendered output. That visual artifact == unauthenticated
  CBC.
- **Multiple ciphertext format variants in one app** — a strong "spidey
  sense" tell. Format A is the new one, format B the old; the glue
  layer often accepts both, and the *old* format is where the
  vulnerable path lives. Hunt the legacy variant.

## Seen in the wild

- **2026-05 — Salesforce Marketing Cloud "Ghosts of Encryption Past"
  (Searchlight Cyber)** — `QS` URL parameter behind email view-in-browser
  button. Three coexisting variants: JWT (modern), hex CBC (legacy
  vulnerable), raw plaintext (oldest, discovered last). 8-byte null-block
  trick + Padre + Stack-Overflow plaintext shape → full decryption.
  Chained with [[ampscript-template-injection]] for tenant data exfil.
  Source:
  [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).

## Heuristics worth remembering

- **Try other formats / encodings even after the "real" one works.** Legacy
  paths leak in patched apps. Same rule as "if JSON works, try
  form-urlencoded / XML".
- **Don't shy away from crypto.** Most app-layer crypto is misimplemented.
  Bit-flip every unauthenticated CBC ciphertext you see; the oracle
  signal is often visible in the first response.
- **Know one byte of plaintext format** = enough to recover the IV. You
  don't need the full plaintext.

## Related

- [[ampscript-template-injection]] — paired with this in the SFDC chain
- [[../../tools/padre/notes]] — the standard tool
