---
name: pipeline-auto
description: Branched per-scope-entry pipeline. Classifies every in-scope entry into url|wildcard|ip_cidr, runs the matching lane (js-harvest for url; subdomain enum + masscan + httpx + js-harvest for wildcard; masscan + httpx + js-harvest for ip/cidr), and HALTS at the audit boundary — never auto-fires opus-deep-audit or cc-taint-adversarial. Use after target-init; trigger /pipeline-auto <name> or "run pipeline on <name>".
---

# pipeline-auto

Front-door for the branched pipeline. Spec: `plans/PIPELINE_AUTO.md`.

## When to invoke
- `target-init` has produced `targets/<name>/status.json`.
- User says: "run pipeline on <name>", "/pipeline-auto <name>",
  "kick off the pipeline", or any phrasing implying full-target sweep
  short of audit.

## What it does
1. Classifies each `scope.in` entry:
   - URL (host, `https://...`) → **url lane**
   - `*.apex.tld` or bare apex → **wildcard lane**
   - IP, CIDR, IP-range → **ip_cidr lane**
2. Runs lanes in parallel (cap `--max-parallel`, default 4):
   - **url**: js-harvest → sourcemap-explode → rag-ingest → js-index →
     db-isolate → implicit-tags → async-edges → browser-context-infer →
     chain-bestfirst → sanitizer-on-path → chain-triage → dom-xss-hunt.
   - **wildcard**: subdomain enum (recon MCP) → resolve → masscan →
     httpx → for each live web host with JS, spawn url-lane.
   - **ip_cidr**: masscan → httpx → for each live web host with JS,
     spawn url-lane.
3. Writes `targets/<name>/_audit_queue.jsonl` and sets
   `status.json.phase = "ready_for_audit"`. **Stops there.** Opus /
   Sonnet audit (`opus-deep-audit`, `cc-taint-adversarial`,
   `opus-gap-audit`, `autoresearch-loop`) is a separate, user-triggered
   step.

## Inputs
- `targets/<name>/status.json` (must exist; run `target-init` if not).
- `memory.md > masscan_rate_pps`, `masscan_max_ips` (optional overrides).

## How to call
```
python3 bin/pipeline_run.py <name> [--dry-run] [--max-parallel 4] \
    [--masscan-mode {local,droplet}] [--ports {web,full}] \
    [--lanes url,wildcard,ip_cidr]
```

Always start with `--dry-run` on a new target — it prints the lane
classification without running anything. Confirm with the user that
lane assignment looks right before launching the real pipeline.

## Hard rules
1. **Never auto-fire audit.** The pause boundary is the whole point.
   `_audit_queue.jsonl` lists the chains ready for audit; the user
   triggers `/cc-taint-adversarial <name>` or `/opus-deep-audit <name>`.
2. **Respect `out:` deny-list** at every HTTP/scan step.
3. **masscan guards**: rate-cap from memory.md; `--ports full` requires
   `--confirm-full`; > `masscan_max_ips` requires `--force`.
4. **Synack** (`*-syn` target dirs) is reference-only — skip entirely.
5. **Scope drift**: re-run `bin/scope_aggregate.py` before any wildcard /
   ip_cidr lane if its mtime is older than 7 days.

## Outputs
- `targets/<name>/_audit_queue.jsonl` (one row per audit-ready chain set)
- `targets/<name>/recon/{masscan,live_web,*}.jsonl`
- `targets/<name>/raw/`, `sources/`, `index/`, `chains/` (from sub-skills)
- `targets/<name>/status.json.phase = "ready_for_audit"`

## Failure modes
- Unknown-lane entry in scope → log, surface to user, skip.
- masscan binary missing → instruct `brew install masscan` or droplet mode.
- recon MCP failure on wildcard → surface error, keep other lanes running.

## Follow-up
Once at audit boundary, user runs ONE of:
- `/cc-taint-adversarial <name>` — Claude-Code-driven adversarial audit
  (preferred for max-quality engagements, no API spend).
- `/opus-deep-audit <name>` — Sonnet→Opus advisor pipeline (capped by
  `memory.md > opus_budget_per_target_usd`).
