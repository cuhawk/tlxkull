#!/usr/bin/env bash
# Resolve all collected subdomains back to IPs. Reveals IPs missed by initial input.
# Inputs:  /opt/recon/out/subs/all.txt
# Outputs: /opt/recon/out/resolve/{resolved.json,new_ips.txt}
set -euo pipefail

IN="/opt/recon/out/subs/all.txt"
ORIG_IPS="/opt/recon/in/ips.txt"
OUT="/opt/recon/out/resolve"
mkdir -p "$OUT"
test -s "$IN" || { echo "no subs to resolve" >&2; exit 0; }

: > "$OUT/resolved.json"
while read -r host; do
    [ -z "$host" ] && continue
    ips=$(dig +short A "$host" | tr '\n' ',' | sed 's/,$//')
    [ -z "$ips" ] && continue
    jq -nc --arg h "$host" --arg ips "$ips" '{host: $h, ips: ($ips | split(","))}' >> "$OUT/resolved.json"
done < "$IN"

jq -r '.ips[]' "$OUT/resolved.json" | sort -u > "$OUT/all_resolved_ips.txt"
if [ -s "$ORIG_IPS" ]; then
    sort -u "$ORIG_IPS" > "$OUT/orig_ips.sorted"
    comm -23 "$OUT/all_resolved_ips.txt" "$OUT/orig_ips.sorted" > "$OUT/new_ips.txt"
else
    cp "$OUT/all_resolved_ips.txt" "$OUT/new_ips.txt"
fi

echo "resolve phase done; $(wc -l < "$OUT/new_ips.txt") new IPs" >&2
