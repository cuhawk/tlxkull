# Zendesk Bug Bounty Engagement

> Platform: Bugcrowd — https://bugcrowd.com/engagements/zendesk
> Type: BBP (Expedited triage)
> Bounty: Zendesk AI: P1 $5,000–$50,000 | P2 $2,000–$4,000 | P3 $750–$1,500 | P4 $500 | Zendesk Front End: P1 $5,000–$20,000 | P2 $2,000–$3,000 | P3 $750–$1,500 | P4 $250 | Zendesk Suite: P1 $5,000–$10,000 | P2 $2,000 | P3 $500 | P4 $100 | Zendesk Mobile: P1 $2,000 | P2 $1,000 | P3 $500 | P4 $100 | Zendesk Public Repos: P1 $2,000 | P2 $1,000 | P3 $500 | P4 $100 | Zendesk Marketplace Apps: P1 $2,000 | P2 $1,000 | P3 $500 | P4 $100
> Status: In Progress | Started: Dec 11 2025
> Last scope update: 12 Mar 2026

## Scope

- in:  *.zendesk.com/agent, /knowledge/, /explore/, /wfm/, /qa, /admin/  # type: wildcard  (Zendesk Suite — agent-facing paths)
- in:  *.zendesk.com/hc/, *.zendesk.com/auth/                            # type: wildcard  (Zendesk Front End — help center & auth)
- in:  Zendesk Messaging front end / Web widget / SDK                    # type: other     (Front End group)
- in:  Zendesk Mobile SDK (iOS + Android)                                # type: other     (Front End group)
- in:  Social channels / Voice / CC integrations                         # type: other     (Front End group)
- in:  LLM / AI features — agents, copilot, app builder                  # type: other     (Zendesk AI group; trial accounts have limited AI access)
- in:  iOS Zendesk Support App                                           # type: ios_app   (Zendesk Mobile Applications)
- in:  Android Zendesk Support app                                       # type: android_app  (Zendesk Mobile Applications)
- in:  github.com/zendesk                                                # type: other     (Zendesk Public Repositories)
- in:  github.com/Tymeshift                                              # type: other     (Zendesk Public Repositories)
- in:  github.com/klausapp                                               # type: other     (Zendesk Public Repositories)
- in:  github.com/ultimateai                                             # type: other     (Zendesk Public Repositories)
- in:  Zendesk Marketplace Apps by Zendesk                               # type: other

## Auth

- type: session
- creds: env:BUGCROWD_SESSION_TOKEN
- creds: env:BUGCROWD_NINJA_EMAIL    # use @bugcrowdninja.com email for testing
- note: sign up for Zendesk trial at zendesk.com using @bugcrowdninja.com
- note: company name "bb-<username>", domain "bb-username.zendesk.com"

## Notes

- payout speed: validation within 5 days; expedited triage
- status: ACTIVE
- Technology / customer support SaaS; 28 vulns rewarded; avg bounty ~$805
- Safe harbor: yes (CFAA + DMCA exemptions)
- NDA: no disclosure without prior written consent
- scope rating: 2/4
- N-day policy: 30 days after public release
- Shared Responsibility Model applies
- no AI-generated or low-effort reports; must show original analysis
- AI focus: prompt injection, RAG poisoning, retrieval bypass, PII/secrets leakage, cross-tenant data leakage
- out-of-scope: P5, DoS/DDoS, rate limiting, email bombing, all social engineering, SPF/DKIM/DMARC, physical vulns, individual employee reports, third-party breach reports

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
