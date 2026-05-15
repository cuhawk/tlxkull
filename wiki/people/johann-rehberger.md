---
title: Johann Rehberger (wunderwuzzi23)
slug: johann-rehberger
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [wunderwuzzi23, embracethered]
role: researcher
primary_focus: ai-security
tags: [person, role/researcher, focus/ai-security, focus/prompt-injection, focus/llm-agents, focus/data-exfiltration, focus/red-team]
inbound: []
---

# Johann Rehberger (wunderwuzzi23)

## Identity

- **Real name:** Johann Rehberger.
- **Primary handle:** `wunderwuzzi23` (X, GitHub); blog brand `Embrace the Red`.
- **Role:** AI red-team researcher / author. Formerly led red teams at
  Microsoft (Azure Data) and Uber. Holds an MSc in Computer Security
  from the University of Liverpool; previously instructor for ethical
  hacking at the University of Washington. Contributor to the MITRE
  ATT&CK framework.
- **Author of:** *Cybersecurity Attacks – Red Team Strategies*
  (Packt, 2020) — practical playbook for building and running an
  internal red team program.

## Focus areas

- Indirect prompt injection in production LLM products (ChatGPT,
  Copilot, Bard/Gemini, Claude, Devin).
- AI agent hijacking — turning chat / coding agents into C2 nodes
  ("ZombAIs", AgentHopper, Agent Commander).
- LLM data exfiltration channels (markdown image rendering, URL
  preview, DNS, file/network APIs).
- Persistent prompt injection via long-term memory and connector
  state ("SpAIware").
- Classical offensive tradecraft: AAD / ROPC / MFA bypass, phishing
  proxies, malicious package supply-chain.

## Online presence

