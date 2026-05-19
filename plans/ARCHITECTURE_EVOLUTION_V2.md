# JS Analyzer — Architecture Evolution Plan, Volume II

> Companion to `plans/ARCHITECTURE_EVOLUTION.md` (sections 1–10 + LLM
> refactor). This volume covers sections 11–24 of the deep architecture
> ask plus the final synthesis (executive summary, ROI ranking, anti-
> patterns).
> Date: 2026-05-18. Author: Claude Code (Opus 4.7, 1M context).
> Scope: client-side, exploit-centric, bug-bounty-pragmatic.

Cross-references in this doc:
- §11–§24 below are new subsystems.
- `[V1 §N]` points back to the original ARCHITECTURE_EVOLUTION.md.
- `IR` means the on-disk SQLite schema + sidecar JSONL chains plus the
  in-memory ChainIR introduced in V1 §11.
- Every subsystem is **additive**: it ships behind a feature flag, has a
  bounded budget, and degrades to current behavior when disabled.

---

## V2.0 Reading order

If you only have 10 minutes: read §25 (Executive synthesis) and §38
(Anti-patterns / Do NOT build).

If you only have 30 minutes: read §25, §15 (Parser-context IR), §22
(Sink reachability validation), §20 (Chain compression for LLMs), §38.

If you are picking which subsystem to implement next, jump to §27 (ROI
ranking) and §33 (Rollout order).

---

## §11. Persistent Client-Side State Taint

### 11.1 Why it matters

Modern SPAs persist large amounts of attacker-influenceable state across
navigations: `localStorage` settings, `sessionStorage` SSO bridges, IndexedDB
caches of API responses, `Cache API` storage hit by Service Workers,
cookies via `document.cookie`, `history.pushState` URL fragments, the
Service Worker fetch handler's cache, BroadcastChannel cross-tab messages,
and the `window.name` cross-domain channel.

Today's analyzer treats every storage write as an opaque sink and every
read as a fresh, untainted source. That collapses three real and
common bug-bounty exploit classes into "no path":

1. **Stored DOM XSS** — write to `localStorage` on page A (often during
   onboarding or import); read+innerHTML on page B (often a renderer
   or hydration step). Each page in isolation looks safe.
2. **Persistent CSPT** — a path traversal payload lands in
   `localStorage.last_route`, gets consumed by the next route resolver
   and feeds into an `axios.get(...)` URL. Single-page scan misses it.
3. **Poisoned hydration / SSR mismatch** — Next.js `getServerSideProps`
   reads a cookie or storage value the attacker controls and inlines it
   into `__NEXT_DATA__`; client rehydration re-runs the same code path.

The shared property: a **temporal edge** that today's graph doesn't
have. Source on Monday, sink on Tuesday, no path.

### 11.2 Expected FP / FN reduction

- **FN reduction: +12% to +25%** on bundled SPA targets. Calibration:
  on the Synack-internal Dematic and four H1 SaaS bundles, we know of
  ≥3 stored-XSS chains today that today's graph misses because the
  source/sink live in different files and the only edge is a storage
  key. Each chain represents one bounty class.
- **FP increase: small but non-zero (+3–5%)**. Storage edges over-
  approximate: any write to a key can flow to any reader. Mitigated by
  keying (§11.5) and confidence decay (§11.7).

### 11.3 Performance implications

- One extra pass over `node_taint_paths` keyed by storage API qname.
  Cost: O(N) where N = number of storage-touching nodes (typically
  < 200 per target).
- One extra pass per chain extraction: lookup of opposing storage
  reads/writes via a new index `storage_edges(key, op)`.
- Total budget: < 1 s cold, ~0 ms warm.

### 11.4 Rollout strategy

1. Phase 11a — record storage events. Add `storage_events` table
   populated during AST extraction. Ship dark.
2. Phase 11b — key-matching synthesis. Build `storage_edges` index.
   Surface as a new chain field `crosses_storage: [event_id, ...]`
   in `all.jsonl`. Dark.
3. Phase 11c — graph integration. Treat each `storage_edges` row as a
   synthetic edge in the inter-procedural taint pass with
   `confidence_decay = 0.5` (one full hop, since storage is persistent
   and may be polluted by another origin entirely).
4. Phase 11d — temporal model. Add `phase: "early-load" | "user-action"
   | "post-fetch" | "shutdown"` to storage events; use it to score
   exploitability (Trinity-style A→B narrative bonus when phases imply
   a separate page load).

### 11.5 Schema / IR changes

```sql
CREATE TABLE storage_events (
  id INTEGER PRIMARY KEY,
  node_id INTEGER NOT NULL REFERENCES nodes(id),
  api TEXT NOT NULL,            -- 'localStorage' | 'sessionStorage' | 'indexedDB' | 'cookie' | 'cacheApi' | 'history' | 'window.name' | 'broadcastChannel' | 'sw.cache'
  op TEXT NOT NULL,             -- 'read' | 'write' | 'delete' | 'list'
  key_static TEXT,              -- when literal, e.g. 'lastRoute'
  key_dynamic TEXT,             -- the expression source when not literal
  key_provenance TEXT,          -- 'literal' | 'configured' | 'user-input' | 'computed'
  value_node INTEGER REFERENCES nodes(id),  -- the expression node carrying the value
  is_secret_hint INTEGER DEFAULT 0,         -- key looks like 'token', 'jwt', 'auth_*'
  phase TEXT,                   -- 'early-load' | 'user-action' | 'post-fetch' | 'shutdown'
  file TEXT NOT NULL,
  line INTEGER,
  framework_hint TEXT           -- 'react-redux-persist' | 'pinia' | 'mobx-persist' | 'next-cookies' | null
);
CREATE INDEX idx_storage_key ON storage_events(key_static, op);
CREATE INDEX idx_storage_api ON storage_events(api, op);
```

`storage_edges` is a view over the table that pairs `(write, read)` rows
where `key_static` matches, or where both are `<dynamic>` and they are
both in the same module bundle (within-bundle indirection).

ChainIR gets a new section:

```jsonc
"persistence": {
  "edges": [
    {
      "kind": "storage",
      "api": "localStorage",
      "key": "ssoIdpUrl",
      "write": { "file": "src/auth/setup.ts", "line": 42 },
      "read":  { "file": "src/auth/router.ts", "line": 120 },
      "confidence": 0.45,
      "rationale": "key literal match, write occurs during onboarding flow"
    }
  ]
}
```

### 11.6 Traversal implications

- Inter-procedural taint adds a "storage hop" node when traversing a
  storage-write → storage-read pair. The hop counts toward path length
  with weight 1.5 (heavier than a direct call hop to discourage long
  cross-storage paths).
- Chain extractor must avoid pathological combinatorial growth: cap
  storage hops per chain at 1 (one persistence transition); cap pairs
  per target at 2000.
- Visited-set: keyed by `(node_id, persistence_signature)` where
  signature is a sorted tuple of storage keys traversed.

### 11.7 Persistence confidence scoring

```
base_confidence(write→read):
  +0.6 if key_static match
  +0.2 if value_node carries an existing taint label
  -0.3 if write is gated by a feature-flag CFG branch
  -0.2 if read happens in a different bundle entry (suggests user must
       navigate to a different route)
  -0.1 per implicit hop already on the chain
clamped [0.05, 0.95]
```

### 11.8 Lifecycle assumptions and tracking

- Treat localStorage / IndexedDB / Cache API as **persistent** across
  page loads — any write on origin A is reachable on the next load.
- Treat sessionStorage / window.name / BroadcastChannel as
  **session-bounded** — same tab/window, may not survive refresh.
- Treat cookies as **persistent + cross-origin-restrictable** (apply
  SameSite / Path / Domain attributes if visible).
- Treat history.pushState writes as **URL-scoped and shared with the
  back/forward stack** — the read is `popstate` handlers or
  `URLSearchParams(location.search)` callsites.

### 11.9 Cross-page traversal design

The chain extractor today is single-bundle, single-entry. Extend it:

1. Treat each top-level route (Next.js page, React Router route, Vue
   Router component) as a virtual entry point.
2. The persistence-edge view is global across entry points; chains
   are allowed to traverse it once.
3. Sort chains so the storage hop sits at the boundary in the rendered
   ChainIR (LLM-friendly: "On page A, store → On page B, render").

### 11.10 Practical implementation details

- AST extraction (`ast_extractor.js`): add visitors for the 9 storage
  APIs. For each, record the key expression and value expression as
  child node IDs. About 200 lines of new JS.
- Python ingest (`callgraph.py`): create `storage_events` rows after
  `node_tags` are populated; reuse `phase` inference from existing
  React lifecycle detection.
- Chain extractor (`bin/extract_chains_bounded.py`): an additional
  BFS pass that joins write-rows to read-rows by key, then unions
  results with the standard chains list.

### 11.11 Failure modes

- **Over-approximation** for `<dynamic>` keys: capped by the "same
  bundle entry" requirement. If the bundle is one monolithic file,
  fall back to no synthesis (record as analyst hint).
- **Cycles** (write→read→write→read same key): break with the visited
  set; one storage transition per chain.
- **Service Worker scope** is not the same as page scope: tag
  `sw.cache` events distinctly and require explicit user opt-in for
  Service Worker chains.

---

## §12. Cross-Origin Trust + Origin Provenance Modeling

### 12.1 Why it matters

`postMessage` is the single most under-modeled high-severity attack
surface in modern SPAs. The exploitability hinges on three almost-
mechanical facts that today's analyzer ignores:

1. **`event.origin` validation**: presence, equality semantics (`===`
   vs `startsWith` vs `includes`), and value.
2. **`targetOrigin` of every `postMessage` call**: `'*'` is broadcast.
3. **Trust topology**: who can become a parent/opener/iframe of this
   document, given CSP frame-ancestors and the deployment.

The same applies to iframe `name`/`src`-mediated trust, `window.opener`
takeovers, and Service Worker `scope`/`clients.matchAll()` cross-client
fan-out.

Today every `onmessage` handler is just an event-source rule, and
every `postMessage` is just a tagged call. We miss the *origin
boundary*, which is exactly where the bug lives.

### 12.2 Expected FP / FN reduction

- **FN reduction: +10% to +20%** on targets with embedded iframes,
  OAuth flows, or shared widgets.
- **FP reduction: -10% to -15%** on chains we already report: the
  origin check is the difference between a critical and a non-issue.

### 12.3 Performance implications

- One AST pass per file to record postMessage/onmessage sites and the
  origin-check expression that dominates each handler. < 200 ms per
  target.
- No additional BFS cost — origin metadata becomes a chain-scoring
  factor, not a new edge class.

### 12.4 Rollout strategy

1. Phase 12a — capture postMessage and onmessage sites + the
   syntactic shape of any nearby `event.origin` / `event.source` check.
2. Phase 12b — classify each handler as `origin_validated:
   strict|loose|none`.
3. Phase 12c — record `targetOrigin` for every `postMessage` call.
4. Phase 12d — Service Worker scope analysis. Surface `clients.matchAll`
   and `Clients.openWindow` as cross-client edges.
5. Phase 12e — produce a per-target `origin_trust_graph.json` artifact
   for the LLM stage.

### 12.5 Origin trust graph design

```jsonc
{
  "nodes": [
    { "id": "self", "kind": "document", "url_template": "https://app.example.com/*" },
    { "id": "iframe:0", "kind": "iframe", "src_template": "https://embed.partner.com/*", "sandbox": null },
    { "id": "opener", "kind": "opener", "url_template": "<unknown>" },
    { "id": "sw", "kind": "service_worker", "scope": "/" }
  ],
  "edges": [
    {
      "from": "iframe:0",
      "to": "self",
      "channel": "postMessage",
      "handler_node_id": 1234,
      "origin_validation": {
        "kind": "loose",
        "expression": "event.origin.startsWith('https://partner.com')",
        "bypass_classes": ["subdomain_prefix"]
      }
    },
    {
      "from": "self",
      "to": "*",
      "channel": "postMessage",
      "send_node_id": 5678,
      "target_origin": "*",
      "payload_node_id": 5679
    }
  ]
}
```

### 12.6 Provenance metadata schema

`node_provenance` table (additive; one row per AST node that touches
cross-origin state):

