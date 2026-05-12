# Monzo Public Bug Bounty Program

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/monzobank/monzopublicbugbountyprogram/detail
> Type: BBP | Public | Open
> Bounty: N/A
> Avg payout: £490 | Accepted: 0/578 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-05-08

## Scope

- in:  *.monzo.com                                       # type: wildcard # tier:4
- in:  *.prod-ffs.io                                     # type: wildcard # tier:4
- in:  1052238659                                        # type: ios_app # tier:3
- in:  co.uk.getmondo                                    # type: android_app # tier:3
- in:  www.monzo.com                                     # type: url # tier:2
- in:  monzo.com                                         # type: url # tier:2
- in:  */p2p/*                                           # type: wildcard # tier:5
- in:  */contact-discovery/*                             # type: wildcard # tier:5
- in:  */inbound-p2p/*                                   # type: wildcard # tier:5
- in:  *.monzo.me                                        # type: wildcard # tier:5
- in:  community.monzo.com                               # type: url # tier:5
- in:  login.internal.monzo.com                          # type: url # tier:5
- in:  monzo.me                                          # type: url # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
