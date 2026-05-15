---
title: Joseph Thacker (rez0)
slug: rez0
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [rez0__, rez0, jthack, rez0corp]
role: researcher
primary_focus: ai-security
tags: [person, role/researcher, role/host, focus/ai-security, focus/prompt-injection, focus/agent-security, focus/saas]
inbound: []
---

## Identity

- **Real name:** Joseph Thacker
- **Primary handle:** `rez0__` (X/Twitter), `jthack` (GitHub), `rez0corp` (LinkedIn)
- **Role:** Principal AI Engineer / Senior Offensive Security Engineer at AppOmni (SaaS security). Independent AI-security researcher and bug-bounty hunter. Co-host of the Critical Thinking — Bug Bounty Podcast AI mini-series ("Vulnus Ex Machina"). Recurring CT co-host on AI-themed episodes.
- **Track record:** 1,000+ vulnerabilities submitted/collaborated on across Fortune 500 programs (per AppOmni / HackerOne profile). Among the earliest hunters to systematise prompt-injection-as-bug-bounty methodology (2023 onwards).

## Focus areas

- AI application security — prompt injection (direct + indirect) in production LLMs
- AI agent security — tool-use abuse, agent jailbreaks, hackbots
- Bug-bounty methodology for AI features (recon, taxonomy of impact)
- SaaS security (day job at AppOmni)
- AI-assisted offensive tooling (Claude Code skills, hackbots, ffuf+AI wrappers)

## Online presence

