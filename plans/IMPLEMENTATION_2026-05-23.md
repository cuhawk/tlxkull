# Implementation 2026-05-23 — Claude YT takeaways

Source: distillation of @claude YouTube videos posted 2026-05-16 →
2026-05-23, focused on Anthropic's "How we Claude Code", "Tool, skill,
or subagent? Decomposing an agent", "Agents that remember", "Memory
and dreaming for self-learning agents", "Evals for taste", "Making
agentic workflows trustworthy and verifiable with a custom DSL",
"The prompting playbook", "How Anthropic uses Claude in Cybersecurity",
Code with Claude London 2026 keynote, and "Beyond the basics with
Claude Code".

Decision: skip CMA, MCP tunnels, and Anthropic Routines (cost vs Max
sub coverage doesn't pencil out — see chat transcript 2026-05-23).
Skip DO droplets too for cockpit work (keep DO only for `recon`).
Everything below runs on the existing local Max-sub-covered
interactive Claude Code.

## What shipped

### 1. Two-judge verdict pipeline

**Why:** the 2026 prompting playbook flagged that a single LLM judge
over-justifies its first scored token. Adding a fresh-context
verifier subagent that reads only the auditor's reasoning catches
strawman counterarguments, mis-cited lines, and miscalibrated
confidence — before any browser-confirm budget is spent.

**Files:**

- `.claude/skills/cc-taint-adversarial/prompts/verifier.md` — new
  prompt template enforcing reasons-first key ordering, a 5-check
  list (exploit traceability, counterargument substance,
  blocking_unknowns load-bearing-ness, triage/confidence
  calibration, sanity grep), and a no-escalation rule (verifier may
  only agree or downgrade).
- `bin/verdict_verifier.py` — prepare/ingest/finalize subcommands.
  Ingest rewrites the opus record's triage/confidence on
  downgrade, strips chain from browser/mock queues, re-queues to
  `_re_expand_queue.jsonl` on `evidence_gap`. Enforces
  no-escalation invariants in code.
- `.claude/skills/cc-taint-adversarial/SKILL.md` — Step 4.5 added.
- `.claude/skills/cc-taint-adversarial/prompts/adversarial.md` —
  strengthened reasons-first key-order instruction.

### 2. tlx-investigate — Clue pattern

**Why:** Anthropic's internal "Clue" agent demoed at Code with
Claude London: NL question → visible plan → tool calls → cited
verdict + remediation. Same discipline works for TLX target
questions ("biggest unaudited surface?", "why did chain c042 drop?",
"sibling functions that bypass DOMPurify?").

**Files:**

- `.claude/skills/tlx-investigate/SKILL.md` — 261 lines, hard rules,
  4-step flow (plan blocking → execute → verdict+remediation →
  result block), per-target `investigations/<utc>/` scratch dir.
- `.claude/skills/tlx-investigate/prompts/factcheck_subagent.md` —
  read-only fact-check subagent template with JSON-only output
  schema.

### 3. Wiki-dream — offline curator

**Why:** Anthropic's "Memory and dreaming" pattern. Nightly batch
walks recent tail data (autoresearch, findings, opus audits,
verifier downgrades, podcast distill logs), dispatches read-only
subagents to distill candidate wiki patches into
`wiki-staging/<utc>/`. Non-destructive — user reviews and manually
promotes.

**Files:**

- `.claude/skills/wiki-dream/SKILL.md`
- `.claude/skills/wiki-dream/prompts/distill.md`
- `bin/wiki_dream.py` — gather / ingest / summary / promote
  subcommands; backlog gate prevents losing curation work.

### 4. Mythos-read — full-tree audit

**Why:** Mythos OpenBSD-vuln discovery validated full-source-tree
LLM audit for catching bugs the chain graph misses (cross-file
invariants, prototype pollution gadgets, crypto misuse,
auth-state confusion, dead-code reactivation).

**Files:**

- `.claude/skills/mythos-read/SKILL.md`
- `.claude/skills/mythos-read/prompts/full_tree.md`
- `bin/mythos_read.py` — size / prepare / ingest / summary
  subcommands. Default 5 MB eligibility cap. Novel medium+
  hypotheses get emitted as `chains/_mythos_synthetic.jsonl`
  rows for follow-up cc-taint-adversarial. Idempotent.

Reality check from `mythos_read.py size`: current TLX targets are
all over-budget at 5 MB (smallest: 16 MB). Skill is correctly
positioned as a special-case tool for smaller engagements OR for
users willing to raise `--max-bytes` after weighing the
prompt-quality tradeoff.

### 5. Eval set for chain audits

**Why:** before this, every change to taint logic was a coin-flip
— no way to detect regressions until weeks later. Eval set freezes
known TPs (control), known FPs (edge), and known undeterminables
(boundary), and grades any new cc-taint-adversarial run against
the pinned outcomes.

**Files:**

- `evals/chain_audit/README.md` — bucket semantics, entry schema,
  how to populate from real engagements.
- `evals/chain_audit/{control,edge,boundary}.jsonl` — empty
  initially; user populates 10 entries per bucket from real
  engagement data.
- `bin/run_chain_eval.py` — prepare/score subcommands. Score
  compares pass rate per bucket and emits a delta vs the prior
  run.

### 6. DOM verification contract on browser-confirm

**Why:** Tar's DOM-contract idea from Designing-with-Claude (Code
with Claude London 2026): emit `data-verify-*` attributes from the
PoC; have the verifier read them deterministically; stop
LLM-judging screenshots. Boosts confirm reliability.

