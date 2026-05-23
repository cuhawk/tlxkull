---
title: Microsoft Storm-0558 Outlook key forge (May-Jun 2023)
slug: ms-storm-0558
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, surface/cloud-idp, technique/key-theft, technique/token-forgery, technique/crash-dump-leak, actor/storm-0558]
inbound: []
---

# Microsoft Storm-0558 Outlook key forge (May-Jun 2023)

## What happened

Between 2023-05-15 and 2023-06-16 a China-nexus actor Microsoft
tracks as **Storm-0558** read mailboxes at ~25 organisations,
including **US Department of State**, **US Department of Commerce**
(Secretary Raimondo), and an unspecified set of US House staff
inboxes. Detection came from a State Department analyst who noticed
anomalous `MailItemsAccessed` audit logs -- a log type only customers
on the E5 SKU had at the time. Microsoft itself did not detect the
intrusion.

The attacker held a **Microsoft Account (MSA) consumer signing key**
they should never have had. They used it to mint signed JWTs for
arbitrary OWA / Outlook.com mailboxes. Because of a **token-validator
bug** in some Microsoft and third-party libraries, the same MSA
consumer key could also produce tokens that validated against
**Exchange Online Enterprise (Azure AD)** -- a cross-realm validation
gap that nobody had documented before. The April 2024 **CSRB report**
called the breach "preventable" and Microsoft's security culture
"inadequate". Microsoft initially blamed a crash-dump exfiltration
path; they retracted that explanation in March 2024 and now state
they do not know the key-acquisition mechanism.

## Attack chain

1. **MSA consumer signing key theft.** Microsoft's initial hypothesis:
   the key was present in a crash dump of a consumer signing service
   that was moved into a corporate debugging environment; an
   engineer's account was later compromised and the dump exfiltrated.
   In March 2024 Microsoft retracted that hypothesis, stating they
   have no log evidence supporting it; the true acquisition path is
   still publicly unknown.
2. **Token forge -- consumer scope.** The actor signed JWTs claiming
   `aud=outlook.office.com` and arbitrary `oid` (object id) for MSA
   consumer mailboxes. MSA token validation accepted the signature
   because the key was a valid MSA signing key.
3. **Cross-realm forge -- enterprise scope (the bug).** A bug in
   `getSigningKeys()` in Microsoft's identity SDK and in
   common.aad.microsoft endpoints did not differentiate between MSA
   keys and AAD keys. A token signed by an MSA key with an AAD
   `iss` / `aud` claim was accepted as if it were AAD-signed --
   bypassing the realm separation that exists exactly so a consumer
   key cannot mint enterprise tokens.
4. **Pull mailbox content via OWA API.** With forged AAD tokens the
   actor used the Exchange Online REST API and OWA endpoints to pull
   full mailbox contents from targeted enterprise tenants.
5. **Detected by a customer's E5 audit log.** State Dept analyst
   spotted `MailItemsAccessed` events that didn't correspond to any
   normal session and reported up. Microsoft revoked the key on
   2023-07-03; public disclosure 2023-07-11.

## Lessons for bug hunters

- **Cross-realm token validation is a class.** When a target's auth
  stack accepts JWTs from multiple issuers (consumer, enterprise,
  partner, B2C), audit *every* validator path: does it check
  `iss` / `tid` / key-source as a tuple, or just verify the signature
  against any key it can resolve? See [[jwt-multitenant-key-confusion]].
- **Key validity windows.** The stolen key was *inactive* / pre-2021
  but the validators did not enforce the rotation cliff. When
  reviewing a target's signing infrastructure, look for any code path
  that resolves a kid (key id) by listing -- a long list of valid
  historical keys is the same as a long-lived breach surface.
- **Crash-dump scrubbing is a real control.** Heap memory in a
  signing service crash dump is where private keys live. Programs
  that handle keys in HSMs should scrub heap before any dump leaves
  the secure enclosure. For your own findings, demonstrate "secret
  reached debug env" as a chain step where possible.
- **Microsoft's customer-side telemetry gap was the headline
  finding.** Premium-only `MailItemsAccessed` logs meant 75% of
  affected tenants could not even detect the breach. When you write
  up a report against a SaaS vendor, note explicitly what audit log
  the customer needs to *see* your PoC -- it's part of the impact
  story.
- **CSRB-style root-cause storytelling sells findings.** Pair every
  technical primitive with the org-level control that should have
  caught it (rotation, scrubbing, validator differentiation, customer
  log parity). Synack triage rewards reports that name the missing
  control. Cross-link [[csrb-style-rca]].

## Primary sources

- [CSRB: Review of the Summer 2023 Microsoft Exchange Online Intrusion](https://www.cisa.gov/sites/default/files/2025-03/CSRBReviewOfTheSummer2023MEOIntrusion508.pdf)
  -- the 34-page DHS report with 25 recommendations and the
  "preventable" verdict.
- [Microsoft: Analysis of Storm-0558 techniques for unauthorized email access](https://www.microsoft.com/en-us/security/blog/2023/07/14/analysis-of-storm-0558-techniques-for-unauthorized-email-access/)
  -- Microsoft's primary technical write-up of the token-forge path
  and the cross-realm validator bug.

## Related

- [[okta-lapsus]]
- [[jwt-multitenant-key-confusion]]
- [[csrb-style-rca]]
