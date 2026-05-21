---
title: Deep Link Mobile CSRF — State Change via Custom URL Scheme
slug: deep-link-mobile-csrf
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/csrf, technique/mobile, technique/deep-link]
inbound: []
---

# Deep Link Mobile CSRF — State Change via Custom URL Scheme

## Pattern

Mobile applications define custom URL schemes (deep links) like
`periscope://follow?user=victim`. When a user clicks a link with a custom
scheme, the OS opens the registered application and passes the URL parameters.
If the application automatically performs a state-changing action (follow,
purchase, settings change) when opened via deep link, without requiring further
user interaction or CSRF protection, any website can trigger this action by
redirecting to the deep link URL.

In the Periscope/Twitter case: the deep link `periscope://follow?user=target`
automatically followed the target user when the victim clicked a link on a
web page. The Periscope app treated the link parameters as trusted without
requiring any token or confirmation.

## Preconditions

- Mobile app has a deep link scheme that triggers state-changing actions.
- No CSRF token or confirmation required when the action is triggered via
  deep link.
- Attacker can craft a link (web page redirect, shortened URL, QR code) that
  opens the deep link.

## Detection

- Enumerate the app's deep link scheme from `AndroidManifest.xml` or iOS
  `Info.plist` (`LSApplicationQueriesSchemes`, `CFBundleURLSchemes`).
- Test each deep link action for automatic execution without confirmation:
  `intent://`, `<scheme>://action?param=value`.
- On iOS: use `window.location = "scheme://..."` from a web page.
- On Android: use `<a href="scheme://...">` or JS redirect.

## Triggering

```html
<!-- Web page that silently follows a Twitter/Periscope account -->
<script>
  window.location = "periscope://follow?user=attacker_account";
</script>
```

Or via `<a href="periscope://follow?user=attacker">` (user click triggers it,
appearing as a normal link).

## Seen in the wild

- 2018 — Twitter/Periscope, awarded bounty twice. The deep link CSRF was
  discovered, paid out, re-tested after a patch, and found to still be
  exploitable (different endpoint or insufficient fix). Paid again on the second
  report.
  [BBRE](https://www.youtube.com/watch?v=lylt9gk7Hy0)

## References

- OWASP Mobile Security Testing Guide — Deep Links
- Android Deep Link security documentation
- See also: [../csrf/_index.md](../csrf/_index.md)
