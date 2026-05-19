---
title: Sergey Toshin
slug: sergey-toshin
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-19T14:42:00Z
handles: [bagipro, _bagipro]
role: researcher
primary_focus: mobile-android
tags: [person, role/researcher, focus/mobile-android, focus/oem-samsung, focus/oem-xiaomi, focus/intent-redirection, focus/content-providers, vendor/oversecured]
inbound: []
---

# Sergey Toshin

## Identity

- **Real name:** Sergey Toshin
- **Primary handle:** `bagipro` (HackerOne), `_bagipro` (X / Twitter)
- **Role:** founder & CEO of [Oversecured](https://oversecured.com); independent mobile-security researcher
- **Notoriety:** #1 all-time researcher on the Google Play Security Rewards Program; #1 on the Samsung Mobile Security program; first solo hunter to publicly self-fund a security startup ($1M+) entirely from Android bounty earnings (TechCrunch, Nov 2020).

## Focus areas

- Android pre-installed / OEM app surface (Samsung, Xiaomi, Google AOSP apps)
- Intent redirection and unprotected exported components → privilege escalation
- Deep-link / URI-handler abuse → token theft and ATO
- Content Provider weaknesses (path-traversal, `grantUriPermissions`, arbitrary file read/write)
- WebView mis-use (intent-scheme URL parsing, `shouldOverrideUrlLoading` selectors)
- Dynamic code loading as a persistence + RCE primitive on Android

## Online presence

- [Oversecured company site](https://oversecured.com)
- [Oversecured blog](https://oversecured.com/blog) (primary research output; legacy URL `blog.oversecured.com` 301s here)
- [X / Twitter — @_bagipro](https://x.com/_bagipro)
- [HackerOne — bagipro](https://hackerone.com/bagipro)
- [LinkedIn](https://www.linkedin.com/in/bagipro/)
- [Oversecured GitHub org](https://github.com/oversecured) — hosts `ovaa` (Oversecured Vulnerable Android App), `OversecuredVulnerableiOSApp`, plus CI integrations (`oversecured-github`, `oversecured-bitrise-step`, `oversecured-android-gradle`, `oversecured-azure-extension`).
- [HackerOne interview — Hacker Spotlight: bagipro](https://www.hackerone.com/blog/hacker-spotlight-interview-bagipro)
- [TechCrunch — Oversecured launch (Nov 2020)](https://techcrunch.com/2020/11/12/oversecured-mobile-app-security-bug-bounty/)

## Key research / posts

OEM / pre-installed app series:

- [Two weeks of securing Samsung devices: Part 1 (Apr 2021)](https://oversecured.com/blog/two-weeks-of-securing-samsung-devices-part-1) — pre-installed Samsung apps (Managed Provisioning, Secure Folder, Knox, DeX) chained to read/write arbitrary files as system, install apps with device-admin, edit contacts / SMS. Patched in Samsung Apr–May 2021 monthly updates.
- [Two weeks of securing Samsung devices: Part 2 (Aug 2021)](https://blog.oversecured.com/Two-weeks-of-securing-Samsung-devices-Part-2/) — follow-up batch on the same Galaxy-S10+ verified scope; further system-uid escalations via implicit-intent hijacks.
- [20 Security Issues Found in Xiaomi Devices (Apr 2024)](https://blog.oversecured.com/20-Security-Issues-Found-in-Xiaomi-Devices/) — 20 distinct flaws across Mi Video, Mi Browser, Gallery, GetApps, MIUI System Apps; arbitrary activity / receiver / service access with system privileges, account-info disclosure via implicit broadcasts. See [../techniques/mobile/android-intent-url-scheme-pivot.md](../techniques/mobile/android-intent-url-scheme-pivot.md).

Android primitive deep-dives:

- [Android deep link vulnerabilities: how intent filters lead to account takeover (2026)](https://oversecured.com/blog/android-deep-link-vulnerabilities) — canonical writeup on `exported=true` + `BROWSABLE` + missing param validation as the dominant ATO setup. Direct seed for [../techniques/mobile/android-deep-link-bypass.md](../techniques/mobile/android-deep-link-bypass.md).
- [Interception of Android implicit intents](https://blog.oversecured.com/Interception-of-Android-implicit-intents/) — implicit-broadcast hijack pattern that recurs throughout the Samsung and Xiaomi series.
- [Android: Access to app protected components](https://blog.oversecured.com/Android-Access-to-app-protected-components/) — non-exported-component access via intent selectors; underlies WebView intent-scheme bypasses. See [../techniques/mobile/android-intent-url-scheme-pivot.md](../techniques/mobile/android-intent-url-scheme-pivot.md).
- [Android security checklist: WebView](https://blog.oversecured.com/Android-security-checklist-webview/) — `shouldOverrideUrlLoading` + `Intent.parseUri` selector bypass; recommends filtering the selector, not just the scheme.
- [Gaining access to arbitrary Content Providers](https://blog.oversecured.com/Gaining-access-to-arbitrary-Content-Providers/) — provider path-traversal + `grantUriPermissions` abuse template.
- [Content Providers and the potential weak spots they can have](https://blog.oversecured.com/Content-Providers-and-the-potential-weak-spots-they-can-have/) — companion checklist for content-provider review.
- [Android security checklist: theft of arbitrary files](https://blog.oversecured.com/Android-security-checklist-theft-of-arbitrary-files/) — the "steal arbitrary files from another app" recipe; primary pattern behind the TikTok and Google Pay chains.

Vendor-specific landmark chains:

- [TikTok Android — session-token / arbitrary-file theft (Sep 2020)](https://techcrunch.com/2020/09/11/tiktok-android-bugs-account-hijack/) — local malicious app pivots to TikTok session tokens + permission hijack (camera / mic / media). Pre-Oversecured-launch flagship disclosure.
- [Why dynamic code loading could be dangerous for your apps: a Google example](https://blog.oversecured.com/Why-dynamic-code-loading-could-be-dangerous-for-your-apps-a-Google-example/) — Google app: intent redirection → vulnerable content provider with `grantUriPermissions` → write arbitrary Google Play Core module → persistent local RCE inheriting Google-account / Gmail / SMS / mic / location permissions. Fixed May 2021.
- [Intent redirection in popular Android apps (Daily Swig coverage)](https://portswigger.net/daily-swig/intent-redirection-vulnerabilities-in-popular-android-apps-spotlight-danger-of-dynamic-code-loading-warn-researchers) — meta-summary of the dynamic-code-loading attack class he popularised.

## CT podcast appearances

- [2023-09-28 Ep. 38 — Mobile Hacking Maestro: Sergey Toshin](../sources/podcasts/ct/20230928_W6UWw0L01sE_Mobile_Hacking_Maestro_Sergey_Toshin_Ep._38.en.vtt)

## Notes

- Workflow: bulk-downloads hundreds of Android APKs, runs them through his in-house static scanner (productised as Oversecured), and triages the hits — methodology mirrors the JS-callgraph approach we use in `tlx/`, just retargeted at Smali / Java bytecode. Confirmed by his own HackerOne interview: "I download hundreds of apps from different programs and scan them, then report bugs."
- Signature pattern: chain a public exported component (Activity / Receiver / Provider) with an attacker-controlled intent / URI that the app implicitly trusts → land in a privileged context (system_uid, content provider with `grantUriPermissions`, deep-link auth callback) → steal files or mint tokens. Almost never a single-step bug; always a 2–4 hop pivot.
- OEM bias: targets Samsung and Xiaomi disproportionately because pre-installed OEM apps run with platform-level privileges and ship un-obfuscated, making static review trivial. Same dynamic applies to other Tier-1 OEMs (LG, Huawei, OPPO) — worth probing when scope allows.
- Style: terse, code-snippet-heavy posts; always includes the malicious-app PoC manifest + `Intent` constructor. Good template for our own mobile findings.
- Cross-references in our wiki: nearly every page under [../techniques/mobile/](../techniques/mobile/) traces some primitive back to an Oversecured post — keep this dossier as the canonical link hub when ingesting future mobile sources.
- He's Ukrainian-Russian (Moscow-based at company founding, displays a Ukrainian flag on his X profile post-2022). Public posture is apolitical-technical; vendor-disclosure relationships with Samsung and Google are intact.

## Wiki RAG ingestion

Blog bodies ingested 2026-05-19 into the `wiki` Chroma collection.
Source files:

- `wiki/sources/blogs/personal/oversecured/`

Query via `docs_query(collection="wiki", query="...")` instead of WebFetch.

