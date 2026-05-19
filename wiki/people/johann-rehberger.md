---
title: Johann Rehberger (wunderwuzzi23)
slug: johann-rehberger
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
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

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/embracethered/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

<!-- sources:auto:start -->
## Ingested blog posts

- [posts 2023 37c3 new important instructions](../sources/blogs/personal/embracethered/blog-posts-2023-37c3-new-important-instructions.md)
- [posts 2023 advanced plugin data exfiltration trickery](../sources/blogs/personal/embracethered/blog-posts-2023-advanced-plugin-data-exfiltration-trickery.md)
- [posts 2023 adversarial prompting tutorial and lab](../sources/blogs/personal/embracethered/blog-posts-2023-adversarial-prompting-tutorial-and-lab.md)
- [posts 2023 anthropic fixes claude data exfiltration via images](../sources/blogs/personal/embracethered/blog-posts-2023-anthropic-fixes-claude-data-exfiltration-via-images.md)
- [posts 2023 bing chat data exfiltration poc and fix](../sources/blogs/personal/embracethered/blog-posts-2023-bing-chat-data-exfiltration-poc-and-fix.md)
- [posts 2023 chatgpt chat with code plugin take down](../sources/blogs/personal/embracethered/blog-posts-2023-chatgpt-chat-with-code-plugin-take-down.md)
- [posts 2023 chatgpt cross plugin request forgery and prompt injection](../sources/blogs/personal/embracethered/blog-posts-2023-chatgpt-cross-plugin-request-forgery-and-prompt-injection.md)
- [posts 2023 chatgpt custom instruction post exploitation data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2023-chatgpt-custom-instruction-post-exploitation-data-exfiltration.md)
- [posts 2023 chatgpt plugin vulns chat with code](../sources/blogs/personal/embracethered/blog-posts-2023-chatgpt-plugin-vulns-chat-with-code.md)
- [posts 2023 chatgpt plugin youtube indirect prompt injection](../sources/blogs/personal/embracethered/blog-posts-2023-chatgpt-plugin-youtube-indirect-prompt-injection.md)
- [posts 2023 chatgpt vulns enter the matrix](../sources/blogs/personal/embracethered/blog-posts-2023-chatgpt-vulns-enter-the-matrix.md)
- [posts 2023 chatgpt webpilot data exfil via markdown injection](../sources/blogs/personal/embracethered/blog-posts-2023-chatgpt-webpilot-data-exfil-via-markdown-injection.md)
- [posts 2023 data exfiltration in azure openai playground fixed](../sources/blogs/personal/embracethered/blog-posts-2023-data-exfiltration-in-azure-openai-playground-fixed.md)
- [posts 2023 ekoparty prompt injection talk](../sources/blogs/personal/embracethered/blog-posts-2023-ekoparty-prompt-injection-talk.md)
- [posts 2023 google bard data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2023-google-bard-data-exfiltration.md)
- [posts 2023 google bard image to prompt injection](../sources/blogs/personal/embracethered/blog-posts-2023-google-bard-image-to-prompt-injection.md)
- [posts 2023 google docs ai scam](../sources/blogs/personal/embracethered/blog-posts-2023-google-docs-ai-scam.md)
- [posts 2023 google gcp generative ai studio data exfiltration fixed](../sources/blogs/personal/embracethered/blog-posts-2023-google-gcp-generative-ai-studio-data-exfiltration-fixed.md)
- [posts 2023 hitcon llm security presentation and trip report](../sources/blogs/personal/embracethered/blog-posts-2023-hitcon-llm-security-presentation-and-trip-report.md)
- [posts 2023 llm cost and dos threat](../sources/blogs/personal/embracethered/blog-posts-2023-llm-cost-and-dos-threat.md)
- [posts 2023 openai custom malware gpt](../sources/blogs/personal/embracethered/blog-posts-2023-openai-custom-malware-gpt.md)
- [posts 2023 openai data exfiltration first mitigations implemented](../sources/blogs/personal/embracethered/blog-posts-2023-openai-data-exfiltration-first-mitigations-implemented.md)
- [posts 2023 video data exfiltration vulns in llm applictions](../sources/blogs/personal/embracethered/blog-posts-2023-video-data-exfiltration-vulns-in-llm-applictions.md)
- [posts 2024 ascii smuggler updates](../sources/blogs/personal/embracethered/blog-posts-2024-ascii-smuggler-updates.md)
- [posts 2024 ascii smuggling and hidden prompt instructions](../sources/blogs/personal/embracethered/blog-posts-2024-ascii-smuggling-and-hidden-prompt-instructions.md)
- [posts 2024 aws amazon q fixes markdown rendering vulnerability](../sources/blogs/personal/embracethered/blog-posts-2024-aws-amazon-q-fixes-markdown-rendering-vulnerability.md)
- [posts 2024 chatgpt gpt 4o mini instruction hierarchie bypasses](../sources/blogs/personal/embracethered/blog-posts-2024-chatgpt-gpt-4o-mini-instruction-hierarchie-bypasses.md)
- [posts 2024 chatgpt hacking memories](../sources/blogs/personal/embracethered/blog-posts-2024-chatgpt-hacking-memories.md)
- [posts 2024 chatgpt macos app persistent data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2024-chatgpt-macos-app-persistent-data-exfiltration.md)
- [posts 2024 chatgpt persistent denial of service](../sources/blogs/personal/embracethered/blog-posts-2024-chatgpt-persistent-denial-of-service.md)
- [posts 2024 claude computer use c2 the zombais are coming](../sources/blogs/personal/embracethered/blog-posts-2024-claude-computer-use-c2-the-zombais-are-coming.md)
- [posts 2024 claude hidden prompt injection ascii smuggling](../sources/blogs/personal/embracethered/blog-posts-2024-claude-hidden-prompt-injection-ascii-smuggling.md)
- [posts 2024 cookie theft in 2024 and what todo](../sources/blogs/personal/embracethered/blog-posts-2024-cookie-theft-in-2024-and-what-todo.md)
- [posts 2024 copilot studio protect your copilots](../sources/blogs/personal/embracethered/blog-posts-2024-copilot-studio-protect-your-copilots.md)
- [posts 2024 deepseek ai prompt injection to xss and account takeover](../sources/blogs/personal/embracethered/blog-posts-2024-deepseek-ai-prompt-injection-to-xss-and-account-takeover.md)
- [posts 2024 exploring google bard vm](../sources/blogs/personal/embracethered/blog-posts-2024-exploring-google-bard-vm.md)
- [posts 2024 github copilot chat prompt injection data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2024-github-copilot-chat-prompt-injection-data-exfiltration.md)
- [posts 2024 google ai studio data exfiltration now fixed](../sources/blogs/personal/embracethered/blog-posts-2024-google-ai-studio-data-exfiltration-now-fixed.md)
- [posts 2024 google aistudio mass data exfil](../sources/blogs/personal/embracethered/blog-posts-2024-google-aistudio-mass-data-exfil.md)
- [posts 2024 google colab image render exfil](../sources/blogs/personal/embracethered/blog-posts-2024-google-colab-image-render-exfil.md)
- [posts 2024 google notebook ml data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2024-google-notebook-ml-data-exfiltration.md)
- [posts 2024 hackspacecon 2024](../sources/blogs/personal/embracethered/blog-posts-2024-hackspacecon-2024.md)
- [posts 2024 hiding and finding text with unicode tags](../sources/blogs/personal/embracethered/blog-posts-2024-hiding-and-finding-text-with-unicode-tags.md)
- [posts 2024 lack of isolation gpts code interpreter](../sources/blogs/personal/embracethered/blog-posts-2024-lack-of-isolation-gpts-code-interpreter.md)
- [posts 2024 llm apps automatic tool invocations](../sources/blogs/personal/embracethered/blog-posts-2024-llm-apps-automatic-tool-invocations.md)
- [posts 2024 llm context pollution and delayed automated tool invocation](../sources/blogs/personal/embracethered/blog-posts-2024-llm-context-pollution-and-delayed-automated-tool-invocation.md)
- [posts 2024 m365 copilot prompt injection tool invocation and data exfil using ascii smuggling](../sources/blogs/personal/embracethered/blog-posts-2024-m365-copilot-prompt-injection-tool-invocation-and-data-exfil-using-ascii-smuggling.md)
- [posts 2024 machine learning attack series keras backdoor model](../sources/blogs/personal/embracethered/blog-posts-2024-machine-learning-attack-series-keras-backdoor-model.md)
- [posts 2024 security probllms in xai grok](../sources/blogs/personal/embracethered/blog-posts-2024-security-probllms-in-xai-grok.md)
- [posts 2024 terminal dillmas prompt injection ansi sequences](../sources/blogs/personal/embracethered/blog-posts-2024-terminal-dillmas-prompt-injection-ansi-sequences.md)
- [posts 2024 the dangers of unfurling and what you can do about it](../sources/blogs/personal/embracethered/blog-posts-2024-the-dangers-of-unfurling-and-what-you-can-do-about-it.md)
- [posts 2024 trust no ai prompt injection along the cia security triad paper](../sources/blogs/personal/embracethered/blog-posts-2024-trust-no-ai-prompt-injection-along-the-cia-security-triad-paper.md)
- [posts 2024 whoami conditional prompt injection instructions](../sources/blogs/personal/embracethered/blog-posts-2024-whoami-conditional-prompt-injection-instructions.md)
- [posts 2025 39c3 agentic probllms exploiting computer use and coding agents](../sources/blogs/personal/embracethered/blog-posts-2025-39c3-agentic-probllms-exploiting-computer-use-and-coding-agents.md)
- [posts 2025 agenthopper a poc ai virus](../sources/blogs/personal/embracethered/blog-posts-2025-agenthopper-a-poc-ai-virus.md)
- [posts 2025 ai clickfix ttp claude](../sources/blogs/personal/embracethered/blog-posts-2025-ai-clickfix-ttp-claude.md)
- [posts 2025 amazon q developer data exfil via dns](../sources/blogs/personal/embracethered/blog-posts-2025-amazon-q-developer-data-exfil-via-dns.md)
- [posts 2025 amazon q developer interprets hidden instructions](../sources/blogs/personal/embracethered/blog-posts-2025-amazon-q-developer-interprets-hidden-instructions.md)
- [posts 2025 amazon q developer remote code execution](../sources/blogs/personal/embracethered/blog-posts-2025-amazon-q-developer-remote-code-execution.md)
- [posts 2025 amp agents that modify system configuration and escape](../sources/blogs/personal/embracethered/blog-posts-2025-amp-agents-that-modify-system-configuration-and-escape.md)
- [posts 2025 amp code fixed data exfiltration via images](../sources/blogs/personal/embracethered/blog-posts-2025-amp-code-fixed-data-exfiltration-via-images.md)
- [posts 2025 amp code fixed invisible prompt injection](../sources/blogs/personal/embracethered/blog-posts-2025-amp-code-fixed-invisible-prompt-injection.md)
- [posts 2025 announcement the month of ai bugs](../sources/blogs/personal/embracethered/blog-posts-2025-announcement-the-month-of-ai-bugs.md)
- [posts 2025 anthropic filesystem mcp server bypass](../sources/blogs/personal/embracethered/blog-posts-2025-anthropic-filesystem-mcp-server-bypass.md)
- [posts 2025 aws kiro aribtrary command execution with indirect prompt injection](../sources/blogs/personal/embracethered/blog-posts-2025-aws-kiro-aribtrary-command-execution-with-indirect-prompt-injection.md)
- [posts 2025 chatgpt chat history data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2025-chatgpt-chat-history-data-exfiltration.md)
- [posts 2025 chatgpt codex remote control zombai](../sources/blogs/personal/embracethered/blog-posts-2025-chatgpt-codex-remote-control-zombai.md)
- [posts 2025 chatgpt deep research connectors data spill and leaks](../sources/blogs/personal/embracethered/blog-posts-2025-chatgpt-deep-research-connectors-data-spill-and-leaks.md)
- [posts 2025 chatgpt how does chat history memory preferences work](../sources/blogs/personal/embracethered/blog-posts-2025-chatgpt-how-does-chat-history-memory-preferences-work.md)
- [posts 2025 chatgpt operator prompt injection exploits](../sources/blogs/personal/embracethered/blog-posts-2025-chatgpt-operator-prompt-injection-exploits.md)
- [posts 2025 claude abusing network access and anthropic api for data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2025-claude-abusing-network-access-and-anthropic-api-for-data-exfiltration.md)
- [posts 2025 claude code exfiltration via dns requests](../sources/blogs/personal/embracethered/blog-posts-2025-claude-code-exfiltration-via-dns-requests.md)
- [posts 2025 cline vulnerable to data exfiltration](../sources/blogs/personal/embracethered/blog-posts-2025-cline-vulnerable-to-data-exfiltration.md)
- [posts 2025 cross agent privilege escalation agents that free each other](../sources/blogs/personal/embracethered/blog-posts-2025-cross-agent-privilege-escalation-agents-that-free-each-other.md)
- [posts 2025 cursor data exfiltration with mermaid](../sources/blogs/personal/embracethered/blog-posts-2025-cursor-data-exfiltration-with-mermaid.md)
- [posts 2025 devin ai kill chain exposing ports](../sources/blogs/personal/embracethered/blog-posts-2025-devin-ai-kill-chain-exposing-ports.md)
- [posts 2025 devin can leak your secrets](../sources/blogs/personal/embracethered/blog-posts-2025-devin-can-leak-your-secrets.md)
- [posts 2025 devin i spent usd500 to hack devin](../sources/blogs/personal/embracethered/blog-posts-2025-devin-i-spent-usd500-to-hack-devin.md)
- [posts 2025 gemini memory persistence prompt injection](../sources/blogs/personal/embracethered/blog-posts-2025-gemini-memory-persistence-prompt-injection.md)
- [posts 2025 github copilot remote code execution via prompt injection](../sources/blogs/personal/embracethered/blog-posts-2025-github-copilot-remote-code-execution-via-prompt-injection.md)
- [posts 2025 github custom copilot instructions](../sources/blogs/personal/embracethered/blog-posts-2025-github-custom-copilot-instructions.md)
- [posts 2025 google jules invisible prompt injection](../sources/blogs/personal/embracethered/blog-posts-2025-google-jules-invisible-prompt-injection.md)
- [posts 2025 google jules remote code execution zombai](../sources/blogs/personal/embracethered/blog-posts-2025-google-jules-remote-code-execution-zombai.md)
- [posts 2025 google jules vulnerable to data exfiltration issues](../sources/blogs/personal/embracethered/blog-posts-2025-google-jules-vulnerable-to-data-exfiltration-issues.md)
- [posts 2025 m365 copilot image generation without authentication](../sources/blogs/personal/embracethered/blog-posts-2025-m365-copilot-image-generation-without-authentication.md)
- [posts 2025 manus ai kill chain expose port vs code server on internet](../sources/blogs/personal/embracethered/blog-posts-2025-manus-ai-kill-chain-expose-port-vs-code-server-on-internet.md)
- [posts 2025 mcp com server automate anything on windows](../sources/blogs/personal/embracethered/blog-posts-2025-mcp-com-server-automate-anything-on-windows.md)
- [posts 2025 model context protocol security risks and exploits](../sources/blogs/personal/embracethered/blog-posts-2025-model-context-protocol-security-risks-and-exploits.md)
- [posts 2025 openhands remote code execution zombai](../sources/blogs/personal/embracethered/blog-posts-2025-openhands-remote-code-execution-zombai.md)
- [posts 2025 openhands the lethal trifecta strikes again](../sources/blogs/personal/embracethered/blog-posts-2025-openhands-the-lethal-trifecta-strikes-again.md)
- [posts 2025 security advisory anthropic slack mcp server data leakage](../sources/blogs/personal/embracethered/blog-posts-2025-security-advisory-anthropic-slack-mcp-server-data-leakage.md)
- [posts 2025 security keeps google antigravity grounded](../sources/blogs/personal/embracethered/blog-posts-2025-security-keeps-google-antigravity-grounded.md)
- [posts 2025 sneaky bits and ascii smuggler](../sources/blogs/personal/embracethered/blog-posts-2025-sneaky-bits-and-ascii-smuggler.md)
- [posts 2025 spaiware and chatgpt command and control via prompt injection zombai](../sources/blogs/personal/embracethered/blog-posts-2025-spaiware-and-chatgpt-command-and-control-via-prompt-injection-zombai.md)
- [posts 2025 the normalization of deviance in ai](../sources/blogs/personal/embracethered/blog-posts-2025-the-normalization-of-deviance-in-ai.md)
- [posts 2025 windsurf dangers lack of security controls for mcp server tool invocation](../sources/blogs/personal/embracethered/blog-posts-2025-windsurf-dangers-lack-of-security-controls-for-mcp-server-tool-invocation.md)
- [posts 2025 windsurf data exfiltration vulnerabilities](../sources/blogs/personal/embracethered/blog-posts-2025-windsurf-data-exfiltration-vulnerabilities.md)
- [posts 2025 windsurf sneaking invisible instructions for prompt injection](../sources/blogs/personal/embracethered/blog-posts-2025-windsurf-sneaking-invisible-instructions-for-prompt-injection.md)
- [posts 2025 windsurf spaiware exploit persistent prompt injection](../sources/blogs/personal/embracethered/blog-posts-2025-windsurf-spaiware-exploit-persistent-prompt-injection.md)
- [posts 2025 wrapping up month of ai bugs](../sources/blogs/personal/embracethered/blog-posts-2025-wrapping-up-month-of-ai-bugs.md)
- [posts 2026 agent commander your agent works for me now](../sources/blogs/personal/embracethered/blog-posts-2026-agent-commander-your-agent-works-for-me-now.md)
- [posts 2026 breaking opus 4 7 with chatgpt](../sources/blogs/personal/embracethered/blog-posts-2026-breaking-opus-4-7-with-chatgpt.md)
- [posts 2026 data exfiltration mitigation paper by openai](../sources/blogs/personal/embracethered/blog-posts-2026-data-exfiltration-mitigation-paper-by-openai.md)
- [posts 2026 defcon talk copirate 365](../sources/blogs/personal/embracethered/blog-posts-2026-defcon-talk-copirate-365.md)
- [posts 2026 given enough agents all bugs become shallow](../sources/blogs/personal/embracethered/blog-posts-2026-given-enough-agents-all-bugs-become-shallow.md)
- [posts 2026 minting next auth nextjs auth cookies react2shell threat](../sources/blogs/personal/embracethered/blog-posts-2026-minting-next-auth-nextjs-auth-cookies-react2shell-threat.md)
- [posts 2026 scary agent skills](../sources/blogs/personal/embracethered/blog-posts-2026-scary-agent-skills.md)
- [posts](../sources/blogs/personal/embracethered/blog-posts.md)
- [blog](../sources/blogs/personal/embracethered/blog.md)

<!-- sources:auto:end -->
