# CoinDesk Data - Data API

> Platform: Bugcrowd — https://bugcrowd.com/engagements/CCData-mbb-og
> Type: BBP
> Bounty: See program page
> Status: In progress (started May 13, 2025)

## Scope

- # TODO: scope not loaded — re-scrape with scroll

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Targets

### In Scope (P1=$3,500–7,500)
- in: http://data-api.coindesk.com/ (Digital Asset Data REST API)
- in: https://tools-api.cryptocompare.com/ (Tools API)

### Out of scope
- out: https://www.coindesk.com/
- out: https://uat.coindesk.com/
- out: https://events.coindesk.com
- out: https://consensus2025.coindesk.com/
- out: https://consensus-hongkong2025.coindesk.com/
- out: https://data.coindesk.com/
- out: https://developers.coindesk.com
- out: All other sub-domains/APIs not listed above

## Auth
- Register at https://www.cryptocompare.com/ with @bugcrowdninja.com email
- Create API key (required for most functionality)

## Rewards
| Priority | Range |
|----------|-------|
| P1 | $3,500–7,500 |
| P2 | $1,500–3,500 |
| P3 | $500–1,500 |
| P4 | $250–500 |

CVSS: P1=10.0-9.0, P2=8.9-7.0, P3=6.9-4.0, P4=<=3.9 Low, P5=<=3.9 Info

## Focus areas
- Unauthorized access to admin/back-end functionality
- Vertical privilege escalation or access to user data
- Focus testing on the APIs themselves only

## OOS
- DoS testing
- Any APIs not at data-api.coindesk.com
- URL redirections
- Coin scams (no ability to intervene)

## Notes
- Report non-listed CCData assets to: security.incident@bullish.com (no reward)
- Disclosure: Coordinated (explicit permission required)
