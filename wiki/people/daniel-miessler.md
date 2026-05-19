---
title: Daniel Miessler
slug: daniel-miessler
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
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

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/daniel-miessler/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

<!-- sources:auto:start -->
## Ingested blog posts

- [_index](../sources/blogs/personal/daniel-miessler/_index.md)
- [2016 oldest political story](../sources/blogs/personal/daniel-miessler/blog-2016-oldest-political-story.md)
- [30 books that i will re read for the rest of my life](../sources/blogs/personal/daniel-miessler/blog-30-books-that-i-will-re-read-for-the-rest-of-my-life.md)
- [a quick thought on crypto](../sources/blogs/personal/daniel-miessler/blog-a-quick-thought-on-crypto.md)
- [ai and synthetic mind creation](../sources/blogs/personal/daniel-miessler/blog-ai-and-synthetic-mind-creation.md)
- [ai layoffs arent about ai](../sources/blogs/personal/daniel-miessler/blog-ai-layoffs-arent-about-ai.md)
- [ai unmasked our work as scaffolding](../sources/blogs/personal/daniel-miessler/blog-ai-unmasked-our-work-as-scaffolding.md)
- [apple vision pro first impressions](../sources/blogs/personal/daniel-miessler/blog-apple-vision-pro-first-impressions.md)
- [apples ai jump](../sources/blogs/personal/daniel-miessler/blog-apples-ai-jump.md)
- [chinas new dystopian citizen rating system](../sources/blogs/personal/daniel-miessler/blog-chinas-new-dystopian-citizen-rating-system.md)
- [concise transparent communication as the primary metric of competency](../sources/blogs/personal/daniel-miessler/blog-concise-transparent-communication-as-the-primary-metric-of-competency.md)
- [economy failing exxon making record profit](../sources/blogs/personal/daniel-miessler/blog-economy-failing-exxon-making-record-profit.md)
- [effort vs outcome](../sources/blogs/personal/daniel-miessler/blog-effort-vs-outcome.md)
- [exit rate vs bounce rate](../sources/blogs/personal/daniel-miessler/blog-exit-rate-vs-bounce-rate.md)
- [faceid removes an authentication step except for apple pay](../sources/blogs/personal/daniel-miessler/blog-faceid-removes-an-authentication-step-except-for-apple-pay.md)
- [frame](../sources/blogs/personal/daniel-miessler/blog-frame.md)
- [happiness struggle and options](../sources/blogs/personal/daniel-miessler/blog-happiness-struggle-and-options.md)
- [hillary clinton faustian case point](../sources/blogs/personal/daniel-miessler/blog-hillary-clinton-faustian-case-point.md)
- [how much incel terrorism can we prevent with kindness](../sources/blogs/personal/daniel-miessler/blog-how-much-incel-terrorism-can-we-prevent-with-kindness.md)
- [how would you prove evolution](../sources/blogs/personal/daniel-miessler/blog-how-would-you-prove-evolution.md)
- [http](../sources/blogs/personal/daniel-miessler/blog-http.md)
- [hyphens vs dashes](../sources/blogs/personal/daniel-miessler/blog-hyphens-vs-dashes.md)
- [impostor syndrome wikipedia the free encyclopedia](../sources/blogs/personal/daniel-miessler/blog-impostor-syndrome-wikipedia-the-free-encyclopedia.md)
- [information security definitions](../sources/blogs/personal/daniel-miessler/blog-information-security-definitions.md)
- [information security](../sources/blogs/personal/daniel-miessler/blog-information-security.md)
- [introducing substrate old](../sources/blogs/personal/daniel-miessler/blog-introducing-substrate-old.md)
- [is it wrong to have children](../sources/blogs/personal/daniel-miessler/blog-is-it-wrong-to-have-children.md)
- [job losses automation active passive](../sources/blogs/personal/daniel-miessler/blog-job-losses-automation-active-passive.md)
- [liberal gun owner explores gun data](../sources/blogs/personal/daniel-miessler/blog-liberal-gun-owner-explores-gun-data.md)
- [linkclump for web testing](../sources/blogs/personal/daniel-miessler/blog-linkclump-for-web-testing.md)
- [machine learning doesnt introduce unfairness it reveals it](../sources/blogs/personal/daniel-miessler/blog-machine-learning-doesnt-introduce-unfairness-it-reveals-it.md)
- [microsoft amazon facebook can go far without mobile play](../sources/blogs/personal/daniel-miessler/blog-microsoft-amazon-facebook-can-go-far-without-mobile-play.md)
- [military controls movies](../sources/blogs/personal/daniel-miessler/blog-military-controls-movies.md)
- [my current predictions for thinking machines](../sources/blogs/personal/daniel-miessler/blog-my-current-predictions-for-thinking-machines.md)
- [my letter to a linux desktop user](../sources/blogs/personal/daniel-miessler/blog-my-letter-to-a-linux-desktop-user.md)
- [network ports](../sources/blogs/personal/daniel-miessler/blog-network-ports.md)
- [news analysis no 270](../sources/blogs/personal/daniel-miessler/blog-news-analysis-no-270.md)
- [news analysis no 283](../sources/blogs/personal/daniel-miessler/blog-news-analysis-no-283.md)
- [news analysis no 304](../sources/blogs/personal/daniel-miessler/blog-news-analysis-no-304.md)
- [news analysis no 330](../sources/blogs/personal/daniel-miessler/blog-news-analysis-no-330.md)
- [no 371](../sources/blogs/personal/daniel-miessler/blog-no-371.md)
- [no 380 llm mind reading automated war rusty sudo eliezer bitterness theory](../sources/blogs/personal/daniel-miessler/blog-no-380-llm-mind-reading-automated-war-rusty-sudo-eliezer-bitterness-theory.md)
- [pre suasion vs persuasion](../sources/blogs/personal/daniel-miessler/blog-pre-suasion-vs-persuasion.md)
- [predicting future twitter](../sources/blogs/personal/daniel-miessler/blog-predicting-future-twitter.md)
- [rise corporate technology ecosystem](../sources/blogs/personal/daniel-miessler/blog-rise-corporate-technology-ecosystem.md)
- [rise of pokemon go arvr gaming](../sources/blogs/personal/daniel-miessler/blog-rise-of-pokemon-go-arvr-gaming.md)
- [rudimentary threat model framework password vs touchid vs faceid](../sources/blogs/personal/daniel-miessler/blog-rudimentary-threat-model-framework-password-vs-touchid-vs-faceid.md)
- [san francisco is a microcosm of americas future](../sources/blogs/personal/daniel-miessler/blog-san-francisco-is-a-microcosm-of-americas-future.md)
- [security report analysis forrester security analytics platforms 2016](../sources/blogs/personal/daniel-miessler/blog-security-report-analysis-forrester-security-analytics-platforms-2016.md)
- [sota models over custom ones](../sources/blogs/personal/daniel-miessler/blog-sota-models-over-custom-ones.md)
- [spqa ai architecture replace existing software](../sources/blogs/personal/daniel-miessler/blog-spqa-ai-architecture-replace-existing-software.md)
- [summary 21 immutable laws marketing](../sources/blogs/personal/daniel-miessler/blog-summary-21-immutable-laws-marketing.md)
- [summary rework](../sources/blogs/personal/daniel-miessler/blog-summary-rework.md)
- [take 1 security podcast episode 10](../sources/blogs/personal/daniel-miessler/blog-take-1-security-podcast-episode-10.md)
- [tcpflags](../sources/blogs/personal/daniel-miessler/blog-tcpflags.md)
- [the conservative christian view of the jews the standard for cognitive dissonance](../sources/blogs/personal/daniel-miessler/blog-the-conservative-christian-view-of-the-jews-the-standard-for-cognitive-dissonance.md)
- [the intellectual dark web is a clear case of dark forest theory](../sources/blogs/personal/daniel-miessler/blog-the-intellectual-dark-web-is-a-clear-case-of-dark-forest-theory.md)
- [the irony of opposing government programs](../sources/blogs/personal/daniel-miessler/blog-the-irony-of-opposing-government-programs.md)
- [the most exciting features from the wwdc 2018 keynote](../sources/blogs/personal/daniel-miessler/blog-the-most-exciting-features-from-the-wwdc-2018-keynote.md)
- [the problem with cybersecurity hiring](../sources/blogs/personal/daniel-miessler/blog-the-problem-with-cybersecurity-hiring.md)
- [the single reason harry potter is better than the marvel mcu](../sources/blogs/personal/daniel-miessler/blog-the-single-reason-harry-potter-is-better-than-the-marvel-mcu.md)
- [the sleepy puppy xss payload management framework](../sources/blogs/personal/daniel-miessler/blog-the-sleepy-puppy-xss-payload-management-framework.md)
- [the strange game of shared for profit cybersecurity risk scores](../sources/blogs/personal/daniel-miessler/blog-the-strange-game-of-shared-for-profit-cybersecurity-risk-scores.md)
- [the ubermensch](../sources/blogs/personal/daniel-miessler/blog-the-ubermensch.md)
- [the universal arc](../sources/blogs/personal/daniel-miessler/blog-the-universal-arc.md)
- [the ways we deceive ourselves](../sources/blogs/personal/daniel-miessler/blog-the-ways-we-deceive-ourselves.md)
- [thoughts about her](../sources/blogs/personal/daniel-miessler/blog-thoughts-about-her.md)
- [three republican mistakes](../sources/blogs/personal/daniel-miessler/blog-three-republican-mistakes.md)
- [uncanny valley assertive women](../sources/blogs/personal/daniel-miessler/blog-uncanny-valley-assertive-women.md)
- [unsupervised learning episode 35](../sources/blogs/personal/daniel-miessler/blog-unsupervised-learning-episode-35.md)
- [unsupervised learning no 210 member edition](../sources/blogs/personal/daniel-miessler/blog-unsupervised-learning-no-210-member-edition.md)
- [unsupervised learning no 79](../sources/blogs/personal/daniel-miessler/blog-unsupervised-learning-no-79.md)
- [were all in fractal microcults](../sources/blogs/personal/daniel-miessler/blog-were-all-in-fractal-microcults.md)
- [when will windows be ready for the desktop](../sources/blogs/personal/daniel-miessler/blog-when-will-windows-be-ready-for-the-desktop.md)
- [why central park karen deserves what she got](../sources/blogs/personal/daniel-miessler/blog-why-central-park-karen-deserves-what-she-got.md)
- [why im camping for the iphone 5](../sources/blogs/personal/daniel-miessler/blog-why-im-camping-for-the-iphone-5.md)
- [why you should hate anthropic](../sources/blogs/personal/daniel-miessler/blog-why-you-should-hate-anthropic.md)
- [windowsfilesharing](../sources/blogs/personal/daniel-miessler/blog-windowsfilesharing.md)
- [your relationship with failure determines your potential](../sources/blogs/personal/daniel-miessler/blog-your-relationship-with-failure-determines-your-potential.md)

<!-- sources:auto:end -->