- Blog: [josephthacker.com](https://josephthacker.com)
- X / Twitter: [@rez0__](https://x.com/rez0__)
- GitHub: [github.com/jthack](https://github.com/jthack)
- LinkedIn: [in/josephthacker](https://www.linkedin.com/in/josephthacker/)
- Company: [appomni.com](https://appomni.com/) — see [AppOmni author posts](https://appomni.com/blog/)
- Wiz contributor: [wiz.io/authors/joseph-thacker](https://www.wiz.io/authors/joseph-thacker)
- Talk: [The Promptfather — An Offer AI Can't Refuse (Bugcrowd LevelUp)](https://live-bug-crowd.pantheonsite.io/resources/levelup/the-promptfather-an-offer-ai-cant-refuse/)

## Key research / posts

- **How to Hack AI Agents and Applications** ([josephthacker.com/hacking/2025/02/25/how-to-hack-ai-apps.html](https://josephthacker.com/hacking/2025/02/25/how-to-hack-ai-apps.html)) — the canonical methodology post. Splits AI vulns into (a) prompt injection as the bug itself, (b) prompt injection as a delivery vector for classical web bugs (XSS, SQLi, IDOR, RCE), and (c) AI-native bugs (markdown-image exfil, ANSI-escape attacks, multimodal injection, RAG leakage, wallet-drain via no-rate-limit). Seed of the wiki's AI-hacking methodology.
- **PIPE — Prompt Injection Primer for Engineers** ([github.com/jthack/PIPE](https://github.com/jthack/PIPE)) — co-authored with input from Justin Gardner, Daniel Miessler, Hrishi. The engineering-side reference for prompt-injection defenses; 580+ stars.
- **ffufai — AI-powered ffuf wrapper** ([github.com/jthack/ffufai](https://github.com/jthack/ffufai)) — LLM picks fuzz dictionaries from endpoint context. 770+ stars; the prototype "small AI tool wrapping a classic recon tool" pattern he keeps iterating on.
- **The Agentic Hacking Era: Ramblings and a Tool** ([josephthacker.com/hacking/2026/03/06/the-agentic-hacking-era.html](https://josephthacker.com/hacking/2026/03/06/the-agentic-hacking-era.html)) — argues Claude Code + agentic loops are now the primary bug-hunting interface; releases a Caido skill that lets agents create replay sessions, manage findings, and pull auth tokens directly. 15 H/Crit bugs in 6 weeks claimed.
- **Claude Code Hacking Skills** ([josephthacker.com/hacking/2026/03/20/claude-code-hacking-skills.html](https://josephthacker.com/hacking/2026/03/20/claude-code-hacking-skills.html)) — companion video walking through Claude Code skills for hacking workflows.
- **AI's Impact on Software and Bug Bounty** ([josephthacker.com/ai/2026/02/24/ai-s-impact-on-bug-bounty.html](https://josephthacker.com/ai/2026/02/24/ai-s-impact-on-bug-bounty.html)) — 2026 state-of-the-field essay on how AI shifts the bounty economics.
- **Hacking an AI Children's Toy: Remote Access to Every Conversation** ([josephthacker.com/hacking/2026/01/29/bondu-smart-toy-vulnerability.html](https://josephthacker.com/hacking/2026/01/29/bondu-smart-toy-vulnerability.html)) — Bondu smart-toy disclosure; IoT-meets-LLM case study.
- **From Theory to Reality: Explaining the Best Prompt Injection Proof of Concept** (May 2023) — early viral PoC writeup; the markdown-image exfiltration via indirect prompt injection pattern that seeded much subsequent work.
- **Invisible Unicode prompt-injection thread** ([x.com/rez0__/status/1745545813512663203](https://x.com/rez0__/status/1745545813512663203)) — flagged invisible-character tag smuggling as "biggest breakthrough since prompt injection itself"; widely cited follow-up.
- **AppOmni — Lessons Learned from Black Hat 2023** ([appomni.com/blog/lessons-learned-from-blackhat2023-on-saas-identities-ai](https://appomni.com/blog/lessons-learned-from-blackhat2023-on-saas-identities-ai/)) — house-style summary of the "biggest risk is exposing LLMs to sensitive data or state-changing actions" thesis.
- **All About Hackbots: AI Agents That Hack** (LinkedIn long-form) — early framing of hackbots as a product category, pre-dating most commercial entrants.

## CT podcast appearances

- [2023-06-22 Ep 24 — AI + Hacking with Daniel Miessler and Rez0](../sources/podcasts/ct/20230622_Jt2d3XA07ig_Daniel_Miessler_and_Rez0_-_Hacking_with_AI_Ep._24.en.vtt)
- [2024-12-12 Ep 101 — AI Attack Vectors / CTBB Hijacked — Rez0 and Johann](../sources/podcasts/ct/20241212_c3sVyof96lo_AI_Attack_Vectors_-_CTBB_Hijacked_-_Rez0___and_Johann_Ep._101.en.vtt)
- [2025-04-03 Ep 117 — Vulnus Ex Machina — AI Hacking Part 1](../sources/podcasts/ct/20250403__0tOgk8Xbiw_Vulnus_Ex_Machina_-_AI_Hacking_Part_1_Ep._117.en.vtt)
- [2025-05-22 Ep 123 — Vulnus Ex Machina — AI Hacking Part 2](../sources/podcasts/ct/20250522_krEzRUG8eWo_Vulnus_Ex_Machina_-_AI_Hacking_Part_2_Ep.123.en.vtt)
- [2025-06-12 Ep 126 — Vulnus Ex Machina — AI Hacking Part 3](../sources/podcasts/ct/20250612_ghoVKhz_s_A_Vulnus_Ex_Machina_-_AI_Hacking_Part_3_Ep._126.en.vtt)

Vulnus Ex Machina ("Vulnerability in the Machine") is the 3-part CT mini-series he authored: Part 1 = AI-feature recon and identifying attack surface; Part 2 = mastering prompt injection, taxonomy of impact, triggering traditional vulns through LLMs; Part 3 = showcase of his own AI bounty findings with payouts.

## Notes

- **AI-hacking subspecialty.** Among the small first-wave (~2023) of bounty hunters who built a *methodology* around LLM features rather than treating prompt injection as a one-shot curiosity. The "prompt injection is a delivery mechanism, not the bug" framing is his signature contribution to the field.
- **Co-host pattern.** Effectively the AI-track co-host for Critical Thinking. Justin Gardner ([justin-gardner.md](./justin-gardner.md)) hosts the main client-side line; Joseph hosts AI episodes. Frequent collab with Johann Rehberger (`wunderwuzzi`) on AI-vector episodes (e.g. Ep 101).
- **Tooling philosophy.** Strong builder — every blog post tends to ship a tool (ffufai, PIPE, ffuf_claude_skill, cewlai, claude-goal, Caido agent skill). Pattern: take a classic recon/exploit tool, wrap with an LLM, release as small focused repo.
- **Twitter-first content cadence.** Long-form on `josephthacker.com` is rarer than X/Twitter threads — many of his sharpest observations (invisible-Unicode injection, "AI models developing spidey-sense", indirect-injection via texts/emails being a disaster) appear first as `@rez0__` threads. Treat his X feed as a primary research source, not a promo channel.
- **Day-job lens.** AppOmni is SaaS-security focused, so his framing often pulls in SaaS-identity, OAuth-to-LLM, and tool-call-abuse angles that pure-research AI-safety folks miss. See AppOmni blog for the enterprise-flavored writeups; josephthacker.com for the bug-bounty-flavored ones.
- **Collab graph.** Daniel Miessler (UL NO — newsletter/AI), Johann Rehberger (`wunderwuzzi`, Embrace the Red), Justin Gardner (CT co-host), Hrishi (PIPE contributor).
- **When to invoke this dossier:** any time a target ships an LLM feature, a RAG endpoint, an agent with tool-use, or a markdown-rendering AI chat. His methodology post is the default starting checklist before custom recon.
