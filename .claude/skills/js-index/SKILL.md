---
name: js-index
description: Build the interprocedural callgraph + framework detection + tag table for an exploded source tree by calling the tlx MCP js_index_target tool. Run after rag-ingest when status.json.phases.index is missing or stale (sources mtime > index mtime). Writes index/{nodes,edges}.jsonl and frameworks.json into the target dir.
---

# js-index

## Purpose
Run TLX's `js_index_target` against `targets/<name>/sources/` and
persist the resulting graph artifacts inside the target dir so they're
versioned alongside the target's other state.

## Inputs
- `targets/<name>/sources/**` (output of `sourcemap-explode`).

## Steps
1. Call the MCP tool:
   ```
   js_index_target(target_folder="targets/<name>/sources/")
   ```
2. The tool persists the callgraph in TLX's own SQLite/Chroma at
   `~/.tlx/`. We additionally export a copy into the target dir so
   each engagement is self-contained.
3. After success, mirror the artifacts into `targets/<name>/index/`:
   - `index/nodes.jsonl` — `{qname, file, line, kind, framework_tag}`
   - `index/edges.jsonl` — `{caller_qname, callee_qname, edge_kind}`
   - `index/frameworks.json` — detected frameworks + versions
   - `index/tags.jsonl` — source/sink/sanitizer tags
   (use a helper at `bin/export_index.py` that reads from `~/.tlx/`.)
4. Stamp `status.json.phases.index` with counts.

## Outputs
- `targets/<name>/index/{nodes,edges,tags}.jsonl`
- `targets/<name>/index/frameworks.json`

## Failure modes
- `js_index_target` returns zero nodes → almost always framework
  misdetection. Set
  `session_kv_set("target_<name>:framework_override", "<react|vue|...>")`
  via the TLX UI or a one-off Python call (MCP exposes only
  `session_kv_get` on purpose); re-index.
- AST parser chokes on a file → it's logged inside TLX; we surface
  `index/_skipped.json` so the user knows the coverage gap.

## Result block
```json
"phases": { "index": { "status": "done", "ts": "<iso>",
  "nodes": N, "edges": E, "tags": T, "frameworks": [...] } }
```
