---
title: Ep 73 - Sandboxed IFrames and WAF Bypasses
slug: 20240530-sandboxed-iframes-and-waf-bypasses-ep-73
url: https://www.youtube.com/watch?v=uHOxsmdsXUA
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, iframe, sandbox, waf-bypass, frame-hijack, optional-chaining, csp-redirect]
inbound: []
---

# Ep 73 - Sandboxed IFrames and WAF Bypasses

- Date: 2024-05-30
- video_id: uHOxsmdsXUA
- Speakers: Justin Gardner (JG), Joel Margolis (JM)

## Summary

Johan Carlsson's XSS challenge revealed two related sandboxed-iframe
techniques: a path-based CSP whitelist allows trusting a redirect from
`allowed/script.js` to `evil/script.js`, and `<iframe srcdoc=...
sandbox>` leaks the **top-level** `document.baseURI` even with no
`allow-same-origin`. Sandboxed-iframe `window.open` propagates the
sandbox properties (including `origin: null`) to the new tab - so a
top-level navigation to a trusted bank ends up null-origin and can be
addressed cross-window by another null-origin iframe via a postMessage
handler that does `event.origin == window.origin`. Justin formalized
"frame hijacking": pre-name an iframe identically to a popup-target name
on the victim flow; Chrome will route the popup into the attacker's
iframe. No-WAF-pls - Shubs / Assetnote tool padding HTTP requests with
~8 KB to ~100 MB of `A`s to bypass WAFs by overflowing their inspection
buffers. Optional chaining `?.()` between a function name and its parens
slips past most WAFs that pattern-match on identifier-paren juxtaposition.
A Chrome force-cache CORS exfil (`fetch(url, {cache:'force-cache'})`
against `Access-Control-Allow-Origin: *` cached resources) - fixed by
Chrome since publication.

## Techniques extracted

- [[../../techniques/csp/path-csp-redirect-bypass]] - path-based `script-src` whitelists trust redirect chains; redirect from allowed path to attacker path executes.
- [[../../techniques/dom-xss/sandbox-srcdoc-base-uri-leak]] - `<iframe sandbox srcdoc>` can read top-level `document.baseURI` without `allow-same-origin`.
- [[../../techniques/dom-xss/sandbox-window-open-null-origin]] - `window.open` from a sandboxed iframe inherits the sandbox; the new tab's origin is `null`, enabling cross-window scripting via another null-origin frame.
- [[../../techniques/dom-xss/frame-hijacking-named-iframe]] - pre-name an iframe on attacker.com to match an OAuth/popup target name; Chrome routes the victim's `window.open` into the attacker iframe.
- [[../../techniques/dom-xss/optional-chaining-waf-bypass]] - `alert?.()` slips past WAFs signature-matching on `identifier(`; works in JavaScript optional-chaining context.
- [[../../techniques/dom-xss/waf-padding-bypass]] - `no-waf-pls`: pad request body to 8 KB-100 MB to overflow WAF inspection buffers.
- [[../../techniques/xs-leaks/force-cache-cors-leak]] - Chrome's GET response cache (2-day default for cacheable responses without `Cache-Control: no-store`) plus `fetch(.., {cache:'force-cache'})` against `Access-Control-Allow-Origin: *` cached resources exfiltrates the response. (Fixed.)

## Tools mentioned

- [[../../tools/caido/notes]] - no-waf-pls Caido workflow extension shipped by Justin.

## Quotes

> "If you can make a redirect from okayjavascript to badjavascript, then it will trust that redirection."

> "When a srcdoc is used in iframe in conjunction with that sandbox, you can access the document.baseURI property - and it gives you the URI of the top-level document."

> "I call this bad boy frame hijacking. Make sure whenever you see a new pop-up happening, look to see the window.open call - check the name."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
