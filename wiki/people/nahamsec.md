---
title: Ben Sadeghipour (NahamSec)
slug: nahamsec
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [nahamsec]
role: dual
primary_focus: recon
tags: [person, role/hunter, role/host, focus/recon, focus/ssrf, focus/content, focus/training]
inbound: []
---

## Identity

- **Real name:** Ben Sadeghipour
- **Primary handle:** `nahamsec`
- **Role:** Full-time hacker, content creator, trainer, and keynote speaker. CEO / co-founder of [HackingHub](https://hackinghub.io). Organizer of NahamCon (virtual security conference). Formerly Head of Hacker Operations / Hacker Education at HackerOne.
- **Track record:** 1,000+ vulnerabilities reported across Meta, Apple, Amazon, Google, Airbnb, Snapchat, Zoom, TikTok, and the US Department of Defense. Hacking professionally since ~2014. DEF CON 27 main-stage speaker ("Owning the Clout through SSRF and PDF Generators", 2019, w/ Cody Brocious).
- **Bounty + content blend:** Among the first hunters to publicly disclose making $500k/year as a full-time bounty hunter + content creator (CT Ep 53 title). Signature business model = bug bounty income + YouTube/Twitch + paid training (Udemy, HackingHub) + sponsorship.

## Focus areas

- Reconnaissance / attack-surface mapping — subdomain enum, cert transparency, ASN, dorking, JS recon. See `../techniques/recon/` and [../tools/karpathy/llmwiki.md](../tools/karpathy/llmwiki.md).
- SSRF and cloud-metadata escalation (Lyft / WeasyPrint research, DEF CON 27 talk).
- XSS — long-running theme; 18% of his valid submissions per his 2025 retrospective.
- Bug-bounty pedagogy — beginner-to-pro curriculum design, course/lab authorship.
- Content creation as a hacker discipline — turning live hacking and writeups into recurring YouTube/Twitch content.

## Online presence

- Website / blog: [nahamsec.com](https://www.nahamsec.com) — [posts index](https://www.nahamsec.com/posts), [about](https://www.nahamsec.com/about), [slides](https://www.nahamsec.com/slides)
- X / Twitter: [@NahamSec](https://x.com/nahamsec)
- YouTube: [@NahamSec](https://www.youtube.com/@NahamSec)
- Twitch: [twitch.tv/nahamsec](https://www.twitch.tv/nahamsec)
- GitHub: [github.com/nahamsec](https://github.com/nahamsec)
- HackerOne: [hackerone.com/nahamsec](https://hackerone.com/nahamsec)
- LinkedIn: [in/nahamsec](https://www.linkedin.com/in/nahamsec/)
- Instagram: [instagram.com/nahamsec](https://www.instagram.com/nahamsec)
- Discord: [NahamSec server](https://discord.com/servers/nahamsec-598608711186907146)
- HackingHub: [hackinghub.io](https://hackinghub.io) — co-founded with John Hammond and Adam Langley
- NahamCon: [nahamcon.com](https://www.nahamcon.com/)
- Udemy course: [Intro to Bug Bounty Hunting and Web Application Hacking](https://www.udemy.com/course/intro-to-bug-bounty-by-nahamsec/)
- SANS profile: [sans.org/profiles/ben-sadeghipour](https://www.sans.org/profiles/ben-sadeghipour)

## Key research / posts

- **My Expense Report resulted in a Server-Side Request Forgery (SSRF) on Lyft** ([nahamsec.com/posts/my-expense-report-resulted-in-a-server-side-request-forgery-ssrf-on-lyft](https://www.nahamsec.com/posts/my-expense-report-resulted-in-a-server-side-request-forgery-ssrf-on-lyft)) — HTML tags in expense notes survived through the PDF generator (WeasyPrint), enabling SSRF reachable to AWS metadata. Co-found with [@daeken](https://x.com/daeken). The chain that seeded the DEF CON 27 research.
- **Owning the Clout through SSRF and PDF Generators (DEF CON 27, 2019)** ([defcon.org slides PDF](https://media.defcon.org/DEF%20CON%2027/DEF%20CON%2027%20presentations/DEFCON-27-Ben-Sadeghipour-Owning-the-clout-through-SSRF-and-PDF-generators.pdf)) — generalizes the Lyft chain across multiple HTML-to-PDF engines (WeasyPrint, wkhtmltopdf, etc.). Canonical reference for PDF-generator SSRF as a class.
- **Vulnerabilities to Master in 2025: Your Path to $100k in Bug Bounties** ([nahamsec.com/posts/high-value-web-security-vulnerabilities-to-learn-in-2025](https://www.nahamsec.com/posts/high-value-web-security-vulnerabilities-to-learn-in-2025)) — Feb 2025 retrospective on six payout-heavy bug classes: XSS, SSRF, path traversal, web cache deception, supply-chain, race conditions. SSRF = ~25% of his personal earnings; XSS = ~18% of valid submissions.
- **Bug Bounty Full Time** ([nahamsec.com/posts/hacking-full-time](https://www.nahamsec.com/posts/hacking-full-time)) — non-technical: lessons from going full-time. Often paired with Rhynorater's "Hacker Healthcare" piece when advising new full-timers.
- **Getting Started in Bug Bounty** ([nahamsec.com/getting-started-in-bug-bounty](https://www.nahamsec.com/getting-started-in-bug-bounty)) — his canonical beginner roadmap. Companion to the GitHub resources repo below.
- **Resources-for-Beginner-Bug-Bounty-Hunters** ([github.com/nahamsec/Resources-for-Beginner-Bug-Bounty-Hunters](https://github.com/nahamsec/Resources-for-Beginner-Bug-Bounty-Hunters)) — 12k-star community reading list (blogposts, talks, tools). The Jhaddix-style canonical entry-point list for new hunters.
- **lazyrecon** ([github.com/nahamsec/lazyrecon](https://github.com/nahamsec/lazyrecon)) — 2k-star shell pipeline automating subdomain enum + screenshotting + dir-busting. The methodology blueprint behind his recon YouTube series; spiritual sibling to JHaddix's recon framework.
- **JSParser** ([github.com/nahamsec/JSParser](https://github.com/nahamsec/JSParser)) — Python tool that pulls endpoints out of JS files. Recon staple for JS attack-surface enumeration.
- **bbht — Bug Bounty Hunting Tools** ([github.com/nahamsec/bbht](https://github.com/nahamsec/bbht)) — one-shot Ubuntu provisioning script that installs the core BB toolchain. Companion to lazyrecon for fresh VPS setups.
- **crtndstry** ([github.com/nahamsec/crtndstry](https://github.com/nahamsec/crtndstry)) — subdomain finder leveraging crt.sh + DNSdumpster. Cited as inspiration in our `memory/feedback_recon_sub_sources` (global memory) memory (crt.sh JSON is a must-have source).
- **Free Recon Course and Methodology For Bug Bounty Hunters** ([YouTube](https://www.youtube.com/watch?v=evyxNUzl-HA)) and **Bug Bounty Recon Basics: The Complete Course (Part 1)** ([YouTube](https://www.youtube.com/watch?v=krCsMZfbuB4)) — the long-form video versions of his recon methodology. Practical reference for ASN / dorking / subfinder / httpx / Shodan / tlsx workflows.
- **Practical AI for Bounty Hunters (NahamCon 2024)** ([Class Central index](https://www.classcentral.com/course/youtube-nahamcon2024-practical-ai-for-bounty-hunters-atjhaddix-295688)) — w/ JHaddix; an early talk on integrating LLMs into the recon + reporting loop.

## CT podcast appearances

- [2024-01-11 Ep 53 — 500k/yr as Full-Time Bug Hunter Content Creator](../sources/podcasts/ct/20240111_5o0Ldc8Kypg_500k_yr_as_Full-Time_Bug_Hunter_Content_Creator_-_Nahamsec_Ep._53.en.vtt)
- [2024-05-09 Ep 70 — NahamCon and CSP Bypasses Everywhere](../sources/podcasts/ct/20240509_t6cTvajgYsM_NahamCon_and_CSP_Bypasses_Everywhere_Ep._70.en.vtt)

## Notes

- **NahamCon = his flagship event.** Free virtual security con streamed on YouTube + Twitch. 2024 hosted by John Hammond + Joel Margolis + Justin Gardner. 2025 main edition hosted by Jason Haddix with an AI-dedicated second track. Winter edition (Dec 17-18, 2025) added — talks + workshops + CTF. The con is the public-facing hub for the whole NahamSec brand; his network of hosts/speakers (Hammond, Haddix, Margolis, Gardner, etc.) overlaps heavily with the CT crowd.
- **Signature = recon + content, not client-side.** Unlike Rhynorater's escalation/client-side specialty, Ben's edge is *finding things others miss* via wide attack-surface mapping + then converting the find into educational content. lazyrecon / bbht / crtndstry / JSParser are the tooling fingerprint. SSRF is his most-cited bug class but recon is the methodology layer beneath it.
- **Income model.** Public about earning $500k+/yr blending bounties + YouTube + Twitch + sponsorships + paid training (Udemy + HackingHub labs). Cited in CT Ep 53 as a case study for the "content-creator hunter" career path; relevant context when comparing to Rhynorater's CRIT / advisor-only model.
- **HackingHub.** Subscription lab platform co-founded with John Hammond + Adam Langley. Direct competitor / complement to HackTheBox / PortSwigger Academy for the bug-bounty-curriculum niche. Course URL form: `https://hhub.io/nahamsec`.
- **Collab patterns:** Frequent recurring co-host / co-researcher set — JHaddix, John Hammond, STÖK (Fredrik Alexandersson), Cody Brocious (`daeken`), and the CT hosts. JHaddix 2025 NahamCon hosting handoff signals the recon-community alliance.
- **Cross-link to tooling memory.** Our recon stack notes (`memory/feedback_recon_sub_sources` (global memory)) explicitly include crt.sh + Shodan — both staples of NahamSec's recon methodology, consistent with crtndstry's design.
- **Not a contributor to Yaworski's *Real-World Bug Hunting*** (No Starch, 2019) based on a search of the book's listings — that book sources case studies from disclosed H1 reports rather than co-author chapters, so Ben's bugs may be *cited* but he's not on the byline. Flag as unverified pending direct check of the printed acknowledgments.
