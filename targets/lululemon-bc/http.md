# lululemon

> Platform: Bugcrowd — https://bugcrowd.com/engagements/lululemon
> Type: BBP
> Bounty: P1 $2,700–$4,000 | P2 $1,000–$2,000 | P3 $300–$700 | P4 $50 | Special P1 up to $10,000
> Status: In progress (started Jun 04, 2019)

## Scope

### North e-commerce sites
- in:  https://shop.lululemon.com   # type: url — primary North American e-commerce
- in:  *.lululemon.com   # type: wildcard — North American scope

### International e-Commerce Sites (10 sites, common codebase — same vuln = counted once)
- in:  https://www.lululemon.com/en-gb/   # type: url — UK
- in:  https://www.lululemon.com/en-au/   # type: url — Australia
- in:  https://www.lululemon.com/en-nz/   # type: url — New Zealand
- in:  https://www.lululemon.com/en-de/   # type: url — Germany
- in:  https://www.lululemon.com/en-fr/   # type: url — France
- in:  https://www.lululemon.com/en-jp/   # type: url — Japan
- in:  https://www.lululemon.com/en-cn/   # type: url — China
- in:  https://www.lululemon.com/en-kr/   # type: url — Korea
- in:  https://www.lululemon.com/en-sg/   # type: url — Singapore
- in:  https://www.lululemon.com/en-se/   # type: url — Sweden

## Auth

- type: signup
- creds: Self-signup using @bugcrowdninja.com email (website + mobile)
- mobile: Download from App Store (iOS)

## Notes

- safe harbor: yes (CFAA + DMCA)
- disclosure: NOT allowed (nondisclosure)
- status: ACTIVE (resumed Apr 9, 2025 after pause)
- Average payout $744; validation within 5 days; scope 3/4
- Non-prod/stage/QA = duplicate of prod; edge dev instances = duplicate of shop.lululemon.com
- International sites: strict PII compliance required; finding on any 1 = applies to all 10

## Special Rewards

- **$10,000**: Unauthorized remote DB access OR complete ATO without any user interaction (RCE, SQLi, reverse shell, etc.)
- **$5,000**: ATO with minimal user interaction (single click) | Auth bypass at checkout/login/track | ATO in checkout/PII/PCI/gift card areas

## Focus Areas

- Checkout and payment process
- Gift card system: https://shop.lululemon.com/shop/luluGiftCards.jsp
- Account takeover
- SQLi, RCE
- Auth/authz issues
- PCI/PII data access

## OOS

- DoS/DDoS, DMARC/SPF, social engineering, phishing
- Rate limiting, missing cookie flags, missing security practices without PoC
- Credential stuffing, leaked credentials
- N-day/CVE: wait 30 days after initial publication
- Non-production sites (stage, QA, non-prod)
- CSRF: only P1 CSRF (complete ATO) eligible; all other CSRF = ineligible
- Reflected XSS: only P1/P2 eligible; lower = ineligible
- AEM Systems: P3-P5 exploits OOS
- lululemon Studio: P3-P5 exploits OOS
