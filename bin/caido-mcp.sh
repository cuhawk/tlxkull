#!/bin/sh
# Wrapper: source env, exec Caido MCP wrapper with TLX venv python.
set -e
[ -f "$HOME/.config/claude/.env" ] && . "$HOME/.config/claude/.env"
[ -f "/Users/soural/Documents/TLX/.env" ] && . "/Users/soural/Documents/TLX/.env"
export CAIDO_API_URL="${CAIDO_API_URL:-http://127.0.0.1:8080/api/graphql}"
exec /Users/soural/Documents/TLX/tlx/.venv/bin/python /Users/soural/Documents/TLX/bin/caido-mcp.py
