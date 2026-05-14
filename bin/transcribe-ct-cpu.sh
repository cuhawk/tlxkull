#!/usr/bin/env bash
# CPU-only second worker using whisper.cpp turbo-q5_0.
# Runs alongside bin/transcribe-ct.sh (mlx/Metal). Shares lockfile dir, picks
# whichever VTT not yet done / not locked. Lower throughput but independent
# compute path so net pipeline is faster.
# Usage: bin/transcribe-ct-cpu.sh [N]

set -uo pipefail

ROOT="/Users/soural/Documents/TLX/wiki/sources/podcasts/ct"
VTT_DIR="$ROOT"
OUT_DIR="$ROOT/whisper/transcripts"
AUDIO_DIR="$ROOT/whisper/audio_tmp"
LOG="$ROOT/whisper/_log.jsonl"
MODEL="/Users/soural/.cache/whisper-models/ggml-large-v3-turbo-q5_0.bin"
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
# Iterate REVERSE so this worker starts from newest eps, mlx from oldest.
# Reduces contention on the same vid early in the run.
for vtt in $(ls -1r "$VTT_DIR"/*.en.vtt); do
  base="$(basename "$vtt" .en.vtt)"
  vid="$(echo "$base" | sed -E 's/^[0-9]{8}_(.{11}).*/\1/')"
  out_txt="$OUT_DIR/${base}.txt"
  out_srt="$OUT_DIR/${base}.srt"
  audio_wav="$AUDIO_DIR/${vid}.wav"

  if [[ -s "$out_txt" ]]; then
    continue
  fi
  lockfile="$AUDIO_DIR/${vid}.lock"
  if ! ( set -o noclobber; echo "$$" > "$lockfile" ) 2>/dev/null; then
    continue
  fi
  trap 'rm -f "$lockfile"' EXIT
  if [[ "$count" -ge "$MAX" ]]; then rm -f "$lockfile"; break; fi
  count=$((count + 1))

  ts="$(date -u +%FT%TZ)"
  echo "[$ts] [CPU] >>> $base (vid=$vid)"

  if [[ ! -s "$audio_wav" ]]; then
    if ! yt-dlp -q --no-warnings -x --audio-format wav \
        --postprocessor-args "-ar 16000 -ac 1" \
        -o "$AUDIO_DIR/${vid}.%(ext)s" \
        "https://www.youtube.com/watch?v=${vid}" 2>>"$LOG.err"; then
      echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"dl_fail\",\"engine\":\"cpu\"}" >> "$LOG"
      rm -f "$lockfile"
      continue
    fi
  fi

  if [[ ! -s "$audio_wav" ]]; then
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"no_wav\",\"engine\":\"cpu\"}" >> "$LOG"
    rm -f "$lockfile"
    continue
  fi

  # CPU-only: disable Metal via env var, use 6 threads.
  t0="$(date +%s)"
  if GGML_METAL_DISABLED=1 whisper-cli \
        -m "$MODEL" \
        -f "$audio_wav" \
        -of "$AUDIO_DIR/${vid}" \
        -otxt -osrt \
        -l en \
        -t 6 -p 1 \
        >>"$LOG.out" 2>&1; then
    t1="$(date +%s)"
    dt=$((t1 - t0))
    mv "$AUDIO_DIR/${vid}.txt" "$out_txt"
    mv "$AUDIO_DIR/${vid}.srt" "$out_srt"
    rm -f "$audio_wav"
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"ok\",\"sec\":$dt,\"engine\":\"cpu\"}" >> "$LOG"
    echo "[$(date -u +%FT%TZ)] [CPU] <<< $base ok (${dt}s)"
  else
    echo "{\"ts\":\"$ts\",\"vid\":\"$vid\",\"base\":\"$base\",\"status\":\"whisper_fail\",\"engine\":\"cpu\"}" >> "$LOG"
    echo "[$(date -u +%FT%TZ)] [CPU] <<< $base FAILED"
  fi
  rm -f "$lockfile"
done

echo "[CPU] Done. Processed $count episode(s)."
