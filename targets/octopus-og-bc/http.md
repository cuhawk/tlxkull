# Octopus Bug Bounty Program

> Platform: Bugcrowd — https://bugcrowd.com/engagements/octopus-og
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://octopus.com website ReactJS   # type: url
- in:  *.octopus.app website cloud   # type: wildcard
- out: https://aiagent.octopus.com/ website   # type: url
- out: https://trust.octopus.com website   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Notes (appended)

- status: ACTIVE (since May 2019)
- Use @bugcrowdninja.com email; other emails treated as malicious/blocked
- Register at: https://octopus.com/register?registerReturnUrl=%2Fsignin
- Leaked API keys only valid if domain URL references *.octopus.app
- API keys with localhost/test in name are invalid
- WAF bypasses are OOS (since Mar 2022, until further notice)
- Self-hosted Octopus Deploy product is OOS
- Cloud-hosted Octopus Deploy product is OOS
- Subdomain takeover is OOS
- trust.octopus.com is OOS (since Sep 2024)
- aiagent.octopus.com removed from scope (Sep 2024)
- Session cookies on account.octopus.com valid up to 10min after logout — don't report session fixation unless ATO after 10min
- Pivoting between test.octopus.com and test-account.octopus.com is fine
- i.octopus.com files are intended to be public (tax docs, W8-BEN-E, etc.)
- No automated scanners
