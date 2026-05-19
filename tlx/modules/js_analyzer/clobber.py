"""DOM clobbering engine.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §13.

Detects DOM-clobber gadget candidates by joining:
  * ``global_reads`` — reads from ``window.X`` / ``document.X`` /
    ``globalThis.X`` / unresolved bare identifiers in non-strict mode.
  * HTML sinks whose insertion mode allows ``id``/``name`` attributes
    (most do unless sanitizer config strips them).

Gadget shapes recognized: plain-id, nested-form, anchor-href,
object-data. The consumer's access pattern decides which shape is
exploitable.

Behind ``ENABLE_DOM_CLOBBER``.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Iterable

__all__ = [
    "GadgetShape",
    "ingest_global_reads",
    "synthesize_candidates",
    "BUNDLER_GLOBALS",
]


GadgetShape = str  # 'plain-id' | 'nested-form' | 'anchor-href' | 'object-data'


# Globals defined by the bundler — never clobber-able even if reachable.
BUNDLER_GLOBALS: frozenset[str] = frozenset((
    "__webpack_require__", "__webpack_modules__", "__webpack_exports__",
    "__webpack_chunk_load__", "webpackChunk_", "webpackJsonp",
    "__VITE_DEFINE__", "import_meta", "__esModule",
    "Symbol", "Reflect", "Proxy", "Promise", "Map", "Set",
    "Array", "Object", "String", "Number", "Boolean", "Date",
    "JSON", "Math", "RegExp", "Error", "TypeError",
))


def _looks_unguarded(snippet: str | None) -> bool:
    """Best-effort: a global access is "unguarded" when the surrounding
    code does NOT contain a typeof / hasOwnProperty / optional-chain
    check on the same name.
    """
    if not snippet:
        return True
    if re.search(r"typeof\s+\w+\s*[!=]==?\s*['\"]undefined['\"]", snippet):
        return False
    if "hasOwnProperty" in snippet or ".?." in snippet:
        return False
    if "?." in snippet:
        return False
    return True


def _classify_consumer(snippet: str | None) -> str:
    if not snippet:
        return "other"
    if re.search(r"\.(innerHTML|outerHTML|insertAdjacentHTML)", snippet):
        return "string-sink"
    if re.search(r"location\.(href|assign|replace)", snippet):
        return "navigate"
    if re.search(r"\b(fetch|axios|XMLHttpRequest)\b", snippet):
        return "data-fetch"
    if re.search(r"\(\s*[A-Za-z_]+\s*\)", snippet):
        return "function-call"
    return "config"


def ingest_global_reads(
    conn: sqlite3.Connection,
    records: Iterable[dict],
) -> int:
    """Populate ``global_reads`` from AST records tagged
    ``ast_kind == 'global_read'``.

    Record shape::

        {
          "ast_kind":     "global_read",
          "node_id":      int,
          "global_name":  "config",
          "access_path":  "window.config.api.endpoint",
          "snippet":      "...",        # nearby source for guard inference
          "consumer_node": int | None,
          "file":         str,
          "line":         int | None,
        }
    """
    cur = conn.cursor()
    inserted = 0
    for rec in records:
        if rec.get("ast_kind") != "global_read":
            continue
        name = rec.get("global_name")
        if not name or name in BUNDLER_GLOBALS:
            continue
        snippet = rec.get("snippet")
        cur.execute(
            """INSERT INTO global_reads
               (node_id, global_name, access_path, unguarded,
                consumer_kind, consumer_node, file, line)
               VALUES (?,?,?,?,?,?,?,?)""",
            (rec.get("node_id") or 0,
             name,
             rec.get("access_path") or name,
             int(_looks_unguarded(snippet)),
             _classify_consumer(snippet),
             rec.get("consumer_node"),
             rec.get("file") or "",
             rec.get("line")),
        )
        inserted += cur.rowcount
    conn.commit()
    return inserted


@dataclass(frozen=True)
class ClobberCandidate:
    html_sink_node: int
    global_read_id: int
    global_name: str
    gadget_shape: GadgetShape
    reachability_score: float
    rationale: str


# Decide a gadget shape from the consumer's access pattern. ``access_path``
# already encodes the consumer's dotted access; we pick the shape that
# best fits.
def _gadget_shape_for(access_path: str, consumer_kind: str) -> GadgetShape:
    ap = access_path.lower()
    if ap.endswith(".href") or "href" in ap:
        return "anchor-href"
    if ap.endswith(".action") or ".action" in ap:
        return "nested-form"
    if ap.endswith(".data"):
        return "object-data"
    if consumer_kind == "navigate":
        return "anchor-href"
    if consumer_kind == "function-call":
        return "plain-id"
    return "plain-id"


def synthesize_candidates(
    conn: sqlite3.Connection,
    *,
    sanitizer_allows_id_name: bool = True,
) -> list[ClobberCandidate]:
    """Join HTML sinks with global reads to produce candidates.

    Caller flag ``sanitizer_allows_id_name`` should reflect whether the
    target's effective sanitizer config strips ``id``/``name``. Default
    is True (DOMPurify default).
    """
    out: list[ClobberCandidate] = []
    if not sanitizer_allows_id_name:
        return out
    cur = conn.cursor()
    # HTML sinks the V1 taxonomy already tagged ``innerHTML_assign``,
    # ``document_write``, etc.
    cur.execute(
        """SELECT nt.node_id, n.file, n.start_line
           FROM   node_tags nt
           JOIN   nodes n ON n.id = nt.node_id
           WHERE  nt.taxonomy_id IN (
                  'innerHTML_assign','outerHTML_assign',
                  'document_write','document_writeln',
                  'insertAdjacentHTML','range_createContextualFragment',
                  'react_dangerouslySetInnerHTML','vue_v_html')""",
    )
    sinks = [(r[0], r[1], r[2]) for r in cur.fetchall()]
    if not sinks:
        return out
    cur.execute("SELECT id, node_id, global_name, access_path, consumer_kind, "
                "unguarded, file FROM global_reads WHERE unguarded=1")
    reads = cur.fetchall()
    for (read_id, _read_node, gname, access_path, ckind,
         _unguarded, _rfile) in reads:
        shape = _gadget_shape_for(access_path or gname, ckind or "")
        for (sink_node, _sfile, _sline) in sinks:
            # Conservative reachability: leave at 0.5 unless the caller
            # provides path-based scoring; the chain extractor refines.
            out.append(ClobberCandidate(
                html_sink_node=sink_node,
                global_read_id=read_id,
                global_name=gname,
                gadget_shape=shape,
                reachability_score=0.5,
                rationale=f"global {gname!r} read by {ckind} consumer; "
                          f"sink permits id/name",
            ))
    # Persist for chain renderer.
    for cand in out:
        cur.execute(
            """INSERT INTO clobber_candidates
               (html_sink_node, html_sink_attrs_allowed,
                global_read_id, gadget_shape, reachability_score)
               VALUES (?,?,?,?,?)""",
            (cand.html_sink_node, "id,name",
             cand.global_read_id, cand.gadget_shape,
             cand.reachability_score),
        )
    conn.commit()
    return out
