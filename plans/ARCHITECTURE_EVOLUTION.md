# JS Analyzer — Architecture Evolution Plan

> Deep audit + production-grade evolution roadmap for `tlx/modules/js_analyzer`.
> Date: 2026-05-18. Author: Claude Code (Opus 4.7, 1M context).
> Companion docs: `plans/PLAN.md` (workspace plan), `plans/IMPL_TIER123.md`
> (in-flight T1–T3), `plans/CC_TAINT_ADVERSARIAL.md` (LLM stage refactor v1).

This plan is **additive**. It preserves the existing schema, the
Sonnet→Opus advisor pipeline, the implicit-tag closure, sanitizer-on-path,
and the per-target DB-isolation workflow. It evolves them into a
production-grade analyzer that competes with commercial SAST plus the
better academic JS taint research (CodeQL Library, ODGen, FAST, JaSt).

---

## 0. Executive summary

The current analyzer is a solid Tier 2 system: regex+AST taxonomy, a per-file
callgraph with import-edge repair, intra-procedural taint with property-name
support, inter-procedural taint over `dataflow_edges`, implicit-tag closure
expansion, and a Sonnet→Opus advisor that converts chains into verdicts. It
already has DB-per-target isolation and chain scoring with sink/source/path
factors. The recently shipped implicit-tags + sanitizer-on-path + bucket
inversion phases (project_implicit_tags_plan.md) closed the wrapper-blindness
gap and tightened the audited→confirmed FP rate.

The remaining ceiling is **semantic**: every false-positive class we still
hit lives in one of seven blind spots — dynamic property dispatch, async
continuations, browser sink viability, sanitizer reality, framework
hydration semantics, runtime indirection (webpack/eval/lazy chunks), and
confidence-driven traversal pruning. The LLM is silently compensating for
all of them, which inflates Opus cost and caps recall at the boundary of
what static evidence the LLM can reason about.

This plan attacks the seven blind spots with **bounded, additive
subsystems** that plug into the existing tables and the existing chain
extractor. Each subsystem has an explicit failure mode, a budget, and a
fallback. We stage rollout so any single phase can be shipped and reverted
without touching the others.

The single biggest win is **(P0) sink viability scoring + parser context**.
It cuts the false-positive rate on the hot list by an estimated 30-50% and
unlocks (P1) confidence-driven pruning. The biggest *novel* win is
**(P2) lightweight runtime augmentation** — a single in-page agent that
captures eval/dynamic-import/webpack-runtime resolutions and reconciles
them back into the static graph. None of the open-source JS SAST projects
do this well.

---

## 1. Current-state snapshot (faithful, not aspirational)

### 1.1 What we have

| Capability | Where | State |
|---|---|---|
| AST → graph | `ast_extractor.js` (87 KB) + `callgraph.py` (1250 LOC) | Solid. 60+ rule IDs, framework-gated. |
| Callgraph resolution | `callgraph.py` Phase D1 + D2 | Bare-name + import-edge repair. No this-binding. |
| Intra-procedural taint | `taint.py` (147 LOC) | Line-ordered worklist, var-name granular incl. static dotted paths. |
| Inter-procedural taint | `interprocedural_taint.py` (225 LOC) | `dataflow_edges` walk with `arg_to_param`/`return`. |
| Sanitizer tracking | `node_sanitizers` table + sanitizer-on-path skill | Coarse mode shipped; strict-dominance flag exists but unused. |
| Source/sink tagging | `taxonomy.py` + `taxonomies/*.json` + AST rule IDs | Static, framework-gated by `ACTIVE_FRAMEWORKS`. |
| Implicit closure tags | `implicit_tags.py` | Hop-decay `0.7^hop`, max_hops=2, shipped. |
| Bucket-inversion / naming heuristics | `bin/bucket_inversion.py`, `bin/naming_heuristic.py` | Confidence 0.3-0.5 implicit seeds. |
| Chain extraction | `bin/extract_chains_bounded.py` (327 LOC) | BFS, sink↔source pairing, bounded by `--max-paths`. |
| Sanitizer-on-path | `sanitizer_on_path` skill | Splits `all.jsonl` → `sanitized.jsonl` + `clean.jsonl`. |
| LLM cascade | `audit_pipeline.py` + `claude_agent.py` + `exploit_agent.py` | Sonnet triage gate + Sonnet main audit + bounded Opus consults + Opus exploit synth. |
| Incremental cache | `file_hashes` table in callgraph.py | File-hash skip only. No incremental taint. |
| Runtime confirmation | `mock_backend/core/sink_monitor.py` | Headless sink-fire detection. Boolean flag bubbles to chain score. |
| Browser context | none | Not modeled. |

### 1.2 Identified blind spots (root cause of every remaining FP class)

| Blind spot | Concrete miss case | Today's behaviour |
|---|---|---|
| Dynamic property dispatch | `sinkMap[op](payload)` | Edge marked `dynamic`, taint stops at the call site. |
| Computed member access | `window[fn]`, `obj[user]`, `this[prop]` | Property collapses to `<dynamic>`; aliasing loses precision. |
| Async continuations | `addEventListener(..., handler)`, `Promise.then(handler)`, `await fetch(...).then(...)` | Handler qname is captured but no caller→handler edge exists in `edges`; taint never flows from event source into handler. |
| Browser sink viability | `el.innerHTML = x` where `x` lives in a Trusted-Types-only context | Sink scored equal regardless of context. |
| Sanitizer reality | `DOMPurify.sanitize(x, {ALLOWED_URI_REGEXP: /.*/})` | Counted as full sanitization. No version, no config awareness. |
| Framework hydration | React `dangerouslySetInnerHTML` vs SSR-only HTML escape | Tagged with one rule; no SSR/CSR boundary modeling. |
| Runtime indirection | webpack chunk loader → real module name resolved at runtime | Static call lands on the loader, not the real sink. |
| Confidence pruning | All chains traversed up to `--max-paths` | No probability-aware pruning; budget burnt on low-confidence chains. |

These eight blind spots are the rest of this document.

---

## 2. Dynamic property resolution

### 2.1 Why it matters

Modern bundles dispatch through tables: route maps, sink maps, redux-style
reducer tables, `i18n[lang][key]`, `_handlers[type]`. Every miss here is an
end-to-end FN: the analyzer sees the data going *into* the table and
nothing coming out the other side. Conversely, naive over-approximation
("`obj[x]` taints every property") produces a graph explosion the chain
extractor cannot survive.

### 2.2 Design — symbolic property tracker

Add a new analysis stage between AST extraction and call graph resolution.
For each function emit a **property-shape facts** stream:

```python
# New table
CREATE TABLE prop_shapes (
    node_id INTEGER NOT NULL,         -- function in which the shape lives
    base_var TEXT NOT NULL,           -- "sinkMap"
    line INTEGER NOT NULL,
    shape_kind TEXT NOT NULL,         -- 'object_literal'|'class_inst'|'param'|'import'|'unknown'
    keys_json TEXT,                   -- JSON list of known string keys when shape_kind in {object_literal,class_inst}
    keys_confidence REAL NOT NULL,    -- 0..1; 1.0 for literals, 0.5 for assignment patterns
    closed BOOLEAN NOT NULL,          -- true when no dynamic add observed
    evidence_lines TEXT,              -- JSON list of lines where keys were observed
    PRIMARY KEY (node_id, base_var, line)
);

CREATE INDEX idx_prop_shapes_base ON prop_shapes(base_var);
```

