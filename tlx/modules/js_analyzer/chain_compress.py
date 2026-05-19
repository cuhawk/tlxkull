"""Exploit-chain compression + canonicalization.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §20.

A 20-hop chain through Redux dispatch / reducer / selector / hook /
ref forwarding adds zero exploit-relevant information per hop but
inflates LLM verdict-prompt tokens 5-10x. This module reduces chains
to a canonical narrative that *preserves every exploit-relevant
decision* (sanitizer attempts, parser-context transitions, origin
boundaries, persistence transitions) and collapses the boilerplate.

Inputs:
  chain: dict matching chains/all.jsonl rows. Required keys:
    - chain_id, path: list[hop], source, sink
    where hop has at minimum {"qname": str, "file": str, "line": int}
    Optional per-hop keys: kind, tag, sanitizer, parser_context_boundary,
    origin_boundary, storage_boundary, framework_summary.

Outputs:
  Mutates ``chain`` in place adding:
    - narrative: list[{hop, kind, qname, summary?, evidence?, ...}]
    - original_hop_count, compressed_hop_count, compression_ratio
    - decisions_preserved: list[str]
    - lost_evidence_count: int  (should be 0; >0 = bug or aggressive collapse)

Behind ``ENABLE_CHAIN_COMPRESSION`` (default ON; deterministic, additive).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Final

__all__ = [
    "compress",
    "compress_many",
    "render_narrative",
    "SUMMARIZERS",
]


# Per-framework summarizer patterns (§20.7). Match by sequence of
# trailing qname tokens; the matcher uses the last-name of each qname
# (so ``store.dispatch`` and ``dispatch`` both match).
SUMMARIZERS: Final[dict[str, list[dict[str, Any]]]] = {
    "redux": [
        {"match": ["dispatch", "reducer", "selector"],
         "summary": "Redux state flow"},
        {"match": ["dispatch", "thunk", "fetch"],
         "summary": "Redux thunk → network call"},
        {"match": ["dispatch", "reducer"],
         "summary": "Redux action → reducer"},
    ],
    "react": [
        {"match": ["setState", "useEffect", "ref"],
         "summary": "React state → effect → DOM ref"},
        {"match": ["useState_set", "useEffect"],
         "summary": "React state → effect"},
        {"match": ["useContext", "render"],
         "summary": "React context → render"},
    ],
    "vue": [
        {"match": ["commit", "mutation", "getter"],
         "summary": "Vuex state flow"},
        {"match": ["dispatch", "action", "commit"],
         "summary": "Vuex action → mutation"},
    ],
    "angular": [
        {"match": ["BehaviorSubject_next", "subscribe"],
         "summary": "RxJS subject → subscriber"},
        {"match": ["EventEmitter_emit", "subscribe"],
         "summary": "Angular EventEmitter → subscriber"},
    ],
    "next": [
        {"match": ["getServerSideProps", "props", "render"],
         "summary": "Next SSR props → render"},
        {"match": ["getStaticProps", "props", "render"],
         "summary": "Next SSG props → render"},
    ],
}


# Tag predicates — a hop carrying any of these is "must preserve":
# losing it would drop a decision the LLM needs.
_MUST_PRESERVE_KEYS: Final = frozenset((
    "sanitizer", "parser_context_boundary", "origin_boundary",
    "storage_boundary", "trust_boundary", "framework_summary",
    "is_source", "is_sink", "viability_override",
))


def _last_name(qname: str) -> str:
    if not qname:
        return ""
    return qname.rsplit(".", 1)[-1].rsplit("/", 1)[-1]


def _hop_must_preserve(hop: dict) -> bool:
    if hop.get("is_source") or hop.get("is_sink"):
        return True
    for k in _MUST_PRESERVE_KEYS:
        if hop.get(k):
            return True
    # Tags that the V1 chain extractor stamps:
    tag = hop.get("tag") or ""
    if any(s in tag for s in ("sanitizer", "purify", "escape", "encode")):
        return True
    return False


def _framework_passthrough(
    prev: dict, cur: dict, nxt: dict | None,
) -> tuple[str, str] | None:
    """If (prev, cur, nxt) match a summarizer pattern, return
    (framework, summary). The summarizer eats *cur* (and the matching
    sequence) — caller is responsible for merging.
    """
    if nxt is None:
        return None
    seq = [_last_name(prev.get("qname", "")),
           _last_name(cur.get("qname", "")),
           _last_name(nxt.get("qname", ""))]
    for fw, patterns in SUMMARIZERS.items():
        for pat in patterns:
            m = pat["match"]
            if len(m) > len(seq):
                continue
            # Sliding window match starting at index 0
            if all(_eq_token(a, b) for a, b in zip(m, seq)):
                return (fw, pat["summary"])
    return None


def _eq_token(pattern_tok: str, actual_tok: str) -> bool:
    """Pattern tokens are matched against the trailing qname or its
    common synonyms. Both literal equality and case-insensitive
    suffix match are accepted to handle minified bundles where
    ``a.dispatch`` becomes ``B.t``.
    """
    if not pattern_tok or not actual_tok:
        return False
    if pattern_tok == actual_tok:
        return True
    return actual_tok.lower().endswith(pattern_tok.lower())


def _equivalent_edge(prev: dict, cur: dict) -> bool:
    """Consecutive hops are equivalent (so cur is collapsible) when:
      * same qname (a self-loop or re-export wrapper);
      * cur is a pure pass-through wrapper (only forwards args).
    Conservative: never collapse across files.
    """
    if not prev or not cur:
        return False
    if prev.get("file") != cur.get("file"):
        return False
    if _last_name(prev.get("qname", "")) == _last_name(cur.get("qname", "")):
        return True
    return False


def _hop_evidence(hop: dict) -> dict:
    """Trim per-hop fields the LLM doesn't need but keep the address."""
    return {
        "file": hop.get("file"),
        "line": hop.get("line"),
        "qname": hop.get("qname"),
    }


