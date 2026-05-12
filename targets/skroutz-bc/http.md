# Skroutz Public Managed Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/skroutz
> Type: BBP
> Bounty: P1 $4100–$4500 | P2 $1500–$1750 | P3 $600–$850 | P4 $100–$250
> Status: In progress

## Scope

- in:  https://www.skroutz.gr   # type: url

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

## Additional Domain Flavors (same backend — single target)

- skroutz.gr (main, Greek)
- skroutz.de
- skroutz.bg
- skroutz.ro (includes Romanian Leu multi-currency — historical bonus focus)
- skroutz.cy
- skroutz.eu

## Credentials

Self-registration through normal registration flow. No provided credentials.
Keep account creations minimal. Do not share credentials.
No test payment methods — DO NOT complete purchases with real cards.
API OAuth2: No client_id/client_secret provided — test from unauthenticated perspective.
API docs: https://developer.skroutz.gr/api/v3/

## Focus Areas

- Authentication incl. OAuth2 logins
- API endpoints (unauthenticated perspective)
- Checkout/payment workflow (steps involving credit card details WITHOUT completing payment)
- Smart Basket / "Purchase from Skroutz" functionality
- 2FA mechanism (implemented only on specific endpoints — NOT on login; enabled on email change)

## OOS

- AI chatbot agent
- DoS/DDoS
- CSRF (aware of all relevant issues)
- HTTP security headers (without demonstrable impact)
- Cookie flags (without demonstrable impact)
- SSL/TLS
- Password policy / session expiration
- Self-XSS / Clickjacking
- Account lockout / rate limiting absence
- Email/username enumeration
- Leaked credentials from other sites
- Legacy browser-only vulns
- Out-of-date libraries (unless exploitable)

## Notes

- Live production environment — be non-destructive
- Do NOT target other users' data; use multiple test accounts
- Contact team immediately if real customer data is detected
- No IP/port scanning, no attacking load balancers directly
- Automated tools: pace reasonably; do not mass-create DB entries
- Coordinated disclosure
- Safe harbor: full
