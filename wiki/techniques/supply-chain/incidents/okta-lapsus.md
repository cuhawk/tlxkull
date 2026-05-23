---
title: Okta / Lapsus$ Sitel breach (Jan 2022)
slug: okta-lapsus
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, surface/idp, technique/third-party-contractor, technique/session-hijack, actor/lapsus]
inbound: []
---

# Okta / Lapsus$ Sitel breach (Jan 2022)

## What happened

Between 2022-01-16 and 2022-01-21, the extortion crew Lapsus$
obtained interactive access to a customer-support engineer's
workstation at **Sitel** (a sub-processor Okta contracts for tier-1
support, acquired from Sykes). For roughly 25 minutes inside that
window, the attacker held a console-level session in an Okta
"SuperUser" / customer-tenant admin tooling that allows tenant-side
password resets and MFA factor resets. Okta's later forensics put the
maximum potential impact at **366 customer tenants** (~2.5% of Okta's
book at the time), though Okta said no customer-tenant compromise was
confirmed.

Public disclosure happened only on 2022-03-22, after Lapsus$ posted
screenshots of the support console to Telegram. Okta's initial
position -- that no customers were impacted -- collapsed within 48
hours, and CEO Todd McKinnon publicly admitted the 60-day disclosure
delay was a mistake. The incident reframed identity providers as
single points of supply-chain failure for every SaaS app they front.

## Attack chain

1. **Initial access via support contractor.** Lapsus$ obtained
   credentials for a Sitel support engineer (likely via an info-stealer
   log or a SIM-swap; the Sitel/Mandiant report timeline is partially
   redacted). The engineer's workstation was reachable via RDP through
   the SuperOps remote-management stack Sitel uses to administer
   support agents.
2. **Persistence via MFA factor add.** On 2022-01-20 Okta's security
   team got an alert that a *new password factor* was added to the
   Sitel engineer's Okta account from a novel device. The attacker did
   not pass the push-MFA challenge, but the factor add itself was the
   indicator.
3. **Console pivot.** Inside the active RDP session the attacker
   reached the Okta SuperUser/admin tool the engineer normally used to
   service customer tickets -- tenant search, password reset, factor
   reset -- with read access to support-relevant fields per tenant.
4. **25-minute live window.** Okta forensics later bounded the
   "interactive in-console" time to a 25-minute window. Hundreds of
   tenant records were viewable in principle during that window.
5. **Disclosure lag.** Sitel investigated through January and February;
   Mandiant report reached Okta on 2022-03-17. Okta did not notify the
   366 customers. Lapsus$ went public on 2022-03-22 with screenshots,
   forcing the disclosure.

## Lessons for bug hunters

- **The IdP soft underbelly is the support tooling, not the IdP
  itself.** When you target an enterprise via its SaaS, ask: which
  admin/support app can reset MFA for the user you want? Who staffs
  that app? Often it's a BPO contractor reachable via a customer
  portal. The auth boundary you care about is the *admin tool's*
  auth, not the IdP's. Cross-link [[support-tool-tenancy-bypass]].
- **MFA factor-add events are gold for IR teams and audit targets.**
  Any admin-facing app that allows adding a credential factor to a
  *third-party tenant* without strong intra-tenant authorization is a
  high-impact bug. Look for tenant-id-in-URL primitives and try
  IDOR-by-id-rotation. See [[caido-idor]].
- **Sub-processor sprawl is in scope.** A target's SaaS vendor's BPO
  contractor's remote-admin tool is four hops from the asset and
  every hop has its own credential pool. Synack/H1 programs
  increasingly accept reports where the proven exploit chain crosses
  vendor boundaries (with documented impact).
- **Disclosure clocks matter for legal-eligibility analysis.** Okta
  delayed 60 days; SEC later opened inquiries. For your own findings,
  capture immutable timestamps (Caido replay logs, screenshots with
  ntp-verified clock) so a vendor cannot post-date what you reported
  when.
- **A 25-minute window is forever in extortion-actor time.** Token
  scopes, session lifetimes, and "just-in-time" admin elevation are
  audit-worthy controls. Compare to [[oktapus-twilio]].

## Primary sources

- [Okta: Investigation of the January 2022 Compromise](https://www.okta.com/blog/2022/03/oktas-investigation-of-the-january-2022-compromise/)
  -- official Okta post-mortem with the 25-minute bounding analysis.
- [Cloudflare: Cloudflare's investigation of the January 2022 Okta compromise](https://blog.cloudflare.com/cloudflare-investigation-of-the-january-2022-okta-compromise/)
  -- third-party impact analysis with the customer-tenant
  cross-reference logic any defender would want to run.

## Related

- [[oktapus-twilio]]
- [[support-tool-tenancy-bypass]]
- [[ms-storm-0558]]
