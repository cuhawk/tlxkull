---
title: .NET Remoting ObjRef leak → unauth RCE
slug: dotnet-remoting-objref
created_utc: 2026-05-13T00:00:00Z
updated_utc: 2026-05-13T00:00:00Z
tags: [technique/server-side, technique/rce, technique/dotnet]
inbound: []
---

# .NET Remoting ObjRef leak → unauth RCE

CodeWhite (Markus Wulftange).

## Pattern
.NET Remoting over HTTP requires knowing a per-object random URL string
to invoke methods. CodeWhite's research leaks the object reference URL
via a separate primitive, enabling unauthenticated RCE on exposed HTTP
endpoints.

CVE assigned March 22 2024; patched in Microsoft updates Jan 2024 but
omitted from advisory.

Repo `code-white/HttpRemotingObjRefLeak` ships:
- Vulnerable web app
- Payload generator
- Automated objref-leak script (~100 LOC python)

## Preconditions
- Exposed HTTP endpoint serving .NET Remoting.
- Pre-patch (Jan 2024) Microsoft .NET Remoting framework.

## Detection
- Hunt for any HTTP endpoint serving `application/octet-stream` with
  `.NET Remoting`-style request bodies.
- Probe for `?wsdl`-equivalent enumeration endpoints.

## Triggering
Use `code-white/HttpRemotingObjRefLeak` PoC.

## Related
- Saroosh (NCC Group) 2019 .NET Remoting blog (precursor).
- [[aspnet-machinekey-rce]] (adjacent .NET deserialization class).

## Seen in the wild
- CVE March 22 2024.
- Critical Thinking Podcast Ep 64.

## References
- CodeWhite blog — "Leaking ObjRefs to Exploit HTTP .NET Remoting"
- code-white/HttpRemotingObjRefLeak (GitHub)
- Critical Thinking Podcast Ep 64
