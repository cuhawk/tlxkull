---
title: Execution-origin vs file-host scoping for client-side chain triage
slug: scope-aware-chain-triage
created_utc: 2026-05-18T15:00:00Z
updated_utc: 2026-05-18T15:35:00Z
tags: [technique/recon, technique/workflow, pattern/scope-gate, pattern/gate-ordering, pipeline/chain-triage]
inbound: []
---

# Execution-origin vs file-host scoping

## The mistake to avoid

A taint chain's sink is reported as `sink.file =
assets.coolblue.de/js/stm/foo.js`. The `assets.coolblue.de` host is
not in the program's `http.md`. **Tempting wrong move:** mark the
chain `out_of_scope_sink` and archive.

The CDN/asset host hosts the JS *file*, but the JS *executes* in
whatever page loads it via `<script src=>`. If `www.coolblue.de`
(in-scope) loads `assets.coolblue.de/js/foo.js`, foo.js runs inside
the `www.coolblue.de` origin. DOM access, cookies, session storage,
auth bearer — all `www.coolblue.de`. An XSS in foo.js IS an XSS on
`www.coolblue.de`.

The right gate is **execution origin**, not file host.

## When file-host scope filtering is actually correct

Only when the JS file does not load into any in-scope page. Detect
by either:

- Static: `js-harvest` `_discovered_from.jsonl` (or whatever harvest
  log) shows which in-scope page seeded the asset URL. No in-scope
  seed → file probably loads from an out-of-scope tenant only.
- Dynamic: load each in-scope entry URL in the browser and observe
  whether the asset appears in `document.scripts`. If not, exclude.

## Supporting-host policy

CDNs / asset hosts adjacent to a program's primary hosts are usually
operated by the same org. Read-only `GET`/`HEAD` probes to fetch JS
bundles or check whether a referenced runtime endpoint exists are
generally accepted as part of testing the in-scope app. Mutating
verbs, auth-credentialed probes, or active fuzzing of CDN endpoints
need explicit program OK.

Concrete policy template (target dossier):

```
supporting_hosts:
  - assets.<program>.<tld>
  - cdn.<program>.<tld>
supporting_host_policy:
  - read-only GET/HEAD allowed
  - credentials:'omit' when probing
  - no mutating verbs
  - report all probe URLs in finding writeup
```

## Gate ordering for client-side chains with HTTP-fed sinks

Many client-side chains funnel through an XHR/fetch whose response
becomes the sink input — `addScriptSync(url) → new
Function(xhr.responseText)()` is one canonical shape. Three gates
typically need to hold:

1. **State gate** — runtime flag must allow the code path
   (e.g. `isPreview === true`).
2. **Throw/timing gate** — some prior fallback must throw to enter
   the dangerous branch (e.g. `document.write` post-DCL).
3. **Reflective endpoint gate** — the URL fetched must exist
   server-side AND reflect attacker-controlled input into a body
   that survives the sink's parser (`new Function`, `eval`,
   `innerHTML`).

**Order live-probe gates by cost.** Gate 3 (probe the endpoint with a
canary) is one HTTP request. If the endpoint returns 403/404, or
returns JSON/XML/HTML that won't parse as JS, the chain is dead
regardless of gates 1 and 2. **Always probe gate 3 first.** Don't
spend time crafting the `optimizely.push` payload to flip the state
flag if `/dist/preview_data.js` returns 403.

## Detection

Quick host audit on a target post-`chain-triage`:

```bash
jq -r '.sink.file' targets/<name>/chains/hot.jsonl \
  | sed 's/[/_].*//' | sort -u
```

For each non-`www.<program>` host:

1. Open the in-scope entry URL in a browser. Check whether the asset
   shows up in `document.scripts`.
2. If yes: treat the chain as in-scope (execution origin) and live-
   probe. The CDN host is a *supporting host*, not out-of-scope.
3. If no: file-host filter applies; archive as out_of_scope_sink.

## Why it matters

- **Cost of a false out-of-scope archive:** a real bug skipped. The
  vulnerability is real, fires in the in-scope origin, but is buried
  under an incorrect classification.
- **Cost of a false in-scope assumption:** probes to a host the
  program disowns. Mitigate via read-only/credentials:'omit'.
- **Cost of skipping gate 3:** crafting state-flip payloads when the
  endpoint doesn't exist — pure waste.

## Seen in the wild

- {date: 2026-05-18, target: coolblue-intigriti, chain: 12, verdict:
  false_positive}
  Static finding: `new Function(n.responseText)()` at line 9297 of
  `assets.coolblue.de/js/stm/6689543890403328.js`, fed by XHR to
  `/dist/preview_data.js?token=<attacker_controllable>`.
  Earlier session archived as `out_of_scope_sink` (wrong reasoning —
  sink file lives on CDN). On revival, the JS file loads into
  `www.coolblue.de` via `<script src=>` — chain IS in-scope by
  execution origin. Live-probed gate 3 first: every path under
  `assets.coolblue.de/dist/` returns 403 application/xml.
  `/dist/preview_data.js` is not deployed. Chain confirmed FP at
  gate 3 in 2 HTTP probes, ~5 seconds. Gates 1 and 2 never had to be
  tested. Findings record at
  [[../../../findings/12-coolblue-intigriti-optimizely-preview-rce-fp]]
  (or `targets/coolblue-intigriti/findings/12/confirmed.json`).
- {date: 2026-05-18, target: coolblue-intigriti, chains: [33, 56, 57,
  78], status: pending_revisit}
  Same STM bundle, prototype-pollution gadget sinks. Originally
  archived as `drop` by `cc-taint-route`. Worth re-auditing now that
  scope-policy is clarified; the gadgets fire only if their
  respective triggers (state mutations) actually run, which is again
  a gate-3-shaped question (does an in-scope page mutate a path that
  reaches these sinks?).

## Related

- [[adjacent-function-gap]] — sibling recon technique.
- [[../../tools/tlx/ai-whitebox-workflow]] — parent pipeline.
- [[../../targets/coolblue-intigriti]] — first program where this
  pattern was identified.

## References

- TLX project file `CLAUDE.md` — hard rule #1 (scope) still applies,
  just interpreted by execution origin not file host.
- TLX target `coolblue-intigriti` `chains/_fp_archive.jsonl` —
  entries 12 (false_positive after live), 33/56/57/78 (drop, awaiting
  re-audit under refined policy).
- TLX `findings/12/notes.md` — full live reproduction transcript.
