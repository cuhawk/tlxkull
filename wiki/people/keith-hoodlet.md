---
title: Keith Hoodlet
slug: keith-hoodlet
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [andmyhacks, securingdev]
role: researcher
primary_focus: ai-bias
tags: [person, role/researcher, focus/ai-bias, focus/program-design, focus/appsec, focus/devsecops]
inbound: []
---

# Keith Hoodlet

## Identity

- Real name: Keith Hoodlet
- Primary handles: `andMYhacks` (Bugcrowd / hunter handle, 2018 MVP), `securingdev` (current pro handle)
- Role: researcher (AI/ML & application security)
- Current position: Director of Security Research at **1Password** (per current GitHub bio). Previously Engineering Director, AI/ML & Application Security Assurance at **Trail of Bits**.
- Prior: founded the AppSec / DevSecOps program at **Thermo Fisher Scientific**; Trust & Security Engineer at **Bugcrowd**; Customer Success Engineer at **Rapid7**; Code Security Engineer at **Veracode**.
- Credentials: OSCP, OSWA. Bugcrowd Top 100 + MVP (2018). Named "50 Influential DevSecOps Professionals on Peerlyst" (2019).
- Education: dual Computer Science + Psychology — the psychology background is the explicit hook for his bias-bounty methodology.

## Focus areas

- AI bias bounty methodology (DoD CDAO winner, see below)
- AI/ML supply-chain security (pickle files, polyglot models, dependency risk)
- Application security program design + DevSecOps maturity
- Vulnerability disclosure program (VDP) design — when a VDP vs paid bounty is appropriate
- Static analysis / "LLMs as static analyzers" framing

## Online presence

