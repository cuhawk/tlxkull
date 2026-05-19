---
title: Daniel Thatcher
slug: daniel-thatcher
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [_danielthatcher, danielthatcher]
role: researcher
primary_focus: server-side
tags: [person, role/researcher, focus/server-side, focus/http-smuggling, focus/ssrf, focus/timing, vendor/portswigger, vendor/intruder]
inbound: []
---

# Daniel Thatcher

## Identity

- **Real name:** Daniel Thatcher
- **Primary handle:** `_danielthatcher` (X), `danielthatcher` (GitHub)
- **Role:** Researcher (formerly Security Research Engineer at Intruder.io;
  current affiliation with PortSwigger per user notes — see *Notes* below
  on attribution caveat).

## Focus areas

- Server-side web exploitation
- HTTP request / header smuggling, reverse-proxy parser discrepancies
- SSRF (incl. XXE-to-SSRF) and DNS rebinding
- Server-side prototype pollution detection
- Cache poisoning via header smuggling

## Online presence

- [X / Twitter — @_danielthatcher](https://twitter.com/_danielthatcher)
- [GitHub — danielthatcher](https://github.com/danielthatcher)
- [Personal blog — blog.long.lat](https://blog.long.lat)
- [Intruder Research index](https://www.intruder.io/research)

## Key research / posts

- **Practical HTTP Header Smuggling: Sneaking Past Reverse Proxies to Attack AWS and Beyond** (Nov 10, 2021)
  - [Intruder post](https://www.intruder.io/research/practical-http-header-smuggling)
  - [Black Hat EU 2021 whitepaper (PDF)](https://i.blackhat.com/EU-21/Wednesday/EU-21-Thatcher-Practical-HTTP-Header-Smuggling-wp.pdf)
  - Mutates header *names* (space/control chars) so front-end parser and
    back-end parser disagree; bypassed AWS API Gateway IP allow-lists and
    enabled cache poisoning via Host smuggling. Featured in
    [PortSwigger Top 10 Web Hacking Techniques of 2021](https://portswigger.net/research/top-10-web-hacking-techniques-of-2021).

- **In GUID We Trust** (Oct 11, 2022)
  - [Intruder post](https://www.intruder.io/research/in-guid-we-trust)
  - Maps the security properties of UUID v1/v3/v4/v5 (and lookalikes) and
    when "random ID" assumptions break in auth / password-reset flows.

- **Detecting Server-Side Prototype Pollution** (Feb 15, 2023)
  - [Intruder post](https://www.intruder.io/research/server-side-prototype-pollution)
  - Black-box probes for SSPP — sends gadget payloads and watches for
    side-channel state mutation in subsequent responses.

- **Simple Bugs in SAML Apps — Oracle Commerce Cloud** (Jul 2023)
  - [Intruder post](https://www.intruder.io/research/simple-bugs-in-saml-apps---oracle-commerce-cloud)
  - XXE in Oracle Commerce Cloud's `/store/v1/login` SAML endpoint via
    external DTD → blind SSRF. Methodology applies to most SAML/SSO
    handlers that parse user-supplied XML.

- **We Hacked Ourselves With DNS Rebinding** (Dec 1, 2023)
  - [Intruder post](https://www.intruder.io/research/we-hacked-ourselves-with-dns-rebinding)
  - Used DNS rebinding against Intruder's own ZAP-AJAX-spider screenshot
    worker (long browsing window) to reach IMDSv2 and extract AWS
    credentials. Defeats the "DNS rebinding is theoretical" handwave.

- **Tricks for Reliable Split-Second DNS Rebinding in Chrome and Safari** (Dec 6, 2023)
  - [Intruder post](https://www.intruder.io/research/split-second-dns-rebinding-in-chrome-and-safari)
  - Reliable sub-second DNS rebinding primitives for Chromium and
    WebKit; bypasses local-network access restrictions introduced as
    DNS-rebinding mitigations.

- **Exploiting a 'Useless' Cookie-Based XSS and Making it Useful** (Sep 16, 2020)
  - [blog.long.lat](https://blog.long.lat) — early personal-blog post on
    cookie-based XSS chaining.

## CT podcast appearances

- None confirmed as of 2026-05-15. (Not located via Critical Thinking
  Bug Bounty search; transcripts under `wiki/sources/podcasts/ct/` do
  not contain his name. Add here when first confirmed appearance lands.)

## Notes

- **Strong server-side bias.** Across Header Smuggling → SSPP → DNS
  rebinding → XXE-SSRF, the through-line is parser / trust-boundary
  discrepancies on the server, not client-side sinks. His own blog
  tagline ("a little too much focus on useless XSS") is self-deprecating
  — published research is overwhelmingly server-side.

- **Tooling.** Author of
  [`smuggles`](https://github.com/danielthatcher/smuggles) (HTTP request
  smuggling scanner, Go),
  [`spydom`](https://github.com/danielthatcher/spydom) (headless-Chrome
  DOM recon), and
  [`Cookieless-Session-Scanner`](https://github.com/danielthatcher/Cookieless-Session-Scanner)
  (Burp plugin for ASP.NET cookieless sessions). The header-smuggling
  tooling extends Kettle's `Param Miner` toolkit — confirmed working
  relationship even before any PortSwigger move.

- **PortSwigger / Kettle attribution caveat.** User notes describe him
  as co-authoring *Listen to the whispers: web timing attacks that
  actually work* with James Kettle. Public byline on
  [portswigger.net/research/listen-to-the-whispers-...](https://portswigger.net/research/listen-to-the-whispers-web-timing-attacks-that-actually-work)
  and the
  [PDF](https://portswigger.net/kb/papers/ckizlam/listen-to-the-whispers.pdf)
  list Kettle (@albinowax) as sole author. A PortSwigger researcher
  bio page for Thatcher was not reachable at the time of writing
  (HTTP 404 on `/research/daniel-thatcher`). Treat the "joined
  PortSwigger" claim as user-asserted and to-be-confirmed; the
  Intruder-era research catalog above is fully sourced. Update this
  section when an official PortSwigger researcher page or co-author
  byline appears.

- **Cross-references.**
  - HTTP header smuggling pattern → see
    `wiki/techniques/request-smuggling/` (create on first finding).
  - DNS rebinding split-second technique → see
    `wiki/techniques/ssrf/dns-rebinding.md` (create on first finding).
  - Server-side prototype pollution detection → see
    `wiki/techniques/prototype-pollution/server-side.md` (create on
    first finding).

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/daniel-thatcher/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

<!-- sources:auto:start -->
## Ingested blog posts

- [2019 04 09 obtaining xss using moodle features and minor bugs](../sources/blogs/personal/daniel-thatcher/2019-04-09-obtaining-xss-using-moodle-features-and-minor-bugs.md)
- [2020 09 16 exploiting a useless cookie based xss and making it useful](../sources/blogs/personal/daniel-thatcher/2020-09-16-exploiting-a-useless-cookie-based-xss-and-making-it-useful.md)
- [2026 01 06 research at intruder](../sources/blogs/personal/daniel-thatcher/2026-01-06-research-at-intruder.md)
- [projects](../sources/blogs/personal/daniel-thatcher/projects.md)

<!-- sources:auto:end -->
