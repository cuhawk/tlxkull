---
name: tlx-investigate
description: Natural-language investigation skill for a TLX target — answer "why / which / where / how" questions about a specific engagement by writing a visible plan, executing read-only tool calls, fanning out read-only Claude Code subagents for discrete fact-checks, and emitting a cited verdict + remediation list. Implements Anthropic's "Clue" detection-and-response pattern from Code with Claude London 2026. Trigger with `/tlx-investigate`, "investigate this target", "answer this question about <target>", "what's the biggest unaudited surface in", "give me a plan to exploit", "explain why chain X", or "diagnose <target>".
---

# tlx-investigate

## Purpose

Answer free-form analyst questions about a specific TLX target with
the same discipline Anthropic's internal "Clue" agent uses for
detection-and-response triage: plan, execute, cite, recommend. The
output is a short markdown report stored under
`targets/<name>/investigations/<utc>/report.md` plus a status.json
phase entry — so the answer is auditable and resumable, not lost in
chat history.

Use this skill when the user asks any of:

- "Which chains in coralbug3-syn touch cookie auth?"
- "What's the biggest unaudited surface in netlify-h1 right now?"
- "Why did chain c042 verdict drop?"
- "Are there sibling functions in foo.js that bypass DOMPurify?"
- "Give me the 3 highest-impact unaudited chains in <target> and a
  6-step exploit plan for each."
- "Diagnose <target>" (general health-check; falls back to status.json
  phase audit).

Do **not** use this skill for: live HTTP, wiki writes, opus deep-audit
dispatch (those have their own skills). This skill *prepares the next
action*, it does not perform it.

## Hard rules

1. **No live HTTP.** No browser MCP navigation. No `caido-replay`
   invocation. If the answer requires a live test, recommend
   `browser-confirm` in `## Recommended next actions` and stop.
2. **No wiki writes.** Reads of `wiki/` for evidence are fine.
   New wiki pages go through `wiki-ingest`.
3. **No API-key calls.** No `ANTHROPIC_API_KEY`, no Gemini chat models.
   Subagents are Claude Code `general-purpose` agents only — same
   rule as `cc-taint-adversarial`.
4. **Plan before act.** `plan.md` must exist on disk before any tool
   call beyond reading the target's `status.json`. If you skip this,
   the investigation is invalid and must be redone.
5. **Cite every claim.** Every bullet in `## Findings` must end with
   `(evidence: <file:line> | <chain_id> | <wiki/path.md>)`. No
   uncited assertion ships.
6. **Time-box: 15 minutes wall-clock.** If the investigation
   exceeds 15m, finalize what's known, mark `incomplete: true` in
   the status.json entry, write the report, and stop. Do not blow
   the budget chasing a thread.

## Inputs

| Path | Required | Producer |
| --- | --- | --- |
| `<question>` | required | user |
| `targets/<name>/status.json` | required | `target-init` |
| `targets/<name>/chains/*.jsonl` | preferred | `chain-triage` / `dom-xss-hunt` |
| `targets/<name>/index/{nodes,edges}.jsonl` | preferred | `js-index` |
| `targets/<name>/sources/` | preferred | `sourcemap-explode` |
| RAG `target_<name>` collection | optional | `rag-ingest` |
| `wiki/` | always readable | `wiki-ingest` |

If `<name>` is ambiguous, read `memory.md > Current target` first; if
still ambiguous, ask the user one tight question and stop.

## Steps

### Step 1 — Plan (BLOCKING)

Pick the UTC timestamp once: `UTC=$(date -u +%Y%m%dT%H%M%SZ)`.
Create `targets/<name>/investigations/$UTC/` and write `plan.md`
with this shape:

```markdown
# Investigation plan — <target>

**Question:** <quote user verbatim>
**Started:** <UTC ISO>
**Time-box:** 15 minutes

## Steps

1. <concrete step — tool / file / bin script>
2. ...
```

