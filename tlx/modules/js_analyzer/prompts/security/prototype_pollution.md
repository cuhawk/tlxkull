---
id: prototype_pollution
kind: security
title: Prototype pollution gadgets
tags: [prototype-pollution, gadgets, deep-merge]
always_include: false
priority: 50
---

Prototype-pollution analysis.

Sources (writes to __proto__ / constructor.prototype):
  Object.assign with user-controlled keys, JSON.parse output spread into
  config, query-string parsers (qs, querystring), recursive merge / extend /
  deepClone helpers without `__proto__` / `constructor` filtering.

Sinks (gadgets — code that reads polluted properties):
  templating engines reading defaults from Object.prototype,
  `if (obj.isAdmin)` checks on objects without `Object.create(null)`,
  `Object.assign({}, defaults, opts)` where defaults is user-supplied,
  spread into HTML attributes (`<img {...attrs}>` → onerror gadget).

Trace pattern:
  1. semantic_search for "merge", "extend", "deepClone", "Object.assign(".
  2. semantic_search for "__proto__", "constructor.prototype".
  3. For each merge helper, confirm it skips `__proto__` / `constructor` keys.
  4. Then look for downstream property reads that act as gadgets.