Three resolution levels, applied in order:

1. **Literal object-shape inference.** Walk every `ObjectExpression` and
   `ClassDeclaration` in the AST. Record key set. If `Object.defineProperty`
   or computed assignment is observed on the same base, drop `closed` to
   false but keep keys.
2. **String-lattice propagation.** For each variable, track a *string
   abstract domain* with three levels: `Top` (any string), `Const(s)`,
   `Set({s1,s2,...})` (≤ 16 elements; over → `Top`). Propagate through
   string concatenation, `String.prototype.concat`, template literals,
   `String(x)`. The 16-element cap is the explosion gate.
3. **Computed call resolution.** When the call graph hits a `dynamic`
   callee like `obj[k]()`, look up `prop_shapes` for `obj`, intersect with
   the string domain of `k`, and rewrite the edge into N concrete edges
   with confidence `(keys_confidence × key_match_ratio)`. Cap N at 8 per
   call site (configurable). On overflow, leave as `dynamic_overapprox`
   and downgrade confidence to 0.2.

### 2.3 Data flow integration

Property shapes feed two consumers:

- **Edge rewriter** (callgraph.py Phase D3, new): demotes/refines `dynamic`
  edges into concrete edges with a `resolved_kind='prop_shape'` tag.
- **Variable tracker** in `taint.py`: when assigning `const v = obj[k]`, if
  the keys set is small and the string domain of `k` is `Const` or
  `Set(<=4)`, taint each tracked sub-property `obj.s1`, `obj.s2`
  independently (multi-fact emission).

### 2.4 Graph explosion controls

- Per-callsite refinement cap (default 8).
- Per-target total refinement cap (default 20k).
- Refinement records the original `dynamic` edge so it is recoverable.
- A statically-detected "registry pattern" (a single `register(name, fn)`
  call site with N invocations) is treated as **one** edge with a
  variant-set body, not N edges, until a concrete call site demands
  expansion.

### 2.5 Files touched / created

```
NEW   tlx/modules/js_analyzer/prop_shapes.py        (~400 LOC)
NEW   tlx/modules/js_analyzer/string_lattice.py     (~250 LOC)
EDIT  tlx/modules/js_analyzer/ast_extractor.js       — emit ObjectExpression keys, computed assignments
EDIT  tlx/modules/js_analyzer/callgraph.py           — Phase D3 edge refinement, new prop_shapes table
EDIT  tlx/modules/js_analyzer/taint.py               — multi-fact emission on small-keyset computed access
EDIT  bin/extract_chains_bounded.py                  — consume new `resolved_kind='prop_shape'` edges
```

### 2.6 Rollout

1. **Phase 1**: Emit prop_shapes only; do *not* rewrite edges. Compare
   shape-coverage % across the current target list.
2. **Phase 2**: Edge rewriting behind `--enable-prop-resolve` flag.
   Side-by-side chain.jsonl A/B for ten engagements.
3. **Phase 3**: On by default once FP rate on hot.jsonl drops without
   FN regression on the eval corpus.

### 2.7 Failure mode

If shapes mis-resolve, the original `dynamic` edge is still on disk under
its original `resolved_kind`. Chain extractor falls back when refinement
confidence < 0.3. Worst case: ignored.

---

## 3. Async / event continuation graphs

### 3.1 Why it matters

The biggest single under-counted FN class in our current hot list is
"source enters event handler, sink fires inside handler". Today the AST
extractor records the handler qname; the call graph has no edge from
`addEventListener` → handler, so inter-procedural taint cannot bridge.
Similarly Promise chains lose the link between `.then(handlerA).then(handlerB)`
and the original async source.

### 3.2 Design — explicit continuation edge type

Add a new edge kind to `edges`:

```
ALTER TABLE edges ADD COLUMN edge_class TEXT DEFAULT 'sync';
-- values: 'sync' | 'continuation' | 'message' | 'observer'
```

Plus a sibling table for continuation metadata:

```
CREATE TABLE continuations (
    edge_id INTEGER PRIMARY KEY,           -- FK to edges.rowid (logical)
    producer_kind TEXT NOT NULL,           -- 'addEventListener'|'promise_then'|'await'|'setTimeout'|'mutationobserver'|'fetch_chain'|'postMessage'|'websocket'|'rxjs_subscribe'
    event_name TEXT,                       -- 'click','message','load',...
    arg_index INTEGER NOT NULL,            -- which positional arg is the handler
    taint_through INTEGER NOT NULL,        -- 1 if handler receives event with tainted property paths
    event_taint_paths TEXT                 -- JSON: ['data','origin'] for postMessage etc.
);
```

### 3.3 Recognized producers (initial set)

| Producer | Continuation edge | Source-tainting? |
|---|---|---|
| `target.addEventListener(name, fn, opts?)` | call→fn | yes — event object .target.value etc.; postMessage .data is `dom_message` source |
| `Promise.prototype.then(onFulfilled, onRejected?)` | promise-producer→fn | yes — arg = upstream resolved value |
| `Promise.prototype.catch(fn)` | producer→fn | yes — arg = upstream rejection |
| `await expr` | enclosing function continues | yes — continuation receives expr's resolved value |
| `setTimeout/setInterval/setImmediate(fn, ...)` | call→fn | no (timer args are user-supplied at registration) |
| `MutationObserver(fn).observe(target, opts)` | observer→fn | yes if target is in user-controlled DOM |
| `window.addEventListener('message', fn)` | call→fn | yes — postMessage source; `dom_message_origin` already in taxonomy |
| `WebSocket.onmessage = fn` / `ws.addEventListener` | call→fn | yes — `dom_websocket_data` (add to taxonomy) |
| RxJS `obs.subscribe(fn)` / `pipe(...).subscribe(fn)` | producer→fn | yes — upstream observable taint |
| `fetch(...).then(...)` / `axios(...).then(...)` | request→fn | yes if URL is user-controlled (SSRF feedback) |

### 3.4 Event-loop ordering — *what we do not promise*

We do not promise correct happens-before ordering across continuations.
Taint is unioned at the merge point — that's a deliberate
over-approximation. A handler is reachable if *any* continuation edge
points at it; we don't model whether the registration ran before the
event. This is exploit-soundness; we want recall, not WCET.

### 3.5 Bounded traversal

- **Continuation depth cap** in chain extractor: each continuation hop
  counts 1.5× a sync hop (default `--max-depth-async 8`).
- **Cycle detection** is essential: `subscribe(fn)` where `fn` re-emits
  loops. BFS already has a visited set keyed by `(node_id, taint_signature)`;
  extend the signature with continuation count.
- **Severity-aware budget**: continuation chains terminating in
  `low`-severity sinks are pruned before continuation expansion.

### 3.6 Files touched / created

