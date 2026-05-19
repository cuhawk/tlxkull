---
title: Gal Nagli (naglinagli)
slug: gal-nagli
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [naglinagli, galnagli, nagli]
role: dual
primary_focus: cloud
tags: [person, role/dual, role/hunter, role/researcher, focus/cloud, focus/saas, focus/recon, focus/supply-chain, focus/ai-platforms]
inbound: []
---

# Gal Nagli (naglinagli)

## Identity

- **Real name:** Gal Nagli. Based in Israel (Tel Aviv area).
- **Primary handles:** `naglinagli` (X / HackerOne / Bugcrowd / GitHub) and
  the shorter `galnagli` used on X and on his personal site
  `galnagli.com`.
- **Role:** Dual — full-time application-security researcher at **Wiz**
  (cloud-security platform), and one of the world's top public
  bug-bounty hunters. Previously security engineer at Salesforce and
  Enso Security, after mandatory service in the IDF's C4I and Cyber
  Defense Directorate. Founder/CEO of **Shockwave.cloud**, an
  attack-surface-management SaaS spun out of his bounty automation.
- **Reputation:** Ranked top 10 HackerOne (2021), top 100 Bugcrowd
  all-time, "Million-Dollar Hacker" tier on H1. Travelled to seven
  international live-hacking events in a single year (2022 — Dubai,
  Paris, Denver, Austin, Las Vegas, Singapore, Barcelona).

## Focus areas

- Cloud / SaaS attack-surface management — recon-driven external
  exposure discovery.
- Server-side: auth-bypass, unauthenticated RCE in enterprise
  controllers (Aviatrix-class), exposed managed databases (DeepSeek
  ClickHouse).
- Modern AI-platform security: ChatGPT, DeepSeek, Base44, vibe-coding
  platforms.
- Supply-chain compromise of widely-used JS libraries (lottie-player,
  tj-actions/changed-files).
- Web cache deception and CDN-edge trust failures.
- Methodology: heavy automation + privileged-cred manual hunting +
  collaboration on LHEs.

## Online presence

