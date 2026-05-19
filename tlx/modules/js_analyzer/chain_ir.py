"""Canonical Chain IR — the payload the LLM stage consumes.

Plan: plans/ARCHITECTURE_EVOLUTION.md §11.

Replaces the current "raw chain JSON + whole-function snippets"
payload to ``claude_agent.analyse_chains_async``. Goal:

  * Sonnet receives a single coherent IR per chain (target context +
    source + sink + path + sanitizers + browser context + window
    snippets + open questions).
  * Sonnet does NOT re-derive static analysis from raw text.
  * Token cost drops ~5-10x (window snippets vs whole functions).

The IR is built by ``ChainIR.from_chain(chain, ctx)`` given a chain
dict from ``extract_chains_bounded`` / ``extract_chains_bestfirst``
and a ``BrowserContext`` (optional). It is consumed by
``claude_agent.py`` when ``ENABLE_LLM_CHAIN_IR`` is set; the old
payload remains the default until A/B verdict comparison is done.

Pure module — dataclasses + serialization. No LLM calls, no DB.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "TargetSummary",
    "SourceIR",
    "SinkIR",
    "PathHop",
    "SanitizerIR",
    "AsyncIR",
    "PropShapeIR",
    "RuntimeIR",
    "ChainIR",
    "from_chain",
]


# ── Sub-IR records ──────────────────────────────────────────────────────


@dataclass
class TargetSummary:
    name: str = ""
    framework: str | None = None
    rendering_model: str | None = None
    csp_present: bool = False
    csp_unsafe_inline: bool = False
    csp_unsafe_eval: bool = False
    trusted_types_enforced: bool = False
    library_versions: dict[str, str] = field(default_factory=dict)


@dataclass
class SourceIR:
    qname: str
    file: str
    line: int
    taxonomy_id: str
    controllability_score: float
    tag_source: str = "regex"          # 'regex' | 'ast' | 'implicit_closure' | 'continuation' | ...
    confidence: float = 1.0


@dataclass
class SinkIR:
    qname: str
    file: str
    line: int
    taxonomy_id: str
    severity: str = "high"
    exec_context: str | None = None
    parser_context: str | None = None
    trusted_types_guarded: bool = False
    viability_factor: float = 1.0
    confidence: float = 1.0


@dataclass
class PathHop:
    index: int
    qname: str
    file: str
    line: int
    kind: str                            # 'source' | 'sink' | 'intermediate' | 'sanitizer'
    edge_class: str = "sync"             # 'sync' | 'continuation'
    resolved_kind: str = "exact"
    confidence: float = 1.0


@dataclass
class SanitizerIR:
    sanitizer_id: str
    file: str
    line: int
    confidence: float = 1.0
    clears: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    library_version: str | None = None
    bypass_match: dict | None = None
    is_partial: bool = False


@dataclass
class AsyncIR:
    producer_kind: str
    caller_qname: str
    handler_qname: str
    line: int
    event_taint_paths: list[str] = field(default_factory=list)
    taint_through: bool = True


@dataclass
class PropShapeIR:
    qname: str
    base_var: str
    keys: list[str]
    confidence: float
    closed: bool


@dataclass
class RuntimeIR:
    sink_fired: bool = False
    eval_corpus_refs: list[str] = field(default_factory=list)
    postmessage_traces: list[dict] = field(default_factory=list)


@dataclass
class ChainIR:
    schema_version: int = 1
    chain_id: int | str = 0
    target: TargetSummary = field(default_factory=TargetSummary)
    source: SourceIR | None = None
    sink: SinkIR | None = None
    path: list[PathHop] = field(default_factory=list)
    sanitizers: list[SanitizerIR] = field(default_factory=list)
    asyncs: list[AsyncIR] = field(default_factory=list)
    dynamic_resolutions: list[PropShapeIR] = field(default_factory=list)
    runtime_evidence: RuntimeIR = field(default_factory=RuntimeIR)
    confidence: float = 0.0
    confidence_breakdown: dict = field(default_factory=dict)
    open_questions: list[str] = field(default_factory=list)
    snippet_windows: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# ── Construction ────────────────────────────────────────────────────────


def _target_summary_from(target_folder: str | Path, bctx) -> TargetSummary:
    name = Path(target_folder).name if target_folder else ""
    if bctx is None:
        return TargetSummary(name=name)
    libs: dict[str, str] = {}
    p = Path(target_folder) / "library_versions.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for k, v in data.items():
                if isinstance(v, dict) and v.get("version"):
                    libs[k] = str(v["version"])
        except Exception:
            pass
    return TargetSummary(
        name=name,
        framework=bctx.rendering.framework or None,
        rendering_model=bctx.rendering.model or None,
        csp_present=bool(bctx.csp.raw),
        csp_unsafe_inline=bool(bctx.csp.unsafe_inline_allowed),
        csp_unsafe_eval=bool(bctx.csp.unsafe_eval_allowed),
        trusted_types_enforced=bool(bctx.trusted_types.enforced),
        library_versions=libs,
    )


def _sink_capability(taxid: str) -> dict:
    try:
        from modules.js_analyzer.sink_viability import load_capabilities
        return load_capabilities().get(taxid, {})
    except Exception:
        return {}


def _open_questions(chain: dict) -> list[str]:
    """Surface analyzer-known unknowns so the LLM doesn't have to
    pattern-match for them."""
    out: list[str] = []
    src = chain.get("source", {}) or {}
    snk = chain.get("sink", {}) or {}
    if (src.get("tag_source") or "").startswith("implicit_") and src.get("confidence", 1.0) < 0.7:
        out.append("source is closure-expanded with low confidence — verify wrapper actually flows attacker data")
    if "continuation" in (src.get("tag_source") or ""):
        out.append("source is event-handler-derived — verify the producer (postMessage/.then/.subscribe) is reachable by an attacker")
    # depth uncertainty
    if int(chain.get("depth", 0)) > 6:
        out.append("path > 6 hops — chain confidence decays sharply; consider whether intermediate functions are pure")
    if chain.get("annotations"):
        for ann in chain["annotations"]:
            if ann.get("kind") == "partial_sanitizer":
                out.append("sanitizer on path is version- or config-weakened — bypass may apply")
    return out


def from_chain(
    chain: dict,
    *,
    target_folder: str | Path = "",
    snippets_whole: dict[str, str] | None = None,
    browser_context: Any = None,
    sanitizer_verdicts: list[dict] | None = None,
    source_root: str | Path | None = None,
) -> ChainIR:
    """Build a ChainIR from a raw chain dict.

    Args:
        chain: a row from chains/*.jsonl
        target_folder: per-target directory (for TargetSummary)
        snippets_whole: optional qname→whole-function-source map. Used
            only when window extraction can't read the underlying file.
        browser_context: optional ``BrowserContext`` instance.
        sanitizer_verdicts: pre-evaluated per-sanitizer registry verdicts.
        source_root: optional file-path prefix for window extraction.
    """
    target = _target_summary_from(target_folder, browser_context)

    src = chain.get("source") or {}
    snk = chain.get("sink") or {}
    cap = _sink_capability(snk.get("taxonomy_id", ""))
    viability = float(chain.get("viability_factor", 1.0))

    source_ir = SourceIR(
        qname=src.get("qname", ""),
        file=src.get("file", ""),
        line=int(src.get("line") or 0),
        taxonomy_id=src.get("taxonomy_id", ""),
        controllability_score=float(chain.get("confidence_breakdown", {}).get("p_source") or 0.0)
            or float(src.get("confidence", 1.0)),
        tag_source=src.get("tag_source", "regex"),
        confidence=float(src.get("confidence", 1.0)),
    )

    sink_ir = SinkIR(
        qname=snk.get("qname", ""),
        file=snk.get("file", ""),
        line=int(snk.get("line") or 0),
        taxonomy_id=snk.get("taxonomy_id", ""),
        severity=snk.get("severity", "high"),
        exec_context=cap.get("exec_context"),
        parser_context=cap.get("parser_context"),
        trusted_types_guarded=bool(cap.get("trusted_types_guarded")),
        viability_factor=viability,
        confidence=float(snk.get("confidence", 1.0)),
    )

    path_qnames = chain.get("path") or []
    path_files = chain.get("path_files") or []
    hops: list[PathHop] = []
    for i, q in enumerate(path_qnames):
        f = path_files[i] if i < len(path_files) else ""
        hops.append(PathHop(
            index=i,
            qname=q,
            file=f,
            line=0,                            # exact line filled when caller supplies it
            kind="source" if i == 0 else "sink" if i == len(path_qnames) - 1 else "intermediate",
            edge_class="continuation" if chain.get("has_continuation") and i > 0 else "sync",
            resolved_kind="exact",
            confidence=1.0,
        ))

    sanitizers: list[SanitizerIR] = []
    for sv in (sanitizer_verdicts or []):
        sanitizers.append(SanitizerIR(
            sanitizer_id=sv.get("sanitizer_id", ""),
            file=sv.get("file", ""),
            line=int(sv.get("line") or 0),
            confidence=float(sv.get("confidence", 1.0)),
            clears=list(sv.get("clears") or []),
            reasons=list(sv.get("reasons") or []),
            library_version=sv.get("library_version"),
            bypass_match=sv.get("bypass_match"),
            is_partial=float(sv.get("confidence", 1.0)) < 0.5,
        ))

    runtime = RuntimeIR(sink_fired=bool(chain.get("runtime_confirmed")))

    # Snippet windows: extract around source.line + sink.line + per-hop
    # call sites if known. Sanitizer landmarks too.
    try:
        from modules.js_analyzer.snippet_window import extract_chain_windows
        windows = extract_chain_windows(
            source_landmark=(source_ir.file, source_ir.line) if source_ir.file else ("", 0),
            sink_landmark=(sink_ir.file, sink_ir.line) if sink_ir.file else ("", 0),
            path_hops=[(h.file, h.line) for h in hops if h.file],
            sanitizer_landmarks=[(s.file, s.line) for s in sanitizers if s.file and s.line],
            source_root=source_root,
        )
    except Exception:
        windows = []

    ir = ChainIR(
        chain_id=chain.get("id", 0),
        target=target,
        source=source_ir,
        sink=sink_ir,
        path=hops,
        sanitizers=sanitizers,
        runtime_evidence=runtime,
        confidence=float(chain.get("p_chain") or chain.get("score", 0.0) / 100.0),
        confidence_breakdown=chain.get("confidence_breakdown") or {},
        open_questions=_open_questions(chain),
        snippet_windows=windows,
    )
    # If window extraction failed (mock chain, no real files) and the
    # caller passed whole-function snippets, fall back to them so the
    # LLM still has source text.
    if not ir.snippet_windows and snippets_whole:
        for q in path_qnames:
            src_text = snippets_whole.get(q)
            if src_text:
                ir.snippet_windows.append({
                    "file": q,
                    "note": "whole_function_fallback",
                    "text": src_text,
                })
    return ir
