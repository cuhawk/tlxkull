#!/usr/bin/env bash
# Idempotent recon-droplet bootstrap. Invoked once via cloud-init.
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
mkdir -p /var/lib/recon /opt/recon /opt/recon/out

apt-get update -y
apt-get install -y --no-install-recommends \
    masscan nmap dnsutils whois jq curl wget git unzip ca-certificates \
    python3 python3-pip golang-go rsync

# projectdiscovery toolchain
export GOBIN=/usr/local/bin
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# amass
AMASS_VER="v4.2.0"
curl -fsSL -o /tmp/amass.zip "https://github.com/owasp-amass/amass/releases/download/${AMASS_VER}/amass_Linux_amd64.zip"
unzip -o /tmp/amass.zip -d /tmp/amass
install -m 0755 /tmp/amass/amass_Linux_amd64/amass /usr/local/bin/amass

# feroxbuster
FEROX_VER="2.11.0"
curl -fsSL -o /tmp/ferox.zip "https://github.com/epi052/feroxbuster/releases/download/v${FEROX_VER}/x86_64-linux-feroxbuster.zip"
unzip -o /tmp/ferox.zip -d /tmp/ferox
install -m 0755 /tmp/ferox/feroxbuster /usr/local/bin/feroxbuster

# shodan
pip3 install --break-system-packages shodan

# SecLists (shallow for speed)
git clone --depth 1 https://github.com/danielmiessler/SecLists.git /opt/SecLists
# Wordlist used by phase_ferox.sh: /opt/SecLists/Discovery/Web-Content/raft-large-directories.txt

touch /var/lib/recon/bootstrap.done
