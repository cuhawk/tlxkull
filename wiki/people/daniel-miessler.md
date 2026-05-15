---
title: Daniel Miessler
slug: daniel-miessler
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [danielmiessler]
role: researcher
primary_focus: ai-security
tags: [person, role/researcher, focus/ai-security, focus/tooling, focus/wordlists, focus/thought-leadership]
inbound: []
---

## Identity

- **Real name:** Daniel Miessler
- **Primary handle:** `danielmiessler` (X/Twitter, GitHub, newsletter)
- **Role:** Independent security/AI researcher, writer, podcaster. Founder of Unsupervised Learning (newsletter + podcast). Bay Area; prior security-engineering roles at IOActive, HP Fortify, Robinhood. Tooling-side legacy is large — SecLists and RobotsDisallowed are still the de-facto wordlist defaults in web bug-bounty recon a decade after their initial publication.
- **Track record:** Long-form analyst rather than a vuln-disclosure hunter. SecLists has 70.9k stars on GitHub; Fabric (his AI-prompt CLI) has 41.7k. Newsletter has been running continuously for 500+ weekly editions. X following ~156k.

## Focus areas

- AI augmentation tooling (Fabric, Substrate, PAI/Personal AI Infrastructure)
- AI security thought-leadership (continuous threat modelling, AI + monitoring)
- Recon wordlists / payload corpora (SecLists, RobotsDisallowed)
- "Prompting as the moat" — minimal-RAG, large-context prompting philosophy
- Cybersecurity + national security + AI synthesis (newsletter beat)

## Online presence

