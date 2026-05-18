---
title: Beautify minified bundles before js-index (function boundary preservation)
slug: beautify-before-index
created_utc: 2026-05-18T16:00:00Z
updated_utc: 2026-05-18T16:00:00Z
tags: [technique/recon, technique/workflow, pattern/pipeline-fix, pipeline/js-index, pipeline/chain-triage]
inbound: []
---

# Beautify before js-index

## The failure mode

Modern webpack/rollup bundles ship as a single very long line. js-index
uses tree-sitter to parse the file, which works on minified code in
principle — but function-boundary detection collapses. The result:

- All functions report `line: 1`.
- Most function qnames become webpack mangles (`$.set`, `$.validate`,
  `$1`, `$V`, `$N`) since the analyzer falls back to whatever
  identifier the AST attaches.
- The bundle's hundreds of distinct functions get bucketed under a
  handful of names.
- Chain extraction produces large numbers of **depth=0 self-flow
  chains** where `source.qname === sink.qname`. The analyzer found a
  source-tag pattern AND a sink-tag pattern inside the same opaque
  function body. It can't prove or disprove flow → it flags
  conservatively.

These self-flows look high-severity on paper (score 90+, source =
`onmessage_handler` or `proto_assign_merge`, sink = `setTimeout_string`
/ `event_handler_attr_assign` / etc.). They are almost entirely
statistical noise.

## Detection

Two checks on a fresh target:

```bash
# 1. Are bundles unbeautified?
for f in targets/<name>/raw/*.js; do
  lines=$(wc -l < "$f")
  bytes=$(wc -c < "$f")
  ratio=$((bytes / (lines + 1)))
  echo "$lines lines / $bytes bytes / ratio=$ratio $f"
done | sort -k7 -n  # sort by lines asc
# Files with bytes/lines > 1000 are minified.

# 2. Are most hot chains self-flow?
jq -r '. | select(.source.qname == .sink.qname) | .id' chains/hot.jsonl | wc -l
# vs total
wc -l chains/hot.jsonl
# If self-flow fraction > 50%, beautify is missing.
```

For netlify-h1 (2026-05-18): 20/20 hot chains self-flow, all at line=1,
all on minified `app.netlify.com/6932.bundle.js`. Pipeline missing
beautify.

## Fix

Add a `beautify` phase between `js-harvest` and `js-index`. The
reference recipe (from coolblue-intigriti `status.json.phases.beautify`):

```
npx --yes js-beautify -r -n -s 2 targets/<name>/sources/*.js
```

Coolblue beautified 69 of 86 files; resulting expansion ratio 184x
(1725 → 318634 lines), longest remaining line 98890 chars (residual
inline blobs — base64 lookup tables / huge regex). Tree-sitter handles
the residual long lines fine because the analyzer is AST-based, not
line-based — what matters is that function boundaries are now
detectable on real bundle code.

After beautify, re-run:

```
target-init  # if status.json missing
js-index <target>
db-isolate snapshot <target> <in-scope-host-prefixes...>
extract_chains <target>
```

## What changes after beautify

- Chains drop from depth=0 self-flow to depth>=1 with distinct
  source/sink qnames.
- Function qnames pick up real identifiers (or at least real
  boundaries: `module_4382.foo` instead of `$.set`).
- Self-flow chain count drops dramatically. The remaining chains are
  the ones actually worth auditing.

## Pipeline gate (recommended)

In `target-init`, refuse to run `js-index` unless a beautify check
passes. Mark the file as minified when `(bytes/lines) > 500` and warn
the operator. Either auto-beautify or fail fast.

## Seen in the wild

- {date: 2026-05-18, target: netlify-h1, chains: [25574-25581, 35589-35600], verdict: false_positive_batch}
  20 hot chains all flagged 6932.bundle.js functions at line=1 with
  source=postMessage/proto-merge and sink=setTimeout-string/event-handler-attr/etc.
  Live test against app.netlify.com unauthenticated: 5 postMessage
  listeners registered, 11 attacker-shape payloads sent, ZERO sinks
  fired from listener code paths, ZERO prototype pollution. Self-flow
  chains diagnosed as static-analyzer noise from unbeautified bundle.
  Details:
  [`targets/netlify-h1/findings/35589/confirmed.json`](../../../targets/netlify-h1/findings/35589/confirmed.json).
- {date: 2026-05-15, target: coolblue-intigriti, status: no incident}
  Coolblue ran the beautify phase (69 of 86 files beautified) before
  js-index. Self-flow rate on hot chains was much lower. Confirms the
  fix is effective.

## Related

- [[scope-aware-chain-triage]] — sibling chain-triage lesson; execution
  origin vs file host.
- [[adjacent-function-gap]] — another approach that benefits from
  intact function boundaries (impossible on a single-line bundle).
- [[../../tools/tlx/ai-whitebox-workflow]] — parent pipeline.

## References

- TLX target `coolblue-intigriti` `status.json.phases.beautify` —
  reference recipe with file counts.
- TLX target `netlify-h1` `status.json.phases.hot_chain_live_confirm_batch` —
  symptom record with all 20 chain ids.
- js-beautify: <https://github.com/beautifier/js-beautify>.
