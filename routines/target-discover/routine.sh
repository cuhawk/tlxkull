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

# Load secrets (DISCORD_WEBHOOK_URL, etc) if .env exists.
[[ -f .env ]] && set -a && source .env && set +a

# Post a Discord notification with the given content + optional embed JSON.
# Silent no-op when DISCORD_WEBHOOK_URL is unset.
notify_discord() {
  local content="$1"
  local embed_json="${2:-}"
  [[ -z "${DISCORD_WEBHOOK_URL:-}" ]] && return 0
  local payload
  if [[ -n "$embed_json" ]]; then
    payload=$(python3 -c "import json,sys; print(json.dumps({'content': sys.argv[1], 'embeds': [json.loads(sys.argv[2])]}))" "$content" "$embed_json")
  else
    payload=$(python3 -c "import json,sys; print(json.dumps({'content': sys.argv[1]}))" "$content")
  fi
  curl -sS -X POST -H "Content-Type: application/json" \
    -d "$payload" "$DISCORD_WEBHOOK_URL" \
    -o /dev/null -w '%{http_code}' >> "$LOG.discord" 2>&1 || true
  echo "" >> "$LOG.discord"
}

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

# -- API walk (cookie-based, primary discovery path for H1/BC/Intigriti) ----
if [[ "$mode" != "gmail" ]]; then
  if ls "${ROUTINE_DIR}/cookies"/*.json >/dev/null 2>&1 \
     && ls "${ROUTINE_DIR}/auth_state"/*.json >/dev/null 2>&1; then
    python3 "${ROUTINE_DIR}/api_walk.py" $dry_run | tee -a "$LOG"
  else
    echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"routine\":\"target-discover\",\"action\":\"api_walk_skipped_no_cookies\",\"ok\":true}" >> "$LOG"
  fi
fi

# -- Dashboard walk fallback (playwright HTML snapshot — disabled by default) -
# Uncomment if api_walk fails for a platform and you want HTML snapshots.
# if [[ "$mode" != "gmail" ]] && ls "${ROUTINE_DIR}/cookies"/*.json >/dev/null 2>&1; then
#   python3 "${ROUTINE_DIR}/dashboard_walk.py" $dry_run | tee -a "$LOG"
# fi

# -- Discord summary (always, even on quiet day) ------------------------------
summary=$(python3 - <<'PY' "$ROUTINE_DIR"
import json, sys, pathlib, datetime, collections
root = pathlib.Path(sys.argv[1])
inbox = pathlib.Path("inbox/invites")
sweep_log = inbox / "_sweep_log.jsonl"
last = {}
if sweep_log.exists():
    for line in sweep_log.read_text().splitlines():
        if line.strip():
            try: last = json.loads(line)
            except: pass
counts = collections.Counter()
for plat in ["hackerone", "intigriti", "bugcrowd", "synack"]:
    pdir = inbox / plat
    if pdir.exists():
        for s in pdir.iterdir():
            if (s / "READY").exists():
                counts[plat] += 1
print(json.dumps({"last_run": last, "ready_seeds": dict(counts)}))
PY
)
new=$(echo "$summary" | python3 -c "import json,sys; d=json.load(sys.stdin); l=d.get('last_run',{}); print(f\"created={l.get('created',0)} duplicate={l.get('duplicate',0)} synack_ready={d['ready_seeds'].get('synack',0)} h1_ready={d['ready_seeds'].get('hackerone',0)} intigriti_ready={d['ready_seeds'].get('intigriti',0)} bc_ready={d['ready_seeds'].get('bugcrowd',0)}\")")
notify_discord "**target-discover** ($(date -u +%FT%TZ)) — mode=$mode — $new"

echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"routine\":\"target-discover\",\"action\":\"done\",\"ok\":true,\"summary\":$summary}" >> "$LOG"
