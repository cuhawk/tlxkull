# taintview — BloodHound-style DOM Taint Chain Viewer

**Status:** Draft
**Date:** 2026-05-13
**Owner:** soural
**Related:** [chain-triage](../../../.claude/skills/chain-triage), [dom-xss-hunt](../../../.claude/skills/dom-xss-hunt), [opus-deep-audit](../../../.claude/skills/opus-deep-audit)

## Problem

The TLX pipeline produces JSONL files describing JS taint chains
(`targets/<name>/chains/{all,hot,dom_reachable,dom_unreachable}.jsonl`)
and per-chain Opus verdicts (`targets/<name>/opus/<id>.md`). Today,
reasoning about why a candidate is hot or false-positive means reading
JSONL by hand and grepping qnames across files. There is no visual
representation of how sources flow into sinks, no way to see which
intermediate functions act as taint hubs, and no quick way to inspect
the source snippet for a node without running the MCP CLI.

## Goals

1. Browse every chain in a target as an interactive node-link graph.
2. See, at a glance, which functions are taint hubs (high fan-in/out across chains).
3. Animate taint propagation along a selected chain, source → sink, the
   way BloodHound animates an attack path.
4. Inspect a node's source code on demand without leaving the UI.
5. Read Opus verdict text inline next to the chain it concerns.
6. Allow the operator to write a manual verdict (TP / FP / undet + note)
   back to disk so subsequent runs see it.

## Non-goals

- Editing the graph (adding/removing nodes/edges).
- Running TLX skills from the UI (no "rerun audit" button).
- Multi-target merged view. One target loaded at a time.
- Authentication. Localhost-only single-user tool.
- Mobile / responsive layout. Desktop browser only.

## Users

Single operator (soural). Bug-bounty hunter triaging DOM-XSS candidates
on one target at a time. Heavy keyboard user; expects fast filtering
and snippet inspection.

## Architecture

Two processes, both started by one CLI entrypoint:

```
+-------------------------+        +----------------------------+
|  Browser (Cytoscape SPA)| <----> |  FastAPI sidecar (Python)  |
|  http://localhost:8765/ |  HTTP  |  bin/taintview_server.py   |
+-------------------------+        +----------------------------+
                                              |
                                              | stdio (existing pattern)
                                              v
                                   +----------------------------+
                                   |  tlx MCP server            |
                                   |  (js_get_snippet,          |
                                   |   js_examine_chain)        |
                                   +----------------------------+
```

### Component A — SPA (`tools/taintview/`)

- Vite + React + TypeScript.
- Cytoscape.js for the graph (cose-bilkent layout for force-direction,
  dagre layout as an alternate "linear flow" view).
- Tailwind for styles (no design system; minimal dark theme).
- Build output checked into `tools/taintview/dist/` so the sidecar can
  serve it without a node toolchain at runtime.

#### Layout

```
+--------------------------------------------------------------+
| Header: target name | chain count | "Reload" | layout switch |
+----------+--------------------------------+------------------+
| Filters  |                                |  Node detail     |
| (left)   |        Graph canvas            |  (right)         |
|          |                                |                  |
|  source  |                                |  qname           |
|  taxon.  |                                |  file:line       |
|  ☑ url_  |                                |  taxonomy        |
|    query |                                |  --- snippet --- |
|  ☑ ...   |                                |  [code]          |
|          |                                |                  |
|  sink    |                                |  --- opus ---    |
|  taxon.  |                                |  [verdict text]  |
|  ☐ ...   |                                |                  |
|          |                                |  --- verdict --- |
|  score   |                                |  [TP][FP][undet] |
|  >= 70   |                                |  note: ____      |
|          |                                |                  |
|  depth   |                                |                  |
|  <= 6    |                                |                  |
|          |                                |                  |
|  verdict |                                |                  |
|  ☑ TP    |                                |                  |
|  ☑ FP    |                                |                  |
|  ☑ undet |                                |                  |
|  ☑ none  |                                |                  |
+----------+--------------------------------+------------------+
| Chain table (bottom dock, resizable)                         |
| id | src tax | sink tax | depth | score | verdict | reach    |
| 103| location_search | bypassSec... | 2 | 85 | FP | unreach |
| 158| ...                                                     |
+--------------------------------------------------------------+
```

#### Graph model

