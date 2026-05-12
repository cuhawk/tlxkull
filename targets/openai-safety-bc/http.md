# OpenAI Safety Bug Bounty

> Platform: Bugcrowd — https://bugcrowd.com/engagements/openai-safety
> Type: BBP (Bug Bounty Program) | Public (transitioned public Mar 25, 2026) | Expedited triage
> Bounty: P1 $5,500–$7,500 (exceptional up to $100,000) | P2 $2,500–$3,500 | P3 $750–$1,500 | P4 $250–$500
> Status: In Progress (started Jul 29, 2025) | Avg payout: $500 (last 90d) | Validation within: 5 days
> Last scope update: Mar 25, 2026

## Scope

- in:  openai.com                                         # type: domain
- in:  *.openai.com                                       # type: wildcard
- in:  chatgpt.com                                        # type: domain
- in:  Agentic Tools (Atlas Browser, Codex, Operator, Connectors, ChatGPT agentic tools)  # type: other
- in:  MCP / Connector integrations (OpenAI-side config, permissioning, confirmation UX)  # type: other
- in:  OpenAI Proprietary Information (internal data, CoT reasoning chains)               # type: other
- in:  Account and Platform Integrity (rate limit bypasses, mass account creation)        # type: other
- in:  Other Novel Abuse (direct path to user harm with actionable remediation)           # type: other
- out: Content Issues (model policy-violating responses — not addressable via sec fixes)  # type: other
- out: Third-party MCP servers not resulting in OpenAI-side remediation                   # type: other
- out: Geographic access restriction bypasses                                             # type: other
- out: Fraud/social engineering (fake OpenAI Startup Fund accounts etc.)                 # type: other

## Auth

- type: session
- creds: env:OPENAI_BUGCROWD_SESSION
- creds: env:OPENAI_TEST_ACCOUNT_A     # must be bugcrowdninja.com email — victims must be test accounts you own

## Notes

- payout speed: ~5 days validation
- program focus: SAFETY and ABUSE issues — complements OpenAI's main Security BBP
- qualifying criteria: must be design/implementation issue in active product, consistently reproducible, not duplicate
- agentic scope: indirect prompt injection via Connectors/MCP causing data exfiltration or unauthorized actions
- agentic scope: authz bypasses where agent accesses data beyond permitted scope (cross-workspace/tenant)
- agentic scope: agents performing tool actions without user confirmation or with misleading confirmations
- rate limit bypass: must demonstrate access at next subscription tier or higher (e.g. Free→Go, Plus→Pro)
- mass account creation: ≥10 accounts without human interaction qualifies
- CoT in scope: full unsummarized Chain of Thought disclosure
- system prompts: OUT OF SCOPE
- test accounts: safety/abuse testing may cause account bans — use dedicated test accounts only
- no reimbursement for account upgrades
- historical max bounty increased to $100,000 for exceptional/critical findings (Mar 2026)
- IDOR bonus period ran Mar 26–Apr 30 2025 (2× rewards P1–P3)
- request header required: X-Request-Purpose: BugcrowdResearch
- recent accepted submissions on: openai.com, *.openai.com (P4)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
