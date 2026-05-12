# City of Vienna Managed Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/city-of-vienna-mbb-og
> Type: BBP
> Bounty: Points–$3,500
> Status: In Progress
> Last scope update: (see program brief)

## Scope

- in:  *.wien.gv.at                        # type: wildcard  (confirmed via CrowdStream — City of Vienna government portal)
- in:  www.wien.gv.at                      # type: domain   (confirmed via CrowdStream)
- in:  stp.wien.gv.at                      # type: domain   (confirmed via CrowdStream — P1 finding Apr 2026)
- in:  *.wien.at                           # type: wildcard  (confirmed via CrowdStream)
- in:  *.gesundheitsverbund.at             # type: wildcard  (confirmed via CrowdStream — Vienna Healthcare Group)

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing

## Notes

- payout speed: validation within 4 days
- status: ACTIVE
- Government / City of Vienna digital services
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 4/4
- 116 vulns rewarded; avg payout $738
- Very active program — 83 submissions in past 6 months
- gesundheitsverbund.at = Vienna Healthcare Group (hospitals, clinics)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