- Blog: [securing.dev](https://securing.dev) — "Pseudo-random musings on Security, Software Development, and Life"
- About page: [securing.dev/about](https://securing.dev/about/)
- LinkedIn: [linkedin.com/in/securingdev](https://www.linkedin.com/in/securingdev/)
- GitHub (current): [github.com/securingdev](https://github.com/securingdev)
- GitHub (hunter handle): [github.com/andMYhacks](https://github.com/andMYhacks)
- Mastodon: [@securingdev@infosec.exchange](https://infosec.exchange/@securingdev)
- SC Media contributor page: [scworld.com/contributor/keith-hoodlet](https://www.scworld.com/contributor/keith-hoodlet)
- Bugcrowd hunter profile: [bugcrowd.com/h/author/keith-hoodletbugcrowd-com](https://bugcrowd.com/h/author/keith-hoodletbugcrowd-com)
- Trail of Bits author page: [blog.trailofbits.com/authors/keith-hoodlet](https://blog.trailofbits.com/authors/keith-hoodlet/)
- Note: he does not (publicly) maintain an active X/Twitter handle as primary channel; the X handle `andMYhacks` referenced in the task brief redirects most public conversation to Mastodon.

## Key research / posts

- **[Hacking AI Bias while Hacking Human Bias](https://securing.dev/posts/hacking-ai-bias/)** (2024-04-19) — write-up of his #1 finish in the **U.S. DoD CDAO Bias Bounty** (the first-ever DoD AI bias bounty, run via Bugcrowd + ConductorAI, [announcement](https://www.defense.gov/News/Releases/Release/Article/3659519/cdao-launches-first-dod-ai-bias-bounty-focused-on-unknown-risks-in-llms/)). Core method: (1) use a second LLM to generate "conceivable but notional DoD use case" scenarios, (2) hold 3-5 variables constant and swap one independent variable at a time, scientific-method style, (3) test each prompt 5-10 times for reproducibility (he demonstrated patterns with <0.06% random probability), (4) record video evidence so triagers can reconstruct markdown fidelity. Findings included gender role-play bias (male personas for management, female for HR/ethics), age-based discrimination, and name-based discrimination.
- **[On AI, Security, Reasoning, and Bias](https://securing.dev/posts/ai-security-reasoning-and-bias/)** (2025-03-10) — argues LLMs are closer to **static analysis** than to fuzzing: pattern matching over training-data distribution, not genuine reasoning. RLHF reshapes outputs without removing the underlying training-data bias. Useful framing for AI red-teamers.
- **[Critical Thinking in the age of AI](https://securing.dev/posts/critical-thinking-in-the-age-of-ai/)** (2025-04-24) — workflow piece on using AI tools without atrophying your own analysis.
- **[Vibe Coding with Devcontainers in the CLI](https://securing.dev/posts/vibe-coding-with-devcontainers/)** (2025-09-09) — pragmatic devcontainer setup for AI-assisted coding, security-aware.
- **[Financial vs. Technological Bubbles](https://securing.dev/posts/financial-vs-technological-bubbles/)** (2025-10-23) — AI hype-cycle take.
- **[AI, Addiction, Burnout, and the Time Value of Money](https://securing.dev/posts/ai-and-the-time-value-of-money/)** (2026-02-24) — most recent essay.
- **[Attack Driven Development](https://www.youtube.com/watch?v=dOm_hWk1OFU)** (InfoSec World 2018) — early Bugcrowd-era talk; AppSec-from-the-attacker-lens framing. [Press release](https://www.bugcrowd.com/press-release/bugcrowds-keith-hoodlet-to-present-attack-driven-development-at-infosec-world-2018/), [slides](https://www.slideshare.net/FrancoisRaynaud/attack-driven-development-by-keith-hoodlet).
- **Application Security Weekly podcast** — co-founded with Paul Asadoorian; hosted eps 0-55. Recent guest appearances:
  - [ASW #284 — Hacking AI Bias with Human Techniques](https://www.scworld.com/podcast-episode/3133-ai-hype-security-oh-my-hacking-ai-bias-caleb-sima-keith-hoodlet-asw-284)
  - [ASW #376 — Developing the Skills Needed for Modern Software Development](https://www.scworld.com/podcast-segment/14407-developing-the-skills-needed-for-modern-software-development-keith-hoodlet-ron-rasin-shashwat-sehgal-asw-376)
- **[From Pickle Files to Polyglots: Hidden Risks in AI Supply Chains](https://mlsecops.com/podcast/from-pickle-files-to-polyglots-hidden-risks-in-ai-supply-chains)** — MLSecOps podcast appearance from his Trail of Bits tenure.
- **InfoSec Mentors Project** (re-launched 2017, archived 2020) — 500+ users, 165+ mentees connected. His program-design fingerprint shows up in this too.

## CT podcast appearances

- [2024-05-16 Ep 71 — More VDP Chats & AI Bias Bounty Strats with Keith Hoodlet](../sources/podcasts/ct/20240516_rAKe3iGUoeM_More_VDP_Chats_AI_Bias_Bounty_Strats_with_Keith_Hoodlet_Ep._71.en.vtt) — when a VDP is the right call vs paid bounty, scaling AppSec in large orgs, and the AI bias bounty methodology applied to chatbot role-play. HackerNotes recap: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-71-vdp-chats-ai-bias-bounty-strats-keith-hoodlet](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-71-vdp-chats-ai-bias-bounty-strats-keith-hoodlet). Episode page: [criticalthinkingpodcast.io/episode-71-more-vdp-chats-ai-bias-bounty-strats-with-keith-hoodlet](https://www.criticalthinkingpodcast.io/episode-71-more-vdp-chats-ai-bias-bounty-strats-with-keith-hoodlet/). YouTube: [rAKe3iGUoeM](https://www.youtube.com/watch?v=rAKe3iGUoeM).
- [2024-05-22 Ep 72 — THIS is how to prove the impact of AI bias](../sources/podcasts/ct/20240522_ltiMtAdLYno_THIS_is_how_to_prove_the_impact_of_AI_bias.en.vtt) — direct continuation: proving statistical significance of a bias finding (reproducibility runs, variable isolation), and how triagers should evaluate impact for a class of finding that lacks a CVSS analog.

## Notes

- **Signature move:** apply human cognitive-bias frameworks (his psychology background) to surface LLM biases that other testers miss. He treats RLHF-tuned LLMs as systems with training-data priors, and his variable-isolation protocol is essentially psychology's experimental method ported to prompt engineering.
- **Why he matters for us:** the AI-bias-bounty category is still small, the methodology is mostly his, and any future engagement on an AI/ML scope (chatbots, decision-support LLMs, content moderation models) should pull his variable-isolation + reproducibility playbook before testing. Cross-link any AI-bias finding to this page.
- **Program-design angle:** ex-Bugcrowd Trust & Security Engineer + founder of Thermo Fisher's AppSec program. When evaluating whether a target's bug-bounty program is well-designed (scope quality, payout sanity, VDP vs paid choice), his Ep 71 commentary is the canonical CT reference.
- **Career arc:** Veracode → Rapid7 → Bugcrowd → Thermo Fisher → GitHub → Trail of Bits → 1Password. The 1Password move (per current GitHub bio) is the freshest data point; older sources still list Trail of Bits. Update if confirmed via a public announcement.
- **Caveats:** he is primarily a researcher / program-designer / podcast voice — not a high-volume H1/Bugcrowd submitter today. His bounty cred peaked with the DoD CDAO win, not steady-state hunting.
- **Related wiki pages to seed:** `wiki/techniques/ai-bias/` (variable-isolation protocol, reproducibility-run threshold), `wiki/tools/bugcrowd/program-design.md`, and a future page on VDP-vs-paid decision criteria all naturally cross-link here.
