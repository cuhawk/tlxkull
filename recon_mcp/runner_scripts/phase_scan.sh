#!/usr/bin/env bash
# Scan phase: masscan top-10k + remainder, dig/nslookup PTR, shodan host lookup.
# Inputs: /opt/recon/in/ips.txt (one IP or CIDR per line)
# Outputs: /opt/recon/out/scan/{masscan_top10k.json,masscan_rest.json,ptr.json,shodan.json,hosts.txt}
set -euo pipefail

IN="/opt/recon/in/ips.txt"
OUT="/opt/recon/out/scan"
mkdir -p "$OUT"
test -s "$IN" || { echo "no IP input; skipping" >&2; exit 0; }

masscan -iL "$IN" --top-ports 10000 --rate 5000 -oJ "$OUT/masscan_top10k.json" || true
masscan -iL "$IN" -p1-65535 --rate 2500 -oJ "$OUT/masscan_rest.json" || true

jq -r '.[]?.ip' "$OUT/masscan_top10k.json" "$OUT/masscan_rest.json" 2>/dev/null \
    | sort -u > "$OUT/hosts.txt" || true

: > "$OUT/ptr.json"
while read -r ip; do
    [ -z "$ip" ] && continue
    ptr=$(dig +short -x "$ip" | sed 's/\.$//' | head -n1 || true)
    nptr=$(nslookup "$ip" 2>/dev/null | awk -F'= ' '/name =/ {print $2}' | sed 's/\.$//' | head -n1 || true)
    jq -nc --arg ip "$ip" --arg dig "$ptr" --arg nslookup "$nptr" \
        '{ip: $ip, dig_ptr: $dig, nslookup_ptr: $nslookup}' >> "$OUT/ptr.json"
done < "$OUT/hosts.txt"

: > "$OUT/shodan.json"
if [ -n "${SHODAN_API_KEY:-}" ]; then
    shodan init "$SHODAN_API_KEY" >/dev/null
    while read -r ip; do
        [ -z "$ip" ] && continue
        out=$(shodan host --format json "$ip" 2>/dev/null || true)
        [ -n "$out" ] && echo "$out" >> "$OUT/shodan.json"
    done < "$OUT/hosts.txt"
fi

echo "scan phase done; $(wc -l < "$OUT/hosts.txt") live hosts" >&2
