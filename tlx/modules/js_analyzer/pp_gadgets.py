"""Prototype-pollution gadget discovery (§14).

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §14.

V1 already detects prototype-pollution **writes** (sinks). What's
missing is the *gadget* — code that *reads* a polluted property and
uses it in a real sink. Without a gadget, a pollution chain is
informational; with one, it's high severity.

Pieces:
  * ``implicit_lookups`` table — every ``obj[k]`` with non-literal k.
  * ``pp_gadgets`` table — framework gadget catalog loaded from
    ``taxonomies/pp_gadgets.json``.
  * ``ingest_implicit_lookups()`` — fills ``implicit_lookups`` from
    AST records.
  * ``seed_gadget_catalog()`` — copies catalog rows into the per-target
    DB so chain-extractor joins work locally.
  * ``match_chains()`` — two-pass BFS (§14.9) producing
    ``chains/pp.jsonl``-style records.

Behind ``ENABLE_PP_GADGETS``.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

__all__ = [
    "ingest_implicit_lookups",
    "seed_gadget_catalog",
    "match_chains",
    "load_catalog",
    "Gadget",
    "PPMatch",
]


_CATALOG_PATH = (
    Path(__file__).resolve().parent / "taxonomies" / "pp_gadgets.json"
)


@dataclass(frozen=True)
class Gadget:
    framework: str
    version_range: str
    key_path: str
    gadget_kind: str
    rationale: str
    confidence: float


def load_catalog(path: str | None = None) -> list[Gadget]:
    p = Path(path) if path else _CATALOG_PATH
    if not p.exists():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    out: list[Gadget] = []
    for row in raw.get("gadgets", []):
        out.append(Gadget(
            framework      = row["framework"],
            version_range  = row.get("version_range") or "*",
            key_path       = row["key_path"],
            gadget_kind    = row["gadget_kind"],
            rationale      = row.get("rationale", ""),
            confidence     = float(row.get("confidence", 0.8)),
        ))
    return out


def ingest_implicit_lookups(
    conn: sqlite3.Connection,
    records: Iterable[dict],
) -> int:
    """Record every ``obj[k]`` whose key is non-literal.

    Record shape::

        {
          "ast_kind":      "implicit_lookup",
          "node_id":       int,
          "object_origin": "param"|"import"|"this"|"globalThis"|"literal",
          "key_kind":      "string-literal"|"computed"|"destructure"|"spread",
          "key_value":     str | None,        # when literal
          "has_default":   bool,
          "has_typeof_guard": bool,
          "consumer_kind": "function-call"|"render"|"navigate"|"set-prop"|"eval",
          "consumer_node": int | None,
          "file":          str,
          "line":          int | None,
        }
    """
    cur = conn.cursor()
    inserted = 0
    for rec in records:
        if rec.get("ast_kind") != "implicit_lookup":
            continue
        cur.execute(
            """INSERT INTO implicit_lookups
               (node_id, object_origin, key_kind, key_value,
                has_default, has_typeof_guard, consumer_kind,
                consumer_node, file, line)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (rec.get("node_id") or 0,
             rec.get("object_origin"),
             rec.get("key_kind") or "computed",
             rec.get("key_value"),
             int(bool(rec.get("has_default"))),
             int(bool(rec.get("has_typeof_guard"))),
             rec.get("consumer_kind"),
             rec.get("consumer_node"),
             rec.get("file") or "",
             rec.get("line")),
        )
        inserted += cur.rowcount
    conn.commit()
    return inserted


def seed_gadget_catalog(conn: sqlite3.Connection) -> int:
    """Copy the JSON catalog into the per-target DB so chain-extractor
    joins work locally. Idempotent.
    """
    cur = conn.cursor()
    cur.execute("DELETE FROM pp_gadgets")     # always refresh
    rows = 0
    for g in load_catalog():
        cur.execute(
            """INSERT INTO pp_gadgets
               (framework, version_range, key_path, gadget_kind,
                rationale, confidence)
               VALUES (?,?,?,?,?,?)""",
            (g.framework, g.version_range, g.key_path, g.gadget_kind,
             g.rationale, g.confidence),
        )
        rows += 1
    conn.commit()
    return rows


