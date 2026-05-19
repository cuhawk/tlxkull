---
title: Frans Rosén (fransrosen)
slug: frans-rosen
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [fransrosen, frans-rosen, fransr, fros]
role: researcher
primary_focus: client-side
tags: [person, role/researcher, focus/client-side, focus/oauth, focus/postmessage, focus/supply-chain, focus/cdn]
inbound: []
---

# Frans Rosén (fransrosen)

## Identity

- **Real name:** Frans Rosén
- **Primary handle:** `fransrosen` (X, HackerOne, Bugcrowd, Speaker Deck);
  GitHub handle is `fransr`.
- **Based:** Stockholm, Sweden.
- **Role:** Researcher / hunter. Co-founder of Detectify (now Knowledge
  Advisor at Detectify Labs). Also CTO/Founder at Centra. Frequent
  speaker (NahamCon, OWASP AppSecEU, ThreatCon, Øredev) and recurring
  Critical Thinking podcast guest. He is one of five HackerOne bug
  bounty researchers to reach the $1M milestone.
- **Cure53 affiliation:** Frequently named alongside Cure53-adjacent
  work, but as of this dossier the Cure53 public team page does not
  list him as a permanent team member. Treated here as
  collaborator-class until confirmed.

## Focus areas

- Client-side: postMessage abuse, DOM XSS, browser quirks.
- OAuth flow attacks ("non-happy path" / dirty dancing).
- Supply-chain / build-pipeline RCE (hot JAR swapping, CI/CD trust).
- Cloud trust boundaries (AWS S3 ACLs, Apple CloudKit, SSRF in ODoH).
- Server-side context breaks via header injection (X-Correlation-*).
- Methodology: fuzzing-driven info-disclosure pivots.

## Online presence

