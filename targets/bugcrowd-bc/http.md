# Bugcrowd Bug Bounty — Bugcrowd

**URL:** https://bugcrowd.com/engagements/bugcrowd
**Category:** BBP
**Safe harbor:** Yes
**Disclosure:** Coordinated (explicit permission required)
**Started:** 2013-09-07

## Auth
- Self-provision credentials only — no supplemental creds provided
- Test against Hack Me! (https://bugcrowd.com/hackme) only — NEVER against real customer bounties
- 30-day cooldown for former Bugcrowd employees

## Targets

### In Scope Targets (P1=$2,501–10,000)
- in: bugcrowd.com (core platform)
- in: *.bugcrowd.com (Bugcrowd-owned and operated subdomains)
- NOTE: Government (.gov) targets may not be publicly accessible

### Beta Feature Target (P1=$1,500–5,000)
- in: Centralized authentication beta endpoint (not everyone has access)
- Note: Reports may be duped to internal ones; different rewards from main program

## Rewards
| Priority | Main Program | Beta Feature |
|----------|-------------|--------------|
| P1 | $2,501–10,000 | $1,500–5,000 |
| P2 | $901–2,500 | $500–1,500 |
| P3 | $301–900 | $100–500 |
| P4 | $300 | $100 |

**Bonus:** Up to 100% additional reward for especially impactful P1/P2 findings (at Bugcrowd's discretion).

## Out of scope
- 3rd party services (even if running on *.bugcrowd.com subdomains):
  - www.bugcrowd.com, blog.bugcrowd.com → Pantheon
  - Cloudflare infrastructure
  - Drift, Intercom
  - forum.bugcrowd.com → Discourse
  - email.bugcrowd.com, email.forum.bugcrowd.com → Mailgun
  - collateral.bugcrowd.com → Outreach
  - bounce.bugcrowd.com, go.bugcrowd.com, ww2.bugcrowd.com → Marketo
  - pages.bugcrowd.com → HubSpot
  - researcherdocs.bugcrowd.com → Readme.io
  - events.bugcrowd.com → Splash
  - assetinventory.bugcrowd.com → BitDiscovery
  - bugcrowd*.freshdesk.com, bugcrowd-support.freshdesk.com → Freshdesk
  - github.com/bugcrowd PRs/Issues (unless credential leakage or critical impact)
  - trust.bugcrowd.com → Safebase
- Rate limiting
- EXIF data not stripped from file attachments on submissions (wont-fix, known)
- Username format impersonation (setting username to match staff format — no permissions effect)
- Prompt injection vulnerabilities
- Reports from automated tools only (no manual validation = Not Applicable)
- Theoretical attack vectors without PoC exploitability

## Notes
- Infrastructure runs on AWS
- If you find a Bugcrowd-owned host not listed in scope, submit a report asking about eligibility — no penalty
- Third-party issues caused by Bugcrowd misconfiguration/insecure usage are reportable
- flag.txt resource available (Hack Me challenge)