- **Nodes** are unique function qnames seen in any chain `path[]`.
  Properties: `qname`, `file`, `line`, `role` ∈ {source, sink, hop,
  both}, `taxonomy_ids[]` (a node is a source for some chains and
  intermediate for others; `role` is set from the union).
- **Edges** are caller→callee transitions `path[i] → path[i+1]` from
  any chain. Edge property `chain_ids[]` lists which chains contain
  that edge. Edge weight = `len(chain_ids)`.
- **Color:**
  - Source nodes: red (`#dc2626`).
  - Sink nodes: crimson (`#9f1239`).
  - Both: striped red/crimson.
  - Hops: gray (`#475569`).
- **Size:** node radius ∝ √(chain_count_through_node), clamped 8–28 px.
- **Edge thickness:** ∝ √(edge.weight), clamped 1–6 px.

#### Interactions

| Trigger | Effect |
|---|---|
| Click node | Right rail loads detail. Highlight all chains touching node. Dim others. |
| Double-click node | Center + zoom on node. |
| Click chain table row | Animate taint flow: pulse source → sink along that chain's path, 250 ms per hop. Camera follows. |
| Shift-click two nodes | Show only chains containing both nodes (Bloodhound "shortest path" analogue). |
| `f` key | Focus filter panel search box. |
| `s` key | Toggle snippet panel. |
| Filter change | Re-render graph: hide nodes/edges that no chain in the filtered set touches. |
| Layout switch | Toggle cose-bilkent ↔ dagre (left-to-right "flow" view). |

#### State

Client-side only (no persistence besides verdict writeback). React
state + URL query params for `?target=<name>` and `?selected=<chain_id>`
to share/bookmark a view. When `?selected=<chain_id>` is present on
load, the SPA selects that chain in the table, opens its right-rail
detail, and plays the propagation animation once.

### Component B — FastAPI sidecar (`bin/taintview_server.py`)

Single Python file, ~150 LOC. Endpoints:

| Method | Path | Returns |
|---|---|---|
| GET  | `/` | Static SPA (`tools/taintview/dist/index.html`) |
| GET  | `/assets/*` | Static SPA assets |
| GET  | `/api/targets` | List of dirs under `targets/` that contain `chains/all.jsonl` |
| GET  | `/api/target/{name}/chains` | `{chains: [...]}` — every chain from `chains/all.jsonl`, each annotated with `is_hot: bool` (presence in `hot.jsonl`) and `reach: "reachable"|"unreachable"|"unknown"` (presence in `dom_reachable.jsonl` / `dom_unreachable.jsonl`; `unknown` if neither). |
| GET  | `/api/target/{name}/opus/{chain_id}` | Markdown text of `opus/{chain_id}.md` or 404 |
| GET  | `/api/target/{name}/snippet?qname=...` | Calls tlx MCP `js_get_snippet`. Returns `{source, file, line, start_line, end_line}` |
| POST | `/api/target/{name}/verdict/{chain_id}` | Body: `{verdict: "tp"|"fp"|"undet", note: str}`. Appends to `targets/<name>/verdicts.jsonl`. |
| GET  | `/api/target/{name}/verdicts` | All verdicts as `{chain_id: {verdict, note, ts}}` |

MCP invocation: reuse the same stdio pattern the existing skills use to
talk to the tlx MCP server. The sidecar spawns `python -m mcp_server`
once on startup and keeps the connection alive. If the spawn fails, log
to stderr and serve a 503 with the error text on `/api/...` calls — the
SPA shows a banner.

CORS: not needed (same origin).

Port: `8765` default, `--port` flag to override.

### CLI (`bin/taintview.py`)

```
python bin/taintview.py <target-name> [--port 8765] [--no-open]
```

- Verifies `targets/<name>/chains/all.jsonl` exists.
- Verifies `tools/taintview/dist/index.html` exists; if not, prints
  `cd tools/taintview && npm run build`.
- Starts the FastAPI sidecar via uvicorn.
- Opens `http://localhost:<port>/?target=<name>` in the default browser
  (skip with `--no-open`).
- Ctrl-C shuts down sidecar cleanly.

## Data Flow Examples

### Initial load

1. User runs `python bin/taintview.py coralbug3-syn`.
2. Sidecar starts, opens browser to `/?target=coralbug3-syn`.
3. SPA fetches `/api/target/coralbug3-syn/chains` and
   `/api/target/coralbug3-syn/verdicts`.