- [Blog — Embrace the Red](https://embracethered.com/blog/)
- [X / Twitter — @wunderwuzzi23](https://x.com/wunderwuzzi23)
- [GitHub — wunderwuzzi23](https://github.com/wunderwuzzi23)
- [LinkedIn](https://www.linkedin.com/in/johannrehberger/)
- [HITCON 2023 talk slides — Indirect Prompt Injections](https://embracethered.com/blog/downloads/HITCON_CMT_Indirect_Prompt_Injections_2023_v1.0.pdf)
- [YouTube talk — Indirect Prompt Injections in the Wild](https://www.youtube.com/watch?v=ADHAokjniE4)
- Book — *Cybersecurity Attacks – Red Team Strategies* (Packt, ISBN
  978-1-83882-886-8).

## Key research / posts

- [Hacking Google Bard — From Prompt Injection to Data Exfiltration](https://embracethered.com/blog/posts/2023/google-bard-data-exfiltration/)
  (2023) — Indirect prompt injection via a shared Google Doc renders a
  markdown image whose URL leaks conversation data; bypasses Google's
  CSP through `script.google.com` (Apps Script). Canonical "markdown
  image exfil" primitive — seed for any future
  `../techniques/llm/markdown-image-exfil.md`.
- [ChatGPT: Hacking Memories with Prompt Injection](https://embracethered.com/blog/posts/2024/chatgpt-hacking-memories/)
  — Indirect prompt injection through connectors / image uploads /
  browsing writes attacker-controlled memories that persist across
  sessions. Closed by OpenAI as "Model Safety Issue", not a security
  bug. Seed for `../techniques/llm/persistent-memory-injection.md`.
- [Spyware Injection Into ChatGPT's Long-Term Memory (SpAIware)](https://embracethered.com/blog/posts/2024/chatgpt-macos-app-persistent-data-exfiltration/)
  — Persistent macOS ChatGPT exfiltration: injected memory keeps
  leaking every future chat to attacker endpoint.
- [Exfiltrating Your ChatGPT Chat History and Memories With Prompt Injection](https://embracethered.com/blog/posts/2025/chatgpt-chat-history-data-exfiltration/)
  (2025) — Newer exfil channel after OpenAI's image-rendering fixes.
- [ChatGPT Operator: Prompt Injection Exploits & Defenses](https://embracethered.com/blog/posts/2025/chatgpt-operator-prompt-injection-exploits/)
  — Attacks against OpenAI's agentic browser Operator.
- [ZombAIs: From Prompt Injection to C2 with Claude Computer Use](https://embracethered.com/blog/posts/2024/claude-computer-use-c2-the-zombais-are-coming/)
  — Indirect prompt injection turns Claude's Computer Use into a
  C2-controlled zombie that downloads/executes a payload.
- [AgentHopper: An AI Virus](https://embracethered.com/blog/posts/2025/agenthopper-a-poc-ai-virus/)
  — PoC self-propagating prompt-injection malware that hops between
  AI agents.
- [Agent Commander: Promptware-Powered Command and Control](https://embracethered.com/blog/posts/2026/agent-commander-your-agent-works-for-me-now/)
  — Generalised C2 framework for hijacked agents.
- [GitHub Copilot: Remote Code Execution via Prompt Injection (CVE-2025-53773)](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/)
  — Copilot tricked into editing its own config to flip
  approval-required off, yielding silent command execution.
- [GitHub Copilot Chat: From Prompt Injection to Data Exfiltration](https://embracethered.com/blog/posts/2024/github-copilot-chat-prompt-injection-data-exfiltration/)
  — Indirect prompt injection through source / issues leaks secrets
  out of Copilot Chat.
- [Claude Code: Data Exfiltration with DNS (CVE-2025-55284)](https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/)
  — DNS as the side channel when HTTP egress is blocked.
- [Claude Pirate: Abusing Anthropic's File API For Data Exfiltration](https://embracethered.com/blog/posts/2025/claude-abusing-network-access-and-anthropic-api-for-data-exfiltration/)
  — Uploads exfil content through Anthropic's own File API.
- [How Deep Research Agents Can Leak Your Data](https://embracethered.com/blog/posts/2025/chatgpt-deep-research-connectors-data-spill-and-leaks/)
  — Connector-driven leak surface in agentic deep-research products.
- [Hidden Prompt Injections with Anthropic Claude (ASCII Smuggling)](https://embracethered.com/blog/posts/2024/claude-hidden-prompt-injection-ascii-smuggling/)
  — Unicode tag chars carry invisible instructions past the UI.
- [Sorry, ChatGPT Is Under Maintenance — Persistent DoS via Prompt Injection](https://embracethered.com/blog/posts/2024/chatgpt-persistent-denial-of-service/)
  — Memory-persistent DoS: an injected instruction keeps tripping
  ChatGPT's safety stop on every future turn.

### Open-source tooling

- [yolo-ai-cmdbot](https://github.com/wunderwuzzi23/yolo-ai-cmdbot) —
  Natural-language → shell command bot; demo of the "AI runs my
  terminal" trust surface. (~220 stars)
- [mlattacks](https://github.com/wunderwuzzi23/mlattacks) — Machine
  Learning Attack Series notebooks.
- [ropci](https://github.com/wunderwuzzi23/ropci) — AAD ROPC / MFA
  bypass testing tool.
- [KoiPhish](https://github.com/wunderwuzzi23/KoiPhish) — Phishing
  reverse proxy.
- [this_is_fine_wuzzi](https://github.com/wunderwuzzi23/this_is_fine_wuzzi)
  — PoC malicious Python package that executes on `pip install`.
- [scratch](https://github.com/wunderwuzzi23/scratch) — Public scripts,
  prompts, demo payloads.

## CT podcast appearances

- [2024-12-12 Ep 101 — AI Attack Vectors — CTBB Hijacked — Rez0 and Johann](../sources/podcasts/ct/20241212_c3sVyof96lo_AI_Attack_Vectors_-_CTBB_Hijacked_-_Rez0___and_Johann_Ep._101.en.vtt)

## Notes

- **Pioneer of indirect prompt injection in production LLM products.**
  The 2023 Bard markdown-image exfil is one of the earliest end-to-end
  PoCs of LLM data exfil at a major vendor and seeded most of the
  vocabulary the field now uses ("indirect prompt injection",
  "image-render exfil", "memory poisoning").
- **Signature pattern:** find an untrusted input channel into a
  production LLM (shared doc, connector, repo file, image, URL
  preview), inject instructions that cause the agent to emit a side
  channel (markdown image, URL, DNS lookup, tool call, file upload),
  exfil chat history / secrets through that channel. Variations
  enumerated across 50+ blog posts.
- **August 2025 "Month of AI Bugs":** one disclosed AI-platform bug
  per day for a month; reinforced that virtually every shipped
  agentic product has indirect prompt injection somewhere. Useful
  index post when seeding `../techniques/llm/`.
- **Vendor disclosure stance:** vendors (OpenAI, Anthropic, Google,
  GitHub) frequently triage his prompt-injection reports as "model
  safety", not security. Worth noting when modeling expected payout
  / disclosure friction for any AI-bounty engagement.
- **Cross-refs:** pair with [rez0](rez0.md) (Joseph Thacker) — they
  cohosted CT Ep 101 and overlap on AI red-team tradecraft. Pair
  with [daniel-miessler](daniel-miessler.md) (CT Ep 24,
  "Hacking with AI") for the methodology side.
- **Book takeaway:** *Red Team Strategies* (2020) predates his AI
  focus and is about building internal red teams — useful only if a
  target engagement requires modeling defender posture, not for
  prompt-injection technique.
