#!/usr/bin/env bash
# Idempotent recon-droplet bootstrap. Invoked once via cloud-init.
# Uses prebuilt release binaries everywhere to keep total bootstrap under ~2 min.
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
mkdir -p /var/lib/recon /opt/recon /opt/recon/out

apt-get update -y
apt-get install -y --no-install-recommends \
    masscan nmap dnsutils whois jq curl wget unzip ca-certificates rsync python3

# Pinned tool versions. Bump deliberately; @latest hides upstream breakage.
SUBFINDER_VER="2.6.6"
HTTPX_VER="1.6.10"
DNSX_VER="1.2.1"
AMASS_VER="4.2.0"
FEROX_VER="2.11.0"

fetch_zip() {
    local url="$1" extract_to="$2"
    local tmp; tmp="$(mktemp -d)"
    curl -fsSL -o "$tmp/a.zip" "$url"
    unzip -q -o "$tmp/a.zip" -d "$extract_to"
    rm -rf "$tmp"
}

# projectdiscovery prebuilt binaries (avoid go install -- building from source on a
# small droplet adds 5-10 min and frequently blows the bootstrap timeout).
fetch_zip "https://github.com/projectdiscovery/subfinder/releases/download/v${SUBFINDER_VER}/subfinder_${SUBFINDER_VER}_linux_amd64.zip" /tmp/subfinder
install -m 0755 /tmp/subfinder/subfinder /usr/local/bin/subfinder

fetch_zip "https://github.com/projectdiscovery/httpx/releases/download/v${HTTPX_VER}/httpx_${HTTPX_VER}_linux_amd64.zip" /tmp/httpx
install -m 0755 /tmp/httpx/httpx /usr/local/bin/httpx

fetch_zip "https://github.com/projectdiscovery/dnsx/releases/download/v${DNSX_VER}/dnsx_${DNSX_VER}_linux_amd64.zip" /tmp/dnsx
install -m 0755 /tmp/dnsx/dnsx /usr/local/bin/dnsx

# amass
fetch_zip "https://github.com/owasp-amass/amass/releases/download/v${AMASS_VER}/amass_Linux_amd64.zip" /tmp/amass
install -m 0755 /tmp/amass/amass_Linux_amd64/amass /usr/local/bin/amass

# feroxbuster (skipped at runtime if RECON_SKIP_PHASES=ferox, but install for parity)
fetch_zip "https://github.com/epi052/feroxbuster/releases/download/v${FEROX_VER}/x86_64-linux-feroxbuster.zip" /tmp/ferox
install -m 0755 /tmp/ferox/feroxbuster /usr/local/bin/feroxbuster

# SecLists shallow clone. Skip if ferox phase will not run, saves ~30s and ~150 MB.
if [ "${RECON_SKIP_SECLISTS:-0}" = "1" ]; then
    mkdir -p /opt/SecLists
else
    apt-get install -y --no-install-recommends git
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git /opt/SecLists
fi
# Wordlist used by phase_ferox.sh: /opt/SecLists/Discovery/Web-Content/raft-large-directories.txt

touch /var/lib/recon/bootstrap.done
