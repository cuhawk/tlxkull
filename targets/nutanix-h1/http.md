# Nutanix

> Platform: HackerOne — https://hackerone.com/nutanix
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 90% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-03-21

## Scope

- in:  *.nutanix.com    # type: wildcard # max: critical # not eligible for bounty
- in:  support.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  ticket.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  my.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  jira.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  install.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  bootcamp.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  productsizer.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  gp.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  stage-billing.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  idp.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  cpq.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  iot.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  beam.nutanix.com    # type: url # max: critical # not eligible for bounty
- in:  www.nutanix.dev    # type: url # max: high # not eligible for bounty
- in:  testdrive.nutanix.com    # type: url # max: high # not eligible for bounty
- out:  webex.nutanix.com    # type: url # max: none
- out:  events.nutanix.com    # type: url # max: none
- out:  next.nutanix.com    # type: url # max: none
- out:  mops.nutanix.com    # type: url # max: none
- out:  frame.nutanix.com    # type: url # max: none
- out:  karbon.nutanix.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
