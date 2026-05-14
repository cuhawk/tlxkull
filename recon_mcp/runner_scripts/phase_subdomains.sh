#!/usr/bin/env bash
# Subdomain enum. Sources (all keyless / free):
#   - crt.sh CT logs (largest single source for most targets)
#   - shodan.io/domain/<apex> HTML scrape (no API key needed)
#   - subfinder (whatever free sources still work)
#   - amass enum passive
#   - c99.nl if C99_API_KEY set
#   - hackertarget reverse-IP if /opt/recon/in/ips.txt present
# Outputs: /opt/recon/out/subs/{crtsh,shodan,subfinder,amass,c99,reverseip,all}.txt
set -uo pipefail

OUT="/opt/recon/out/subs"
mkdir -p "$OUT"

DOM="/opt/recon/in/domains.txt"
IPS="/opt/recon/in/ips.txt"

: > "$OUT/crtsh.txt"
: > "$OUT/shodan.txt"
: > "$OUT/subfinder.txt"
: > "$OUT/amass.txt"
: > "$OUT/c99.txt"
: > "$OUT/reverseip.txt"

shodan_scrape() {
    # Anonymous shodan.io/domain/<apex> page lists subdomains under <ul id="subdomains">.
    local apex="$1"
    curl -fsSL -A "Mozilla/5.0" "https://www.shodan.io/domain/${apex}" 2>/dev/null \
        | python3 -c "
import sys
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.cap = False
    def handle_starttag(self, t, a):
        if t == 'ul' and ('id', 'subdomains') in a: self.cap = True
    def handle_endtag(self, t):
        if t == 'ul': self.cap = False
    def handle_data(self, d):
        if self.cap and d.strip(): print(d.strip())
p = P(); p.feed(sys.stdin.read())
" 2>/dev/null | sed "s/$/.${apex}/"
}

crtsh_query() {
    local apex="$1"
    curl -fsSL --max-time 60 "https://crt.sh/?q=%25.${apex}&output=json" 2>/dev/null \
        | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
seen = set()
for r in d:
    for n in r.get('name_value','').split('\n'):
        n = n.strip().lower().lstrip('*.')
        if n and not n.startswith('*'):
            seen.add(n)
for n in sorted(seen):
    print(n)
" 2>/dev/null
}

if [ -s "$DOM" ]; then
    while read -r d; do
        [ -z "$d" ] && continue
        crtsh_query "$d"     >> "$OUT/crtsh.txt"
        shodan_scrape "$d"   >> "$OUT/shodan.txt"
        subfinder -silent -d "$d" 2>/dev/null >> "$OUT/subfinder.txt"
        amass enum -passive -d "$d" -timeout 5 2>/dev/null >> "$OUT/amass.txt"
        if [ -n "${C99_API_KEY:-}" ]; then
            curl -fsSL "https://api.c99.nl/subdomainfinder?key=${C99_API_KEY}&domain=${d}&json" 2>/dev/null \
                | jq -r '.subdomains[]?.subdomain' >> "$OUT/c99.txt" || true
        fi
    done < "$DOM"
fi

if [ -s "$IPS" ]; then
    while read -r ip; do
        [ -z "$ip" ] && continue
        curl -fsSL "https://api.hackertarget.com/reverseiplookup/?q=${ip}" 2>/dev/null \
            | grep -v 'API count' >> "$OUT/reverseip.txt" || true
        sleep 1
    done < "$IPS"
fi

cat "$OUT/crtsh.txt" "$OUT/shodan.txt" "$OUT/subfinder.txt" "$OUT/amass.txt" \
    "$OUT/c99.txt" "$OUT/reverseip.txt" 2>/dev/null \
    | tr '[:upper:]' '[:lower:]' \
    | sed 's/^\*\.//' \
    | grep -E '^[a-z0-9.-]+\.[a-z]{2,}$' \
    | sort -u > "$OUT/all.txt"

per_source() {
    local f="$1" label="$2"
    [ -s "$f" ] && printf "  %-12s %5d\n" "$label" "$(wc -l < "$f")"
}
{
    echo "subdomains: $(wc -l < "$OUT/all.txt") unique"
    per_source "$OUT/crtsh.txt"     crtsh
    per_source "$OUT/shodan.txt"    shodan
    per_source "$OUT/subfinder.txt" subfinder
    per_source "$OUT/amass.txt"     amass
    per_source "$OUT/c99.txt"       c99
    per_source "$OUT/reverseip.txt" reverseip
} >&2
