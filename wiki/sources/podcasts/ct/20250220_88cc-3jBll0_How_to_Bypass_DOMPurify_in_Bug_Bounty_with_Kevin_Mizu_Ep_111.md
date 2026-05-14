---
title: Ep 111 — How to Bypass DOMPurify in Bug Bounty with Kevin Mizu
slug: 20250220-how-to-bypass-dompurify-kevin-mizu-ep-111
url: https://www.youtube.com/watch?v=88cc-3jBll0
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, dompurify, sanitizer, mutation-xss, dom-xss, cookie-fixation, cloudflare-cdn-cgi]
inbound: []
---

# Ep 111 — How to Bypass DOMPurify in Bug Bounty with Kevin Mizu

- Date: 2025-02-20
- video_id: 88cc-3jBll0
- Speakers: Justin Gardner (JG), Kevin Mizu (guest, mizu.re, B-Secure)

## Summary

Two halves. First half is Kevin's chained ATO bug: a same-origin `fetch` →
`document.writeSync` XSS gadget on a useless subdomain combined with a
CloudFlare `cdn-cgi/image` deserialization-style behaviour that
re-fetches an attacker-uploaded image embedding HTML in the EXIF; an
AngularJS gadget bypasses the page's CSP; the chain finishes with a
session-fixation sandwich exploiting a `__Host-` cookie reset
(achieved by sending a malformed `path=/a;domain=` value that confuses
the server's clear-cookie logic) and an authentication-state shadow
where two clients with identical UUID + session-cookie share login.
Second half is Kevin's DOMPurify deep-dive — the practical
misconfigurations bug hunters actually find. Categories: dangerous
allow-lists (adding `iframe srcdoc`, `script`); allow-all `data-*` /
`aria-*` chaining with framework gadgets (Bootstrap UJS, htmx);
`ALLOWED_URI_REGEXP` overrides that drop the `^...$` anchors and let
`javascript:alert(1)//<allowed>.com` slip through; double-call mutation
hijacking via `getElementById` clobbering to swap XML/HTML namespaces;
`replace()` post-sanitization de-mutation (jQuery `<style/>` slash
trick, re-enabled when DOMPurify removed its 2020 guard); plain-text /
no-script context smuggling that survives sanitization because the
browser later reparses the surrounding page. Fingerprinting:
DOMPurify is the only sanitizer that allows `cid:` scheme by default;
in a PDF-render scenario, `<plaintext>` is the universal trick to dump
the post-sanitization output as text. DOM logger++ usage tips:
script-tag-load-event hook + JavaScript event-delegation explanation
(why `onclick` is on `document` not on the element you clicked).

## Techniques extracted

- [[../../techniques/dom-xss/dompurify-pi-bypass]] — append ep 111 entry; Kevin Mizu's research on the post-Slonser bypass landscape.
- [[../../techniques/dom-xss/dompurify-allowed-uri-regex-anchor]] — `ALLOWED_URI_REGEXP` overrides that miss `^...$` anchors let `javascript:` URIs through.
- [[../../techniques/dom-xss/dompurify-namespace-hijack-getbyid]] — two-call DOMPurify pipeline + `getElementById` clobbering swaps the second sanitize from HTML to MathML/SVG namespace.
- [[../../techniques/dom-xss/dompurify-post-output-replace]] — post-sanitize string `replace()` (jQuery `<style/>` 2020 trick) re-enabled after 2024 DOMPurify guard removal.
- [[../../techniques/dom-xss/cloudflare-cdn-cgi-image-exif-xss]] — `cdn-cgi/image` fetches attacker-uploaded image whose EXIF contains HTML; consumed by `document.write` for XSS bypassing CSP via AngularJS gadget.
- [[../../techniques/server-side/cookie-clear-path-confusion]] — `__Host-` cookie session-fixation via malformed `path=/a;domain=` request URI that breaks server-side clear-cookie logic.

## Tools mentioned

- [[../../tools/browser/domlogger-plus-plus]] — Kevin Mizu's DOM-source/sink instrumentation tool; hook the `parse5` / `DOMParser.prototype.parseFromString` call to find post-sanitization mutation points; script-tag-load-event hook for delegated-event gadgets.

## Quotes

> "If you have an HTML injection in a PDF and you don't know what happened with your inputs, use the `<plaintext>` tag — deprecated, converts the rest of the DOM to raw text. That's how you fingerprint what the sanitizer did."

> "The double-underscore-host cookie is a reserved prefix; you cannot set it from JavaScript. But if you don't provide it on the login page, the application will set it for you to the right value — that's the missing piece for session fixation."

> "DOMPurify security solely relies on one regex being executed correctly."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
