# Okta Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/okta
> Type: BBP (Priority Triage)
> Bounty: P1 $100–$75,000 | P2 up to $10,000 | P3 up to $1,000 | P4 $100 | Special: up to $500,000 for RCE/SQLi (limited time)
> Status: In Progress | Started: Nov 16, 2016
> Last scope update: (see announcements)

## Scope

- in:  personal.trexcloud.com              # type: domain   (Okta Personal — confirmed via CrowdStream; use @bugcrowdninja.com to sign up)
- in:  *.oktapreview.com                   # type: wildcard  (Okta PAM sandbox — confirmed via CrowdStream; bugcrowd-pam-###.oktapreview.com)
- in:  *.workflows.oktapreview.com         # type: wildcard  (Okta Workflows sandbox — confirmed via CrowdStream)
- in:  *-admin.oktapreview.com             # type: wildcard  (Okta Admin PAM — confirmed via CrowdStream)
- in:  *.at.oktapreview.com                # type: wildcard  (Okta AT region sandbox — confirmed via CrowdStream)
- in:  support.okta.com                    # type: domain   (Okta Support portal — confirmed via CrowdStream)

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: sign up at personal.trexcloud.com using @bugcrowdninja.com for Okta Personal
- note: Okta credentials (OIE, Workflows, PAM, Advanced Server Access) available via "Get Credentials" at bottom of program brief
- note: contact support@bugcrowd.com if credentials pool exhausted

## Notes

- payout speed: validation within 11 days
- status: ACTIVE
- Cloud / identity management (SSO, MFA, provisioning, MDM, API access management)
- Safe harbor: yes (CFAA + DMCA exemptions)
- scope rating: 4/4
- 460 vulns rewarded; avg payout $1,753
- SPECIAL BONUS: limited-time up to $500,000 for RCE or SQLi on in-scope Okta products
- Okta Personal focus: admin dashboard access, crypto breaks, sharing functionality, import/export apps, mobile intents, input validation
- CRITICAL: do NOT navigate beyond the admin/IdP dashboard if you gain access — stop and report immediately
- out-of-scope: (see full program brief for complete exclusion list)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
