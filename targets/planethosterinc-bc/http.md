# PlanetHoster Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/planethosterinc
> Type: BBP
> Bounty: P1 $2000–$3000 | P2 $1250–$2250 | P3 $800–$1500 | P4 $200–$1000
> Status: In progress (started Nov 07, 2017)

## Scope

- in:  https://my.planethoster.com   # type: url
- in:  https://api.planethoster.net   # type: url
- in:  https://world.planethoster.net   # type: url
- in:  https://mg.n0c.com/   # type: url
- in:  https://www.planethoster.com   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- disclosure: NOT allowed
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Credentials & Access

- Obtain test account via **Get Credentials** button at bottom of program brief
- Do NOT change your test email address — violation of program compliance
- Account pre-loaded with **€100 credit** for purchase/payment testing
- If more credit needed: open Bugcrowd Support ticket with reason

## API Access (IP Whitelisting Required)

1. Log into https://my.planethoster.com → Domain Reseller API → Account Info page
2. Open support ticket (top-right of page):
   - **Subject:** `Whitelist IP for API testing`
   - **Body:** "I am testing on behalf of the Bugcrowd bug bounty program and am requesting that my IP [YOUR IP] is whitelisted for API testing."
3. Base URLs:
   - Domain API: https://api.planethoster.net/reseller-api/
   - World API: https://api.planethoster.net/world-api/
   - Full API docs: https://apidoc.planethoster.com/en

## World Hosting Panel Access

1. Log in to https://my.planethoster.com
2. Navigate to **My Services** → select **WORLD** under Product/Service
3. Then navigate to https://world.planethoster.net with provided credentials
4. v2 interface: https://my.planethoster.com/v2/hosting-management/overview

## Focus Areas

- Domain Names, DNS Management, Order form
- Access to other users' accounts / information
- Information that should not be available
- User passwords
- World hosting panel

## OOS

- Any DoS/DDoS attacks (production environment)
- Automated testing on Support channels
- Any domain/subdomains of PlanetHoster NOT listed in targets above