```
NEW   tlx/modules/js_analyzer/async_graph.py         — producer detectors + edge writer
EDIT  tlx/modules/js_analyzer/ast_extractor.js       — already emits handler qnames; add producer metadata
EDIT  tlx/modules/js_analyzer/callgraph.py           — new edge_class, continuations table, post-import-repair Phase D4
EDIT  tlx/modules/js_analyzer/interprocedural_taint.py — walk continuation edges; inject event-shaped taint at handler entry
EDIT  bin/extract_chains_bounded.py                  — async-aware BFS depth cap
NEW   plans/ASYNC_PRODUCER_CATALOG.md                — canonical producer list incl. RxJS/socketio
```

### 3.7 Rollout

1. **Phase 1**: Extract continuation edges, persist, do not propagate
   taint. Measure: how many chains gain a virtual sink upstream.
2. **Phase 2**: Inject event-shaped taint at handler entry for postMessage
   + addEventListener + Promise.then. Keep RxJS / Observer / WS behind
   flag.
3. **Phase 3**: All producers on; tune depth cap.

### 3.8 Precision tradeoffs accepted

- We will report `addEventListener('click', handler)` chains even where
  the click target is not user-reachable. Sink-viability scoring (§4) is
  responsible for de-prioritizing these.
- We will not model async generators or `for-await-of`. Edge cases;
  defer.

---

## 4. Browser runtime semantics & sink viability

### 4.1 Why it matters

`el.innerHTML = userData` reads identically in static text whether the
page is plain HTML, served with `Content-Security-Policy: default-src 'self'
'unsafe-inline'`, served with Trusted Types, or assigned to an element
that lives inside a `<template>`. In one case it is RCE; in another it
is inert. Today we score them identically. This single fix is the
biggest FP-rate driver we have not pulled.

### 4.2 Design — sink capability schema

Augment the taxonomy. Each sink gains a `capabilities` block:

```json
// taxonomies/sinks.json — additive
{
  "id": "dom_innerhtml",
  "pattern": "\\.innerHTML\\s*=",
  "kind": "sink",
  "severity": "high",
  "description": "Element.innerHTML assignment",
  "capabilities": {
    "exec_context": "html_parser",
    "script_exec": "via_script_tag_old_browsers_only_or_event_handler",
    "trusted_types_guarded": false,
    "csp_neutralized_by": ["script-src 'none' AND no inline-handler bypass"],
    "csp_bypassable_by": ["unsafe-inline", "unsafe-eval (rarely)", "dangling markup"],
    "parser_context": "html",
    "framework_overrides": {
      "react": "via dangerouslySetInnerHTML only; React escapes children",
      "vue": "via v-html",
      "angular": "blocked by default; bypass via bypassSecurityTrustHtml"
    }
  }
}
```

Capability fields used by scoring:

- `exec_context` ∈ {`html_parser`, `js_global`, `js_eval`, `url`, `attribute`, `style`, `text`, `srcdoc`}
- `script_exec` — free-form note used by LLM
- `trusted_types_guarded` — whether a Trusted-Types policy stops the sink
- `parser_context` — what parser receives the bytes

### 4.3 Page-level browser-context inference

A new pass (`browser_context.py`) infers per-target:

- **CSP** — from `Content-Security-Policy` headers captured during
  `caido-capture` and stored in `targets/<name>/runtime/<utc>/state.json`,
  plus `<meta http-equiv="CSP">` parsed from any indexed HTML.
- **Trusted Types** — presence of `trustedTypes.createPolicy(...)` in the
  bundle (already tagged `trusted_types_create_policy`). If any policy
  exists and CSP has `require-trusted-types-for 'script'`, set
  `target.trusted_types_enforced=true`.
- **SSR vs CSR** — Next.js (already detected) plus a fingerprint for
  Vite, Nuxt, Astro, Remix, Sapper.

Persisted as `targets/<name>/browser_context.json`:

```json
{
  "csp": {
    "raw": "...",
    "default_src": ["'self'"],
    "script_src": ["'self'", "https://cdn.example.com"],
    "trusted_types_required": true,
    "unsafe_inline_allowed": false,
    "unsafe_eval_allowed": false
  },
  "trusted_types": { "enforced": true, "policies": ["default", "dompurify"] },
  "rendering": { "model": "ssr_then_csr", "framework": "nextjs", "hydration": true },
  "sandbox_iframes": [],
  "evidence_files": ["raw/_response_headers.txt", "raw/index.html"]
}
```

### 4.4 Sink viability scoring

Per chain, compute:

```
viability_score = base_severity
                 × csp_neutralization_factor
                 × trusted_types_factor
                 × parser_context_factor
                 × framework_override_factor
```

Examples:

- `innerHTML` on a CSP `script-src 'none'` page → `csp_neutralization_factor=0.25`
  (still gives DOM clobbering / dangling markup / CSS injection;
  not arbitrary JS).
- `innerHTML` with Trusted Types enforced → `trusted_types_factor=0.05`
  unless the chain *creates* a TT policy along the way.
- `dangerouslySetInnerHTML` inside React → `framework_override_factor=1.0`
  but only when `csp_neutralization_factor` allows script exec.
- `<element srcdoc=...>` → parser_context is a fresh document; same as
  document.write inside a sandboxed iframe.

Scoring is **multiplicative**, never additive, so the dominant blocker
wins. A `trusted_types_factor=0.05` overrides everything else: that sink
just isn't reachable as XSS.

### 4.5 Files touched / created

```
NEW   tlx/modules/js_analyzer/browser_context.py     — CSP/TT/SSR inference, browser_context.json writer
NEW   tlx/modules/js_analyzer/sink_viability.py      — viability_score computation
EDIT  tlx/modules/js_analyzer/taxonomies/sinks.json  — add `capabilities` blocks (start with top 30 sinks)
EDIT  tlx/modules/js_analyzer/reporter.py            — score_chain() incorporates viability_score
EDIT  bin/extract_chains_bounded.py                  — emit viability_score per chain
NEW   skills/browser-context-infer/SKILL.md          — runs after caido-capture+js-index
```

### 4.6 Rollout

1. **Phase 1**: Score chains with viability but do not drop. Emit
   side-by-side comparison.
2. **Phase 2**: Drop chains with `viability_score < 0.1` from `hot.jsonl`;
   keep in `all.jsonl`.
3. **Phase 3**: Plumb `capabilities` block into LLM prompt so it stops
   re-deriving the CSP analysis from scratch.

---

## 5. Sanitizer reality modeling

### 5.1 Why it matters

`DOMPurify.sanitize(x)` is treated identically whether:

- DOMPurify version is `2.0.16` (multiple mXSS bypasses against
  `MutationObserver`-less browsers), or
- The call passes `ALLOWED_TAGS: ['*']` (everything allowed), or
- The call passes `RETURN_DOM_FRAGMENT: true` and the result is dropped
  into innerHTML elsewhere.

Today we accept any call as full sanitization. That underweights real
findings (a length check is a "sanitizer" today) and overweights known
bypasses.

### 5.2 Design — sanitizer capability registry

Two-level structure:

