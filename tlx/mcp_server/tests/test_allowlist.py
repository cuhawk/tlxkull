"""Allowlist sanity: identifiers + immutability."""
from __future__ import annotations

from mcp_server.allowlist import TOOL_ALLOWLIST


def test_allowlist_is_frozenset() -> None:
    assert isinstance(TOOL_ALLOWLIST, frozenset)


def test_allowlist_entries_are_valid_identifiers() -> None:
    bad = [n for n in TOOL_ALLOWLIST if not n.isidentifier()]
    assert not bad, f"non-identifier names in allowlist: {bad}"


def test_allowlist_no_duplicates_or_empty() -> None:
    assert TOOL_ALLOWLIST, "allowlist must not be empty"
    assert all(n and isinstance(n, str) for n in TOOL_ALLOWLIST)
