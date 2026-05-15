#!/opt/homebrew/bin/bash
# CTBB RSS poll + harvest. Idempotent.
# Drops new VTTs into wiki/sources/podcasts/ct/ and invokes transcribe-ct.sh.
# Marks each newly-transcribed episode READY in inbox/ctbb/<vid>/ for the
# ingest skill (which a Claude Code session picks up later).
#
# Usage:
#   bin/ctbb-poll.sh          # poll, dl new VTTs, transcribe, mark READY
#   bin/ctbb-poll.sh --dry    # show what would be processed
#
# Skips YouTube Shorts (links containing /shorts/).

set -uo pipefail

ROOT="/Users/soural/Documents/TLX"
CT_DIR="$ROOT/wiki/sources/podcasts/ct"
TX_DIR="$CT_DIR/whisper/transcripts"
INBOX="$ROOT/inbox/ctbb"
CHANNEL_ID="UC6zbKG1pqq2do-_oa9QFliA"
RSS_URL="https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}"
LOG="$ROOT/wiki/sources/podcasts/ct/whisper/_poll_log.jsonl"
DRY=0

[[ "${1:-}" == "--dry" ]] && DRY=1

mkdir -p "$CT_DIR" "$INBOX"

ts() { date -u +%FT%TZ; }

# Fetch RSS, extract (videoId, link) pairs, drop /shorts/ entries.
mapfile -t entries < <(
  curl -fsSL "$RSS_URL" \
    | python3 -c '
import sys, re, xml.etree.ElementTree as ET
data = sys.stdin.read()
root = ET.fromstring(data)
ns = {"a": "http://www.w3.org/2005/Atom", "y": "http://www.youtube.com/xml/schemas/2015"}
for e in root.findall("a:entry", ns):
    vid = e.find("y:videoId", ns).text
    link = e.find("a:link", ns).get("href", "")
    if "/shorts/" in link:
        continue
    print(vid)
'
)

need_harvest=()   # no transcript yet — must dl + whisper
need_ready=()     # transcript present but inbox marker missing
for vid in "${entries[@]}"; do
  # Already DONE → skip entirely.
  if [[ -f "$INBOX/$vid/DONE" ]]; then
    continue
  fi
  if compgen -G "$TX_DIR/*_${vid}_*.txt" >/dev/null; then
    # Transcript exists. If inbox already READY, nothing to do.
    if [[ -f "$INBOX/$vid/READY" ]]; then
      continue
    fi
    need_ready+=("$vid")
    continue
  fi
  need_harvest+=("$vid")
done

if [[ ${#need_harvest[@]} -eq 0 && ${#need_ready[@]} -eq 0 ]]; then
  echo "[$(ts)] no new episodes"
  echo "{\"ts\":\"$(ts)\",\"event\":\"poll\",\"new\":0}" >> "$LOG"
  exit 0
fi

echo "[$(ts)] harvest=${#need_harvest[@]} ready_only=${#need_ready[@]}"

if [[ "$DRY" -eq 1 ]]; then
  echo "{\"ts\":\"$(ts)\",\"event\":\"dry\",\"harvest\":${#need_harvest[@]},\"ready\":${#need_ready[@]}}" >> "$LOG"
  exit 0
fi

# Download VTT for each vid needing harvest.
for vid in "${need_harvest[@]}"; do
  if compgen -G "$CT_DIR/*_${vid}_*.en.vtt" >/dev/null; then
    continue
  fi
  (cd "$CT_DIR" && yt-dlp -q --no-warnings \
       --write-subs --write-auto-subs \
       --sub-lang en --sub-format vtt --skip-download \
       --restrict-filenames \
       -o "%(upload_date)s_%(id)s_%(title)s.%(ext)s" \
       "https://www.youtube.com/watch?v=${vid}" 2>>"$LOG.err") \
       && echo "{\"ts\":\"$(ts)\",\"vid\":\"$vid\",\"event\":\"vtt_dl\"}" >> "$LOG" \
       || { echo "[$(ts)] vtt_dl FAIL $vid"; continue; }
done

# Drive transcription via existing script (handles dl audio + mlx_whisper).
if [[ ${#need_harvest[@]} -gt 0 ]]; then
  "$ROOT/bin/transcribe-ct.sh" "${#need_harvest[@]}" 2>&1 | tail -40
fi

# Drop READY markers. Union of: just-harvested vids + pre-existing transcripts
# we hadn't claimed yet.
to_ready=("${need_harvest[@]}" "${need_ready[@]}")
ready_count=0
for vid in "${to_ready[@]}"; do
  txt="$(compgen -G "$TX_DIR/*_${vid}_*.txt" | head -1)"
  if [[ -z "${txt:-}" || ! -s "$txt" ]]; then
    echo "[$(ts)] transcript missing for $vid — skip READY"
    continue
  fi
  base="$(basename "$txt" .txt)"
  mkdir -p "$INBOX/$vid"
  ln -sf "$txt" "$INBOX/$vid/transcript.txt"
  echo "$base" > "$INBOX/$vid/base"
  date -u +%FT%TZ > "$INBOX/$vid/READY"
  echo "{\"ts\":\"$(ts)\",\"vid\":\"$vid\",\"base\":\"$base\",\"event\":\"ready\"}" >> "$LOG"
  echo "[$(ts)] READY $vid"
  ready_count=$((ready_count + 1))
done

# Fire headless Claude Code ctbb-ingest if any new READY markers landed.
# Skip if CTBB_AUTO_INGEST=0 in env (manual override).
if [[ "$ready_count" -gt 0 && "${CTBB_AUTO_INGEST:-1}" == "1" ]]; then
  if command -v claude >/dev/null 2>&1; then
    echo "[$(ts)] firing headless ctbb-ingest for $ready_count episodes"
    echo "{\"ts\":\"$(ts)\",\"event\":\"ingest_fire\",\"n\":$ready_count}" >> "$LOG"
    (cd "$ROOT" && claude -p "/ctbb-ingest" \
        --max-budget-usd 5 \
        --dangerously-skip-permissions \
        --output-format text \
        >> "$ROOT/wiki/sources/podcasts/ct/whisper/_ingest_claude.log" 2>&1) \
        && echo "{\"ts\":\"$(ts)\",\"event\":\"ingest_done\"}" >> "$LOG" \
        || echo "{\"ts\":\"$(ts)\",\"event\":\"ingest_fail\"}" >> "$LOG"
  else
    echo "[$(ts)] claude CLI missing — READY markers left for manual ingest"
    echo "{\"ts\":\"$(ts)\",\"event\":\"ingest_skip_no_cli\"}" >> "$LOG"
  fi
fi