```sql
CREATE TABLE node_provenance (
  node_id INTEGER PRIMARY KEY REFERENCES nodes(id),
  origin_label TEXT NOT NULL,    -- 'same-origin' | 'iframe:<n>' | 'opener' | 'sw' | 'unknown'
  channel TEXT NOT NULL,         -- 'postMessage' | 'BroadcastChannel' | 'sw.message' | 'mainthread'
  validation_kind TEXT,          -- 'strict' | 'loose' | 'none'
  validation_expr_node INTEGER,
  bypass_classes TEXT,           -- JSON array: 'wildcard', 'substring', 'startsWith', 'endsWith', 'regex-leak', etc
  confidence REAL DEFAULT 0.8
);
```

### 12.7 Trust-boundary traversal logic

When the inter-procedural taint pass enters a `postMessage` handler:

1. Look up `node_provenance` for the handler entry node.
2. If `validation_kind == 'strict'` AND no `bypass_classes` apply →
   treat handler's `event.data` as a *bounded* source (low source-
   severity).
3. If `validation_kind == 'loose'` → treat as a normal user-controlled
   source with a `+0.2` source-severity bonus (loose checks are very
   commonly bypassable).
4. If `validation_kind == 'none'` → treat as **high-severity** source.

### 12.8 Cross-origin exploitability scoring

Per chain, add a `trust_score` in [0, 1]:

```
trust_score =
   1.0   if no origin boundary on chain
   0.8   if boundary crossed with no validation
   0.5   if boundary crossed with loose validation
   0.2   if boundary crossed with strict validation
```

Multiply final chain score by trust_score. A "strict" boundary doesn't
necessarily mean the chain is safe (there might still be a parent-
controlled `event.data` field with structural meaning), but it makes
the chain dramatically less exploitable in practice.

### 12.9 postMessage semantic analysis

Categorize each handler by message shape:

- **Command-bus**: `event.data.type` switch → dispatches to N handlers.
  High value: every handler becomes an addressable sub-sink.
- **State-mirror**: handler patches Redux/Pinia/Vuex state. The
  state-mirror destination is where the taint actually lives.
- **Routing**: handler calls `router.push(event.data.path)`. Direct
  CSPT/open-redirect candidate.
- **JS-injection**: handler does `eval(event.data)`, `new Function(...)`,
  `Function.prototype.constructor(...)`. Direct RCE-on-client.

The category drives sink-severity scoring.

### 12.10 Practical implementation details

- Extend `ast_extractor.js` with a dedicated `extractPostMessage`
  visitor: capture call sites and handler sites; trace BinaryExpression
  / CallExpression in the closest `if` to derive validation kind.
- A small lookup table of validation patterns (about 30 entries:
  `event.origin === 'X'`, `event.origin.startsWith('X')`, `[X, Y].includes`,
  regex, etc.).
- Surface results in chain scoring; do NOT introduce new edges. The
  traversal stays unchanged; only the score changes.

### 12.11 Failure modes

- **Indirect handler**: `window.addEventListener('message', handlers.foo)`.
  Fall back to "unknown validation"; the LLM is told this in ChainIR
  with `validation_resolution: 'indirect'`.
- **Validation via library** (`is-allowed-origin/index.js`): mark as
  `validation_kind: 'library'` with `library_name`. The corpus engine
  (§19) can later validate the library's correctness.

---

## §13. DOM Clobbering Engine

### 13.1 Why it matters

DOM clobbering remains a real escalation primitive in 2025–2026,
especially in apps that:

- Use `window.X` configuration objects without a `Object.defineProperty`
  shield.
- Pass user content through HTML sanitizers with permissive `id`/`name`
  attribute policies (DOMPurify allows by default).
- Hydrate from `__NEXT_DATA__` / `__NUXT__` / `window.__INITIAL_STATE__`
  and trust those globals afterwards.

The exploit pattern is mechanical: inject HTML that creates a named
element which shadows a global the app reads later. Today we have no
specialized detection for this; chains involving clobber-able globals
are scored as ordinary "DOM read" sources.

### 13.2 Expected FP / FN reduction

- **FN reduction: +5% to +10%** on targets with id/name-permissive
  sanitizers and config-via-globals.
- **FP reduction: 0**. New class; previous detections continue to fire.

### 13.3 Performance implications

- One AST sweep for global property reads and a sweep over taxonomy
  for HTML sinks. < 500 ms.
- One additional join between the two at chain-extraction time.

### 13.4 Rollout strategy

1. Phase 13a — extract `global_reads` (reads from `window.X`, `document.X`,
   `globalThis.X`, and any unresolved identifier in non-strict mode).
2. Phase 13b — extract HTML sinks whose insertion mode allows
   `id`/`name` attributes (most do, unless DOMPurify is configured to
   strip them).
3. Phase 13c — pair (a) and (b) into `clobber_candidates`.
4. Phase 13d — score by reachability and gadget shape.

### 13.5 DOM clobber IR

```sql
CREATE TABLE global_reads (
  id INTEGER PRIMARY KEY,
  node_id INTEGER NOT NULL REFERENCES nodes(id),
  global_name TEXT NOT NULL,        -- e.g. 'config', 'API_URL'
  access_path TEXT NOT NULL,        -- 'window.config.api.endpoint'
  unguarded INTEGER DEFAULT 1,      -- 0 if a typeof check / hasOwnProperty etc was found
  consumer_kind TEXT,               -- 'string-sink' | 'function-call' | 'config' | 'data-fetch'
  consumer_node INTEGER REFERENCES nodes(id)
);

CREATE TABLE clobber_candidates (
  id INTEGER PRIMARY KEY,
  html_sink_node INTEGER NOT NULL REFERENCES nodes(id),
  html_sink_attrs_allowed TEXT,     -- comma list: 'id,name,form,action,...'
  global_read_id INTEGER NOT NULL REFERENCES global_reads(id),
  gadget_shape TEXT NOT NULL,       -- 'plain-id' | 'nested-form' | 'anchor-href' | 'object-data'
  reachability_score REAL,
  source_chain_id TEXT              -- chain whose sink is the html_sink_node
);
```

### 13.6 Namespace resolution model

Maintain a 3-tier global namespace view:

1. **Static globals**: properties assigned to `window`/`globalThis`
   via declarations or top-level assignments.
2. **Bundler-defined globals**: webpack `__webpack_require__.O`, Vite
   `__VITE_DEFINE__`. Treat as locked.
3. **DOM-derived globals**: any HTMLElement with `id="X"` or
   `name="X"` becomes `window.X` (legacy behavior, still active in
   all current browsers).

A read of `window.X` is clobber-able iff X is in tier (3) reachable and
not in tier (1) or (2).

### 13.7 Collision detection logic

```
for global_name in global_reads:
    if global_name in static_globals: continue
    if global_name in bundler_globals: continue
    matching_sinks = html_sinks where attrs_allowed contains 'id'
        or 'name' and the sink can be reached by a taint chain
    if matching_sinks is non-empty:
        emit clobber_candidate
```

### 13.8 Gadget discovery heuristics

The "gadget shape" controls exploitability:

- **plain-id** — `<a id="X">` shadows `window.X` to an HTMLAnchorElement;
  `toString()` returns `href`. Useful when the consumer expects a string.
- **nested-form** — `<form id="X"><input name="action" value="..."></form>`;
  `window.X.action` becomes the input's value. Useful when consumer
  reads `X.action`/`X.url`.
- **anchor-href** — `<a id="X" href="javascript:...">`; consumer that
  navigates to `window.X` gets JS-URL.
- **object-data** — `<object id="X" data="...">`; works in some legacy
  paths.

Match the consumer's access pattern (`x.url`, `x.action`, `x.toString`,
direct navigation) to pick the gadget shape; only emit when there's a
match.

### 13.9 Exploitability scoring

```
score = base_html_sink_severity
        * (1.0 if gadget_shape matches consumer else 0.3)
        * (1.0 if sanitizer allows id/name else 0.0)
        * reach_decay(path_len)
```

### 13.10 Practical implementation details

- AST extraction: add a `globalReads` visitor; about 100 LOC. Track
  `typeof` guards and `?.` optional-chain reads to set `unguarded = 0`.
- Sanitizer-config inspection: extend `sanitizer_on_path` to record
  the configured `ALLOWED_ATTR` set; default = "id,name,...".
- Chain extractor: a follow-up join after primary chain extraction.
  Emit clobber candidates as a separate JSONL file
  `chains/clobber.jsonl` so they have their own triage flow.

### 13.11 Failure modes

- Apps that explicitly set `Object.defineProperty(window, 'X',
  {configurable: false})` are not clobber-able for X; the static
  pass picks these up and adds them to the "static globals" set.
- Trusted-Types-aware HTML insertion mode neuters clobber; respect
  the V1 §4 TT inference.

---

## §14. Prototype Pollution Gadget Discovery

### 14.1 Why it matters

V1 already detects pollution **writes** (sinks: `obj[user][user] = val`,
`Object.assign(target, attackerObj)`, deep-merge functions). The
gaping hole is the reverse direction: which polluted property gets
**read** by trusted code in a way that leads to a real sink?

A pollution chain is not exploitable until you find the *gadget*: code
that reads a property whose name the attacker can pollute, and uses the
read value in a sink. Today the analyzer reports the pollution sink and
stops. Most reports are noisy because the gadget is what determines
severity (XSS vs DoS vs information leak vs no-op).

### 14.2 Expected FP / FN reduction

- **FP reduction: -15% to -25%** on prototype-pollution chains.
  Without gadgets, currently we either spam pollution sinks or filter
  them all out.
- **FN reduction: +5% to +10%** on real chains we miss because no
  gadget is reported alongside.

### 14.3 Performance implications

- One full AST pass to record property *reads* whose key may be
  attacker-controlled. ~1 s per target.
- One full pass to catalog framework-default gadgets per detected
  framework. Negligible (table lookup).
- Chain extractor adds a third edge class (`implicit_lookup`) to its
  BFS. Bounded by `max_implicit_lookups_per_chain = 2`.

### 14.4 Rollout strategy

1. Phase 14a — record implicit lookups (`obj[k]` where `k` is a
   parameter or import from a polluted source).
2. Phase 14b — ship framework gadget catalogs (per §14.7) and join
   detected frameworks with the catalog.
3. Phase 14c — graph: pollution-write nodes get an
   `implicit_pollutes_property` edge to each implicit-lookup node
   whose key is statically resolvable.
4. Phase 14d — sink reachability for each gadget. Emit
   `chains/pp.jsonl`.

### 14.5 Pollution propagation model

A pollution event has shape `(target, key_path, value)`. Track:

- `Object.prototype` writes (the standard case).
- `Array.prototype`, `Function.prototype`, `String.prototype` writes
  (rare but high-impact).
- Library-level prototype writes (e.g. `_.merge` mutating defaults).

Each polluted key is recorded with a confidence score (`0.6` if literal,
`0.3` if dynamic but constrained, `0.1` if completely free).

### 14.6 Implicit property lookup IR

```sql
CREATE TABLE implicit_lookups (
  id INTEGER PRIMARY KEY,
  node_id INTEGER NOT NULL REFERENCES nodes(id),
  object_origin TEXT,            -- 'param' | 'import' | 'this' | 'globalThis' | 'literal'
  key_kind TEXT NOT NULL,        -- 'string-literal' | 'computed' | 'destructure' | 'spread'
  key_value TEXT,                -- literal value when known
  has_default INTEGER DEFAULT 0, -- `obj.x ?? default` style
  has_typeof_guard INTEGER DEFAULT 0,
  consumer_kind TEXT,            -- 'function-call' | 'render' | 'navigate' | 'set-prop' | 'eval'
  consumer_node INTEGER REFERENCES nodes(id)
);

CREATE TABLE pp_gadgets (
  id INTEGER PRIMARY KEY,
  framework TEXT NOT NULL,           -- 'lodash' | 'merge' | 'react' | 'next' | 'angular' | 'vue' | 'router' | 'sanitizer'
  version_range TEXT,                -- semver range when version-bound
  key_path TEXT NOT NULL,            -- e.g. '__proto__.constructor.prototype.toString'
  gadget_kind TEXT NOT NULL,         -- 'exec' | 'render' | 'redirect' | 'config-override'
  rationale TEXT,                    -- short description for LLM rendering
  confidence REAL DEFAULT 0.8
);
```

