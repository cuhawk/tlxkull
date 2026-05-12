# Elementor: Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/elementor
> Type: BBP
> Bounty: See program page
> Status: In progress (started Dec 17, 2020)

## Scope

- in:  https://my.elementor.com/ Wordpress MySQL jQuery   # type: url
- in:  https://go.elementor.com/ Wordpress MySQL jQuery   # type: url
- in:  https://translate.elementor.com/ Wordpress MySQL PHP   # type: url
- in:  https://developers.elementor.com/ Wordpress MySQL jQuery   # type: url
- in:  https://library.elementor.com/ Wordpress MySQL jQuery   # type: url
- in:  https://elementor.careers Wordpress MySQL jQuery   # type: url
- in:  https://activitylog.io/ Wordpress MySQL jQuery   # type: url
- in:  https://send2.co/ Wordpress MySQL jQuery   # type: url

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

## Auth
- Sign up at https://my.elementor.com/signup/ with @bugcrowdninja.com email
- Free one-week Elementor Pro license: https://my.elementor.com/store/checkout?add-plans=WyJFTEVNRU5UT1ItQ0xPVUQtQlVHQk9VTlRZLVRSWS0wMSJd (requires @bugcrowdninja.com email)

## Plugin vulnerabilities → Patchstack (NOT this program)
Elementor, Elementor Pro, Ally, Image Optimizer, Activity Log, Temporary Login, Site Mailer, Elementor Blocks for Gutenberg, Hello Elementor, Hello Biz, Hello Plus

## Rules
- Nondisclosure — no public disclosure allowed
- WAF active — no mass scanning; max 25 req/sec; if blocked, stop for 24hrs
- Only test your own accounts; do not access other users' data
- Out-of-scope submissions with good reasoning + demonstrable impact may be accepted (case-by-case)

## Rewards
| Priority | Range |
|----------|-------|
| P1 (extraordinary — full system compromise) | Up to $5,000 |
| P1 | $2,000–4,000 |
| P2 | $500–2,000 |
| P3 | $0–500 |
| P4 | Points only |

## Out of scope
- *.elementor.cloud (other users' sites — your own cloud site is in scope)
- Contact / support forms
- SSL-related attacks, insecure cipher suites
- Weak/bypass CAPTCHA
- Username / email enumeration
- Brute force on login/forgot password
- Account lockout
- HTTP security headers, cookies issues
- Weak password policies
- CSRF on anonymous forms (login, contact)
- Clickjacking
- Mail server domain misconfigs (DMARC, SPF, DKIM)
- Old/EOL platforms, browsers, plugins
