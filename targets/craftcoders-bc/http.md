# craftcoders — Craft Coders Marketplace Bug Bounty (Bugcrowd BBP)

> **TYPE: Atlassian Marketplace Add-on** — Target is the mailto.wiki add-on, NOT marketplace.atlassian.com itself.
> Must install the add-on in your own Atlassian Cloud/Server/DC test instance to test.
> Test instance namespace: `bugbounty-test-<bugcrowd-name>.atlassian.net`

## Program info
- URL: https://bugcrowd.com/engagements/craftcoders
- Type: bug_bounty (Atlassian add-on)
- Scope rating: 1/4
- Started: Dec 07, 2021

## Rewards
- P1: $1,500
- P2: $900
- P3: $300
- P4: $100

## In scope
- type: web
  url: mailto.wiki add-on (installed in your Atlassian Confluence Cloud/Server/DC test instance)
  notes: The add-on application itself is in scope; the marketplace.atlassian.com URL is NOT

## Out of scope
- marketplace.atlassian.com (the Atlassian marketplace site)
- https://mailto.wiki (documentation website)
- Customer cloud instances and data
- Atlassian's own infrastructure
- Test environments (e.g. stage.connect.mailto.wiki)
- Unencrypted SMTP (intentionally allowed)
- AWS SPAM/virus filter false positives/negatives

## Focus areas
- Email header injection
- Cross Instance Data Leakage/Access
- SSRF, RCE, XSS (Stored/Reflected), CSRF, SQLi, XXE
- Access control / IDOR
- Path traversal

## Notes
- Automated scanners strictly prohibited (ban enforced)
- Must use @bugcrowdninja.com email address
- Reports in plain text only (no PDF/DOCX)
- Cloud setup: navigate signup, use format `bugbounty-test-<username>`, install mailto.wiki from marketplace
- Server/DC: download from https://www.atlassian.com/software/confluence/download