@dataclass
class _Acc:
    out: list[dict] = field(default_factory=list)
    collapsed_qnames: list[str] = field(default_factory=list)
    decisions: set[str] = field(default_factory=set)
    lost_evidence_count: int = 0
    skip_next: int = 0


def _emit_source(acc: _Acc, hop: dict) -> None:
    acc.out.append({
        "hop": len(acc.out) + 1,
        "kind": "source",
        "qname": hop.get("qname"),
        "evidence": _hop_evidence(hop),
        "tag": hop.get("tag"),
    })
    acc.decisions.add("source")


def _emit_sink(acc: _Acc, hop: dict) -> None:
    acc.out.append({
        "hop": len(acc.out) + 1,
        "kind": "sink",
        "qname": hop.get("qname"),
        "evidence": _hop_evidence(hop),
        "tag": hop.get("tag"),
        "context": hop.get("context_class") or hop.get("context"),
    })
    acc.decisions.add("sink")


def _emit_preserved(acc: _Acc, hop: dict) -> None:
    kind = "passthrough"
    summary = None
    if hop.get("sanitizer"):
        kind = "sanitizer_attempt"
        summary = f"sanitizer attempt: {hop.get('sanitizer')}"
        acc.decisions.add("sanitizer_verdict")
    elif hop.get("parser_context_boundary"):
        kind = "parser_context_boundary"
        summary = f"context: {hop.get('context_class', 'unknown')}"
        acc.decisions.add("parser_context")
    elif hop.get("origin_boundary"):
        kind = "origin_boundary"
        summary = f"origin validation: {hop.get('validation_kind', 'unknown')}"
        acc.decisions.add("origin_validation")
    elif hop.get("storage_boundary"):
        kind = "storage_boundary"
        summary = f"persistence via {hop.get('api', 'storage')}"
        acc.decisions.add("storage_transition")
    elif hop.get("trust_boundary"):
        kind = "trust_boundary"
        summary = f"trust: {hop.get('trust_kind', 'unknown')}"
        acc.decisions.add("trust_boundary")
    elif hop.get("framework_summary"):
        kind = "framework_passthrough"
        summary = hop["framework_summary"]
        acc.decisions.add("framework_passthrough")
    acc.out.append({
        "hop": len(acc.out) + 1,
        "kind": kind,
        "qname": hop.get("qname"),
        "summary": summary,
        "evidence": _hop_evidence(hop),
    })