- Personal site: [naglinagli.github.io](https://naglinagli.github.io/)
- Blog: [galnagli.com/blog](https://galnagli.com/blog)
- Wiz author page: [wiz.io/authors/gal-nagli](https://www.wiz.io/authors/gal-nagli)
- X / Twitter: [@galnagli](https://x.com/galnagli) (also `@naglinagli`)
- HackerOne: [hackerone.com/nagli](https://hackerone.com/nagli)
- Bugcrowd: [bugcrowd.com/nagli](https://bugcrowd.com/nagli)
- GitHub: [github.com/naglinagli](https://github.com/naglinagli)
- LinkedIn: [linkedin.com/in/galnagli](https://www.linkedin.com/in/galnagli)
- Company: [shockwave.cloud](https://shockwave.cloud)
- Bugcrowd Researcher Spotlight:
  [bugcrowd.com/blog/researcher-spotlight-nagli](https://www.bugcrowd.com/blog/researcher-spotlight-nagli/)
- YesWeHack profile interview:
  [yeswehack.com/community/collaboration-nagli-bug-bounty-hunter](https://www.yeswehack.com/community/collaboration-nagli-bug-bounty-hunter)

## Key research / posts

- **[ChatGPT account takeover via web cache deception (X thread)](https://x.com/galnagli/status/1639343866313601024)**
  (2023-03-24). Crafted `chat.openai.com/api/auth/session/<x>.css`
  caused Cloudflare to cache the JWT-bearing JSON session response as
  a public CSS asset. One click on the malicious URL exfiltrated
  `accessToken`, name, email, billing data. OpenAI patched within
  ~2 hours. Canonical modern web-cache-deception case study and the
  research that put Nagli on the AI-platform-security map.
- **[Wiz Research Uncovers Exposed DeepSeek Database Leaking Sensitive Information](https://www.wiz.io/blog/wiz-research-uncovers-exposed-deepseek-database-leak)**
  (2025-01-29, lead author). External-recon of ~30 DeepSeek
  subdomains turned up open ports 8123/9000 on
  `oauth2callback.deepseek.com` and `dev.deepseek.com`, exposing an
  unauthenticated ClickHouse with 1M+ log lines including plaintext
  chats and API keys. Cross-link: `../techniques/recon/` (port-on-
  unusual-subdomain pivot).
- **[Wiz Research Identifies Exploitation in the Wild of Aviatrix Controller (CVE-2024-50603)](https://www.wiz.io/blog/wiz-research-identifies-exploitation-in-the-wild-of-aviatrix-cve-2024-50603)**
  (2025-01-11, w/ Merav Bar, Gili Tikochinski, Shaked Tanchuma Yogev;
  CVE by Jakub Korepta / SecuRing). Unauth RCE in Aviatrix Controller
  PHP endpoints; in 65% of AWS environments the controller VM has
  lateral-movement paths to admin cloud-control-plane permissions.
  Observed XMRig + Sliver in-the-wild after Nuclei template dropped.
- **[Wiz Research Uncovers Critical Vulnerability in AI Vibe Coding platform Base44](https://www.wiz.io/blog/critical-vulnerability-base44)**
  (2025-07-29, lead author). SSO-protected private apps could be
  joined by any attacker who knew the public `app_id`, because the
  signup endpoint never enforced the SSO gate. Patched in 24h by Wix
  (post-acquisition). Signature shape: trivial auth-bypass on a
  hyped AI-builder platform.
- **[Supply chain attack on lottie-player](https://www.wiz.io/blog/lottie-player-supply-chain-attack)**
  (2024-10-31, w/ Merav Bar, Danielle Aminov). npm-token compromise
  pushed malicious 2.0.5–2.0.7 that injected fake Web3 wallet prompts
  on every consuming site; one confirmed victim lost 10 BTC
  (~US$723k). Library has ~94k weekly downloads / 4M lifetime uses.
- **[GitHub Action tj-actions/changed-files supply chain attack (CVE-2025-30066)](https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066)**
  (2025-03-15). Compromised popular GHA leaked repository secrets to
  workflow logs across thousands of repos.
- **[Wiz Research Discovers One in Five Organizations Exposed to Systemic Risks in Vibe-Coded Applications](https://www.wiz.io/blog/common-security-risks-in-vibe-coded-apps)**
  (2025-09-18). Cross-tenant data exposure, missing authz, and
  exposed secrets endemic to "vibe-coded" SaaS — generalises the
  Base44-class pattern across the AI-builder ecosystem.
- **[AI Agents vs Humans: Who Wins at Web Hacking in 2026?](https://www.wiz.io/blog/ai-agents-vs-humans-who-wins-at-web-hacking-in-2026)**
  (2026-01-29). Benchmark study comparing autonomous AI agents
  against human hunters on real web targets — sets up the Wiz Red
  Agent product line.
- **[Introducing the Wiz Red Agent — AI-Powered Attacker](https://www.wiz.io/blog/introducing-the-wiz-red-agent)**
  (2026-03-23). Context-aware AI attacker that continuously probes
  enterprise attack surface; productisation of Nagli's bounty
  automation thesis.
- **[Red Agent and Claude Opus: Securing Production Targets at Scale](https://www.wiz.io/blog/red-agent-claude-opus)**
  (2026-04-30). Wiz × Anthropic integration delivering continuous AI
  red-teaming on production targets.
- **[Hacking Moltbook: The AI Social Network Any Human Can Control](https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys)**
  (2026-02-02). Exposed DB on an AI social network leaked 35k emails
  + 1.5M API keys.
- **DEF CON 29 AppSec Village — "Vulnerability Inheritance: Finding
  bugs and scoring bounties through 3rd party integrations"** (2021).
  Methodology talk on chaining third-party SaaS integrations into
  primary-program impact.

### Open-source tooling

- **[Shockwave-OSS](https://github.com/naglinagli/Shockwave-OSS)** — open-source
  cut of the Shockwave attack-surface-management stack. 700+ stars.
  Cross-link: `../techniques/recon/`.
- **[CVE-2021-26832](https://github.com/naglinagli/CVE-2021-26832)** — XSS
  disclosure in Priority Enterprise Management System v8.00.

## CT podcast appearances

- [2023-04-13 Ep 15 — Gal Nagli — The Israeli Million-Dollar Hacker](../sources/podcasts/ct/20230413_P1prvdlP-jk_Gal_Nagli_-_The_Israeli_Million-Dollar_Hacker_Ep._15.en.vtt)
- [2023-12-14 Ep 49 — Getting Live Hacking Event Invites & Bug Bounty Collab with Nagli](../sources/podcasts/ct/20231214_TXZIPXKyNJc_Getting_Live_Hacking_Event_Invites_Bug_Bounty_Collab_with_Nagli_Ep._49.en.vtt)

## Notes

- **Signature shape:** external-recon-first, server-side payoff.
  Typical chain: ASM sweep across SaaS / cloud subdomains → unusual
  port on a "dev"/"oauth" host → unauthenticated admin surface
  (database, controller, signup endpoint) → cloud-control-plane or
  customer-data impact. Fewer giant chain writeups than Curry-style
  collabs; more single-primitive surgical disclosures with high blast
  radius.
- **AI-platform beat:** since the 2023 ChatGPT bug Nagli has been the
  go-to Wiz researcher for AI-vendor disclosures (DeepSeek, Base44,
  Moltbook, vibe-coded apps). Pattern: hype-driven AI startup ships
  with classic SaaS misconfigs (open DB, missing authz on signup,
  exposed secrets), Nagli's recon finds it in days.
- **LHE specialist:** one of CT's primary references for "how to get
  invited to live-hacking events" (Ep 49). Style emphasises pre-event
  prep, division-of-labour with co-hunters, and exploiting privileged
  creds the program hands out.
- **Israeli scene:** strong overlap with the Wiz / former-Unit-8200 /
  Tel-Aviv cloud-security cohort. Frequent Wiz co-authors: Merav Bar,
  Danielle Aminov, Gili Tikochinski, Shaked Tanchuma Yogev.
- **Methodology cues to copy:**
  - Always port-scan beyond 80/443 on every recon-discovered subdomain
    (DeepSeek ClickHouse only appeared on 8123/9000).
  - "Dev/staging/oauth" subdomains run looser auth than prod —
    pivot through them.
  - Public `app_id` / `tenant_id` values are not access control. Test
    every signup/join endpoint against the assumption that knowing
    the id ≠ being authorised.
  - Cache key includes path suffix on most CDNs — `.css`/`.js`
    suffixes on sensitive JSON endpoints remain a productive
    primitive years after the original ChatGPT bug.
- **Voice:** concise corporate-research tone in Wiz posts; sharper +
  thread-style on X. Personal-blog backlog (`galnagli.com/blog`) is
  thinner since the move to Wiz — most current research lives on
  `wiz.io/blog`.
- **Cross-link:** `../techniques/recon/` (recon-first methodology is
  the through-line). When a wiki technique page on "cache-key-suffix
  WCD" or "exposed ClickHouse on dev subdomain" is created, seed it
  from this dossier.

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/naglinagli-gh/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

<!-- sources:auto:start -->
## Ingested blog posts

- [disclosures](../sources/blogs/personal/naglinagli-gh/disclosures.md)
- [milestones](../sources/blogs/personal/naglinagli-gh/milestones.md)

<!-- sources:auto:end -->
