---
name: chain-triage
description: Rank candidate taint chains produced by js-index and split into hot vs cold. Calls js_get_chains(max_chains=200), scores by (source_severity × sink_severity), path length, and framework-match strength, writes chains/all.jsonl and chains/hot.jsonl. Run after js-index, before opus-deep-audit. Hot chains get Opus attention; cold chains feed autoresearch-loop.
---

# chain-triage

## Purpose
Decide what's worth deep-auditing. The static analyzer can produce
hundreds of chains; only a few are worth Opus's time. Triage compresses
the queue.

## Inputs
- `targets/<name>/index/` (from `js-index`).

## Steps
1. Call `js_get_chains(target_folder="targets/<name>/sources/", max_chains=200)`.
2. For each returned chain, compute a composite score:
   ```
   score = w_sev   * sink_severity(sink_kind)
         + w_src   * source_severity(source_kind)
         - w_path  * log(1 + path_length)
         + w_fw    * framework_match_bonus(chain, frameworks)
         - w_sanit * sanitizer_penalty(chain.path_has_sanitizer)
   ```
   Default weights live in `bin/triage_weights.json`; user can tune.
3. Write `targets/<name>/chains/all.jsonl` (every chain) and
   `chains/hot.jsonl` (top N where N = min(20, count*0.1)).
4. Compute a quick distribution (`{sink_kind: count}`,
   `{source_kind: count}`) for the result block.

## Sink severity defaults (high → low)
1. DOM XSS sinks (`innerHTML`, `outerHTML`, `dangerouslySetInnerHTML`,
   `document.write`, `eval`, `setTimeout(string)`, `Function(string)`)
2. Open redirect sinks (`window.location` family, `<a href>` set)
3. Prototype pollution gadgets
4. PostMessage sinks without origin checks
5. URL parsing on user-controlled input feeding fetch()

## Source severity defaults
1. `window.name`, `document.referrer`, URL fragment/query
2. `postMessage` event data
3. Network responses where origin isn't strictly trusted
4. Cookie / localStorage values

## Outputs
- `targets/<name>/chains/all.jsonl`
- `targets/<name>/chains/hot.jsonl`
- updated `status.json.phases.triage`

## Failure modes
- Empty chains list → most often means `js-index` didn't recognize
  any sources. Re-check framework detection; consider lowering
  `min_chain_score` threshold in TLX config.

## Result block
```json
"phases": { "triage": { "status": "done", "ts": "<iso>",
  "total": N, "hot": M, "sink_dist": {...}, "source_dist": {...} } }
```
