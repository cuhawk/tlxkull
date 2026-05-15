"""Adjacent-function gap analyzer (T1.1).

Given a security control qname (e.g. ``RequireRole``, ``csrf.verify``,
``DOMPurify.sanitize``), enumerate the functions that DO call the
control, then surface their siblings that DO NOT — the "forgotten
security control" class from
``wiki/techniques/recon/adjacent-function-gap.md``.

The output is shaped like a chain so the existing two-tier cascade
(``audit_pipeline.cascade_triage``) can gate the candidates before they
reach Opus.

Sibling-selection heuristic: same ``nodes.file`` AND same parent module
qname (computed by stripping the leaf segment of the caller qname). For
React components — files ending ``.jsx`` / ``.tsx`` — siblings are
co-defined components within the file.
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import asdict, dataclass
from typing import Iterable

from .callgraph import CallGraph


@dataclass
class CallerNode:
    id: int
    qname: str
    file: str
    name: str
    parent: str | None
    start_line: int | None
    end_line: int | None
    callsite_line: int | None  # line in caller where control is invoked


@dataclass
class SiblingNode:
    id: int
    qname: str
    file: str
    name: str
    parent: str | None
    start_line: int | None
    end_line: int | None
    calls_control: bool


def _parent_module(qname: str) -> str:
    """Strip the leaf segment to derive the parent module qname.

    ``foo.bar.handler`` → ``foo.bar``. Single-segment qnames return ``""``.
    """
    if "." not in qname:
        return ""
    return qname.rsplit(".", 1)[0]


def _is_component_file(file: str) -> bool:
    return file.endswith((".jsx", ".tsx"))


def find_control_callers(cg: CallGraph, control_qname: str) -> list[CallerNode]:
    """Return every function (caller) that has an edge to ``control_qname``.

    The same caller may appear multiple times if it invokes the control
    on multiple lines — we return the earliest callsite line and dedupe
    by caller id.
    """
    rows = cg.conn.execute(
        """
        SELECT n.id, n.qualified_name, n.file, n.name, n.parent,
               n.start_line, n.end_line, MIN(e.line) AS callsite_line
        FROM edges e
        JOIN nodes n  ON n.id  = e.caller_id
        JOIN nodes cn ON cn.id = e.callee_id
        WHERE cn.qualified_name = ?
        GROUP BY n.id
        ORDER BY n.qualified_name
        """,
        (control_qname,),
    ).fetchall()
    return [
        CallerNode(
            id=r[0],
            qname=r[1],
            file=r[2],
            name=r[3],
            parent=r[4],
            start_line=r[5],
            end_line=r[6],
            callsite_line=r[7],
        )
        for r in rows
    ]


def find_siblings(cg: CallGraph, caller: CallerNode) -> list[SiblingNode]:
    """Return functions in the same file + parent module as ``caller``."""
    parent = _parent_module(caller.qname)
    cur = cg.conn.execute(
        """
        SELECT id, qualified_name, file, name, parent, start_line, end_line
        FROM nodes
        WHERE file = ?
          AND id != ?
          AND kind IN ('function', 'method', 'arrow', 'component')
        """,
        (caller.file, caller.id),
    )
    out: list[SiblingNode] = []
    for r in cur.fetchall():
        sibling_qname = r[1]
        sibling_parent = _parent_module(sibling_qname)
        same_parent = parent and sibling_parent == parent
        same_component_file = _is_component_file(caller.file)
        if not (same_parent or same_component_file):
            continue
        out.append(
            SiblingNode(
                id=r[0],
                qname=sibling_qname,
                file=r[2],
                name=r[3],
                parent=r[4],
                start_line=r[5],
                end_line=r[6],
                calls_control=False,  # filled in by `mark_control_callers`
            )
        )
    return out


def mark_control_callers(
    cg: CallGraph, siblings: list[SiblingNode], control_qname: str
) -> None:
    """Set ``calls_control=True`` for siblings that already call the control."""
    if not siblings:
        return
    qmarks = ",".join("?" * len(siblings))
    rows = cg.conn.execute(
        f"""
        SELECT DISTINCT e.caller_id
        FROM edges e
        JOIN nodes cn ON cn.id = e.callee_id
        WHERE cn.qualified_name = ?
          AND e.caller_id IN ({qmarks})
        """,
        (control_qname, *(s.id for s in siblings)),
    ).fetchall()
    callers = {r[0] for r in rows}
    for s in siblings:
        if s.id in callers:
            s.calls_control = True


def _slug(text: str) -> str:
    safe = "".join(c if c.isalnum() else "_" for c in text)
    return safe.strip("_")[:40] or "unnamed"


def _severity_score(file: str, sibling_name: str) -> tuple[int, str]:
    """Heuristic severity ranking for gap chains.

    Boost API/route handlers, mutating verbs, admin/auth boundaries.
    Returns (score, severity-label).
    """
    s = 50
    name = sibling_name.lower()
    file_l = file.lower()
    if any(w in name for w in ("delete", "remove", "destroy", "drop", "purge")):
        s += 30
    if any(w in name for w in ("update", "patch", "edit", "set", "create", "post")):
        s += 20
    if any(w in name for w in ("admin", "owner", "internal", "private")):
        s += 25
    if any(w in name for w in ("get", "list", "fetch", "read")):
        s -= 5
    if any(w in file_l for w in ("/admin/", "/internal/", "/api/")):
        s += 15
    if any(w in file_l for w in ("/test", "__tests__", ".spec.", ".test.")):
        s -= 100
    label = (
        "critical" if s >= 90 else "high" if s >= 70 else "medium" if s >= 50 else "low"
    )
    return s, label


def gap_chain(
    control_qname: str, caller: CallerNode, sibling: SiblingNode
) -> dict:
    score, severity = _severity_score(sibling.file, sibling.name)
    cid = (
        "gap_"
        + _slug(control_qname)
        + "_"
        + hashlib.sha256(
            f"{control_qname}|{caller.qname}|{sibling.qname}".encode()
        ).hexdigest()[:10]
    )
    return {
        "id": cid,
        "kind": "gap",
        "control": control_qname,
        "fn_ok": caller.qname,
        "fn_gap": sibling.qname,
        "file": sibling.file,
        "score": score,
        "severity": severity,
        "source": {
            "qname": sibling.qname,
            "file": sibling.file,
            "line": sibling.start_line or 1,
            "taxonomy_id": f"gap_{_slug(control_qname)}",
        },
        "sink": {
            "qname": sibling.qname,
            "file": sibling.file,
            "line": sibling.end_line or sibling.start_line or 1,
            "taxonomy_id": f"missing_{_slug(control_qname)}",
        },
        "path": [sibling.qname],
        "depth": 1,
        "callsite_in_fn_ok": caller.callsite_line,
    }


def find_gaps(
    cg: CallGraph,
    control_qname: str,
    *,
    max_gaps: int | None = None,
    dedupe_by_fn_gap: bool = True,
) -> tuple[list[dict], dict]:
    """Top-level entry point — returns (gap_chains, stats).

    Each entry in ``gap_chains`` is a chain-shaped dict suitable for
    ``audit_pipeline.cascade_triage`` and downstream Opus audit.

    When ``dedupe_by_fn_gap`` is True (default) only one chain is kept
    per (control, fn_gap) pair — the one with the highest-severity
    caller as evidence. This keeps Opus budget tight; turn it off if you
    want the full evidence matrix.
    """
    callers = find_control_callers(cg, control_qname)
    if not callers:
        return [], {"control": control_qname, "callers_found": 0, "gaps_found": 0}

    seen_pairs: set[tuple[str, str]] = set()
    raw: list[dict] = []
    for caller in callers:
        siblings = find_siblings(cg, caller)
        mark_control_callers(cg, siblings, control_qname)
        for s in siblings:
            if s.calls_control:
                continue
            key = (caller.qname, s.qname)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            raw.append(gap_chain(control_qname, caller, s))

    raw.sort(key=lambda c: c["score"], reverse=True)
    if dedupe_by_fn_gap:
        chosen: dict[str, dict] = {}
        for c in raw:
            fg = c["fn_gap"]
            if fg not in chosen:
                chosen[fg] = c
        gaps = list(chosen.values())
    else:
        gaps = raw

    if max_gaps is not None:
        gaps = gaps[:max_gaps]
    stats = {
        "control": control_qname,
        "callers_found": len(callers),
        "gaps_unique": len({c["fn_gap"] for c in gaps}),
        "gaps_found": len(gaps),
        "evidence_pairs_total": len(raw),
        "max_gaps": max_gaps,
    }
    return gaps, stats


def gap_audit_prompt(
    control_qname: str,
    fn_gap_qname: str,
    fn_gap_snippet: str,
    sibling_callers_snippet: str,
    file_path: str,
) -> str:
    """Build the Opus audit prompt for a single gap candidate.

    Uses the longer template from
    ``wiki/techniques/recon/adjacent-function-gap.md`` verbatim, with the
    sibling snippets and the OK-path callsite injected.
    """
    return f"""You are reviewing the file at {file_path}.
