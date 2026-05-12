#!/usr/bin/env bash
# Cron entry: every 15 min run cleanup_orphans against the recon MCP.
# This kills droplets that escaped a crashed MCP process — runaway cost protection.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$HOME/.config/claude/.env" ] && set -a && . "$HOME/.config/claude/.env" && set +a
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
cd "$ROOT"
uv run --project recon_mcp python -c '
import asyncio
from recon_mcp.config import load_config
from recon_mcp.do_client import DOClient
from recon_mcp.jobs import JobStore
from recon_mcp.handlers.cleanup import handle_cleanup_orphans

async def main():
    cfg = load_config()
    store = JobStore(db_path=str(cfg.db_path))
    await store.init()
    do = DOClient(token=cfg.do_api_token)
    out = await handle_cleanup_orphans(store=store, do=do)
    print("destroyed:", out.destroyed)

asyncio.run(main())
'
