---
title: Ep 171 - Path-Scoped Cookie Hacks with Uppercase, Post-based Raw Protobuf XSS
slug: 20260423-path-scoped-cookie-hacks-uppercase-protobuf-xss-ep-171
url: https://www.youtube.com/watch?v=l5fs7Okdj3o
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
fetched_utc: 2026-05-14T00:00:00Z
kind: podcast
extracted: true
extract_model: claude-code-manual
tags: [source, podcast, ct, protobuf, xss, path-scoped-cookie, uppercase-bypass, clickjacking, cspt-desktop, age-leak-dob]
inbound: []
---

# Ep 171 - Path-Scoped Cookie Hacks with Uppercase, Post-based Raw Protobuf XSS

- Date: 2026-04-23
- video_id: l5fs7Okdj3o
- Speakers: Justin Gardner (JG, solo)

## Summary

Justin's solo recap of bugs from a marathon LHE month. The headline finding
is a raw-protobuf XSS via cross-origin HTML form submission - four
browser-imposed constraints (ASCII range, bare-LF normalization,
text/plain `=` requirement, trailing CRLF) all had to be solved in the
wire-level encoding. He demonstrates the path-scoped cookie bypass:
uppercasing a single character in the URL path causes the browser to
withhold path-scoped cookies (path comparison is case-sensitive) while
back-ends route case-insensitively - selectively dropping one cookie
without touching the others. Two clickjacking refinements: top-level
navigation from inside an iframe via Ctrl-click, and `keydown` (not just
click) satisfies the "user gesture" requirement for `window.open` without
pop-up blocker. CSPT also works on desktop apps: a websocket-received
user-supplied path component, when carrying a path-traversal, hit a
different HTTP endpoint than intended - desktop / IoT apps that speak
HTTP internally are CSPT-vulnerable. PII-impact insight: leaking a
person's age over time leaks their full date of birth (find the day the
number changes). And a shoutout to Lyra's research on SVG-enhanced
clickjacking that makes invisible iframe overlays visually react to
clicks.

## Techniques extracted

- [[../../techniques/dom-xss/post-based-protobuf-xss]] - full constraint suite to land XSS via wire-format protobuf in a text/plain form POST.
- [[../../techniques/server-side/path-scoped-cookie-bypass]] - uppercase path variant selectively drops path-scoped cookies on case-sensitive cookie/case-insensitive backend mismatch.
- [[../../techniques/dom-xss/cspt-on-desktop-apps]] - CSPT generalises to any app with internal HTTP - desktop, IoT, websocket bridges.
- [[../../techniques/dom-xss/age-to-dob-leak]] - leaking a person's age across days reveals their full date of birth (find the change-day).
- [[../../techniques/dom-xss/keydown-user-gesture-popup]] - `keydown` satisfies the browser's user-gesture requirement for unblocked `window.open` (not just `click`).
- [[../../techniques/dom-xss/ctrl-click-iframe-top-level-nav]] - Ctrl-click on a link inside an iframe triggers a top-level navigation, usable in CSRF + clickjacking chains.
- [[../../techniques/dom-xss/svg-enhanced-clickjacking]] - Lyra's SVG-overlay clickjacking: invisible buttons render visual click feedback, lowering victim suspicion.

## Tools mentioned

- [[../../tools/protoscope]] - needed to encode/decode hand-crafted protobuf payloads for the XSS chain.

## Quotes

> "Capital letters are really overpowered. The back-end was processing it as the same path, but the browser was not sending the cookie because the cookie was hard scoped to a specific path that did not have that capital letter."

> "If you leak the age of a person you also leak their birthday, their full date of birth, because you can just look at that age and then find the day that it changes."

> "CSPTs work not only on web apps but also on desktop apps or any other type of app - anything that interacts with HTTP can be CSPT."

## Cross-links

- [[../README.md]]
- [[../extracts.md]]
