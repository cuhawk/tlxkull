# Anthropic Bug Bounty Program

> Platform: HackerOne — https://hackerone.com/anthropic
> Type: BBP (Bug Bounty Program) | Managed by HackerOne | Gold Standard Safe Harbor
> Bounty: $100 – $10,000 | Avg $1,000–$1,600 | Top $4,700–$8,300
> Response efficiency: 97% | Avg first response: 21h | Avg triage: 1d 20h | Avg bounty: 1w 9h
> Last scope update: May 8, 2026

## Scope

- in:  claude.ai                                          # type: domain
- in:  console.anthropic.com                              # type: domain
- in:  api.anthropic.com                                  # type: domain
- in:  support.anthropic.com                              # type: domain
- in:  docs.anthropic.com                                 # type: domain
- in:  anthropic.atlassian.com                            # type: domain
- in:  github.com/anthropics                              # type: repo
- in:  com.anthropic.claude                               # type: android_app
- in:  com.anthropic.claude                               # type: ios_app
- in:  Claude.app                                         # type: macos_app
- in:  fcoeoabgfenejglbffodgkkbkcdhcgfn                   # type: other
- in:  Claude Code (github.com/anthropics/claude-code)    # type: repo
- in:  API & SDKs (GraphQL@api.anthropic.com)             # type: api
- in:  Infrastructure & Internal Apps/Services            # type: other
- in:  Leaked Employee API Keys                           # type: other
- in:  Claude Desktop Extensions / MCP servers            # type: other
- out: github.com/modelcontextprotocol                    # type: repo

## Auth

- type: session
- creds: env:H1_SESSION_TOKEN

## Notes

- payout speed: ~1 week 9 hours to bounty
- program launched: May 2026
- open scope: rewards all owned assets based on impact even if not listed
- fast payment: within 1 month of receiving report
- Core assets: claude.ai, console.anthropic.com, api.anthropic.com, Official Clients, Claude Code, API & SDKs
- Non-Core assets: support, docs, atlassian, github, infra, leaked keys, Claude in Chrome, MCP
- Claude Code focus: permission prompt bypasses, invisible command execution, file writes outside working dir
- atlassian note: AP Inbox, Finsys Intake, Dev Accounts Payable queues are intentionally accessible — informative
- github repos: archived repos and forks are excluded unless impact can be demonstrated on Anthropic assets
- MCP: third-party connectors OOS — only Anthropic-developed software in scope
- triagers: HackerOne-managed | includes retesting + collaboration enabled
- total bounties paid: $551,585 | resolved reports: 270 | hackers thanked: 166
- top finding areas: Claude Code (41% of resolved), claude.ai (15%), Infra (7%), Clients (7%)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
