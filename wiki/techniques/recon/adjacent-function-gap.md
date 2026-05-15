---
title: Adjacent-function gap analysis (inverse taint)
slug: adjacent-function-gap
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [technique/recon, technique/whitebox, technique/ai, pattern/inverse-taint]
inbound: []
---

# Adjacent-function gap analysis

## Pattern

Most static review (and TLX's current taint-chain audit) looks at
flows that *exist*. Adjacent-function gap analysis flips it: find
where a security control *exists*, then enumerate sibling functions
in the same module / router / class that handle similar data
**without** that control.

Justin Gardner's highest-yield AI prompt (CT Ep 137); landed
high/crit on a HackerOne spot-check SDK in <6 hours. Single most
quoted prompt template in the CT canon.

## Preconditions

- Source obtained and indexable (sourcemap-explode complete or
  small repo).
- At least one verified security-relevant function exists in the
  codebase (auth check, sanitizer, ACL, rate limit). Find via test
  files — "what tests does the team write?" points to controls
  the team cares about.

## Detection

1. Identify a confirmed control: e.g. `requireRole('admin')`,
   `sanitizeHtml()`, `rateLimit({...})`, `csrf.verify(token)`.
2. Enumerate callsites with a structural query (callgraph node
   list filtered by callee qname). TLX:
   `js_get_chains(callee=<qname>)` then dedupe by parent function.
3. For each callsite, get sibling functions:
   - same file
   - same router path prefix
   - same React/Vue component module
   - same Go package / Java class
4. Prompt LLM: "Compare these N siblings. List the ones that
   accept similar input shapes / hit similar resources but DO NOT
   call <control>."

## Triggering

Killer prompt (Justin's exact phrasing, CT Ep 137):

> *"Look at where security controls are implemented and then look at
> similar or adjacent functions that might be missing that same
> control."*

Longer template (works with Claude Code or Gemini CLI on whole-bundle
context):

```
You are reviewing the file at <path>.
Function FN_OK = <qname> calls security control CONTROL = <qname>.

1. List every other function in the same module/router/component
   that touches the same resource class (e.g. same SDK method, same
   DB table, same route prefix, same RPC verb).
2. For each, state whether it invokes CONTROL or an equivalent
   sanitizer. Quote the exact line.
3. Output a JSON array of {function, callsite_line, control_present:
   bool, reason}.
4. Rank gaps by exploit severity assuming the missing control was
   intentional protection.
```

## Why it beats forward taint

- Forward taint finds where source can reach sink — exists only if
  the developer wired the sink up at all.
- Reverse-gap finds where the developer *forgot* to wire the
  control — a finding the codebase makes invisible because the
  taint chain never crosses the protection.
- Catches "auth on A, none on B" patterns that PortSwigger Academy
  drills as "broken access control" — typically the highest-paid
  bug class in modern programs.

## Bypasses (when gap is fake)

- Control applied at framework level (middleware decorator) — read
  router config / express.Router.use / Next middleware.ts before
  flagging.
- Control applied at proxy level (nginx / Caddy / Cloudflare) — read
  reverse proxy config in repo.
- Control applied at SDK layer (auto-injected by client). Common in
  gRPC wrappers.

## TLX integration

Proposed skill `opus-gap-audit` (sibling to `opus-deep-audit`):

1. Given a control qname, query callgraph for all callsites.
2. For each callsite, find siblings via:
   - same `nodes.file`
   - parent qname differs by leaf only (`foo.bar.A` vs `foo.bar.B`)
   - same React component file boundary
3. Emit `chains/gap_<control>.jsonl` — one row per sibling without
   control.
4. Run cascade-audit ([[../../tools/karpathy/js-review-cascade]])
   on top-N gaps.

## Seen in the wild

- {date: 2025-08-28, source: CT Ep 137} — Justin Gardner, HackerOne
  spot-check SDK, high/crit in <6h.

## References

- Critical Thinking Podcast Ep 137 — <https://www.youtube.com/watch?v=sTG-OX5BbBc>
- HackerNotes — <https://blog.criticalthinkingpodcast.io/p/hackernotes-ep-137-how-we-do-ai-assisted-whitebox-review-new-cspt>

## Related

- [[ai-whitebox-source-review]] — parent four-pass workflow that
  produces this prompt in Pass 4.
- [[../../tools/karpathy/js-review-cascade]] — cost-cap the LLM
  passes.
- [[../../tools/karpathy/source-code-review]] — "forgotten security
  control" is root-cause class 3.
- [[../../tools/tlx/ai-whitebox-workflow]].
