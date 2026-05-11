"""Probe-payload generator for chain confirmation.

Pure deterministic. No LLM, no anthropic, no google.genai.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class ProbeSpec:
    source_qname: str
    probe_value: str
    rewrite_map: dict[str, str] = field(default_factory=dict)


def _bare_name(qname: str) -> str:
    if not qname:
        return qname
    for sep in ("::", "."):
        if sep in qname:
            qname = qname.rsplit(sep, 1)[-1]
    return qname


class PayloadInjector:
    def __init__(self, sentinel_prefix: str = "probe-xss-") -> None:
        self.sentinel_prefix = sentinel_prefix

    def make_probe(self, chain: dict) -> ProbeSpec:
        source_qname = str(chain.get("source_qname", ""))
        probe_value = f"{self.sentinel_prefix}{uuid4().hex[:8]}"
        bare = _bare_name(source_qname)
        rewrite_map: dict[str, str] = {}
        if bare:
            rewrite_map[bare] = json.dumps(probe_value)
        return ProbeSpec(
            source_qname=source_qname,
            probe_value=probe_value,
            rewrite_map=rewrite_map,
        )

    def sentinel_for(self, chain_id: str) -> str:
        digest = hashlib.sha256(chain_id.encode("utf-8")).hexdigest()
        return digest[:8]
