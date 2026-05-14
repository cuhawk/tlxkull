---
title: Ctrl-Click Top-Level Navigation from Inside an Iframe
slug: ctrl-click-iframe-top-level-nav
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/clickjacking, technique/csrf, technique/iframe]
inbound: []
---

# Ctrl-Click Top-Level Navigation from Inside an Iframe

## Pattern

Normally a click on a link inside an iframe navigates the iframe itself
(unless `target=_top` / `target=_blank` is specified). However,
**Ctrl-click** (or Cmd-click on macOS) on any link forces a top-level
navigation - the link opens in a new tab regardless of iframe scoping.

Practical attack: attacker iframes a target page where a clickable
element triggers an action via top-level navigation (CSRF-via-link,
e.g., `/auth/login_as?token=...`). Without Ctrl-click, the link
navigates the iframe - useful for the attacker (cookie-bearing request
fires) but the attacker doesn't immediately benefit. With Ctrl-click,
the link opens a new tab -> top-level navigation fires the CSRF, the
attacker controls the surrounding page, and can chain.

Justin Gardner's Ep 171 case: needed a CSRF inside an iframe to set a
cookie. The action was bound to a link that required top-level
navigation. The clickjacking PoC asked the victim to Ctrl-click one
button - account takeover.

## Preconditions

- Attacker can frame the victim page (no `X-Frame-Options` /
  `frame-ancestors`).
- Victim flow requires a top-level navigation (a link target, a form
  submission with `target=_blank`).
- The attacker can convince the victim to Ctrl-click via clickjacking
  UI (e.g., "Ctrl+click this link to open in a new tab to continue").

## Detection

- Audit any flow that fires sensitive actions via top-level link
  navigation - these are clickjacking-via-Ctrl-click candidates.

## Triggering

```html
<!-- attacker.com -->
<style>
  iframe { position:fixed; top:0; left:0; width:100%; height:100%;
           opacity:0.01; }
  .lure { position:fixed; top:50%; left:50%; }
</style>
<div class="lure">
  <p>Hold Ctrl and click "Continue" to verify your account.</p>
</div>
<iframe src="https://victim.com/page-with-csrf-link"></iframe>
```

To further refine - see [[svg-enhanced-clickjacking]] for hiding UI
elements unless the Ctrl key is held, lowering victim suspicion.

## Bypasses

- Strict `frame-ancestors` on the victim page - full mitigation.
- Pop-up blocker on Ctrl-click -> unlikely; Ctrl-click is treated as
  user-intentional new-tab.

## Seen in the wild

- {date: 2026-04-23, source: CT Ep 171} - Justin Gardner: used Ctrl-click in an iframe to top-level-navigate a victim's CSRF endpoint, completing a login-CSRF + clickjacking chain to ATO.

## References

- Critical Thinking Podcast Ep 171 - <https://www.youtube.com/watch?v=l5fs7Okdj3o>
- Related: [[keydown-user-gesture-popup]], [[svg-enhanced-clickjacking]], [[frame-hijacking-named-iframe]]
