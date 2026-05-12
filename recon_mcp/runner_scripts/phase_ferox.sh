#!/usr/bin/env bash
# feroxbuster directory brute over each httpx-validated URL.
# Input:  /opt/recon/out/httpx/httpx.json
# Output: /opt/recon/out/ferox/<sanitized_host>.json
set -euo pipefail

IN="/opt/recon/out/httpx/httpx.json"
OUT="/opt/recon/out/ferox"
WORDLIST="/opt/SecLists/Discovery/Web-Content/raft-large-directories.txt"
mkdir -p "$OUT"

test -s "$IN" || { echo "no httpx results; skipping" >&2; exit 0; }
test -s "$WORDLIST" || { echo "wordlist missing: $WORDLIST" >&2; exit 1; }

jq -r '.url' "$IN" | sort -u | while read -r url; do
    [ -z "$url" ] && continue
    safe=$(echo "$url" | sed 's|https\?://||; s|[/:?&=]|_|g')
    feroxbuster --silent --json \
        --url "$url" \
        --wordlist "$WORDLIST" \
        --threads 30 \
        --depth 2 \
        --timeout 7 \
        --status-codes 200,204,301,302,307,401,403 \
        --output "$OUT/${safe}.json" \
        || true
done

echo "ferox phase done" >&2
