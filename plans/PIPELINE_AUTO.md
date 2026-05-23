# Pipeline Auto — branched per-scope-entry driver

Goal: one entry point that takes `targets/<name>/http.md` after `target-init`
and dispatches every scope entry to the right lane, then halts the whole
target at the audit boundary so the user (or a dedicated trigger) decides
when to spend Opus/Sonnet budget.

Driver lives at `bin/pipeline_run.py`. Lanes are independent and run in
parallel where the per-lane subprocess is safe to background.

---

## Scope entry classification

Each `in:` line under `## Scope` in `http.md` is classified once:

| Pattern                                         | Lane         |
|-------------------------------------------------|--------------|
| `https?://host[/...]` or bare host with no `*` | `url`        |
| `*.apex.tld` or bare apex `apex.tld` (auto-promoted) | `wildcard`   |
| `A.B.C.D`, `A.B.C.D/NN`, or `A.B.C.D - E.F.G.H` | `ip_cidr`    |

Classification result is persisted to
`targets/<name>/status.json.scope_classified = [{"entry": "...", "lane": "url|wildcard|ip_cidr"}]`
so it can be inspected without re-parsing.

`out:` lines are loaded into a deny-list every lane consults before any
network call.

---

## Lane A — `url` (website)

Goal: produce indexed chains ready for adversarial audit, then stop.

```
js-harvest        ← scope already has the host
sourcemap-explode ← only if .map files were recovered
rag-ingest        ← writes target_<name> chroma collection
js-index          ← MCP js_index_target
db-isolate        ← per-target snapshot DBs (REQUIRED per CLAUDE.md)
implicit-tags     ← closure-expand tags
async-edges       ← handler-body interprocedural
browser-context-infer
chain-bestfirst (preferred) or extract_chains_bounded
sanitizer-on-path
chain-triage      ← writes chains/hot.jsonl
dom-xss-hunt      ← writes chains/dom_reachable.jsonl
─────── PAUSE BOUNDARY ───────
write targets/<name>/_audit_queue.jsonl
status.json.phase = "ready_for_audit"
```

The pause boundary is enforced by the driver: it never invokes
`opus-deep-audit`, `cc-taint-adversarial`, `opus-gap-audit`, or
`autoresearch-loop`. Those remain explicit user actions.

`_audit_queue.jsonl` rows:

```json
{"target": "<name>", "lane": "url", "chains_file": "chains/dom_reachable.jsonl", "n_chains": 42, "ready_utc": "...", "next": "/cc-taint-adversarial <name>"}
```

---

## Lane B — `wildcard`

Goal: turn `*.apex.tld` into a list of live web hosts, then for each one
spawn a `url` lane sub-run.

```
subdomain enum    ← recon MCP (subfinder + amass + crt.sh + Shodan scrape)
resolve A/AAAA    ← dnsx
masscan_run       ← top-web ports {80,443,8080,8443,8000,8888,7443,9443}
httpx             ← banner + tech + title; writes live_web.jsonl
per live_web host with JS detected (Wappalyzer hits / Server: header / content-type):
    spawn url-lane(host)  ← serial-by-host, parallel across hosts up to N
─────── PAUSE BOUNDARY ───────
```

`masscan_run` against resolved subdomain IPs is the rate-bounded step; cap
at `memory.md > masscan_rate_pps` (default 5000) and warn if the resolved
IP set crosses `memory.md > masscan_max_ips` (default 50000).

Subdomain enum reuses the existing `recon` MCP, not a new code path.

Live-web detection threshold: response on any web port AND
`content-type: text/html` OR a `<script>` tag in the first 64 KiB. Hosts
without JS get logged to `_no_js_hosts.jsonl` and skipped — there is no
JS pipeline to run on them.

---

## Lane C — `ip_cidr`

Goal: identical to lane B from `masscan_run` onward; skips subdomain enum.

```
ip expansion       ← bin/scope_expand_ips.py output already exists
masscan_run        ← same port profile as lane B
httpx              ← live_web.jsonl
per live_web host with JS detected:
    spawn url-lane(host)  ← host = IP here, virtual-host probing optional
─────── PAUSE BOUNDARY ───────
```

For raw IPs there is no Host header guess; httpx is invoked with
`-no-fallback-scheme` and the IP itself. If banner advertises a vhost,
the vhost is recorded but the url-lane still keys on the IP literal
unless the user opts in to vhost-rewrite (cli flag, off by default).

---

## Shared scaffolding (new files)

| File                                | Purpose                                                                                  |
|-------------------------------------|------------------------------------------------------------------------------------------|
| `bin/pipeline_run.py`               | Driver: classify scope, fan out lanes, write status, write audit queue.                  |
| `bin/masscan_run.py`                | masscan wrapper. Two modes: `local` (host masscan) and `droplet` (DO ephemeral).         |
| `bin/wildcard_enum.py`              | Subfinder + crt.sh + amass passive + resolve. Wraps recon MCP where possible.            |
| `bin/httpx_probe.py`                | httpx wrapper. Emits `live_web.jsonl` with JS-presence flag.                             |
| `bin/audit_queue.py`                | Append + dedup helper for `_audit_queue.jsonl`. Used by every lane at pause boundary.    |
| `.claude/skills/pipeline-auto/SKILL.md` | Skill front-door — single-command pipeline kickoff.                                  |

---

## Pause boundary contract

Every lane MUST stop after `dom-xss-hunt` (lane A) or after spawning all
sub-lanes (lanes B/C). The driver:

1. Writes `targets/<name>/_audit_queue.jsonl` listing every chains file
   ready for human-triggered audit.
2. Sets `status.json.phase = "ready_for_audit"`.
3. Prints a one-line summary per lane.
4. Exits 0.

Audit invocation stays user-driven via `/cc-taint-adversarial <name>` or
`/opus-deep-audit <name>`. No skill autospawns them.

---

## Concurrency + safety

- Per-target max parallel lanes = `min(cpu/2, 4)`, override via
  `--max-parallel`.
- Masscan runs at most once per target until completed; second invocation
  resumes from saved state.
- Every lane writes a heartbeat to `status.json.phases.<lane>.heartbeat_utc`
  every 30 s so a crash is visible.
- The driver respects `out:` deny-list at every HTTP/scan step.
- `--dry-run` prints the classified scope and the lane each entry would
  trigger, then exits.

---

## Resume semantics

Re-running `bin/pipeline_run.py <name>` on a half-done target:

- Reads `status.json.phases.*`; any phase with `status == "done"` is
  skipped.
- A phase with `status == "running"` older than 10 min without a
  heartbeat is considered crashed; the driver re-runs it.
- A phase with `status == "ready_for_audit"` halts — driver exits with
  message "already at audit boundary; run audit skill or pass --resume-past-audit".

---

## Open questions (defer to runtime / user)

1. **masscan host**: local laptop vs DO droplet. Default local for ≤50k
   IPs, droplet beyond. Override via `--masscan-mode {local,droplet}`.
2. **httpx tech-fingerprint depth**: cheap (`-tech-detect`) vs full
   Wappalyzer. Default cheap; flip via `--httpx-deep`.
3. **vhost expansion on IP/CIDR lane**: off by default.
4. **port profile**: web-only is the default. Full-65k requires
   `--ports full` and emits a confirmation prompt.