4. SPA builds graph model client-side, renders.

### Click chain row in bottom table

1. SPA fetches `/api/target/<n>/opus/<chain_id>` (cached after first call).
2. Animates path through graph.
3. Right rail shows sink node detail with opus markdown rendered.

### Show snippet

1. User clicks node → right rail shows qname/file/line.
2. User clicks "Show snippet" → SPA fetches
   `/api/target/<n>/snippet?qname=<qname>`.
3. Sidecar forwards to tlx MCP `js_get_snippet`, returns source text.
4. SPA renders with prismjs highlight, ±5 lines around `line`.

### Write verdict

1. User picks TP/FP/undet radio in right rail, types note, hits save.
2. SPA POSTs `/api/target/<n>/verdict/<chain_id>`.
3. Sidecar appends `{chain_id, verdict, note, ts}` to
   `targets/<n>/verdicts.jsonl`. `ts` is ISO-8601 UTC. On read, the
   sidecar collapses by `chain_id` to "last entry wins".
4. Chain table row updates verdict column live.

## File Layout

```
tools/taintview/
  package.json
  vite.config.ts
  tsconfig.json
  tailwind.config.ts
  src/
    main.tsx
    App.tsx
    api.ts                  # fetch wrappers
    state/
      chains.ts             # chain model + derived graph
      filters.ts            # filter state
    components/
      Graph.tsx             # Cytoscape canvas
      FilterRail.tsx
      NodeDetail.tsx
      ChainTable.tsx
      SnippetView.tsx
      OpusView.tsx
      VerdictEditor.tsx
    util/
      animate.ts            # path-pulse animation
  dist/                     # build output, checked in
bin/
  taintview.py              # CLI launcher
  taintview_server.py       # FastAPI sidecar
```

## Error Handling

| Failure | UI behavior |
|---|---|
| chains/all.jsonl missing | CLI prints error, refuses to start. |
| tlx MCP fails to spawn | Sidecar logs to stderr; `/api/snippet` returns 503 with error. SPA shows "snippet unavailable: <err>" in right rail. Graph + chains still work. |
| opus/<id>.md missing | `/api/opus` returns 404; right rail shows "no opus writeup". |
| chain has invalid path (single-node, empty) | Skip with console warning. |
| Cytoscape layout times out on >5k nodes | SPA detects via timing and switches to dagre layout, shows banner. |
| Browser closed mid-session | Sidecar keeps running until Ctrl-C. |

## Testing

- **Sidecar:** pytest. Stub tlx MCP via fake stdio process. Assert all
  endpoints return correct shape. Test verdict append idempotency
  (re-posting same chain_id updates rather than duplicates — last write
  wins per chain).
- **SPA:** Vitest + React Testing Library. Two tests are enough for
  initial cut:
  1. Given a fixture of 3 chains sharing one hop node, the graph
     renders 5 unique nodes and 4 unique edges.
  2. Clicking a chain row triggers the animate function with the
     expected node id sequence.
- **End-to-end:** manual smoke against `coralbug3-syn` (real data).
  Document in spec PR description.

## Open Questions

None — all design decisions captured above.

## Risks & Tradeoffs

- **Cytoscape on large graphs.** A target with 10k+ chains and many
  shared hops may exceed 5k nodes. Mitigation: filter defaults to
  `score >= 70` (matches `hot.jsonl` threshold) on initial load; users
  opt into the full graph via filter.
- **Sidecar lifetime.** Long-running uvicorn process holds MCP stdio
  open. If tlx MCP crashes mid-session, snippet calls fail until
  restart. Sidecar should detect EOF on stdio and respawn the MCP once
  before giving up.
- **Build output in git.** Checking `dist/` in keeps the tool runnable
  without a node toolchain but adds binary churn. Acceptable for a
  single-user repo; revisit if it bothers diffs.
- **Verdict file as JSONL.** Append-only with "last write wins per
  chain_id" semantics requires reading the whole file to dedupe on
  load. At <10k chains per target this is fine; not a real bottleneck.

## Out-of-Scope Extensions (future)

- Graphify-style cross-target view: compare two targets' graphs.
- Time-machine: replay how the chain set grew across `autoresearch.jsonl` iterations.
- WebSocket push: live updates as a new `autoresearch-loop` writes new chains.

These are noted only so reviewers don't propose them in v1.
