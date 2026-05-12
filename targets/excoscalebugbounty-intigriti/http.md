# Exoscale Bug Bounty

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/exoscale/excoscalebugbounty/detail
> Type: BBP | Public | Open
> Bounty: N/A
> Avg payout: N/A | Accepted: 0/0 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-05-06

## Scope

- in:  https://portal.exoscale.com/                      # type: url # tier:3
- in:  https://sos-*.exo.io                              # type: wildcard # tier:3
- in:  https://sks-*.exo.io                              # type: wildcard # tier:3
- in:  *.internal.exoscale.ch                            # type: wildcard # tier:3
- in:  https://www.exoscale.com/                         # type: url # tier:2
- in:  https://community.exoscale.com/                   # type: url # tier:2
- in:  https://changelog.exoscale.com/                   # type: url # tier:5
- in:  https://exoscalestatus.com/                       # type: url # tier:5
- in:  https://academy.exoscale.com/                     # type: url # tier:5
- in:  https://jobs.exoscale.com/                        # type: url # tier:5
- in:  CDN service                                       # type: other # tier:5
- in:  Marketplace products                              # type: other # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
