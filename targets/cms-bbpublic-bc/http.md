# cms-bbpublic

> Platform: Bugcrowd — https://bugcrowd.com/engagements/cms-bbpublic
> Type: BBP
> Bounty: P1 $5000–$7000 | P2 $2500–$3500 | P3 $1000–$2500 | P4 $250–$500
> Status: In progress (was paused Jan 2 2026, resumed ~Apr 2026)

## Scope

- in: https://portal.cms.gov/
- in: https://www.cms.gov/
- in: https://cmsnationaltrainingprogram.cms.gov/
- in: *.nsa-idr.cms.gov
- in: *.qpp.cms.gov
- in: https://csscoperations.com/
- out: https://eua.cms.gov/   # explicitly removed Jan 2, 2026
- out: https://eua.cms.gov/efi   # explicitly removed Jan 2, 2026
- out: *.my.site.com   # Salesforce vendor platform
- out: *.service-now.com   # ServiceNow vendor platform
- out: *.atlassian.net   # Atlassian vendor platform

## Notes

- Centers for Medicare & Medicaid Services 2026 Public Bug Bounty
- All associated subdomains of in-scope domains are in scope unless excluded
- Websites CMS-owned/managed that link to this policy are also in scope
- Third-party/vendor systems excluded even if reachable from CMS.gov
- US federal program: no researchers from sanctioned countries (China, Russia, Cuba, etc.)
- Current CMS Federal employees/contractors may not participate
- No leaked/breached credentials allowed for testing
- Use 'Bugcrowd Bug Bounty' or 'BugcrowdCMS' in plaintext requests for log deconfliction
- No user accounts provided; create own accounts
- Recent activity (May 2026): portal.cms.gov active

## Auth

- type: self-registered
- note: No accounts provided; self-register with own accounts