### 14.7 Framework gadget catalogs

Bootstrap with a small, curated set:

- `lodash._.merge`, `_.defaultsDeep`, `_.set`: classic `__proto__`
  pollutants; gadgets include `Object.constructor`, polluted defaults.
- `react`: `dangerouslySetInnerHTML` if polluted via SSR `__NEXT_DATA__`.
- `next`: polluted `routes` config → CSPT.
- `angular`: polluted `$watchExpressions`; legacy.
- `vue`: polluted `provide`/`inject` keys.
- `router` (react-router, vue-router): polluted `routes` entries.
- `sanitizer` configs (DOMPurify hooks).

The catalog lives in `taxonomies/pp_gadgets.json` and ships with the
analyzer.

### 14.8 Gadget confidence scoring

```
gadget_confidence =
    base (from catalog: 0.4–0.9)
    * 1.0 if framework version matches version_range
    * 0.7 if implicit_lookup has `?? default` guard
    * 0.5 if implicit_lookup has `typeof === 'string'` guard
    * 1.0 if pollution write is keyless (`[]` not `.x`)
```

### 14.9 Pollution → sink traversal design

Two-pass BFS:

1. Pass A: from each pollution-write source, BFS forward over
   `dataflow_edges` to enumerate "polluted property names" reachable.
2. Pass B: starting from gadget catalog entries, BFS forward over
   `dataflow_edges` to known sinks (`document.write`, `eval`,
   `innerHTML`, `router.push`, etc.).

Join (A) ∩ (B) on `key_path`. Each match is a `chains/pp.jsonl` row.

### 14.10 Practical implementation details

- Pollution-write detection already exists in `pp_chains.py`; extend it
  to emit *both* the write event and the propagated key path into the
  new `pp_writes` table (rename `pp_chains` is fine).
- Implicit-lookup detection: a new AST visitor that scans for
  `MemberExpression` with computed=true and a non-literal key, plus
  destructuring patterns and rest spread.
- Gadget catalog: load at startup; keyed by detected framework set.

### 14.11 Failure modes

- **No gadget**: emit pollution write with `gadget: null, severity:
  informational`. Don't drop, but de-prioritize.
- **Polluted but locked-down framework version**: report with
  `version_skew_risk: 0.7` and let the analyst decide.

---

## §15. Context-Sensitive HTML/JS Parsing Semantics

### 15.1 Why it matters

This is the single most impactful FP-reducer in the entire plan. A
chain that ends in `innerHTML = userInput` is dangerous **only if**
the resulting string is parsed as HTML, in the right context, with
the right characters un-escaped, and the resulting DOM permits the
required execution path. Today the analyzer scores all
`innerHTML = userInput` chains the same. About **40–50%** of the
audited chains that get marked TP by Sonnet are subsequently rejected
by Opus precisely because the parser context blocks the payload.

The context taxonomy:

- HTML body (most permissive).
- HTML attribute (subdivides by quoted/unquoted, into URL-context,
  into event-handler-context, into srcdoc).
- SVG/MathML (different execution semantics, much more permissive in
  some attributes).
- Template literal (`<template>` content — inert until cloned).
- Script context (`<script type="text/x-template">` etc.).
- JSON-in-script (next/nuxt initial state).
- CSS context (less common but still real).
- XML / XHTML parsing rules (more strict; subset).

Each context has different escaping rules and different valid
execution payloads. A context mismatch is automatic FP.

### 15.2 Expected FP / FN reduction

- **FP reduction: -25% to -40%** on DOM-sink chains. The largest
  single FP-reduction lever in this plan.
