# Indeed

> Platform: Bugcrowd — https://bugcrowd.com/engagements/indeed
> Type: BBP
> Bounty: See program page
> Status: In progress (started Jan 26, 2015)

## Scope

- in:  https://indeed.com   # type: url
- in:  https://*.indeedflex.com   # type: url
- in:  https://apis.indeed.com/graphql   # type: url
- in:  https://play.google.com/store/apps/details?id=com.indeed.android.jobsearch   # type: android_app
- in:  https://apps.apple.com/us/app/indeed-job-search/id309735670   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.syftapp.android   # type: android_app
- in:  https://apps.apple.com/gb/app/indeed-flex-job-search/id1013812731   # type: ios_app
- in:  https://*.indeed.tech   # type: url
- in:  https://*.indeed.net   # type: url
- in:  https://resume.com   # type: url
- in:  https://wowjobs.ca   # type: url
- in:  https://apps.apple.com/us/app/%E5%B1%A5%E6%AD%B4%E6%9B%B8%E4%BD%9C%E6%88%90-%E3%82%A4%E3%83%B3%E3%83%87%E3%82%A3%E3%83%BC%E3%83%89/id1484451230   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.indeed.resume   # type: android_app
- in:  https://apps.apple.com/us/app/indeed-connect-for-employers/id6443822731   # type: ios_app
- in:  https://chromewebstore.google.com/detail/indeed-recruiter-extensio/kiodpphbmnmcmnfgpnmkkhmkllnlflef   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- disclosure: standard Bugcrowd terms
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Bounty Tiers

| Tier | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| Primary Targets | $4,000–$10,000 | $1,000–$4,000 | $200–$1,000 | $50–$200 |
| Secondary Targets | $4,000–$10,000 | $1,000–$4,000 | $200–$1,000 | — |
| Other Targets | $0–$1,000 | $0–$400 | $0–$200 | — |

## Auth / Testing Requirements

- Accounts must use @bugcrowdninja.com email only
- Include "bugbounty" in company title, all text fields, AND user-agent string
- Career Scout access: claim account from Credentials bucket → install TestFlight → https://testflight.apple.com/join/veieI9UZ

## Notes

- safe harbor: yes
- disclosure: coordinated (explicit request required)
- 2,096 vulns rewarded; validation within 7 days; average payout $828
- Scope 4/4
- Localized domains (mx.indeed.com, ca.indeed.com, etc.) share same codebase — same vuln = one reward
- Combine similar vulns found across multiple locations into single submission

## Focus Areas

- Career Scout: prompt injection, insecure output handling, auth/authz issues
- secure.indeed.com: auth bypass, OAuth flaws
- apis.indeed.com/graphql: priv esc, sensitive data exposure
- account.indeed.com: broken access control, priv esc
- billing.indeed.com: sensitive data exposure
- employers.indeed.com: priv esc

## OOS Vuln Types

- AI safety (getting chatbot to say bad things)
- Sandboxed code execution in AI apps
- Multi-turn AI attacks not reproducible
- AI volumetric DoS
- Self-XSS, clickjacking on non-sensitive pages
- User enumeration, rate-limiting (unless integrity impact)
- External SSRF, internal SSRF without PoC
- SPF/DMARC/DKIM missing
