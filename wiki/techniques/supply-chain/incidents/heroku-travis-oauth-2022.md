---
title: Heroku + Travis CI OAuth → GitHub private-repo theft (Apr 2022)
slug: heroku-travis-oauth-2022
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, technique/oauth-token-abuse, scope/ci-cd, registry/npm, registry/github]
inbound: []
---

# Heroku + Travis CI OAuth → GitHub private-repo theft (Apr 2022)

## What happened

On **2022-04-12** GitHub Security detected unauthorised access to
**npm's production infrastructure** via a compromised AWS API key
that had been stored in a private repository. Investigation traced the
intrusion back to **OAuth user tokens** issued by GitHub to two
third-party integrators: the **Heroku Dashboard** GitHub app and
**Travis CI**. The attacker held valid Heroku- and Travis-issued
OAuth tokens for many GitHub users, enumerated each user's orgs, and
**selectively cloned private repositories** from dozens of victim
organisations -- including **GitHub itself / npm**.

GitHub publicly disclosed on **2022-04-15**. Heroku confirmed
exfiltration on **2022-04-09**. The initial vector that gave the
attacker the OAuth tokens (a Heroku-side compromise, a Travis-side
compromise, or shared upstream) has **never been publicly clarified**
by either vendor. Heroku eventually disabled the GitHub integration
entirely while it investigated; npm rotated all keys and audited every
private package source that the attacker could have read.

## Attack chain

1. **OAuth-app token store compromise at integrator.** Both Heroku and
   Travis CI hold long-lived GitHub OAuth user tokens on behalf of
   their customers, scoped to `repo` (full read/write to public + private
   repos). The attacker obtained the integrators' stored tokens at
   scale -- the public disclosure does not say how. (Plausibly: a stolen
   DB backup, a vault credential, an internal engineer compromise akin
   to [[circleci-2023-oauth]].)
2. **Enumeration by org listing.** For each stolen token, the attacker
   called `GET /user/orgs` to map which organisations the victim
   belonged to. This produced a ranked target list of high-value orgs
   (npm, financial services, payments).
3. **Selective private-repo clone.** For each org of interest the
   attacker listed `GET /user/repos?affiliation=organization_member`
   and cloned the private repos. This is fast and quiet -- it shows up
   in GitHub audit logs as normal "Heroku Dashboard" or "Travis CI" API
   calls, which security teams whitelist by default.
4. **Lateral via secrets-in-repo.** Cloned repos contained the AWS
   API key that gave access to npm's production environment. From
   there the attacker queried package metadata and (per GitHub's
   disclosure) **downloaded some private npm package source** before
   GitHub cut off access.
5. **Detection by anomalous AWS API key use.** GitHub detected the
   AWS key in use from an unfamiliar source. Reverse-tracing through
   GitHub audit logs revealed the Heroku/Travis OAuth tokens as the
   common factor across the victim list.

## Lessons for bug hunters

- **Third-party OAuth apps with `repo` scope = transitive trust.**
  Any target whose engineers authorise OAuth apps with broad `repo`
  scope has a delegated trust path through that vendor. Recon-time
  probe: visit `https://github.com/<org>` and check the public
  Integrations / OAuth-app section in `.github/` config; cross-ref
  authorised apps against current advisories. Programs do pay for
  "over-privileged OAuth scope" findings.
- **Audit-log telemetry blindspots are real.** A "normal" OAuth app
  pulling repos at high volume from a residential or VPN IP is the
  exfil signature. Most orgs do not alert on it because the OAuth app
  is whitelisted. When evaluating a target's detection posture, ask:
  do they alert on OAuth-app behaviour anomalies, or only on raw
  password/2FA failures?
- **Refresh tokens with no expiry are landmines.** GitHub user OAuth
  tokens at the time had no built-in expiry. Until rotated, a token
  granted years ago by an ex-employee was still valid. Probe whether
  your target rotates / expires OAuth tokens for departed users and
  for revoked third-party integrations.
- **Secrets in private repos are still secrets.** Private != safe.
  Treat any AWS / GCP / npm / Docker creds checked into git as
  pre-leaked. Search history for `AKIA`, `aws_access_key_id`,
  `.pypirc`, `.npmrc`, even on private repos when access is possible
  through a finding. Same pattern as [[codecov-bash-uploader]].
- **"Initial vector undisclosed" is the canonical incident shape.**
  Plan disclosures and post-mortems will redact the original
  intrusion. Build your model from the *secondary* IOCs (token
  enumeration patterns, repo-listing API calls) -- those are public
  and reusable across future incidents.

## Primary sources

- [GitHub Blog: "Security alert: Attack campaign involving stolen OAuth user tokens issued to two third-party integrators"](https://github.blog/news-insights/company-news/security-alert-stolen-oauth-user-tokens/)
  -- GitHub's official disclosure including the enumeration pattern and npm impact.
- [Cycode: "GitHub OAuth Compromise Affecting Heroku and Travis-CI Users"](https://cycode.com/blog/github-oauth-compromise-affecting-heroku-and-travis-ci-users/)
  -- technical breakdown of the OAuth app trust model and remediation steps.

## Related

- [[circleci-2023-oauth]]
- [[codecov-bash-uploader]]
- [[tj-actions-changed-files]]
