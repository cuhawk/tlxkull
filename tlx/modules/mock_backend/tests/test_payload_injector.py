"""Tests for mock_backend payload_injector (Phase 7B Task 1)."""
from __future__ import annotations

import json

from modules.mock_backend.core.payload_injector import (
    PayloadInjector,
    ProbeSpec,
    _bare_name,
)


def test_make_probe_returns_non_empty_probe_value():
    inj = PayloadInjector()
    chain = {
        "source_qname": "modules.app::user_input",
        "source_line": 12,
        "sink_type": "innerHTML",
    }
    spec = inj.make_probe(chain)
    assert isinstance(spec, ProbeSpec)
    assert spec.probe_value
    assert spec.probe_value.startswith("probe-xss-")
    assert len(spec.probe_value) == len("probe-xss-") + 8


def test_make_probe_unique_per_call():
    inj = PayloadInjector()
    chain = {"source_qname": "x::y", "source_line": 1, "sink_type": "eval"}
    a = inj.make_probe(chain)
    b = inj.make_probe(chain)
    assert a.probe_value != b.probe_value


def test_sentinel_for_is_deterministic():
    inj = PayloadInjector()
    a = inj.sentinel_for("chain-abc-123")
    b = inj.sentinel_for("chain-abc-123")
    c = inj.sentinel_for("chain-different")
    assert a == b
    assert a != c
    assert len(a) == 8


def test_rewrite_map_uses_bare_identifier_not_qualified():
    inj = PayloadInjector()
    chain = {
        "source_qname": "modules.controllers::handleQuery",
        "source_line": 7,
        "sink_type": "document.write",
    }
    spec = inj.make_probe(chain)
    assert "handleQuery" in spec.rewrite_map
    assert "modules.controllers::handleQuery" not in spec.rewrite_map
    # Replacement is a JSON-serialised literal so it can drop into JS source.
    assert spec.rewrite_map["handleQuery"] == json.dumps(spec.probe_value)


def test_make_probe_handles_missing_source_qname():
    inj = PayloadInjector()
    spec = inj.make_probe({})
    assert spec.source_qname == ""
    assert spec.rewrite_map == {}


def test_bare_name_strips_double_colon_and_dot():
    assert _bare_name("a::b::c") == "c"
    assert _bare_name("foo.bar") == "bar"
    assert _bare_name("foo") == "foo"


def test_custom_sentinel_prefix_used():
    inj = PayloadInjector(sentinel_prefix="canary-")
    spec = inj.make_probe({"source_qname": "f"})
    assert spec.probe_value.startswith("canary-")
