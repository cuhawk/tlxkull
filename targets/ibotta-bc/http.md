# ibotta

> Platform: Bugcrowd — https://bugcrowd.com/engagements/ibotta
> Type: BBP
> Bounty: P1 $1000 | P2 $750 | P3 $500 | P4 $250
> Status: In progress (rewards reduced Apr 10, 2026)

## Scope

- in: https://ibotta.com   # All ibotta domains in scope
- in: https://app.ibotta.com/sign-in
- in: https://chrome.google.com/webstore/detail/ibotta-browser-extension/mfaedmjlefifhnhpgipjjiiekchaimpk   # Chrome extension (out of beta)
- out: https://investors.ibotta.com   # hosted by third party
- out: https://ir.ibotta.com   # hosted by third party
- out: https://trust.ibotta.com   # hosted by third party

## Notes

- Cash-back rewards platform (US only; test via US IP)
- All Ibotta-owned domains are in scope
- Chrome extension recently moved out of beta — high interest target
- Web v2 target: access token exposure / scraping / 3rd party data flow = informational unless chained
- Focus: grocery retailer credential sniffing, cashout manipulation, 2FA bypass, injection
- Geo: US only; international researchers must use US proxy/VPN
- Caching issues known, bounties already paid (Feb 2025 announcement)
- N-day policy: 7 day grace period after public disclosure

## Auth

- type: self-registered
- note: Register with @bugcrowdninja.com email; need grocery store rewards account (not provisioned)
