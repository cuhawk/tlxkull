---
title: Android Intent-URL Scheme Pivots and App-Launch Prompt Bypass
slug: android-intent-url-scheme-pivot
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/mobile, technique/android, technique/intent-url]
inbound: []
---

# Android Intent-URL Scheme Pivots and App-Launch Prompt Bypass

## Pattern

Chromium-based browsers on Android (Chrome, Samsung Internet, WebView)
implement the `intent://` URL scheme that lets a web page launch another
installed app and pass parameters. When two apps register the same scheme
(e.g. both Chrome and Samsung Internet claim `http`), the browser MUST
prompt the user with an "Open with" dialog. **Bypassing that prompt** - so
a click in Chrome silently spawns Samsung Internet on the same URL - is a
bounty-grade primitive because:

1. Older Chromium-based browsers shipped with Android often run far older
   engine versions. Force-pivoting from Chrome (current) to Samsung
   Internet (older) hands the attacker a fresh attack surface (n-day
   browser CVEs).
2. The pivot can elevate severity from "adjacent" to "remote" - a malicious
   web page becomes the entry point to an Android-app exploit chain.

Adjacent quirks the same NDEV TK research exposes:
- Add-to-home-screen spoof (icon/URL mismatch).
- Iframe escape via specific intent-URL malformations.
- Google Assistant routine invocation via `googleapp://deeplink?...` -
  silently triggers user-saved routines without consent (home automation,
  etc.).

## Preconditions

- Target Android device has at least two apps registered for the relevant
  scheme.
- Victim opens an attacker-controlled URL in Chrome (or WebView).
- Browser does not enforce the "Open with" prompt for the malformed intent
  URL.

## Detection

- Static: decompile target app (jadx/apktool) and enumerate
  `<intent-filter>` declarations in `AndroidManifest.xml`.
- Dynamic: craft known-good intent URLs (`intent://...#Intent;package=
  com.sec.android.app.sbrowser;end`) and observe Chrome behavior; absence
  of the chooser dialog is the bug.

## Triggering

Generic intent-URL form:

```
intent://path/data#Intent;scheme=https;package=com.sec.android.app.sbrowser;end
```

Variants exposed by NDEV TK:

- Force-launch another browser without prompt: malformed `package=` value.
- Iframe escape: nest the intent URL inside an iframe and use
  `target=_blank` to break out.
- Google Assistant: `googleapp://deeplink?command=<routine_name>` - chains
  with home-automation routines stored in the victim's account.

## Bypasses

- "Open with" prompt enforced for popular schemes - try less-common schemes
  registered by system apps (Samsung-only schemes, OEM bloatware).
- WebView `shouldOverrideUrlLoading` filtering - bypass via
  data-URL-embedded intent strings, fragment encoding, or by chaining
  through a redirect on an allow-listed origin.

## Seen in the wild

- {date: 2024-11-14, source: CT Ep 97} - NDEV TK reported multiple Android Chrome intent-URL issues, including silent-pivot to Samsung Internet ($3,000 bounty) and Google Assistant routine invocation (status: asked, not fixed).

## References

- NDEV TK writeup - Android Chrome behaviors (referenced in episode).
- Critical Thinking Podcast Ep 97 - <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- Related: [[android-deep-link-bypass]]