```json
// taxonomies/sanitizers.json
{
  "id": "dompurify_sanitize",
  "pattern": "DOMPurify\\.sanitize\\b",
  "clears": ["dom_innerhtml", "dom_outerhtml", "react_dangerously"],
  "library": "dompurify",
  "version_aware": true,
  "default_config_clears": ["html"],
  "config_aware": true,
  "config_options": [
    {"flag": "ALLOWED_TAGS", "weakens_when": "contains *",   "downgrade_to": 0.0},
    {"flag": "RETURN_DOM_FRAGMENT", "behaviour": "returns fragment; downstream insertAdjacentHTML uses raw HTML — clears nothing if fragment is re-serialized"},
    {"flag": "KEEP_CONTENT", "behaviour": "preserves content of forbidden tags — bypassable"}
  ],
  "known_bypass_versions": [
    {"version": "<2.4.0", "bypass": "mXSS via Mutation breakout", "downgrade_to": 0.4},
    {"version": "<2.3.0", "bypass": "Trusted Types policy escape", "downgrade_to": 0.5}
  ]
}
```

Plus three families of *generic* sanitizer detectors:

1. **Length-only guards** (`if (x.length < N)`) — `downgrade_to = 0.1`,
   not a sanitizer, but blocks length-dependent payloads. Stored as
   `node_sanitizers` row with `clears='length_guard'`.
2. **Encoding round-trips** (`decodeURIComponent(encodeURIComponent(x))`)
   — taint preserved across; downgrade other path sanitizers in
   adjacent code by 0.5 because they may have been bypassed.
3. **Regex sanitizers** — capture the regex literal, run a known-bypass
   matcher (e.g. matches `/<script>/i` only — bypass via
   `<ScRiPt>`/`<svg onload>`). Compile a small bypass corpus.

### 5.3 Version fingerprinting

Driven by `bin/npm_version_diff.py` (already exists for T3.1) plus
`package-lock.json` parsing if available; otherwise sniff vendored
strings. Persist into `targets/<name>/library_versions.json`:

```json
{
  "dompurify": { "version": "2.3.6", "evidence": "raw/vendor.js:84212", "confidence": 0.9 },
  "validator": { "version": ">=13", "evidence": "package-lock.json", "confidence": 1.0 }
}
```

### 5.4 Confidence downgrade rules

When sanitizer-on-path matches a sink-clearing sanitizer, look up
version + config. Apply downgrades:

```
sanitizer_confidence = base_clears_confidence  (default 1.0)
                       × version_factor       (1.0 unless bypass version)
                       × config_factor        (1.0 unless weakening flag)
                       × context_factor       (1.0 unless decode-reencode pair detected)
```

If `sanitizer_confidence < 0.5`, the chain is *not* moved to
`sanitized.jsonl`; it stays in `clean.jsonl` with a `partial_sanitizer`
note.

### 5.5 Files touched / created

```
EDIT  tlx/modules/js_analyzer/taxonomies/sanitizers.json — version + config metadata
NEW   tlx/modules/js_analyzer/sanitizer_registry.py    — version fingerprint + config parser
NEW   tlx/modules/js_analyzer/sanitizer_bypass_corpus.py — regex-weakness + known-CVE table
EDIT  tlx/modules/mock_backend/core/sink_monitor.py     — emit sanitizer config evidence into events
EDIT  bin/sanitizer_on_path.py (or skill driver)        — consume confidence, route partial-clears
```

### 5.6 Rollout

1. **Phase 1**: DOMPurify version + config metadata only. Compare
   `sanitized.jsonl` reductions per target.
2. **Phase 2**: Length-guard + regex-weakness families. Watch FN regress.
3. **Phase 3**: Trusted Types interaction with sanitizer registry.

---

## 6. Framework semantic expansion

### 6.1 Why it matters

Framework detection (frameworks.json) is currently a gate on which AST
visitors fire. The visitors themselves are coarse — one rule per sink.
Frameworks have **semantic invariants** (React auto-escapes children;
Angular sanitizes by default; Next.js has SSR-only props; Electron has a
context isolation boundary) that should rewrite the chain *before* it
ever reaches the LLM.

### 6.2 Design — framework adapter layer

Introduce a plugin module per framework under
`tlx/modules/js_analyzer/frameworks/`:

```
frameworks/
  __init__.py            -- registry of adapters
  react.py
  vue.py
  angular.py
  nextjs.py
  svelte.py
  lit.py
  electron.py
```

Each adapter implements three hooks:

```python
class FrameworkAdapter(Protocol):
    name: str

    def patch_tags(self, conn: sqlite3.Connection) -> int:
        """Add framework-aware tags (e.g. `react_jsx_text` source for
        JSX text positions; `react_dangerously_set_inner_html` sink).
        Return number of rows inserted."""

    def rewrite_edges(self, conn: sqlite3.Connection) -> int:
        """Insert virtual continuation edges that model hydration,
        ref callbacks, useEffect, Vue directive bindings, Angular
        decorator wiring. Return number of edges inserted."""

    def adjust_viability(self, chain: dict, ctx: BrowserContext) -> float:
        """Return a multiplicative adjustment to viability_score
        based on framework semantics (e.g. Angular SafeHtml bypass
        chain is 1.0; Angular HTML interpolation only is 0.0)."""
```

### 6.3 Initial coverage

| Adapter | First-cut scope |
|---|---|
| React | `dangerouslySetInnerHTML`, `ref` callbacks, `useEffect`/`useLayoutEffect` continuation edges, JSX children auto-escape annotation |
| Next.js | App-router server vs client (`"use client"` boundary tag on nodes), `getServerSideProps` data tainting, `searchParams` source |
| Vue | `v-html`, `:is` dynamic component, `vue-router` route params source |
| Angular | `bypassSecurityTrust*` family as a viability `1.0` boost; `[innerHTML]` template binding from `.html` files via `template_analyzer` |
| Svelte | Compiler output detection (`svelte/internal` markers); `@html` directive surfaced via compiled function name pattern |
| Lit | `unsafeHTML` directive; `html\`...\`` tag function not a sink itself |
| Electron | `nodeIntegration`/`contextIsolation` evidence; `webContents.executeJavaScript` sink; preload/main/renderer boundary tag |

### 6.4 Files touched / created

```
NEW   tlx/modules/js_analyzer/frameworks/__init__.py    — adapter registry
NEW   tlx/modules/js_analyzer/frameworks/<each>.py      — adapters
EDIT  tlx/modules/js_analyzer/callgraph.py              — invoke `patch_tags` + `rewrite_edges` after Phase D2
EDIT  tlx/modules/js_analyzer/reporter.py               — score_chain calls `adjust_viability`
EDIT  tlx/modules/js_analyzer/framework_detect.py       — already detects; pass active set to adapters
```

### 6.5 Rollout

Ship in dependency order: React → Next.js → Vue → Angular → Svelte → Lit → Electron.
Each adapter is independently flag-gated (`--enable-react-adapter`).

---

## 7. Runtime-augmented analysis

### 7.1 Why it matters

Static analysis cannot resolve a webpack `__webpack_require__` against
`webpack_runtime[chunkId].modules[moduleId]`, cannot decode obfuscated
string tables, cannot follow lazy chunks loaded by string concatenation,
cannot trace `Function(decode(s))()` synthesized at runtime. Real
bug-bounty bundles do all four.

We are **not** building a fuzzer. We are building **passive runtime
telemetry** that fills four specific holes.

