#!/usr/bin/env bash
# One-shot full-channel VTT pull for Bug Bounty Reports Explained.
# Drops every .en.vtt under wiki/sources/podcasts/bbre/.
# Skips /shorts/. Idempotent — yt-dlp skips already-downloaded VTTs.
#
# Usage: bin/bbre-backfill.sh
# After this completes, run bin/transcribe-bbre.sh (or bin/bbre-poll.sh)
# to whisper-transcribe + drop READY markers.

set -uo pipefail

ROOT="/Users/soural/Documents/TLX"
BBRE_DIR="$ROOT/wiki/sources/podcasts/bbre"
LOG="$BBRE_DIR/whisper/_backfill_log.jsonl"

mkdir -p "$BBRE_DIR" "$BBRE_DIR/whisper"
ts() { date -u +%FT%TZ; }

echo "[$(ts)] backfill start"
echo "{\"ts\":\"$(ts)\",\"event\":\"start\"}" >> "$LOG"

# Pull every long-form video's English VTT. --match-filter excludes shorts.
cd "$BBRE_DIR" && yt-dlp \
    --no-warnings \
    --match-filter "!is_short" \
    --write-subs --write-auto-subs \
    --sub-lang en --sub-format vtt --skip-download \
    --restrict-filenames \
    --ignore-errors \
    -o "%(upload_date)s_%(id)s_%(title)s.%(ext)s" \
    "https://www.youtube.com/@BugBountyReportsExplained/videos" \
    2>>"$LOG.err"

vtt_count=$(find "$BBRE_DIR" -maxdepth 1 -name "*.en.vtt" | wc -l | tr -d ' ')
echo "[$(ts)] backfill done. vtts=$vtt_count"
echo "{\"ts\":\"$(ts)\",\"event\":\"done\",\"vtts\":$vtt_count}" >> "$LOG"
