"""Pre-flight safety checks for recon jobs."""
from __future__ import annotations

import ipaddress

from .input_parser import Target, TargetKind


class SafetyError(Exception):
    pass


MAX_CIDR_HOSTS = 1 << 17  # /15 = 131072 hosts; /8 (16M) blocked
MAX_TARGETS_PER_JOB = 100


def check_targets(targets: list[Target]) -> None:
    if len(targets) > MAX_TARGETS_PER_JOB:
        raise SafetyError(f"too many targets ({len(targets)} > {MAX_TARGETS_PER_JOB})")
    for t in targets:
        if t.kind is TargetKind.CIDR:
            n = ipaddress.ip_network(t.value).num_addresses
            if n > MAX_CIDR_HOSTS:
                raise SafetyError(
                    f"CIDR {t.value} too large ({n} > {MAX_CIDR_HOSTS}); split into smaller blocks"
                )
