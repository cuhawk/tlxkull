---
title: Salesforce Marketing Cloud (SFDC MC)
slug: target-salesforce-marketing-cloud
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [target/salesforce, target/saas, target/email-platform]
inbound: []
---

# Salesforce Marketing Cloud (SFDC MC)

## What it is

Multi-tenant email marketing / customer-engagement platform inside
the Salesforce ecosystem. Renders outbound emails through a
proprietary server-side template language (**AMPScript**). Hosts
encrypted "view in browser" copies of every sent email at
account-prefixed domains.

## Attack-surface highlights

- **AMPScript renderer** — proprietary template language with
  double-evaluation foot guns and an `HTTPGet()` egress primitive.
  Any user-influenced field that lands in a rendered email is a
  template-injection candidate. See
  [[../techniques/server-side/ampscript-template-injection]].
- **Encrypted QS parameters** — the "view in browser" links carry an
  encrypted `QS` parameter. Format has changed over time; older CBC
  variants coexist with newer JWT variants. The legacy variant is the
  vulnerable one. See
  [[../techniques/server-side/cbc-iv-recovery-null-block]].
- **Multi-tenant blast radius** — successful template injection or
  decryption tends to expose data across tenants, not just the
  attacker's account.
- **First-name field** is a recurring exploit primitive — used as the
  insertion point in multiple chains because it's both
  user-controlled and reliably rendered into emails.

## Prior findings

- **2026-05 — "Ghosts of Encryption Past" (Searchlight Cyber).**
  Double-evaluation in subject + first-name. CBC IV recovery against
  legacy QS variant. Cross-tenant email read.
  Source: [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).
- **~2025 (undisclosed) — Justin Gardner + Evan Conley + Chubbs.**
  Same `TreatAsContent` + `HTTPGet` chain pattern, payload hosted on
  a `.gg` domain. Earlier instance of the same primitive class.

## Triage signal

When working SFDC MC scope:

1. Test `%%=1+1=%%` and `{{=1+1=}}` in every user-influenced field
   that ends up in an outbound email or a rendered preview page.
2. Decode the `QS` parameter on view-in-browser URLs; check format
   variants (JWT vs hex vs raw). Bit-flip the hex variant. Look for
   the junk-character oracle.
3. Watch for the rare third "raw parameters" variant — it's often the
   most permissive of the three.

## Related

- [[../techniques/server-side/ampscript-template-injection]]
- [[../techniques/server-side/cbc-iv-recovery-null-block]]
- [[../tools/padre/notes]]
