# DocuSign

> Platform: HackerOne — https://hackerone.com/docusign
> Type: VDP
> Bounty: N/A (VDP)
> Avg bounty: N/A
> Response efficiency: 70% | Avg first response: N/A | Total paid: N/A
> Last scope update: N/A

## Scope

- in:  All Docusign apps and assets not listed below as Out of Scope    # type: other # max: critical # not eligible for bounty
- out:  https://*.account.docusign.com/    # type: wildcard # max: none
- out:  https://www.docusign.net/restapi/*    # type: wildcard # max: none
- out:  https://www.docusign.net/api/3.0/*    # type: wildcard # max: none
- out:  https://www.rooms.docusign.com/*    # type: wildcard # max: none
- out:  https://app.docusign.com/    # type: url # max: none
- out:  https://www.docusign.net/signing/    # type: url # max: none
- out:  https://admin.docusign.com    # type: url # max: none
- out:  https://partners.docusign.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- triaged by HackerOne: yes

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
