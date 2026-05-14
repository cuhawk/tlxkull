---
title: ASP.NET MVC view-engine default-path RCE via arbitrary file write
slug: aspnet-mvc-view-engine-path
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/aspnet, technique/file-write, technique/rce]
inbound: []
---

# ASP.NET MVC view-engine default-path RCE via arbitrary file write

## Pattern

ASP.NET MVC's default Razor view engine resolves view files by
convention. For a request to `/Foo/Bar`, the engine probes a fixed
sequence of relative paths under the application root:

```
~/Views/Foo/Bar.cshtml
~/Views/Foo/Bar.vbhtml
~/Views/Shared/Bar.cshtml
~/Views/Shared/Bar.vbhtml
~/Areas/.../Views/Foo/Bar.cshtml
... (many more)
```

The probing happens *before* any web.config request-filtering takes
effect for the rendered file. So even when a strict `web.config`
allow-list forbids all extensions, the view engine still reads and
renders an attacker-written `cshtml` from one of the default paths —
because Razor reads it through internal APIs, not as an HTTP-served
asset.

Combine with an arbitrary-file-write primitive (LFI-to-write, archive
extraction traversal, log poisoning that flushes to a writable path):
write `Bar.cshtml` to `/Views/Foo/`, then GET `/Foo/Bar` — Razor
compiles and executes the cshtml. RCE.

Researcher: FSI (Critical Thinking Research Lab post on this).

## Preconditions

- ASP.NET MVC application using the default Razor view engine
  (`RazorViewEngine`).
- An arbitrary-file-write primitive that can target paths under
  `/Views/` or `/Areas/`.
- `web.config` may forbid serving `.cshtml` directly (200 → 404), but
  this doesn't matter — the view engine reads the file internally.

## Detection

- Run `procmon` against the worker process (or hook `File.OpenRead`)
  while hitting `/Foo/Bar`.
- Observe the probe sequence — every path the engine tries is a
  candidate write target.

## Triggering

```
# attacker write primitive places file at:
~/Views/Foo/Bar.cshtml

# contents:
@{ System.Diagnostics.Process.Start("cmd", "/c whoami > C:\\temp\\out"); }

# trigger:
GET /Foo/Bar HTTP/1.1
```

## Bypasses

- If `/Views/` is read-only, target `/Areas/<Area>/Views/`.
- If RazorView engine is disabled, look for other view engines
  (`WebFormViewEngine` — `.aspx`).
- Master-page / layout paths (`_Layout.cshtml`) are also auto-loaded
  — drop a malicious layout to compromise every view rendered.

## Seen in the wild

- {date: 2025-11-27, source: CT Ep 150} — FSI's CTBB research-lab post
  with full probe-path enumeration; demonstrated against a target
  with file-write but no served-extension permissions.

## References

- FSI's CTBB research-lab writeup (ASP.NET MVC view engine search
  patterns)
- Critical Thinking Podcast Ep 150
- ASP.NET MVC view-engine documentation
- Related: [[../dom-xss/cspt-react-useparams]] (different framework,
  same "internal path resolution" mistake)
