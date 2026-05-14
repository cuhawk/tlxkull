---
title: Android intent TOCTOU - bad-resolve / launch-anywhere
slug: android-intent-toctou-launch-anywhere
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/mobile, technique/android, technique/race-condition, technique/privilege-escalation]
inbound: []
---

# Android intent TOCTOU — bad-resolve / launch-anywhere

DEFCON-33 — kidanhey (formalization extending the classic "bad-resolve"
class of intent vulnerabilities).

## Pattern
Android system services receive an `Intent`, perform a permission /
destination check against it, then **resolve and launch** the resulting
activity. Between check and launch there's a window during which the
intent's resolution can change (e.g. an app installs/uninstalls,
package-manager state updates). The check passes on a safe component,
but the launch lands on a privileged one — privilege escalation.

Two key amplifications kidanhey introduced:

1. **Extending the window**: a large, malformed AndroidManifest forces
   the resolver into a slow path, widening the TOCTOU window enough to
   win the race deterministically.
2. **Resolver-state mutation**: install/uninstall an app between check
   and launch (achievable from a user-installed companion app with
   `INSTALL_PACKAGES` / via shared-uid tricks).

## Preconditions
- Android version with affected intent-resolution flow (talk goes
  into specific versions).
- Attacker app installed (or remote intent delivery via another
  vulnerability).
- A target component reachable post-resolution but not pre-resolution.

## Detection / AI-assisted prompt
Talk closes with a Claude/Gemini-ready prompt to grep decompiled APKs
for the pattern. Loose paraphrase:

> "Find calls where a security or destination check is run on an Intent
> at one point in the code and the same Intent (or one derived from it)
> is launched later in the function body — particularly where state can
> change between the check and the launch."

## Triggering
Code-pattern of vulnerability:
```java
if (isSafe(intent)) {            // TOC
  ... // arbitrary delay / state change here
  startActivity(intent);          // TOU
}
```

## Bypasses / hardening
- Re-validate intent resolution immediately before launch.
- Pin the resolution: capture `ResolveInfo` at check time and launch
  with explicit `ComponentName`.

## Seen in the wild
- {date: 2025-08, source: CT Ep 149} — DEFCON 33 talk.

## References
- DEFCON 33 — "Bypassing intent destination checks: launch-anywhere
  privilege escalation" by kidanhey
- Critical Thinking Podcast Ep 149
- Related: [[postmessage-async-origin-swap-race]] (web analogue),
  [[single-packet-attack]] (race-window-widening idiom)
