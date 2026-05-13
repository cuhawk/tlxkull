---
title: Android deep-link URL parser disagreement
slug: android-deep-link-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/mobile, technique/url-parsing]
inbound: []
---

# Android deep-link URL parser disagreement

Sergey Toshin (Oversecured) — recurring Android class.

## Pattern
Android URL parsers handle host validation differently across implementations:
- `Uri.getHost()` (Android `android.net.Uri`)
- string match on full URL
- prefix match
- `java.net.URI` (different than `android.net.Uri`)

Craft a deep link whose `getHost()` resolves to trusted domain but a
separate string-check elsewhere in the app sees attacker domain (or vice
versa) → cross-app deep-link hijack.

## Preconditions
- Android app with deep-link intent filter.
- App uses one parser for security check + different parser for action.

## Detection
- Decompile APK with JADX-GUI.
- Find every `Intent.getData()` consumer.
- Check whether host validation uses same parser as the action that
  consumes the URL.
- Run Oversecured scanner first as breadth filter.

## Triggering
Document specific payloads in Oversecured "Android URL parsing tricks" /
"Attack vectors on the View" blog posts.

Common pattern:
- `https://attacker.com\\@trusted.com/path` — backslash parser
  disagreement.
- `https://trusted.com.attacker.com` (TLD regex bypass).
- `https://attacker.com#@trusted.com/cb`.

## Related primitives (Sergey, Ep 38)
- iOS-from-Android port: replay Android deep-link list against iOS — many
  "secure in Android, not iOS" wins.
- Google Play VRP $1000/critical app vuln (100M+ installs, ~500 apps).
  Report there even if developer has own bounty — faster pay, Google
  forces fix.

## Seen in the wild
- Sergey #1 in Samsung's bounty program.
- Quora arbitrary file-read via AnySDK (~$10K early win).
- Critical Thinking Podcast Ep 38.

## References
- Oversecured blog — "Attack vectors on the View" / Golden URL parsing
- Sergey HackerOne disclosed reports
- Critical Thinking Podcast Ep 38
- Bagipro golden URL techniques (also referenced Eps 62, 67)
