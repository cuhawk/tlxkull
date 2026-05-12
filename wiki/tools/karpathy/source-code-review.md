---
title: Source Code Review Methodology
slug: source-code-review
created_utc: 2026-05-12T00:00:00Z
updated_utc: 2026-05-12T00:00:00Z
tags: [tool/karpathy, methodology, source-code-review]
inbound: []
---

# Source Code Review Methodology

Meta-analysis distilled from CT Ep. 172. Synthesis of multiple expert sources
(SL Cyber / Shubs, industry write-ups, practitioner notes).

## Three root causes of all bugs (abstract model)

Every code-audit finding reduces to one of:

1. **Tracing data flow better than the developer** — the developer does not
   realize they are operating on attacker-controlled data at a particular point
   in the pipeline. Classic: zip → extract → XML attribute → shell command;
   developer never connected the upload to the shell-out.

2. **Knowing the nuances of the sink context better than the developer** —
   the developer thinks their transformation is safe. Classic: `Path.Combine`
   where a second absolute-path argument silently discards the first; XXE where
   the developer did not know XML parsers can make HTTP requests; SQL injection
   where parameterization was missed in one of 500 query sites.

3. **Forgotten security control** — auth check, sanitization, or rate limit
   is simply absent or applied inconsistently.

Use this model during mapping: tag each interesting code path with which of the
three it might represent.

## Phase 1 — Obtain source

Priority order:
1. Open-source repository (GitHub).
2. npm / pip / Maven package (may differ from GitHub — always check both).
3. Shipped sourcemaps (`.js.map` files — check Claude Code's own release; they
   included map files).
4. Docker images / cloud marketplace images (extract filesystem).
5. Decompilation: `uncompyle` for Python bytecode; `jadx` / `cfr` for JARs;
   Ghidra + Claude Code MCP for binaries.
6. Pay a developer on Fiverr to set up the stack and get shell access to pull
   the code (~$200; cheaper than days of failed local setup).

## Phase 2 — Set up local environment + debugger

Use AI to handle environment setup — the biggest time sink before AI. Once
running, **attach a debugger**. Setting a breakpoint and inspecting live
variable state is dramatically more valuable than reading static code.

## Phase 3 — Map the attack surface

Before hunting bugs, understand the architecture:
- Feed build files (Makefile, `docker-compose.yml`, `package.json` scripts,
  `requirements.txt`) to Claude and ask for a component map.
- Enumerate all exposed interfaces: HTTP routes, gRPC services, WebSocket
  handlers, message queue consumers.
- Check reverse proxy config (nginx, Caddy, HAProxy) — this defines the actual
  attack surface, not the back-end router alone. Items explicitly blocked by
  the proxy may be accessible from adjacent services.
- Check middleware chain: where is auth enforced? Is the decorator applied
  holistically or per-route? Missing middleware on one route = gadget.
- Do not skip boring-looking routes. Justin's Grafana SSRF (2020) lived in
  the avatar endpoint — unauthenticated, overlooked by most auditors.
- Use `hyōketsu` (hykotsu) to fingerprint known open-source JARs/libraries in
  the codebase so you spend time only on custom code.

## Phase 4 — Hunt ("sniffing for blood")

**Core heuristic: complexity × capability**

Look for where user input enters a **complex environment** with high
capability to escape into dangerous operations:

| Sink context | Why complex | Capability |
|---|---|---|
| SQL / database string | syntax, encodings, string delimiters | read/write/execute DB |
| Shell command string | metacharacters, quoting, env variables | OS RCE |
| XML / XXE parser | entity expansion, DTD, external refs | SSRF, file read |
| URL composition | `?`, `#`, `@`, scheme, path traversal | SSRF, open-redirect |
| Configuration file | INI/YAML/TOML syntax, includes | arbitrary config injection |
| Template engine | expression syntax, filters, macros | SSTI / RCE |
| Dynamic code eval | JS `eval`, Python `exec`, XSLT, Rhino, Jel | code execution |
| Protobuf / binary protocol | field offsets, length prefixes | type confusion |
| JSON string concatenation | quote escaping, nesting | JSON injection |

**Path traversal in SDKs:** SDK methods that accept a `userId`, `filePath`, or
`resourceId` and interpolate it directly into a URL path — `../../org` or
`../../admin` can traverse to a different resource class.

**Config file injection:** underrated; many config languages have include/exec
semantics that developers ignore.

**`Path.Combine` (C#) absolute-path injection:** second argument overrides
the first if it is an absolute path. Developers assume it prepends a safe base
directory.

**Dynamic evaluation sinks:** XSLT, Rhino script, Jel (JetBrains Expression
Language), EL (Jakarta EE) — alarm should fire whenever input lands here.

## Phase 5 — AI-assisted workflow tips

- Map phase: "given these build files and these route definitions, draw me a
  component diagram showing all external interfaces".
- Ghidra + Claude Code MCP: connect Claude directly to Ghidra for binary
  analysis — highly effective even if you are not a reverse engineering expert.
- Ask specifically: "find all locations where a user-controlled parameter is
  interpolated into a URL path, shell command, or file path without
  sanitization."
- Context injection: feed entire technique write-ups (like this file) to prime
  the model before asking it to audit a module.

## Sources

- CT Ep. 172: `../../sources/podcasts/ct/20260430_t1O7ul7Vey0_Source_Code_Review_Meta_Analysis_Ep.172.en.vtt`
- Podcast: "Source Code Review Meta Analysis (Ep. 172)" — <https://www.youtube.com/watch?v=t1O7ul7Vey0>
- YesWeHack open-source security testing guide (linked in episode description)
- SL Cyber writeups (Shubs) — `Path.Combine` traversal, XSLT / Rhino sinks