**Files:**

- `bin/poc_verify_contract.js` — new JS helper read via
  `evaluate_script`. Returns `{fired, trigger, source, sink,
  result_canary, evidence, entries[]}`.
- `.claude/skills/browser-confirm/SKILL.md` — Step 2c added (live
  mode), Step 6 added (mock mode). Output extended with
  `verify_contract.json`.
- `.claude/skills/report-finding/SKILL.md` — Step 5 now includes
  the minimal contract HTML example so generated PoCs emit it.

### 7. Per-finding session UX

**Why:** Anthropic Cloud Security's per-finding session model — one
Claude session per finding instead of one mega-session draining
the queue. Local equivalent: fan out one subagent per queued
chain (capped at 3 parallel — Caido queue can't handle more).

**Files:**

- `.claude/skills/per-finding-session/SKILL.md`
- `.claude/skills/per-finding-session/prompts/finding.md` — per-
  finding subagent template; write access is scoped to the
  `findings/<chain_id>/` scratch dir only.
- `bin/per_finding_dispatch.py` — plan / collect subcommands.
  Detects live-sensitive targets (`-syn` suffix) and forces mode
  to mock automatically.

### 8. Audit tools (prompt-cache + skill hygiene)

**Why:** prompting playbook flagged cache-busters and stale
defensive instructions as common silent regressions.

**Files:**

- `bin/cache_audit.py` — scans `.claude/skills/**/SKILL.md` and
  prompt-rendering bin scripts for cache-busters (datetime.now
  inside prompt prefixes, long descriptions, template tokens).
  185 files scanned; 60 findings (mostly noise — 4 high-sev
  false positives in non-prompt code; 37 long descriptions =
  real action items for later cleanup).
- `bin/skill_hygiene_audit.py` — scans skills for old
  thinking-toggle artifacts, undated `# IMPORTANT:` markers,
  one-sided cost statements, general exhortations, frontmatter
  health. 35 issues across 37 skills (24 long descriptions, 8
  missing trigger phrases, 3 undated absolutes — the 3 absolutes
  got dated in this batch).

Both audits are advisory-only; nothing auto-modifies skills.
Run as part of pre-engagement hygiene.

### 9. Dated 3 undated `# IMPORTANT` markers

`.claude/skills/{opus-deep-audit,recon,report-finding}/SKILL.md`
absolute rules now carry `(2026-05 — <reason>)` stamps so future
Claudes know whether the rule still applies.

### 10. DSL chain rep spec (deferred)

`plans/CHAIN_DSL.md` outlines a Python-subset DSL representation
for chains that the auditor + verifier read and rewrite, with
content-addressable memoization. **No code written.** Implement
only after two-judge verifier + eval set prove out and audit
quality is the bottleneck.

## What's tracked as future cleanup (NOT shipping in this batch)

- 37 SKILL.md `description:` fields >350 chars. Re-write to keep
  trigger phrase but cap length. Helps both prompt-cache and skill
  discoverability. Batch as separate pass.
- 8 SKILL.md descriptions missing the `Use when` / `Trigger:`
  phrase. Same batch.
- The 4 high-severity `cache_audit.py` hits are false positives
  (non-prompt code) but the heuristic should be tightened to
  reduce noise in future runs.
- Populate `evals/chain_audit/{control,edge,boundary}.jsonl` from
  real engagement data (10 entries per bucket target). Requires
  user to walk past audits and extract chains.

## Why DSL is deferred

Don't start until ALL three are true:
1. Two-judge verifier has surfaced ≥5 caught false-positive
   verdicts.
2. Eval set has ≥15 entries.
3. cc-taint-adversarial has run on ≥4 fresh targets and per-target
   audit cost is measurably the engagement bottleneck.

Before that, the DSL is yak-shaving.

## Validation steps

- `python3 bin/verdict_verifier.py --target X --dry-run prepare` → 0
- `python3 bin/run_chain_eval.py prepare --bucket all --dry-run` → 0
- `python3 bin/wiki_dream.py gather --hours 24 --dry-run` → 0
- `python3 bin/mythos_read.py size --target coralbug3-syn` → over-budget verdict
- `python3 bin/per_finding_dispatch.py --target coralbug3-syn --dry-run plan` → mode=mock (correct: synack-l4 target)
- `python3 bin/cache_audit.py --md | head -50` → markdown report
- `python3 bin/skill_hygiene_audit.py --md | head -50` → markdown report

## Cross-references

- `plans/CC_TAINT_ADVERSARIAL.md` — original cc-taint-adversarial spec.
- `plans/CHAIN_DSL.md` — DSL spec (deferred implementation).
- `notes/pipeline_calibration_2026-05-18.md` — the eval-set source data.
- `memory.md` — updated with the post-2026-06-15 billing rule, new
  skills, and CMA/DO decision.
