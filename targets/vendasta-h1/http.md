# Vendasta

> Platform: HackerOne — https://hackerone.com/vendasta
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 65% | Avg first response: N/A | Total paid: N/A
> Last scope update: 2023-03-01

## Scope

- in:  *.apigateway.co    # type: wildcard # max: critical # not eligible for bounty
- in:  *.vendasta-internal.com    # type: wildcard # max: critical # not eligible for bounty
- in:  *.yesware.com    # type: wildcard # max: critical # not eligible for bounty
- in:  customervoice.biz    # type: url # max: critical # not eligible for bounty
- in:  your-domain.socialsmbs.com    # type: url # max: critical # not eligible for bounty
- in:  your-domain.steprep.com    # type: url # max: critical # not eligible for bounty
- in:  your-domain.smblogin.com    # type: url # max: critical # not eligible for bounty
- in:  your-domain.pdqs.mobi    # type: url # max: critical # not eligible for bounty
- in:  your-domain.snapshotreport.biz    # type: url # max: critical # not eligible for bounty
- in:  task-manager.biz    # type: url # max: critical # not eligible for bounty
- in:  partners.vendasta.com    # type: url # max: critical # not eligible for bounty
- in:  *.vendasta.com    # type: wildcard # max: critical # not eligible for bounty
- out:  www.yesware.com    # type: url # max: none
- out:  help.yesware.com    # type: url # max: none
- out:  roadmap.vendasta.com    # type: url # max: none
- out:  www.vendasta.com    # type: url # max: none
- out:  t.yesware.com    # type: url # max: none
- out:  Spamming of forms and APIs with automated vulnerability scanners are strictly out of scope    # type: other # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