@dataclass
class PPMatch:
    write_node: int
    write_key_path: str
    gadget: Gadget
    sink_node: int
    score: float
    rationale: str


def _gadget_confidence(
    gadget: Gadget,
    write_key_path: str | None,
    lookup_row: dict,
    framework_set: frozenset[str],
) -> float:
    score = gadget.confidence
    if gadget.framework not in framework_set:
        # Reduce, don't drop — framework detection may miss minor libs.
        score *= 0.6
    # Lookup-side discounts:
    if lookup_row.get("has_default"):
        score *= 0.7
    if lookup_row.get("has_typeof_guard"):
        score *= 0.5
    # Write-side confidence: keyless write (`obj[]`) treated as more
    # permissive than `obj.x`.
    if write_key_path and write_key_path.endswith("[]"):
        score *= 1.1
    return round(min(1.0, max(0.05, score)), 3)


def match_chains(
    conn: sqlite3.Connection,
    *,
    framework_set: frozenset[str] = frozenset(),
    max_matches: int = 1000,
) -> list[PPMatch]:
    """Two-pass join (§14.9):

      Pass A — every pollution write (taxonomy_id IN pp_write_*).
      Pass B — every implicit_lookup keyed on a string that matches a
               catalog gadget's key_path tail.
      Join   — same key tail; emit ``PPMatch`` with confidence.
    """
    cur = conn.cursor()
    cur.execute(
        """SELECT nt.node_id, nt.evidence, n.file, n.start_line
           FROM   node_tags nt
           JOIN   nodes n ON n.id = nt.node_id
           WHERE  nt.taxonomy_id LIKE 'pp_write%'
           LIMIT  ?""",
        (max_matches,),
    )
    writes = cur.fetchall()
    if not writes:
        return []
    cur.execute("SELECT * FROM pp_gadgets")
    gadgets_db = cur.fetchall()
    if not gadgets_db:
        seed_gadget_catalog(conn)
        cur.execute("SELECT * FROM pp_gadgets")
        gadgets_db = cur.fetchall()
    catalog: list[Gadget] = [
        Gadget(framework=r[1], version_range=r[2], key_path=r[3],
               gadget_kind=r[4], rationale=r[5] or "",
               confidence=float(r[6] or 0.8))
        for r in gadgets_db
    ]
    cur.execute(
        "SELECT id, node_id, key_value, consumer_kind, "
        "has_default, has_typeof_guard, file, line, consumer_node "
        "FROM implicit_lookups WHERE key_value IS NOT NULL "
        "LIMIT ?",
        (max_matches,),
    )
    lookups = cur.fetchall()
    out: list[PPMatch] = []
    for (write_node, evidence, _wfile, _wline) in writes:
        # Pollution writes don't always record the key path explicitly;
        # use the evidence string as a fallback. The chain extractor
        # downstream refines this.
        write_key_path = (evidence or "").strip().split()[-1] if evidence else None
        for (_lid, lookup_node, key_value, consumer_kind,
             has_default, has_typeof_guard, _file, _line, _cnode) in lookups:
            for g in catalog:
                key_tail = g.key_path.rsplit(".", 1)[-1]
                if not key_value:
                    continue
                if key_tail and (key_tail == key_value
                                 or key_value.endswith(key_tail)):
                    score = _gadget_confidence(
                        g, write_key_path,
                        {"has_default": has_default,
                         "has_typeof_guard": has_typeof_guard},
                        framework_set,
                    )
                    out.append(PPMatch(
                        write_node=write_node,
                        write_key_path=write_key_path or "",
                        gadget=g,
                        sink_node=lookup_node,
                        score=score,
                        rationale=f"{g.framework} gadget: {g.rationale}",
                    ))
                    if len(out) >= max_matches:
                        return out
    return out
