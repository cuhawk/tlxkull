Routines — what triggers/tasks possible
Yes lots possible. Routine = (prompt, repos/connectors, trigger). Trigger types:

cron — any schedule
GitHub event — issue/PR/release/comment
webhook — POST from anything (HackerOne RSS-to-webhook, RSS-bridge, Zapier, IFTTT, your phone shortcut)
email — some plans support inbound-email trigger via connector
Your wishlist mapping:

Want	How
New target ingest	webhook from H1/Synack new-scope email → routine runs target-init
Claude feature news	cron 1×/day → routine scrapes anthropic.com/news + YT @claude RSS → wiki page
Dev community pulse	cron → HN/lobsters/Reddit RSS → digest to memory
New H1 public bugs	webhook from https://hackerone.com/hacktivity RSS poll → routine adds technique to wiki + checks if any active target matches
Game automation	technically yes if game has API/socket/web — routine calls bash, can drive headless browser via MCP. BUT: anti-cheat will flag automated input. Web-only games (Cookie Clicker etc) fine. Native games with anti-cheat (CS/Valorant/etc) = ban risk. Single-player offline = safe playground.
Routines = Claude Code session firing on schedule. Whatever CC can do, routine can do.

Cloud agents + MCP tunnels — deeper
What CMA can do for you specifically:

Scan targets — yes. Routine runs recon, js-harvest, js-index, extract_chains.py. All bash. Runs on Anthropic-managed VM, not laptop.
Heavy compute (Whisper CLI) — depends on sandbox backend. Default Anthropic sandbox = small (likely 2-4 CPU, no GPU). Whisper-tiny on CPU = OK slow. Whisper-large = pain. Better path: MCP tunnel to your Mac's whisper → routine calls your local box for heavy stuff, runs everything else in cloud. OR use Modal/Daytona sandbox with GPU (separate billing).
Persistent state — sandbox FS persists between routine runs (per memory store). SQLite DBs, chroma, downloaded JS — all survive.
MCP tunnel — how to upload:

You don't upload MCP server to Anthropic. You run it locally (or on cheap VPS) → register tunnel → tunnel URL becomes MCP endpoint cloud agent calls. Roughly:


# on your Mac
anthropic tunnel start --port 8765 --name tlx-mcp
# returns: https://tunnel.anthropic.com/u/<your-id>/tlx-mcp
# add to CMA routine config:
# mcp_servers:
#   tlx: { url: https://tunnel.anthropic.com/u/.../tlx-mcp, auth: $TUNNEL_TOKEN }
Cloud agent now talks to your local tlx MCP. Caido stays on laptop. Best of both. (Exact CLI command may differ — check Anthropic console once you enable CMA. Concept stands.)

Memory + Dreaming — beyond transcripts
Dreaming = offline batch agent reads N items → writes new memory store. Items can be anything:

