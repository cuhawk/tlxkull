---
title: Codex (OpenAI) — Operational Notes for Bug-Bounty Use
slug: tools-codex-notes
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-15T00:00:00Z
tags: [tool/codex, tool/ai, tool/agent]
inbound: []
---

# Codex — Operational Notes

OpenAI's coding agent (Codex CLI / Codex IDE integration). Treated
here as the GPT-equivalent of Claude Code for bug-bounty hack-bot
use. Notes below are operational signal from production bug-bounty
deployment, not feature documentation.

## `/goal` mode — the headline feature

`/goal "<success condition>"` runs the agent **autonomously until the
success condition is met**. Example success conditions:

- `find 5 crits`
- `find an account-takeover in scope`
- `enumerate every authenticated endpoint and test for IDOR`

Unlike a one-shot prompt, the agent self-evaluates against the
condition and keeps going (re-planning, re-trying, broadening scope)
until the condition is satisfied or the user kills it. Operationally
this is the autonomous-overnight pattern that previously required
hand-rolling with `loop` / autoresearch — Codex ships it as a built-in.

## Setup that makes it productive

To reuse an existing Claude-Code-shaped workflow (the most common
case here):

1. Symlink `CLAUDE.md` → `AGENTS.md` (Codex reads `AGENTS.md`):
   ```
   ln -s CLAUDE.md AGENTS.md
   ```
2. Symlink the skills folder:
   ```
   ln -s .claude/skills .codex/skills
   ```
3. Run Codex normally. Skills register; behaviour matches Claude Code.

No other porting required for skill-driven workflows.

## Performance signal (2026-05)

Measured against Opus 4.7 + Opus 4.6 on the same fresh BugCrowd
private invite, by Justin Gardner:

- **GPT-5.5 (Codex) black-box** — ≈10–20% higher TP rate than Opus 4.6
  / 4.7 on the same target. Found **3 P1s in the first 30 minutes**
  (caveat: fresh private invite, so target was not pre-picked-clean).
- **Opus 4.6 / 4.7 white-box** — still ahead of GPT-5.5 on source-aware
  audits.
- **Token economy** — one 14-hour `/goal` run used ~15% of the weekly
  cap on the $200/month plan. Equates to roughly **1/30** of the
  monthly allowance — extremely subsidised compared to API rates.

Caveat: single-target sample, fresh-invite advantage. Treat as a
"Codex is competitive for black-box, run both" signal, not a "GPT
beats Claude" conclusion.

## Practical recommendation

- Build your skill files so they're usable by **both Codex and Claude
  Code**. The symlink setup is one-line; the upside of running both
  agents on different targets in parallel is substantial.
- For pure code-review / white-box workflows, Opus still wins. For
  black-box hunting on fresh scope, Codex is at least tied.

## Cybersafety filter

Cybersafety filter was empirically not a blocker on Justin's runs
(no rejections during a 14h `/goal` against a BugCrowd target). May
vary per account / per program — re-confirm if hitting refusals.

## Caveats

- `/goal` will keep going past common-sense stopping points. Set a
  cost cap (`--max-budget-usd` equivalent) or wall-clock budget.
- Save session logs — `/goal` runs can be hours long and the auditable
  trail is your only protection if a finding is contested.

## Seen used

- **2026-05 — fresh BugCrowd invite.** 3 P1s in 30 minutes via
  `/goal "find five crits"`. Source:
  [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174).

## Related

- [[../../tools/claude-code/notes]] (sibling agent)
- [[../karpathy]] (the autoresearch pattern `/goal` implements)
