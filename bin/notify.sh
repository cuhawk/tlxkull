#!/usr/bin/env bash
# Discord webhook notifier. Reads DISCORD_WEBHOOK_URL from env (or ~/.config/claude/.env).
# Usage:
#   bin/notify.sh "message text"
#   bin/notify.sh -t "title" -m "body"
#   echo "msg" | bin/notify.sh -
set -u

ENV_FILE="${HOME}/.config/claude/.env"
if [ -z "${DISCORD_WEBHOOK_URL:-}" ] && [ -r "$ENV_FILE" ]; then
  # shellcheck disable=SC2046
  export $(grep -E '^DISCORD_WEBHOOK_URL=' "$ENV_FILE" | tail -1 | xargs)
fi
if [ -z "${DISCORD_WEBHOOK_URL:-}" ]; then
  echo "DISCORD_WEBHOOK_URL not set" >&2
  exit 2
fi

title=""
msg=""
while [ $# -gt 0 ]; do
  case "$1" in
    -t) title="$2"; shift 2 ;;
    -m) msg="$2"; shift 2 ;;
    -)  msg=$(cat); shift ;;
    *)  msg="${msg:+$msg }$1"; shift ;;
  esac
done

[ -z "$msg" ] && { echo "no message"; exit 2; }

host=$(hostname -s 2>/dev/null || echo host)
prefix="[$host]"
[ -n "$title" ] && prefix="$prefix **$title**"

# Truncate to 1900 chars (discord limit 2000)
msg_truncated=$(printf '%s' "$msg" | head -c 1900)
content="$prefix\n\`\`\`\n${msg_truncated}\n\`\`\`"

# JSON-escape via python (handles quotes/newlines)
payload=$(python3 -c "import json,sys; print(json.dumps({'content': sys.argv[1]}))" "$(printf '%b' "$content")")

curl -sS -o /dev/null -w "%{http_code}\n" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d "$payload" \
  "$DISCORD_WEBHOOK_URL"
