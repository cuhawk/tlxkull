---
title: 0xLupin (Roni Carta)
slug: 0xlupin
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [0xlupin]
role: hunter
primary_focus: supply-chain
tags: [person, role/hunter, focus/supply-chain, focus/server-side, focus/dependency-confusion, focus/google-vrp]
inbound: []
---

## Identity

- **Real name:** Roni Carta
- **Primary handle:** `0xLupin`
- **Role:** Bug-bounty hunter and co-founder/CEO of Lupin & Holmes (landh.tech), the offensive-security company behind the Depi supply-chain security tool. Former Senior Security Engineer at ManoMano (Red Team / Pentesting). Began bug bounty at ~18; approaching ~$800K disclosed earnings by age 23.
- **Location:** Tokyo, Japan (Lupin & Holmes operates between France and Japan; Roni is Tokyo-based and CT Ep 37 was the in-person "Tokyo Hacking" interview).
- **Track record:** Google VRP regular, MVH at Google Las Vegas BugSwat 2024 (with Justin Gardner), MVH at Google Tokyo BugSwat / LLM bugSWAT 2025. $50K Google AI bounty (with rez0 + Rhynorater). $50,500 DockerHub supply-chain bounty (with Snorlhax). $17K HashiCorp backdoor finding. $10,500 npm cache-poisoning.

## Focus areas

- Software supply-chain attacks (dependency confusion, package compromise, registry abuse, GitHub Actions cache poisoning)
- Server-side / RCE via non-HTTP attack surface (CI/CD, package managers, dev-env trust chains)
- Google VRP (AI bugSWAT, Google Cloud, Bard/Gemini)
- Red-teaming + offensive tooling
- Cloudflare / WAF bypass research

## Online presence

