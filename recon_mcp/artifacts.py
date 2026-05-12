"""Parse pulled-down phase outputs into a single structured summary."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_lines(p: Path) -> list[str]:
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text().splitlines() if l.strip()]


def _read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out: list[dict] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def summarize(root: Path) -> dict:
    out = root / "out"
    hosts = _summarize_hosts(out)
    return {
        "hosts": hosts,
        "subdomains": _read_lines(out / "subs" / "all.txt"),
        "new_ips_from_resolve": _read_lines(out / "resolve" / "new_ips.txt"),
        "http_endpoints": _summarize_httpx(out),
        "ferox_findings": _summarize_ferox(out),
    }


def _summarize_hosts(out: Path) -> list[dict]:
    ips = _read_lines(out / "scan" / "hosts.txt")
    masscan = _read_json(out / "scan" / "masscan_top10k.json") or []
    masscan_rest = _read_json(out / "scan" / "masscan_rest.json") or []
    ports_by_ip: dict[str, set[int]] = {}
    for entry in [*masscan, *masscan_rest]:
        ip = entry.get("ip")
        if not ip:
            continue
        for p in entry.get("ports", []):
            port = p.get("port")
            if port is not None:
                ports_by_ip.setdefault(ip, set()).add(int(port))
    ptr = {rec["ip"]: rec for rec in _read_jsonl(out / "scan" / "ptr.json")}
    return [
        {
            "ip": ip,
            "ports": sorted(ports_by_ip.get(ip, set())),
            "ptr": (ptr.get(ip, {}).get("dig_ptr") or ptr.get(ip, {}).get("nslookup_ptr") or None),
        }
        for ip in sorted(set(ips) | ports_by_ip.keys())
    ]


def _summarize_httpx(out: Path) -> list[dict]:
    return [
        {
            "url": r.get("url"),
            "status_code": r.get("status_code"),
            "title": r.get("title"),
            "tech": r.get("tech") or [],
            "tls": r.get("tls"),
        }
        for r in _read_jsonl(out / "httpx" / "httpx.json")
        if r.get("url")
    ]


def _summarize_ferox(out: Path) -> list[dict]:
    findings: list[dict] = []
    ferox_dir = out / "ferox"
    if not ferox_dir.exists():
        return findings
    for f in ferox_dir.glob("*.json"):
        for r in _read_jsonl(f):
            if r.get("type") != "response":
                continue
            findings.append({
                "url": r.get("url"),
                "status": r.get("status"),
                "content_length": r.get("content_length"),
            })
    return findings
