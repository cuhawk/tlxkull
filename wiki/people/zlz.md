---
title: Brett Buerhaus (bbuerhaus / zlz)
slug: zlz
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [bbuerhaus, zlz, ziot]
role: hunter
primary_focus: enterprise
tags: [person, role/hunter, focus/enterprise, focus/web, focus/recon, focus/collaboration]
inbound: []
---

# Brett Buerhaus (bbuerhaus / zlz)

## Identity

- **Real name:** Brett Buerhaus. California, US.
- **Primary handles:** `bbuerhaus` (X, LinkedIn), `ziot` (legacy alias —
  blog, HackerOne, GitHub), `zlz` (CT podcast / community shorthand;
  note that `zlz` is also Sam Curry's HackerOne handle — the two names
  are entangled and frequently conflated).
- **Role:** Bug-bounty hunter and red-team engineer. ~15 years in
  security. Currently Associate Director, Cyber Security at Yuga Labs;
  past roles include Senior Red Team at Blizzard Entertainment, plus
  app-sec / game-security positions.
- **Collaborator with Sam Curry** on most of the marquee enterprise
  chains attributed to that crew (Apple, auto industry, points.com).

## Focus areas

- Enterprise SaaS / web auth chains (Airbnb, Apple, Yahoo, Google).
- Recon-driven dealer/employee-portal abuse on B2B side surfaces.
- DOM clobbering + client-side JS gadget chaining.
- Obfuscated-JS reversing and request-signing tooling.
- CTF web challenges (DEFCON badge, Google CTF, h@cktivitycon).

## Online presence

