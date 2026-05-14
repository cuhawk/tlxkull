---
title: Sandbox-Propagated window.open - Null-Origin Tab Hijack
slug: sandbox-window-open-null-origin
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/iframe, technique/sandbox-escape]
inbound: []
---

# Sandbox-Propagated window.open - Null-Origin Tab Hijack

## Pattern

When `window.open` is invoked from a sandboxed iframe, the new tab
**inherits the same sandbox flags** as the iframe. Even when the
navigation targets a fully-trusted origin (e.g., `https://bank.com`), the
new tab's effective origin is `null` because the sandbox does not include
`allow-same-origin`.

Consequence: another null-origin iframe (or another sandboxed tab) under
attacker control can postMessage and even script the new tab if the
victim's code does an `event.origin == window.origin` check (`null ==
null` -> true). Cookies for the trusted origin are still sent on the
initial navigation, so the victim's authenticated content lands in the
null-origin tab - and the attacker can then read or rewrite the DOM
cross-window via origin-loose handlers.

Researcher: documented at blog.huli.tw (cited in episode); widely
exploitable.

## Preconditions

- Attacker controls a sandboxed iframe on the victim page (often via
  `iframe srcdoc=` with an attribute-injection bug).
- Victim flow involves a `window.open` from the sandboxed iframe (or
  attacker triggers one via a click on a link inside the iframe).
- The target popup origin's postMessage handler trusts `event.origin
  == window.origin` style checks.

## Detection

- `js_analyzer`: list sandboxed iframe origins, then trace `window.open`
  calls from each.
- Audit postMessage listeners: any handler whose origin check is
  `==`/`endsWith` against the receiver's own origin is suspect.

## Triggering

```html
<!-- attacker.com -->
<iframe sandbox="allow-scripts allow-popups" src="https://attacker.com/clickbait.html"></iframe>

<!-- attacker.com/clickbait.html -->
<a href="https://bank.com/profile" target="_blank">click me</a>
<!-- Click -> bank.com loads with null origin + bank.com cookies -->
```

After the popup loads, a second sandboxed iframe on attacker.com can
postMessage to the popup. If bank.com's handler checks
`event.origin === window.origin` (both null), the check passes.

## Bypasses

- bank.com's CSP `frame-ancestors`/`X-Frame-Options` does NOT mitigate -
  the navigation is a top-level open, not an embedding.
- Mitigation requires explicit origin whitelist in postMessage handlers
  (no `== window.origin` shortcut).

## Seen in the wild

- {date: 2024-05-30, source: CT Ep 73} - Justin Gardner: nearly chained this exploit; one mitigating factor blocked the final delivery, but technique is generally applicable. blog.huli.tw publication referenced.

## References

- huli.tw - "iframes and window.open" deep dive (cited in episode).
- HTML spec - sandbox flag inheritance on window.open.
- Critical Thinking Podcast Ep 73 - <https://www.youtube.com/watch?v=uHOxsmdsXUA>
- Related: [[sandbox-srcdoc-base-uri-leak]], [[iframe-sandwich-cross-tab]], [[frame-hijacking-named-iframe]]
