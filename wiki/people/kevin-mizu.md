---
title: Kévin Gervot (Mizu)
slug: kevin-mizu
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [kevin_mizu, kevin-mizu, mizu]
role: researcher
primary_focus: client-side
tags: [person, role/researcher, focus/client-side, focus/dompurify, focus/mxss, focus/sanitizer-bypass, focus/dom-xss, focus/html-parsing]
inbound: []
---

# Kévin Gervot (Mizu)

## Identity

- Real name: Kévin Gervot. Publishes under handle **Mizu**.
- French web-security researcher; day-job pentester at a French firm (his X bio and GitHub README both list "Pentester @ <French company>"); spends free time on client-side research.
- Member of the **Critical Thinking Bug Bounty Podcast research lab** (CTBB lab). One of the CT show's go-to voices on HTML sanitizer internals.
- CTF player on FlatNetworkOrg and Rhackgondins; played on ECSC_TeamFrance in 2023. Frequent author of Root-Me / FCSC web challenge writeups.

## Focus areas

- **DOMPurify internals and bypasses** — the signature topic; he has multiple bypasses against modern DOMPurify (3.1.x) plus a published two-part series mapping bypass surface and misconfiguration patterns end-to-end.
- **Mutation XSS (mXSS)** — exploits HTML's re-parse behavior (node flattening at depth 512, insertion modes, stack of open elements, namespace confusion) to turn sanitized output back into executable markup.
- **Client-side gadget hunting** — JavaScript gadgets that turn HTML-injection into XSS by going around CSP and DOMPurify (see `GMSGadget`).
- **HTML-parsing edge cases** — long-tail browser quirks: Firefox iframe DOM/render desync, character-encoding (ISO-2022-JP) tricks, parser state confusion. Often roots his exploits in spec corners.
- **Tooling for sink discovery** — author of DOMLogger++, the browser extension that hooks sinks for live triage; a fixture in many bug-bounty client-side workflows.

## Online presence

