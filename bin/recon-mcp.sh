#!/usr/bin/env bash
# recon MCP entrypoint — mirrors bin/tlx-mcp.sh pattern.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$HOME/.config/claude/.env" ] && set -a && . "$HOME/.config/claude/.env" && set +a
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
cd "$ROOT"
exec uv run --project recon_mcp python -m recon_mcp.server
