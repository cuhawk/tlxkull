# Rivian Bug Bounty

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/rivian/rivianbugbounty/detail
> Type: BBP | Public | Open
> Bounty: N/A
> Avg payout: $628 | Accepted: 89/457 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-03-16

## Scope

- in:  https://business.rivian.com/api                   # type: url # tier:4
- in:  https://rivian.com/api/gql/content/graphql        # type: url # tier:4
- in:  https://rivian.com/api/gql/gateway/graphql        # type: url # tier:4
- in:  https://rivian.com/api/gql/orders/graphql         # type: url # tier:4
- in:   *.rivian.com                                     # type: wildcard # tier:3
- in:  1570215232                                        # type: ios_app # tier:3
- in:  basecamp.rivian.com                               # type: url # tier:3
- in:  com.rivian.android.consumer                       # type: android_app # tier:3
- in:  rivian.com                                        # type: url # tier:3
- in:  assets.rivian.com                                 # type: url # tier:5
- in:  careers.rivian.com                                # type: url # tier:5
- in:  demovehicles.rivian.com                           # type: url # tier:5
- in:  feedback.rivian.com                               # type: url # tier:5
- in:  internalshop.rivian.com                           # type: url # tier:5
- in:  media.rivian.com                                  # type: url # tier:5
- in:  stories.rivian.com                                # type: url # tier:5
- in:  view.e.rivian.com                                 # type: url # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
