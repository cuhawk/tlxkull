---
title: Defunct-domain SSO takeover (Truffle Sec)
slug: defunct-domain-sso-takeover
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/oauth, technique/sso, technique/recon, technique/supply-chain]
inbound: []
---

# Defunct-domain SSO takeover

Truffle Sec research — Google OAuth + downstream SaaS.

## Pattern
Many SaaS tools key user accounts by `email`+`hd` (hosted domain) from
Google OIDC. When a startup folds or migrates domains, its old domain
expires and becomes purchasable. Buying it lets the attacker stand up
Google Workspace on the old domain, re-create the email addresses of
the former employees, and **sign back into** every downstream SaaS that
those former employees registered with using Google SSO — full account
takeover for any data left in those SaaS tools.

The OIDC spec recommends pairing `email` with an immutable subject
identifier (`sub`) per-tenant. Most downstream apps don't enforce it.
Truffle Sec proposed adding two immutable identifiers to the OIDC flow;
Google awarded $1,337 and is reportedly considering the change.

## Preconditions
- Target SaaS uses Google SSO and identifies users by `email` + `hd` (not
  by `sub` paired with `hd`).
- Source organization has folded / migrated, freeing the domain.
- Attacker can register the domain (rare but happens).

## Detection / recon
- Identify your target's vendor list (publicly disclosed customers,
  case studies, "Powered by ...", BIMI/SPF/DMARC of received marketing
  emails).
- Cross-reference against expired/expiring domains (Whois, certificate
  transparency expirations, LinkedIn employee profiles that mention
  defunct previous employers).
- Re-register the candidate.

Related primitive (Nagli ATO): dump tenant user-list from a leaked dev
token, find users on email domains pending renewal, register one, walk
in via SSO.

## Bypasses / hardening
- Downstream SaaS: pair `email` with `sub` per-tenant; new sub = new
  user (force re-invite or admin re-approval).
- Pair domain renewal with internal account-lifecycle (HR offboarding
  closes SaaS accounts even when the user-account isn't in the IDP).

## Seen in the wild
- {date: 2025-01, source: CT Ep 107} — Truffle Sec; $1,337 Google VRP.
- Earlier related: Nagli Azure SSO defunct-domain ATO (covered in
  CT 2024-recap episode).

## References
- Truffle Sec blog — OAuth bugs affecting millions of accounts
- Critical Thinking Podcast Ep 107
- Related: [[mutable-claim-ato]], [[redirect-uri-bypass]]
