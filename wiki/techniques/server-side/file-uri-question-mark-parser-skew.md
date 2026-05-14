---
title: file:// URI parser disagreement on `?` enables path traversal in image renderers
slug: file-uri-question-mark-parser-skew
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/server-side, technique/parser-skew, technique/url-parsing, technique/file-read]
inbound: []
---

# file:// URI parser disagreement on `?` enables path traversal in image renderers

## Pattern

Two URL parsers in the same request flow disagree on whether `?` is
the path/query separator when the scheme is `file://`. One parser
treats `?` as a literal path character (correct per POSIX — filesystem
filenames can contain `?`), the other treats `?` as the start of the
query string (HTTP semantics applied to a file URI).

Canva's case (referenced in Ep 44): the *validator* parsed the URI as
HTTP-shaped and saw `file:///svg/./?...` as path=`/svg/./` + query=
`...` — looked safe (no traversal). The *renderer* parsed the URI
through the OS file API and saw the entire string as the path,
including the traversal sequence that the attacker hid after the `?`:

```
file:///svg/./?../../../etc/passwd
```

Validator: "path is `/svg/./`, fine." Renderer: "open the file
`/svg/./?../../../etc/passwd`" — and the OS file API does NOT treat
`?` as special; it follows the literal `..` segments and reads
`/etc/passwd`. Content gets embedded in the rendered SVG/JPEG.

## Preconditions

- Application accepts a `file://` URL or file path for rendering
  (image conversion, PDF generation, SVG to PNG).
- A validator/whitelist check uses an HTTP-shaped URL parser
  (`URL.parse`, `urllib.urlparse`, Java `java.net.URI`).
- A renderer uses an OS-level file open (`open()`, `fopen()`,
  `File.OpenRead`) that treats the path verbatim.

## Detection

- Submit `file:///<allowed-path>/?../../../etc/passwd` and look for
  `/etc/passwd` contents in the rendered output.
- Try variants: `?#`, `??`, `%3F`, double-encoded.

## Triggering

```
file:///app/static/svg/./?../../../etc/passwd
```
Validator considers `/app/static/svg/./` safe; renderer reads
`/etc/passwd`.

For Windows: filenames cannot contain `?` (OS rejects); the parser
skew doesn't fire — try other reserved characters or rely on the
HTTP-parser-only treating `\` as path separator.

## Bypasses

- If `?` is normalized out: try `#` (HTTP fragment, but POSIX-legal
  in filenames).
- If both parsers agree on `?`: try `;` (path-parameter delimiter in
  Java URI; literal char in filesystem).
- Whitespace + null byte for old C-based filename APIs.

## Seen in the wild

- {date: 2023-circa, source: CT Ep 44} — Canva security team blog "When
  URL Parsers Disagree."

## References

- Canva security blog — When URL Parsers Disagree (Dec 2022)
- Critical Thinking Podcast Ep 44
- Orange Tsai BlackHat 2017/2018 — URL parser confusion
- Related: [[../dom-xss/url-anatomy-bypass-cheatsheet]],
  [[secondary-context-path-traversal]]
