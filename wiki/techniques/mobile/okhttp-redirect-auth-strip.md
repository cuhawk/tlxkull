---
title: OkHttp redirect Authorization-header strip
slug: okhttp-redirect-auth-strip
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/mobile]
inbound: []
---

# OkHttp redirect Authorization strip

## Pattern
OkHttp drops `Authorization` header on redirects when scheme/host/port
differ. **Custom signing headers pass through, but `Authorization` does
not.**

Attacker controlling a webview-handled URL with bypass + open-redirect
cannot exfil bearer token because OkHttp scrubs it.

Workaround vector: look for transformation/normalisation differences
between Android intent host parsing and OkHttp host parsing (e.g.
backslash → slash) per Bagipro's golden URL tricks. If the two parsers
disagree on hostname, OkHttp may consider host unchanged and KEEP the
auth header on the redirect.

## Preconditions
- Mobile app uses OkHttp.
- Webview / fetch path takes attacker-influenced URL.
- Goal: leak `Authorization: Bearer <token>` cross-host.

## Detection
- Trace `OkHttpClient.Builder()` config in decompiled APK.
- Check `followRedirects(true)` and absence of custom auth interceptor.

## Triggering
Direct attempt fails (OkHttp strips). To bypass:
1. Find host-parser disagreement between intent parser and OkHttp.
2. Craft URL where intent parser sees attacker host, OkHttp sees trusted
   host (or both see "unchanged" same host) → token stays on redirect.

## Related
- [[android-deep-link-bypass]]
- Mobile pre-auth redirect: middleware auto-attaches auth header to
  trusted hosts (Ep 64) — control redirect host, client follows + re-attaches
  token.

## Seen in the wild
- Critical Thinking Podcast Eps 62, 64.

## References
- Critical Thinking Podcast Eps 62, 64
- Bagipro golden URL tricks
