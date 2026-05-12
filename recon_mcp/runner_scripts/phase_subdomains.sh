#!/usr/bin/env bash
# Subdomain enum: amass passive, subfinder, c99.nl API, hackertarget reverse-IP.
# Inputs:
#   /opt/recon/in/domains.txt  (one apex per line)
#   /opt/recon/in/ips.txt      (for reverse-IP via hackertarget)
# Outputs: /opt/recon/out/subs/{amass.txt,subfinder.txt,c99.txt,reverseip.txt,all.txt}
set -euo pipefail

OUT="/opt/recon/out/subs"
mkdir -p "$OUT"

DOM="/opt/recon/in/domains.txt"
IPS="/opt/recon/in/ips.txt"

: > "$OUT/amass.txt"
: > "$OUT/subfinder.txt"
: > "$OUT/c99.txt"
: > "$OUT/reverseip.txt"

if [ -s "$DOM" ]; then
    while read -r d; do
        [ -z "$d" ] && continue
        amass enum -passive -d "$d" -timeout 5 >> "$OUT/amass.txt" || true
        subfinder -silent -d "$d" >> "$OUT/subfinder.txt" || true
        if [ -n "${C99_API_KEY:-}" ]; then
            curl -fsSL "https://api.c99.nl/subdomainfinder?key=${C99_API_KEY}&domain=${d}&json" \
                | jq -r '.subdomains[]?.subdomain' >> "$OUT/c99.txt" || true
        fi
    done < "$DOM"
fi

if [ -s "$IPS" ]; then
    while read -r ip; do
        [ -z "$ip" ] && continue
        curl -fsSL "https://api.hackertarget.com/reverseiplookup/?q=${ip}" \
            | grep -v 'API count' >> "$OUT/reverseip.txt" || true
        sleep 1
    done < "$IPS"
fi

cat "$OUT/amass.txt" "$OUT/subfinder.txt" "$OUT/c99.txt" "$OUT/reverseip.txt" \
    | tr '[:upper:]' '[:lower:]' | grep -E '^[a-z0-9.-]+\.[a-z]{2,}$' \
    | sort -u > "$OUT/all.txt"

echo "subdomain phase done; $(wc -l < "$OUT/all.txt") unique subs" >&2
