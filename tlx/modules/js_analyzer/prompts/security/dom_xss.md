---
id: dom_xss
kind: security
title: DOM-based cross-site scripting
tags: [xss, dom, client-side]
always_include: false
priority: 50
---

DOM-XSS analysis cheat-sheet.

Sources (untrusted input):
  location.hash, location.search, location.href, location.pathname,
  document.URL, document.referrer, document.cookie, window.name,
  postMessage `event.data`, URLSearchParams, history.state, localStorage,
  sessionStorage, IndexedDB.

Sinks (DOM execution / HTML write):
  innerHTML, outerHTML, document.write, document.writeln,
  insertAdjacentHTML, eval, Function(), setTimeout/setInterval with string,
  src=, href= (javascript:), srcdoc, dangerouslySetInnerHTML (React),
  v-html (Vue), [innerHTML]="" (Angular).

Trace pattern:
  1. semantic_search for source identifiers above.
  2. For each hit, read the function and look for assignment to a sink.
  3. Report source → variable → sink with file, function, line.
  4. Note any sanitization between source and sink (DOMPurify, escape,
     textContent assign — these break the chain).
