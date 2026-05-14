#!/usr/bin/env bash
# Re-transcribe Critical Thinking podcast VTTs with mlx-whisper large-v3-turbo.
# Idempotent: skips episodes already in transcripts/.
# Usage: bin/transcribe-ct.sh [N]   # N = max episodes this run (default: all)

set -uo pipefail

ROOT="/Users/soural/Documents/TLX/wiki/sources/podcasts/ct"
VTT_DIR="$ROOT"
OUT_DIR="$ROOT/whisper/transcripts"
AUDIO_DIR="$ROOT/whisper/audio_tmp"
LOG="$ROOT/whisper/_log.jsonl"
MODEL="mlx-community/whisper-large-v3-turbo"
MAX="${1:-99999}"

mkdir -p "$OUT_DIR" "$AUDIO_DIR"

# Sweep stranded outputs left by previously killed bash wrappers.
"$(dirname "$0")/finalize-stranded.sh" >/dev/null 2>&1 || true

# Clean stale lockfiles whose owning process is no longer alive.
for lf in "$AUDIO_DIR"/*.lock; do
  [[ -e "$lf" ]] || continue
  pid="$(cat "$lf" 2>/dev/null)"
  if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$lf"
  fi
done

count=0
for vtt in "$VTT_DIR"/*.en.vtt; do
  base="$(basename "$vtt" .en.vtt)"
  # Filename pattern: <YYYYMMDD>_<VIDEO_ID_11chars>_<title>
  # YouTube IDs are 11 chars [A-Za-z0-9_-] and may contain underscores.
  vid="$(echo "$base" | sed -E 's/^[0-9]{8}_(.{11}).*/\1/')"
  out_txt="$OUT_DIR/${base}.txt"
  out_srt="$OUT_DIR/${base}.srt"
  audio_wav="$AUDIO_DIR/${vid}.wav"

  if [[ -s "$out_txt" ]]; then
    continue
  fi
  lockfile="$AUDIO_DIR/${vid}.lock"
  if ! ( set -o noclobber; echo "$$" > "$lockfile" ) 2>/dev/null; then
    echo "[skip locked] $base"
    continue
  fi
  trap 'rm -f "$lockfile"' EXIT
  if [[ "$count" -ge "$MAX" ]]; then rm -f "$lockfile"; break; fi
  count=$((count + 1))

  ts="$(date -u +%FT%TZ)"
  echo "[$ts] >>> $base (vid=$vid)"

  # Download audio if missing.
  if [[ ! -s "$audio_wav" ]]; then
    if ! yt-dlp -q --no-warnings -x --audio-format wav \
        --postprocessor-args "-ar 16000 -ac 1" \
        -o "$AUDIO_DIR/${vid}.%(ext)s" \
        "https://www.youtube.com/watch?v=${vid}" 2>>"$LOG.err"; then
      echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"dl_fail\"}" >> "$LOG"
      rm -f "$lockfile"
      continue
    fi
  fi

  if [[ ! -s "$audio_wav" ]]; then
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"no_wav\"}" >> "$LOG"
    rm -f "$lockfile"
    continue
  fi

  # Transcribe with mlx-whisper. Outputs <basename>.{txt,srt} in --output-dir.
  t0="$(date +%s)"
  if mlx_whisper "$audio_wav" \
        --model "$MODEL" \
        --output-dir "$AUDIO_DIR" \
        --output-name "$vid" \
        --output-format all \
        --language en \
        --fp16 True \
        --verbose False \
        >>"$LOG.out" 2>&1; then
    t1="$(date +%s)"
    dt=$((t1 - t0))
    mv "$AUDIO_DIR/${vid}.txt" "$out_txt"
    mv "$AUDIO_DIR/${vid}.srt" "$out_srt"
    # Clean other mlx outputs (vtt/tsv/json) to save disk
    rm -f "$AUDIO_DIR/${vid}.vtt" "$AUDIO_DIR/${vid}.tsv" "$AUDIO_DIR/${vid}.json"
    rm -f "$audio_wav"
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"ok\",\"sec\":$dt,\"engine\":\"mlx\"}" >> "$LOG"
    echo "[$(date -u +%FT%TZ)] <<< $base ok (${dt}s)"
  else
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"whisper_fail\",\"engine\":\"mlx\"}" >> "$LOG"
    echo "[$(date -u +%FT%TZ)] <<< $base FAILED"
  fi
  rm -f "$lockfile"
done

echo "Done. Processed $count episode(s)."