### 7.2 Design — lightweight in-page agent

A single ~6 KB JS agent (`runtime/agent.js`) injected into the browser
either via the `claude-in-chrome` MCP `evaluate_script` hook or via
Caido's request-rewriting on any 2xx HTML response. It monkeypatches:

| Patch | Why |
|---|---|
| `Function.prototype.constructor` (`new Function(s)`) | Capture dynamically-generated source |
| `eval` | Same; record caller stack + source body |
| `__webpack_require__` / `webpackJsonp` / `__webpack_modules__` | Resolve chunkId → real module name |
| `Element.prototype.innerHTML` setter | Capture sink fires with caller stack |
| `document.write` | Same |
| `Element.prototype.setAttribute` (event-handler attrs) | Capture `on*` attribute assignments |
| `window.postMessage` send + receive | Cross-frame taint observation |
| `Promise.prototype.then` (registration only) | Map dynamic continuation registrations |
| `Reflect.set` / `Object.defineProperty` for `__proto__` chains | Prototype pollution sink/source confirmation |

The agent **does not** modify behavior. It only writes records to a
ring-buffer in `window.__tlx_runtime__` and POSTs batches to a localhost
collector (`bin/runtime_collector.py`, port from `memory.md`).

### 7.3 Record format (append-only JSONL)

```
{
  "ts": 1715990400.123,
  "kind": "sink_fire|eval_source|webpack_resolve|continuation|postmessage_in|postmessage_out|set_proto",
  "url": "https://target.example/app",
  "fn_caller": ["@webpack-internal/0:42", "main.js:128:18"],     // captured frames
  "args_preview": ["...truncated 256B preview..."],
  "args_taint_match": ["dom_message"],                            // names of taint signals matched in args via heuristic
  "meta": { ... per-kind payload ... }
}
```

Persisted to `targets/<name>/runtime/<utc-iso>/events.jsonl`.

### 7.4 Static ↔ runtime reconciliation

A merger (`bin/runtime_merge.py`) reads `events.jsonl`, joins to the
static graph by file+line+function-name pattern, and emits:

- New `edges` rows with `resolved_kind='runtime_observed'`, confidence
  1.0 (we *saw* the call happen).
- `node_tags` rows with `source='runtime_observed'`, confidence 1.0,
  for sinks that fired (already partly in mock_backend; extend to real
  browser).
- New `continuations` rows for confirmed handler dispatches.
- `prop_shapes` upgrade: keys observed at runtime override static keys
  set, with `closed=true` for the observed call site.
- An `eval_corpus/<sha256>.js` file per observed eval/`Function` body,
  re-fed into `js-index` as a synthetic file in `sources/_eval/`.

### 7.5 Replay format

Stored under `targets/<name>/runtime/<run-id>/` as a small replay
bundle:

```
runtime/2026-05-18T18-22-04Z/
  events.jsonl
  agent_meta.json        -- agent version, patches applied, target URL
  eval_corpus/
    <sha256>.js          -- decoded eval bodies
    _index.json          -- sha256 → {first_seen_line, callers, taint_match}
  webpack_modules.json   -- chunkId → moduleId → real-file-or-name
  state.json             -- summary stats (counts per kind)
```

### 7.6 Rollout phases

1. **Phase 1**: Ship agent, collector, and `runtime_merge.py`. Run only
   on demand (skill `runtime-augment`). Just write events, do not feed
   back into static analysis.
2. **Phase 2**: Feed runtime-observed edges back into `extract_chains`.
   Verify FN reduction on a target where webpack indirection is known
   to hide a sink (use one of the existing engagements as the
   regression test).
3. **Phase 3**: Auto-trigger via `passive-listen` skill — runtime
   agent runs whenever the user has a live browsing session via the
   `caido-capture` proxy.

### 7.7 Performance and risk

- Agent is fully passive; failure mode is missing records, never
  altered behaviour.
- 6 KB minified; <1ms per patched call site (measured target: <2%
  end-user CPU overhead).
- The collector is localhost-only; do not POST events to anything else.
- Out-of-scope-host filter: agent refuses to send records for any URL
  outside the project's Caido scope (read at agent boot from a
  localhost endpoint).

---

## 8. Confidence-driven path ranking

### 8.1 Why it matters

`extract_chains_bounded.py` already prunes by `--max-paths`. But it
prunes blindly: a 9-hop low-severity chain consumes the same budget as
a 2-hop high-severity chain. Once the graph grows past ~500k edges
(real bug-bounty bundles routinely exceed this), the budget is spent
before the interesting chains are emitted.

### 8.2 Design — propagated chain confidence

Every node, edge, and tag carries a confidence today. Stitch them into
a chain-level *expected exploitability*:

```
P(chain) =  P(source controllable)
          × Π P(edge resolved)
          × Π (1 - P(sanitizer at hop blocks))
          × P(sink reachable | browser context)
          × P_async_discount(continuation hops)
          × P_dynamic_discount(prop_shape hops)
```

Components:

- **P(source controllable)** = `node_tags.confidence` of the source node,
  refined by source type (location_hash > postMessage > localStorage).
- **P(edge resolved)** = 1.0 for `exact`, 0.85 for `name_match`, 0.7 for
  `prop_shape`, 1.0 for `runtime_observed`, 0.3 for `dynamic_overapprox`.
- **P(sanitizer blocks)** = `sanitizer_confidence` from §5; default 0.0
  if no sanitizer on hop.
- **P(sink reachable)** = `viability_score` from §4.
- **P_async_discount** = 0.95^continuation_hops (small bias against
  over-deep async chains).
- **P_dynamic_discount** = 0.9^prop_shape_hops.

### 8.3 Traversal pruning

The BFS in `extract_chains_bounded.py` becomes a **best-first search**
keyed by partial P(chain) computed up to the frontier. With:

- **Per-source budget**: top-K=64 chains.
- **Global budget**: top-N=4000 chains (configurable; default scales
  with `nodes.count`).
- **Hard prune**: any partial chain with `P_partial < 0.05` is dropped.
- **Adaptive depth**: depth cap is `int(20 - 10*log(1/P_partial))`,
  clamped to [3, 12].

### 8.4 Calibration

Calibrate against the existing eval corpus: every confirmed TP/FP
across past engagements has a recorded final P(chain). Fit a logistic
on P(chain) → P(true_positive). Use the fit to threshold `hot.jsonl`
selection: take everything with calibrated P(TP) > 0.4. Re-fit
quarterly or after every 50 confirmed verdicts.

### 8.5 Files touched / created

```
EDIT  bin/extract_chains_bounded.py                  — best-first; partial-P cutoff
NEW   tlx/modules/js_analyzer/chain_confidence.py    — P(chain) computation
NEW   bin/calibrate_confidence.py                    — logistic fit + threshold writer
NEW   targets/_calibration/confidence_model.json     — persisted coefficients
EDIT  tlx/modules/js_analyzer/reporter.py            — use calibrated probability for sorting
```

### 8.6 Rollout

1. **Phase 1**: Compute P(chain) but rank with the current scorer.
   Output side-by-side comparison.
