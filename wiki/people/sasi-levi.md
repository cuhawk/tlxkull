---
title: Sasi Levi
slug: sasi-levi
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [sasi2103]
role: researcher
primary_focus: ai-security
tags: [person, role/researcher, focus/ai-security, focus/prompt-injection, focus/llm-agents, focus/data-exfiltration, focus/api-security]
inbound: []
---

# Sasi Levi

## Identity

- **Real name:** Sasi Levi.
- **Primary handle:** `sasi2103` (X).
- **Role:** Security Research Lead at Noma Security (Tel Aviv). Heads
  Noma Labs offensive research on agentic / RAG-based enterprise AI
  products.
- **Background:** Previously Group Manager, Cyber Security Research at
  Salt Security (progressed Senior Researcher → Research Lead → Group
  Manager). Earlier Senior Software Engineer / Tech Lead at
  ContexStream (SDN). BSc, Netanya Academic College.
- **OG hacker.** Top-10 PayPal bug bounty 2012; early Coinbase
  bug-reward in nascent-Bitcoin era (per CT Ep 152 intro).

## Focus areas

- Indirect prompt injection in production agentic AI (Gemini
  Enterprise, Vertex AI Search, Salesforce Agentforce, Docker Ask
  Gordon).
- Trust-boundary collapse between retrieved (RAG) data and model
  instructions in enterprise Workspace connectors (Gmail, Calendar,
  Docs, Sheets).
- Markdown / `<img>`-tag data exfiltration via auto-rendered remote
  resources; CSP bypass through expired-whitelisted-domain takeover.
- MCP server abuse — invisible-Unicode hidden instructions, metadata
  injection through Docker image labels.
- API security (legacy Salt Security focus) carrying into agentic-API
  surface.

## Online presence

- [X / Twitter — @sasi2103](https://x.com/sasi2103)
- [LinkedIn — Sasi Levi (Noma Security)](https://www.linkedin.com/in/sasi-levi-1665a73/)
- [Noma Security Labs](https://noma.security/noma-labs/)
- [Cobalt.io author page](https://www.cobalt.io/blog/author/sasi-levi)

## Key research / posts

- [GeminiJack — Hacking Google Gemini Enterprise with Indirect Prompt Injection](https://noma.security/noma-labs/geminijack/)
  (disclosed 2025-12) — Zero-click exfil of Workspace data (Gmail,
  Calendar, Docs, Sheets) via poisoned shared doc / calendar invite /
  email. RAG retrieval treats untrusted text as instructions; exfil via
  unfiltered `<img>` tag. Vertex AI Search was subsequently separated
  from Gemini Enterprise as part of the fix. Seeds technique pages on
  RAG-context poisoning + markdown image exfil.
- [GeminiJack blog post](https://noma.security/blog/geminijack-google-gemini-zero-click-vulnerability/)
  — Public writeup with four-phase attack (content poisoning → normal
  user query → RAG retrieval → exfil via image URL).
- [ForcedLeak — AI Agent risks exposed in Salesforce AgentForce](https://noma.security/blog/forcedleak-agent-risks-exposed-in-salesforce-agentforce/)
  (disclosed 2025-09-25, reported 2025-07-28, CVSS 9.4) — Web-to-Lead
  `Description` field (42 000 chars) as injection vector; CSP bypass by
  purchasing the expired-but-whitelisted `my-salesforce-cms.com` to
  create a trusted exfil channel. Canonical reference for
  expired-allowlisted-domain exfil pattern.
- [DockerDash — Two attack paths, one AI supply-chain crisis](https://noma.security/blog/dockerdash-two-attack-paths-one-ai-supply-chain-crisis/)
  (disclosed 2026-02-03, fixed in Docker Desktop 4.50.0) — Malicious
  metadata label in a Docker image hijacks Docker's *Ask Gordon* AI
  assistant; MCP Gateway doesn't separate informational metadata from
  runnable instructions. RCE on Cloud/CLI deployments, data exfil on
  Desktop. Seeds `techniques/llm/mcp-metadata-injection.md`.
- [Overview of Unserialization Vulnerability (Cobalt.io blog)](https://www.cobalt.io/blog/the-forgotten-unserialization-vulnerability)
  — Pre-AI-era post on Java/PHP deserialization; useful provenance for
  his classical-appsec foundations.
- [X thread — invisible-Unicode MCP smuggling](https://x.com/sasi2103/status/1915366925053349932)
  — Noma demo of a malicious MCP using invisible Unicode chars to hide
  instructions. Related to Rehberger's ASCII-smuggling line of work
  ([johann-rehberger](johann-rehberger.md)).

## CT podcast appearances

- [2025-12-11 Ep 152 — GeminiJack and Agentic Security with Sasi Levi](../sources/podcasts/ct/20251211_6JZsoJnqSxE_GeminiJack_and_Agentic_Security_with_Sasi_Levi_Ep._152.en.vtt)
  — Companion [HackerNotes write-up](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-152-geminijack-and-agentic-security-with-sasi-levi).

## Notes

- **Signature pattern.** Identify an agentic-AI product that ingests
  untrusted external content (shared Workspace docs, Salesforce
  Web-to-Lead, Docker image metadata, MCP tool output) and acts on it
  with broad privileges. Inject instructions that emit a side channel
  (markdown image, `<img>` tag, MCP tool call) to attacker-controlled
  infra. The class is identical to Rehberger's
  ([johann-rehberger](johann-rehberger.md)) markdown-image-exfil
  primitive applied to enterprise-RAG products instead of
  consumer chatbots.
- **Calendar > Email > Docs** as the injection surface ranking in CT
  Ep 152 — Calendar entries have very large free-text fields and full
  description exposure in retrieval context.
- **CSP-bypass primitive worth its own page:** expired
  whitelisted-domain takeover (ForcedLeak's `my-salesforce-cms.com`).
  Look for analogous expired-but-trusted domains in any agent's CSP
  egress allowlist.
- **Disclosure track record is strong.** Coordinated, vendor-confirmed
  fixes for Google, Salesforce, Docker within ~3-6 months each — good
  reference timeline when modelling expected agentic-AI bounty cycles.
- **Cross-refs:** pair with [johann-rehberger](johann-rehberger.md)
  (markdown-image exfil pioneer, ASCII-smuggling) for technique
  lineage; pair with rez0 / Joseph Thacker for agentic-AI red-team
  methodology.
- **RSAC 2026.** Sasi + Gal Moyal (Noma) scheduled to present an
  agentic-risk framework — watch for follow-up writeup.
