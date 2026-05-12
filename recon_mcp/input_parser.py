"""Classify recon targets into IP, CIDR, or wildcard-domain."""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class TargetKind(str, Enum):
    IP = "ip"
    CIDR = "cidr"
    WILDCARD = "wildcard"


@dataclass(frozen=True)
class Target:
    kind: TargetKind
    value: str


class InputError(ValueError):
    pass


_DOMAIN_RE = re.compile(r"^(?:\*\.)?(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$", re.IGNORECASE)


def _strip(raw: str) -> str:
    raw = raw.strip()
    if "://" in raw:
        raw = urlparse(raw).netloc or urlparse(raw).path
    raw = raw.split("/", 1)[0] if not _looks_like_cidr(raw) else raw
    return raw.strip().rstrip(".")


def _looks_like_cidr(s: str) -> bool:
    return "/" in s and s.count(".") >= 1 and s.split("/")[-1].isdigit() and len(s.split("/")[-1]) <= 3


def _classify(token: str) -> Target:
    if "/" in token:
        try:
            net = ipaddress.ip_network(token, strict=False)
        except ValueError as e:
            raise InputError(f"bad CIDR: {token!r} ({e})") from e
        if net.version == 6:
            raise InputError(f"IPv6 not supported yet: {token!r}")
        return Target(TargetKind.CIDR, str(net))
    if token.startswith("*."):
        domain = token[2:]
        if not _DOMAIN_RE.match(domain):
            raise InputError(f"bad wildcard domain: {token!r}")
        return Target(TargetKind.WILDCARD, domain.lower())
    try:
        ip = ipaddress.ip_address(token)
    except ValueError:
        ip = None
    if ip is not None:
        if ip.version == 6:
            raise InputError(f"IPv6 not supported yet: {token!r}")
        return Target(TargetKind.IP, str(ip))
    if _DOMAIN_RE.match(token):
        raise InputError(f"bare domain {token!r} not allowed — pass as wildcard (*.{token})")
    raise InputError(f"unrecognized target: {token!r}")


def parse_targets(raw: list[str]) -> list[Target]:
    if not raw:
        raise InputError("empty target list")
    seen: set[tuple[TargetKind, str]] = set()
    out: list[Target] = []
    for r in raw:
        t = _classify(_strip(r))
        key = (t.kind, t.value)
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out
