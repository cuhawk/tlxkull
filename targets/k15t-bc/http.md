# k15t — K15t Bug Bounty (Atlassian Marketplace)

**Platform:** Bugcrowd BBP  
**Program URL:** https://bugcrowd.com/engagements/k15t  
**Started:** Jul 11, 2019  
**Disclosure:** Coordinated disclosure (explicit permission required before publishing)  
**Safe Harbor:** Not listed  

---

## Rewards (CVSS overrides VRT)

| Priority | Reward |
|----------|--------|
| P1 | $1,500 |
| P2 | $900 |
| P3 | $300 |
| P4 | $100 |

---

## Authentication

- Create Atlassian Cloud instance at `<username>.atlassian.net` using @bugcrowdninja.com email
- Install live app versions from Atlassian Marketplace (free trial available)
- **Unsubscribe before 30-day trial ends** to avoid charges
- Data Center: download from atlassian.com + use timebomb license

**CRITICAL:** Testing/spamming live support portals or Atlassian Marketplace sites = **banned from ALL Atlassian programs**

---

## In-Scope Domains

- `*.addons.k15t.com/*`
- `*.k15t.app/*`
- `*.scrollhelp.site/*`

---

## In-Scope Apps — Cloud

- Backbone Issue Sync for Jira
- Scroll PDF Exporter
- Scroll Word Exporter
- Scroll HTML Exporter (+ Scroll Exporter Extensions)
- Scroll Documents for Confluence
- Variants for Scroll Documents
- Translations for Scroll Documents
- Scroll Imagemap for Confluence
- Scroll Viewport for Confluence
- Scroll Content Quality for Confluence

## In-Scope Apps — Data Center

- Scroll PDF Exporter
- Scroll Word Exporter
- Scroll HTML Exporter
- Scroll Documents for Confluence
- Variants for Scroll Documents
- Translations for Scroll Documents
- Scroll Imagemap for Confluence
- Scroll Versions for Confluence
- Scroll Translations for Confluence
- Scroll Viewport for Confluence

---

## Focus Areas

- **Backbone Issue Sync:** Unauthorized cross-instance data leakage or access
- **Scroll Documents:** Document content confidentiality bypass
- **Scroll Viewport:** XSS through authoring content; SSRF during site generation

---

## Out-of-Scope

- DoS/DDoS attacks
- Automated scanners
- Customer production instances (only test your own provisioned instance)
- Word Exporter: custom templates with embedded scripts (known/accepted behavior)
- HTML Exporter: security issues in exported HTML via modified files or custom JS

---

## Notes

- Part of broader Atlassian Marketplace Bug Bounty ecosystem
- CVSS scoring takes precedence over Bugcrowd VRT for priority assignment
- No safe harbor explicitly listed — coordinate before any disclosure
