---
title: CSPT on Desktop / IoT Apps (Non-Web HTTP Surfaces)
slug: cspt-on-desktop-apps
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/cspt, technique/desktop, technique/iot]
inbound: []
---

# CSPT on Desktop / IoT Apps (Non-Web HTTP Surfaces)

## Pattern

Client-Side Path Traversal (CSPT) is usually presented as a web-app
technique, but it applies to **any application that builds an HTTP URL
from user input and fetches it client-side**. Desktop apps, IoT
firmwares, mobile apps, and websocket bridges all routinely do this -
often without the layered defences a web SPA has.

Concrete example (Justin Gardner, Ep 171): a desktop app received user
input over a websocket and incorporated it into an HTTP path. A path
traversal in the input truncated the intended path and hit a completely
different internal endpoint - high-impact remote primitive from a
remote-machine attacker who could reach the websocket.

Architecturally relevant surfaces:
- Electron / Tauri apps with local HTTP bridges.
- IoT devices with cloud-control daemons.
- Mobile apps using local HTTP servers (Cordova, common in older
  hybrid apps).
- Print spoolers, media servers, anything that exposes an HTTP API on
  localhost.

## Preconditions

- Application incorporates external input (websocket, IPC message,
  query parameter from a custom URL scheme handler, etc.) into an HTTP
  path used by an internal fetch.
- The internal HTTP server routes paths in a way that allows traversal
  to a different endpoint (most do - Express, FastAPI, Spring, all
  resolve `..` similarly to web frameworks).

## Detection

- Reverse-engineer the app's HTTP wiring: identify all internal HTTP
  endpoints (proxy through Charles / mitmproxy with localhost CA, or
  read source if available).
- For each input source (websocket message, custom URL scheme handler,
  cloud-pushed config), trace whether the value ends up in an HTTP path.
- Probe with `../../different/endpoint` and observe.

## Triggering

Generic websocket payload:

```json
{
  "type": "fetch_resource",
  "id": "../../admin/system_dump"
}
```

Generic custom-URL-scheme payload (mobile / desktop):

```
myapp://load?path=../../config/secrets.json
```

## Bypasses

- Apps that URL-encode `/` before insertion mitigate; verify with
  manual encoding tricks (`%2F`, double-encode `%252F`, `..\` on
  Windows-built apps).
- Server-side normalization may strip - test the actual exposed
  endpoint set.

## Seen in the wild

- {date: 2026-04-23, source: CT Ep 171} - Justin Gardner: desktop app received websocket-supplied path component; path-traversal hit a different internal endpoint than intended; high-impact remote primitive.

## References

- Critical Thinking Podcast Ep 171 - <https://www.youtube.com/watch?v=l5fs7Okdj3o>
- Related: [[cspt-fetch-hijacking]], [[cspt-cache-deception-chain]]
- Mobile sibling: [cspt-mobile-deeplink-stored-params](../mobile/cspt-mobile-deeplink-stored-params.md)
- Impact-chaining cookbook: [cspt-impact-gadgets](../server-side/cspt-impact-gadgets.md)