2. **Phase 2**: Best-first traversal in extractor.
3. **Phase 3**: Calibrated threshold for hot.jsonl.

---

## 9. Sanitizer reality + Trusted Types coupling

Already covered in §5. Trusted Types specifically: a
`trustedTypes.createPolicy(name, {createHTML: fn})` call where `fn` is
the identity function or a regex-only check is a **fake** sanitizer.
The registry models this as version-aware: if the policy body matches
`return s` (identity) or `s.replace(/<script.*?>/gi, '')`, sanitizer
confidence drops to 0.2. Cross-link from `taxonomies/sanitizers.json`
entry `trusted_types_policy` → bypass corpus.

---

## 10. Incremental recomputation + graph persistence

### 10.1 Why it matters

Today an `npm install` upstream that touches one chunk forces a full
re-index. For large bundles (>2k modules), that's tens of minutes. CI
adoption requires <1 minute warm-cache re-runs.

### 10.2 Design — content-addressed invalidation

Already in place: `file_hashes` skips AST extraction for unchanged
files. Extend to:

```
CREATE TABLE node_hashes (
    node_id INTEGER PRIMARY KEY,
    body_sha256 TEXT NOT NULL,         -- hash of node source bytes [start_line..end_line]
    deps_sha256 TEXT NOT NULL,         -- hash of (sorted callee qnames + sorted prop_shapes + sorted node_tags)
    last_indexed_at REAL NOT NULL
);

CREATE TABLE taint_cache (
    node_id INTEGER PRIMARY KEY,
    flows_json TEXT NOT NULL,          -- output of solve_function_taint
    cache_sha256 TEXT NOT NULL,        -- = body_sha256 of node when computed
    valid INTEGER NOT NULL             -- 0 if invalidated by neighbour change
);
```

### 10.3 Recomputation DAG

When `js-index` runs:

1. Identify the set of files with changed `file_hashes.sha256`.
2. For each changed file, find affected nodes by overlapping line range.
3. Walk the callgraph backward (callers) to a bounded depth (default 3).
   This is the **dirty set**.
4. Recompute AST tags, sanitizer tags, dataflow_edges *only* for the
   dirty set.
5. Recompute intra-procedural taint for the dirty set (cheap).
6. Recompute inter-procedural taint by replaying only flows that
   touch dirty nodes — keep an `interprocedural_taint_flows` index by
   `source_node_id`/`sink_node_id`, mark stale rows where either end is
   dirty.
7. Recompute implicit_tags only if direct-tag set changed; otherwise
   reuse.

### 10.4 Migration / versioning

Add `schema_version` row to `kv` table; bump on any column add. A
migration runner under `bin/migrate_db.py` performs forward-only
migrations. Per-target DBs are snapshotted before migration into
`targets/<name>/db/.bak/`.

### 10.5 Files touched / created

```
EDIT  tlx/modules/js_analyzer/callgraph.py           — dirty-set logic, node_hashes table
NEW   tlx/modules/js_analyzer/incremental.py         — recomputation DAG driver
NEW   bin/migrate_db.py                              — schema migration runner
EDIT  bin/db-isolate.py                              — record schema_version in snapshot
```

### 10.6 Rollout

1. **Phase 1**: Persist `node_hashes` and `taint_cache` but do not skip
   anything. Validate cache correctness against full re-runs.
2. **Phase 2**: Skip intra-procedural taint where cache is valid.
3. **Phase 3**: Incremental inter-procedural + implicit_tags.

---

## 11. LLM stage refactor

### 11.1 Why it matters

`claude_agent.py` currently asks Sonnet to compensate for: sanitizer
adequacy reasoning, framework escape contexts, constant-source
detection, length-gate detection, pure-intermediate detection,
controllability inference. Every one of these is a static-analysis
miss. With §2–§10 shipped, the LLM should reason about **what we
cannot pre-compute**: exploit synthesis, version-specific bypasses,
unusual sink contexts, and PoC generation.

### 11.2 Design — canonical chain IR

Replace the current "chain JSON + raw snippets" payload with a
**canonical IR** (`chain_ir.py`):

```python
@dataclass
class ChainIR:
    chain_id: str
    target: TargetSummary           # framework, browser_context, library versions
    source: SourceIR                # qname, taxonomy_id, controllability_score, evidence_lines
    sink: SinkIR                    # qname, taxonomy_id, capabilities, viability_score
    path: list[PathHop]             # [{qname, file, line, kind, edge_class, confidence, snippet_compact}]
    sanitizers: list[SanitizerIR]   # canonicalized + confidence-downgraded
    asyncs: list[AsyncIR]           # continuation hops
    dynamic_resolutions: list[PropShapeIR]
    runtime_evidence: RuntimeIR     # sink_fired?, eval_corpus refs, postMessage trace
    confidence: float               # P(chain) calibrated
    open_questions: list[str]       # things static analysis explicitly does not know
```

`snippet_compact` is a **window**, not the whole function: lines around
the source/sink/edge call site, plus a 3-line context before/after.
Pre-stripped of comments and reformatted to a fixed width.

### 11.3 Prompt architecture

The Sonnet prompt becomes a **verdict template**:

```
You are a JavaScript security auditor with the static analyzer's
report (`ChainIR`) in front of you. Decide whether this chain is
exploitable in the target's browser context. Use ONLY the ChainIR
fields and the snippets attached. Do not infer information that is
not in the ChainIR — if open_questions lists something, you may flag
it; otherwise treat the analyzer's evidence as ground truth.

[ChainIR JSON]
[Snippet bundle]

Output format (strict JSON):
{
  "verdict": "true_positive|false_positive|undetermined",
  "vuln_class": "...",
  "severity": "low|medium|high|critical",
  "proof": "one-sentence reasoning chained to ChainIR fields",
  "evidence_refs": ["chain.path[2].snippet", "chain.sanitizers[0]"],
  "exploit_class": "reflected|stored|dom|cspt|chained|other"
}
```

Sonnet *never* sees raw JSON for `node_tags`, `dataflow_edges`,
`node_sanitizers`. It sees only the canonicalized IR. This kills the
"LLM re-derives static analysis" pattern.

### 11.4 Opus consult — now exploit-only

The `js_consult_opus` tool becomes **exploit synthesis only**:

```
Given a confirmed-TP chain, write a runnable PoC. Output:
{
  "url_template": "https://<host>/...",
  "headers": {...},
  "body": "...",
  "payload": "<actual payload string>",
  "expected_observable": "alert(1) | console.log | etc.",
  "browser_constraints": "Chrome+CSP-policy-X | any | ..."
}
```

No "should I escalate to second opinion" branch — Opus is only invoked
for TPs that need PoCs. Cuts consult cost ~5x.

### 11.5 Retrieval

For exploit synthesis, before calling Opus, retrieve from:

- `wiki` collection: top-3 chunks matching `(vuln_class, framework,
  sanitizer family)`. Already in place via `docs_query`.
- `findings/_index.jsonl` across all targets: prior PoCs for the same
  taxonomy_id.

Inject the top-3 as `prior_exploits` field in Opus prompt.

### 11.6 Token optimization

- ChainIR + window snippets cap at 6k tokens per chain (vs current
  whole-function snippets which routinely hit 20k+).
