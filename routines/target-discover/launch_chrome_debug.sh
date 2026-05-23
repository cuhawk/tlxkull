#!/opt/homebrew/bin/bash
# Quit your Chrome, relaunch with --remote-debugging-port=9222 using your
# existing default profile (cookies + login sessions preserved). Run once
# before bootstrap_cookies.py.
#
# Usage:
#   bash routines/target-discover/launch_chrome_debug.sh
#
# What it does:
#   1. Quits running Chrome (osascript graceful quit; SIGTERM fallback).
#   2. Waits for Chrome to exit cleanly.
#   3. Relaunches Chrome with --remote-debugging-port=9222 pointing at
#      ~/Library/Application Support/Google/Chrome (your real profile).
#   4. Waits for CDP endpoint to come up.
#
# After this script: run `python3 routines/target-discover/bootstrap_cookies.py`
# Then quit Chrome and reopen normally — debug port is one-shot.

set -euo pipefail

PORT=9222
PROFILE_DIR="$HOME/Library/Application Support/Google/Chrome"
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [[ ! -x "$CHROME_BIN" ]]; then
  echo "ERR: Chrome not found at $CHROME_BIN" >&2
  exit 1
fi

if curl -sS --max-time 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
  echo "CDP already up on :$PORT — skipping relaunch."
  exit 0
fi

if pgrep -f "Google Chrome" >/dev/null; then
  echo "Quitting Chrome (graceful)..."
  osascript -e 'tell application "Google Chrome" to quit' || true
  for i in {1..15}; do
    pgrep -f "Google Chrome" >/dev/null || break
    sleep 1
  done
  if pgrep -f "Google Chrome" >/dev/null; then
    echo "Graceful quit timed out; sending TERM..."
    pkill -TERM -f "Google Chrome" || true
    sleep 2
  fi
fi

echo "Launching Chrome with --remote-debugging-port=$PORT + your default profile..."
"$CHROME_BIN" \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$PROFILE_DIR" \
  >/dev/null 2>&1 &
disown

echo "Waiting for CDP endpoint..."
for i in {1..20}; do
  if curl -sS --max-time 1 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
    echo "  ok — CDP at http://127.0.0.1:$PORT"
    curl -sS "http://127.0.0.1:$PORT/json/version" | python3 -m json.tool | head -5
    echo ""
    echo "Now run: python3 routines/target-discover/bootstrap_cookies.py"
    echo "After cookies are saved, quit Chrome and reopen normally."
    exit 0
  fi
  sleep 1
done

echo "ERR: CDP endpoint never came up. Check Chrome started OK." >&2
exit 1
