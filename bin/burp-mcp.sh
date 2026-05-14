#!/bin/sh
# Wrapper: c0tton-fluff/burp-mcp-server (Go).
# Requires Burp Suite Pro running with MCP extension enabled (default 127.0.0.1:9876).
set -e
[ -f "$HOME/.config/claude/.env" ] && . "$HOME/.config/claude/.env"
[ -f "/Users/soural/Documents/TLX/.env" ] && . "/Users/soural/Documents/TLX/.env"

export BURP_MCP_URL="${BURP_MCP_URL:-http://127.0.0.1:9876/sse}"

exec /Users/soural/Documents/TLX/mcps/burp-mcp-server/burp-mcp-server serve