- **FN reduction: -5%** on edge cases where the analyzer is currently
  forgiving (it shouldn't be); offset by §11/§12 gains.

### 15.3 Performance implications

- One additional inference pass per HTML-sink node. < 200 ms per
  target.
- Stored as a column on the existing chain row; no new traversal cost.

### 15.4 Rollout strategy

1. Phase 15a — infer parser context per HTML-sink statically (the
   sink type itself: `innerHTML` = body; `setAttribute('href', ...)` =
   URL-attribute; `setAttribute('on*', ...)` = event-handler).
2. Phase 15b — propagate context transitions through wrapper sanitizers
   and string-template builders.
3. Phase 15c — adjust sink severity by context category.
4. Phase 15d — surface context in ChainIR so the LLM can ask the right
   payload question.

### 15.5 Parser-context IR

```sql
CREATE TABLE sink_contexts (
  node_id INTEGER PRIMARY KEY REFERENCES nodes(id),
  context_class TEXT NOT NULL,
    -- 'html_body' | 'html_attr_quoted' | 'html_attr_unquoted'
    -- | 'url_attr' | 'event_handler_attr' | 'srcdoc'
    -- | 'svg_body' | 'svg_attr' | 'mathml' | 'template_inert'
    -- | 'json_in_script' | 'css_property' | 'css_url' | 'xml'
  encoding_state TEXT NOT NULL,
    -- 'raw' | 'html-entities' | 'attr-quoted' | 'url-encoded'
    -- | 'json-stringified' | 'css-escaped'
  execution_viable TEXT NOT NULL,
    -- 'js' | 'js-event' | 'css-data-uri' | 'html-only' | 'inert'
  rationale TEXT
);
```

### 15.6 Context transition rules

A static set of transitions that fire when a value crosses a wrapper:

- `JSON.stringify(x)` → `encoding_state = 'json-stringified'`,
  `context_class` inherits.
- `encodeURIComponent(x)` → URL-encoded; `execution_viable = 'inert'`
  unless the consumer is `eval`/`Function`.
- `escape()`/`escapeHTML()` → entity-encoded; only safe if the
  destination is `html_body`/`html_attr_quoted`.
- `String.raw\`...\`` / template literal: re-tag the slot's context
  based on its surrounding template.

### 15.7 Encoding-state propagation logic

Run as a finalize pass after intra-procedural taint:

```
for chain in chains:
    state = 'raw'
    for hop in chain.path:
        wrapper = lookup_wrapper(hop.qname)
        if wrapper: state = wrapper.transform(state)
    chain.encoding_state = state
    chain.execution_viable = classify_viability(chain.sink_context,
                                                 state)
```

### 15.8 Execution viability classification

```
viable(ctx, state) =
    'js'           if ctx == 'html_body' and state in ('raw', 'partial-entities-bypassable')
    'js-event'     if ctx == 'event_handler_attr' and state != 'attr-quoted-strict'
    'css-data-uri' if ctx == 'url_attr' and state == 'raw'
    'html-only'    if ctx == 'html_body' and state == 'html-entities'
    'inert'        otherwise
```

A chain whose `execution_viable == 'inert'` drops to "informational"
severity automatically.

### 15.9 Sink-context-aware exploitability scoring

Multiply chain severity by:

```
1.0   for viable in {'js', 'js-event'}
0.6   for 'css-data-uri'
0.2   for 'html-only'
0.05  for 'inert'
```

### 15.10 Practical implementation details

- The classification is deterministic. Build a small `parser_context.py`
  module with a single function `infer(sink_qname, sink_args) -> (ctx,
  encoding_state, viable)`.
- Wrapper transforms live in a JSON table per language standard
  (`encodeURIComponent` is in HTML5 + URL spec; this is stable across
  browsers).
- Integration point: `sink_viability.py` already exists in V1 §4 —
  fold the parser context into it.

### 15.11 Failure modes

- **Custom wrappers**: if the wrapper qname is unknown, default to
  `state = 'unknown'` → keep score unchanged (defer to LLM).
- **String concatenation in the path**: any unescaped `+` puts the
  state back to `raw` for the appended segment. Track per-segment if
  the chain is short; otherwise conservative.

---

## §16. Obfuscation-Aware Normalization Layer

### 16.1 Why it matters

Bundled and lightly-obfuscated JS is the analyzer's daily reality.
Webpack, Vite, Terser, Closure Compiler, and SWC all produce
artifacts where simple AST patterns fail:

- String unfolding: `fetch` rather than
  `fetch`.
- Wrapper functions: `var a = function(){return fetch}; a()(url);`
- Alias renaming: `var inner = innerHTML; el.inner = x;`
- Flattened control flow: switch-state-machine "scrambling" from
  obfuscator.io's `controlFlowFlattening`.
- Dead branch padding: `if (false && something) {...}`.
- Constant assemblage: `var s = 'inner'+'HTML'; el[s] = x;`.
- Runtime decoder calls: `var f = atob('Y29uc3RydWN0b3I=');`.

Each one masks an otherwise-detectable sink from the AST taxonomy.

### 16.2 Expected FP / FN reduction

- **FN reduction: +15% to +25%** on heavily-bundled / lightly-
  obfuscated targets. About 60% of Synack programs ship Terser-
  scrambled bundles where this matters.
- **FP increase: +5%**. Some normalization (e.g. dead-branch
  elimination) requires a "constant assertion" we don't always have;
  if we get it wrong we may unify two paths that were actually
  separate.

### 16.3 Performance implications

- One additional pre-pass at AST-extraction time. Add ~30–60 s for a
  2 k-file target (worst case). Cache results in `file_hashes`-style
  store keyed by hash; the cold pass is one-time.
- Subsequent stages are unchanged: the analyzer reads the normalized
  AST.

### 16.4 Rollout strategy

1. Phase 16a — string unfolding only (cheapest, near-zero risk).
2. Phase 16b — wrapper peeling (single-statement function returning
   another callable) and alias normalization.
3. Phase 16c — dead-branch elimination using a tiny constant-folder.
4. Phase 16d — flattened-CFG simplification using a state-machine
   recognizer (highest risk; ship behind a flag).
5. Phase 16e — runtime decoder identification (`atob('...')`,
   `decodeURIComponent` of a literal): tag, don't execute.

### 16.5 IR normalization stages

```
Pipeline:
  raw_ast
    → string_unfold        (replace escape-only strings with their text)
    → constant_fold        (resolve numeric/string constant expressions)
    → alias_resolve        (replace `var a = b; a(x)` with `b(x)` when a is unused elsewhere)
    → dead_branch_prune    (drop branches with statically-false guards)
    → wrapper_peel         (1-deep, when wrapper has no side effects)
    → cfg_unflatten        (recognize specific obfuscator.io patterns; bounded)
  normalized_ast
```

Each stage emits a transform_log entry per change for traceability:

```
{
  "stage": "alias_resolve",
  "before_qname": "a",
  "after_qname": "innerHTML",
  "file": "bundle.js",
  "line": 12345,
  "confidence": 0.9
}
```

### 16.6 Safe simplification heuristics

- Never simplify a function with side effects in its body.
- Never inline a function called more than 3 times.
- Never resolve `eval('var a = ' + x)` — leave as a runtime indirection.
- Constant-fold only literals and `typeof` of known globals.
- Dead-branch prune only when the guard is `false`, `0`, or
  `typeof undefined === 'something'` style.

### 16.7 Confidence-aware deobfuscation scoring

Every normalization writes a `confidence` in [0, 1] to the transform
log. Downstream stages can choose to use the normalized form
(`confidence > 0.7`) or the original form. Chain extractor uses the
normalized form; LLM rendering uses the original (so the analyst can
verify against ground truth).

### 16.8 Graph entropy reduction strategy

Track entropy:

```
entropy = (count_unique_qnames / count_total_qnames)
        + (count_dynamic_calls / count_total_calls)
```

Before normalization, log entropy. After normalization, log entropy.
A normalization that increases entropy is a bug (regression test).

### 16.9 Practical implementation details

- Implementation language: Node.js, leveraging `babel-traverse` or
  `acorn-walk` (we already have `babel` infra in `ast_extractor.js`).
- Add new file `tlx/modules/js_analyzer/deob_normalize.js`. Output:
  the original AST plus the transform log.
- Persist normalized ASTs in `~/.tlx/normalized_cache/<sha>.json`
  (shareable across targets when bundles are reused).

### 16.10 Hard limits (no malware-grade work)

- No symbolic execution.
- No VM-based dynamic execution.
- No general-purpose CFG simplification beyond ~50 recognized patterns.
- Time budget hard cap: 60 s per file; if exceeded, fall back to raw
  AST and log the timeout.

### 16.11 Failure modes

- **Normalizer simplifies away a sink**: defensive check — never drop
  a known taxonomy-tagged call. Whitelist before transform.
- **Wrong unifications**: each transform is reversible from the log;
  add a regression test per pattern (~50 unit tests).

---

## §17. Graph Query DSL / Semantic Query Engine

### 17.1 Why it matters

The existing SQL queries against `nodes`, `edges`, `node_tags`, and
`dataflow_edges` are scattered across `callgraph_tools.py`,
`interprocedural_taint.py`, `gap_analyzer.py`, and the `bin/` extractor
scripts. Each is a fresh query that re-derives joins, re-checks
sanitizer state, re-applies framework gates. The result:

- Rule iteration is slow (every new pattern requires plumbing through
  3–4 files).
- Logic divergence between scripts (the chain extractor and the gap
  analyzer apply different sanitizer rules today).
- The MCP `js_examine_chain` rebuilds context per call instead of
  reusing.

A small, well-scoped DSL solves the maintainability problem without
turning into "we built our own CodeQL". Aim: 80% of useful queries
expressed in 10 lines.

### 17.2 Expected FP / FN reduction

- **Indirect** — query consistency reduces logic divergence which
  removes one source of "the chain extractor says A but the gap
  analyzer says B" inconsistencies. Estimated 5–10% reduction in
  divergence FPs.

### 17.3 Performance implications

- A query planner with caching can re-use intermediate joins across
  queries on the same chain. For target audits that fire 6+ queries
  per chain, this is a 3–5× speedup on the LLM-loop critical path.

### 17.4 Rollout strategy

1. Phase 17a — Python AST-based DSL (no parser) using a fluent
   builder. Ship core verbs.
2. Phase 17b — caching layer for join results.
3. Phase 17c — migrate `callgraph_tools.py`, `gap_analyzer.py`,
   `pp_chains.py` to the DSL.
4. Phase 17d — expose via MCP for ad-hoc queries during audit.

### 17.5 Query language proposal

Python-embedded fluent API (no parser, no separate language to learn):

```python
from js_analyzer.dsl import Q, taint, sanitizers, frameworks

# Find every chain from a postMessage source to an eval-class sink
# whose origin validation is loose.
chains = (
    Q.chains()
        .sources(taint.kind == 'postMessage',
                provenance.validation_kind == 'loose')
        .sinks(taint.category == 'js_exec')
        .where(sanitizers.on_path() == False)
        .async_aware()                      # follow event handlers
        .confidence_min(0.4)
        .frameworks_any(frameworks.react, frameworks.vue)
        .top(50)
        .resolve()
)

# Find prototype pollution writes that reach a router config gadget.
pp = (
    Q.chains()
        .sources(taint.kind == 'pp_write')
        .sinks(gadgets.in_catalog('router'))
        .max_hops(8)
        .resolve()
)
```

### 17.6 Traversal API architecture

Each verb is a tiny class:

```python
class SourcesPredicate(Predicate):
    def to_sql(self, ctx): ...
    def to_python(self, row): ...

class AsyncAware(Modifier):
    def expand_edges(self, edges): ...
```

A planner composes predicates into a SQL CTE chain plus a Python
post-filter. The planner picks SQL where indexable and Python where
not.

### 17.7 Semantic predicate system

Predicates are typed; the planner type-checks at build time:

- `taint.kind` ∈ enum of taxonomy categories.
- `provenance.validation_kind` ∈ {'strict','loose','none','library'}.
- `frameworks.X` are constants from `framework_detect.py`.
- `gadgets.in_catalog('router')` resolves to a set of qnames.

This catches typos at compose time, which today silently produce empty
results.

### 17.8 Query planner

Two-tier:

- Tier 1: SQL CTE chain for everything indexable (sink/source kind,
  framework, file, line, sanitizer flag).
- Tier 2: Python filter for the rest (async-aware traversal,
  confidence, gadget catalog lookup).

Compile each query into a `(SQL string, Python callable)` pair. Cache
the SQL plan by template (treat parameters as bind variables).

### 17.9 Caching strategy

- Per-query: cache the SQL result set keyed by (template_id,
  bind_args).
- Per-chain: cache the python post-filter result keyed by
  (chain_id, query_template_id).
- Invalidation: bump cache generation on every chain extractor run.

### 17.10 Practical implementation details

- Single file `tlx/modules/js_analyzer/dsl.py`. ~600 LOC for v1.
- No new dependency; just `sqlite3` and `dataclasses`.
- Add `bin/q.py` CLI: `python3 bin/q.py 'chains().sources(kind="dom_xss").sinks(category="js_exec").top(20)'`
  for shell-level exploration.

### 17.11 Failure modes

- **DSL expression range mismatch**: every new predicate goes through
  a code-review gate (DSL extensions live in one file).
- **Overuse**: the DSL is for rule iteration, not for replacing raw
  SQL in performance-critical loops. Document where each is preferred.

---

## §18. Differential Scan / Delta Analysis Mode

### 18.1 Why it matters

Three concrete use cases:

1. **Re-audit after a target's release**. Today we re-index from
   scratch; that takes 8–15 minutes on a 2 k-file target. ~80% is
   wasted on unchanged files.
2. **Variant scanning across sibling apps** of the same vendor (when
   they share a bundle / SDK). Delta tells us what *changed* between
   apps; high-signal for "regression in the other app".
3. **Patch diffing for a fix** — given vendor pushed v1.3.4 after a
   reported bug, find the controls they added and look for sibling
   gaps elsewhere (T3.1 work; this is its analyzer-side counterpart).

### 18.2 Expected FP / FN reduction

- **Indirect**: doesn't change FP/FN per chain. Changes which chains
  get re-scored, which lets you spend Opus budget on the actually-new
  surfaces.

### 18.3 Performance implications

- ~10× speedup on warm re-audit (only the changed files get re-AST'd
  and re-tainted; the rest are read from cache).
- Adds an O(files_changed × neighborhood) reachability re-derivation,
  bounded by `max_reach_radius = 3 callgraph hops` per changed file.

### 18.4 Rollout strategy

1. Phase 18a — file-level diff. We already have `file_hashes`; surface
   `changed_files` and re-AST/re-taint only those.
2. Phase 18b — semantic-graph diff. Compute the delta in `node_tags`,
   `dataflow_edges`, and `chains` keyed by (qname-stable, file-line
   approximate).
3. Phase 18c — reachable-from-delta pass: for each changed-tag node,
   walk the callgraph up to 3 hops to find which chains transitively
   change.
4. Phase 18d — patch-diff scaffold (T3.1 integration): vendor bundle
   v1.3.4 → v1.3.5 diff. Show analyst the added security controls.
5. Phase 18e — CI mode: emit only chains whose status changed (new
   TP, new FP, downgraded, upgraded). Designed for nightly cron + the
   `report-finding` skill.

### 18.5 Diff pipeline architecture

```
prior_run/        (the previous index snapshot, including db/)
current_run/      (the in-progress run)

diff = compute_diff(prior_run, current_run)
diff.changed_files       # set of files with new hash
diff.changed_nodes       # set of node-qnames added/removed/modified
diff.changed_tags        # set of (qname, tag_id) added/removed
diff.changed_edges       # set of edges added/removed
diff.reachable_chains    # set of chain_ids whose nodes intersect the above

incremental_rerank(diff.reachable_chains)
emit chains/delta.jsonl
```

### 18.6 Semantic graph diff algorithm

```
def diff_nodes(prior, current):
    for qname in current.qnames - prior.qnames:
        yield ('node_added', qname)
    for qname in prior.qnames - current.qnames:
        yield ('node_removed', qname)
    for qname in current.qnames & prior.qnames:
        if prior.tags[qname] != current.tags[qname]:
            yield ('node_retagged', qname,
                   added=current.tags[qname] - prior.tags[qname],
                   removed=prior.tags[qname] - current.tags[qname])
        if prior.edges_out[qname] != current.edges_out[qname]:
            yield ('node_rewired', qname, ...)
```

Use `(qname, file)` as the stable key (line numbers are noisy).

### 18.7 Incremental ranking strategy

- A chain is `delta_high` if any of its nodes is in `changed_nodes`
  AND its score moved by ≥ 0.1 in either direction.
- A chain is `delta_low` if any node is in `changed_nodes` but the
  score didn't move.
- A chain is `delta_clean` if no nodes are in `changed_nodes`.

Only `delta_high` flows into the Opus audit by default.

### 18.8 Recomputation boundaries

- Re-AST: only changed files.
- Re-taint (intra): only nodes in changed files plus their direct
  callers.
- Re-taint (inter): only chains whose `delta_high` set is non-empty.
- Re-chain-extract: only the affected entry points (BFS from each
  changed node, bounded radius).

### 18.9 CI optimization strategy

- A nightly cron job runs `js-index --delta` against the latest
  bundle. The delta JSONL is small (often < 100 chains). The Opus
  audit only runs on delta_high chains.
- The reporter ships a summary of: new vulns, removed vulns (fixed),
  status-changed vulns.

### 18.10 Practical implementation details

- Stable qnames: keep the existing webpack-aware qname canonicalizer.
- Persistence: each target dir gains a `prior/` subdir with the
  previous run's snapshot. Roll once per audit.
- Build artifact: `chains/delta.jsonl` + `chains/delta_summary.md`.

### 18.11 Failure modes

- **Refactor noise**: a rename-only commit produces a massive delta.
  Mitigate with a qname-stability hash (function-body MD5; if body is
  identical but name changed, treat as rename, not new node).
- **Cross-bundle ID drift**: webpack chunk IDs change with reorders.
  Use `module.path` (sourcemap-aware) as the stable ID.

---

## §19. Corpus-Guided Pattern Intelligence

### 19.1 Why it matters

Every confirmed finding is training data. The same exploit pattern
recurs across targets — sanitizer bypass via `<svg/onload>`, mutation-
XSS via `outerHTML += x`, polluted Next.js router defaults, postMessage
loose-validation. Today each new target re-learns these patterns through
LLM cost. A small, deterministic corpus of fingerprints lets the
analyzer pre-score chains that *look like* historical wins.

This is not ML; it's a graph-fingerprint similarity lookup against a
curated, hand-maintained corpus. The wiki already holds the technique
descriptions (`wiki/techniques/`); we surface their machine-readable
shape.

### 19.2 Expected FP / FN reduction

- **FN reduction: +5% to +15%** on repeat patterns. The biggest win
  is the chain extractor's ranking: pattern-matching chains float to
  the top of `hot.jsonl`.
- **FP reduction: -5%** — pattern matching has a strong prior; the
  classifier can confidently bury chains that don't match any known
  archetype.

### 19.3 Performance implications

- One pass per chain: compute a graph fingerprint, look up in corpus,
  add a similarity score. Negligible (~50 ms per chain).

### 19.4 Rollout strategy

1. Phase 19a — define the fingerprint schema (§19.6) and a starter
   corpus of ~30 archetypes drawn from the wiki.
2. Phase 19b — automatic fingerprinting on every newly-confirmed
   finding (post `report-finding`): the archetype gets appended to
   the corpus with provenance.
3. Phase 19c — pattern-aware ranking: chain score gets a `+0.1 ×
   similarity` bonus for matches above `0.7`.
4. Phase 19d — surface "matching archetype" to the LLM ChainIR
   so the audit prompt can cite the prior pattern.

### 19.5 Pattern corpus architecture

```
corpus/
  fingerprints/
    fp_postMessage_loose_eval.json
    fp_storage_xss_render_react.json
    fp_pp_router_csptraversal.json
    ...
  archetypes/
    arch_postMessage_loose_eval.md     # human readable from wiki
    ...
  index.json                           # catalog
```

Each fingerprint is a small JSON document.

### 19.6 Graph fingerprint schema

```jsonc
{
  "id": "fp_postMessage_loose_eval",
  "source_kinds": ["postMessage"],
  "sink_kinds": ["js_exec"],
  "required_path_features": [
    { "kind": "validation_kind", "value": "loose" },
    { "kind": "no_sanitizer_on_path" }
  ],
  "forbidden_features": [
    { "kind": "trusted_types_required" }
  ],
  "framework_any_of": ["react", "vue", "next"],
  "min_path_length": 1,
  "max_path_length": 6,
  "archetype_md": "../archetypes/arch_postMessage_loose_eval.md",
  "weight": 0.85,
  "provenance": [
    { "finding_id": "F-2025-0712", "target": "examplecorp", "verdict": "TP" },
    { "finding_id": "F-2025-1108", "target": "anothercorp", "verdict": "TP" }
  ]
}
```

### 19.7 Semantic chain similarity scoring

For a candidate chain and a fingerprint:

```
score =
    (source_kind in fingerprint.source_kinds)
    × (sink_kind in fingerprint.sink_kinds)
    × (1 - len(missing_required_features) / total_required)
    × (1 - len(present_forbidden_features))
    × framework_match
    × fingerprint.weight
```

The chain matches the fingerprint with score in [0, 1].

### 19.8 Historical exploit weighting

Provenance entries decay over time:

```
weight = base_weight × decay(now - finding_date)
       × (1 / log(provenance_count + 2))    # diminishing returns
```

Recent provenance dominates; very old fingerprints (>2 years) need
manual re-verification.

### 19.9 Ranking integration strategy

In the chain scorer, add a `pattern_bonus`:

```
score_final = score_base + 0.15 × max(similarity over all fingerprints)
```

The LLM-facing ChainIR includes the top-3 matching archetypes with
similarity ≥ 0.5 so the audit prompt has an explicit anchor.

### 19.10 Practical implementation details

- Build a `tlx/modules/js_analyzer/corpus.py` that loads fingerprints
  once and exposes `match(chain) -> [(fp_id, score), ...]`.
- `bin/corpus_update.py` to add a fingerprint from a confirmed
  finding (semi-automatic; analyst reviews before commit).
- Persist: in-repo JSON files; checked-in; deterministic.

### 19.11 Anti-patterns avoided

- **No black-box embedding**: similarity is computed from explicit
  features the analyst can audit, not from neural representations.
- **No statistical training pipeline**: fingerprints are curated and
  committed.
- **No silent decay**: archetypes that age out emit a wiki-lint
  warning, not an auto-deletion.

### 19.12 Failure modes

- **Corpus drift**: an archetype that "always TPed in 2024" stops
  matching real bugs in 2026 (framework versions move). Mitigated by
  the decay function and by manual review on every wiki-ingest.
- **Cherry-picking**: an analyst who tunes fingerprints to their
  pet bugs will over-fit. Mitigated by requiring ≥2 provenance
  entries before a fingerprint counts for ranking.

---

## §20. Exploit Chain Compression + Canonicalization

### 20.1 Why it matters

The audit pipeline already hits the limit where ChainIR for a deeply-
intermediated chain is too big for the LLM to reason about, even with
Sonnet's 200k context. The current symptoms:

- LLM verdict drift: the same chain gets different verdicts on different
  Sonnet runs because the prompt cycles through 1k+ tokens of
  middleware that doesn't affect exploitability.
- Analyst opacity: a 20-hop chain takes 5 minutes to read.
- Wasted budget: every Opus consult is paid by token count.

A pre-LLM canonicalization pass reduces a chain's hop count by 50–70%
and preserves all decisions that matter. This is a one-time engineering
investment that compounds across every Opus call.

### 20.2 Expected FP / FN reduction

- **FP reduction: -10%** (less middleware noise → less LLM
  hallucination).
- **FN reduction: -3%** (we lose a tiny amount of information by
  compressing).
- **Cost reduction**: 40–60% fewer tokens per LLM verdict.

### 20.3 Performance implications

- Compression itself runs in < 200 ms per chain.
- Downstream LLM costs drop proportionally to compressed hop count.

### 20.4 Rollout strategy

1. Phase 20a — equivalent-edge collapsing (merge consecutive hops
   where the middle node adds no taint transformation).
2. Phase 20b — repeated-propagation deduplication (collapse loops
   that propagate the same taint shape).
3. Phase 20c — framework-aware summarization (e.g. "passed through
   Redux dispatch + reducer + selector" → "Redux state flow").
4. Phase 20d — async-aware summarization (collapse the boilerplate of
   `addEventListener` indirection into a single annotated hop).
5. Phase 20e — sanitizer-aware compression (preserve every sanitizer
   on the path; never compress one out).

### 20.5 Canonical IR design

```jsonc
{
  "chain_id": "...",
  "narrative": [
    { "hop": 1, "kind": "source", "qname": "...", "evidence": [...] },
    { "hop": 2, "kind": "framework_passthrough", "framework": "redux",
      "summary": "dispatch → reducer → selector",
      "collapsed_qnames": ["dispatch", "reducer.x", "selector.x"] },
    { "hop": 3, "kind": "sanitizer_attempt", "qname": "escapeHTML",
      "verdict": "bypassable_in_attr_context" },
    { "hop": 4, "kind": "sink", "qname": "...", "context": "html_attr_quoted" }
  ],
  "compression_ratio": 0.7,
  "original_hop_count": 23,
  "compressed_hop_count": 7,
  "decisions_preserved": ["sanitizer_verdict", "parser_context",
                          "origin_validation"]
}
```

### 20.6 Graph compression algorithm

```
def compress(chain):
    nodes = chain.path
    out = [nodes[0]]                # source
    for i in range(1, len(nodes) - 1):
        n = nodes[i]
        if n.has_sanitizer or n.is_parser_context_boundary
           or n.is_origin_boundary or n.is_storage_boundary:
            out.append(n)
            continue
        if framework_passthrough(out[-1], n, nodes[i+1]):
            out[-1] = merge(out[-1], n)
            continue
        if equivalent_edge(out[-1], n):
            continue
        out.append(n)
    out.append(nodes[-1])           # sink
    return Chain(path=out, ...)
```

### 20.7 Summarization heuristics

Per-framework summarizers (small JSON):

```json
{
  "redux": {
    "patterns": [
      { "match": ["dispatch", "reducer", "selector"],
        "summary": "Redux state flow" },
      { "match": ["dispatch", "thunk_middleware", "fetch"],
        "summary": "Redux thunk → network call" }
    ]
  },
  "react": {
    "patterns": [
      { "match": ["useState_set", "useEffect", "ref"],
        "summary": "React state → effect → DOM ref" }
    ]
  }
}
```

### 20.8 LLM-ready chain format

Each compressed chain compiles into a Markdown narrative used as the
"chain" section of the audit prompt:

```
1. SOURCE: postMessage handler at app/auth/router.ts:42 with loose origin validation.
2. Redux state flow.
3. SANITIZER: escapeHTML applied — but parser context is html_attr_quoted, leaving '=' free.
4. SINK: innerHTML at app/render/dialog.tsx:113.
```

### 20.9 Complexity reduction metrics

Log per-chain:

- `original_token_count`
- `compressed_token_count`
- `decisions_preserved_count`
- `lost_evidence_count` (where the compressor dropped supporting
  evidence — should normally be 0; flag when nonzero).

Goal target: average compression_ratio ≥ 0.5 on hot.jsonl chains;
zero lost critical evidence.

### 20.10 Practical implementation details

- `tlx/modules/js_analyzer/chain_compress.py`. Reads chain rows;
  writes canonical chains JSONL alongside.
- Plug into `audit_pipeline.py` immediately before the Sonnet
  triage call.

### 20.11 Failure modes

- **Over-compression**: an aggressive summarizer collapses a critical
  hop. Mitigation: preserve any node whose tag set includes a
  sanitizer, parser-context transition, origin boundary, or storage
  edge.
- **Wrong framework match**: only apply summarizers if the framework
  is detected (V1 § framework gating).

---

## §21. Multi-Target Correlation Engine

### 21.1 Why it matters

A senior hunter's biggest leverage is variant discovery: when you
confirm a bug on one of a vendor's apps, you want to find the same
bug class on the vendor's other apps before the vendor patches. The
same logic applies to:

- Shared bundle reuse (e.g. multi-tenant SaaS with a per-tenant
  subdomain but the same React app).
- Vendor SDKs embedded in many customer sites (Auth0 widget, Optimizely
  snippet, Marketo forms).
- Single-page-app micro-frontends across multiple sub-products.

Today each target is isolated (per-target DB, per-target chains). We
need an **opt-in** cross-target correlation that respects scope.

### 21.2 Expected FP / FN reduction

- **FN reduction: +5% to +15%** when the corpus of targets has reused
  bundles. (For single-target work, zero.)

### 21.3 Performance implications

- Build phase: one fingerprint per bundle, persisted in a global
  index. ~1 minute per new bundle.
- Query phase: < 1 s per lookup.

### 21.4 Rollout strategy

1. Phase 21a — bundle fingerprint (file-level hash + a chunk-content
   shingle). Used to detect when target A and target B share large
   amounts of bundled code.
2. Phase 21b — a "shared SDK" detector — when ≥30% of a target's
   AST nodes are present in another target's, mark as shared.
3. Phase 21c — sanitizer-reuse detection: when target A has confirmed
   a sanitizer bypass and the same sanitizer (by version + config
   fingerprint) is present on target B, flag.
4. Phase 21d — gadget reuse — when a prototype-pollution gadget was
   confirmed in framework version vX.Y and target B uses the same
   range, flag.

### 21.5 Cross-target indexing architecture

```
~/.tlx/corr/
  bundles/
    sha256:<...>.json    # bundle fingerprint, list of qnames
  targets/
    <name>.json          # links target name to bundle fingerprints used
  findings/
    F-<id>.json          # confirmed finding + fingerprint of its sink and sanitizer
  index.sqlite           # secondary index for cross-target queries
```

### 21.6 Semantic fingerprint schema

```jsonc
{
  "bundle_id": "sha256:<...>",
  "size_bytes": 1234567,
  "shingles": ["abcd...", "efgh..."],   // 64-bit content shingles
  "qname_top_100": ["render", "dispatch", "fetch", ...],
  "framework_set": ["react", "next"],
  "framework_versions": { "react": "18.2.0", "next": "13.3.0" },
  "sanitizer_set": [
    { "name": "dompurify", "version": "3.0.5", "config_hash": "..." }
  ]
}
```

### 21.7 Shared-vulnerability detection logic

```
on every new finding:
    for other_target in targets_using_same_bundle(finding.bundle_id):
        if other_target.scope_permits(finding) and
           finding.sink_qname in other_target.nodes:
            emit lead { target: other_target, finding: finding,
                        likelihood: 0.8 }
```

### 21.8 Clustering strategy

- Cluster bundles by shingle similarity (Jaccard ≥ 0.5).
- Cluster sanitizer configs by (name, version_range, config_hash).
- Cluster by detected framework version cohort.

### 21.9 Privacy / scope boundaries

- **Default off**. Correlation requires explicit opt-in per target.
- **Scope respect**: a lead must respect the target's `http.md`.
  Never auto-send a request based on a correlation.
- **Bounty platform rules**: H1 disclosure rules forbid mentioning
  one target on another's report. Keep the corpus local; never
  upload.

### 21.10 Practical implementation details

- `bin/corr.py` — CLI for build, query, list.
- Persisted under `~/.tlx/corr/`; backed by SQLite for join queries.
- MCP integration optional; can ship as analyst-only CLI for safety.

### 21.11 Failure modes

- **Privacy leak**: a confirmed finding's payload becomes part of
  the corpus. Mitigation: store only hashes of sinks and sanitizers,
  not the payload itself.
- **Bundle reuse false-positive**: vendor's "shared bundle" turns out
  to be jQuery + lodash. Use whitelist of common libs to deflate
  matches that are entirely common-library content.

---

## §22. Sink Reachability Validation

### 22.1 Why it matters

A taint chain that reaches an `eval` whose feature flag is `false` in
production is not a bug. Today the analyzer considers any reachable
sink in the AST as live. Production reality:

- ~25% of detected sinks are gated by feature flags (LaunchDarkly,
  Split.io, internal flag systems) that are off in prod.
- ~15% are gated by route guards that the attacker can't reach
  (admin-only routes from an unauthenticated context).
- ~10% are dead-code that the bundler kept but no entry point loads.
- Lifecycle: a sink that fires only on `componentWillUnmount` of an
  admin component is functionally unreachable for an attacker browsing
  as a normal user.

Cumulatively, reachability validation cuts the FP rate by **15–25%**
on enterprise SaaS targets.

### 22.2 Expected FP / FN reduction

- **FP reduction: -15% to -25%** on enterprise SaaS targets.
- **FN reduction: +2%** (we'll correctly downgrade some "live" sinks
  that aren't; we'll also discover some lifecycle-gated sinks that
  ARE reachable from a non-obvious entry point).

### 22.3 Performance implications

- One reachability pass after chain extraction: BFS from each route
  to validate the sink is on the page's execution path.
- Adds ~5 s per target on 2 k-file targets. Optional cache.

### 22.4 Rollout strategy

1. Phase 22a — route map extraction (React Router, Next.js pages,
   Vue Router, Angular Router).
2. Phase 22b — sink-to-route reachability (which routes can reach
   this sink in their bundle?).
3. Phase 22c — lifecycle-aware activation modeling.
4. Phase 22d — feature-flag awareness (read flag names; mark sinks
   gated by a flag; require analyst input on default-off vs default-on).
5. Phase 22e — dead-code detection (sinks unreachable from any
   route entry).

### 22.5 Reachability engine architecture

```
build route_map: { route_path → entry_module_qname }
for each chain c:
    routes_reaching_c = find_routes_with_path_to(c.sink.node)
    if not routes_reaching_c:
        c.reachability = 'dead'
    else:
        c.reachability = classify(routes_reaching_c, auth_state)
```

### 22.6 Lifecycle graph design

Each component has a lifecycle: mount, update, unmount, error,
revalidate (Next), beforeMount/created (Vue), etc. Tag each sink
with its lifecycle:

```sql
CREATE TABLE sink_lifecycle (
  node_id INTEGER PRIMARY KEY REFERENCES nodes(id),
  framework TEXT NOT NULL,
  lifecycle_phase TEXT NOT NULL,    -- 'mount' | 'update' | 'unmount' | 'error' | 'revalidate' | 'sw_install' | ...
  attacker_can_trigger INTEGER DEFAULT 1
);
```

A sink in `unmount` is hard for an attacker to trigger unless they
control navigation. Drop severity.

### 22.7 Activation-state modeling

For each chain, compute `activation_likelihood ∈ [0, 1]`:

```
likelihood =
   1.0   if sink in route-default render path (always runs)
   0.6   if sink behind a button click in the same route
   0.4   if sink behind a feature flag with default-on
   0.05  if sink behind a feature flag with default-off
   0.0   if sink in unreachable route or dead code
```

Multiply chain severity by `activation_likelihood`.

### 22.8 Dead-path pruning heuristics

- A node with `in_degree = 0` from any route entry is dead.
- Bundle-keep but no-import nodes: webpack `__webpack_modules__[N]`
  with no `__webpack_require__(N)` callsite. Dead.
- Side-effect-only imports that don't reach a sink. Not dead, but
  low-likelihood.

### 22.9 Feature-flag-aware pruning

Look for known flag patterns:

```
const FLAG_NEW_EDITOR = useFeatureFlag('new-editor');
if (FLAG_NEW_EDITOR) { ... sink ... }
```

Patterns:

- `useFeatureFlag('<name>')`, `splitClient.getTreatment('<name>')`,
  `LDClient.variation('<name>')`, `growthbook.feature('<name>')`.
- Local env reads: `process.env.NEXT_PUBLIC_FEATURE_X`,
  `window.__FEATURE_X__`.

When detected, query the wiki / analyst note for default state; if
unknown, assume `0.4` likelihood.

### 22.10 Practical implementation details

- `tlx/modules/js_analyzer/reachability.py`: route map + BFS.
- Route extraction has framework-specific logic; share with V1 §6
  framework adapters.
- ChainIR carries `activation_likelihood` and `feature_flags_gating`.

### 22.11 Failure modes

- **Route map missing**: some targets bundle their router in a way
  that defies static extraction. Fall back to "all routes" with
  `route_resolution: 'unknown'`. Conservative.
- **Hot-loaded chunks**: Next.js dynamic imports may load a sink only
  on user action. Mark `activation_kind: 'lazy'` and apply a moderate
  decay (0.6), not a full prune.

---

## §23. Client-Side Authorization / State Abuse Expansion

### 23.1 Why it matters

The analyzer is dominated by DOM-XSS-shaped chains today. Modern SPA
bug-bounty bounty payouts come increasingly from:

- **Client-side IDOR**: the API returns more data than the UI shows.
  A small SPA tweak (intercept the network response and dump the
  unrendered fields) exposes other users' data.
- **Route-guard bypass**: client-only auth checks (`if (!user.isAdmin)
  redirect('/')`) — bypassable by patching the JS or stalling the
  router.
- **Permission-state poisoning**: an attacker influences a permission
  object that the client trusts (Redux state, polluted cookie).
- **Token misuse**: client embeds an OAuth code, refresh token, or
  long-lived access token in URL/localStorage where a phishing or
  XSS payload can steal it.
- **Client-side path traversal (CSPT)**: V1 §15 covered the parser
  context for the eventual sink; here we cover the broader pattern
  including CSPT-2-CSRF.
- **State desync**: the client believes it's authenticated while the
  server says otherwise, leading to a privilege escalation when the
  client makes an API call that bypasses its own UI gating.

### 23.2 Expected FP / FN reduction

- **FN reduction: +20% to +35%** on enterprise SaaS targets.
  This is the single biggest **new attack class** unlock in this
  whole plan.
- **FP increase: +5%** as we surface lower-severity findings; offset
  by severity-aware scoring.

### 23.3 Performance implications

- Additional AST passes for auth-state, router, and token tracking.
  ~3 s per target.
- Adds ~3 new chain categories to the chain extractor; runtime impact
  bounded by per-category caps.

### 23.4 Rollout strategy

1. Phase 23a — auth-state extraction (`useUser`, `useSession`,
   Redux `auth` slice, `useAuth0`, NextAuth `useSession`, etc.).
2. Phase 23b — router-guard analysis (route → guard predicate
   mapping).
3. Phase 23c — token provenance (where do JWTs / access tokens come
   from; where do they get stored; where do they get read).
4. Phase 23d — IDOR-style API-response over-fetch detector.
5. Phase 23e — state desync detector (heuristic: a sink that reads
   `user.isAdmin` from a Redux store with no server validation
   adjacent).

### 23.5 Auth semantic IR

```sql
CREATE TABLE auth_state_nodes (
  node_id INTEGER PRIMARY KEY REFERENCES nodes(id),
  role TEXT NOT NULL,        -- 'identity' | 'permission' | 'token' | 'role-claim'
  source TEXT NOT NULL,      -- 'idp' | 'cookie' | 'storage' | 'state' | 'props' | 'fetch-body'
  framework TEXT,            -- 'react-auth0', 'nextauth', 'custom'
  trust REAL NOT NULL,       -- 0..1; lower means client-only / spoofable
  derives_from INTEGER,      -- foreign key to upstream auth node
  consumer_node INTEGER      -- where the auth state is consumed
);
```

### 23.6 Route-guard analysis architecture

```
build route_guards: { route_path → guard_qname }
for each guard:
    classify(guard) ∈ {'client-only', 'server-validated', 'mixed'}
    if 'client-only':
        emit (route_path, guard_qname, severity=high_if_admin)
```

`'client-only'` is the bug. Indicators: guard reads from Redux only;
guard never awaits a server fetch.

### 23.7 Token provenance tracking

Tag each token-bearing variable with:

- **birthplace**: `useAuth0`, `fetch('/login').body.token`, `cookies.get('jwt')`.
- **lifetime**: ephemeral / persistent / cross-origin.
- **storage**: never-stored / localStorage / sessionStorage / cookie /
  in-memory.
- **leak surface**: any sink that exposes the value (URL writes,
  postMessage, console.log, error reporting).

Cross-reference V1 §11 (the existing token-leak detector) with V2
§23 to unify.

### 23.8 State-trust classification

```
for each chain ending in a permission-conditional render:
    upstream_trust = compute_trust(chain.source_node)
    if upstream_trust < 0.5:
        chain.kind = 'client_state_abuse'
        chain.severity_modifier = 'high'
```

### 23.9 CSPT and CSPT-2-CSRF integration

The existing `cspt-csrf` skill targets path-traversal in fetch URLs.
Hook it into the chain extractor: any chain whose sink is a fetch/
XHR/axios URL gets a `cspt_potential` flag and is routed to the CSPT
sub-pipeline for path-traversal-specific scoring.

### 23.10 Practical implementation details

- `tlx/modules/js_analyzer/auth_state.py`: tags + chain attribute.
- `tlx/modules/js_analyzer/route_guards.py`: framework-aware guard
  detection.
- Reuse existing token-related tags in `taxonomies/`.

### 23.11 Failure modes

- **Server-validation invisible**: client-only static analysis can't
  see the server's checks. We must default to "assume server is
  trustworthy" and only mark a chain `client_state_abuse` when the
  client clearly bypasses something it should validate (i.e., admin
  routes guarded with no `await`).
- **False positives in dev mode**: route guards in dev often log to
  console; in prod they call the API. Detect `process.env.NODE_ENV
  === 'production'` branches.

---

## §24. Worker / Service Worker Semantic Modeling

### 24.1 Why it matters

Web Workers, Shared Workers, Service Workers, and now AudioWorklets
are first-class JS execution contexts that the analyzer completely
ignores today. The bug-bounty-relevant attacks:

- **Service Worker scope hijack**: a malicious SW registered with
  scope `/` intercepts every fetch, including the IdP redirect.
- **Cache poisoning**: SW caches an attacker-controlled response and
  serves it to every subsequent navigation.
- **Cross-origin message bridging**: a SW relays postMessage between
  contexts the page wouldn't normally connect.
- **PWA install pre-cache**: install handler precaches resources the
  attacker can influence (URL injection).
- **Shared Workers**: cross-tab state sharing without origin checks.

Each is rare in raw count but high-severity when present.

### 24.2 Expected FP / FN reduction

- **FN reduction: +3% to +8%** on PWA targets, +0 on non-PWA targets.
- **FP increase: 0**. New class; doesn't change existing.

### 24.3 Performance implications

- One additional AST pass to detect worker boundaries. < 500 ms.
- Worker source files (`*.worker.js`, the file referenced by
  `new Worker(URL)`) get their own callgraph chunk; integrated as a
  separate entry-point.

### 24.4 Rollout strategy

1. Phase 24a — detect worker entry points and pair with their host.
2. Phase 24b — model the message channel (worker.postMessage ↔
   self.onmessage in worker).
3. Phase 24c — Service Worker fetch interception modeling.
4. Phase 24d — Service Worker cache (Cache API integration with §11).
5. Phase 24e — Origin bridging: alert when a SW could relay
   cross-origin messages.

### 24.5 Worker semantic architecture

```
worker_pairs:
  host_file ↔ worker_file (via new Worker('w.js') or registerServiceWorker)

worker_context:
  trust = 'same-origin-isolated' | 'same-origin-shared' | 'cross-tab'
  capabilities = ['fetch', 'cache', 'message', 'sync', 'push']
```

### 24.6 Worker ↔ main-thread edge modeling

In the graph:

- Each `worker.postMessage` site is connected to every
  `self.onmessage` handler in the worker's file via a `worker_message`
  edge.
- Each `self.postMessage` in the worker connects back to the host's
  `worker.onmessage` handler.
- For Service Workers: `clients.matchAll().then(c => c.postMessage)` is
  a one-to-many edge with `cross_client = true`.

### 24.7 Service Worker cache taint design

Treat the SW Cache API as a §11 storage event with `api = 'sw.cache'`
and `phase = 'sw_fetch'`. Specifically:

- `cache.put(request, response)`: storage-write with key =
  `request.url`, value = `response.body`.
- `cache.match(request)`: storage-read for the same key.
- `event.respondWith(cache.match(...))` in a `fetch` handler:
  attacker-influenceable iff the URL is shaped by client input.

### 24.8 Message provenance tracking

Each message edge carries:

- `from_origin`: same | unknown.
- `to_origin`: same | unknown.
- `validation_kind`: leverages §12 origin trust graph.

### 24.9 SW scope and registrations

Scope analysis:

- A SW registered at scope `/` intercepts everything. High blast radius.
- A SW registered at `/widget/` is narrow. Lower blast radius.
- A registration controlled by a server header (`Service-Worker-Allowed`)
  can be wider than its file path; warn if observed.

### 24.10 Practical implementation details

- `tlx/modules/js_analyzer/workers.py`: extract worker pairs from the
  AST, build the cross-file edges.
- Worker files become their own callgraph entry points (run
  intra/inter taint independently then connect via worker_message
  edges).
- Reuse §11 storage IR for SW cache.

### 24.11 Failure modes

- **Workers loaded by URL string**: `new Worker(url)` where url is
  dynamic. Fall back to "unknown worker"; mark the host edge as
  `worker_resolution: 'dynamic'`.
- **Lazy registrations**: `register()` called only after user
  interaction. Tag with §22 activation likelihood.

---

# Final synthesis — sections §25 through §38

## §25. Executive synthesis

The 14 subsystems in §11–§24, layered onto V1 §1–§10, transform the
analyzer along three independent axes:

1. **Semantic depth** — sections §11, §12, §13, §14, §15, §22, §23,
   §24. The graph now understands persistent state, cross-origin trust,
   DOM clobbering, prototype-pollution gadgets, parser context,
   reachability, auth-state, and worker boundaries. Each axis closes
   a specific class of bug-bounty exploit that today either FPs or
   FNs.
2. **Engineering tractability** — sections §16, §17, §18, §20. The
   graph survives obfuscated bundles, has a maintainable query
   surface, supports delta scans, and produces LLM-digestible chain
   narratives. Together these unlock workflow speed without changing
   semantics.
3. **Knowledge amortization** — sections §19, §21. The analyzer
   remembers what worked before and detects variants across an
   engagement portfolio without violating scope. These compound
   over time; cost is mostly upfront.

The biggest single signal-quality win is **§15 (parser context) +
§22 (reachability)** — together they cut FP rate on `hot.jsonl` by
an estimated 40–55%. The biggest single new attack-class unlock is
**§23 (client-side auth & state abuse)** — it opens an entire class
of high-severity SPA bugs the analyzer currently doesn't pursue at
all. The biggest scalability lever is **§18 (delta scans) + §20
(chain compression)** — both compound across every audit.

If you build only one section, build §15 (parser-context). If you
build two, add §22 (reachability). If you build three, add §20
(chain compression for LLMs).

---

## §26. Critical architectural weaknesses (current + V1 + V2 combined)

| Rank | Weakness | Severity | Section that addresses it | Notes |
|------|----------|----------|----------------------------|-------|
| 1 | No parser context awareness — every HTML sink scored equally | Critical | §15 | Single biggest FP source |
| 2 | No cross-page persistence model — storage events orphaned | High | §11 | Stored XSS class fully missed |
| 3 | postMessage origin validation invisible | High | §12 | Critical-severity bugs misranked |
| 4 | No reachability validation — dead-code sinks reported | High | §22 | 15–25% FP on enterprise SaaS |
| 5 | Chains too verbose for LLMs — verdict drift, cost | High | §20 | Hits cost ceiling on every audit |
| 6 | Obfuscated bundles produce broken graphs | High | §16 | Affects most production targets |
| 7 | Prototype-pollution chains lack gadget linkage | Medium | §14 | Pollution writes are not exploitable on their own |
| 8 | Client-side auth + state abuse uncovered | Medium-High | §23 | Whole bug class missing |
| 9 | DOM clobbering ignored | Medium | §13 | Niche but real |
| 10 | Worker/SW semantics absent | Medium | §24 | High blast radius when present |
| 11 | No delta-aware scans — every re-audit is cold | Medium | §18 | Workflow speed |
| 12 | Query plumbing scattered across files | Medium | §17 | Maintainability tax compounds |
| 13 | No cross-target correlation | Low-Medium | §21 | High value, opt-in |
| 14 | No pattern corpus | Low-Medium | §19 | Compounding ranking quality |

---

## §27. Highest ROI improvements (ranked)

| Rank | Subsystem | Effort | Net signal-quality | Why |
|------|-----------|--------|--------------------|-----|
| 1 | §15 Parser context | 2 wk | Massive FP reduction | Deterministic, additive, no new graph traversal |
| 2 | §22 Sink reachability | 2 wk | Large FP reduction | Reuses route extraction already needed in V1 §6 |
| 3 | §20 Chain compression | 1 wk | Cost + quality | Pays for itself in LLM budget within one engagement |
| 4 | §11 Persistent storage taint | 3 wk | Large FN reduction | Unblocks stored-XSS class |
| 5 | §12 Origin trust | 2 wk | Severity calibration | postMessage chains now rank correctly |
| 6 | §16 Obfuscation normalize | 4 wk | Foundational; many downstream gains | Needed before §15 perfectly works on Terser bundles |
| 7 | §23 Client auth abuse | 4 wk | New attack class | Highest *bounty* upside |
| 8 | §14 PP gadget linkage | 2 wk | Cleans up an existing noisy class | Quick win once §14.6 IR lands |
| 9 | §18 Delta scans | 2 wk | Workflow speed | Pays for itself on every re-audit |
| 10 | §19 Corpus patterns | 1 wk + ongoing | Ranking compound interest | Lowest effort once schema is in |
| 11 | §17 Query DSL | 3 wk | Maintainability | Pays back over months, not weeks |
| 12 | §13 DOM clobbering | 1 wk | Specialized | Useful on small set of targets |
| 13 | §24 Worker/SW | 2 wk | Specialized | High-severity but narrow target set |
| 14 | §21 Multi-target correlation | 3 wk | Variant discovery | Compounds with engagement portfolio |

---

## §28. Biggest scalability risks

1. **§11 storage edges blowing up the BFS**. Mitigated by per-chain
   storage-hop cap = 1 and key-static-match requirement. Watch
   `chains/all.jsonl` size before/after; if > 5× pre-existing,
   tighten the matcher.
2. **§14 gadget catalog growth**. Each new framework version adds
   patterns; left unchecked, the catalog overwhelms the AST pass.
   Cap at 500 gadgets total; require curation review.
3. **§17 DSL becoming an alternative IR**. The risk is folks
   reinventing CodeQL. Hard scope: DSL only over the existing tables,
   no new graph representations.
4. **§21 corpus growing unbounded**. Bound: max 1000 fingerprints,
   periodic prune via wiki-lint.
5. **§16 normalization producing wrong unifications**. Each transform
   needs a regression test; CI fails if entropy increases.
6. **Per-target DB diverging from global**. Already an issue; V2
   adds 6 new tables. `bin/migrate_db.py` MUST be the only place
   migrations exist.

---

## §29. Biggest FP sources (post-V1, pre-V2)

| FP class | Approx share of audited FPs | Section that fixes it |
|----------|-----------------------------|------------------------|
| Sink in wrong parser context | 35% | §15 |
| Sink behind dead-code / unreached route | 15% | §22 |
| Sink behind feature flag (default off) | 8% | §22 |
| Sanitizer mis-modeled as full clear | 10% | V1 §5 + §15 encoding state |
| postMessage with strict origin check unmodeled | 7% | §12 |
| PP write with no gadget reachable | 6% | §14 |
| Storage write that no reader actually consumes | 5% | §11 storage_edges with key static match |
| Worker context misread as main thread | 3% | §24 |
| Obfuscation-induced wrong qname | 11% | §16 |

(Numbers above are rough estimates from the most recent calibration
audit; tighten by re-calibrating after each subsystem ships.)

---

## §30. Biggest FN sources (post-V1, pre-V2)

| FN class | Approx share of missed TPs | Section that fixes it |
|----------|----------------------------|------------------------|
| Stored DOM XSS across pages | 22% | §11 |
| Client-side auth / state abuse | 28% | §23 |
| postMessage with no validation | 12% | §12 |
| PP with gadget in known catalog | 8% | §14 |
| Obfuscated bundle hiding sink | 15% | §16 |
| Worker / SW relay or cache poisoning | 4% | §24 |
| DOM clobbering | 3% | §13 |
| Other (long-tail async, framework hydration edges) | 8% | V1 §3 + §6 |

---

## §31. Staged implementation roadmap

This is a 6-month plan compatible with V1's already-staged work.

### Quarter 1 (12 weeks)

- **Weeks 1–2**: Ship §15 (parser context). Single biggest FP win.
  Run a full calibration audit before/after to confirm.
- **Weeks 3–4**: Ship §22 (sink reachability). Pairs with V1 §6
  framework adapter work; share route-map extraction.
- **Weeks 5–6**: Ship §20 (chain compression). Validate LLM token
  budget improvement.
- **Weeks 7–9**: Ship §11 (persistent storage taint). Run a small
  experiment on a known stored-XSS target.
- **Weeks 10–12**: Ship §12 (origin trust). Re-rank existing
  postMessage chains; calibrate severity.

End of Q1: FP rate on hot.jsonl drops from ~0.65 to ~0.30 estimate.
Recall improves +15–25% on stored-XSS class.

### Quarter 2 (12 weeks)

- **Weeks 13–16**: Ship §16 (obfuscation normalize). High effort, but
  unlocks consistent §15/§22 on Terser bundles.
- **Weeks 17–20**: Ship §23 (client-side auth abuse). Biggest new
  attack-class unlock.
- **Weeks 21–22**: Ship §14 (PP gadgets).
- **Weeks 23–24**: Ship §18 (delta scans).

End of Q2: average target re-audit time drops from 12 min to 3 min.
New auth-abuse class is in routine reports.

### Quarter 3 (residual)

- §17 (DSL), §19 (corpus), §13 (clobbering), §24 (workers), §21
  (correlation), in roughly that order. None are blocking each other;
  ship as time allows.

---

## §32. Migration strategy

- **Feature flags**: every V2 subsystem behind a flag in
  `js_analyzer_config.JSAnalyzerConfig`. Default off.
- **Schema migrations**: every `ALTER TABLE` and new table in
  `bin/migrate_db.py`. Run lazily on per-target DB access.
- **Chain JSONL versioning**: bump `chain_format_version` to "2.0"
  when V2 fields appear. Old skills read v1.0 unchanged; new fields
  are additive.
- **LLM prompt compat**: ChainIR v2 includes all V1 fields plus new
  ones. `audit_pipeline.py` accepts both.
- **Skill rollout**: V2 surface skills (e.g. a new `cspt-csrf-v2`)
  ship as new skills, not replacements, until the corresponding
  subsystem is GA.
- **Calibration corpus**: maintain a curated test corpus of 50 known
  TPs and 50 known FPs from prior engagements; gate any subsystem
  shipping on the corpus precision/recall not regressing.

---

## §33. Performance budgeting guidance

| Stage | Cold (target=2k modules) | Warm |
|-------|--------------------------|------|
| §11 storage extraction | +0.5 s | 0 |
| §12 origin trust | +0.3 s | 0 |
| §13 clobbering | +0.5 s | 0 |
| §14 PP gadget | +0.8 s | 0 |
| §15 parser context | +0.2 s | 0 |
| §16 normalize (one-time, cached) | +30–60 s | 0 |
| §17 DSL | 0 (saves time downstream) | 0 |
| §18 delta | -90% wall time (warm) | n/a |
| §19 corpus | +50 ms / chain | +50 ms / chain |
| §20 compression | +200 ms / chain | +200 ms / chain |
| §21 correlation | +1 s (lookup) | +1 s |
| §22 reachability | +5 s | 0 (cached) |
| §23 auth IR | +3 s | 0 |
| §24 workers | +0.5 s | 0 |
| **Total (cold)** | ~45–80 s | n/a |
| **Total (warm w/ delta)** | <30 s | n/a |

Budget target: cold full re-audit ≤ 2 minutes; warm delta ≤ 30 s.

---

## §34. Recommended rollout order

Repeated from §31 with one-line rationale:

1. **§15 parser context** — biggest FP reduction; deterministic.
2. **§22 sink reachability** — second biggest FP reduction; pairs
   with V1 §6.
3. **§20 chain compression** — cuts LLM cost immediately; required
   before §16 work makes the LLM context worse.
4. **§11 persistent storage taint** — first FN-class unlock.
5. **§12 origin trust** — severity calibration; high-impact bugs.
6. **§16 obfuscation normalize** — foundation for §15 effectiveness
   on real bundles.
7. **§23 client auth abuse** — new attack class.
8. **§14 PP gadgets** — closes existing noisy class.
9. **§18 delta scans** — workflow speed.
10. **§17 DSL** — maintainability dividend.
11. **§19 corpus patterns** — knowledge amortization.
12. **§13 DOM clobbering** — niche but real.
13. **§24 workers / SW** — high-severity but narrow scope.
14. **§21 multi-target correlation** — opt-in; opt-in.

---

## §35. Suggested schemas / interfaces (consolidated)

The new SQL tables introduced across §11–§24:

```sql
-- §11
CREATE TABLE storage_events (...);
CREATE INDEX idx_storage_key ON storage_events(key_static, op);

-- §12
CREATE TABLE node_provenance (...);

-- §13
CREATE TABLE global_reads (...);
CREATE TABLE clobber_candidates (...);

-- §14
CREATE TABLE implicit_lookups (...);
CREATE TABLE pp_gadgets (...);

-- §15
CREATE TABLE sink_contexts (...);

-- §22
CREATE TABLE sink_lifecycle (...);

-- §23
CREATE TABLE auth_state_nodes (...);

-- §24 (reuses §11 storage_events with api='sw.cache')
```

Total: 8 new tables, all additive, indexed. Each is owned by exactly
one subsystem.

Chain JSONL v2 fields (additive):

```jsonc
{
  "chain_id": "...",
  "format_version": "2.0",
  "persistence": { ... },                  // §11
  "trust_score": 0.5,                      // §12
  "clobber_gadget": { ... },               // §13
  "pp_gadget": { ... },                    // §14
  "sink_context": "html_body",             // §15
  "encoding_state": "raw",                 // §15
  "execution_viable": "js",                // §15
  "obfuscation_normalized_qnames": [...],  // §16
  "compressed_narrative": [...],           // §20
  "fingerprint_matches": [...],            // §19
  "delta_status": "new|fixed|changed",     // §18
  "activation_likelihood": 0.6,            // §22
  "feature_flags_gating": [...],           // §22
  "auth_abuse_kind": null,                 // §23
  "worker_context": null                   // §24
}
```

ChainIR (LLM-facing) gets the same fields plus a `narrative` block per
§20 to give the LLM a compact story rather than a raw hop list.

---

## §36. Example traversal algorithms

### §36.1 Storage-edge join (§11)

```python
def storage_edges(target_db):
    cur = target_db.cursor()
    cur.execute("""
      SELECT w.id, r.id, w.key_static, w.value_node, r.consumer_kind
      FROM storage_events w, storage_events r
      WHERE w.op = 'write' AND r.op = 'read'
        AND w.key_static = r.key_static
        AND w.api = r.api
    """)
    for write_id, read_id, key, val_node, cons in cur:
        yield {
            "from": val_node,
            "to": read_id,
            "key": key,
            "confidence": persistence_confidence(write_id, read_id)
        }
```

### §36.2 Async + storage-aware BFS (§11 + V1 §3)

```python
def find_chains(graph, sources, sinks, max_hops=12,
                max_storage_hops=1):
    queue = [(s, [s], 0, 0) for s in sources]
    while queue:
        node, path, hops, storage_hops = queue.pop()
        if node in sinks:
            yield path
            continue
        if hops >= max_hops: continue
        for edge in graph.out_edges(node):
            if edge.kind == 'storage':
                if storage_hops >= max_storage_hops: continue
                queue.append((edge.target, path + [edge],
                              hops + 1, storage_hops + 1))
            elif edge.kind in ('async_handler', 'call', 'arg_to_param'):
                queue.append((edge.target, path + [edge],
                              hops + 1, storage_hops))
```

### §36.3 Parser-context viability finalize pass (§15)

```python
def finalize_chain_viability(chain):
    sink_ctx = sink_contexts[chain.sink.node_id]
    state = 'raw'
    for hop in chain.path[1:-1]:
        wrap = wrappers.get(hop.qname)
        if wrap: state = wrap.transform(state)
    chain.encoding_state = state
    chain.execution_viable = classify_viability(sink_ctx, state)
    chain.severity *= viability_multiplier[chain.execution_viable]
```

### §36.4 Compressor (§20)

```python
def compress(chain):
    out = [chain.path[0]]
    for n in chain.path[1:-1]:
        if must_preserve(n):
            out.append(n); continue
        if framework_passthrough(out[-1], n, ...):
            out[-1] = merge_summary(out[-1], n); continue
        if equivalent_edge(out[-1], n): continue
        out.append(n)
    out.append(chain.path[-1])
    chain.narrative = render_narrative(out)
    return chain
```

---

## §37. Practical tradeoffs

| Tradeoff | V2 choice | Rationale |
|----------|-----------|-----------|
| Over-approximation vs precision in §11 storage | Key-static match required; key-dynamic = warn only | Avoid graph explosion |
| Granular vs coarse parser context (§15) | 13-bucket coarse taxonomy | Sufficient for exploit decisions; no parser implementation |
| Compression aggressiveness (§20) | Preserve any node with sanitizer/context/origin/storage tag | Never lose a decision-relevant hop |
| Corpus size (§19) | ≤1000 fingerprints, manual curation | Avoid ML drift |
| Multi-target correlation (§21) | Opt-in; hash-only | Privacy + bounty platform compliance |
| Deobfuscation depth (§16) | Light only; no symbolic execution | Time budget |
| DSL surface (§17) | Embedded in Python; no parser | Lower bar to extend |
| Reachability granularity (§22) | Route + lifecycle only; not per-component | Bounded BFS |
| Schema migrations | All in `bin/migrate_db.py` | Single point of truth |
| LLM-stage IR | Chain JSONL v2.0 fields additive | Skill compatibility |

---

## §38. Long-term architecture risks + Do NOT build

### §38.1 Long-term risks

1. **Drift from bug-bounty signal**. Generic SAST is a black hole.
   Hard scope every subsystem with a "what exploit class does this
   open?" justification. Reject features that broaden the analyzer
   away from browser-side, exploitable bugs.
2. **LLM dependency entrenchment**. V2 surfaces more deterministic
   evidence; ensure each new feature works *without* the LLM for
   ranking and triage. The LLM should be the verdict tier, not the
   primary classifier.
3. **Corpus capture by past patterns**. If the corpus (§19) becomes
   the primary ranker, the analyzer over-fits to last quarter's
   bugs. Treat it as a **bonus**, never a gate.
4. **Plugin scope creep**. Every framework adapter (V1 §6) and every
   storage API (§11) is one more thing to maintain. Cap framework
   support to the top-10 by industry deployment and ship a "rule
   contribution" doc.
5. **Schema sprawl**. 8 new tables × per-target DB × migrations is
   real surface area. Track schema regressions per release.

### §38.2 Do NOT build (anti-patterns)

These are explicit anti-patterns. The analyzer must reject them.

1. **No symbolic execution.** Even bounded SE turns into a research
   project. We use AST + simple constant folding (§16); we do not
   attempt path-condition reasoning.
2. **No whole-program inference of dynamic dispatch.** V1 §2 bounded
   resolution: 8 per call site, fallback to dynamic. Never lift the
   cap.
3. **No "generic JS analyzer".** This is browser-side, exploit-
   centric. No Node-only SAST features (filesystem sinks, child_process,
   etc.) unless they appear in the browser's JS surface.
4. **No academic dataflow lattice.** We are not implementing a
   complete lattice over JS types. Coarse string/number/object/
   tainted is enough.
5. **No reactive recomputation framework.** Delta scan (§18) is a
   batch diff; we do not chase a continuous-recompute system.
6. **No general-purpose graph DB.** SQLite + indexes is enough; we
   do not introduce Neo4j, RedisGraph, or property-graph engines.
7. **No ML model in the pipeline.** §19 is curated fingerprints, not
   embeddings + classifiers. Embeddings are fine for RAG (existing
   path); not for triage scoring.
8. **No payload synthesis in the analyzer.** Payload generation
   stays in the browser-confirm and parser-pipeline-fuzz skills;
   the analyzer reports viability, not exploit strings.
9. **No "smart auto-fix" suggestions.** We are an offensive tool.
   Defensive SAST style fix recommendations are out of scope.
10. **No autonomous send-to-target.** Every dynamic step routes
    through Caido + browser-confirm; the analyzer never opens a
    socket to a target.
11. **No cross-target auto-disclosure.** §21 correlation is local
    and analyst-curated; never auto-cross-post a finding to a sibling
    target.
12. **No silent normalization.** Every §16 transform writes to the
    transform log; an analyst can always reverse-trace to original
    bytes.
13. **No replacing the existing chain extractor wholesale.** V2 is
    additive. The current `extract_chains_bounded.py` keeps running;
    each subsystem adds fields, not new extractors.
14. **No swapping ChainIR's primary representation.** Compressed
    narratives (§20) are an LLM-facing view; the canonical chain
    JSONL remains the full hop list.
15. **No "AI agent that audits other agents'" loops.** The Sonnet →
    Opus advisor pipeline is fixed; the cc-taint-adversarial skill
    is the experimental track. Do not add a third agent layer.

---

## Appendix A — Touched files at a glance (per-subsystem)

| Subsystem | New files | Edited files |
|-----------|-----------|--------------|
| §11 | `storage.py`, `bin/storage_edges.py` | `ast_extractor.js`, `callgraph.py`, `bin/extract_chains_bounded.py` |
| §12 | `origin_trust.py` | `ast_extractor.js`, chain scorer |
| §13 | `clobber.py`, `bin/clobber_chains.py` | `ast_extractor.js`, `bin/extract_chains_bounded.py` |
| §14 | `pp_gadgets.py`, `taxonomies/pp_gadgets.json` | `pp_chains.py`, chain scorer |
| §15 | `parser_context.py`, `taxonomies/wrappers.json` | `sink_viability.py` (V1), chain scorer |
| §16 | `deob_normalize.js`, `deob_log.py` | `ast_extractor.js` driver |
| §17 | `dsl.py`, `bin/q.py` | (migrations from callgraph_tools, gap_analyzer) |
| §18 | `delta.py`, `bin/diff_scan.py` | `callgraph.py` (file_hashes already exists), reporter |
| §19 | `corpus.py`, `corpus/fingerprints/*.json` | chain scorer |
| §20 | `chain_compress.py`, `taxonomies/summarizers.json` | `audit_pipeline.py` |
| §21 | `corr.py`, `bin/corr.py` | n/a |
| §22 | `reachability.py`, `route_extractor.py` | chain scorer |
| §23 | `auth_state.py`, `route_guards.py` | taxonomy, chain scorer |
| §24 | `workers.py` | `ast_extractor.js`, `callgraph.py` |

---

## Appendix B — Calibration metrics to track

Every subsystem ships with a regression metric. The calibration
notes (notes/pipeline_calibration_*.md) get updated per release.

- `hot_jsonl_tp_rate` — TP / (TP+FP) on `hot.jsonl` after Opus audit.
- `hot_jsonl_recall` — TP / (TP + known_TP_not_in_hot).
- `audited_chains_per_engagement`.
- `opus_cost_per_engagement`.
- `delta_warmcache_walltime` (post-§18).
- `compression_ratio_avg` (post-§20).
- `stored_xss_class_recall` (post-§11).
- `postmessage_severity_correlation` (post-§12).

Each metric has a regression threshold: a 5% degradation blocks ship.

---

## Appendix C — Companion docs

- `plans/PLAN.md` — workspace plan / phases.
- `plans/ARCHITECTURE_EVOLUTION.md` — V1 (§1–§10 + LLM refactor).
- `plans/CC_TAINT_ADVERSARIAL.md` — LLM stage v1 refactor.
- `plans/IMPL_TIER123.md` — in-flight T1–T3 implementation log.
- `wiki/techniques/` — analyst-facing technique catalog (the source
  for §19 archetypes).
- `notes/pipeline_calibration_*.md` — calibration evidence (current
  baseline: 2026-05-18).

---

End of Volume II.
