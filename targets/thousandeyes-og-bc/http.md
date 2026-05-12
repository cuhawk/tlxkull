# Cisco ThousandEyes Vulnerability Hunting aka Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/thousandeyes-og
> Type: BBP
> Bounty: P1 $4100–$4500 | P2 $1500–$1750 | P3 $600–$850 | P4 $200–$250
> Status: In progress

## Scope

- in:  https://api.thousandeyes.com/   # type: url
- in:  https://app.thousandeyes.com/   # type: url
- in:  https://www.thousandeyes.com/   # type: url
- out: https://blog.thousandeyes.com/   # type: url
- out: https://app.thousandeyes.com/sfdc/community   # type: url

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

## Additional In-Scope Targets

- in: ThousandEyes Enterprise Agent (Linux) — downloadable agent software; test via Jira instance
- in: ThousandEyes Endpoint Agent (Windows) — endpoint agent for monitoring

## Credentials

Account creation required: sign up at https://app.thousandeyes.com/register/ with @bugcrowdninja.com email
Use "Bugcrowd" for First, Last, and Company name fields.
Account activated within 1 business day.
Credentials may need to be requested through program — check Bugcrowd credentials tab.

## Required Header

Append "Bugcrowd-<BugcrowdUsername>" to User-Agent for ALL HTTP/HTTPS traffic before testing.

## Notes

- No automated scans (incl. brute-force enumeration); Turbo Intruder limited to 15 requests for unique tests only
- No DoS testing; report vectors to USSR@thousandeyes.com
- Do NOT test support subdomain, chat, community (sfdc/community), or open support tickets
- Manually crafted agent traffic NOT valid — only test via ThousandEyes web application test settings
- Edited binaries NOT valid findings
- Do NOT register agents into other accounts
- Cross-account access (IDOR) is top priority focus area
- Leaked 3rd-party credentials = OOS (as of Oct 2024)
- Program was paused; un-paused Jan 16, 2026 — review brief before testing
- Coordinated disclosure (explicit permission required)
- Program previously private but now public
- Cisco products: report to psirt@cisco.com; Cisco operational infra: https://bugcrowd.com/ciscosecurity
