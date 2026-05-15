---
title: Gareth Heyes
slug: gareth-heyes
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [garethheyes, hackvertor]
role: researcher
primary_focus: client-side
vendor: portswigger
tags: [person, role/researcher, vendor/portswigger, focus/client-side, focus/xss, focus/css-injection, focus/prototype-pollution, focus/sandbox-escape]
inbound: []
---

# Gareth Heyes

## Identity

- **Real name:** Gareth Heyes
- **Primary handle:** `garethheyes`
- **Role:** Principal security researcher at PortSwigger (vendor of Burp Suite)
- **Based:** UK
- **Focus:** PortSwigger's client-side research lead. Best known for smashing
  the AngularJS sandbox to pieces, crafting elegant restricted-character XSS
  vectors, and pioneering CSS-only data exfiltration. Author of PortSwigger's
  XSS Cheat Sheet and the book *JavaScript for Hackers*. Long-time maintainer
  of Hackvertor (Burp extension) and MentalJS (JS sandbox).

## Focus areas

- DOM XSS and exotic JavaScript vectors (non-alphanumeric, paren-less, restricted-character)
- Framework sandbox escapes (AngularJS, CSP-strict envs)
- CSS injection / CSS-only data exfiltration (blind exfil, inline-style exfil)
- Prototype pollution — client-side gadgets and server-side black-box detection
- HTML / mail / URL parser differentials (email atom splitting)
- Tooling for hackers: Hackvertor, Shazzer, MentalJS, DOM Invader

## Online presence

- [PortSwigger research profile](https://portswigger.net/research/gareth-heyes) — canonical publication index
- [Personal site — garethheyes.co.uk](https://garethheyes.co.uk/)
- [X / Twitter — @garethheyes](https://x.com/garethheyes)
- [GitHub — @hackvertor](https://github.com/hackvertor)
- [Leanpub author page](https://leanpub.com/u/garethheyes) — *JavaScript for Hackers* and other titles
- [JavaScript for Hackers (book, Leanpub)](https://leanpub.com/javascriptforhackers) — DOM hacking, SOP bypass, prototype pollution, XSS techniques
- [JavaScript for Hackers (Amazon print)](https://www.amazon.com/JavaScript-hackers-Learn-think-hacker/dp/B0BRD9B3GS)
- [Hackvertor (Burp extension, source)](https://github.com/hackvertor) — tag-based conversion/encoding tool, ships under PortSwigger org
- [PortSwigger XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) — he is the canonical maintainer

## Key research / posts

- **[Inline Style Exfiltration: leaking data with chained CSS conditionals](https://portswigger.net/research/inline-style-exfiltration)** (2025-08-26) — Exfiltrates attribute data via inline `style=` only, using chained CSS `if()` + `attr()` to fire background-image requests. Drops the stylesheet-import requirement that all prior CSS-injection techniques assumed. Cross-link: `../techniques/css-injection/`.
- **[Splitting the email atom: exploiting parsers to bypass access controls](https://portswigger.net/research/splitting-the-email-atom)** (2024) — Differential parsing of email addresses (RFC vs. application validators) to smuggle a different effective recipient/identity past allow-lists; powers OAuth account-takeover and SSO impersonation chains.
- **[Blind CSS Exfiltration: exfiltrate unknown web pages](https://portswigger.net/research/blind-css-exfiltration)** (2023-12-05) — Uses the CSS `:has()` selector to extract form input names/values, textarea names, form actions, and anchor hrefs from pages the attacker can't see, in pure CSS with no JS. The current state-of-the-art when CSP blocks XSS but style injection is allowed. Cross-link: `../techniques/css-injection/has-not-input-enum.md`.
- **[Server-side prototype pollution: Black-box detection without the DoS](https://portswigger.net/research/server-side-prototype-pollution)** (2023) — Introduces non-destructive probes for server-side PP — type-confusion, status-code, reflected-property — that don't crash the server. Established server-side PP as a routine bounty class. Cross-link: `../techniques/prototype-pollution/`.
- **[Widespread prototype pollution gadgets](https://portswigger.net/research/widespread-prototype-pollution-gadgets)** (2022-06-22) — Catalogued exploitable PP gadgets in Google Analytics, Google Tag Manager, Adobe DTM, and common browser APIs; showed PP-to-DOM-XSS is a real chain on production sites. Cross-link: `../techniques/prototype-pollution/client-side-pp-gadget.md`, `../techniques/dom-xss/prototype-pollution-xss.md`.
- **[Stealing passwords from infosec Mastodon — without bypassing CSP](https://portswigger.net/research/stealing-passwords-from-infosec-mastodon-without-bypassing-csp)** (2022-11-15) — Mastodon Glitch HTML-filter bypass via the `:verified:` emoji replacement; injected an invisible form that Chrome autofill populated with credentials. Showcase of "no JS needed, autofill is the sink." Cross-link: `../techniques/dom-xss/scriptless-attacks.md`.
- **[DOM-based AngularJS sandbox escapes](https://portswigger.net/research/dom-based-angularjs-sandbox-escapes)** (2017) — The definitive series shredding AngularJS's expression sandbox across versions; this is the work he is most associated with historically. Cross-link: `../techniques/dom-xss/framework-vectors-angular.md`, `../techniques/dom-xss/client-side-template-injection.md`.
- **[Executing non-alphanumeric JavaScript without parenthesis](https://portswigger.net/research/executing-non-alphanumeric-javascript-without-parenthesis)** (2016) — Encoding JS with `[]`, `+`, and template literals plus tag-function tricks to call functions with no `()`. Foundation for modern restricted-character WAF bypasses. Cross-link: `../techniques/dom-xss/no-parens-jsonp-callback.md`, `../techniques/dom-xss/restricted-character-bypass.md`.

## CT podcast appearances

- None confirmed as of 2026-05-15. He is repeatedly *cited* on the podcast (HackerNotes Ep. 62 "Frontend Language Oddities" and Ep. 79 "The State of CSS Injection" both lean heavily on his CSS-exfil work) but has not appeared as a guest. Re-check on next `ctbb-ingest` run.

## Notes

- **PortSwigger client-side research lead.** Where James Kettle (`james-kettle.md`) owns the server-side / protocol research, Gareth owns the in-browser side: XSS vectors, CSS, sandboxes, prototype pollution. The two share authorship on tooling (DOM Invader, Burp Scanner client-side checks).
- **Signature style.** Tiny, surgical payloads. He hunts the smallest possible vector that still works under a given restriction (no parens, no alpha, no JS, CSP strict-dynamic, etc.) — then writes a Burp Scanner check around it.
- **Tooling first, then write-up.** Hackvertor (encoding/decoding tag DSL), Shazzer (browser fuzzer), MentalJS (sandboxed JS DOM) all predate the matching blog posts. Reading the extension source is often the fastest path to understanding the technique.
- **Book — *JavaScript for Hackers*.** Self-published via Leanpub (2022, expanded 2024). Covers fuzzing, DOM hacking, SOP bypass, prototype pollution, and his canonical XSS playbook. The closest thing to a textbook for our `techniques/dom-xss/` folder.
- **Cadence.** Roughly 1-2 major PortSwigger research posts per year, plus continuous additions to the XSS Cheat Sheet and Hackvertor tag library. Each major paper ships with a Burp Scanner / DOM Invader check.
- **Recurring themes to watch for in his posts:** parser differentials (mail, URL, HTML), CSS as a Turing-complete exfil channel, restricted-character JS, framework sandbox internals.