def compress(chain: dict) -> dict:
    """Compress one chain dict in place. Returns the same chain dict for
    chaining; new fields are additive — original ``path`` is untouched
    so the audit pipeline can still render the full hop list when an
    analyst asks.
    """
    path = chain.get("path") or []
    n = len(path)
    if n == 0:
        return chain
    acc = _Acc()
    # Source.
    _emit_source(acc, path[0])
    # Intermediate hops with summarization.
    i = 1
    while i < n - 1:
        if acc.skip_next > 0:
            acc.skip_next -= 1
            i += 1
            continue
        hop = path[i]
        nxt = path[i + 1] if i + 1 < n else None
        if _hop_must_preserve(hop):
            _emit_preserved(acc, hop)
            i += 1
            continue
        # Try framework summarization (3-grams).
        if nxt is not None and i + 1 < n - 1:
            fw_match = _framework_passthrough(path[i - 1] if i else hop,
                                              hop, nxt)
            if fw_match:
                fw, summary = fw_match
                # Collapse cur + nxt into a single framework_passthrough hop.
                acc.out.append({
                    "hop": len(acc.out) + 1,
                    "kind": "framework_passthrough",
                    "framework": fw,
                    "summary": summary,
                    "collapsed_qnames": [
                        hop.get("qname"),
                        nxt.get("qname"),
                    ],
                    "evidence": _hop_evidence(hop),
                })
                acc.decisions.add("framework_passthrough")
                acc.skip_next = 1   # consume nxt
                i += 1
                continue
        # Equivalent-edge collapse.
        if acc.out and _equivalent_edge(path[i - 1] if i else None, hop):
            acc.collapsed_qnames.append(hop.get("qname", ""))
            i += 1
            continue
        # Generic pass-through hop — drop, but record qname.
        acc.collapsed_qnames.append(hop.get("qname", ""))
        i += 1
    # Sink.
    if n >= 2:
        _emit_sink(acc, path[-1])
    elif n == 1:
        # Source == sink; rare.
        pass

    compressed_count = len(acc.out)
    chain["narrative"] = acc.out
    chain["original_hop_count"] = n
    chain["compressed_hop_count"] = compressed_count
    chain["compression_ratio"] = (
        round(1 - (compressed_count / n), 4) if n > 0 else 0.0
    )
    chain["decisions_preserved"] = sorted(acc.decisions)
    chain["lost_evidence_count"] = acc.lost_evidence_count
    chain["compressed_collapsed_qnames"] = acc.collapsed_qnames
    return chain


def compress_many(chains: list[dict]) -> list[dict]:
    """Convenience: compress an iterable of chain dicts in place."""
    return [compress(c) for c in chains]


