# Just Eat Takeaway.com Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/justeattakeaway
> Type: BBP
> Bounty: P1 $100–$4,500 | P2 $750–$1,500 | P3 $100–$750 | P4 $50–$100
> Status: In Progress
> Last scope update: Oct 2025 (app.business.* and business.* removed)

## Scope

- in:  *.justeattakeaway.com               # type: wildcard  (confirmed via CrowdStream — main brand)
- in:  *.takeaway.com                      # type: wildcard  (confirmed via CrowdStream — Netherlands/EU)
- in:  *.thuisbezorgd.nl                   # type: wildcard  (confirmed via CrowdStream — Dutch brand)
- in:  *.skipthedishes.com                 # type: wildcard  (confirmed via CrowdStream — Canadian brand)
- in:  *.10bis.co.il                       # type: wildcard  (confirmed via CrowdStream — Israeli brand)
- in:  *.scoober.com                       # type: wildcard  (confirmed via CrowdStream — delivery logistics)
- in:  *.jet-external.com                  # type: wildcard  (confirmed via CrowdStream)
- in:  uk.api.just-eat.io                  # type: domain   (confirmed via CrowdStream — UK API)
- in:  i18n.api.just-eat.io                # type: domain   (confirmed via CrowdStream — i18n API)
- in:  SkipTheDishes (mobile app)          # type: other     (confirmed via CrowdStream — Canadian delivery app)
- in:  Takeaway.com (app/service)          # type: other     (confirmed via CrowdStream)
- in:  Just-Eat Holding Limited            # type: other     (confirmed via CrowdStream)
- out: app.business.* (all business.* subdomains)  # type: wildcard  (removed Oct 2025 — decommissioned)

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing

## Notes

- payout speed: validation within 4 days
- status: ACTIVE
- Hospitality / food delivery marketplace; global brands (JET, Thuisbezorgd, 10bis, SkipTheDishes, Takeaway)
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 4/4
- 577 vulns rewarded; avg payout $219
- Hacktober SWAG bonus: P1/P2 submissions receive merchandise vouchers
- do not include harsh language in reports (professional/neutral wording required)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