- Site: [danielmiessler.com](https://danielmiessler.com)
- Blog: [danielmiessler.com/blog](https://danielmiessler.com/blog)
- Newsletter: [newsletter.danielmiessler.com](https://newsletter.danielmiessler.com/) — Unsupervised Learning, weekly, 500+ issues
- Podcast: [Unsupervised Learning on Apple Podcasts](https://podcasts.apple.com/us/podcast/unsupervised-learning/id1099711235) / [omny.fm/shows/unsupervised-learning](https://omny.fm/shows/unsupervised-learning)
- X / Twitter: [@DanielMiessler](https://x.com/danielmiessler)
- GitHub: [github.com/danielmiessler](https://github.com/danielmiessler)
- Projects index: [danielmiessler.com/projects](https://danielmiessler.com/projects/)
- Human 3.0: [human3.unsupervised-learning.com](https://human3.unsupervised-learning.com)

## Key research / posts

- **Fabric** ([github.com/danielmiessler/Fabric](https://github.com/danielmiessler/Fabric)) — open-source AI-prompt framework. Patterns = reusable markdown system prompts; Stitches = pattern chains. Go CLI + REST API + web UI; provider-agnostic (OpenAI, Anthropic, Gemini, Ollama, Azure). 41.7k stars. The reference implementation of the "prompts as code, version-controlled in markdown" pattern.
- **SecLists** ([github.com/danielmiessler/SecLists](https://github.com/danielmiessler/SecLists)) — the canonical pentesting wordlist collection (Discovery, Fuzzing, Payloads, Pattern-Matching, Web-Shells, Usernames, Passwords). 70.9k stars, MIT-licensed, packaged in Kali/BlackArch. Co-maintained with Ignacio Portal, g0tmi1k; Jason Haddix contributes direction. Release 2026.1 shipped 2026-03-23.
- **RobotsDisallowed** ([github.com/danielmiessler/RobotsDisallowed](https://github.com/danielmiessler/RobotsDisallowed)) — curated `Disallow:` paths scraped from Majestic Million top sites. `curated.txt` (~500 entries) is the default content-discovery seed in many recon pipelines. Unmaintained since 2019 but still useful.
- **AI is Mostly Prompting** ([danielmiessler.com/blog/ai-is-mostly-prompting](https://danielmiessler.com/blog/ai-is-mostly-prompting)) — May 2024. Thesis: ~90% of practical AI value comes from precise prompting, not RAG or fine-tuning. Large context + clear instructions wins. Signature take that informs Fabric's design.
- **AI's Predictable Path** ([danielmiessler.com/blog/ai-predictable-path-7-components-2024](https://danielmiessler.com/blog/ai-predictable-path-7-components-2024)) — 7-component forecast for AI's near-term shape; introduces "DAs" (digital assistants) as the dominant interface, building on his 2016 Real Internet of Things thesis.
- **The Real Internet of Things** ([danielmiessler.com/blog/the-real-internet-of-things](https://danielmiessler.com/blog/the-real-internet-of-things)) — 2016 essay/book. Reverse-engineers IoT from human desires (prediction, interface, evolution) rather than from devices.
- **Human 3.0 / The Problem with Human 2.0** ([danielmiessler.com/blog/human-3-creator-revolution](https://danielmiessler.com/blog/human-3-creator-revolution)) — argues post-AI humans split into builders vs displaced; the through-line of his current personal-AI work.
- **Substrate** ([github.com/danielmiessler/Substrate](https://github.com/danielmiessler/Substrate)) — open-source framework for "human understanding, meaning, and progress"; companion to Fabric on the values/identity side.
- **PAI — Personal AI Infrastructure** ([github.com/danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure)) — agentic-AI infra for individual users; the 2025-2026 evolution of the Fabric philosophy from CLI prompts to standing personal agents.
- **TELOS** ([github.com/danielmiessler/Telos](https://github.com/danielmiessler/Telos)) — framework for articulating personal identity/values/goals as context for AI assistants.
- **Unsupervised Learning newsletter — recent editions** ([NO. 527](https://newsletter.danielmiessler.com/p/unsupervised-learning-no-527), [NO. 526](https://newsletter.danielmiessler.com/p/unsupervised-learning-no-526)) — May 2026 coverage of supply-chain hacks, Shadow AI backdoors, Palo Alto portal vulns, AI-readiness in enterprises.

## CT podcast appearances

- [2023-06-22 Ep 24 — Daniel Miessler and Rez0 — Hacking with AI](../sources/podcasts/ct/20230622_Jt2d3XA07ig_Daniel_Miessler_and_Rez0_-_Hacking_with_AI_Ep._24.en.vtt)

## Notes

- **Tooling legacy >> live bug-hunting.** Daniel is not a contemporary bounty hunter. His relevance to this wiki is upstream: SecLists and RobotsDisallowed seed nearly every recon scan we run, and Fabric is the most popular reference design for the "AI prompts as a versioned library" pattern that informs how we organise our own Claude Code skills. Treat his dossier as a tooling-history page first, AI-commentary page second.
- **SecLists handoff.** Day-to-day maintenance is g0tmi1k + Ignacio Portal — Miessler is figurehead/owner now. Jason Haddix ([jason-haddix.md](./jason-haddix.md)) shapes the methodology side. If a wordlist gap shows up in our pipeline, the PR target is the SecLists repo, not Daniel directly.
- **Fabric philosophy parallels Claude Code skills.** Fabric Patterns (markdown system prompts, one per task, composable into Stitches) map almost 1:1 onto how this workspace structures `.claude/skills/<name>/SKILL.md`. Worth borrowing pattern names (`summarize`, `extract_wisdom`, `analyze_claims`, `create_threat_scenarios`) when designing new skills.
- **Newsletter as security-AI weathervane.** Unsupervised Learning is the single most-cited "AI + security trends" newsletter in the field. Useful for spotting macro shifts (e.g. the move from "AI feature = prompt injection target" to "AI infra = supply-chain target"), less useful for specific bug patterns.
- **Rez0 collab.** Listed as contributor on Joseph Thacker's [PIPE — Prompt Injection Primer for Engineers](https://github.com/jthack/PIPE) (see [rez0.md](./rez0.md)). The Ep 24 CT appearance with Joseph is the only formal joint output and pre-dates most of today's AI-security canon by 18+ months.
- **Style.** Long-form essayist; aesthetic-conscious site; signature shield emoji (Shield) on profiles. Light on technical PoCs in public; heavy on framing, taxonomy, and forward-looking essays. Cite him for *framing* a security/AI argument, cite Rez0/Rehberger for the *bug pattern*.
- **When to invoke this dossier:** when picking wordlists for content discovery (SecLists path map), when designing a new Claude Code skill (Fabric pattern naming conventions), or when needing a citable industry-voice on AI-security strategy in a writeup.