def _enrich_string_path(chain: dict) -> dict:
    """Normalize chain shapes: when path is list[str] (bestfirst output),
    convert to list[hop dict] so :func:`compress` can run.

    Returns the same dict; mutates in place. Idempotent.
    """
    path = chain.get("path") or []
    if not path or isinstance(path[0], dict):
        return chain
    files = chain.get("path_files") or []
    src = chain.get("source") or {}
    sink = chain.get("sink") or {}
    hops: list[dict] = []
    n = len(path)
    for i, qname in enumerate(path):
        file = files[i] if i < len(files) else ""
        hop: dict = {"qname": qname, "file": file}
        if i == 0:
            hop["is_source"] = True
            hop["line"] = src.get("line")
            tax = src.get("taxonomy_id")
            if tax:
                hop["tag"] = tax
        if i == n - 1:
            hop["is_sink"] = True
            hop["line"] = sink.get("line")
            tax = sink.get("taxonomy_id")
            if tax:
                hop["tag"] = tax
        hops.append(hop)
    chain["path"] = hops
    chain["_path_was_strings"] = True
    return chain


def compress_chain(chain: dict) -> dict:
    """Public entry point that handles both bestfirst-style (path as
    list[str]) and enriched (path as list[dict]) chains.

    Adds ``narrative`` + ``compressed_hop_count`` + ``compression_ratio``
    fields to *chain* and returns it. Preserves the original path shape:
    when the input was list[str] (bestfirst-style), the path is restored
    after compression so other consumers (reporter, audit_pipeline) see
    the same view.
    """
    original_path = chain.get("path")
    _enrich_string_path(chain)
    compress(chain)
    if chain.pop("_path_was_strings", False):
        chain["path"] = original_path
    return chain


# ──────────────────────────────────────────────────────────────────────
# LLM-ready rendering
# ──────────────────────────────────────────────────────────────────────

def render_narrative(chain: dict) -> str:
    """Produce a compact markdown rendering for the audit prompt. The
    ChainIR already carries the structured narrative — this is for the
    "chain" section of the human-readable system prompt to the LLM.
    """
    narrative = chain.get("narrative") or []
    if not narrative:
        return ""
    lines: list[str] = []
    for entry in narrative:
        idx = entry.get("hop", "?")
        kind = entry.get("kind", "step")
        evd = entry.get("evidence") or {}
        loc = f"{evd.get('file', '?')}:{evd.get('line', '?')}"
        if kind == "source":
            lines.append(f"{idx}. SOURCE: {entry.get('qname')} at {loc}.")
        elif kind == "sink":
            ctx = entry.get("context") or "unknown context"
            lines.append(f"{idx}. SINK: {entry.get('qname')} at {loc} ({ctx}).")
        elif kind == "framework_passthrough":
            lines.append(
                f"{idx}. {entry.get('summary')} "
                f"({entry.get('framework')})."
            )
        elif kind == "sanitizer_attempt":
            lines.append(f"{idx}. {entry.get('summary')} at {loc}.")
        elif kind == "parser_context_boundary":
            lines.append(f"{idx}. {entry.get('summary')} at {loc}.")
        elif kind == "origin_boundary":
            lines.append(f"{idx}. {entry.get('summary')} at {loc}.")
        elif kind == "storage_boundary":
            lines.append(f"{idx}. {entry.get('summary')} at {loc}.")
        elif kind == "trust_boundary":
            lines.append(f"{idx}. {entry.get('summary')} at {loc}.")
        else:
            qn = entry.get("qname") or "(passthrough)"
            lines.append(f"{idx}. {qn} at {loc}.")
    return "\n".join(lines)


# CLI for ad-hoc compression of a chains/*.jsonl file.
if __name__ == "__main__":
    import argparse
    import sys
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="chains JSONL to compress")
    ap.add_argument("--out", default="-", help="output file or '-' for stdout")
    ap.add_argument("--render-md", action="store_true",
                    help="emit a markdown narrative block after each JSON line")
    args = ap.parse_args()

    out_stream = sys.stdout if args.out == "-" else open(args.out, "w", encoding="utf-8")
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                ch = json.loads(raw)
                compress(ch)
                out_stream.write(json.dumps(ch, ensure_ascii=False) + "\n")
                if args.render_md:
                    out_stream.write("---\n" + render_narrative(ch) + "\n---\n")
    finally:
        if out_stream is not sys.stdout:
            out_stream.close()
