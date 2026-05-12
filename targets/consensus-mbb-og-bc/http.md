# Consensus by CoinDesk

> Platform: Bugcrowd — https://bugcrowd.com/engagements/consensus-mbb-og
> Type: BBP
> Bounty: See program page
> Status: In progress

## Scope

- in:  https://consensus2026.sandbox.events.coindesk.com/ ReactJS NodeJS website   # type: url
- out: https://uat.coindesk.com/ nginx ReactJS   # type: url
- out: https://events.coindesk.com website   # type: url
- out: https://uat.accounts.coindesk.com website   # type: url
- out: https://consensus-hongkong2025.coindesk.com/ website   # type: url
- out: https://consensus2023.coindesk.com/ website   # type: url
- out: https://consensus2024.coindesk.com/ website   # type: url
- out: https://consensus2025.coindesk.com/ website   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Notes (appended)

- status: ACTIVE (public since Feb 2025)
- Sandbox only — live coindesk.com and production event sites are OOS
- Use @bugcrowdninja.com email to create account
- Test promo codes: sandbox-test (100% off), PortalTestCode25 (25% off)
- Test CC: 4111 1111 1111 1111 exp:06/26 cid:123 (payment processing is OOS)
- Crypto payment testing OOS — no compensation for losses
- IDORs temporarily OOS (since Nov 2024)
- Focus: subdomain takeovers, unauthorized admin access, content modification
- CoinDesk Auth (*.auth.coindesk.com) covered by separate CoinDesk.com BBP
