# Files.com

> Platform: HackerOne — https://hackerone.com/files
> Type: BBP
> Bounty: Low $250 | Medium $750 | High $2,000 | Critical $10,000
> Avg bounty: $200–$250
> Response efficiency: 57% | Avg first response: N/A | Total paid: $180,399
> Last scope update: 2025-04-08

## Scope

- in:  app.files.com    # type: url # max: critical
- in:  your-assigned-subdomain.files.com    # type: url # max: critical
- in:  www.files.com    # type: url # max: critical
- in:  FIles.com REST API    # type: other # max: critical
- in:  Files.com SDK's    # type: other # max: critical
- in:  Files.com Mobile App    # type: other # max: critical
- in:  Files.com Command Line Interface (CLI) App    # type: downloadable_executables # max: critical
- in:  Files.com Desktop v4 App (previously known as Desktop App)     # type: downloadable_executables # max: critical
- in:  Files.com Desktop v6 App    # type: downloadable_executables # max: critical
- in:  Files.com On-Premise Agent    # type: downloadable_executables # max: critical
- in:  Rest API    # type: other # max: critical
- in:  Files.com Desktop Application for Windows or Mac    # type: downloadable_executables # max: critical
- out:  developers.files.com    # type: url # max: none
- out:  status.files.com    # type: url # max: none
- out:  mail.files.com    # type: url # max: none

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- total bounties paid: $180,399

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
