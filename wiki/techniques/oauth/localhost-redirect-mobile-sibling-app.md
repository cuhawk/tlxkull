---
title: OAuth localhost callback intercepted by sibling mobile app
slug: localhost-redirect-mobile-sibling-app
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/oauth, technique/redirect-uri, technique/mobile]
inbound: []
---

# OAuth localhost callback intercepted by sibling mobile app

## Pattern
Provider OAuth flows that whitelist `http://localhost:PORT/...` redirect
URIs assume "if you control localhost you already own the box." On
Android (and similarly iOS with custom URL schemes), **any installed
app can bind any unprivileged port > 1024 without additional
permissions**. A malicious app that registers on the same callback port
front-runs / replaces the legitimate desktop-style listener and silently
captures the OAuth code on behalf of the victim's session.

JG covered a researcher who hit this against a major program and got
*informative* — wrongly, in JG's view: "you cannot just let every other
app on the device have access to your account, right? Like that's not okay."

## Preconditions
- Provider's OAuth config accepts `http://localhost:PORT/...` redirect URIs.
- Victim has installed a malicious sibling app (Trojan, sideloaded,
  rogue legitimate app) on the same device.
- Provider does NOT use PKCE (or PKCE secret is reachable by the sibling
  app via Android intent leakage, content provider, etc.).

## Detection
- Inventory all OAuth clients with `localhost` in `redirect_uris`.
- Confirm PKCE is mandatory (S256, not plain).
- Inspect Android manifest patterns: any app can `LISTEN` on
  TCP-localhost without `INTERNET` permission gating.

## Triggering
Build a minimal Android app:
```kotlin
val ss = ServerSocket(8080, 0, InetAddress.getByName("127.0.0.1"))
while (true) {
  val client = ss.accept()
  val req = client.getInputStream().bufferedReader().readLine()
  // req contains the GET /callback?code=... line
  exfilCode(req)
  client.getOutputStream().write("HTTP/1.1 200 OK\r\n\r\nThanks".toByteArray())
}
```
Bind on app start; the next time the user runs the legitimate OAuth flow
the rogue app catches the code first.

## Related
- [[localhost-redirect-open-redirect-chain]] — desktop variant.
- [[redirect-uri-bypass]]
- [[pkce-downgrade]]

## Seen in the wild
- {date: 2025, source: CT Ep 116} — informative-classified report, JG
  pushing back against the program.

## References
- Critical Thinking Podcast Ep 116
- Android: ServerSocket binding rules (any uid >= 10000 can bind > 1024)
