"""Two-tier audit cascade orchestrator (T1.2).

Wraps the existing ``analyse_chains_async`` audit loop with a Sonnet
triage gate. Chains the gate rejects are flagged as `false_positive`
with reason ``gate: sonnet_reject``; survivors are passed to the full
audit.

Per ``wiki/tools/karpathy/js-review-cascade.md`` this is the cost-saver
that drops per-chain cost from ~$0.30 (Opus) to ~$0.003 (Sonnet) for
the ~95% of chains that are obvious false positives.

Two cheap stages run before the LLM:
  1. Deterministic dead-code check — zero non-test inbound edges.
  2. Sonnet triage prompt — implements the cheap-stage rubric.

Cost and stats are returned in ``CascadeStats``; the caller persists
them to ``status.json.opus_cost_usd`` (Sonnet gate cost is a small
fraction of overall opus_cost — track separately as ``gate_cost_usd``).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Iterable

from pathlib import Path

from .claude_agent import sonnet_triage


# ---------------------------------------------------------------------------
# Long-context fallback (T1.3)
# ---------------------------------------------------------------------------

# Heuristic: ~4 characters per token across mixed JS/TS/JSON.
# Holds for unminified source; minified is ~3.5 chars/token.
DEFAULT_TOKEN_THRESHOLD = 800_000
DEFAULT_CHARS_PER_TOKEN = 4

# File extensions worth counting as in-scope for the audit prompt.
SOURCE_EXTS = (
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".vue", ".svelte", ".html", ".json",
)


def source_token_estimate(
    sources_root: Path,
    *,
    chars_per_token: int = DEFAULT_CHARS_PER_TOKEN,
    exts: tuple[str, ...] = SOURCE_EXTS,
) -> dict:
    """Walk ``sources_root`` and return a coarse token-count estimate.

    Returns a dict ``{files, bytes, est_tokens, by_ext}``. ``est_tokens``
    is bytes / chars_per_token — the cheap heuristic used to decide
    whether the bundle fits in a long-context model window.
    """
    if not sources_root.exists() or not sources_root.is_dir():
        return {"files": 0, "bytes": 0, "est_tokens": 0, "by_ext": {}}
    by_ext: dict[str, int] = {}
    total_files = 0
    total_bytes = 0
    for p in sources_root.rglob("*"):
        if not p.is_file():
            continue
        suffix = p.suffix.lower()
        if exts and suffix not in exts:
            continue
        try:
            sz = p.stat().st_size
        except OSError:
            continue
        total_files += 1
        total_bytes += sz
        by_ext[suffix] = by_ext.get(suffix, 0) + sz
    return {
        "files": total_files,
        "bytes": total_bytes,
        "est_tokens": total_bytes // chars_per_token,
        "by_ext": by_ext,
    }


def should_use_long_context(
    sources_root: Path,
    *,
    threshold: int = DEFAULT_TOKEN_THRESHOLD,
) -> tuple[bool, dict]:
    """Return (eligible, estimate). Eligible iff est_tokens <= threshold."""
    est = source_token_estimate(sources_root)
    return est["est_tokens"] <= threshold, est


@dataclass
class CascadeStats:
    total: int = 0
    rejected: int = 0
    escalated: int = 0
    rejected_dead_code: int = 0
    rejected_sonnet: int = 0
    gate_cost_usd: float = 0.0
    gate_duration_ms: int = 0
    parse_failures: int = 0


@dataclass
class CascadeResult:
    survivors: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    stats: CascadeStats = field(default_factory=CascadeStats)


def cascade_triage(
    chains: Iterable[dict],
    *,
    findings: dict,
    callgraph_db: sqlite3.Connection | None = None,
    model: str | None = None,
    skip_dead_code: bool = False,
) -> CascadeResult:
    """Run the cascade gate over ``chains``.

    Each chain is annotated under key ``_gate`` with the gate verdict
    payload (deterministic or Sonnet). Pass-through is a shallow merge —
    callers must treat ``chain`` as immutable from here.
    """
    res = CascadeResult()
    for chain in chains:
        res.stats.total += 1
        gate_payload: dict | None = None

        if not skip_dead_code and callgraph_db is not None:
            src_qname = (chain.get("source") or {}).get("qname")
            if src_qname and _is_dead_code(callgraph_db, src_qname):
                gate_payload = {
                    "verdict": "reject",
                    "deterministic": True,
                    "reason": "dead_code",
                }
                res.stats.rejected_dead_code += 1

        if gate_payload is None:
            gate_payload = sonnet_triage(chain=chain, findings=findings, model=model)
            res.stats.gate_cost_usd += gate_payload.get("cost_usd", 0.0)
            res.stats.gate_duration_ms += gate_payload.get("duration_ms", 0)
            if "error" in gate_payload:
                res.stats.parse_failures += 1
            if gate_payload["verdict"] == "reject":
                res.stats.rejected_sonnet += 1

        annotated = {**chain, "_gate": gate_payload}
        if gate_payload["verdict"] == "reject":
            res.rejected.append(annotated)
            res.stats.rejected += 1
        else:
            res.survivors.append(annotated)
            res.stats.escalated += 1
    return res


def _is_dead_code(conn: sqlite3.Connection, qname: str) -> bool:
    """True iff ``qname`` has zero non-test inbound edges in the callgraph."""
    row = conn.execute(
        """
        SELECT COUNT(*) FROM edges e
        JOIN nodes c ON c.id = e.caller_id
        WHERE e.callee_id = (SELECT id FROM nodes WHERE qualified_name = ?)
          AND c.file NOT LIKE '%/__tests__/%'
          AND c.file NOT LIKE '%.test.%'
          AND c.file NOT LIKE '%.spec.%'
          AND c.file NOT LIKE '%/test/%'
          AND c.file NOT LIKE '%/tests/%'
        """,
        (qname,),
    ).fetchone()
    return (row[0] if row else 0) == 0
