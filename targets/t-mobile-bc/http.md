# T-Mobile

> Platform: Bugcrowd — https://bugcrowd.com/engagements/t-mobile
> Type: BBP
> Bounty: P1=$20000-$133700, P2=$12000-$35000, Special=$65000-$133700
> Status: In progress

## Scope

### Special Target (P1 $65000-$133700)

- in: t-mobile-tnp-servers
  type: other
  note: T&P Servers — must provide contents of flag.txt file
- in: t-mobile-internal-server
  type: other
  note: Internal Server (not T&P). Graded based on CCI/Corporate/data accessed. *.internal.t-mobile.com and *.unix.gsm1900.org may be publicly accessible (still counts).
- in: t-mobile-cellular-auth-bypass
  type: other
  note: Cellular Network Auth Bypass via Web/Mobile App over cellular network targeting MSISDN 404-200-7239. Must provide video showing account profile, settings, lines.

### Priority Target (In scope, +20% bonus)

- in: t-mobile-priority
  type: other
  note: Priority target receives additional 20% bonus. Graded by vulnerability location: Core, Primary, or Supplemental.

### Core Assets (P1 $55000, P2 $35000)

- in: *.t-mobile.com
  type: wildcard
  note: Core T-Mobile assets

### Primary Assets (P1 $35000, P2 $25000)

- in: t-mobile-primary
  type: other
  note: Primary T-Mobile assets (target table not loaded — see recent activity showing *.t-mobile.com)

### Supplemental Assets (P1 $20000, P2 $12000)

- in: api.vistarmedia.com
  type: domain
- in: packages.cortexpowered.com
  type: domain
- in: api.vistarmedia.eu
  type: domain
- in: production-dynam-creative.vistarmedia.com
  type: domain
- in: storybook.vistarmedia.com
  type: domain
- in: creatives.vistarmedia.com
  type: domain
- in: sflower.cortexpowered.com
  type: domain
- in: production-delivery-metrics-svc.vistarmedia.com
  type: domain
- in: maps.vistarmedia.com
  type: domain
- in: transcodes-cdn.vistarmedia.com
  type: domain
- in: assets-cdn.vistarmedia.com
  type: domain
- in: docker-staging.adstruc.com
  type: domain
- in: staging-trafficking.vistarmedia.com
  type: domain
- in: job-svc-b.vistarmedia.com
  type: domain
- in: docsite.vistarmedia.com
  type: domain
- in: sfleet.cortexpowered.com
  type: domain
- in: audience-builder.vistarmedia.com
  type: domain
- in: staging-login.vistarmedia.com
  type: domain
- in: clients.adstruc.com
  type: domain
- in: demo.adstruc.com
  type: domain

### Recently Added Supplemental (Mar 2026)

- in: blis.com
  type: domain
- in: *.blis.com
  type: wildcard
- in: blis.co.uk
  type: domain
- in: blis.media
  type: domain
- in: blismedia.com
  type: domain
- in: amazon-tacticalplanner.com
  type: domain
- in: atom-lens.com
  type: domain
- in: emaudience.com
  type: domain
- in: groupmaudience.com
  type: domain
- in: msaudience.com
  type: domain
- in: tpmaudience.com
  type: domain
- in: wmaudience.com
  type: domain
- in: platform.blis.com
  type: domain
- in: platform.development.blis.com
  type: domain
- in: platform.rc.blis.com
  type: domain

### Static Rewards

- in: t-mobile-subdomain-takeover
  type: other
  note: Subdomain takeover = $1500 flat, classified as P3

### Mobile Targets (In scope, graded by Core/Primary/Supplemental)

- in: t-mobile-apps
  type: other
  note: Current T-Mobile apps (target list not loaded from API)

### Out of Scope

- out: Any API endpoint ending with /self-service-*
- out: Clickjacking on pages with no sensitive data
- out: Unauthenticated/logout CSRF
- out: MitM or physical device access required
- out: Outdated library without working PoC
- out: DoS/DDoS
- out: Missing security headers
- out: Open redirects (not eligible)
- out: Cross-Site Scripting (listed as OOS in web section)
- out: Cache poisoning
- out: Automated scanning tool output without manual PoC
- out: Certificate pinning absence, obfuscation, jailbreak detection (mobile)
- out: Attacks on rooted/jailbroken devices

## Auth

- type: session
- creds: env:BUGCROWD_NINJA_EMAIL
- note: Self-register T-Mobile account with @bugcrowdninja.com. Hardware (SIM, phones) must be purchased by researcher. No accounts provisioned by T-Mobile or Bugcrowd.

## Notes

- status: ACTIVE
- required_header: X-Bug-Bounty:BugCrowd-<username> (30% penalty if missing as of 8/14/23)
- submission_template: submission-template.md required (30% penalty if missing as of 9/11/2025)
- rate_limit: Max 5 requests/sec for automated tools
- custom_rating: Uses "Severity Rating Chart 1.4" (not CVSS/VRT). Only P1/P2 and some P3 (static rewards) paid. P3/P4/P5 may be N/A.
- loyalty_program: 20-25% bonus after 2+ P1/P2 per quarter. Tiers: Apprentice(5%), Hero(10%), Knight(15%), Champion(20%), Grand Champion(25%)
- no_deutsche_telekom: Scope limited to T-Mobile USA. Deutsche Telekom assets NOT in scope.
- no_customer_data: Do not modify any data in customer accounts. Will result in ban.
- special_target_MSISDN: 404-200-7239

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
