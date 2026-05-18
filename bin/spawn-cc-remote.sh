#!/usr/bin/env bash
# Spawn a detached interactive `claude --remote-control` session via a
# `script(1)` PTY wrapper and print the claude.ai/code session URL.
#
# Why script(1):
#   `claude --remote-control` is a TUI. Without a real TTY (Bash tool,
#   nohup alone, &) it falls into --print mode and exits demanding a
#   prompt. `script -q` provides a pseudo-TTY so claude boots
#   interactive even when launched from a non-TTY parent.
#
# Survives parent shell exit: nohup + & + disown reparents to init.
#
# Usage:
#   bin/spawn-cc-remote.sh [name]
# Defaults: name=rc-<unix-ts>, log=/tmp/cc-rc-<name>.log

set -euo pipefail

name="${1:-rc-$(date +%s)}"
log="/tmp/cc-rc-${name}.log"
: > "$log"

nohup script -q "$log" claude --remote-control "$name" </dev/null >/dev/null 2>&1 &
disown

for _ in $(seq 1 120); do
  url=$(grep -aoE 'https://claude\.ai/code/session_[A-Za-z0-9]+' "$log" 2>/dev/null | head -1 || true)
  if [ -n "$url" ]; then
    pid=$(pgrep -f "claude --remote-control $name" | tail -1 || true)
    printf 'url=%s\nname=%s\npid=%s\nlog=%s\n' "$url" "$name" "$pid" "$log"
    exit 0
  fi
  sleep 0.5
done

echo "FAILED: no session URL after 60s. Last 40 lines of $log:" >&2
tail -40 "$log" 2>/dev/null | tr -d '\000' | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' >&2
exit 1
