import pytest
from recon_mcp.input_parser import parse_targets, Target, TargetKind, InputError


def test_single_ip():
    assert parse_targets(["1.2.3.4"]) == [Target(kind=TargetKind.IP, value="1.2.3.4")]


def test_cidr_v4():
    assert parse_targets(["10.0.0.0/24"]) == [Target(kind=TargetKind.CIDR, value="10.0.0.0/24")]


def test_wildcard_domain():
    assert parse_targets(["*.example.com"]) == [Target(kind=TargetKind.WILDCARD, value="example.com")]


def test_strips_protocol_and_path():
    assert parse_targets(["https://*.foo.io/login"]) == [Target(kind=TargetKind.WILDCARD, value="foo.io")]


def test_mixed_input():
    result = parse_targets(["1.2.3.4", "10.0.0.0/16", "*.acme.io"])
    assert {t.kind for t in result} == {TargetKind.IP, TargetKind.CIDR, TargetKind.WILDCARD}


def test_rejects_empty_list():
    with pytest.raises(InputError, match="empty"):
        parse_targets([])


def test_rejects_bare_domain_without_wildcard():
    with pytest.raises(InputError, match="wildcard"):
        parse_targets(["example.com"])


def test_rejects_garbage():
    with pytest.raises(InputError):
        parse_targets(["not a target"])


def test_rejects_ipv6_cidr_for_now():
    with pytest.raises(InputError, match="IPv6"):
        parse_targets(["2001:db8::/32"])


def test_dedupes_input():
    result = parse_targets(["1.1.1.1", "1.1.1.1"])
    assert len(result) == 1


def test_cidr_normalizes_host_bits():
    assert parse_targets(["10.0.0.5/24"]) == [Target(kind=TargetKind.CIDR, value="10.0.0.0/24")]


def test_wildcard_case_normalized():
    assert parse_targets(["*.Foo.COM"]) == [Target(kind=TargetKind.WILDCARD, value="foo.com")]
