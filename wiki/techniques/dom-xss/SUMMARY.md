---
title: DOM XSS — summary
slug: dom-xss-summary
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, summary, index]
inbound: []
---

# DOM XSS — summary

## What this class is

DOM XSS occurs when attacker-controlled data flows from a JavaScript source (e.g. `location.hash`, `document.referrer`, `postMessage` data) into a dangerous DOM sink (e.g. `innerHTML`, `eval`, `document.write`) without sanitization — entirely client-side, no server round-trip required. The payload never appears in the HTTP response body; it executes only in the browser's DOM. It is the primary output class of TLX's `js_analyzer` taint engine.

## When to suspect

- `js_analyzer` source tags: `location.hash`, `location.search`, `location.href`, `document.URL`, `document.referrer`, `window.name`, `postMessage`, `localStorage`, `URLSearchParams`
- `js_analyzer` sink tags: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `document.writeln`, `eval`, `Function()`, `setTimeout(string)`, `setInterval(string)`, `src` on `<script>`, `href` on `<a>` (javascript:), `srcdoc`, `$.html()`, `dangerouslySetInnerHTML`
- Framework patterns: Angular `bypassSecurityTrust*`, React `dangerouslySetInnerHTML`, Vue `v-html`, jQuery `$(tainted).html()`
- URL shapes: fragment-heavy SPAs, `?redirect=`, `?url=`, `#/route/` patterns, apps loading templates from URL params
- Third-party script gadgets (JSONP callbacks, analytics tag managers)
- Source maps present — original pre-minified source often shows raw sink calls

## External references

| Topic | PayloadsAllTheThings path | HackTricks path | PortSwigger |
|---|---|---|---|
| XSS payloads, filter bypass, polyglots | `../../_external/payloads-all-the-things/XSS Injection/` | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/` | — |
| DOM XSS specific | `../../_external/payloads-all-the-things/XSS Injection/` | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/dom-xss.md` | [portswigger-dom-based](../../sources/portswigger-dom-based.md) |
| CSP bypass | `../../_external/payloads-all-the-things/XSS Injection/4 - CSP Bypass.md` | `../../_external/hacktricks/src/pentesting-web/content-security-policy-csp-bypass/` | — |
| XSS filter bypass | `../../_external/payloads-all-the-things/XSS Injection/1 - XSS Filter Bypass.md` | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/` | — |
| XSS polyglots | `../../_external/payloads-all-the-things/XSS Injection/2 - XSS Polyglot.md` | — | — |
| postMessage to XSS | — | `../../_external/hacktricks/src/pentesting-web/postmessage-vulnerabilities/blocking-main-page-to-steal-postmessage.md` | — |
| DOM clobbering | — | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/dom-clobbering.md` | [portswigger-dom-based](../../sources/portswigger-dom-based.md) |
| XSS in Angular | `../../_external/payloads-all-the-things/XSS Injection/5 - XSS in Angular.md` | — | — |
| Steal info via JS | — | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/steal-info-js.md` | — |

## Related local pages

- [postMessage SUMMARY](../postmessage/SUMMARY.md) — postMessage is a common DOM XSS source
- [Prototype Pollution SUMMARY](../prototype-pollution/SUMMARY.md) — PP gadgets frequently escalate to DOM XSS sinks

## Sub-patterns to expand

- [ ] `innerHTML-sink.md` — direct innerHTML assignment from URL fragment
- [ ] `eval-sink.md` — eval/Function/setTimeout with tainted string
- [ ] `document-write-sink.md` — document.write with tainted data
- [ ] `jquery-html-sink.md` — jQuery `.html()`, `.append()` sinks
- [ ] `angular-bypass-trust.md` — `bypassSecurityTrustHtml` misuse
- [ ] `react-dangerously-set.md` — `dangerouslySetInnerHTML` misuse
- [ ] `csp-bypass-chains.md` — CSP present but bypassable via gadget
- [ ] `jsonp-callback-xss.md` — attacker-controlled JSONP callback parameter
- [x] `dom-clobbering-to-xss.md` — clobbering gadgets that reach a sink
- [ ] `postmessage-source-xss.md` — postMessage data flows into sink (see also postmessage/)
- [x] `taint-flow-open-redirect.md` — taint flow from hash/search into location sink (open redirect)
