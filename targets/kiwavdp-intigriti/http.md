# Kiwa Vulnerability Disclosure Program

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/kiwa/kiwavdp/detail
> Type: VDP | Public | Open
> Bounty: N/A
> Avg payout: N/A | Accepted: 16/109 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-04-23

## Scope

- in:  *.kiwa.com                                        # type: wildcard # tier:1
- in:  *.kiwaimpact.com                                  # type: wildcard # tier:1
- in:  *.kiwa.info                                       # type: wildcard # tier:1
- in:  *.kiwa.nl                                         # type: wildcard # tier:1
- in:  *.kiwa.se                                         # type: wildcard # tier:1
- in:  *.kiwa.no                                         # type: wildcard # tier:1
- in:  https://careers.kiwa.com/                         # type: url # tier:5
- in:  https://qr.kiwa.com/                              # type: url # tier:5
- in:  https://www.kiwa.com/en/contact/                  # type: url # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