- Static system prompt cached via `cache_control: ephemeral` (already
  done; preserve).
- Move framework spotlight + sanitizer rubric *out* of the system
  prompt and into the per-chain IR. Lets us drop a 1.5k-token static
  rubric.

### 11.7 Files touched / created

```
NEW   tlx/modules/js_analyzer/chain_ir.py            — dataclass + serializer
NEW   tlx/modules/js_analyzer/snippet_window.py      — window extraction
EDIT  tlx/modules/js_analyzer/claude_agent.py        — switch to IR payload; drop static rubric
EDIT  tlx/modules/js_analyzer/exploit_agent.py       — retrieve prior_exploits; produce structured PoC
EDIT  tlx/modules/js_analyzer/reporter.py            — emit ChainIR alongside legacy chain JSON during transition
NEW   tlx/modules/js_analyzer/prompts/claude_verdict.md  — replace claude_analyst.md
NEW   tlx/modules/js_analyzer/prompts/opus_exploit.md
```

### 11.8 Rollout

Already partially staged via `plans/CC_TAINT_ADVERSARIAL.md` (CC-driven
per-chain adversarial audit). Land §11 *after* that skill is
operational; the two converge into one path.

---

## 12. Prioritized roadmap

### 12.1 Sequencing matrix (ROI vs effort)

| # | Subsystem | FP impact | FN impact | Effort | Risk | Order |
|---|---|---|---|---|---|---|
| **P0** | Browser sink viability + CSP/TT inference (§4) | **-30 to -50%** | 0 | 2 weeks | Low | 1 |
| **P0** | Sanitizer reality (§5) | -15 to -25% | +5 to +15% (no longer dropping partial-clears as safe) | 2 weeks | Low | 2 |
| **P1** | Async/event continuations (§3) | -5% (chains now have real upstream) | **+20 to +40%** | 3 weeks | Medium | 3 |
| **P1** | LLM stage refactor (§11) | -10% (less hallucinated affirmations) | -5% (Sonnet rejects more) | 2 weeks | Medium | 4 |
| **P1** | Confidence-driven pruning (§8) | indirect | indirect; scalability unlocked | 1.5 weeks | Low | 5 |
| **P2** | Dynamic property resolution (§2) | -5% | +10 to +20% | 4 weeks | High (graph explosion risk) | 6 |
| **P2** | Framework adapters (§6) | -5 to -10% per adapter | +5 to +10% per adapter | 1.5 weeks per | Low | 7 (incremental) |
| **P2** | Runtime augmentation (§7) | -5% | **+10 to +20% on bundled obfuscated targets** | 4 weeks | Medium (browser instrumentation) | 8 |
| **P3** | Incremental recompute (§10) | 0 | 0 | 2 weeks | Medium (cache invalidation correctness) | 9 |

### 12.2 Quarterly plan

**Sprint A (4 weeks)** — P0 wins: §4 viability + §5 sanitizer reality.
Single biggest FP-rate reduction. Both fit additively in the current
schema; no chain extractor rewrites. Ship behind feature flags.

**Sprint B (4 weeks)** — P1 recall + LLM refactor: §3 async
continuations + §11 LLM stage refactor. The continuation work unlocks
~30% of currently missed chains; the LLM refactor cuts Sonnet token
spend ~40% by removing the "re-derive analysis" pattern.

**Sprint C (4 weeks)** — P1 scalability: §8 confidence-driven pruning,
plus the React+Next adapters from §6 (in parallel). After this,
hot.jsonl is calibrated rather than top-K by raw score.

**Sprint D (6 weeks)** — P2 dynamic dispatch + runtime augmentation
(§2 + §7). High-value but architecturally heavy. Land in stages with
heavy flag-gating.

**Sprint E (3 weeks)** — Incremental recompute (§10) and remaining
framework adapters. Ship CI integration.

### 12.3 Architectural risks

| Risk | Mitigation |
|---|---|
| Graph explosion from §2 | Hard caps (8 per call site, 20k per target), fallback to original `dynamic` edge. |
| Async continuation cycles | Visited-set keyed by `(node, taint_sig, continuation_count)`. |
| Runtime agent breaks target page | Pure read; monkeypatch wrappers preserve `[[Construct]]`/`[[Call]]` slots; defensive try/catch around every patched call. |
| Confidence model drift | Re-calibrate per 50 verdicts; persist coefficients per target class. |
| Sanitizer registry staleness | Pull DOMPurify/Validator/Sanitize-html releases via `bin/npm_version_diff.py` weekly. |
| LLM ChainIR loses information | Keep legacy JSON payload alongside ChainIR for one quarter; A/B Sonnet verdicts. |
| Per-target DB diverges from global after migrations | `bin/migrate_db.py` re-runs migrations against every per-target snapshot found in `targets/*/db/`. |

### 12.4 Performance budgets (targets)

| Stage | Cold-cache budget | Warm-cache budget |
|---|---|---|
| AST extract (per file) | 50 ms | 0 ms (skipped via file_hashes) |
| Callgraph build (per target, 2k modules) | 12 s | 2 s |
| Intra-procedural taint | 4 s | 0.5 s |
| Inter-procedural taint | 8 s | 1 s |
| Implicit closure | 3 s | unchanged (skip unless direct tags moved) |
| Chain extraction (current) | 8 s | 8 s |
| Chain extraction (with §8 best-first) | **3 s for hot, 12 s for full** | unchanged |
| Browser context inference | 0.5 s | 0 s |
| Sink viability scoring | 0.2 s | 0 s |
| Sanitizer registry lookup | 0.1 s | 0 s |
| LLM Sonnet verdict per chain | ~$0.005 (was ~$0.02) | n/a |
| Opus exploit synth per TP | ~$0.05 (was ~$0.20) | n/a |

### 12.5 Definition of done (overall)

- A clean target re-index takes <30 s for 2k modules.
- `hot.jsonl` precision (TP rate) > 0.6 on the calibration corpus (was
  ~0.35 in the most recent pipeline calibration audit).
- `hot.jsonl` recall on known-TP corpus > 0.85.
- Opus spend per engagement < the budget in `memory.md`.
- Each subsystem has a feature flag, a fallback, and a regression test
  against a tiny synthetic target under `tlx/modules/js_analyzer/tests/`.

---

## 13. Open design questions (not blockers)

1. **Cross-target taint sharing.** Today every target's analysis is
   isolated. Should `prior_exploits` retrieval (§11) cross targets, and
   if so how do we anonymize? Defer until §11 ships.
2. **WASM sinks.** Some targets ship WASM compilation that does
   string-processing. Out of scope for v1 of every section above.
3. **Source maps as truth.** When sourcemaps exist (sourcemap-explode),
   should the canonical qname be original or compiled? We currently
   keep compiled — original would help LLM read but break runtime
   reconciliation (§7). Keep compiled; emit original as `qname_original`
   for LLM rendering only.
4. **HTML template files.** `template_analyzer` parses Angular/Vue
   templates; should React JSX inline strings also flow through it?
   Decide during §6 adapter work.

---

## 14. Migration / backwards compatibility

- **Schema migrations**: every `ALTER TABLE` lands behind
  `bin/migrate_db.py`. Old targets/db snapshots are migrated lazily on
  next access.
