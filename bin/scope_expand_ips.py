#!/usr/bin/env python3
"""Expand every CIDR / IP / IP-range in targets/scope_*_ip_cidr.txt into individual IPs.

Output: targets/scope_all_ips_expanded.txt
  - IPv4 CIDRs /16 and smaller expanded host-by-host (network + broadcast included).
  - IPv4 CIDRs larger than /16 (e.g. /8) skipped — too big, listed in skipped[].
  - IP ranges "A.B.C.D - E.F.G.H" expanded via summarize_address_range.
  - Bare IPs pass through.
  - IPv6 entries skipped entirely.
  - Deduped, sorted by integer IP value.
"""
MIN_PREFIX = 16
import ipaddress
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "targets"
FILES = [
    ROOT / "scope_hackerone_ip_cidr.txt",
    ROOT / "scope_bugcrowd_ip_cidr.txt",
    ROOT / "scope_intigriti_ip_cidr.txt",
]
OUT = ROOT / "scope_all_ips_expanded.txt"
RANGE_RE = re.compile(r"^\s*([\d.]+)\s*-\s*([\d.]+)\s*$")

ipv4: set[int] = set()
skipped: list[tuple[str, str]] = []

for f in FILES:
    if not f.is_file():
        continue
    for raw in f.read_text(errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        m = RANGE_RE.match(s)
        try:
            if m:
                lo = ipaddress.IPv4Address(m.group(1))
                hi = ipaddress.IPv4Address(m.group(2))
                for net in ipaddress.summarize_address_range(lo, hi):
                    for host in net:
                        ipv4.add(int(host))
            elif ":" in s:
                skipped.append((s, "ipv6 skipped"))
            elif "/" in s:
                net = ipaddress.ip_network(s, strict=False)
                if isinstance(net, ipaddress.IPv4Network):
                    if net.prefixlen < MIN_PREFIX:
                        skipped.append((s, f"prefix /{net.prefixlen} smaller than cap /{MIN_PREFIX}"))
                        continue
                    for host in net:
                        ipv4.add(int(host))
                else:
                    skipped.append((s, "ipv6 skipped"))
            else:
                addr = ipaddress.ip_address(s)
                if isinstance(addr, ipaddress.IPv4Address):
                    ipv4.add(int(addr))
                else:
                    skipped.append((s, "ipv6 skipped"))
        except ValueError as e:
            skipped.append((s, str(e)))

with OUT.open("w") as fh:
    for n in sorted(ipv4):
        fh.write(str(ipaddress.IPv4Address(n)) + "\n")

print(f"ipv4 expanded: {len(ipv4):,}")
print(f"skipped: {len(skipped)}")
for s, err in skipped[:20]:
    print(f"  {s!r}: {err}", file=sys.stderr)
print(f"output: {OUT}")