4-8 steps. Each step names a concrete tool / file / bin script
(e.g. "Read `targets/<name>/chains/dom_reachable.jsonl`",
"`mcp__tlx__js_get_chains(target=<name>, sink_category='dom_xss')`",
"Dispatch fact-check subagent: 'does `renderHTML` in `foo.js`
sanitize before innerHTML?'").

Do **not** proceed past Step 1 until `plan.md` exists on disk.

### Step 2 — Execute

Work through the plan. Allowed tools:

- `Read`, `Grep`, `Glob` across `targets/<name>/`, `wiki/`, `tlx/`,
  `plans/`, `notes/`, `bin/`.
- `mcp__tlx__js_get_chains` (filter by sink_category / source_category
  / file prefix).
- `mcp__tlx__js_get_snippet` (qname → source body).
- `mcp__tlx__js_examine_chain` (chain id → full path with snippets).
- `mcp__tlx__docs_query` with `collection="target_<name>"` (per-target
  source RAG) or `collection="wiki"` (technique RAG).
- `mcp__tlx__session_kv_get` for cached state.
- Optional: dispatch **read-only general-purpose subagents** for
  discrete subqueries. ONE subagent per subquery. Use the prompt
  template at `.claude/skills/tlx-investigate/prompts/factcheck_subagent.md`.
  Capture each response to
  `targets/<name>/investigations/$UTC/subagent_<n>.json`.

Forbidden in this phase:

- Any `Write` / `Edit` to files outside
  `targets/<name>/investigations/$UTC/`.
- Any live HTTP (browser MCP navigate / chrome-devtools navigate /
  caido replay).
- Any `wiki/` write.
- Any tool call that invokes `ANTHROPIC_API_KEY` or Gemini chat
  models (`js_run_audit`, `js_audit_status`, `js_consult_opus` —
  these are *not* allowed from inside this skill; recommend them
  in next-actions instead).

### Step 3 — Verdict + remediation

Write `targets/<name>/investigations/$UTC/report.md` with this
structure (exactly these section headers, in this order):

```markdown
# <short title derived from question>

## Question

> <verbatim quote of user's question>

## Plan

See [plan.md](plan.md).

## Findings

- <claim 1> (evidence: <file:line> | <chain_id> | <wiki/path.md>)
- <claim 2> (evidence: ...)
- ...

## Verdict

<one paragraph, 3-6 sentences, direct answer to the question>

## Recommended next actions

1. `<concrete CC command or skill invocation>` — <why>
2. ...

## Open questions

- <only if blocking_unknowns remain; each suggests the bin script /
  skill that would resolve it. Omit section entirely if none.>
```

Each `## Findings` bullet MUST end with an evidence pointer. No
exceptions.

### Step 4 — Result block

Append to `targets/<name>/status.json.phases.investigations[]`:

```json
{
  "ts": "<UTC ISO>",
  "question": "<verbatim>",
  "report_path": "investigations/<utc>/report.md",
  "findings_count": <N>,
  "subagent_count": <K>,
  "incomplete": <bool, only present if true>
}
```

Use the `bin/_lib.py` helpers (`write_status_phase` or
`status_lock`) so concurrent skills don't trample the file.

## Subagent dispatch pattern

Each fact-check is ONE subagent. The prompt body is constructed by
substituting variables into `prompts/factcheck_subagent.md`:

- `{{TARGET_NAME}}` — the target name.
- `{{TARGET_DIR}}` — absolute path to `targets/<name>/`.
- `{{SUBQUERY}}` — the discrete subquery (one sentence).
- `{{HINTS}}` — optional bullet list of files / chains / wiki pages
  the subagent should look at first.

Dispatch:

```
Agent(
  subagent_type="general-purpose",
  description="tlx-investigate factcheck: <subquery short>",
  prompt=<rendered prompt body>,
)
```

Capture the JSON response to
`targets/<name>/investigations/$UTC/subagent_<n>.json` where `<n>`
is a zero-padded integer. Validate the schema (see
`prompts/factcheck_subagent.md`); on schema failure, log to
`status.json.errors` and skip that finding — do not retry by
hammering the subagent.

## Run examples

**Question: "What's the biggest unaudited surface in coralbug3-syn?"**

Plan: read `status.json.phases`, read `chains/hot.jsonl`, diff against
`opus/` and `findings/`, group remaining chains by sink-category, pick
the bucket with highest cumulative product × count. Report names the
bucket and lists top 3 chain ids with snippet pointers; next actions
include "Run `python3 bin/cc_taint_runner.py --target coralbug3-syn
prepare --chain-ids ...`".

**Question: "Why did chain c042 verdict drop?"**

Plan: `mcp__tlx__js_examine_chain(chain_id="c042")`, read
`opus/c042.json` if exists, grep `_audit_log.jsonl` for c042. Report
cites the dominator guard that the auditor flagged and the line at
which the source value gets sanitized. Next actions: nothing (FP
confirmed) OR "Run `parser-pipeline-fuzz` if the sanitizer is
`DOMPurify@<old-version>`".

**Question: "Are there sibling functions in foo.js that bypass
DOMPurify?"**

Plan: `mcp__tlx__js_get_snippet` for each direct child of the class
in `foo.js`, dispatch one fact-check subagent per sibling asking
"does this function call DOMPurify.sanitize before any innerHTML /
outerHTML / insertAdjacentHTML / document.write call?". Findings
list each sibling with verdict + evidence pointer. Next actions:
`opus-gap-audit` on confirmed bypassers.

## Failure modes

| Symptom | Action |
| --- | --- |
| Question references a target whose dir doesn't exist | Stop. Ask user to confirm target name. Do not auto-create. |
| `status.json` missing | Stop. Recommend `target-init` in chat reply; do not proceed. |
| Time-box hit (15m wall-clock) | Write report with `incomplete: true`, list partial findings + open questions, stop. |
| Subagent emits prose instead of JSON | Re-issue once with "Output JSON only." appended. If still bad, mark that subquery as `blocking_unknown` and continue. |
| User asks something this skill can't answer (live HTTP needed) | Write a minimal report explaining what's needed; populate `## Recommended next actions` with the right skill (usually `browser-confirm` or `caido-replay`). |

## Why this skill exists

Investigation is the bridge between "pipeline output" and "user
action". Without it, every analyst question forks an unaudited
chat thread; with it, every question produces a cited, dated,
auditable record under the target. Same discipline as Clue: plan,
execute, cite, recommend — no shortcut from question to verdict.
