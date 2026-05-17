# Remote Claude Code Web — Target Data Sharing

> **Audience:** A fresh Claude Code session, possibly Claude Code Web,
> that needs to know whether and how it can do real engagement work on
> this repo without the user's local environment.

## 1. Problem

User wants to run static-analysis phases of bug-bounty engagements from
Claude Code Web (claude.ai/code) while away from the local machine:

1. Open Claude Code Web pointed at this GitHub repo.
2. Give it a target name.
3. Have it run the heavy CC-subagent work (e.g. `cc-taint-adversarial`).
4. Commit results back to the branch.
5. Locally `git fetch` and finish runtime confirmation.

Today this won't work. Reasons:

- `targets/*` is gitignored ([.gitignore:14](../.gitignore#L14)). Per-engagement
  artifacts never reach GitHub.
- The `tlx` MCP server depends on `~/.tlx/js_analyzer.db` and
  `~/.tlx/chroma/` on the user's machine. Remote CC has no such state.
- Caido + chrome-devtools MCPs require local services (Caido daemon,
  real Chrome with extensions). Not relevant to static phases, but
  any skill that touches them silently won't work remote.
- `mock_backend` (mock_run / mock_extract) is a local FastAPI process.

The fix is to make the **static portion** of an engagement
self-contained inside the repo so a remote CC session can read it from
git, run CC-driven analysis, and write results back. The runtime
portion stays strictly local.

## 2. What we will NOT change

These constraints are accepted as permanent. The plan works around them.

1. **No live target traffic from remote CC.** Browser-confirm, Caido
   replay, mock_run all stay local. Remote does static only.
2. **No auth secrets in the repo.** `http.md`, `findings/`, anything
   referencing creds — remain local-only.
3. **No `~/.tlx/` syncing.** That dir is workstation-personal.
   Remote uses the per-target snapshot already required by CLAUDE.md.
4. **No live API keys in the repo.** ANTHROPIC_API_KEY / GOOGLE_API_KEY
   stay in local `.env`. Remote CC runs as the seat user; it doesn't
   need them per the API-key whitelist.

## 3. What changes

Three buckets of changes.

### A. Gitignore — opt-in target sharing

Edit `.gitignore`:

```
# Per-engagement target dirs (scope, artifacts, findings — all local-only by default)
targets/*
!targets/_TEMPLATE_http.md

# Opt-in: if a target dir contains a marker file named .remote-shareable,
# the explicitly-shareable subset below is allowed through.
!targets/*/.remote-shareable
!targets/*/db/
!targets/*/db/**
!targets/*/index/
!targets/*/index/**
!targets/*/chains/
!targets/*/chains/**
!targets/*/sources/
!targets/*/sources/**
!targets/*/opus/
!targets/*/opus/**
!targets/*/status.json
```

Hard rule: **the un-ignore patterns only take effect when the target dir
contains a `.remote-shareable` file**. If the marker is missing, all
subpaths stay ignored. Implementation:

- Add a pre-commit hook (`.githooks/pre-commit-target-share-guard`) that
  rejects any `git add targets/<name>/{db,index,chains,sources,opus,status.json}`
  when `targets/<name>/.remote-shareable` is absent.
- Set up via `git config core.hooksPath .githooks` on every clone (add
  to SETUP.md).

Rationale: gitignore alone is fragile (negation patterns can leak). The
hook is the actual safety gate.

**Never shareable, even with marker:**
- `targets/*/http.md` (scope + auth references)
- `targets/*/raw/` (raw downloaded JS — may be license-restricted)
- `targets/*/findings/` (PoCs, possibly with creds in headers)
- `targets/*/caido/` (replay captures, contains tokens)
- `targets/*/runtime/` (passive-listen dumps, contains live request bodies)

Add explicit nested ignores:
```
targets/*/http.md
targets/*/raw/
targets/*/findings/
targets/*/caido/
targets/*/runtime/
```

These take priority over the un-ignore. Verify with
`git check-ignore -v targets/<name>/raw/foo.js`.

### B. Bin-script refactor — read from per-target snapshot, not global DB

CLAUDE.md already requires per-target DB isolation. Audit every bin
script that touches `~/.tlx/`. They must accept `--db
targets/<name>/db/js_analyzer.db` and `--chroma targets/<name>/db/chroma`
explicitly. Default-to-global is a latent remote-break.

Scripts to audit:
- `bin/db-isolate.py` (already snapshot-aware — verify)
- `bin/export_index.py` (already takes `--db` — verify)
- `bin/extract_chains.py` (already per-target — verify)
- Anything in [bin/](../bin/) that imports `tlx.modules.js_analyzer.db` —
  grep + audit.

Add a smoke test: with `~/.tlx/` renamed away, every script in the bin
chain still runs given `--db` + `--chroma` pointing at a target dir.

### C. cc-taint-adversarial — remote-runnable design

The plan in [CC_TAINT_ADVERSARIAL.md](CC_TAINT_ADVERSARIAL.md) is already
mostly remote-friendly because it uses CC subagents (no `tlx` MCP
required for the audit step). Confirm + harden:

- Step 1 `bin/expand_snippet.py`: reads sqlite + filesystem only. No
  MCP. Remote-OK if `targets/<name>/db/` is present.
- Step 2 `bin/bucket_anomaly.py`: dispatches CC subagent via the
  `Agent` tool. No MCP. Remote-OK.
- Step 3 adversarial skill: dispatches CC subagent. Subagent prompt
  must not depend on `mcp__tlx__*` tools.
  **If it does, restructure** so the subagent reads
  `chains/expanded/<id>.json` directly via `Read` instead of calling
  `mcp__tlx__js_get_snippet`.
- Step 4 `bin/cc_taint_route.py`: filesystem only. Remote-OK.
- Step 5 runtime wiring: stays local.

## 4. Async workflow

```
LOCAL  (user's workstation)
  1. target-init → js-harvest → sourcemap-explode → rag-ingest
  2. js-index → db-isolate snapshot → extract_chains
  3. chain-triage → dom-xss-hunt
  4. touch targets/<name>/.remote-shareable
  5. git add targets/<name>/{db,index,chains,sources,status.json,.remote-shareable}
     git commit -m "share: <name> static prereqs"
     git push

REMOTE (Claude Code Web)
  6. git pull
  7. /cc-taint-adversarial <name>
  8. git add targets/<name>/opus/
     git commit -m "adversarial audit: <name>"
     git push

LOCAL
  9. git fetch + merge
 10. /browser-confirm <name>  (live Chrome + Caido)
 11. /report-finding <name>
```

Failure modes:
- Remote tries to run a skill that hits `mcp__tlx__*` → fail fast with
  clear error. Don't silently fall back.
- Remote tries to run a skill that hits `chrome-devtools` /
  `mcp__caido__*` / `mock_*` → same.
- Merge conflict on `opus/` if local also ran the same chain in
  parallel → prefer remote's verdict, archive local under
  `opus/_conflicts/`.

## 5. Risks + mitigations

| Risk | Mitigation |
| --- | --- |
| Auth refs leak via target dir | Hard-ignore `http.md`, `findings/`, `caido/`, `runtime/`. Pre-commit hook enforces. |
| Decompiled JS license issue (`raw/` or `sources/`) | `raw/` always ignored. `sources/` only shared if user opts in per-target via `.remote-shareable`. For closed-source targets, **don't** share `sources/`. |
| Chroma collection size (100s of MB) | Use git-lfs for `targets/*/db/chroma/`. Add `.gitattributes` entry. Reconsider per-target — small targets fine without LFS. |
| Public repo exposure | This whole flow assumes a **private** GitHub repo. Document loudly in SETUP.md. Add a `repo-is-public` check in the pre-commit hook that fails the commit if the remote is detected as public. |
| Drift between remote opus output and local state | Track `status.json.phases.cc_taint_adversarial.commit_sha` so we know which DB snapshot the verdicts came from. If local snapshot changed, force re-audit. |
| API-key whitelist violation | Remote CC runs as user's CC seat — no `ANTHROPIC_API_KEY` use. Confirms whitelist. But if a refactor accidentally adds `anthropic.Anthropic(...)` it'd run remote too. CI test: grep for forbidden imports outside `tlx/modules/js_analyzer/`. |

## 6. Alternative: target data in a submodule

If the user doesn't want target data inside the main repo at all:

- Create a separate private repo `tlx-targets-private`.
- Add as submodule at `targets/`.
- Remote CC fetches the submodule (needs deploy key configured in
  Claude Code Web's repo settings).
- Submodule has its own `.gitignore` matching the rules above.

Pros: cleaner separation, public main repo possible.
Cons: more git plumbing, submodule pinning friction.

Decision deferred — user choice.

## 7. Build steps

Tackle in order.

### Step 1 — Lock down gitignore + hook

**Files:**
- Edit [.gitignore](../.gitignore) per §3A.
- Create `.githooks/pre-commit-target-share-guard` (bash script).
- Update [plans/SETUP.md](SETUP.md) with one-time
  `git config core.hooksPath .githooks` instruction.

**Verification:**
```bash
# Without marker — should fail
mkdir -p targets/_smoke && touch targets/_smoke/db/x
git add targets/_smoke/db/x  # expect: hook rejects

# With marker — should succeed
touch targets/_smoke/.remote-shareable
git add targets/_smoke/.remote-shareable targets/_smoke/db/x  # expect: OK

# Cleanup
git rm --cached -r targets/_smoke && rm -rf targets/_smoke
```

### Step 2 — Bin-script per-target audit

**Files:** every script in `bin/` that touches the global DB.

**Approach:**
1. `grep -rn "~/.tlx" bin/ tlx/modules/ | grep -v test`
2. For each match: confirm it takes `--db` + `--chroma` explicitly OR
   defaults to per-target snapshot resolved from `--target`.
3. Add `--no-fallback` flag (default true) so scripts hard-fail if
   `--db` is missing instead of silently using global.

**Verification:**
```bash
mv ~/.tlx ~/.tlx.bak
# Run each bin script with --target <name> --db ... --chroma ...
# All should succeed without ~/.tlx
mv ~/.tlx.bak ~/.tlx
```

### Step 3 — Pre-commit hook for public-repo guard

**File:** `.githooks/pre-commit-public-repo-guard`

**Scope:**
- Parses `git remote get-url origin`.
- If the URL is github.com/* and `gh repo view --json visibility -q .visibility` returns `PUBLIC`, fail any commit that touches `targets/`.
- Skip the check if `TLX_ALLOW_PUBLIC_TARGET_DATA=1` env is set (escape hatch for non-bounty open-source demos).

**Verification:**
- Point a test branch at a known-public repo, attempt to commit a
  target dir, expect rejection.

### Step 4 — Remote workflow doc + kickoff message

**File:** [plans/REMOTE_CC_KICKOFF.md](REMOTE_CC_KICKOFF.md)

**Content:** the async workflow from §4 as a step-by-step the user can
paste into Claude Code Web to bootstrap a remote session.

### Step 5 — Smoke test end-to-end

Pick a non-sensitive target, run the full local → push → remote → pull
loop. Confirm:
- `targets/<name>/opus/*.json` shows up on remote branch
- `targets/<name>/raw/`, `http.md`, `findings/` did NOT push
- Locally, `git pull` brings the opus dir down
- Local `browser-confirm` picks it up cleanly

## 8. Out of scope

- Real-time collaboration between local + remote on the same target.
  Use branch-per-engagement to serialize.
- Auto-sync of `~/.tlx/` DB. The per-target snapshot already covers
  what's needed; global DB syncing would re-introduce contamination
  per CLAUDE.md isolation rule.
- Cloud Caido instance. User's Caido stays local; remote can't replay.
- Cloud Chrome with extensions. Browser-confirm stays local.

## 9. Kickoff command for the new session

Paste this into a fresh Claude Code (local) session:

```
Read plans/REMOTE_CC_TARGET_DATA.md end-to-end, then plans/CC_TAINT_ADVERSARIAL.md, then CLAUDE.md. Start at Step 1 (gitignore + pre-commit hook). Each step has a verification gate — do not skip past a failed check. Confirm with me before pushing any target data to a public remote.
```

## 10. References

- Main pipeline plan: [CC_TAINT_ADVERSARIAL.md](CC_TAINT_ADVERSARIAL.md)
- Workspace rules: [../CLAUDE.md](../CLAUDE.md)
- DB isolation rule: [../CLAUDE.md](../CLAUDE.md) §"Per-target DB isolation"
- API-key whitelist: `~/.claude/projects/-Users-soural-Documents-TLX/memory/feedback_api_key_whitelist.md`
- Current gitignore: [../.gitignore](../.gitignore)
