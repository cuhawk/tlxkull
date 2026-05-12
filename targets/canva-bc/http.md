# Canva

> Platform: Bugcrowd — https://bugcrowd.com/engagements/canva
> Type: BBP
> Bounty: See program page
> Status: In progress (started Jan 31, 2019)

## Scope

- in:  https://www.canva.com   # type: url
- in:  https://www.canva.com/developers/   # type: url
- in:  https://api.canva.com   # type: url
- in:  *.canva.com   # type: wildcard
- in:  *.canva-apps.com   # type: wildcard
- in:  https://*.canva.tech   # type: url
- in:  https://www.canva.com/en_au/help/chatgpt-templates/   # type: url
- in:  https://www.canva.com/integrations/slack/   # type: url
- in:  *.canva.cn   # type: wildcard
- in:  *.canva-apps.cn   # type: wildcard

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

| Target Group | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| Canva Editor | $15,000 | $4,000 | $1,500 | $200 |
| Canva Developer Platform | $15,000 | $4,000 | $1,500 | $200 |
| Canva Services/Infrastructure | $15,000 | $4,000 | $1,500 | $200 |
| Canva China | $15,000 | $4,000 | $1,500 | $200 |
| Canva Marketplace Apps & Integrations | $6,000 | $1,500 | $750 | $200 |
| Canva Native Applications | $6,000 | $1,500 | $750 | $200 |

## Access

- Sign up using @bugcrowdninja.com email ONLY
- Register for Canva for Work 30-day trial for full access
- Use multiple accounts by creating a team

## Notes (Program-Specific)

- Coordinated disclosure — requires explicit permission request on submission
- Partial safe harbor
- Scope 4/4 — very broad
- Average payout $3,200 (as of last session); validation within 7 days
- Mobile apps: iOS, Android, Desktop (macOS/Windows), Chrome Extension
- *.canva.cn network configuration findings NOT eligible for monetary reward
- BigMarker vulnerabilities: report directly to BigMarker (not Canva)
- Leaked customer credentials via OSINT sources = OOS (since May 26, 2025)
- AI jailbreaking, prompt injection, prompt leaks = OOS unless chained to further vuln