- Personal blog: [mizu.re](https://mizu.re).
- X / Twitter: [@kevin_mizu](https://x.com/kevin_mizu).
- GitHub (org-style profile): [github.com/kevin-mizu](https://github.com/kevin-mizu).
- Profile README repo: [github.com/kevin-mizu/kevin-mizu](https://github.com/kevin-mizu/kevin-mizu).
- DOMLogger++ extension: [github.com/kevin-mizu/domloggerpp](https://github.com/kevin-mizu/domloggerpp) (~790+ stars).
- DOMLogger++ for Caido: [github.com/kevin-mizu/domloggerpp-caido](https://github.com/kevin-mizu/domloggerpp-caido).
- GMSGadget: [github.com/kevin-mizu/GMSGadget](https://github.com/kevin-mizu/GMSGadget).
- Bot-CTF template: [github.com/kevin-mizu/bot-ctf-template](https://github.com/kevin-mizu/bot-ctf-template).
- DOMPurify ISO-2022-JP gist: [gist.github.com/kevin-mizu/9b24a66f9cb20df6bbc25cc68faf3d71](https://gist.github.com/kevin-mizu/9b24a66f9cb20df6bbc25cc68faf3d71).

> Note: searches turned up no Sonar / SonarSource author page for Kévin. SonarSource publishes the canonical [mXSS cheatsheet](https://sonarsource.github.io/mxss-cheatsheet/) and the [mXSS: The Vulnerability Hiding in Your Code](https://www.sonarsource.com/blog/mxss-the-vulnerability-hiding-in-your-code) post (Yaniv Nizry / Sonar R&D), but no public byline ties Mizu to Sonar. Treat the Sonar affiliation as unconfirmed unless a Sonar author page surfaces.

## Key research / posts

- **[Exploring the DOMPurify library: Bypasses and Fixes (1/2)](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes)** (2024-11-17) — Four bypasses against DOMPurify 3.1.0/3.1.1/3.1.2 built on HTML-parsing unpredictability: node flattening at depth 512, insertion-mode abuse, the stack of open elements, and namespace confusion to ship invalid DOM that mutates on reparse. Each subsequent fix is forced into uglier regex territory, culminating in the regex-based attribute filter shipped in 3.1.3. Seeds `../techniques/dom-xss/dompurify-pi-bypass.md`, `../techniques/dom-xss/dompurify-namespace-hijack-getbyid.md`, and `../techniques/dom-xss/dompurify-allowed-uri-regex-anchor.md`.
- **[Exploring the DOMPurify library: Hunting for Misconfigurations (2/2)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations)** (2025-02-10) — Operational follow-up: how to spot a downgraded DOMPurify in the wild. Covers dangerous `ALLOWED_TAGS` / `ADD_URI_SAFE_ATTR` allow-lists, hook footguns (`uponSanitizeAttribute` + `forceKeepAttr`, `beforeSanitizeAttributes` timing → DOM clobbering, `.setAttribute()` from inside hooks), `base href` pollution for URI-attr confusion, namespace-case mismatches (HTML vs SVG `nodeName`), and Unicode `.toUpperCase()` normalization gotchas. Direct seed for `../techniques/dom-xss/dompurify-post-output-replace.md` and the misconfig items in `../techniques/dom-xss/SUMMARY.md`. Also the post Justin walks through on Ep 111.
- **[Abusing Client-Side Desync on Werkzeug](https://mizu.re/post/abusing-client-side-desync-on-werkzeug)** (2023-06-07, SSTIC 2023) — CVE-2022-29361. Werkzeug 2.1.0–2.1.1 keep-alive request parsing lets a same-origin actor smuggle a second request whose response gets cached against the wrong key. Chained with a near-trivial open redirect, poisons a cached JS file → persistent unauthenticated XSS. The "client-side desync as XSS-not-just-ATO" reference.
- **[An 18 years old bug](https://mizu.re/post/an-18-years-old-bug)** (2025-03-01, PwnMe2025) — Firefox iframe desync between the DOM-stored `src` and the rendered `src` (the DOM keeps the original value while the rendering pipeline follows the updated one). Combined with cache-control headers and a deliberately invalid intermediate URL, escapes a sandboxed iframe to read `localStorage` from the parent origin. Filed under browser-quirk territory; relevant to `../techniques/dom-xss/sandbox-srcdoc-base-uri-leak.md` neighbors.
- **[XSS me Luigi](https://mizu.re/post/xss-me-luigi)** — Intigriti-style XSS challenge writeup; useful for the pattern of chaining a small HTML-injection with a DOMPurify-flavored sanitizer bypass against a realistic mitigation stack.
- **[Intigriti March 2023 XSS challenge](https://mizu.re/post/intigriti-march-2023-xss-challenge)** — Earlier monthly-XSS-challenge writeup; representative of his "explain the parser, then the payload follows" style.
- **["Playing with HTML parsing to bypass DOMPurify on default configuration"](https://grehack.fr/)** (GreHack 2024 talk) — Conference version of the (1/2) blog post: same four-bypass set, presented end-to-end with the parser state diagrams.
- **DOMPurify ISO-2022-JP bypass** ([gist](https://gist.github.com/kevin-mizu/9b24a66f9cb20df6bbc25cc68faf3d71)) — Character-encoding-driven bypass: sanitization runs in one encoding context, rendering in another, and the bytes mean different things. The smallest, sharpest example in his catalog.

## Tooling

- **[domloggerpp](https://github.com/kevin-mizu/domloggerpp)** — Browser extension that hooks a customizable set of JS sinks (innerHTML, eval, document.write, postMessage handlers, etc.) and logs hits with stack traces. The de facto starter tool for "is this page actually XSS-able?" triage; pairs cleanly with TLX's static taint output and is referenced in `wiki/tools/` material on client-side dynamic instrumentation.
- **[domloggerpp-caido](https://github.com/kevin-mizu/domloggerpp-caido)** — Caido plugin port. Brings sink-hit logging into the same proxy view that holds the request/response history; relevant to anyone running our `caido-capture` skill on a JS-heavy target.
- **[GMSGadget](https://github.com/kevin-mizu/GMSGadget)** — Collection of JavaScript "gadgets" — `<script>`/`<iframe>`/`<form>` snippets that, when injected as plain HTML against a CSP + sanitizer mitigation stack, still reach script execution. The canonical reference for the "HTML injection → XSS without inline-JS" pattern; pairs with `../techniques/dom-xss/dom-clobbering-to-xss.md`, `../techniques/dom-xss/htmx-csp-bypass.md`, `../techniques/dom-xss/jsonp-callback-csp-bypass.md`, and the prototype-pollution gadget pivots in `../techniques/prototype-pollution/client-side-pp-gadget.md`.
- **[bot-ctf-template](https://github.com/kevin-mizu/bot-ctf-template)** — Headless-Chromium harness template for self-hosting XSS challenges; useful as a reference for our own dynamic confirmation harnesses.

## CT podcast appearances

- [2025-02-20 Ep 111 — How to Bypass DOMPurify in Bug Bounty with Kevin Mizu](../sources/podcasts/ct/) — Walkthrough of the two-part DOMPurify series: bypass categories (mXSS via node manipulation, namespace confusion, allowed-URI-regex anchoring), then misconfig hunting in the wild (hooks, allow-lists, post-output replace). Episode page: [criticalthinkingpodcast.io/episode-111-how-to-bypass-dompurify-in-bug-bounty-with-kevin-mizu](https://www.criticalthinkingpodcast.io/episode-111-how-to-bypass-dompurify-in-bug-bounty-with-kevin-mizu/); HackerNotes write-up: [blog.criticalthinkingpodcast.io/p/hackernotes-ep-111-how-to-bypass-dompurify-with-k-vin-mizu](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-111-how-to-bypass-dompurify-with-k-vin-mizu); YouTube: [youtube.com/watch?v=88cc-3jBll0](https://www.youtube.com/watch?v=88cc-3jBll0).

## Notes

- **DOMPurify-bypass specialist.** If a target ships DOMPurify (or anything that thinks of itself as "another DOMPurify"), Mizu's two-part series is the first thing to re-read before triage. His bypasses target the parser, not the library API — fixes that only patch the API surface tend to remain bypassable.
- **Output style** — long, parser-state-diagrammed writeups; almost always one corner of the HTML spec doing something the developer didn't model. Maps cleanly onto our static taint output: when js_analyzer flags a chain into a DOMPurify call, his blog tells you which configuration knob would make it exploitable.
- **Tooling-first temperament** — every research stream has a companion tool (`domloggerpp` for sink discovery, `GMSGadget` for the gadget catalog, `bot-ctf-template` for the harness). Treat the tools as primary artifacts, not afterthoughts.
- **Collaborators** — works inside the CTBB research lab orbit; Justin Gardner is the most visible bridge. No confirmed Sonar / SonarSource staff affiliation in public sources at time of writing despite topical overlap with the SonarSource mXSS cheatsheet.
- **Cross-refs** — research and tooling feed `../techniques/dom-xss/dompurify-pi-bypass.md`, `../techniques/dom-xss/dompurify-namespace-hijack-getbyid.md`, `../techniques/dom-xss/dompurify-allowed-uri-regex-anchor.md`, `../techniques/dom-xss/dompurify-post-output-replace.md`, `../techniques/dom-xss/dom-clobbering-to-xss.md`, `../techniques/dom-xss/htmx-csp-bypass.md`, and the gadget side of `../techniques/prototype-pollution/client-side-pp-gadget.md`.

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/kevin-mizu/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

