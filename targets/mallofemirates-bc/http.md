# Majid Al Futtaim Properties (Mall of Emirates)

> Platform: Bugcrowd — https://bugcrowd.com/engagements/mallofemirates
> Type: Bug Bounty
> Bounty: P1 $2100–$2500 (max $2600) | P2 $1200–$1500 | P3 $150–$750 | P4 upgraded to P3 ($150–$200)
> Status: ACTIVE (public)

## Scope

# Mall of Emirates group (target table loading — targets known from announcements)
- in:  https://play.google.com/store/apps/details?id=com.belongi.moe   # type: android_app  # Mall of the Emirates Android
- in:  https://apps.apple.com/app/mall-of-the-emirates-moe/id1449578693   # type: ios_app  # Mall of the Emirates iOS
- in:  https://api.mafshoppingmalls.com/   # type: url  # Mall of the Emirates API Gateway
- in:  https://www.premogiftcards.com/   # type: url  # mentioned in credentials/testing section

## Out of scope

- out:  https://identity.majidalfuttaim.com/   # auth issues → report to MPASS program instead

## Auth

- type: session
- creds: @bugcrowdninja.com registration
- notes: Self-provision at https://www.premogiftcards.com/ with @bugcrowdninja.com email

## Notes

- safe harbor: yes
- status: ACTIVE
- Focus: PCI/credit card data access, PII exfiltration, DB access, voucher/promo abuse, RCE, defacement
- OOS: DMARC findings, credential leaks (reported but no reward), no data modification
- 15 business days grace period for zero-day patches
