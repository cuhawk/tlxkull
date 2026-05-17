# plans/

Design + build specs for the TLX workspace. Self-contained — each plan
should be readable cold by a new Claude Code session.

## Index

| File | What |
| --- | --- |
| [PLAN.md](PLAN.md) | Top-level workspace plan. Loaded first per `CLAUDE.md`. |
| [CC_TAINT_ADVERSARIAL.md](CC_TAINT_ADVERSARIAL.md) | Build plan for the Claude-Code-driven adversarial taint-audit pipeline (replaces `opus-deep-audit` on quality-first engagements). |
| [IMPL_TIER123.md](IMPL_TIER123.md) | Tier 1/2/3 implementation roadmap for the broader TLX feature set. |
| [PIPELINE_PERF_PROMPT.md](PIPELINE_PERF_PROMPT.md) | Performance audit prompt for the existing js_analyzer pipeline. |
| [SETUP.md](SETUP.md) | One-time setup notes for the workspace. |
| [USE_CASES.md](USE_CASES.md) | Target use-case catalog the pipelines must handle. |

## Conventions

- New plans land here, not at repo root.
- File names use `SCREAMING_SNAKE_CASE.md` so they're obvious in `ls`.
- Each plan has a "kickoff command" section near the end so a fresh
  session can be told what to paste to start.
- Done? Move plan to `plans/done/<file>` and add a one-line completion
  note at the top with date + commit SHA.
