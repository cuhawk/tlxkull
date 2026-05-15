---
title: Matan Berson (MatanBer)
slug: matanber
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
handles: [matanber, mtnber, matan_ber]
role: researcher
primary_focus: client-side
tags: [person, role/researcher, focus/client-side, focus/chrome-extensions, focus/postmessage, focus/cookies, focus/csti, focus/cspt]
inbound: []
---

# Matan Berson (MatanBer)

## Identity

- **Real name:** Matan Berson
- **Primary handle:** `matanber` (web, GitHub, HackerOne); `MtnBer` on X/Twitter
- **Nationality / base:** Israel
- **Role:** Independent security researcher and bug-bounty hunter
- **Notoriety:** Known for high-impact client-side chains while still a teenager — discovered a Chrome DevTools vulnerability chain at 17. Recurring guest on the Critical Thinking podcast, treated by the hosts as a benchmark voice on client-side methodology.

## Focus areas

- Chrome extension attack surface (content scripts, service workers, isolated worlds, web-accessible resources)
- Cookie-parsing discrepancies, cookie tossing/fixation, cookie jar overflow
- HTTP / Cache API caching abuse and Service Worker poisoning
- postMessage origin/data validation and cross-window messaging
- Client-Side Template Injection (CSTI) and Client-Side Path Traversal (CSPT)
- DOM-XSS via tight-budget gadget chaining

## Online presence

