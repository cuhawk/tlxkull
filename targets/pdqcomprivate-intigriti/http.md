# PDQ bug bounty program

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/pdq/pdqcomprivate/detail
> Type: BBP | Public | Open
> Bounty: N/A
> Avg payout: €478 | Accepted: 99/455 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-01-25

## Scope

- in:  https://app.pdq.com/                              # type: url # tier:2
- in:  https://portal.pdq.com/                           # type: url # tier:2
- in:  https://a.simplemdm.com/                          # type: url # tier:3
- in:  https://auth2.pdq.com/                            # type: url # tier:3
- in:  https://library.pdq.com/                          # type: url # tier:3
- in:  https://*.pdq.com/                                # type: wildcard # tier:5
- in:  https://*.pdq.tools/                              # type: wildcard # tier:5
- in:  https://*.simplemdm.com/                          # type: wildcard # tier:5
- in:  https://*.smartdeploy.com/                        # type: wildcard # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
