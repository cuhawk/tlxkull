#!/bin/sh
# Wrapper: Go-based caido-mcp-server fork (cuhawk/caido-mcp-server).
# Uses OAuth token at ~/.caido-mcp/token.json (run `caido-mcp-server login` to refresh).
# CAIDO_PAT path disabled — server falls back to stored OAuth token.
set -e
[ -f "$HOME/.config/claude/.env" ] && . "$HOME/.config/claude/.env"
[ -f "/Users/soural/Documents/TLX/.env" ] && . "/Users/soural/Documents/TLX/.env"

export CAIDO_URL="${CAIDO_URL:-http://127.0.0.1:8080}"
unset CAIDO_PAT CAIDO_API_TOKEN

exec /Users/soural/Documents/TLX/mcps/caido-mcp-server/caido-mcp-server serve
