#!/usr/bin/env bash
# Scan audio_tmp/ for stranded BBRE transcript outputs (vid.txt + vid.srt) left
# by orphaned worker processes. Move them into transcripts/<base>.{txt,srt}.
# Idempotent. Safe to run anytime.

set -uo pipefail

ROOT="/Users/soural/Documents/TLX/wiki/sources/podcasts/bbre"
VTT_DIR="$ROOT"
OUT_DIR="$ROOT/whisper/transcripts"
AUDIO_DIR="$ROOT/whisper/audio_tmp"
LOG="$ROOT/whisper/_log.jsonl"

mkdir -p "$OUT_DIR"

for txt in "$AUDIO_DIR"/*.txt; do
  [[ -e "$txt" ]] || continue
  vid="$(basename "$txt" .txt)"
  lockfile="$AUDIO_DIR/${vid}.lock"
  if [[ -f "$lockfile" ]]; then
    pid="$(cat "$lockfile" 2>/dev/null)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "[skip live] $vid"
      continue
    fi
    rm -f "$lockfile"
  fi
  vtt="$(ls "$VTT_DIR"/*_"${vid}"_*.en.vtt 2>/dev/null | head -1)"
  if [[ -z "$vtt" ]]; then
    echo "[no vtt match] $vid"
    continue
  fi
  base="$(basename "$vtt" .en.vtt)"
  out_txt="$OUT_DIR/${base}.txt"
  out_srt="$OUT_DIR/${base}.srt"
  if [[ -s "$out_txt" ]]; then
    echo "[already done] $base"
    rm -f "$AUDIO_DIR/${vid}.txt" "$AUDIO_DIR/${vid}.srt" \
          "$AUDIO_DIR/${vid}.vtt" "$AUDIO_DIR/${vid}.tsv" \
          "$AUDIO_DIR/${vid}.json" "$AUDIO_DIR/${vid}.wav"
    continue
  fi
  mv "$AUDIO_DIR/${vid}.txt" "$out_txt"
  [[ -e "$AUDIO_DIR/${vid}.srt" ]] && mv "$AUDIO_DIR/${vid}.srt" "$out_srt"
  rm -f "$AUDIO_DIR/${vid}.vtt" "$AUDIO_DIR/${vid}.tsv" "$AUDIO_DIR/${vid}.json"
  rm -f "$AUDIO_DIR/${vid}.wav"
  ts="$(date -u +%FT%TZ)"
  echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"finalized\",\"engine\":\"mlx\"}" >> "$LOG"
  echo "[finalized] $base"
done
