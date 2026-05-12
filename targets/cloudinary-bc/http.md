# Cloudinary Bug Bounty

## Target
- program: cloudinary (Bugcrowd)
- category: bbp
- started: Feb 14, 2018
- nondisclosure: true (no public disclosure permitted)

## Scope
- note: Target tables did not render — specific URLs not captured. Re-check scope page.
- note: Only targets listed on scope page are in scope; any unlisted Cloudinary domain/subdomain is OOS

## Bounties
### In Scope Targets (Tier I)
- Special: $7,000 (extraordinary P1)
- P1: $2,000-4,000
- P2: $500-2,000
- P3: $0-500

### In Scope Tier II
- P1: $500-1,000
- P2: $0-500

## Auth
- Must use @bugcrowdninja.com email to set up Cloudinary account

## High-Value Areas
- Full compromise of Production system (RCE, shell)
- Business logic bypasses with significant impact
- Major operational failure (excluding DoS)

## OOS Vulnerabilities
- External SSRF via Cloudinary's built-in URL fetch functionality (fetch URL, upload API URL param) — ONLY OOS when accessing external servers; accessing internal networks or external services with significant impact IS in scope
- Clickjacking
- Mail server domain misconfiguration (email spoofing, missing DMARC, SPF/DKIM)
- EXIF geolocation data
- Brute force on login/forgot password
- Account lockout enforcement
- Internal IP address disclosure
- Username/email enumeration
- No/weak/CAPTCHA bypass
- Missing HTTP security headers
- Cookie issues
- SSL issues
- Lack of rate limit
- Weak password policies
- Bugs in old/EOL browsers
- Previously known vulnerable libraries without PoC
- Credentials exposed in other data breaches
- Automated scanner reports

## Prohibited Actions
- Automated scanners
- Uploading webshells or arbitrary command files
- Persistent connections to server
- Accessing files/data beyond proof of vulnerability
- Testing UI feedback widget (cloudinary.com/console/api/v1/user/send_feedback)
- Testing 3rd-party Cloudinary services
- Creating support tickets
- DDoS/SPAM attacks

## Submission Requirements
- Full description + exploitability/impact
- Manual step-by-step reproduction
- Videos, screenshots, exploit code, web/API requests
- Email address or Cloud name of test accounts
- For RCE: source IP, timestamp with timezone, server request/response, filenames of uploaded files (must include "bugcrowd" + timestamp)

## Notes
- OOS submissions with reasoning may be considered case-by-case
- OOS submissions without reasoning = OOS with negative points
- Full safe harbor
