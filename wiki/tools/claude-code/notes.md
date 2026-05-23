---
title: Claude Code — Operational Gotchas + Skill-Authoring Notes
slug: tools-claude-code-notes
created_utc: 2026-05-15T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [tool/claude-code, tool/ai, tool/agent]
inbound: []
---

# Claude Code — Operational Gotchas

Selective notes about Claude Code itself — pitfalls that are not
obvious from docs but affect every hack-bot setup that uses skills.

## Skill-frontmatter pitfalls (high-impact)

### `description:` is single-line by default

Markdown / YAML frontmatter does **not** treat `description: ...`
as a multi-line block. Anything you write on subsequent lines is
silently ignored by the Claude / Codex agent loaders. Only the first
line reaches the dispatch decision.

**Wrong** (only the first line is sent to the agent):

```yaml
description: This skill checks for IDOR.
  It walks every authenticated endpoint
  and replays each request with another user's cookie.
```

**Wrong** (some Markdown variants accept this, Claude Code does not):

```yaml
description: >
  This skill checks for IDOR.
  It walks every authenticated endpoint.
```

**Right** — block scalar with `>-`:

```yaml
description: >-
  This skill checks for IDOR.
  It walks every authenticated endpoint and replays each request
  with another user's cookie to surface broken-access-control.
```

The `>-` form is parsed correctly and the **entire description** is
passed to the agent's skill-dispatch prompt. Confirmed to massively
improve invocation accuracy on existing skills that had been silently
truncated.

### `snake_case` skill names invoke better than `camelCase`

Empirically (not documented) the agent matches skill names to the
user's request more reliably when the skill `name:` is `snake_case`.
Rename `myCoolSkill` → `my_cool_skill` if you're seeing low
invocation rate.

### The word `Claude` in a skill name is a poison pill

Skills with the word `Claude` (or `claude`) in the `name:` field
underperform — possibly tokenizer / reserved-token interference,
possibly a deliberate filter to prevent recursive self-reference.
Rename:

- `dm_other_claudes` → `dm_other_agents`
- `claude_bridge` → `agent_bridge`

Measured improvement in invocation rate after rename (rezo, CT Ep. 174).

## Training-data opt-out is per-machine / per-install

Disabling "use my data to improve Claude" on the web/console UI does
**not** automatically propagate to a Claude Code install on a fresh
VPS, container, or new dev machine. The setting lives in a local
config file that is created per install. If you scale Claude Code
across machines (CI runners, hack-bot fleet), audit the opt-out on
**every** machine.

**Organization-licensed accounts** are automatically excluded from
training data — preferred posture for hunters who don't want their
hack-bot sessions used as training data.

## `--print` / Agent SDK billing change (2026-05)

Anthropic announced that programmatic Claude Code usage (`-p` /
`--print` flag, Agent SDK calls) is **no longer covered by the
subscription's subsidised token bucket** (the ~$4000/mo equivalent on
the $200 plan). Subscribers instead get a separate ~$200 of API
credits earmarked for programmatic mode — much smaller than the
subsidised bucket they used to draw from.

Impact for hackbot operators: any harness built on `claude -p ...` or
the Agent SDK either burns the new $200 quota fast or pays API rates.
Anthropic's stated motivation (per Johann Rehberger's framing on CT
Ep. 175) is to stop businesses reselling subsidised tokens as a
service via `-p` — the personal-hackbot use case is collateral.

### Workaround — PTY harness driving the interactive TUI

Subscription tokens **still cover** normal interactive use. Drive the
TUI from a pseudo-terminal and write messages directly into stdin:

- Use `--resume` / `-r` instead of `-p` to keep a long-running session
  that you re-attach to programmatically.
- Wrap in a PTY harness (`pty.openpty()` + write to the master fd).
  Claude's normal UI renders into the slave end; you read its output
  and write replies back.
- Combine with `--remote-control` to expose the session over the
  cloud / claude.ai/code so a phone client can drive it.

Justin's hackbot + rezo's setup both use this pattern post-billing-
change. No observed quality difference vs `-p`; same model on the
backend.

Caveat: editing requests through a proxy *would* be a TOS-grey
workaround (intercepting + flipping an `interactive=true` flag at the
API layer) — Justin draws the line at "using the app via the TUI we
were given is fine; mutating their wire protocol is gray-hat". Keep
your harness in the "we just type into the TUI" lane.

## Stop-hook → re-prompt loop (continuous hack-bot)

Simpler alternative to the Ralph loop / Codex `/goal` for keep-
running-forever behaviour:

1. Register Claude Code's **stop hook** (config file under
   `~/.claude/...`). Fires whenever Claude naturally stops the turn.
2. The hook grabs the session's PTY fd and writes a continuation
   message into it ("don't stop, keep going. you have more work.").
3. Claude reads the new input and resumes.

Pros: no external orchestrator, no token overhead from a wrapper
agent, survives long autonomous runs.

Cons:

- On tight-scope targets Claude will sometimes respond "I've done
  everything, I'm just going to wait" and re-stop immediately. Stop-
  hook fires again, loop continues, but the agent isn't making
  progress — needs a watchdog that detects N consecutive "done" stops
  and re-tasks with a new direction.
- No upper bound on tokens spent — pair with a wall-clock budget.

## Source

- [CT Ep. 174](wiki://podcasts/ct/20260514_qi4dGzjDPI8_Saving_Bug_Bounty_Programs_+_AMPScript_tessl_GPT-5.5_Ep._174)
  — frontmatter / naming / training-data gotchas (rezo + Justin
  Gardner).
- [CT Ep. 175](wiki://podcasts/ct/20260521_v-XhQHy_jHM_Rhyno_s_Hackbot_Setup_Sick_Bugs_and_ZDI_Drama_Ep._175)
  — `--print` billing change + PTY workaround + stop-hook continuous-
  loop pattern (Justin Gardner + Joel Margolis).

## Related

- [[../codex/notes]] — sibling agent, mostly compatible skill format
