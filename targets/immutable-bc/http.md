# Immutable Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/immutable
> Type: BBP
> Bounty: P1 $15000–$25000 | P2 $5000–$15000 | P3 $450–$600 | P4 $50–$200
> Status: In progress (started Feb 22, 2022)

## Scope

- in:  *.immutable.com   # type: wildcard
- in:  https://auth.immutable.com/   # type: url
- in:  https://passport.immutable.com/   # type: url
- in:  https://hub.immutable.com/   # type: url
- in:  https://api.immutable.com/   # type: url
- in:  https://api.x.immutable.com/   # type: url
- in:  https://link.x.immutable.com/   # type: url
- in:  https://market.immutable.com/   # type: url
- in:  https://docs.immutable.com/   # type: url
- in:  *.testnet.immutable.com   # type: wildcard
- in:  testnet.immutable.com   # type: domain
- in:  *.imtbl.com   # type: wildcard
- in:  imx.community   # type: domain
- out: guildofguardians.com   # type: domain
- out: *.guildofguardians.com   # type: wildcard
- out: *.godsunchained.com   # type: wildcard
- out: *.gogbackend.com   # type: wildcard
- out: gogbackend.com   # type: domain
- out: godsunchained.com   # type: domain
- out: mineloader.com   # type: domain
- out: *.mineloader.com   # type: wildcard

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- validation within: 7 days
- avg payout: $512 (last 3 months)
- vulns rewarded: 64
- safe harbor: yes
- industry: Computer Software
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
