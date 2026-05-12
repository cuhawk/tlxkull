# Majid Al Futtaim Loyalty Program (Share Rewards)

> Platform: Bugcrowd — https://bugcrowd.com/engagements/majidalfuttaim-loyalty
> Type: BBP
> Bounty: See program page
> Status: In progress (started Jul 16, 2019)

## Scope

- in:  https://www.sharerewards.com/   # type: url
- in:  https://apps.apple.com/us/app/share-rewards/id1465450657   # type: ios_app
- in:  https://play.google.com/store/apps/details?id=com.maf.share&hl=en_US&gl=US   # type: android_app
- in:  https://www.vtcprodapi.maf.ae/svc/svcHifi.svc/SaveOCRReceipt   # type: url
- in:  https://production.maf.auth0.com/api/v2/   # type: url
- in:  https://production.maf.auth0.com   # type: url
- in:  https://maf-holding-prod.apigee.net   # type: url

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL

## Notes

- safe harbor: yes
- disclosure: NOT allowed
- status: ACTIVE

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []

## Bounty

- P1: $2,100–$2,500 | P2: $1,200–$1,500 | P3: $150–$749
- Valid P4 reports upgraded to P3: $150–$200
- Average payout: $1,137.50

## Credentials

- Self-signup using @bugcrowdninja.com email
- Shared test accounts (shared with all researchers — do NOT change password):
  - Email: mafproperties.synack4@gmail.com / Password: Securiestest1
  - Email: mafproperties.synack5@gmail.com / Password: Securiestest1
  - Both have reward points and a test credit card linked

## Notes

- safe harbor: yes
- Nondisclosure
- Production environment testing
- P4 upgraded to P3 ($150–$200)
- Auth issues on identity.majidalfuttaim.com → report to MPASS program instead
- Zero-days: allow 15 business days for patch before submission

## Focus Areas

- Payment using rewards without deduction (payment cycle abuse)
- Fraudulent addition/earning of reward points
- Transfer rewards from other user accounts (family functionality abuse)
- Remote access to PCI data (credit card, CVV)
- Remote access to user PII (name, contact, password)
- Auth data in cleartext (keys, passwords)
- PCI/PII exfiltration, remote DB access, RCE
- Defacement, fraudulent promo code use
