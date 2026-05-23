---
title: CircleCI Jan 2023 OAuth token theft
slug: circleci-2023-oauth
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, scope/ci-cd, technique/session-cookie-theft, technique/infostealer, technique/2fa-bypass]
inbound: []
---

# CircleCI Jan 2023 OAuth token theft

## What happened

On **2022-12-29** a CircleCI customer reported suspicious activity on
their **GitHub OAuth token**. CircleCI's investigation found that on
**2022-12-16** one of its engineers had been infected with
**information-stealing malware** that the corporate AV did not flag.
The malware exfiltrated a **valid authenticated session cookie** for
CircleCI's internal SSO; because the cookie was already past the 2FA
step, the attacker could replay it to log in as the engineer and skip
2FA entirely. The engineer's role allowed generating production
access tokens, and the attacker used that to read CircleCI's customer
secrets database.

On **2023-01-04** CircleCI publicly disclosed and forced **mass
rotation of every customer GitHub and Bitbucket OAuth token** issued
through the platform, plus all stored project env vars, contexts,
SSH keys, and API tokens. Customers that did not rotate had to assume
every secret in their pipeline was compromised. The breach window for
data access was roughly **2022-12-16 → 2023-01-04**.

## Attack chain

1. **Infostealer drop on engineer laptop.** Specific malware family
   was not publicly named; behaviour matches RedLine / Vidar-class
   commodity stealers that scrape browser cookies, password stores,
   and crypto wallets. Loaded onto the engineer's device on 2022-12-16
   via a vector CircleCI did not publish.
2. **AV blind spot.** The variant was new enough that the engineer's
   endpoint AV did not flag it. CircleCI later added explicit MDM/AV
   rules for the observed behaviour, implying the original was
   signature-only-detection territory.
3. **Session cookie replay bypasses 2FA.** The stolen cookie was a
   post-SSO session token tied to the engineer's SSO identity. SSO +
   2FA had been enforced at login but the long-lived session cookie
   was not bound to device or IP, so the attacker replayed it from
   their own host. (This is the same primitive used in
   [[heroku-travis-oauth-2022]] OAuth-token replay.)
4. **Lateral move to prod via role abuse.** The compromised account
   had permission to generate production access tokens. Attacker
   issued tokens, queried the secrets-storage subsystem, and
   exfiltrated **customer env vars, GitHub OAuth tokens, project SSH
   keys, and context values** for ~every active project.
5. **Mass rotation as remediation.** CircleCI invalidated all customer
   GitHub OAuth tokens server-side, requiring every CircleCI customer
   to reauthorize. Customers had to additionally rotate any secret
   stored in CircleCI (~hours to days of cross-org incident response).

## Lessons for bug hunters

- **Session cookies that survive 2FA are tier-1 targets.** On any
  bug-bounty target, if a session cookie remains valid after MFA
  challenge and is not bound to device fingerprint / IP / TLS-CB, it
  is exfilable via XSS, infostealer, or browser extension. Probe by
  exporting the auth cookie from one browser session and replaying it
  from another network -- if it works, that is a finding on its own
  (session hijack via cookie). See [[heroku-travis-oauth-2022]] for the
  third-party-token analogue.
- **OAuth tokens stored at vendor = vendor-controlled blast radius.**
  When a target uses GitHub/Bitbucket OAuth via a third-party SaaS,
  the SaaS holds long-lived refresh-capable tokens. If the SaaS is
  compromised, every customer is compromised. As a hunter, report
  "OAuth token scope too broad" findings (e.g. CI vendors that
  request `repo` instead of `repo:status`) -- programs pay for these.
- **`echo` and CI step output equals secret leakage.** Any CI vendor
  that exposes env vars to step output is one `set -x` away from
  spilling them. Audit your target's CI for `set -x`, `bash -x`,
  `echo "$SECRET"`, and any step that prints env or `printenv`.
  Same primitive surfaces in [[tj-actions-changed-files]] and
  [[codecov-bash-uploader]].
- **Engineer endpoints are the most reliable entry point.** Vendors
  publicise "0 customer impact via prod" while a developer laptop is
  the actual root cause. When triaging a vendor's blast radius,
  always ask: which internal humans can issue tokens? How are their
  sessions bound? Treat the answer as the trust boundary.
- **Forced-rotation events are recon goldmines.** When a vendor
  forces rotation, customers leak which tokens they rotated and when
  in public status pages, commit messages
  (`fix: rotate codecov token`), and PR descriptions. This is a
  reliable signal of where high-value secrets live in a target's
  infra.

## Primary sources

- [CircleCI: "CircleCI incident report for January 4, 2023 security incident"](https://circleci.com/blog/jan-4-2023-incident-report/)
  -- official post-mortem including the cookie-replay mechanism.
- [BleepingComputer: "CircleCI's hack caused by malware stealing engineer's 2FA-backed session"](https://www.bleepingcomputer.com/news/security/circlecis-hack-caused-by-malware-stealing-engineers-2fa-backed-session/)
  -- detailed reporting on the malware behaviour and AV evasion.

## Related

- [[heroku-travis-oauth-2022]]
- [[codecov-bash-uploader]]
- [[tj-actions-changed-files]]
