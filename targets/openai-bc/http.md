# OpenAI

> Platform: Bugcrowd — https://bugcrowd.com/engagements/openai
> Type: BBP
> Bounty: P1=$2000-$100000, P2=$1000-$2000, P3=$500-$1000, P4=$200-$500 (varies by target group)
> Status: In progress

## Scope

### In Scope — API Targets (P1 $2000-$6500, P2 $1000-$2000, P3 $500-$1000, P4 $200-$500)

- in: api.openai.com
  type: domain
  note: OpenAI APIs and public cloud resources serving the API (Azure storage, VMs, etc.)

### In Scope — ChatGPT (P1 $2000-$6500, P2 $1000-$2000, P3 $500-$1000, P4 $200-$500)

- in: chat.openai.com
  type: domain
  note: ChatGPT Plus, logins, subscriptions, OpenAI-created plugins (Browsing, Code Interpreter). Include conversation ID in reports.

### In Scope — OpenAI Research Org (P1 $1250-$3500, P2 $600-$1250, P3 $200-$600)

- in: openai.org
  type: domain
- in: *.openai.org
  type: wildcard

### In Scope — Other OpenAI Targets (P1 $1250-$2500, P2 $600-$1250, P3 $200-$600)

- in: openai.com
  type: domain
  note: Main website, developer docs, developer playground, other internet-facing OpenAI infrastructure

### In Scope — Third Party Corporate Targets (P1 $1000-$2500, P2 $500-$1000, P3 $200-$500, max $5000)

- in: third-party-corporate
  type: other
  note: Confidential OpenAI info exposed through third parties (Google Workspace, Asana, Notion, Stripe, etc.). Look-only, no additional testing against the companies themselves.

### In Scope — OpenAI API Keys (P1 $250-$2500)

- in: api-keys-program
  type: other
  note: Report found API keys via https://openai.com/form/api-key-bug-bounty — DO NOT submit keys through Bugcrowd. Valid keys have prefix sk- or sess-

### In Scope — Sora (P1 only, app shutting down Apr 26 2026)

- in: sora.com
  type: domain
  note: Sora social app/website. Shutting down Apr 26 2026. Only P1 findings accepted.

### In Scope — Atlas browser (P1 $2000-$6500)

- in: atlas-browser
  type: other
  note: OpenAI web browser based on Chromium. Privilege escalation/sandbox escape from ChatGPT side panel, bypasses of origin isolation. Upstream Chromium bugs -> Chrome VRP.

### In Scope — Codex (P1 $500-$1500, P2 $250-$500, P3 $100-$250, P4 $50-$100)

- in: codex-cli
  type: other
  note: Codex across all surfaces (CLI, App, IDE, Web) and sandbox. Focus on sandbox escape/bypass (filesystem, network, process boundaries).

### In Scope — Access to unreleased/private models

- in: private-models
  type: other
  note: Attacks that let you query private/unreleased OpenAI models not in API docs.

### Out of Scope

- out: Model issues (jailbreaks, DAN prompts, getting model to say bad things)
- out: Model hallucinations
- out: Sandboxed Python code execution in ChatGPT code interpreter (intended feature)
- out: Agent Mode sandbox code execution
- out: Container Tool Sandbox (GPT-5 models running as root — not privilege escalation)
- out: pay.openai.com (CNAME to Stripe — report to Stripe VRP)
- out: community.openai.com (CNAME to third party)
- out: DoS, brute force, password spraying, fuzzing
- out: SPF/DMARC/DKIM email issues
- out: Missing HTTP headers without PoC
- out: SSL/TLS cipher issues without PoC
- out: Clickjacking
- out: API rate limiting (except sustained bypass at hundreds of requests scale)

## Auth

- type: session
- creds: env:BUGCROWD_NINJA_EMAIL
- note: Can use personal account or sign up with @bugcrowdninja.com email

## Notes

- status: ACTIVE
- max_bounty: $100000 (exceptional P1 critical findings since Mar 26 2025)
- model_issues: Report to https://openai.com/form/model-behavior-feedback NOT bugcrowd
- api_keys: Submit at https://openai.com/form/api-key-bug-bounty NOT bugcrowd
- sandbox_check_python: Linux 9d23de67 4.4.0 kernel + whoami=sandbox = inside Python sandbox
- sandbox_check_agent: Linux 6.12.13 2025 kernel + whoami=oai = inside Agent sandbox
- sandbox_check_container: root user + whoami=sandbox = Container Tool Sandbox GPT-5 (no escape)
- safety_bounty: New Safety Bug Bounty launched Mar 25 2026 (separate from this BBP)

## Optional: known peer IDs (for caido-idor and mobile-idor)

- peer_ids: []

## Optional: artifact pointers

- artifacts: []
