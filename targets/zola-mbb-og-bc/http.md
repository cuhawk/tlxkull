# Zola Managed Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/zola-mbb-og
> Type: Bug Bounty
> Bounty: P1 $1500–$2000 | P2 $800–$1200 | P3 $400–$600 | P4 $150–$200
> Status: PAUSED (paused 10 Feb 2026)

## Scope

# NOTE: Targets are blurred — inferred from description text (baby.zola.com context)
- in:  https://baby.zola.com/   # type: url  # NextJS/ReactJS/NodeJS — main target (45 known issues)
- in:  Zola Baby Registry iOS App   # type: ios_app  # Objective-C/Swift (US App Store only)

## Out of scope

- out:  help.zola.com   # explicitly OOS (mentioned in policy)

## Auth

- type: session
- creds: @bugcrowdninja.com registration
- notes: US-based device required for iOS app

## Notes

- safe harbor: yes
- status: PAUSED
- No collaboration
- Focus: Account takeover, auth bypass, PII, registry features
- OOS: chat feature, contact form, volumetric/DoS, email enumeration, S3 buckets, DNS/mail misconfig
