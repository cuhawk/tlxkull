#!/usr/bin/env bash
# httpx liveness + fingerprint over (subs + hosts + new_ips).
# Inputs:  /opt/recon/out/subs/all.txt, /opt/recon/out/scan/hosts.txt, /opt/recon/out/resolve/new_ips.txt
# Outputs: /opt/recon/out/httpx/{targets.txt,httpx.json}
set -euo pipefail

OUT="/opt/recon/out/httpx"
mkdir -p "$OUT"

cat /opt/recon/out/subs/all.txt /opt/recon/out/scan/hosts.txt /opt/recon/out/resolve/new_ips.txt 2>/dev/null \
    | sort -u > "$OUT/targets.txt"

test -s "$OUT/targets.txt" || { echo "no targets for httpx" >&2; exit 0; }

httpx -silent -json \
    -status-code -title -tech-detect -tls-grab -content-length \
    -threads 50 -rate-limit 200 -timeout 10 -retries 1 \
    -ports 80,443,8080,8443,8000,8888 \
    -l "$OUT/targets.txt" -o "$OUT/httpx.json" || true

echo "httpx phase done; $(wc -l < "$OUT/httpx.json" 2>/dev/null || echo 0) live URLs" >&2
