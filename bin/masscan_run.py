#!/usr/bin/env python3
"""masscan wrapper — local or DigitalOcean droplet mode.

Spec: plans/PIPELINE_AUTO.md §masscan_run.

Usage:
    python3 bin/masscan_run.py --hosts <ip-list> --ports {web,full,<csv>} \
                               --mode {local,droplet} --output <jsonl>

Output format (jsonl, one record per open port):
    {"ip": "1.2.3.4", "port": 443, "proto": "tcp", "ts": "<iso>", "banner": "<optional>"}

Notes
-----
* Default rate = 5000 pps (overridable via --rate). Hard cap 50000.
* Refuses to start if --hosts exceeds memory.md > masscan_max_ips (default
  50000) without --force.
* `--ports full` requires --confirm-full to avoid accidental 65k sweeps.
* Local mode shells out to /usr/local/bin/masscan or `masscan` on PATH.
* Droplet mode is a stub that prints the recon MCP recipe — actual droplet
  spin-up should be added once the local path is stable.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

WEB_PORTS = "80,443,8080,8443,8000,8888,7443,9443,4443,8081,8181,8200,8888,9000,9001"

DEFAULT_MAX_IPS = 50000
DEFAULT_RATE = 5000
HARD_RATE_CAP = 50000


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def count_hosts(path: Path) -> int:
    n = 0
    with path.open() as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                n += 1
    return n


def resolve_ports(spec: str) -> str:
    if spec == "web":
        return WEB_PORTS
    if spec == "full":
        return "0-65535"
    # csv passthrough
    return spec


def run_local(hosts_file: Path, ports: str, rate: int, output: Path) -> None:
    masscan = shutil.which("masscan")
    if not masscan:
        sys.exit("masscan not found on PATH — install: brew install masscan / apt install masscan")

    # masscan native output → ndjson via -oJ; we post-process to our schema.
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    cmd = [
        masscan,
        "-iL", str(hosts_file),
        "-p", ports,
        "--rate", str(rate),
        "-oJ", str(tmp_path),
        "--wait", "5",
    ]
    print(f"[masscan_run] {' '.join(cmd)}")
    rc = subprocess.call(cmd)
    if rc != 0:
        sys.exit(f"masscan exited rc={rc}")

    # masscan -oJ writes a JSON array with trailing comma quirks; we use the
    # ndjson reader pattern that tolerates both.
    output.parent.mkdir(parents=True, exist_ok=True)
    n_open = 0
    with output.open("w") as out_f:
        for line in tmp_path.read_text(errors="replace").splitlines():
            s = line.strip().rstrip(",")
            if not s or s in {"[", "]"}:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError:
                continue
            ip = obj.get("ip")
            for port_entry in obj.get("ports", []):
                if port_entry.get("status") != "open":
                    continue
                rec = {
                    "ip": ip,
                    "port": port_entry.get("port"),
                    "proto": port_entry.get("proto", "tcp"),
                    "ts": now_utc(),
                }
                out_f.write(json.dumps(rec) + "\n")
                n_open += 1
    tmp_path.unlink(missing_ok=True)
    print(f"[masscan_run] {n_open} open ports → {output}")


def run_droplet(hosts_file: Path, ports: str, rate: int, output: Path) -> None:
    # Stub — print the recipe for now.
    print("[masscan_run] droplet mode is a stub.")
    print("  next steps to implement:")
    print("    1. recon_start with a custom 'masscan' phase, region matched to scope")
    print("    2. push hosts_file to droplet via cloud-init")
    print("    3. download /root/masscan.json after job done; post-process to", output)
    sys.exit(2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hosts", required=True, help="newline-delimited IP/CIDR file")
    ap.add_argument("--ports", default="web", help="web | full | csv (e.g. 80,443,8443)")
    ap.add_argument("--mode", choices=["local", "droplet"], default="local")
    ap.add_argument("--rate", type=int, default=DEFAULT_RATE)
    ap.add_argument("--output", required=True, help="ndjson output path")
    ap.add_argument("--max-ips", type=int, default=DEFAULT_MAX_IPS)
    ap.add_argument("--force", action="store_true", help="bypass --max-ips guard")
    ap.add_argument("--confirm-full", action="store_true", help="required for --ports full")
    args = ap.parse_args()

    hosts_path = Path(args.hosts)
    if not hosts_path.is_file():
        sys.exit(f"hosts file missing: {hosts_path}")
    n = count_hosts(hosts_path)
    print(f"[masscan_run] {n} hosts in {hosts_path}")
    if n > args.max_ips and not args.force:
        sys.exit(f"{n} hosts exceeds --max-ips {args.max_ips}; pass --force to override")
    if args.rate > HARD_RATE_CAP:
        sys.exit(f"--rate {args.rate} exceeds hard cap {HARD_RATE_CAP}")
    if args.ports == "full" and not args.confirm_full:
        sys.exit("--ports full requires --confirm-full")

    ports = resolve_ports(args.ports)
    output = Path(args.output)

    if args.mode == "local":
        run_local(hosts_path, ports, args.rate, output)
    else:
        run_droplet(hosts_path, ports, args.rate, output)


if __name__ == "__main__":
    main()
