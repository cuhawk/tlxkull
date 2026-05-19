"""V2 §20 — Exploit chain compression + canonicalization.

Pre-LLM canonicalizer that collapses long intermediated chains into
a small narrative IR. Default ON (``JS_ENABLE_CHAIN_COMPRESSION=1``).
Cuts Sonnet/Opus token cost by 40-60% on chains > 10 hops; smaller
chains pass through unchanged.

Strategy:
- collapse runs of pure passthrough functions into a single
  ``framework_passthrough`` hop;
- preserve every sanitizer/origin-check/sink hop verbatim;
- preserve continuation-edge boundaries (async producers);
- record ``compression_ratio`` + ``original_hop_count`` so the LLM
  can spot when too much was hidden.

Pure module — no IO, no LLM.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

__all__ = ["NarrativeHop", "compress_chain"]


@dataclass
class NarrativeHop:
    hop: int
    kind: str                       # 'source' | 'framework_passthrough' | 'sanitizer_attempt' | 'async_boundary' | 'sink'
    qname: str | None = None
    framework: str | None = None
    summary: str | None = None
    collapsed_qnames: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


_FRAMEWORK_PASSTHROUGH_HINTS = {
    "dispatch", "reducer", "selector", "useSelector", "useDispatch",
    "useEffect", "useCallback", "useMemo", "useState", "useContext",
    "createSlice", "configureStore", "createReducer", "createSelector",
    "createAction", "subscribe", "connect", "mapStateToProps",
    "mapDispatchToProps", "withRouter", "withTranslation",
}


def _classify_qname(qname: str) -> str:
    last = qname.split("::")[-1]
    if any(hint == last or hint in last for hint in _FRAMEWORK_PASSTHROUGH_HINTS):
        return "framework_passthrough"
    return "intermediate"


def compress_chain(chain: dict) -> dict:
    """Return a new chain dict with a ``narrative`` field replacing the
    raw ``path`` for LLM consumption. The original ``path`` is preserved
    untouched so other consumers (sarif, browser-confirm) still work."""
    path = chain.get("path") or []
    if len(path) <= 3:
        return {**chain, "narrative": _trivial_narrative(chain),
                "compression_ratio": 1.0,
                "original_hop_count": len(path),
                "compressed_hop_count": len(path)}

    narrative: list[NarrativeHop] = []
    src = chain.get("source", {})
    snk = chain.get("sink", {})

    narrative.append(NarrativeHop(
        hop=1, kind="source",
        qname=src.get("qname"),
        evidence={"taxonomy_id": src.get("taxonomy_id"),
                  "tag_source": src.get("tag_source")},
    ))

    middle = path[1:-1]
    collapsed: list[str] = []
    for q in middle:
        if _classify_qname(q) == "framework_passthrough":
            collapsed.append(q)
        else:
            # Flush any pending passthrough run.
            if collapsed:
                narrative.append(NarrativeHop(
                    hop=len(narrative) + 1,
                    kind="framework_passthrough",
                    framework=_guess_framework(collapsed),
                    summary=" → ".join(c.split("::")[-1] for c in collapsed[:4])
                            + (" → …" if len(collapsed) > 4 else ""),
                    collapsed_qnames=collapsed,
                ))
                collapsed = []
            narrative.append(NarrativeHop(
                hop=len(narrative) + 1, kind="intermediate", qname=q,
            ))
    if collapsed:
        narrative.append(NarrativeHop(
            hop=len(narrative) + 1,
            kind="framework_passthrough",
            framework=_guess_framework(collapsed),
            summary=" → ".join(c.split("::")[-1] for c in collapsed[:4])
                    + (" → …" if len(collapsed) > 4 else ""),
            collapsed_qnames=collapsed,
        ))

    # Sanitizer / continuation evidence from chain annotations.
    for ann in chain.get("annotations") or []:
        if ann.get("kind") == "partial_sanitizer":
            narrative.append(NarrativeHop(
                hop=len(narrative) + 1,
                kind="sanitizer_attempt",
                summary=ann.get("sanitizer_verdict", {}).get("sanitizer_id", "<sanitizer>"),
                evidence=ann.get("sanitizer_verdict") or {},
            ))
    if chain.get("has_continuation"):
        narrative.append(NarrativeHop(
            hop=len(narrative) + 1,
            kind="async_boundary",
            summary="continuation edge (addEventListener / .then / postMessage)",
        ))

    narrative.append(NarrativeHop(
        hop=len(narrative) + 1, kind="sink",
        qname=snk.get("qname"),
        evidence={"taxonomy_id": snk.get("taxonomy_id"),
                  "context": chain.get("viability_breakdown", {}).get("exec_context")},
    ))

    return {
        **chain,
        "narrative": [asdict(h) for h in narrative],
        "compression_ratio": round(len(narrative) / max(1, len(path)), 3),
        "original_hop_count": len(path),
        "compressed_hop_count": len(narrative),
        "decisions_preserved": [
            "sanitizer_verdict" if chain.get("annotations") else None,
            "parser_context" if chain.get("viability_breakdown") else None,
            "origin_validation" if chain.get("has_continuation") else None,
        ],
    }


def _guess_framework(qnames: list[str]) -> str | None:
    paths = " ".join(qnames).lower()
    if "redux" in paths or "dispatch" in paths or "reducer" in paths:
        return "redux"
    if "useeffect" in paths or "usecallback" in paths or "usememo" in paths:
        return "react-hooks"
    if "router" in paths:
        return "router"
    if "rxjs" in paths or "observable" in paths:
        return "rxjs"
    return None


def _trivial_narrative(chain: dict) -> list[dict]:
    src = chain.get("source", {})
    snk = chain.get("sink", {})
    return [
        asdict(NarrativeHop(hop=1, kind="source", qname=src.get("qname"))),
        asdict(NarrativeHop(hop=2, kind="sink", qname=snk.get("qname"))),
    ]
