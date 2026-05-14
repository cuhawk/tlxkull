---
title: Ep 97 - Bcrypt Hash Input Truncation, Mobile Device Threat Modeling
slug: 20241114-bcrypt-hash-input-truncation-mobile-device-threat-modeling-ep-97
url: https://www.youtube.com/watch?v=m5mR6dvhtpg
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, bcrypt, mobile, intent-url, url-credentials, window-name, lightyear, php-filter-chain, dom-explorer]
inbound: []
---

# Ep 97 - Bcrypt Hash Input Truncation, Mobile Device Threat Modeling

- Date: 2024-11-14
- video_id: m5mR6dvhtpg
- Speakers: Justin Gardner (JG), Joel Margolis (JM)

## Summary

Bcrypt truncates inputs beyond 72 bytes; Okta concatenated username+password+padding into bcrypt, producing predictable hashes for accounts whose username pushed the password out of the truncation window - auth bypass with any password. NDEV TK released a deep-dive on Android Chrome behaviours covering intent-URLs, register-scheme prompts, iframe escapes, Google Assistant deep-link abuse. Gareth Hayes (PortSwigger) published "Concealing Payloads in URL Credentials": `document.URL` exposes the userinfo portion of a URL while `window.location.href` does not, enabling WAF-invisible payload smuggling. Justin demonstrated a window.name-based exfiltration trick: `name=document.cookie` from a tab that an attacker opened persists across the planned redirect and is later read from an attacker page. Lightyear is a new PHP filter chain exploitation tool that dumps tens of KB with small payloads and no PHP warnings. DOM Explorer (YesWeHack) and Multi HTML Parse (Mathias Karlsson) are cyberchef-style pipeline builders for testing parser/sanitizer chains.

## Techniques extracted

- [[../../techniques/server-side/bcrypt-72-byte-truncation]] - bcrypt truncates input to 72 bytes; concatenated identifier+password schemes lose entropy on long usernames.
- [[../../techniques/mobile/android-intent-url-scheme-pivot]] - Android intent-URLs and `intent://` schema allow cross-app launches; missing "open with" prompt is a bounty-grade primitive.
- [[../../techniques/dom-xss/url-credential-payload-smuggling]] - `document.URL` exposes userinfo (`https://user:pw@host`) while `window.location` parses it out - WAF-invisible DOM source.
- [[../../techniques/dom-xss/window-name-exfil]] - `window.name` persists across same-tab navigations and is invisible to WAFs; can be set to `document.cookie` then read from an attacker-controlled origin.
- [[../../techniques/dom-xss/javascript-uri-name-payload]] - `javascript:name` URI returns the value of `window.name` as the document content of the new page under the same origin.
- [[../../techniques/server-side/php-filter-chain-oracle]] - Lightyear: small payloads, tens of KB output, no PHP warnings, GET-parameter-size workaround for PHP filter chain exfil.
- [[../../techniques/dom-xss/parser-pipeline-fuzzing]] - DOM Explorer / Multi HTML Parse pipelines for mutation-XSS hunting across DOMPurify / parse5 / JSXSS / native DOMParser stacks.

## Tools mentioned

- [[../../tools/caido/notes]] - Static-Flow Tanner's markdown notes plugin with replay-tab cross-links.

## Quotes

> "If your username was too long, then it would just create a predictable hash that would never get changed by your password."

> "JavaScript colon name is a full XSS payload - `window.name` persists across refreshes and the WAF never sees it."

> "If you can open another app from Chrome, that's also an issue, like without user authorization."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