A peer function FN_OK calls security control CONTROL = `{control_qname}`.
A sibling function FN_GAP = `{fn_gap_qname}` does NOT.

1. Compare FN_GAP to FN_OK and any other functions in the same module
   that touch the same resource class (same SDK method, same DB table,
   same route prefix, same RPC verb).
2. For each peer, state whether it invokes CONTROL or an equivalent
   sanitizer. Quote the exact line.
3. Output a JSON array of {{function, callsite_line, control_present:
   bool, reason}}.
4. Rank gaps by exploit severity assuming the missing control was
   intentional protection.

Watch for false-gap patterns:
- Control applied at framework middleware level (express.Router.use,
  Next.js middleware.ts).
- Control applied at proxy level (nginx / Caddy / Cloudflare).
- Control applied at SDK layer (auto-injected in gRPC/SDK wrappers).
If you can show evidence the control runs upstream, mark the gap NOT
exploitable and explain.

FN_GAP SOURCE:
{fn_gap_snippet}

SIBLING CALLERS WITH CONTROL:
{sibling_callers_snippet}

Return:
- verdict: "true_positive" | "false_positive" | "undetermined"
- reasoning: concise paragraph
- proposed_poc: HTTP request or browser steps if true_positive
"""


def to_serializable(callers: Iterable[CallerNode]) -> list[dict]:
    return [asdict(c) for c in callers]
