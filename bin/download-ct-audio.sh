#!/usr/bin/env bash
# Pre-download CT podcast audio as 16kHz mono WAV.
# Idempotent. Parallel N at a time (network, not GPU).
# Usage: bin/download-ct-audio.sh [PARALLEL]   # default 4

set -uo pipefail

ROOT="/Users/soural/Documents/TLX/wiki/sources/podcasts/ct"
VTT_DIR="$ROOT"
AUDIO_DIR="$ROOT/whisper/audio_tmp"
TX_DIR="$ROOT/whisper/transcripts"
LOG="$ROOT/whisper/_dl_log.jsonl"
PAR="${1:-4}"

mkdir -p "$AUDIO_DIR"

dl_one() {
  local vtt="$1"
  local base vid
  base="$(basename "$vtt" .en.vtt)"
  vid="$(echo "$base" | sed -E 's/^[0-9]{8}_(.{11}).*/\1/')"
  local wav="$AUDIO_DIR/${vid}.wav"
  # Already transcribed → skip download
  if [[ -s "$TX_DIR/${base}.txt" ]]; then return 0; fi
  # Already downloaded → skip
  if [[ -s "$wav" ]]; then return 0; fi
  local ts; ts="$(date -u +%FT%TZ)"
  if yt-dlp -q --no-warnings -x --audio-format wav \
       --postprocessor-args "-ar 16000 -ac 1" \
       -o "$AUDIO_DIR/${vid}.%(ext)s" \
       "https://www.youtube.com/watch?v=${vid}" 2>>"$LOG.err"; then
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"status\":\"ok\"}" >> "$LOG"
    echo "[$ts] dl ok $vid ($base)"
  else
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"status\":\"fail\"}" >> "$LOG"
    echo "[$ts] dl FAIL $vid"
  fi
}

export -f dl_one
export AUDIO_DIR TX_DIR LOG

find "$VTT_DIR" -maxdepth 1 -name "*.en.vtt" -print0 \
  | xargs -0 -n1 -P "$PAR" bash -c 'dl_one "$0"'

echo "Download pass done."