- Blog: [buer.haus](https://buer.haus)
- Resume page: [buer.haus/resume](https://buer.haus/resume/)
- X / Twitter: [@bbuerhaus](https://x.com/bbuerhaus)
- GitHub: [ziot](https://github.com/ziot)
- HackerOne: [hackerone.com/ziot](https://hackerone.com/ziot)
- LinkedIn: [bbuerhaus](https://www.linkedin.com/in/bbuerhaus/)
- Bug Bounty Forum AMA: [bugbountyforum.com/blog/ama/ziot](https://bugbountyforum.com/blog/ama/ziot/)
- HackerOne spotlight: [Hacker Spotlight: Interview with Ziot](https://www.hackerone.com/blog/hacker-spotlight-interview-ziot)

## Key research / posts

- **[We Hacked Apple for 3 Months: Here's What We Found](https://samcurry.net/hacking-apple)**
  (2020-10-07, w/ Sam Curry, Ben Sadeghipour, Samuel Erb, Tanner
  Barnes). 55 vulns (11 critical, 29 high) across Apple infra; wormable
  stored XSS in iCloud Mail centerpiece. Brett earned ~$288,500 of the
  combined Apple bounty awards from this engagement.
  See also [../people/sam-curry.md](sam-curry.md).
- **[Web Hackers vs. The Auto Industry](https://samcurry.net/web-hackers-vs-the-auto-industry)**
  (2023-01-03, w/ Sam Curry, Neiko Rivera, Maik Robert, Ian Carroll,
  Justin Rhinehart, Shubham Shah). ~16 OEMs (Ferrari, BMW, Rolls
  Royce, Porsche, Mercedes, Toyota, Nissan, Honda) — SSO/dealer-portal
  bypass + mass-assignment chained to remote-control of millions of
  vehicles. Signature collab piece.
- **[Go Go XSS Gadgets: Chaining a DOM Clobbering Exploit in the Wild](https://buer.haus/2024/02/23/go-go-xss-gadgets-chaining-a-dom-clobbering-exploit-in-the-wild/)**
  (2024-02-23). Real-world DOM clobbering chain — canonical reference
  for the technique outside of PortSwigger's lab material.
- **[Reversing and Tooling a Signed Request Hash in Obfuscated JavaScript](https://buer.haus/2024/01/16/reversing-and-tooling-a-signed-request-hash-in-obfuscated-javascript/)**
  (2024-01-16). End-to-end reversing of an obfuscated client-side
  signing scheme so bug-bounty tooling can keep replaying after the
  signature gate.
- **[Airbnb — When Bypassing JSON Encoding, XSS Filter, WAF, CSP, and Auditor turns into Eight Vulnerabilities](https://buer.haus/2017/03/08/airbnb-when-bypassing-json-encoding-xss-filter-waf-csp-and-auditor-turns-into-eight-vulnerabilities/)**
  (2017-03-08). Classic layered-defense bypass writeup; staple
  reference for XSS-through-stacked-sanitizers training.
- **[Airbnb — Ruby on Rails String Interpolation led to RCE](https://buer.haus/2017/03/13/airbnb-ruby-on-rails-string-interpolation-led-to-remote-code-execution/)**
  (2017-03-13). Server-side template/interpolation RCE.
- **[Airbnb — Chaining Third-Party Open Redirect into SSRF via LivePerson Chat](https://buer.haus/2017/03/09/airbnb-chaining-third-party-open-redirect-into-server-side-request-forgery-ssrf-via-liveperson-chat/)**
  (2017-03-09). Third-party-vendor pivot pattern.
- **[Airbnb — Web-to-App IDOR to view Everyone's Airbnb Messages](https://buer.haus/2017/03/31/airbnb-web-to-app-phone-notification-idor-to-view-everyones-airbnb-messages/)**
  (2017-03-31). Cross-channel (web → mobile push) IDOR.
- **[Escalating XSS in PhantomJS Image Rendering to SSRF / Local-File Read](https://buer.haus/2017/06/29/escalating-xss-in-phantomjs-image-rendering-to-ssrflocal-file-read/)**
  (2017-06-29). Headless-renderer abuse — the recipe many later
  screenshot/PDF-service SSRFs trace back to.
- **[A Tale of Exploitation in Spreadsheet File Conversions](https://buer.haus/2019/10/18/a-tale-of-exploitation-in-spreadsheet-file-conversions/)**
  (2019-10-18). File-conversion / parser-differential exploitation.
- **[ESEA Server-Side Request Forgery and Querying AWS Meta Data](https://buer.haus/2016/04/18/esea-server-side-request-forgery-and-querying-aws-meta-data/)**
  (2016-04-18). Early canonical SSRF → IMDS pivot writeup.
- **[admin.google.com Reflected XSS](https://buer.haus/2015/01/21/admin-google-com-reflected-cross-site-scripting-xss/)**
  (2015-01-21). Google admin-console XSS.
- **[Yahoo Root Access SQLi — tw.yahoo.com](https://buer.haus/2015/01/15/yahoo-root-access-sql-injection-tw-yahoo-com/)**
  (2015-01-15). Critical SQLi.

## CT podcast appearances

- [2024-04-04 Ep 65 — Motivation and Methodology with Sam Curry & Zlz](../sources/podcasts/ct/20240404_iFtcathflSw_Motivation_and_Methodology_with_Sam_Curry_Zlz_Ep._65.en.vtt)
  (co-guest with [Sam Curry](sam-curry.md); the "Zlz" in the episode
  title refers to the duo / Brett's community shorthand).

## Notes

- **Sam Curry's primary collaborator.** Most of the headline
  enterprise/OEM chains on `samcurry.net` carry Brett as co-author —
  Apple (2020), auto industry (2023). Sam handles the long-form
  narrative writeup; Brett's solo posts on `buer.haus` are typically
  the tooling-and-technique deep-dives (DOM clobbering gadgets,
  obfuscated-JS reversing) that feed back into the joint work.
- **Career arc:** game-security / red-team day jobs (Blizzard, now
  Yuga Labs) running parallel to enterprise bug bounty. Started on
  Facebook and Google programs; over 366 valid vulns on HackerOne
  across Verizon Media, Dropbox, PayPal. MVH + Exterminator at
  HackerOne Hack the Air Force 2.0 (H1-212, 2017). HackerOne Top 25
  (2018), Bugcrowd Top 20 (2016).
- **CTF pedigree:** Council of 9 team — DEFCON 23 + 24 Uber Badge
  Challenge winners. Long string of Google CTF / CSAW / DEFCON-qualifier
  web-challenge writeups on the blog. CTF instinct shows up in his
  bounty work as a willingness to chain 5+ small primitives into one
  payload.
- **Methodology cues to copy:** pull JS first and reverse signing /
  obfuscation before fuzzing; treat XSS sinks as gadget-chain entry
  points rather than terminal bugs (DOM clobbering, mutation XSS,
  prototype pollution land here); third-party widgets / vendor
  iframes are first-class targets for SSRF + open-redirect pivots.
- **Voice:** dry, technical, gadget-and-payload-heavy. Posts skew
  toward the "how the primitive works" half of an exploit while Sam
  Curry handles the "what it means at scale" half.
- **Note on bbac.io:** referenced as Brett's personal property; not
  resolving to public content as of this writing. Palisade Security
  (Sam Curry's consulting firm, founded ~2018) is the entity behind
  most joint engagements — see [sam-curry.md](sam-curry.md).
