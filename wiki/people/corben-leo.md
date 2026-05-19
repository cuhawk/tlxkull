---
title: Corben Leo (hacker_)
slug: corben-leo
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [hacker_, lc, cdl, cdll, sxcurity]
role: hunter
primary_focus: recon
tags: [person, role/hunter, focus/recon, focus/server-side, focus/dod, focus/rce, focus/ssrf, focus/cors]
inbound: []
---

## Identity

- **Real name:** Corben Leo
- **Primary handle:** `hacker_` (Twitter/X); `lc` (GitHub); `cdl` (HackerOne)
- **Role:** Full-time bug-bounty hunter since 2016. Co-founder of Boring Mattress Co. (March 2023). Formerly Backend Engineer at Assetnote. Computer Science alum, Dakota State University.
- **Reputation:** "Legendary DoD hacker" — Top Program Hacker at Hack The Army 3.0, top-three at Hack The Army 2.0. Long-running track record against DoD, PayPal, Facebook, Google, Microsoft, Apple, AT&T, Yahoo, Adobe, Atlassian, KuCoin.
- **Style:** Heavy recon-first methodology; chains pre-auth findings (exposed admin / default creds / dev plugins / SSRF) into RCE and ATO.

## Focus areas

- Recon at scale — IPv4-range scanning, historical recon data, content discovery / directory brute-force methodology
- Server-side RCE chains (Jenkins, Atlassian Crowd, AEM, custom apps)
- SSRF — including headless-browser SSRF and pivot-to-cloud-metadata
- CORS exploitation and bypasses
- DoD / military / critical-infrastructure surfaces

## Online presence

