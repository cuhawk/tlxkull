import pytest
from recon_mcp.input_parser import Target, TargetKind
from recon_mcp.safety import (
    check_targets, SafetyError, MAX_CIDR_HOSTS, MAX_TARGETS_PER_JOB,
)


def test_small_cidr_ok():
    check_targets([Target(TargetKind.CIDR, "10.0.0.0/24")])


def test_huge_cidr_rejected():
    with pytest.raises(SafetyError, match="too large"):
        check_targets([Target(TargetKind.CIDR, "10.0.0.0/8")])


def test_too_many_targets_rejected():
    targets = [Target(TargetKind.IP, f"1.1.1.{i}") for i in range(MAX_TARGETS_PER_JOB + 1)]
    with pytest.raises(SafetyError, match="too many"):
        check_targets(targets)


def test_max_cidr_hosts_const_sane():
    assert MAX_CIDR_HOSTS >= 65536
