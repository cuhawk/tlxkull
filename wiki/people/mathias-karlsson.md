---
title: Mathias Karlsson (avlidienbrunn)
slug: mathias-karlsson
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [avlidienbrunn]
role: researcher
primary_focus: client-side
tags: [person, role/researcher, focus/client-side, focus/browser-quirks, focus/url-parsing, focus/htmx]
inbound: []
---

# Mathias Karlsson (avlidienbrunn)

## Identity

- Real name: Mathias Karlsson.
- Primary handle: **avlidienbrunn** (Swedish for "the dead one in the well" — also the running joke behind the Ep 50 "Fall in a well" title).
- Co-founder of [Detectify](https://detectify.com) alongside Fredrik Nordberg Almroth and Frans Rosén. Long-tenured web security researcher; most public output lives on Detectify Labs.
- Active bug bounty hunter since late 2013. HackerOne profile: `avlidienbrunn`, 180+ bug credits, "Most Valuable Hacker" at h1-415 (San Francisco, 2017).
- Frequent guest on Critical Thinking — Justin Gardner has called him the "Bug Bounty Prophet" for an uncanny knack at spotting browser/web-platform edge-case bugs years before they hit mainstream advisories.

## Focus areas

- **Browser quirks & web-platform edge cases** — URL parsers, anchor-tag behavior, navigation primitives, form submission corners.
- **Client-side XSS & sanitizer bypasses** — mXSS, XSLT, postMessage origin checks, framework-attribute primitives.
- **HTMX security** — recent dedicated research stream (CSP-bypass attribute primitives, response-header injection → XSS pivots).
- **Archive-extraction vulnerabilities** — zip slip, tar symlinks, parser-disagreement attacks; built tooling around it.
- **Bug-class methodology** — likes to publish a single deeply weird bug with a maximalist writeup rather than a steady fire-hose.

## Online presence

- Personal site: [avlidienbrunn.se](https://avlidienbrunn.se) (minimalist — handle, links, a `{{2*2}}` joke template-injection probe).
- X / Twitter: [@avlidienbrunn](https://twitter.com/avlidienbrunn).
- GitHub: [github.com/avlidienbrunn](https://github.com/avlidienbrunn).
- LinkedIn: [linkedin.com/in/hackaren](https://se.linkedin.com/in/hackaren) (also `brunnsdykaren`).
- HackerOne: [hackerone.com/avlidienbrunn](https://hackerone.com/avlidienbrunn).
- Detectify Labs author archive: [labs.detectify.com/tag/mathias-karlsson/](https://labs.detectify.com/tag/mathias-karlsson/).
- Detectify Crowdsource profile: [cs.detectify.com/profile/Mathias+Karlsson](https://cs.detectify.com/profile/Mathias+Karlsson).
- GitHub Security Bug Bounty page: [bounty.github.com/researchers/avlidienbrunn.html](https://bounty.github.com/researchers/avlidienbrunn.html).
- Security Fest speaker page: [securityfest.com/speakers/mathias-karlsson/](https://securityfest.com/speakers/mathias-karlsson/).
- Bug Bounty Forum AMA: [bugbountyforum.com/blog/ama/avlidienbrunn/](https://bugbountyforum.com/blog/ama/avlidienbrunn/).
- HackerOne interview video: [youtube.com/watch?v=8WjtSiE76XU](https://www.youtube.com/watch?v=8WjtSiE76XU).

## Key research / posts

- **[How I made LastPass give me all your passwords](https://labs.detectify.com/writeups/how-i-made-lastpass-give-me-all-your-passwords/)** (2016) — Faulty regex in LastPass extension URL parsing: `http://avlidienbrunn.se/@twitter.com/@hehe.php` — browser sees `avlidienbrunn.se`, extension sees `twitter.com` because only the last `@` was URL-encoded. Canonical example of browser-vs-library URL disagreement; informs `../techniques/dom-xss/url-anatomy-bypass-cheatsheet.md` and `../techniques/dom-xss/url-credential-payload-smuggling.md`.
- **[postMessage XSS on a million sites](https://labs.detectify.com/writeups/postmessage-xss-on-a-million-sites/)** (2016) — AddThis share widget, embedded on 1M+ sites, performed no origin check on incoming `postMessage` and dispatched the payload into a script src; universal DOM XSS gadget. The reason every postMessage cheat sheet starts with "check the origin."
- **[How I disabled your Chrome security extensions](https://labs.detectify.com/how-to/how-i-disabled-your-chrome-security-extensions/)** (2015) — Navigating to `chrome-extension://…` URIs via `<a ping>` silently nuked extensions like HTTPS Everywhere with no user interaction. Browser-platform abuse, not a webapp bug — a recurring Karlsson pattern.
- **[The pitfalls of postMessage](https://labs.detectify.com/security-guidance/the-pitfalls-of-postmessage/)** — Follow-up guidance post enumerating the structural ways postMessage handlers get owned (missing origin check, weak origin check, structured-clone source confusion). Feeds `../techniques/postmessage/`.
- **Self XSS: we're not so different, you and I** ([Security Fest 2017](https://securityfest.com/speakers/mathias-karlsson/)) — Talk arguing self-XSS is exploitable far more often than the industry treats it: CSRF + clipboard + interaction-as-a-service. Pre-dates today's interactive-XSS norms by ~5 years.
- **[Archive Alchemist](https://github.com/avlidienbrunn/archivealchemist)** — Python tool to craft malicious ZIP / TAR archives for testing extractors: path traversal (`../`), symlink/hardlink overwrites, polyglot prefixes (GIF+ZIP), parser-disagreement on filename encoding, setuid/sticky-bit smuggling. The companion artifact to Ep 132. Plugs into `../techniques/supply-chain/` and any server-side file-upload testing flow.
- **HTMX research suite** (2024, with Justin Gardner, Ep 68) — Demonstrated multiple universal HTMX gadgets: `hx-trigger`/`hx-on:*`/`hx-vals` use `eval()` so the host must allow `unsafe-eval`; trigger-expression injection via `<meta hx-trigger='x[1)}),alert(3);//]'>` lets you XSS elements that normally can't fire JS; client-side response-header injection becomes XSS when HTMX is the consumer; CDN-CGI image-optimization gadgets pivot to arbitrary-subdomain redirects. Seeded `../techniques/dom-xss/htmx-csp-bypass.md`. CTF: [github.com/avlidienbrunn/htmxchall](https://github.com/avlidienbrunn/htmxchall).
- **[BountyDash](https://github.com/avlidienbrunn/bountydash)** — Personal bounty-platform aggregator dashboard. Less famous than the bugs but representative of his "build the tool, then the bug class follows" pattern.
- **GitHub OAuth redirect-URL validation flaw** (HackerOne, public credit) — Validation discrepancy in GitHub's OAuth authorization endpoint let an attacker redirect users and capture their OAuth grant. Quoted in his GitHub-Bounty researcher page.
- **`form-action` CSP bypass via XHR-submitted forms** (HackerOne) — XHR-submitted forms aren't subject to `form-action`, so CSP-protected pages can still exfil CSRF tokens. Small structural fact, recurring exploitation primitive.

## CT podcast appearances

- [2023-12-21 Ep 50 — Mathias "Fall in a well" Karlsson — Bug Bounty Prophet](../sources/podcasts/ct/20231221_QmPRRI46Wsk_Mathias_Fall_in_a_well_Karlsson_-_Bug_Bounty_Prophet_Ep._50.en.vtt) — burnout, collaboration, specialization, mXSS, XSLT, character encoding, predictions about the future of bug bounty.
- [2024-04-25 Ep 68 — 0-days & HTMX-SS with Mathias](../sources/podcasts/ct/20240425_l-k2pJ7oYa4_0-days_HTMX-SS_with_Mathias_Ep._68.en.vtt) — HTMX attribute-primitive XSS, CSP-bypass via `hx-trigger`, response-header-injection → XSS, CDN-CGI image-optimization gadgets.
- [2025-07-24 Ep 132 — Archive Testing Methodology with Mathias Karlsson](../sources/podcasts/ct/20250724_z9sCrHTl_rM_Archive_Testing_Methodology_with_Mathias_Karlsson_Ep.132.en.vtt) — zip slip, TAR symlinks/hardlinks, Unicode-path disagreements, parser-disagreement attacks (validator vs. extractor), Archive Alchemist tour.

## Notes

- **Recurring CT guest** — three appearances spanning the show's growth arc, treated as a fixture rather than a one-off. Justin's stated "Bug Bounty Prophet" nickname captures the pattern: Karlsson's research predicts the bug class everyone else is hunting 12-24 months later.
- **Signature** — finds bugs at the seams of the web platform: parsers disagreeing with each other (browser vs. extension, validator vs. extractor, framework vs. CSP). Almost never reports a "missing auth check" — almost always reports an emergent behavior from a spec corner two implementations interpret differently.
- **Output cadence** — rare and high-quality. A single Karlsson post tends to seed an entire bug-class wave (URL-confusion, postMessage origin, HTMX `eval`-attributes).
- **Personal style** — minimalist personal site, Swedish dark humor, casual blog tone, deep technical body. The `{{2*2}}` on his homepage is a long-running tells-you-everything joke.
- **Detectify roles** — co-founder; over the years has rotated through engineering, research, advisory positions. Knowledge-advisor / consulting-style framing in recent years per Detectify Labs author bio; no confirmed Cure53 staff page found in public sources at time of writing — treat that affiliation as rumor unless a Cure53 author page surfaces.
- **Collaborators** — frequent pair-work with Frans Rosén (see `frans-rosen.md`), Fredrik Nordberg Almroth, and (more recently) Justin Gardner; HackerOne $10,650 DoD chain co-authored with [Brett Buerhaus](./zlz.md).
- **Cross-refs** — research feeds `../techniques/dom-xss/htmx-csp-bypass.md`, `../techniques/dom-xss/url-anatomy-bypass-cheatsheet.md`, `../techniques/dom-xss/url-credential-payload-smuggling.md`, `../techniques/postmessage/`, and tooling cross-links into `../techniques/supply-chain/` for archive abuse.
