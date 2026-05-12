#!/usr/bin/env bash
# httpx liveness + fingerprint over (subs + every ip:port masscan saw + resolved IPs).
# Feeding masscan's open-port map back into httpx catches services on non-standard
# ports (Elasticsearch:9200, Rails:3000, ActiveMQ:8161, etc.) that the previous
# hardcoded six-port list would have missed.
# Inputs:  /opt/recon/out/subs/all.txt
#          /opt/recon/out/scan/masscan_top10k.json + masscan_rest.json
#          /opt/recon/out/resolve/new_ips.txt
# Outputs: /opt/recon/out/httpx/{targets.txt,httpx.json}
set -euo pipefail

OUT="/opt/recon/out/httpx"
SCAN="/opt/recon/out/scan"
mkdir -p "$OUT"

# Build ip:port pairs from masscan JSON. masscan -oJ emits one object per finding
# with `ip` + `ports[].port`. Empty/missing files are skipped silently.
: > "$OUT/ip_ports.txt"
for f in "$SCAN/masscan_top10k.json" "$SCAN/masscan_rest.json"; do
    [ -s "$f" ] || continue
    jq -r '.[]? | .ip as $ip | (.ports[]? | "\($ip):\(.port)")' "$f" 2>/dev/null \
        || true
done | sort -u > "$OUT/ip_ports.txt"

# Hostname-only inputs get probed across a default port list (httpx applies these
# when no explicit port is supplied). ip:port inputs are probed exactly as given.
cat /opt/recon/out/subs/all.txt /opt/recon/out/resolve/new_ips.txt 2>/dev/null \
    | sort -u > "$OUT/hosts.txt"

cat "$OUT/hosts.txt" "$OUT/ip_ports.txt" 2>/dev/null \
    | awk 'NF' | sort -u > "$OUT/targets.txt"

test -s "$OUT/targets.txt" || { echo "no targets for httpx" >&2; exit 0; }

# Default ports apply only to hostname rows (rows with a port are kept verbatim).
# Wider port list than before; httpx is cheap once a target is reachable.
httpx -silent -json \
    -status-code -title -tech-detect -tls-grab -content-length -web-server \
    -threads 50 -rate-limit 200 -timeout 10 -retries 1 -follow-redirects \
    -ports 80,443,8000,8008,8080,8081,8443,8888,3000,5000,7000,7001,9000,9090,9200,10443 \
    -l "$OUT/targets.txt" -o "$OUT/httpx.json" || true

echo "httpx phase done; $(wc -l < "$OUT/httpx.json" 2>/dev/null || echo 0) live URLs" >&2
