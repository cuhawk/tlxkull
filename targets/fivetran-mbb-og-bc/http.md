# Fivetran

> Platform: Bugcrowd — https://bugcrowd.com/engagements/fivetran-mbb-og
> Type: BBP
> Bounty: P1 $2,500–$7,500 | P2 $1,000–$2,500 | P3 $500–$1,000 | CTF P1 $15,000
> Status: In progress (started Mar 18, 2025)

## Scope

- in:  https://fivetran.com/login   # type: url — *.fivetran.com (primary)
- in:  https://fivetran.com/login   # type: url — Fivetran SDK CTF (connector SDK target)
- out: *.db.fivetran.com
- out: testing-datalake.fivetran.com
- out: shop.fivetran.com
- out: status.fivetran.com
- out: support.fivetran.com
- out: community-stage.fivetran.com
- out: trust.fivetran.com
- out: All HVR products

## Auth

- type: signup
- creds: Sign up at https://fivetran.com/signup using @bugcrowdninja.com email ONLY (no personal email)
- secondary account: add "+1" to @bugcrowdninja.com email

## Notes

- safe harbor: yes (CFAA + DMCA)
- disclosure: coordinated (requires explicit request on submission)
- status: ACTIVE
- P4 findings: marked Not Applicable (no reward)
- No AI tools (ChatGPT, DeepSeek, Gemini) during research — prohibited
- Do not contact Fivetran directly; use support@bugcrowd.com for escalations
- N-day policy: 30 days after public release

## Traffic Identification

- Required header: `X-Bug-Bounty:<bugcrowdusername>`

## CTF Challenge Details

- Target Account ID: `incline_inmate`
- Target Group ID: `needful_french`
- Target Connection ID: `asylum_moat`
- To win: submit SECRET_VALUE + reproduction steps + email submission ID to contact record email with subject "Fivetran CTF Challenge"
- Focus: Connector SDK (https://fivetran.com/docs/connectors/connector-sdk#connectorsdk) — Python scripts run in sandboxed Kubernetes clusters
- First valid submission wins; CTF pauses during remediation then resumes

## Focus Areas

- Access to pipeline data
- Account authentication
- Fivetran Connector SDK

## OOS Submission Types

- P4/P5 vulns
- DoS/DDoS, rate limiting, email flooding
- Social engineering / phishing
- Clickjacking
- Brute force / credential stuffing
- Modifying data in accounts you don't own
- Third-party/external service compatibility issues
- Leaked credentials (points only, no reward)
