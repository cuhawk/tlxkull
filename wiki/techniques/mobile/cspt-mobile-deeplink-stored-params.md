---
title: Mobile CSPT via link-shortener-stored params dispatched through deeplink
slug: cspt-mobile-deeplink-stored-params
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [technique/mobile, technique/cspt, technique/deep-link, technique/path-traversal]
inbound: []
---

# Mobile CSPT via link-shortener-stored params dispatched through deeplink

CT Ep. 175 — Joel Margolis. Second-order CSPT inside a mobile app
where the path-traversal vector arrives via a custom-link-shortener
the app trusts.

## Pattern

The mobile app registers a deeplink for short URLs from a vendor-run
shortener (`https://lnk.vendor/<id>`). The shortener service stores
extra JSON params alongside each short link; the app resolves the
short link via the shortener's API (using a key embedded in the APK),
gets back the stored JSON, and dispatches one of ~27 actions based on
the JSON. At least one action embeds an attacker-controlled value
into the *path* of a downstream POST request that is then sent with
the **victim's** API key.

Result: arbitrary POST verb → arbitrary endpoint on the API, victim-
auth'd, attacker controls the query string (not the body).

## Preconditions

- Mobile app handles a deeplink whose payload is fetched from a vendor
  service (link shortener, dynamic-link service, deferred-deeplink
  provider).
- API key for that vendor service is recoverable from the app (embedded,
  reachable via runtime hooks, or attacker-issued).
- At least one of the deeplink-dispatched actions concatenates a value
  from the fetched JSON into a URL path *before* a network request is
  emitted with the victim's session.

## Detection

- Decompile the APK / `frida-trace` the URL-resolution code path. Look
  for `String.format("%s/%s/...", base, untrustedField)` shapes inside
  deeplink handlers.
- Enumerate every dispatched action: a 27-branch switch with one path-
  concatenating case is the historical signature.
- Static: any field that flows from a shortener-fetched JSON into a
  `Request.Builder().url(...)` / `URL(base, segment)` without
  encoding.

## Triggering

Attacker creates the shortener entry via the leaked API key:

```http
POST /api/v1/links HTTP/1.1
Host: lnk.vendor
X-Api-Key: <leaked-from-apk>
Content-Type: application/json

{
  "target": "https://app.vendor/open",
  "params": {
    "action": "loadResource",
    "id": "x#/../admin/<endpoint>?victimParam=attackerValue"
  }
}
```

Victim taps the shortened link → app launches → fetches stored params
→ `loadResource` builds `POST https://api.vendor/v1/resources/<id>` →
`#` truncates fragment, `..` traverses, victim-auth'd POST lands on
`/v1/admin/<endpoint>` with attacker query params.

Body uncontrolled, but **query params often double as body** server-
side (many frameworks merge `request.params`), recovering most of the
impact. See [[../server-side/cspt-impact-gadgets]] for the impact-
chaining cookbook Joel used to convert this from "path traversal in a
POST" into financial-loss + account-modification + access-grant.

## Bypasses / hardening

- App side: never concatenate a field from an untrusted service into a
  URL path. Allowlist the segment values; reject anything containing
  `/`, `..`, `#`.
- Service side: lock the shortener API key behind a per-user token, not
  an app-wide key embedded in the APK.

## Seen in the wild

- {date: 2026-05-22, source: CT Ep. 175} — Joel Margolis, mobile-app
  finding. Impact: financial loss endpoint, account-modification
  endpoint, request-access auto-approval (suspected).

## Related

- [[../dom-xss/cspt-on-desktop-apps]] — same idea, desktop variant.
- [[android-deep-link-bypass]] — getting the deeplink to fire.
- [[../server-side/deep-link-mobile-csrf]] — adjacent CSRF-via-deeplink
  pattern.
- [[../server-side/cspt-impact-gadgets]] — converting low-impact CSPT
  to high-impact.

## References

- Critical Thinking Podcast Ep. 175 — "Rhyno's Hackbot Setup, Sick Bugs
  and ZDI Drama" (2026-05-21).
  [CT Ep. 175](wiki://podcasts/ct/20260521_v-XhQHy_jHM_Rhyno_s_Hackbot_Setup_Sick_Bugs_and_ZDI_Drama_Ep._175)
