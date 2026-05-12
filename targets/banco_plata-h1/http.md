# Banco Plata

> Platform: HackerOne — https://hackerone.com/banco_plata
> Type: BBP | Self-managed | Standard safe harbor
> Bounty: $100 - $5000 | Response efficiency: 98%
> Last scope update: April 27, 2026

## Scope

- in:  id6443932656   # type: ios_app
- in:  dif.tech.plata   # type: android_app
- in:  *.platacard.mx   # type: wildcard
- in:  *.bancoplata.mx   # type: wildcard
- out: https://platacard.mx/*/whistleblowing   # type: wildcard
- out: https://bancoplata.mx/*/whistleblowing   # type: wildcard

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- payout speed: unknown
- Launched: Jan 2026

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
