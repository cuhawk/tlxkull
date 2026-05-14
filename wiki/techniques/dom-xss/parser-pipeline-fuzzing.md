---
title: Mutation-XSS via Parser-Pipeline Fuzzing (DOM Explorer / Multi HTML Parse)
slug: parser-pipeline-fuzzing
created_utc: 2026-05-14T00:00:00Z
updated_utc: 2026-05-14T00:00:00Z
tags: [technique/dom-xss, technique/mutation-xss, technique/fuzzing]
inbound: []
---

# Mutation-XSS via Parser-Pipeline Fuzzing

## Pattern

Modern web stacks pipe user-supplied HTML through multiple parsers and
sanitizers: `DOMParser` -> `DOMPurify` -> server-side renderer -> PDF
exporter, etc. Each stage may serialize HTML differently - comments,
processing instructions, custom elements, malformed attributes, and
namespaced tags survive one stage and get re-interpreted by the next.
Mutation XSS lives in those differentials.

Two web-hosted tools turn pipeline-fuzzing into a fast iteration loop:

- **DOM Explorer** (YesWeHack, BitK) - `yeswehack.github.io/dom-explorer`
  - Cyberchef-style pipeline UI: add parser/sanitizer stages
  (DOMParser, parse5, DOMPurify, JSXSS), set per-stage config (mime
  type, doctype, selector, output), and watch how the payload mutates.
- **Multi HTML Parse** (Mathias Karlsson) - narrower scope but
  complementary; useful when DOM Explorer doesn't ship a specific parser.

The technique: build the target's exact pipeline locally, fuzz inputs,
verify a survivor on the actual target with a single HTTP request.

## Preconditions

- You can identify the target's parser/sanitizer chain (often inferred
  from response headers, JS libraries loaded, or by static analysis with
  `js_analyzer`).
- The target's pipeline contains at least two parsers that disagree on
  edge-case serialization.

## Detection

- Fingerprint DOMPurify version via `DOMPurify.version` (often global) or
  by sanitizer behavior on known probes.
- Inspect server-rendered HTML for any signs of an additional pass
  (re-encoded entities, re-quoted attributes, comment normalisation).
- Inventory: PDF exporters (Puppeteer / wkhtmltopdf), email renderers,
  RSS feed builders, all introduce parser stages.

## Triggering

1. Open DOM Explorer, configure each pipeline stage to match the target.
2. Paste a known mutation-XSS probe (see [[dompurify-pi-bypass]],
   [[consuming-tags-and-hoisting]]).
3. Inspect each stage's output. Look for any stage where the payload
   gains executable form (`<script>`, `on*=` handler, `javascript:` URI).
4. Test the surviving payload on the live target.

```
Stage 1: DOMParser(text/html) -> <svg><?xml ?><img/onerror=alert(1)></svg>
Stage 2: DOMPurify(default)   -> <svg><img/onerror="alert(1)"></svg>
Stage 3: Server reserialize    -> renders the onerror attribute as live JS
```

## Bypasses

- DOMPurify-specific bypasses chain particularly well - see
  [[dompurify-pi-bypass]] for the processing-instruction class.
- For PDF / image pipelines, also check whether the server-side renderer
  fetches SSRF-vulnerable URLs from attribute values (`<img src=>`,
  `<link href=>`).

## Seen in the wild

- {date: 2024-11-14, source: CT Ep 97} - DOM Explorer release covered; Multi HTML Parse referenced as a precursor.

## References

- DOM Explorer - <https://yeswehack.github.io/dom-explorer/>
- Multi HTML Parse - Mathias Karlsson's site.
- Critical Thinking Podcast Ep 97 - <https://www.youtube.com/watch?v=m5mR6dvhtpg>
- Related: [[dompurify-pi-bypass]], [[consuming-tags-and-hoisting]]
