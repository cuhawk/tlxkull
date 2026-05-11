# Setup — TLX Bug-Bounty Workspace

One-time install steps. Run from this folder. Should take ~15 minutes.

---

## 1. Python env for the vendored TLX subset

```bash
cd tlx
uv venv
uv pip install -e .
uv run playwright install chromium
cd ..
```

If you don't have `uv`, `pip install -e .[dev]` works too.

## 2. API keys

Required env vars (export in your shell rc, or use a per-folder `.envrc`
via `direnv`):

```bash
export GOOGLE_API_KEY=...        # for ChromaDB embedder (text-embedding-004)
export ANTHROPIC_API_KEY=...     # for Opus advisor in js_analyzer audit loop
export CAIDO_API_TOKEN=...       # optional; only if your Caido API requires bearer
```

Get a Google Generative Language key: https://ai.google.dev → "Get API key".
Make sure the Generative Language API is enabled on the GCP project.

## 3. MCP servers — install once

`.claude/settings.json` already wires four MCPs. Install the npx-served
ones (chrome-devtools, playwright) on first run — Claude Code will
prompt or you can prefetch:

```bash
npx -y chrome-devtools-mcp@latest --help >/dev/null
npx -y @modelcontextprotocol/server-playwright --help >/dev/null
```

The `caido` MCP runs from `bin/caido-mcp.py`; its deps:

```bash
uv pip install --python tlx/.venv/bin/python httpx mcp structlog
# or use a separate venv just for the wrapper
```

## 4. Caido

1. Install Caido GUI (https://caido.io).
2. Open Settings → Other → enable the API.
3. Note the local API URL (default: `http://127.0.0.1:8080/api/graphql`
   — update `CAIDO_API_URL` in `.claude/settings.json > mcpServers.caido.env`
   if yours differs).
4. Install Caido's CA cert into your Chrome trust store so HTTPS
   intercept works. Documented in `wiki/tools/caido/cert-trust.md`
   (write this page after your first install).
5. Run `caido_introspect` once via Claude Code:
   "use the caido MCP to introspect the schema and write
   wiki/tools/caido/schema-snapshot.md".
   Compare each TODO(caido-api) marker in `bin/caido-mcp.py` against
   the live schema; update queries if field names differ.

## 5. Verify the tlx MCP boots

```bash
cd tlx
python -m mcp_server <<< '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

Expect a JSON response listing 16 tools (8 js_analyzer + 6 mock_backend
+ docs_query + session_kv_get). If it hangs, the `<<<` here-string
isn't sending an MCP-shaped init. Easier verification: just point
Claude Code at this workspace; first turn will exercise the MCP and
errors surface clearly.

## 6. First target

```bash
mkdir -p targets/<target-name>
cp targets/_TEMPLATE_http.md targets/<target-name>/http.md
$EDITOR targets/<target-name>/http.md
```

Then in Claude Code: "start target <target-name>". The `target-init`
skill fires, normalizes scope, writes `status.json`. Continue from
there per `workflow.md`.

## 7. Optional polish

- `.envrc` (direnv) to auto-load API keys when you `cd` into this folder.
- A shell alias for the wiki RAG: `alias wq='echo "wiki-query: $*" | tee ...'`
- Cron a weekly `wiki-lint`.

---

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `python -m mcp_server` immediately errors with `ModuleNotFoundError: kernel` | You're not in `./tlx/`. `cd tlx` first or fix `cwd` in `.claude/settings.json`. |
| Embedder errors `PERMISSION_DENIED` | `GOOGLE_API_KEY` wrong or Generative Language API disabled on the GCP project. |
| `chromedb` import error | `uv pip install chromadb` (sometimes lazy-installed). |
| Caido MCP returns `{"reachable": false}` | Caido GUI not running OR API disabled in settings. |
| Playwright sink confirmation fails on launch | `uv run playwright install chromium` was skipped. Run it. |
| `js_index_target` returns 0 nodes | Framework misdetection — see `memory.md > Failure-mode reminders`. |
