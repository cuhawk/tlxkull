---
title: postMessage — summary
slug: postmessage-summary
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/postmessage, summary, index]
inbound: []
---

# postMessage — summary

## What this class is

`window.postMessage` vulnerabilities occur when a page's `message` event listener fails to validate the `event.origin` against an allowlist, or when it processes the `event.data` payload without sanitization before passing it to a dangerous sink. An attacker-controlled page (e.g. served via an open redirect or a cross-origin iframe) sends a crafted message that the listener trusts and acts on — leading to DOM XSS, sensitive data exfiltration, CSRF-like state changes, or OAuth token theft from popup windows.

## When to suspect

- `js_analyzer` source tags: `message` event listener (`addEventListener('message', ...)`, `window.onmessage`)
- Origin check patterns: `event.origin === '*'`, missing origin check, `event.origin.includes('example.com')` (bypassable with `evil-example.com`), `event.origin.startsWith('https://trusted')` (bypassable with subdomain)
- Sink tags downstream of `event.data`: `innerHTML`, `eval`, `location.href`, `document.write`
- SPA apps with embedded iframes, OAuth popup flows, or widget/embed SDKs
- Broadcast channels, BroadcastChannel API — same trust issues as postMessage
- URL patterns: `?redirect=`, `?next=`, `?callback=` used to construct frame URLs
- Source maps often reveal inner message routing logic stripped from production bundle

## External references

| Topic | PayloadsAllTheThings path | HackTricks path |
|---|---|---|
| postMessage vulnerabilities | — | `../../_external/hacktricks/src/pentesting-web/postmessage-vulnerabilities/` |
| Blocking main page to steal postMessage | — | `../../_external/hacktricks/src/pentesting-web/postmessage-vulnerabilities/blocking-main-page-to-steal-postmessage.md` |
| Bypassing SOP with iframes (postMessage exfil) | — | `../../_external/hacktricks/src/pentesting-web/postmessage-vulnerabilities/bypassing-sop-with-iframes-1.md` |
| Steal postMessage via iframe location | — | `../../_external/hacktricks/src/pentesting-web/postmessage-vulnerabilities/steal-postmessage-modifying-iframe-location.md` |
| XSS payloads for postMessage sinks | `../../_external/payloads-all-the-things/XSS Injection/` | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/dom-xss.md` |
| DOM clobbering (can set up postMessage path) | — | `../../_external/hacktricks/src/pentesting-web/xss-cross-site-scripting/dom-clobbering.md` |

## Related local pages

- [DOM XSS SUMMARY](../dom-xss/SUMMARY.md) — postMessage data is a top-tier DOM XSS source
- [OAuth SUMMARY](../oauth/SUMMARY.md) — OAuth popup → parent postMessage is a common token exfil vector
- (none yet)

## Sub-patterns to expand

- [ ] `wildcard-origin.md` — listener uses `*` or no origin check
- [ ] `origin-bypass.md` — weak origin check bypassable via subdomain/prefix
- [ ] `postmessage-to-xss.md` — event.data flows into innerHTML/eval
- [ ] `postmessage-oauth-token-theft.md` — OAuth popup sends token; attacker frame intercepts
- [ ] `postmessage-csrf.md` — postMessage triggers state-mutating action without re-validation
- [ ] `broadcast-channel-vuln.md` — BroadcastChannel with same trust gaps