- [HackerOne profile](https://hackerone.com/fransrosen)
- [Bugcrowd profile](https://bugcrowd.com/h/fransrosen)
- [X / Twitter — @fransrosen](https://x.com/fransrosen)
- [GitHub — fransr](https://github.com/fransr)
- [Detectify Labs author archive](https://labs.detectify.com/author/fros/)
- [Detectify Labs tag archive](https://labs.detectify.com/tag/frans-rosen/)
- [Speaker Deck — fransrosen](https://speakerdeck.com/fransrosen)
- [LinkedIn](https://www.linkedin.com/in/fransrosen/)
- [BugBountyForum AMA](https://bugbountyforum.com/blog/ama/fransrosen/)
- [Øredev 2018 speaker page](https://archive.oredev.org/2018/2018/line-up/frans-ros-n)

## Key research / posts

- [Account hijacking using "dirty dancing" in sign-in OAuth flows](https://labs.detectify.com/writeups/account-hijacking-using-dirty-dancing-in-sign-in-oauth-flows/)
  (2022-07-06) — Combines OAuth non-happy paths (invalid state,
  response-type switching, redirect-uri quirks) with weak postMessage
  / sandbox-domain XSS gadgets to steal codes/tokens from error pages
  for 1-click ATO. Seed for `../techniques/oauth/dirty-dancing-state-leak.md`.
- [X-Correlation Injections (or How to break server-side contexts)](https://speakerdeck.com/fransrosen/x-correlation-injections-or-how-to-break-server-side-contexts)
  (2024) — Fuzzing `X-Request-ID` / `X-Correlation-ID` headers with
  shell, JSON, path-traversal, and Log4Shell payloads breaks downstream
  contexts (CI pipelines, internal logging, file paths) for JSON
  injection through RCE. Discussed on CT Ep. 86.
- [Story of an RCE on Apple through hot JAR swapping](https://speakerdeck.com/fransrosen/story-of-a-rce-on-apple-through-hot-jar-swapping)
  (NahamCon 2022 EU — [video](https://www.youtube.com/watch?v=A-O-irpqUWQ),
  [demo repo](https://github.com/fransr/hot-jar-swapping-urlclassloader))
  — Replaces an already-loaded JAR's inner classes via
  `URLClassLoader` to land RCE on Apple's Author publisher /
  Transporter. Cross-link: `../techniques/supply-chain/` (build-time
  trust pivot).
- [Hacking Slack using postMessage and WebSocket-reconnect to steal your precious token](https://labs.detectify.com/writeups/hacking-slack-using-postmessage-and-websocket-reconnect-to-steal-your-precious-token/)
  — Missing origin validation on Slack's postMessage listener lets an
  attacker redirect the WebSocket reconnect URL and exfiltrate the
  auth token. Seed for `../techniques/postmessage/`.
- [postMessage XSS on a million sites](https://labs.detectify.com/writeups/postmessage-xss-on-a-million-sites/)
  — AddThis's postMessage listener built script URLs from untrusted
  message data, yielding DOM XSS on every site embedding the widget.
- [Hacking CloudKit — How I accidentally deleted your Apple Shortcuts](https://labs.detectify.com/writeups/hacking-cloudkit-how-i-accidentally-deleted-your-apple-shortcuts/)
  (2021-09-13) — Apple CloudKit container ACLs let an authenticated
  user reach an unprotected zone-deletion endpoint and wipe all shared
  Apple Shortcuts; also surfaced iCrowd+ and Apple News bugs.
- [A deep dive into AWS S3 access controls — taking full control over your assets](https://labs.detectify.com/writeups/a-deep-dive-into-aws-s3-access-controls-taking-full-control-over-your-assets/)
  (2017-07-13) — Catalogs S3 ACL misconfigs (esp. `WRITE_ACP` =
  total bucket takeover) and introduces a non-destructive test using
  invalid MD5 checksums to confirm write access without uploading.
- [Bypassing and exploiting Bucket Upload Policies and Signed URLs](https://labs.detectify.com/writeups/bypassing-and-exploiting-bucket-upload-policies-and-signed-urls/)
  (2018-08-02) — Practical pre-signed URL / upload policy bypasses
  against S3-style storage.
- [Middleware, middleware everywhere — and lots of misconfigurations to fix](https://labs.detectify.com/ethical-hacking/middleware-middleware-everywhere-and-lots-of-misconfigurations-to-fix/)
  (2021-02-18) — Misrouted edge middleware (auth, ACL, rewrite layers)
  produces silent bypasses; broad survey across CDNs and reverse proxies.
- [XSS using quirky implementations of ACME http-01](https://labs.detectify.com/security-guidance/xss-using-quirky-implementations-of-acme-http-01/)
  (2018-09-04) — Reflected XSS via `/.well-known/acme-challenge/`
  responder quirks.
- [Mega.co.nz XSS — ExternalInterface.call JavaScript injection](https://labs.detectify.com/writeups/how-i-got-the-bug-bounty-for-mega-co-nz-xss/)
  — SWF `ExternalInterface.call()` passed unvalidated params to
  non-existent JS functions, executing attacker-controlled code via
  error handling.
- [A story of the passive-aggressive sysadmin of AEM](https://speakerdeck.com/fransrosen/a-story-of-the-passive-aggressive-sysadmin-of-aem)
  — Adobe Experience Manager misconfig patterns at scale.
- [OWASP AppSecEU 2018 — Attacking "Modern" Web Technologies](https://speakerdeck.com/fransrosen/owasp-appseceu-2018-attacking-modern-web-technologies)
  — Survey talk on then-emerging client-side and trust-boundary bug
  classes.
- [Live Hacking like a MVH — methodology and strategies to win big](https://speakerdeck.com/fransrosen/live-hacking-like-a-mvh-a-walkthrough-on-methodology-and-strategies-to-win-big)
  — His public methodology for live-hacking events (most-viewed deck
  on his Speaker Deck).
- ODoH SSRF research — [thread](https://x.com/fransrosen/status/1517193555302887424)
  — Reported SSRF-class issues in Cloudflare's `odoh-server-go` and
  argued the Oblivious DoH RFC underspecifies SSRF risk.

### Open-source tooling

- [postMessage-tracker](https://github.com/fransr/postMessage-tracker) —
  Chrome extension that logs every postMessage listener on visited
  pages. Workhorse tool for postMessage hunting. (1.3k stars)
- [bountyplz](https://github.com/fransr/bountyplz) — Automated H1 /
  Bugcrowd report submission from markdown templates.
- [template-generator](https://github.com/fransr/template-generator) —
  Handlebars + strapdown variable template editor.
- [hot-jar-swapping-urlclassloader](https://github.com/fransr/hot-jar-swapping-urlclassloader)
  — Demo for the Apple RCE talk.

## CT podcast appearances

- [2023-11-16 Ep 45 — The OG Bug Bounty King — Frans Rosen](../sources/podcasts/ct/20231116_lt48y6WP7qA_The_OG_Bug_Bounty_King_-_Frans_Rosen_Ep._45.en.vtt)
- [2024-06-13 Ep 75 — Rerun of The OG Bug Bounty King — Frans Rosen](../sources/podcasts/ct/20240613_Idx2Fy2GTjE_Rerun_of_The_OG_Bug_Bounty_King_-_Frans_Rosen_Ep._75.en.vtt)
- [2024-08-29 Ep 86 — The X-Correlation between Frans & RCE — Research Drop](../sources/podcasts/ct/20240829_YLdqWZ_E-O4_The_X-Correlation_between_Frans_RCE_-_Research_Drop_Ep._86.en.vtt)

## Notes

- **Blog bodies ingested into wiki RAG 2026-05-19.** Full bodies of the
  Detectify Labs writeups listed above live under
  `wiki/sources/blogs/detectify/` and are embedded in the `wiki` Chroma
  collection. Query via `docs_query(collection="wiki", ...)` instead of
  WebFetch.
- Recurring CT guest; one of Justin/Joel's go-to references for
  client-side and OAuth-flow tradecraft. The Ep 45 rerun (Ep 75) is
  evidence of replay value — the methodology content holds up.
- Signature pattern: long, chained writeups where a single primitive
  (a forgotten postMessage handler, an unvalidated `redirect_uri`, a
  reflected correlation header) is pivoted through 3–5 other systems
  to land impact. Cross-link `../techniques/postmessage/`,
  `../techniques/oauth/`, `../techniques/supply-chain/`.
- Methodology heuristic from his decks: fuzz everything that reflects
  (headers, params, hostnames), then chase the reflection across
  contexts — error pages, log pipelines, CI, third-party widgets.
- Toolwise: `postMessage-tracker` is the canonical "always-on" Chrome
  extension during recon for postMessage-driven account-takeover
  hunting. Add to recon profile.
- Background as Centra CTO / Detectify co-founder shows in the writeups:
  he reasons about product surfaces and platform trust boundaries, not
  just single endpoints. Useful frame for any review of a SaaS that
  shells out to CI, CDNs, or third-party storage.
