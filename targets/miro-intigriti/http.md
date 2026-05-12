# Miro

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/miro/miro/detail
> Type: BBP | Public | Suspended
> Bounty: Low €250 | Medium €500 | High €1,500 | Critical €3,000 | Exceptional €3,250 (Tier 1); Low €100 | Medium €300 | High €900 | Critical €1,500 | Exceptional €1,750 (Tier 2)
> Avg payout: €661 | Total paid: €70,700
> Response: avg first response < 5 days | avg to decide < 2 weeks
> Last scope update: unknown

## Scope

- in:  https://miro.com/   # type: url | tier: Tier 1
- in:  https://miro.com/app   # type: url | tier: Tier 1
- in:  mcp.miro.com   # type: url | tier: Tier 1
- in:  static-website.miro.com   # type: url | tier: Tier 1
- in:  mirostatic.com   # type: url | tier: Tier 1
- in:  https://mirosite.com/   # type: url | tier: Tier 1
- in:  https://api.miro.com/*   # type: wildcard | tier: Tier 1
- in:  Miro SDK   # type: other | tier: Tier 1
- in:  https://miro.com/insights/app   # type: url | tier: Tier 1
- in:  https://miro.com/blog/   # type: url | tier: Tier 1
- in:  eu01.miro.com   # type: other | tier: Tier 1
- in:  us01.miro.com   # type: other | tier: Tier 1
- in:  au01.miro.com   # type: other | tier: Tier 1
- in:  svc.eu01.miro.com   # type: other | tier: Tier 1
- in:  svc.us01.miro.com   # type: other | tier: Tier 1
- in:  svc.au01.miro.com   # type: other | tier: Tier 1
- in:  svg-convert.eu01.miro.com   # type: other | tier: Tier 1
- in:  svg-convert.us01.miro.com   # type: other | tier: Tier 1
- in:  svg-convert.au01.miro.com   # type: other | tier: Tier 1
- in:  r.eu01.miro.com, r01.eu01.miro.com, r02.eu01.miro.com   # type: other | tier: Tier 1
- in:  r.us01.miro.com, r01.us01.miro.com, r02.us01.miro.com   # type: other | tier: Tier 1
- in:  r.au01.miro.com, r01.a01.miro.com, r02.au01.miro.com   # type: other | tier: Tier 1
- in:  eventhub.eu01.miro.com   # type: other | tier: Tier 1
- in:  eventhub.us01.miro.com   # type: other | tier: Tier 1
- in:  eventhub.au01.miro.com   # type: other | tier: Tier 1
- in:  integrations.eu01.miro.com   # type: other | tier: Tier 1
- in:  integrations.us01.miro.com   # type: other | tier: Tier 1
- in:  integrations.au01.miro.com   # type: other | tier: Tier 1
- in:  iOS app (id 1180074773)   # type: ios_app | tier: Tier 1
- in:  Android app (com.realtimeboard)   # type: android_app | tier: Tier 1
- in:  MacOS Desktop Application   # type: macos_app | tier: Tier 1
- in:  Windows Desktop Application   # type: other | tier: Tier 1
- in:  Confluence Cloud Plugin for Miro   # type: other | tier: Tier 2
- in:  Jira Cards for Miro   # type: other | tier: Tier 2
- in:  Jira Cloud Plugin for Miro   # type: other | tier: Tier 2
- out: miro.com/contact/*   # type: wildcard
- out: MarketPlace Submission Process   # type: other
- out: Feedback forms   # type: other
- out: https://community.miro.com/   # type: url
- out: https://developers.miro.com/   # type: url
- out: https://help.miro.com/*   # type: wildcard
- out: https://status.miro.com   # type: url
- out: miro.com/careers/vacancy/*   # type: wildcard
- out: trcksplt.miro.com   # type: other
- out: https://uizard.io/   # type: url
- out: https://support.uizard.io/   # type: url

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN
- note: self-register with @intigriti.me; User-Agent: BugBounty - <username> - Mozilla/5.0...; X-Bugbounty: <username> header required

## Notes

- payout speed: avg to decide < 2 weeks; CURRENTLY SUSPENDED (expected to reopen)
- visual collaboration platform (whiteboard SaaS)
- custom User-Agent AND X-Bugbounty request header required
- no video-only PoCs accepted
- payment testing: limit seats to minimum, cancel subscriptions same day
- board enumeration is out of scope
- bypassing premium features is out of scope
- credentials leaks: report only, no further action, no reward unless chained
- focus: authorization issues, file upload vulns, RCE, auth bypass, account takeover

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
