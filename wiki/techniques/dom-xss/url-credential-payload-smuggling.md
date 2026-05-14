---
title: URL-Credential Payload Smuggling via document.URL
slug: url-credential-payload-smuggling
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/waf-bypass, technique/dom-source]
inbound: []
---

# URL-Credential Payload Smuggling via document.URL

## Pattern

The userinfo portion of a URL - `https://USERNAME:PASSWORD@host/path` -
is preserved by some DOM accessors and stripped by others. Specifically:

- `document.URL` returns the **full URL string including userinfo**.
- `window.location.href` returns the URL **with userinfo stripped**.
- The address bar in Chrome/Firefox **does not display** the userinfo at
  all (visually invisible).
- Safari strips the userinfo entirely on navigation (technique
  Chrome/Firefox-only).

This asymmetry creates a payload-smuggling primitive: WAFs that inspect
only the URL path/query never see the userinfo bytes; sinks that read
`document.URL` (or any anchor's `.username` / `.password` property) do.

Researcher: Gareth Hayes (PortSwigger), inspired by a Johan Carlsson Twitter
post.

## Preconditions

- A DOM-XSS sink consumes `document.URL` (or `anchor.username` /
  `anchor.password`).
- WAF inspects the URL but not the userinfo segment.
- Chrome or Firefox victim (Safari mitigates).

## Detection

- `js_analyzer`: tag sinks reading `document.URL` or `<a>.username` /
  `.password`; flag pages where the URL is embedded into an anchor with an
  `id` attribute (DOM clobbering combo).
- Manual: load the target page with
  `https://<payload>:<more-payload>@victim.com/path` and inspect both
  `location.href` and `document.URL` in DevTools.

## Triggering

```html
<!-- victim navigates to: -->
https://"><svg/onload=alert(1)>:any@victim.com/

<!-- if the page embeds document.URL into an anchor with id="x" : -->
<a id="x" href="<the_full_url>">click</a>

<!-- attacker accesses the smuggled payload via DOM clobbering: -->
<script>console.log(x.username, x.password)</script>
```

Userinfo persists across:
- `document.URL` (full string).
- `<a>.username`, `<a>.password` properties on the anchor element.

## Bypasses

- Combine with [[window-name-exfil]] for full data-exfil chain when the WAF
  also blocks function calls.
- For sinks that decode/normalize the URL: feed payload through both
  `username` and `password` segments and reassemble.

## Seen in the wild

- {date: 2024-11-14, source: CT Ep 97} - Gareth Hayes "Concealing Payloads in URL Credentials" research drop.

## References

- PortSwigger research - Concealing Payloads in URL Credentials.
- Critical Thinking Podcast Ep 97 - <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- Related: [[window-name-exfil]], [[dom-clobbering-to-xss]]
