#!/bin/sh
# Wrapper: source env, exec TLX MCP server with venv python.
# Used by .claude/settings.json. Keeps secrets out of checked-in config.
set -e
[ -f "$HOME/.config/claude/.env" ] && . "$HOME/.config/claude/.env"
[ -f "/Users/soural/Documents/TLX/.env" ] && . "/Users/soural/Documents/TLX/.env"
export TLX_HOME="${TLX_HOME:-$HOME/.tlx}"
cd /Users/soural/Documents/TLX/tlx
exec /Users/soural/Documents/TLX/tlx/.venv/bin/python -m mcp_server
