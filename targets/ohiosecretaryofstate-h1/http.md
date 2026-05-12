# Ohio Secretary of State

> Platform: HackerOne — https://hackerone.com/ohiosecretaryofstate
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 100% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-02-10

## Scope

- in:  *.boe.ohio.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.militaryvotes.ohio.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ohiobusinesscentral.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ohiosecretaryofstate.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.ohiosos.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.safeathomeohio.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.sos.state.oh.us    # type: wildcard # max: critical # not eligible for bounty
- in:  *.vote.ohio.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.voteohio.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  *.electionintegrity.ohio.gov    # type: wildcard # max: critical # not eligible for bounty
- in:  boe.ohio.gov    # type: url # max: critical # not eligible for bounty

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
