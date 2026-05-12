# Lansweeper Bug Bounty Program

> Platform: Intigriti — https://app.intigriti.com/researcher/programs/lansweeper/lansweeper1/detail
> Type: BBP | Public | Open
> Bounty: N/A
> Avg payout: €269 | Accepted: 254/920 submissions | Total paid: N/A
> Response: N/A
> Last scope update: 2026-04-21

## Scope

- in:  Lansweeper Discovery                              # type: url # tier:3
- in:  app.lansweeper.com                                # type: url # tier:3
- in:  fb.lansweeper.com                                 # type: url # tier:3
- in:  edge.lansweeper.com                               # type: url # tier:4
- in:  api.lansweeper.com                                # type: url # tier:3
- in:  backoffice.lansweeper.com                         # type: url # tier:3
- in:  https://lsagentrelay.lansweeper.com/              # type: url # tier:3
- in:  app.lansweeper.com/trial                          # type: url # tier:2
- in:  autoupdateapi.lansweeper.com                      # type: url # tier:2
- in:  docs.lansweeper.com                               # type: url # tier:2
- in:  login.lansweeper.com                              # type: url # tier:2
- in:  on-premises software                              # type: url # tier:2
- in:  www.lansweeper.com                                # type: url # tier:2
- in:  *.lansweeper.com                                  # type: wildcard # tier:1
- in:   lsrunase2.0 and lsencrypt2.0                     # type: other # tier:5
- in:  careers.lansweeper.com                            # type: url # tier:5
- in:  www.lansweeper.com/forum                          # type: url # tier:5

## Auth

- type: session
- creds: env:INTIGRITI_SESSION_TOKEN

## Notes

- payout speed: N/A

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
