---
title: Maintainer account takeover via lapsed domain
slug: maintainer-domain-takeover
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/supply-chain, technique/account-takeover, registry/npm]
inbound: []
---

# Maintainer domain takeover

## Pattern

Open-source maintainers love custom-domain email
(`alice@alice-codes.com`). When the domain lapses, npm/PyPI **do not
re-verify** that the maintainer still owns the email -- only that the
maintainer can read mail. Buy the lapsed domain, set up MX, request
password reset on the registry, log in, publish a backdoored minor
version. Matthew Bryant (Snap -> research) used this to take over an
Angular dependency; the same pattern keeps recurring in supply-chain
weak-link audits.

npm + PyPI made 2FA mandatory only for packages with >1M weekly
downloads or >500 dependents (npm 2022) -- everything below that
threshold remains 2FA-optional.

## Preconditions

- Target package's maintainer uses a custom domain in their registry
  email.
- Domain is expired and re-registrable.
- Maintainer has not enabled 2FA -- registry-side bypass is not the
  attack; password reset is.

## Detection

- Pull maintainer emails from `npm view <pkg> maintainers` or PyPI
  `/pypi/<pkg>/json` `info.author_email`.
- Run domains through a registration / WHOIS lookup; flag any in
  `pending-delete` or `redemption` status.
- Filter to packages with no 2FA badge (npm shows it on the package
  page).

## Triggering

1. Register the lapsed domain.
2. Set up catch-all MX -> inbox.
3. Initiate password reset on npm/PyPI.
4. Login, publish a minor version with malicious `postinstall` /
   top-level code.

## Bypasses

- 2FA-mandatory tiers (>1M weekly DL on npm): need a separate vector.
- Some registries are starting to email forward via the original-registered
  address -- verify the reset flow before buying.

## Defender-side notes

- Pre-claim doppelganger / typo domains for ops-critical maintainers.
- Pin packages by content-addressable hash (`integrity:` in
  `package-lock.json`) -- even hijacked maintainer can't backdoor a
  pinned version.
- Mandatory 2FA + WebAuthn for all package publishers.

## Seen in the wild

- {date: 2021, source: Matthew Bryant / Snap research} -- Angular dep
  takeover.
- {date: 2024, source: CT Ep 74} -- depi survey: domain takeover is one
  of the biggest measured weak links in npm/PyPI supply chain.

## References

- Critical Thinking Podcast Ep 74
- Matthew Bryant -- maintainer domain takeover Angular write-up
- "Weak Links of npm Supply Chain" paper (cited in Ep 74)
- Related: [[dependency-confusion]]
