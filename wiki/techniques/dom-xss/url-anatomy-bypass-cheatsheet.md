---
title: URL anatomy bypass cheatsheet — 9 positions, 9 attack primitives
slug: url-anatomy-bypass-cheatsheet
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/url-parsing, technique/open-redirect, technique/cheatsheet]
inbound: []
---

# URL anatomy bypass cheatsheet — 9 positions, 9 attack primitives

## Pattern

A full URL has nine positional segments. Each segment is a parser
target with its own bypass repertoire. Use this cheatsheet to map the
position of attacker-controlled data in a target URL and choose the
right primitive.

```
scheme://user:pass@host:port/path;params?query#fragment
   1     2    3    4    5    6     7      8       9
```

### 1. Scheme

- `https:` → `javascript:` / `data:` / `vbscript:` / custom-scheme-from-Android-manifest.
- Whitelist of "starts with https:" — bypass with `https:` exact and `//evil.com` (protocol-relative URLs).
- SSRF candidates: `file://`, `gopher://`, `dict://`, `ftp://`,
  `jar://`, `expect://`. See SSRF Bible.

### 2. Username

- `https://attacker.com\@victim.com` — naïve parsers stop at `\`; browser sends to `attacker.com`. Bypasses open-redirect filters that whitelist `victim.com`.
- See [[../dom-xss/url-credential-payload-smuggling]] for full
  cross-API divergence (`document.URL` vs `location.href` etc.).

### 3. Password

- Same bypasses as username. Some parsers treat the username and
  password segments differently (case-sensitivity, encoding rules).

### 4. Host

- Subdomain trickery: `victim.com.evil-user.net`.
- IDN homoglyph: `vïctim.com`.
- Octal/hex IP encoding for SSRF: `0x7f.0.0.1`, `0177.0.0.1`. See
  [[../server-side/octal-ip-ssrf]].
- `localhost.evil.com` — wildcard DNS records pointing at `127.0.0.1`.

### 5. Port

- Inject illegal characters (`a`, `:`, `\n`); some parsers ignore the
  port and fall back to scheme-default, some throw, some pass through
  to the network library.

### 6. Path

- Path traversal `../` / `..%2f` / `%252e%252e/` (double encoding).
- Case bypass for path-scoped cookies — see
  [[../server-side/path-scoped-cookie-bypass]].
- Path-parameter `;` — see segment 7.

### 7. Path parameters (Orange Tsai `..;`)

- Java + .NET URL parsing strip everything after `;` for routing;
  filters that match on the full URI see the `;` content. Famous
  `..;/admin` bypass.
- Some servers parse `;name=value` into path parameters; if
  reflected, they're a low-visibility injection sink.

### 8. Query

- Parameter pollution (HPP): same key twice — first/last wins varies
  by framework.
- URL-encoding cycles around `&`, `=`, `+`, `space`.
- Reflected XSS / SSRF / IDOR sources.

### 9. Fragment

- Never sent to the server. Use as "URL comment" to truncate
  appended suffixes — if the app does `url + '/api.json'`, supply
  `https://evil.com#` to kill the `/api.json` suffix.
- DOM-XSS source via `location.hash` — see
  [[taint-flow-open-redirect]].

## Preconditions

- Attacker controls some segment of a URL processed by the target.
- A validator inspects the URL and a downstream renderer/router
  parses it differently.

## Detection

- For each URL field, dump the raw value and the post-parse value at
  every boundary (client, WAF, app, downstream API).
- Diff the parses: any disagreement is exploit surface.

## Triggering

(per segment — see segment list above)

## Bypasses

- Combine segments: `\\evil.com#@target.com/...` exploits username
  + fragment + host disagreement.
- Backslash + `@` is the workhorse open-redirect bypass.

## Seen in the wild

- {date: 2023-11-09, source: CT Ep 44} — full 9-segment walkthrough
  with example bypasses for each.

## References

- Orange Tsai BlackHat 2017 / 2018 — A New Era of SSRF / URL Parser
  Confusion talks
- SSRF Bible
- Critical Thinking Podcast Ep 44
- Related: [[../server-side/file-uri-question-mark-parser-skew]],
  [[url-credential-payload-smuggling]],
  [[taint-flow-open-redirect]]
