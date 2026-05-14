---
title: Frame Hijacking - Named-Iframe Popup Capture
slug: frame-hijacking-named-iframe
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/iframe, technique/oauth]
inbound: []
---

# Frame Hijacking - Named-Iframe Popup Capture

## Pattern

`window.open(url, name)` reuses an existing browsing context that already
has that `name` in the tab group, instead of creating a new tab. An
attacker page that:

1. Pre-creates an iframe with `name="<victim_popup_name>"`.
2. Embeds the victim origin inside that iframe (a no-frame-options or
   path-specific iframeable page is enough - the URL doesn't have to be
   the OAuth flow itself, just same-origin).
3. Causes the victim page (now loaded in a child iframe) to perform
   `window.open(oauthUrl, victim_popup_name)`.

...hijacks the popup: instead of opening a new tab, the OAuth flow renders
into the attacker-controlled iframe. The attacker now holds a window
reference and can redirect the iframe at any moment - to an attacker-
hosted callback that captures the OAuth code, for example.

Justin Gardner's name: "frame hijacking". Works in Chrome (same browsing
context group), not Firefox (Firefox de-duplicates names differently),
not Chrome incognito (anti-tracking restrictions).

## Preconditions

- The victim flow uses `window.open(url, name)` with a guessable `name`
  argument (very common: literal strings like `"oauth_popup"`, `"auth"`,
  `"login_window"`).
- Some page on the victim origin is iframeable (no `X-Frame-Options:
  DENY` / `frame-ancestors`).
- The victim navigates from the attacker page (so attacker iframe and
  victim iframe share a browsing-context group).

## Detection

- Static: `js_analyzer` -> list every `window.open` call where the second
  argument is a string literal or a deterministic identifier.
- Manual: visit the OAuth/popup flow page, check DevTools for the popup
  name.

## Triggering

```html
<!-- attacker.com -->
<iframe src="https://victim.com/some-iframeable-page"
        name="oauth_popup"></iframe>

<a href="https://victim.com/flow-that-opens-popup" target="_blank">
  click for cool stuff
</a>
```

When the victim's flow page runs `window.open('https://idp.com/oauth?...',
'oauth_popup')`, the iframe - same name, same browsing-context group -
absorbs the navigation. Attacker reads the iframe contents (same origin
with victim.com since the iframe started on victim.com), or redirects to
an attacker callback to capture credentials.

The same-origin reads work because the navigation didn't change the
*containment frame* - only its contents - so the parent reference to the
frame is unchanged.

## Bypasses

- Random per-flow names (UUID-based) - full mitigation.
- `noopener` / `noreferrer` on the trigger - fully detaches the window
  reference.
- `target="_top"` instead of named target - bypasses the technique.

## Seen in the wild

- {date: 2024-05-30, source: CT Ep 73} - Justin Gardner formalized "frame hijacking" on the episode; multiple targets observed using deterministic popup names.

## References

- Chrome browsing-context-group docs.
- Critical Thinking Podcast Ep 73 - <https://www.youtube.com/watch?v=uHOxsmdsXUA>
- Related: [[sandbox-window-open-null-origin]], [[iframe-sandwich-cross-tab]]
