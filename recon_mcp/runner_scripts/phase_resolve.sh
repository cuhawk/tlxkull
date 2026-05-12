#!/usr/bin/env bash
# Resolve all collected subdomains to IPs via dnsx bulk resolver. Reveals IPs missed
# by initial input. Replaces a serial `dig` loop (≥25 min on wildcard targets) with
# dnsx at ~500 qps (~2 min on the same input).
# Inputs:  /opt/recon/out/subs/all.txt
# Outputs: /opt/recon/out/resolve/{resolved.json,all_resolved_ips.txt,new_ips.txt}
set -euo pipefail

IN="/opt/recon/out/subs/all.txt"
ORIG_IPS="/opt/recon/in/ips.txt"
OUT="/opt/recon/out/resolve"
mkdir -p "$OUT"
test -s "$IN" || { echo "no subs to resolve" >&2; exit 0; }

# dnsx -a -resp: A records with response, -json: one JSON line per host.
# -t 500: 500 concurrent workers. -retry 2 covers transient resolver flakes.
dnsx -silent -a -resp -json -t 500 -retry 2 -l "$IN" -o "$OUT/resolved.json" || true

if [ -s "$OUT/resolved.json" ]; then
    # dnsx schema: {"host":"...","a":["1.2.3.4", ...]}; older builds nested under "all".
    jq -r '(.a // .all // [])[]?' "$OUT/resolved.json" | sort -u > "$OUT/all_resolved_ips.txt"
else
    : > "$OUT/all_resolved_ips.txt"
fi

if [ -s "$ORIG_IPS" ]; then
    sort -u "$ORIG_IPS" > "$OUT/orig_ips.sorted"
    comm -23 "$OUT/all_resolved_ips.txt" "$OUT/orig_ips.sorted" > "$OUT/new_ips.txt"
else
    cp "$OUT/all_resolved_ips.txt" "$OUT/new_ips.txt"
fi

echo "resolve phase done; $(wc -l < "$OUT/new_ips.txt") new IPs" >&2
