# Vinted Bug Bounty Program

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/vinted/vinted-bugbountyprogram/detail
> Type: BBP | Public | Open
> Bounty: N/A
> Avg payout: N/A | Accepted: 0/556 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-05-11

## Scope

- in:  *.vinted.net                                      # type: wildcard # tier:4
- in:  *.vinted.com                                      # type: wildcard # tier:4
- in:  *.vinted.fr                                       # type: wildcard # tier:4
- in:  *.vintedgo.com                                    # type: wildcard # tier:4
- in:  Vinted: Shop & sell pre-loved                     # type: ios_app # tier:3
- in:  Vinted: Shop & sell pre-loved                     # type: android_app # tier:3
- in:  *sandbox*.vintedgo.com                            # type: wildcard # tier:2
- in:  *sandbox*.vinted.com                              # type: wildcard # tier:2
- in:  Scam                                              # type: other # tier:6
- in:  api.prod.svc.vintedpay.com                        # type: url # tier:5
- in:  callbacks.prod.svc.vintedpay.com                  # type: url # tier:5
- in:  *.homerr.com                                      # type: wildcard # tier:5
- in:  *vintedpay.com                                    # type: wildcard # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