- [matanber.com](https://matanber.com/) — personal site, blog, and self-hosted CTF-style challenges
- [Blog index](https://matanber.com/blog)
- [X / Twitter — @MtnBer](https://twitter.com/MtnBer)
- [GitHub — matanber](https://github.com/matanber)
- [HackerOne — matanber](https://hackerone.com/matanber)
- [Instagram — matan_ber](https://www.instagram.com/matan_ber/)

## Key research / posts

- [Bidding Like a Billionaire — Stealing NFTs With 4-Char CSTIs (2024-07-11)](https://matanber.com/blog/4-char-csti) — Vue.js CSTI in an NFT marketplace where ENS names were truncated to 8 chars, leaving only 4 chars of executable payload. Chains the `_f` filter gadget, template string concatenation via backticks, and `constructor`-based Function construction to escape the budget and spoof bid amounts in MetaMask confirmation dialogs. Canonical reference for tight-budget CSTI escape.
- [Bypassing WAFs to Exploit CSPT Using Encoding Levels (2024-05-10)](https://matanber.com/blog/cspt-levels) — Three-case CSPT-through-WAF technique driven by mismatches between WAF decode count and application decode count (WAF<app uses repeated encoding, WAF>app uses padded path sequences, equal uses `%2e%2e/`). Chain target is CSPT → open-redirect → XSS. See [../techniques/dom-xss/](../techniques/dom-xss/).
- [postMessage-tracker (Chrome extension)](https://github.com/matanber/postMessage-tracker) — Tool. Hooks `addEventListener('message', ...)` and unwraps common error-reporter wrappers (Raven, New Relic, Rollbar, Bugsnag, jQuery) to surface the underlying listener functions, with a visual indicator and console window-path output for replay. See [../techniques/postmessage/](../techniques/postmessage/).
- [domlogger-configs](https://github.com/matanber/domlogger-configs) — Curated DOMLogger++ configs (48★) for catching DOM sinks and postMessage flows in the wild. The de-facto starting config used across CT-adjacent hunters.
- [mnmlsm — CTF challenge from real-world findings](https://github.com/matanber/mnmlsm) — Distilled challenge series based on chains he found in production.
- Chrome DevTools vulnerability chain (disclosed by MatanBer at 17, referenced in CT Ep. 81) — origin of his client-side reputation; no standalone writeup, discussed verbally in [Ep. 81](../sources/podcasts/ct/20240725_aDcK6Z6K2Zc_Crushing_Client-Side_on_Any_Scope_with_MatanBer_Ep._81.en.vtt).
- MetaMask $120K web-accessible-resource clickjacking (discussed in CT Ep. 95) — phishing-warning extension page (web-accessible) redirected to a sensitive transaction-confirmation page, enabling clickjacking of high-value actions. See [../techniques/csp/](../techniques/csp/) for the broader frame-ancestors / web_accessible_resources defense story.

## CT podcast appearances

- [2024-07-25 Ep. 81 — Crushing Client-Side on Any Scope with MatanBer](../sources/podcasts/ct/20240725_aDcK6Z6K2Zc_Crushing_Client-Side_on_Any_Scope_with_MatanBer_Ep._81.en.vtt)
- [2024-10-31 Ep. 95 — Attacking Chrome Extensions with MatanBer — Big Impact on the Client-Side](../sources/podcasts/ct/20241031_ziP4cx_cbg8_Attacking_Chrome_Extensions_with_MatanBer_-_Big_Impact_on_the_Client-Side_Ep._95.en.vtt)
- [2024-11-07 Ep. 96 — Cookies & Caching with MatanBer](../sources/podcasts/ct/20241107_6fBQWALARHg_Cookies_Caching_with_MatanBer_Ep._96.en.vtt)
- [HackerNotes Ep. 95 & 96 (recap)](https://blog.criticalthinkingpodcast.io/p/cookies-caching-attacking-chrome-extensions-with-matanber)
- [HackerNotes Ep. 81 (recap)](https://blog.criticalthinkingpodcast.io/p/hackernotes-ep81-crushing-clientside-scope-matanber)

## Notes

- **Recurring CT guest.** Three appearances in a four-month window in late 2024 (Ep. 81, 95, 96), each in a different sub-domain of client-side (general methodology, extensions, cookies/caching). When a new CT episode touches client-side, his prior episodes are the canonical pre-read.
- **Signature methodology — context before code.** In Ep. 81 he repeatedly pushes "use the app first, then read the JS." Dynamic analysis with DOMLogger++ and DOM Invader to build a sink map, then static review only for the listeners that actually fire. Counter to the SAST-first habit a lot of hunters fall into.
- **DevTools as primary instrument.** Conditional breakpoints used as code-injection points, log points for arg-tracing without pause, event-listener breakpoints on `onbeforeunload` to surface redirect/navigation gadgets, XHR/fetch breakpoints for origin-tracing requests, and overriding `window.open` to break on window-hijack candidates. Worth promoting these into a `tools/browser/devtools-tricks.md` page.
- **Self-XSS escalation chain (Ep. 81).** Canonical recipe: login-CSRF via SSO → cookie-jar overflow to log victim out → cookie fixation using `path=`/`domain=` attribute scoping → redirect gadget delivering the payload → CORS misconfig for final ATO. The path-scoped cookie trick is the load-bearing primitive — different cookies authenticating the victim against different endpoints of the same origin.
- **Cookie-parsing zoo (Ep. 96).** Different backends parse cookies inconsistently; quoted-value smuggling (`x="evilInjection;y=dontControl";smuggledCookie=anyvalue`) and Safari's `}`-breaks-parsing behavior are the gadgets he leans on. Cross-references Ankur Sundara's cookie research and Shazzer for browser-quirk lookup.
- **Cache API as persistence (Ep. 96).** `caches.open()` + `cache.put()` from a one-shot XSS persists a poisoned JS response across reloads; `fetch(url, {cache: "force-cache"})` can return authenticated cached responses to an unauthenticated initiator when initiator context isn't part of the cache key — Mizu's HeroCTF v6 writeup is the canonical demo he points to.
- **Chrome extension threat model (Ep. 95).** Four-component decomposition (manifest, content scripts, service worker, extension pages) plus the isolated-world boundary. Highest-value attack-surface bullets: web-accessible resources that redirect to non-web-accessible pages (the MetaMask pattern), `externally_connectable` misconfigurations exposing `chrome.runtime.onMessageExternal` to attacker origins, content-script DOM injections that survive `isTrusted` checks via synthetic harvested clicks, closed shadow DOM defeated by CSS-exfil and overlay clickjacking. Likely seed for a future `wiki/techniques/browser-extensions/` subtree.
- **Writeup style.** Long-form narrative with embedded code blocks, each post building one gadget at a time. Closer to PortSwigger Research format than to Sammouda's terse PoC chains. Good template when our writeup needs to teach a primitive, not just report a bug.
- **Cross-reference.** Sits at the intersection of [../techniques/postmessage/](../techniques/postmessage/), [../techniques/dom-xss/](../techniques/dom-xss/), and [../techniques/csp/](../techniques/csp/) — many of his chains touch all three. When opening a new client-side audit on a target with extensions, web messaging, or cookie-based session handling, this page is the entry point.
