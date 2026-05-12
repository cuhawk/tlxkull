# Comcast Xfinity Bug Bounty — Bugcrowd BBP
# https://bugcrowd.com/engagements/comcast-mbb
# Category: Technology | Safe harbor: full | Started: Jan 20, 2022

## Scope

### Primary Targets (P1 $3500-$5500)
- in: *.xfinity.com [production systems with customer data]
- in: *.comcast.com [production systems with customer data]
# NOTE: Targets are "all technologies, products, and services that create the Xfinity consumer experience"
# All endpoints called by Xfinity services/apps are in scope unless excluded
# Targets loading — see CrowdStream: *.comcast.com and *.xfinity.com confirmed as primary targets

### Secondary Targets (P1 $1750-$2750)
- in: (non-production systems, low business impact)
# Secondary targets loading — visit program for current list

## Out of scope
- 3rd party endpoints / Marketing & Analytics endpoints
- Xfinity Home / xFi (separate VDP program)
- NBCUniversal (report to cyber@nbcuni.com)
- Sky

## Rules
- Add header: X-Bug-Bounty:<bugcrowdusername> to all traffic
- Include IP address in P1/P2 reports
- No credentials provided — self-provision accounts
- No DoS, no testing against customer accounts
- High Impact Subdomain Takeover: P2→P3; Basic Subdomain Takeover: P3→P4
- N-Day: in scope after 30 days from public release
