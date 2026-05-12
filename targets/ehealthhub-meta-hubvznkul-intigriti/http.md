# eHealth Hub VZN KUL

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/uz leuven/ehealthhub&meta-hubvznkul/detail
> Type: BBP | Public | Open
> Bounty: N/A
> Avg payout: N/A | Accepted: 0/0 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-05-03

## Scope

- in:  hub.vznkul.be/*                                   # type: wildcard # tier:3
- in:  hub.vznkul.be/services/interhub/InterHubServi     # type: url # tier:3
- in:  hub.vznkul.be/services/intrahub/IntraHubServi     # type: url # tier:3
- in:  hubacc.vznkul.be/*                                # type: wildcard # tier:3
- in:  hubacc.vznkul.be/services/acceptance/interhub     # type: url # tier:3
- in:  hubacc.vznkul.be/services/acceptance/intrahub     # type: url # tier:3
- in:  www.vznkul.be                                     # type: url # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
