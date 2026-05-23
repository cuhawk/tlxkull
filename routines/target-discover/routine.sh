#!/opt/homebrew/bin/bash
# target-discover routine — Gmail sweep + optional dashboard walk.
# launchd entry point. Idempotent. Locks at /tmp/tlx-target-discover.lock.
#
# Usage:
#   bash routine.sh                # production: gmail + dashboard
#   bash routine.sh --gmail-only   # skip dashboard walk
#   bash routine.sh --dry-run      # parse but don't write
#   bash routine.sh --backfill 365 # forward backfill window

set -euo pipefail

cd "$(dirname "$0")/../.."   # repo root
ROUTINE_DIR="routines/target-discover"
LOCK=/tmp/tlx-target-discover.lock
LOG="${ROUTINE_DIR}/_log.jsonl"

mode="full"
backfill_days=7
dry_run=""
for arg in "$@"; do
  case "$arg" in
    --gmail-only) mode="gmail" ;;
    --dashboard-only) mode="dashboard" ;;
    --dry-run) dry_run="--dry-run" ;;
    --backfill) ;;  # consumed next-arg
    [0-9]*) backfill_days="$arg" ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

# flock — abort if another run is in progress (no queueing)
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"routine\":\"target-discover\",\"action\":\"locked\",\"ok\":false}" >> "$LOG"
  exit 0
fi

ts=$(date -u +%FT%TZ)
echo "{\"ts\":\"$ts\",\"routine\":\"target-discover\",\"action\":\"start\",\"mode\":\"$mode\",\"backfill_days\":$backfill_days,\"dry_run\":\"${dry_run:-no}\"}" >> "$LOG"

# -- gmail sweep --------------------------------------------------------------
if [[ "$mode" != "dashboard" ]]; then
  # The actual Gmail MCP calls live inside the CC skill `target-invite-sweep`.
  # We invoke it headless via `claude --print`. Skill writes NDJSON of threads
  # to stdout, which we pipe into parse_invites.py.
  if ! command -v claude >/dev/null; then
    echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"routine\":\"target-discover\",\"action\":\"missing_claude_cli\",\"ok\":false}" >> "$LOG"
    exit 1
  fi
  # Tight allowedTools whitelist — only Gmail MCP read ops. No file ops,
  # no shell, no other MCPs. Defense in depth in case --dangerously-skip
  # is required for non-interactive launchd context (it suppresses
  # permission prompts that would otherwise hang the schedule).
  tmp=$(mktemp)
  claude --print --dangerously-skip-permissions \
    --allowedTools "mcp__claude_ai_Gmail__search_threads,mcp__claude_ai_Gmail__get_thread" \
    "/target-invite-sweep --backfill-days $backfill_days --emit ndjson" \
    > "$tmp" 2>&1 || {
      echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"routine\":\"target-discover\",\"action\":\"claude_failed\",\"ok\":false,\"tmpfile\":\"$tmp\"}" >> "$LOG"
      exit 1
    }
  python3 "${ROUTINE_DIR}/parse_invites.py" --input "$tmp" $dry_run | tee -a "$LOG"
  rm -f "$tmp"
fi

# -- dashboard walk (cookie-based, optional) ---------------------------------
if [[ "$mode" != "gmail" ]]; then
  if ls "${ROUTINE_DIR}/cookies"/*.json >/dev/null 2>&1; then
    python3 "${ROUTINE_DIR}/dashboard_walk.py" $dry_run | tee -a "$LOG"
  else
    echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"routine\":\"target-discover\",\"action\":\"dashboard_skipped_no_cookies\",\"ok\":true}" >> "$LOG"
  fi
fi

echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"routine\":\"target-discover\",\"action\":\"done\",\"ok\":true}" >> "$LOG"
