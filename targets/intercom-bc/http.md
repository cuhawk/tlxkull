# Intercom

> Platform: Bugcrowd — https://bugcrowd.com/engagements/intercom
> Type: BBP
> Bounty: See program page
> Status: In progress (started Feb 16, 2017)

## Scope

- in:  https://api.intercom.io https://api.intercom.io API Testing   # type: url
- in:  https://api.intercom.com https://api.intercom.com API Testing   # type: url
- in:  https://app.intercom.com https://app.intercom.com Ruby on Rails Website Testing Ruby   # type: url
- in:  https://app.intercom.io https://app.intercom.io/ Ruby on Rails Website Testing Ruby   # type: url
- in:  https://www.intercom.com https://www.intercom.com/ NextJS ReactJS Website Testing   # type: url
- in:  https://api-iam.intercom.io https://api-iam.intercom.io API Testing Ruby on Rails Ruby   # type: url
- in:  https://*.mobile-messenger.intercom.com https://*.mobile-messenger.intercom.com API Testing Ruby on Rails Ruby   # type: url
- in:  https://app.fin.ai/ https://app.fin.ai/ Ruby on Rails Website Testing Ruby   # type: url

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
- Sign up: https://app.intercom.com/a/start?security_researcher=true
- Use @bugcrowdninja.com email — account will be terminated if you don't; no reward for valid bugs found
- Create 2+ accounts for cross-org testing; max 4 apps total

## Rules
- No automated scans (strictly prohibited)
- No attacks against existing user base
- No DDoS
- PoC DoS at app level accepted; stress/availability-risk PoCs = abuse
- Test Messenger with your OWN account/installation — do not send payloads to real customers
- Nondisclosure — no public disclosure allowed

## Permission / Paywall bypass policy
- Permission bypass within single workspace: P3 (max, only if affects user privacy/PII)
- All other permission bypasses (excl. paywall): P5 Informational
- Paywall bypass (accessing paid features free): NOT accepted
- Shared security model — workspace owner responsible for who they invite

## Focus areas
- OWASP Top 10 for LLMs and Gen AI Apps
- XSS (including CSP-blocked)
- CSRF on critical actions
- RCE / shell injection
- Authentication bypass
- SQLi
- IDOR

## Useful links
- API docs: https://developers.intercom.com/
- Fin AI Agent: https://www.intercom.com/help/en/articles/7120684-fin-ai-agent-explained
- Changelog (new features): https://www.intercom.com/changes/en
- iOS/Android SDK docs: https://docs.intercom.com/install-on-your-product-or-site/quick-install/install-and-configure-intercom-on-your-mobile-app
