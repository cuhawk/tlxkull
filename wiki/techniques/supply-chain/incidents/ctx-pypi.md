---
title: ctx PyPI maintainer-domain takeover (May 2022)
slug: ctx-pypi
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/python, registry/pypi, technique/domain-takeover, technique/account-takeover, exfil/aws-keys]
inbound: []
---

# ctx PyPI maintainer-domain takeover (May 2022)

## What happened

Between **21 and 24 May 2022** the abandoned PyPI package `ctx` (a tiny
dict-utility library, last released 19 Dec 2014) suddenly published
versions `0.1.2`, `0.2.0`, `0.2.1`, and `0.2.2`. Each new release
carried code that walked `os.environ` and POSTed every variable -- most
importantly anything matching `AWS_*` -- to
`anti-theft-web.herokuapp.com`. The same operator hijacked the
`hautelook/phpass` GitHub repo (the canonical PHPass distribution) by
re-registering the deleted `hautelook` GitHub username and pushing an
identical exfil payload into the PHP source.

The takeover root-cause was the original maintainer's email domain
`figlief.com`, which had expired. The attacker (later self-identified
as an Istanbul-based researcher) **bought the domain for ~$5 on 14 May
2022**, stood up a mailbox for the maintainer address, then walked the
PyPI password-reset flow. SMS-OTP / MFA was not enforced. The
[SANS ISC handler diary entry #28678][isc] caught the new
versions within ~36 hours of the first malicious upload and the
packages were yanked by PSF.

## Attack chain

1. **Identify dormant package + maintainer email.** PyPI exposes the
   uploader email in package metadata historically; trivial to scrape
   for `*@<random-domain>` where the domain is in `WHOIS` `pendingDelete`
   or already expired.
2. **Buy the expired domain.** ~$5 registration, set up a catch-all MX
   so `figlief@figlief.com` (the maintainer address) receives mail.
3. **Trigger PyPI password reset.** Mail arrives at the now-attacker
   mailbox; reset password; log in as the maintainer.
4. **Publish poisoned releases.** Bump version repeatedly so any
   pinned-range `ctx>=0.1.1` install pulls the malicious wheel. Code
   adds an `__init__` side effect that exfiltrates `os.environ` (notably
   `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`)
   to a Heroku endpoint.
5. **Parallel hit on PHP.** Same operator re-registered the deleted
   `hautelook` GitHub account, recreated the `phpass` repo with the
   same Heroku exfil URL. Composer users who pulled `hautelook/phpass`
   by HEAD got the implant.

## Lessons for bug hunters

- **WHOIS-watch every maintainer email of every dependency your target
  pins.** A pinned `requirements.txt`, `package.json`, `composer.json`
  is a list of attack surfaces -- one expired domain per row. The same
  primitive nets paid bounties on programs that depend on niche libs.
  Cross-link [[xz-utils-cve-2024-3094]] (social-engineering maintainers)
  and [[pytorch-torchtriton]] (registry namespace confusion).
- **PyPI maintainer scrape is in scope on most programs.** Package
  metadata is public; mapping `email → domain → registrar status` is
  passive recon -- no requests to the target's own infra.
- **AWS keys in CI env vars are the universal payoff.** Any
  `pip install` step in a CI runner or developer laptop with assumed
  AWS creds exports them to `os.environ`. A package's `setup.py` or
  module-load side effect runs in the same process as the build.
- **Heroku / free-tier ephemeral hosting is the standard C2.** Look for
  exfil endpoints on `*.herokuapp.com`, `*.glitch.me`, `*.vercel.app`,
  `*.workers.dev` in any newly-published package.
- **PyPI now blocks 1800+ known-expired-domain emails** post-incident
  (see follow-up reporting), but the class is not closed -- npm and
  RubyGems still allow registration with any deliverable mailbox.

## Primary sources

- [SANS ISC Handler Diary #28678 -- "ctx Python Library Updated with Extra Features" (Yee Ching, 24 May 2022)][isc]
- [Python Security advisory: "Account Takeover and Malicious Replacement of ctx Project" (Victor Stinner)](https://python-security.readthedocs.io/pypi-vuln/index-2022-05-24-ctx-domain-takeover.html)

[isc]: https://isc.sans.edu/diary/ctx+Python+Library+Updated+with+Extra+Features/28678

## Related

- [[xz-utils-cve-2024-3094]]
- [[pytorch-torchtriton]]
- [[ultralytics-pypi]]