- **Feature flags**: All new behavior gated by
  `js_analyzer_config.JSAnalyzerConfig` keys (default off until phase
  passes regression). The config file is auto-loaded by `module.py`.
- **Skill compatibility**: Existing skills (`dom-xss-hunt`,
  `chain-triage`, `opus-deep-audit`, etc.) consume `chains/*.jsonl`
  with stable fields. New fields are additive.
- **CC-taint-adversarial** (plans/CC_TAINT_ADVERSARIAL.md): the new IR
  payload (§11) is the *input* this skill expects; ChainIR shipping
  is the integration point.
- **Reporter / SARIF**: `sarif_writer.py` keeps its current schema.
  Viability + sanitizer-confidence land under SARIF `properties`.

---

## 15. What this plan deliberately does NOT do

- No new core LLM dependency outside the existing whitelist
  (Anthropic + Gemini embeddings).
- No browser fuzzer. The runtime agent is pure observation.
- No symbolic execution engine. The string-lattice in §2 is the closest
  we go.
- No replacement of the call graph schema. Every table change is
  `ALTER TABLE` or new table.
- No SaaS dependency. Everything ships as Python under `tlx/`.

---

## Appendix A — Touched files at a glance

```
tlx/modules/js_analyzer/
  ast_extractor.js                  EDIT  §2 prop emissions, §3 producer metadata, §6 framework hooks
  callgraph.py                      EDIT  Phase D3 (prop refinement), Phase D4 (continuations), framework adapter invocation, node_hashes
  taint.py                          EDIT  multi-fact emission on prop_shapes
  interprocedural_taint.py          EDIT  walk continuation edges
  implicit_tags.py                  unchanged
  taxonomy.py                       EDIT  load `capabilities` block
  taxonomies/sinks.json             EDIT  capabilities per sink
  taxonomies/sanitizers.json        EDIT  version/config metadata
  reporter.py                       EDIT  ChainIR emission, viability_score, calibrated confidence sort
  claude_agent.py                   EDIT  IR payload, drop static rubric
  exploit_agent.py                  EDIT  prior_exploits retrieval, structured PoC
  audit_pipeline.py                 unchanged

  prop_shapes.py                    NEW   §2 symbolic property tracker
  string_lattice.py                 NEW   §2 string abstract domain
  async_graph.py                    NEW   §3 producer detectors
  browser_context.py                NEW   §4 CSP/TT/SSR inference
  sink_viability.py                 NEW   §4 viability scoring
  sanitizer_registry.py             NEW   §5 version+config registry
  sanitizer_bypass_corpus.py        NEW   §5 known-bypass database
  frameworks/__init__.py            NEW   §6 adapter registry
  frameworks/react.py               NEW   §6
  frameworks/nextjs.py              NEW   §6
  frameworks/vue.py                 NEW   §6
  frameworks/angular.py             NEW   §6
  frameworks/svelte.py              NEW   §6
  frameworks/lit.py                 NEW   §6
  frameworks/electron.py            NEW   §6
  chain_confidence.py               NEW   §8 P(chain) computation
  chain_ir.py                       NEW   §11 canonical IR
  snippet_window.py                 NEW   §11 line-window extraction
  incremental.py                    NEW   §10 recompute DAG
  prompts/claude_verdict.md         NEW   §11 verdict-only prompt
  prompts/opus_exploit.md           NEW   §11 PoC-only prompt

bin/
  extract_chains_bounded.py         EDIT  best-first traversal, prop+async aware
  runtime_collector.py              NEW   §7 localhost event collector
  runtime_merge.py                  NEW   §7 static↔runtime reconciliation
  migrate_db.py                     NEW   §10 schema migrator
  calibrate_confidence.py           NEW   §8 logistic fit

runtime/
  agent.js                          NEW   §7 in-page agent (~6 KB)

skills/
  browser-context-infer/SKILL.md    NEW   §4 driver
  runtime-augment/SKILL.md          NEW   §7 driver
```

---

## Appendix B — Pseudocode highlights

### B.1 Best-first chain extraction (§8)

```python
import heapq

def extract_chains(graph, sources, sinks, *, max_chains=4000, partial_p_cutoff=0.05):
    pq = []   # min-heap on -P_partial so highest probability pops first
    seen = set()
    for src in sources:
        p0 = source_controllability(src)
        heapq.heappush(pq, (-p0, [src], p0, ()))

    out = []
    while pq and len(out) < max_chains:
        neg_p, path, p, sanitizer_path = heapq.heappop(pq)
        if -neg_p < partial_p_cutoff:
            continue
        head = path[-1]
        if head in sinks:
            out.append(materialize_chain(path, p, sanitizer_path))
            continue
        if len(path) >= adaptive_depth(p):
            continue
        for nb, edge in graph.successors(head):
            key = (nb, tuple(sanitizer_path))
            if key in seen:
                continue
            seen.add(key)
            p_edge = edge_confidence(edge)
            p_san = sanitizer_factor_for_edge(edge)
            p_new = p * p_edge * (1 - p_san)
            if p_new < partial_p_cutoff:
                continue
            new_san_path = sanitizer_path + ((edge.sanitizer,) if edge.sanitizer else ())
            heapq.heappush(pq, (-p_new, path + [nb], p_new, new_san_path))
    return out
```

### B.2 String-lattice transfer (§2)

```python
TOP = object()  # any string

def join(a, b):
    if a is TOP or b is TOP: return TOP
    u = a | b
    return TOP if len(u) > 16 else u

def transfer(node):
    match node.kind:
        case 'Literal' if isinstance(node.value, str):
            return {node.value}
        case 'TemplateLiteral':
            parts = [transfer(q) for q in node.quasis_and_exprs]
            return product_concat(parts)   # TOP if any part is TOP
        case 'BinaryExpression' if node.op == '+':
            return product_concat([transfer(node.left), transfer(node.right)])
        case 'Identifier':
            return env.get(node.name, TOP)
        case 'CallExpression' if call_is(node, 'String.prototype.concat'):
            return product_concat([transfer(node.callee.object)] + [transfer(a) for a in node.arguments])
        case _:
            return TOP
```

### B.3 Continuation taint injection (§3)

```python
def propagate_continuations(conn):
    for edge_id, producer_kind, arg_index, event_taint_paths in fetch_continuation_edges(conn):
        caller, callee = edges_endpoints(edge_id)
        # The callee's param at arg_index receives event-shaped taint.
        param_var = nth_param_of(callee, 0)        # always 0 for event handlers
        if producer_kind in ('addEventListener', 'postMessage_in'):
            for path in event_taint_paths or ['data', 'origin']:
                inject_taint(callee, f'{param_var}.{path}',
                             source_rule='dom_message' if producer_kind == 'postMessage_in' else 'dom_event_data',
                             from_edge=edge_id)
        elif producer_kind in ('promise_then', 'await', 'fetch_chain', 'rxjs_subscribe'):
            # Upstream-tainted resolved value flows into arg 0.
            for src_rule in upstream_taint_rules(caller):
                inject_taint(callee, param_var, source_rule=src_rule, from_edge=edge_id)
```

---

End of plan.