- Company blog: [landh.tech/blog](https://www.landh.tech/blog) (Lupin & Holmes — primary writeup venue)
- Company about: [landh.tech/about](https://www.landh.tech/about/)
- X / Twitter: [@0xLupin](https://x.com/0xLupin)
- GitHub: [github.com/Roni-Carta](https://github.com/Roni-Carta)
- Gists: [gist.github.com/Roni-Carta](https://gist.github.com/Roni-Carta)
- LinkedIn: [in/roni-carta](https://www.linkedin.com/in/roni-carta/)
- YouTube: [@0xlupin](https://www.youtube.com/@0xlupin)
- Company LinkedIn: [Lupin & Holmes](https://www.linkedin.com/company/lupin-holmes)

## Key research / posts

- **We Hacked Google A.I. for $50,000** ([landh.tech/blog/20240304-google-hack-50000](https://www.landh.tech/blog/20240304-google-hack-50000/), 2024-03-04) — co-authored with Joseph "rez0" Thacker and Justin "Rhynorater" Gardner from the inaugural Google LLM bugSWAT. Three chains: an IDOR in Bard Vision exposing other users' uploaded images, GraphQL directive overloading triggering DoS in the GCP console, and a prompt-injection-to-Gmail-data exfil via markdown image rendering. Seed for AI-VRP methodology notes.
- **Hacking Millions of Companies with $10: A Massive Software Supply Chain Attack** ([landh.tech/blog/20241107-10-to-hack-millions-of-companies](https://www.landh.tech/blog/20241107-10-to-hack-millions-of-companies), 2024-11-07) — the DockerHub / dev-env supply-chain attack referenced in the $50,500 X(Twitter) post; canonical Lupin work on "popping RCE without an HTTP request" against dev toolchains.
- **How We Hacked a Software Supply Chain for $50K** ([landh.tech/blog/20250211-hack-supply-chain-for-50k](https://www.landh.tech/blog/20250211-hack-supply-chain-for-50k), 2025-02-11) — companion post on the Snorlhax-collab supply-chain RCE.
- **We Hacked Google's A.I. Gemini and Leaked Its Source Code** ([landh.tech/blog/20250327-we-hacked-gemini-source-code](https://www.landh.tech/blog/20250327-we-hacked-gemini-source-code), 2025-03-27) — Google AI VRP follow-up.
- **Netflix Vulnerability: Dependency Confusion in Action** ([landh.tech/blog/20250610-netflix-vulnerability-dependency-confusion](https://www.landh.tech/blog/20250610-netflix-vulnerability-dependency-confusion), 2025-06-10) — concrete dep-confusion case study against Netflix.
- **We Hacked the npm Supply Chain of 36 Million Weekly Installs** ([landh.tech/blog/20251003-36m-installs](https://www.landh.tech/blog/20251003-36m-installs), 2025-10-03) — npm registry compromise at scale.
- **One Label Away from Backdooring 80M Installations per Week** ([landh.tech/blog/20260317-one-label-away-from-80m-install-per-week](https://www.landh.tech/blog/20260317-one-label-away-from-80m-install-per-week), 2026-03-17) — GitHub-label-driven backdoor primitive in popular package maintainership flow.
- **First Week, First Hack: Compromising a Package with 40M Weekly Downloads** ([landh.tech/blog/20260402-img-colour-supply-chain-hack](https://www.landh.tech/blog/20260402-img-colour-supply-chain-hack), 2026-04-02) — img-colour package takeover.
- **TanStack Compromised: GitHub Actions Cache Poisoning Hitting npm** ([landh.tech/blog/20260511-tanstack-supply-chain-compromise](https://www.landh.tech/blog/20260511-tanstack-supply-chain-compromise), 2026-05-11) — GitHub Actions cache as supply-chain pivot.
- **node-ipc Compromised: A Dormant Maintainer, an Expired Domain** ([landh.tech/blog/20260514-node-ipc-compromised](https://www.landh.tech/blog/20260514-node-ipc-compromised), 2026-05-14) — maintainer-email/domain-expiry takeover post-mortem.
- **GitHub: [cf-bypass](https://github.com/Roni-Carta/cf-bypass)** — Cloudflare WAF bypass script. One of his public offensive-tooling repos under Roni-Carta.

## CT podcast appearances

- [2023-09-21 Ep 37 — Tokyo Hacking & Interview with 0xLupin](../sources/podcasts/ct/20230921_dRipv2ZfGbw_Tokyo_Hacking_Interview_with_0xLupin_Ep._37.en.vtt)
- [2024-06-06 Ep 74 — Supply Chain Attack Primer: Popping RCE Without an HTTP Request (feat 0xLupin)](../sources/podcasts/ct/20240606_5bgFIP-3VqI_Supply_Chain_Attack_Primer_-_Popping_RCE_Without_an_HTTP_Request_feat_0xLupin_Ep._74.en.vtt)
- [2024-08-15 Ep 84 — 0xLupin & Takeaways from Google's Las Vegas BugSwat](../sources/podcasts/ct/20240815_x5R43EMOsBQ_0xLupin_Takeaways_from_Google_s_Las_Vegas_BugSwat_Ep._84.en.vtt)
- [2025-05-15 Ep 122 — We Won Google's AI Hacking Event in Tokyo — Main Takeaways](../sources/podcasts/ct/20250515_T0N-H6B9r5g_We_Won_Google_s_AI_Hacking_Event_in_Tokyo_-_Main_Takeaways_Ep.122.en.vtt) (Lupin referenced; Tokyo LLM bugSWAT win)

## Notes

- Tokyo-based French hunter; one of the few CT regulars based in Asia. CT Ep 37 was filmed in person in Tokyo (Justin previously lived in Yokohama — there's a long-running JP connection).
- Signature methodology: chase the "no-HTTP-request" RCE — get code execution on a downstream consumer (developer laptop, CI runner, registry mirror) by compromising the *upstream* dependency rather than the target's HTTP surface. Dep-confusion, typosquatting, maintainer/domain takeover, GHA cache poisoning, registry abuse all fit this frame.
- Frequent Google VRP collaborator with `rez0` and `rhynorater` — the trio has won Google MVH at multiple BugSwat / LLM bugSWAT events (Las Vegas 2024, Tokyo 2025). Pairs especially well with `rhynorater` because their styles (Lupin = server-side / supply-chain, Justin = client-side / source review) are complementary on a single target.
- Frequent collaborator with `snorlhax` on supply-chain campaigns (DockerHub $50.5K, npm $10.5K).
- Built Lupin & Holmes (landh.tech) into a productized offensive-security business — Depi commercializes 4 years of supply-chain attack research; Seedcamp-led $5.9M pre-seed (2025).
- Speaks regularly in French and English; "Tronche de Tech" Ep 25 is the French-language long-form interview if needed.
- Treat the landh.tech blog as a canonical primary source for supply-chain technique pages — feed each post through `wiki-ingest` and cross-link from `techniques/supply-chain/`.