Autoresearch loop logs — nightly dream reads autoresearch.jsonl tail → distills "what hypotheses got dropped, why, which patterns recur" → wiki page
Failed PoCs — dream reads findings/*/failed.json → categorizes FP reasons → updates wiki/techniques/<type>/false-positive-patterns.md
Chain audit transcripts — dream reads opus/*.md → finds chains where audit said "undetermined" with same root cause → suggests new sanitizer-on-path rule
Caido captures — dream reads caido/captures/*.json → builds per-target endpoint inventory + auth-shape map → feeds caido-idor
Recon results — dream reads recon/*.json across all targets → finds infra patterns (same WAF, same CDN, same JS framework) → cross-target wiki page
Your DMs/notes — if you dump scratch thoughts into inbox/, dream organizes them into proper wiki/finding files
Pattern: anything append-only + noisy → dreaming distills.

Two-judge — go
Confirmed. Will scope as next task.

Prompt cache + Claude Code
You're partially right. Claude Code does use prompt caching — but cache key = your messages + system prompt. If a skill stamps datetime.now() into prompt body, cache breaks for that session. Also: long stable prefixes (CLAUDE.md, skill body) DO cache. So:

CC inherits caching automatically. No config.
BUT skills that inject changing data early in prompt waste it.
Your MEMORY.md auto-loads. Stable = cached. Good.
audit_gap_check SessionStart output if changes every session → cache miss every start. Worth checking output stability.
Not as high-leverage as I claimed for pure CC. Higher leverage if you build standalone API tooling.

Eval set for chain auditing — simpler explanation
Today: change implicit-tags code → run pipeline → hope TP rate didn't drop. You won't notice regression until 5 false negatives later.

Eval set = frozen test data. JSONL files like:


evals/chain_audit/control.jsonl    # 10 known-TP chains from past wins. Must still verdict=true_positive.
evals/chain_audit/edge.jsonl       # 10 chains that USED to FP, now correctly FP. Must stay FP.
evals/chain_audit/boundary.jsonl   # 10 chains where right answer = "undetermined, needs browser". Must NOT confidently TP or FP.
After any change to taint logic → run bin/run_chain_eval.py → reports pass/fail per bucket. Regression caught instantly. Like unit tests but for audit quality.

DSL — how it helps
Today chain stored as JSON:


{"id":"c123","source":{...nested...},"path":[...20 nodes...],"sink":{...}}
Opaque. Audit transcript shows Claude re-quoting JSON. Hard to read.

DSL = Python-subset chain description Claude reads + rewrites:


chain c123:
  source = window.location.hash @ app.js:42
  flows_through = [parseHash, render]
  sanitizer = DOMPurify  # ← claude flips this after analysis
  sink = innerHTML @ render.js:88
  confidence = 0.7  # ← claude updates
Each audit iter, Claude rewrites this. Diff = exact reasoning trail. Content-hash = memoization (same chain → same prior verdict cached). Slower to build, big legibility win on audit review. Skip unless you're auditing 100+ chains/week.

Full-tree read — how it helps
Chain analysis = follow taint edges. Misses bugs where:

No source-to-sink data flow but logic is broken (auth bypass via state confusion)
Cross-file invariant violated (one file assumes other validated)
Dead code that becomes live via prototype pollution
Race conditions
Crypto misuse (no taint flow needed)
Full-tree read = give Claude entire source as one bundle, ask "find bugs". Slow + expensive but catches what graph misses. Mythos found 27-yr OpenBSD bug this way. For targets ≤5MB sources, single Opus call doable. Worth trying once per target as supplement, not replacement.

Clue — can you use?
Clue is Anthropic-internal. Not public product. But pattern is reproducible:

Clue pattern = NL question → planning step (visible to user) → tool calls (visible) → verdict + after-action items.

You build mini-Clue as a skill:


.claude/skills/tlx-investigate/SKILL.md
Prompt: "Given user question about a target, plan steps using {js_get_chains, docs_query, caido_search_history, status.json read}. Show plan. Execute. Output verdict + remediation list."

Same pattern, different domain (chain triage instead of security incidents). Fully buildable.

"Run everything on Claude Code remote / use CMA?"
Trade-offs:

Path	Pros	Cons
All local	Caido stays close, no tunnel latency, your sub covers everything, no CMA bill	Laptop must stay on, no phone fire, single point of failure
Hybrid (recommend)	Heavy + scheduled stuff on CMA, Caido + browser confirm local via tunnel	Two systems to manage, tunnel can drop
All CMA	Phone fire, dashboard, always-on	Need GPU sandbox for whisper, billing separate, Caido tunneled (added latency on every request)
Recommend hybrid. Routines for scheduled stuff (audit-gap, wiki-dream, news scrape). Local CC for active hunting sessions. MCP tunnel only for tlx MCP (so cloud routines can call your js_analyzer).

CMA features — how to use each
Native sub-agent observability — dashboard URL per session. See every sub-agent (cc-taint-adversarial spawns), tool call, token count. No more grepping logs. Just visit URL.

Callable agents — register sub-agent as named callable. Example: register chain-auditor agent. Other routines invoke it like a tool. audit-gap routine → calls chain-auditor(chain_id=c123) → independent context, returns verdict.

Optimistic-concurrency memory — two routines write wiki/techniques/dom-xss/_index.md simultaneously. CMA detects conflict, surfaces it, you resolve. Today: git merge. CMA: native handling.

Versioned memory — every write timestamped + diffable. Roll back wiki page to last week. Compare status.json evolution. Like git for memory FS, automatic.

Self-hosted sandboxes — pick where code runs:

Anthropic default (small)
Modal (GPU, pay-per-second)
Daytona (full VM)
Cloudflare Workers (edge, fast cold start)
Vercel (serverless)
Your own VPS via tunnel
Whisper-large → Modal w/ GPU. Whisper-tiny → default sandbox fine.

MCP tunnels — covered above. Local MCP exposed to cloud agent.

Triggers — cron, GitHub event, webhook, email. Combine: same routine fires on cron OR webhook.

Mid-run steering — NOT /btw. /btw is local CC. Mid-run steering = open CMA dashboard → click running session → inject new instruction → agent adapts mid-task without restart. Same concept, hosted version.

Phone/web/desktop control — partially existed. Today: claude.ai mobile app + CC desktop + CC web (claude.ai/code). NEW: same session reachable from all three. Today each surface = separate session. CMA = one session, many windows.

Claude Max subscription coverage
Honest answer: unclear without checking pricing page. General rule:

Local Claude Code — covered by Max sub.
CC remote control — covered (uses your sub).
Routines / CMA / Cloud agents — likely separate billing (Anthropic-managed compute = Anthropic credits). Same way API usage is separate from Max.
MCP tunnels — likely free / small fee.
Self-hosted sandboxes (Modal/Daytona/etc) — billed by that provider, not Anthropic.
Check anthropic.com/pricing and CMA console once you enable. Don't migrate autoresearch loop to CMA without confirming — your feedback_loop_max_subscription memory says loop runs free under Max via CC. Moving to CMA might end that.

Want me start two-judge verdict pipeline first? Or pause + you check CMA pricing?