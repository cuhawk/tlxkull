# epam-mbb-og — EPAM Systems Managed Bug Bounty Program

**Platform:** Bugcrowd BBP  
**Program URL:** https://bugcrowd.com/engagements/epam-mbb-og  
**Started:** Sep 28, 2023  
**Disclosure:** Nondisclosure (no public disclosure allowed)  
**Safe Harbor:** Yes (CFAA + DMCA exempt)  

---

## Rewards (Multi-Tier)

### Subdomain Takeover — Tier 0
| Priority | Reward |
|----------|--------|
| P1/P2/P3 | $150 |

**Exclusions:** *.lab.epam.com, *.projects.epam.com, *.opensource.epam.com, *.gcp.cloudapp.epam.com (OOS for reward; ephemeral GKE infra)

### Tier 1 — 3rd-level subdomains *.epam.com
| Priority | Reward |
|----------|--------|
| P1 | $1,000 |
| P2 | $600 |
| P3 | $300 |
| P4 | $100 |

### Tier 2 — *.projects.epam.com
| Priority | Reward |
|----------|--------|
| P1 | $500 |
| P2 | $250 |
| P3/P4 | Accepted, no bounty |

### Tier 3 — *.lab.epam.com + *.opensource.epam.com (dev/OSS environments)
| Priority | Reward |
|----------|--------|
| P1 | $300 |
| P2 | $150 |
| P3/P4 | Accepted, no bounty |

### Tier 4 — Any level subdomains (excluding Emakina)
| Priority | Reward |
|----------|--------|
| P1 | $500 |
| P2 | $300 |
| P3 | $150 |
| P4 | Not rewarded |

### Open Redirect — *.epam.com (3rd level)
| Priority | Reward |
|----------|--------|
| Any | $100 |

### Open Redirect Tier #1 — *.projects.epam.com, *.lab.epam.com, *.opensource.epam.com
| Priority | Reward |
|----------|--------|
| Any | $50 |

### Points Only
- Leaked credentials/confidential information from malware logs/dumps/intelligence services/public sources

---

## Authentication

- Use @bugcrowdninja.com email alias
- Add header: `X-Bugcrowd: Bugcrowd-<Username>` on every request
- Do NOT use EPAM employee credentials

---

## In-Scope

- in: *.epam.com (3rd-level subdomains) — Tier 1
- in: *.projects.epam.com (any level) — Tier 2
- in: *.lab.epam.com (any level) — Tier 3
- in: *.opensource.epam.com (any level) — Tier 3
- in: Any level subdomains (non-Emakina) — Tier 4

---

## Explicit OOS

- ethics.epam.com — completely OOS
- investors.epam.com — financial disclosure (public company, no rewards)
- https://www.emakina.nl/, emakina.group, emakina.com, emakina.ch, emakina.fr, emakina.us, emakina.at
- Contact forms on epam.com / *.epam.com
- Account removal requests at https://anywhere.epam.com/en/contact-us
- *.gcp.cloudapp.epam.com (ephemeral GKE infra)
- IP auth bypass via Host header manipulation (removed from scope Sep 2024)

---

## Focus Areas

- Injections (SQLi, XXE, SSRF, path traversal)
- RCE
- Stored/Reflected XSS (not self-XSS)
- PII leakage
- Security misconfigurations with demonstrated impact
- Reading server files / executing commands / retrieving sensitive info

---

## Key OOS Vulnerability Types

- Clickjacking, broken link hijacking
- Firebase API key exposure without impact
- Session expiration/lockout issues
- Blind SSRF without impact
- Self-XSS
- CSRF on unauthenticated/non-sensitive forms
- CDN bypass (CloudFront/Cloudflare origin IP disclosure)
- IP auth bypass via Host header
- Missing cookie flags (HttpOnly, Secure)
- Missing email security headers (SPF/DKIM/DMARC)
- Automated scanner reports
- DoS/DDoS
- Emakina sites (Tier 4 exception)
- Open redirect, host header injection on Tier 4 targets
- Dependency confusion, EXIF data, WordPress user enumeration

---

## Main Guidelines (Violations = Immediate Ban)

- No automated form submission tools
- No production system disruption or data destruction
- No ethics.epam.com testing
- Required header on all requests: `X-Bugcrowd: Bugcrowd-<Username>`
- Use @bugcrowdninja.com email alias
- No automated scanners

---

## Notes

- 379 vulnerabilities rewarded historically
- Average payout ~$429 (last 3 months); validation ~8 days
- Nondisclosure: cannot release vulnerability information publicly
- Subdomain takeover at *.projects.epam.com in scope since Jul 2024
- Fake PII may be present in lab/opensource environments