- Blog: [corben.io](https://corben.io)
- X / Twitter: [@hacker_](https://twitter.com/hacker_)
- GitHub: [github.com/lc](https://github.com/lc)
- HackerOne: [hackerone.com/cdl](https://hackerone.com/cdl)
- LinkedIn: [linkedin.com/in/corben-leo](https://www.linkedin.com/in/corben-leo)
- Medium: [medium.com/@cdll](https://medium.com/@cdll)
- Bluesky: [hacking.bsky.social](https://bsky.app/profile/hacking.bsky.social)
- Company (Boring Mattress Co. — co-founder): [boring.co/pages/team](https://www.boring.co/pages/team)

## Key research / posts

- **A $1,000,000 bounty? The KuCoin User Information Leak** (2023-05-18) — [corben.io/blog/hacking-kucoin](https://corben.io/blog/hacking-kucoin) — Unauthenticated `/api/zendesk/api/v2/` reverse-proxy on KuCoin's webapp leaked 276k+ support tickets with PII and session tokens; case-study also in payout-disputes (HackenProof awarded only $5k).
- **A Simple SQL Injection in an Air Force Website** (2022-11-19) — [corben.io/blog/a-simple-sql-injection-in-an-air-force-website](https://corben.io/blog/a-simple-sql-injection-in-an-air-force-website) — Classic DoD pre-auth SQLi; one of his canonical Hack-the-Air-Force findings.
- **A Fun SSRF through a Headless Browser** (2022-05-06) — [corben.io/blog/a-fun-ssrf-through-a-headless-browser](https://corben.io/blog/a-fun-ssrf-through-a-headless-browser) — SSRF via a server-side headless browser; reference pattern for "automation surface as SSRF entrypoint".
- **Exposed Jenkins to RCE on 8 Adobe Experience Managers** (2019-09-04) — [corben.io/blog/19-9-04-jenkins-to-full-pwnage](https://corben.io/blog/19-9-04-jenkins-to-full-pwnage) — Unauth Jenkins with signup-enabled → scraped build logs with custom tool `jenkinz` → harvested AEM service-account creds (`aemingress`) → JSP payload RCE on 8 AEM hosts. Signature recon-into-RCE chain. Highlights reuse of historical recon ("went back through my historical recon data").
- **Analysis of an Atlassian Crowd RCE — CVE-2019-11580** (2019-07-14) — [corben.io/blog/19-7-14-atlassian-crowd-rce](https://corben.io/blog/19-7-14-atlassian-crowd-rce) — Unauth `/admin/uploadplugin.action` with `pdkinstall` dev plugin shipped in release; `Content-Type: multipart/mixed` bypasses parsing failure → arbitrary JAR upload → RCE.
- **Advanced CORS Exploitation Techniques** (2018-06-16) — [corben.io/blog/18-6-16-advanced-cors-techniques](https://corben.io/blog/18-6-16-advanced-cors-techniques) — Regex-misconfig CORS bypasses; Safari's lenient handling of special characters in hostnames trusts `xxe.sh%xx` style suffixes. Widely cited reference.
- **Chaining Bugs to Steal Yahoo Contacts!** (2018-01-11) — [corben.io/blog/18-1-11-chaining-yahoo-bugs](https://corben.io/blog/18-1-11-chaining-yahoo-bugs) — Multi-step client-side chain on Yahoo Mail.
- **Hacking the Hackers: SSRF in HackerTarget** (2017-12-17) — [corben.io/blog/17-12-17-hackertarget](https://corben.io/blog/17-12-17-hackertarget) — SSRF in a recon-SaaS provider; meta-classic.
- **Leveraging LFI to RCE using zip://** (2017-01-01) — [corben.io/blog/17-01-01-zip-to-rce-lfi](https://corben.io/blog/17-01-01-zip-to-rce-lfi) — PHP `zip://` wrapper trick; still-cited reference.
- **Learn to Hack Web Apps** (2022-04-24) — [corben.io/blog/learn-to-hack-webapps](https://corben.io/blog/learn-to-hack-webapps) — His public learning roadmap for new hunters: coding fundamentals → networking → webapp dev → vuln classes → recon.

### Notable Twitter/X threads (cited, not fetched)

- **Telco / Trans-Atlantic cable admin access** ([x.com/hacker_/status/1512552850831851531](https://x.com/hacker_/status/1512552850831851531)) — Scanned IPv4 ranges of a telecommunications bounty target → found a webserver banner "___ Cable System" → directory brute-force on `/admin/accounts/` → endpoint silently issued a valid admin `JSESSIONID`. Cable was on a WikiLeaks-released list of US-critical infrastructure.
- **"I hacked a car company"** ([x.com/hacker_/status/1693617186848551146](https://x.com/hacker_/status/1693617186848551146)) — Gained access to hundreds of an OEM's internal codebases via recon chain (often-cited as illustrative of his recon-first methodology).

## CT podcast appearances

- [2023-06-01 Ep 21 — Chill Chat with Legendary DoD Hacker Corben Leo](../sources/podcasts/ct/2023-06-01_ep21_corben-leo.en.vtt) — Topics: recon methodology origin story, load balancers in recon, triage and report writing, when to pivot from recon into active exploitation. Cross-refs: [Spotify](https://open.spotify.com/episode/3kg0odURegPM21M5MdxVlp) · [criticalthinkingpodcast.io/videos/corben-leo-legendary-dod-hacker-ep-21](https://www.criticalthinkingpodcast.io/videos/corben-leo-legendary-dod-hacker-ep-21/)

## Notes

- **Signature methodology:** recon → historical-recon reuse → chain pre-auth misconfig (exposed dev tooling, default creds, lenient CORS, signup-enabled admin panels) → escalate to RCE / ATO. Distinguishing trait is that his "first finding" is usually a recon artifact (an exposed Jenkins, a reverse-proxied internal API, an IPv4-scan banner), not a payload.
- **Tooling — open source (github.com/lc):**
  - [`gau`](https://github.com/lc/gau) (~4.9k stars) — fetch known URLs from OTX, Wayback, Common Crawl. Recon staple, complements [waybacktool](https://github.com/Rhynorater/waybacktool) — see [justin-gardner.md](justin-gardner.md).
  - [`subjs`](https://github.com/lc/subjs) (~842 stars) — JS-file enumeration over a URL/subdomain list. Common upstream of `js-harvest`-style flows.
  - [`secretz`](https://github.com/lc/secretz) — Travis CI secret-exposure scanner. The `jenkinz` tool from the Adobe writeup is the spiritual successor.
- **Companies / roles (chronological):**
  - **Assetnote** — Backend Engineer (former). Heavy contributor culture around recon tooling; their public [wordlists.assetnote.io](https://wordlists.assetnote.io/) is his recommended primary source for content discovery. See [Assetnote wordlists repo](https://github.com/assetnote/wordlists).
  - **Boring Mattress Co.** — Co-founder since March 2023 with Daehee Park (Tuft & Needle co-founder) and Tyler Marino (ex–Tuft & Needle Head of Product). Phoenix, AZ. Non-security venture; brought on "for a fresh perspective and to keep ourselves honest".
  - Note: prompt referenced "Cosmos.so (formerly Bishop Fox)" — no public confirmation surfaced in 2026-05 search. Bishop Fox's continuous-attack-surface product is **Cosmos** (formerly CAST), separate from `cosmos.so`. Treat as unverified until corroborated; do NOT claim it in writeups.
- **Recon dogma (from his public posts and Ep 21):** be methodical when fuzzing framework-specific routes (Express, Rails, Flask, Django); rotate HTTP methods (don't only `GET`); reuse the same wordlist with different methods; chase historical recon for forgotten subdomains. See [@hacker_/status/1765589673018044715](https://x.com/hacker_/status/1765589673018044715).
- **Collab patterns:** Frequent collaborator with [Shubham Shah](shubham-shah.md) (Assetnote co-founder), [Sean Yeoh](sean-yeoh.md) (Assetnote). CT-era pairings with [Justin Gardner](justin-gardner.md) and the Assetnote crowd.
- **Why he matters to TLX:** archetype for the recon-heavy chain pattern the workflow encodes (`recon` → `js-harvest` → `js-index` → `chain-triage` → `opus-deep-audit`). His writeups are reference data for the "exposed dev tooling → cred harvest → RCE" technique class.

<!-- sources:auto:start -->
## Ingested blog posts

- [17 01 01 zip to rce lfi](../sources/blogs/personal/corben-leo/blog-17-01-01-zip-to-rce-lfi.md)
- [17 01 09 aol xss](../sources/blogs/personal/corben-leo/blog-17-01-09-aol-xss.md)
- [17 05 09 ipb xss](../sources/blogs/personal/corben-leo/blog-17-05-09-ipb-xss.md)
- [17 06 30 bandcamp xss](../sources/blogs/personal/corben-leo/blog-17-06-30-bandcamp-xss.md)
- [17 11 27 tricky cors](../sources/blogs/personal/corben-leo/blog-17-11-27-tricky-cors.md)
- [17 11 30 asus sqli](../sources/blogs/personal/corben-leo/blog-17-11-30-asus-sqli.md)
- [17 12 17 hackertarget](../sources/blogs/personal/corben-leo/blog-17-12-17-hackertarget.md)
- [17 3 10 att rce](../sources/blogs/personal/corben-leo/blog-17-3-10-att-rce.md)
- [18 1 11 chaining yahoo bugs](../sources/blogs/personal/corben-leo/blog-18-1-11-chaining-yahoo-bugs.md)
- [18 12 5 xss to xxe in prince](../sources/blogs/personal/corben-leo/blog-18-12-5-xss-to-xxe-in-prince.md)
- [18 6 16 advanced cors techniques](../sources/blogs/personal/corben-leo/blog-18-6-16-advanced-cors-techniques.md)
- [19 7 14 atlassian crowd rce](../sources/blogs/personal/corben-leo/blog-19-7-14-atlassian-crowd-rce.md)
- [19 9 04 jenkins to full pwnage](../sources/blogs/personal/corben-leo/blog-19-9-04-jenkins-to-full-pwnage.md)
- [adapting to endure sequoia summary](../sources/blogs/personal/corben-leo/blog-adapting-to-endure-sequoia-summary.md)
- [hacking kucoin](../sources/blogs/personal/corben-leo/blog-hacking-kucoin.md)
- [learn to hack webapps](../sources/blogs/personal/corben-leo/blog-learn-to-hack-webapps.md)
- [blog](../sources/blogs/personal/corben-leo/blog.md)

<!-- sources:auto:end -->

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/corben-leo/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

