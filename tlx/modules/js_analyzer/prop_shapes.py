"""Property-shape inference engine.

Plan: plans/ARCHITECTURE_EVOLUTION.md §2 (Dynamic property resolution).

The static AST extractor today emits ``dynamic`` edges for any
``sinkMap[op]()`` / ``window[fn]()`` / ``obj[user]()`` call. Taint
stops at the call site. This module gives those edges a chance to be
*refined* into concrete edges by:

  1. Walking every ``ObjectExpression`` / ``ClassDeclaration`` and
     recording the literal key set of the base variable. → ``prop_shapes``
  2. Tracking, per function, a string lattice (see ``string_lattice.py``)
     for every variable. ``const k = "foo"`` ⇒ ``Const("foo")``. → ``string_facts``
  3. Resolving ``obj[k]()`` at the consumer site: look up
     ``prop_shapes[obj]``, intersect with the lattice of ``k``, and
     emit refined edges with confidence
     ``(keys_confidence × match_ratio)``.

Resolution caps at 8 refinements per call site (configurable). Above
that the edge stays ``dynamic_overapprox`` with confidence 0.2.

Two entry points:

  ingest_object_keys(conn)  — Phase A: populate prop_shapes from existing
                             nodes' raw text (heuristic — AST emit is
                             the ideal upstream).
  ingest_string_facts(conn) — Phase B: populate string_facts from
                             ``const X = "..."`` declarations.
  refine_dynamic_edges(conn) — Phase D3: rewrite edges.resolved_kind
                             from 'dynamic' → 'prop_shape' (or
                             'dynamic_overapprox' on overflow).
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from .string_lattice import StringLattice


__all__ = [
    "ingest_object_keys",
    "ingest_string_facts",
    "refine_dynamic_edges",
    "PropShape",
    "MAX_REFINEMENT_PER_CALLSITE",
    "MAX_REFINEMENT_TOTAL",
]


MAX_REFINEMENT_PER_CALLSITE = 8
MAX_REFINEMENT_TOTAL = 20_000


@dataclass
class PropShape:
    node_id: int
    base_var: str
    line: int
    shape_kind: str           # object_literal | class_inst | param | import | unknown
    keys: list[str] = field(default_factory=list)
    keys_confidence: float = 1.0
    closed: bool = True
    evidence_lines: list[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase A: ObjectExpression / ClassDeclaration key harvesting
# ---------------------------------------------------------------------------


# var foo = { a: ..., 'b': ..., "c": ... }
_OBJECT_DECL_RE = re.compile(
    r"\b(?:var|let|const)\s+(?P<lhs>[A-Za-z_$][\w$]*)\s*=\s*\{"
    r"(?P<body>[^{}](?:[^{}]|\{[^{}]*\}){0,4000})\}",
    re.DOTALL,
)
# Field names: a:, 'a':, "a":, [computed-expr]:
_KEY_RE = re.compile(
    r"(?:[\{\,\(\s])\s*"
    r"(?:(?:'([^']{1,80})')|(?:\"([^\"]{1,80})\")|([A-Za-z_$][\w$]*))"
    r"\s*:",
)

# Dynamic add: obj["x"] = ...; obj.y = ...; Object.defineProperty(obj, "z", ...)
_DYNAMIC_ADD_RE = re.compile(
    r"(?P<base>[A-Za-z_$][\w$]*)\s*"
    r"(?:\[\s*(?:'(?P<key1>[^']+)'|\"(?P<key2>[^\"]+)\")\s*\]|"
    r"\.(?P<key3>[A-Za-z_$][\w$]*))\s*=",
)


def _harvest_object_decls(raw: str) -> list[tuple[str, list[str], bool, int]]:
    """Return [(base_var, keys, closed?, body_offset), ...].

    raw is a function-body or file-level snippet.
    """
    out: list[tuple[str, list[str], bool, int]] = []
    for m in _OBJECT_DECL_RE.finditer(raw):
        base = m.group("lhs")
        body = m.group("body")
        keys: list[str] = []
        for km in _KEY_RE.finditer(body):
            k = next((g for g in km.groups() if g), None)
            if k:
                keys.append(k)
        if not keys:
            continue
        # Detect dynamic adds to the same base later in the snippet.
        closed = True
        for da in _DYNAMIC_ADD_RE.finditer(raw[m.end():]):
            if da.group("base") == base:
                closed = False
                k = da.group("key1") or da.group("key2") or da.group("key3")
                if k and k not in keys:
                    keys.append(k)
        out.append((base, keys, closed, m.start()))
    return out


def ingest_object_keys(
    conn: sqlite3.Connection, *, sources_root: str | None = None
) -> int:
    """Scan every node's source slice + harvest object key sets.

    Returns the number of prop_shapes rows persisted. Idempotent: existing
    rows for the same (node_id, base_var, line) are overwritten.
    """
    # We rely on file_hashes / edges.raw to provide the surface text;
    # for accuracy on minified bundles, prefer raw file reads from
    # nodes.file + [start_line..end_line].
    rows = conn.execute(
        "SELECT id, file, start_line, end_line FROM nodes "
        "WHERE start_line IS NOT NULL AND end_line IS NOT NULL"
    ).fetchall()
    saved = 0
    cur = conn.cursor()
    root = sources_root  # caller may pass target/sources for the lookup
    file_cache: dict[str, list[str] | None] = {}
    for node_id, file, start, end in rows:
        if not file:
            continue
        lines = file_cache.get(file)
        if lines is None:
            try:
                from pathlib import Path
                candidates = [Path(file)]
                if root:
                    candidates.insert(0, Path(root) / file)
                text: str | None = None
                for c in candidates:
                    if c.exists() and c.is_file():
                        text = c.read_text(encoding="utf-8", errors="replace")
                        break
                lines = (text or "").splitlines()
            except Exception:
                lines = []
            file_cache[file] = lines
        if not lines:
            continue
        snippet = "\n".join(lines[start - 1 : end])
        for base, keys, closed, _ in _harvest_object_decls(snippet):
            cur.execute(
                "INSERT INTO prop_shapes "
                "(node_id, base_var, line, shape_kind, keys_json, "
                " keys_confidence, closed, evidence_lines) "
                "VALUES (?, ?, ?, 'object_literal', ?, ?, ?, ?) "
                "ON CONFLICT(node_id, base_var, line) DO UPDATE SET "
                "  keys_json = excluded.keys_json, "
                "  keys_confidence = excluded.keys_confidence, "
                "  closed = excluded.closed",
                (
                    int(node_id), base, int(start),
                    json.dumps(keys),
                    1.0 if closed else 0.6,
                    1 if closed else 0,
                    json.dumps([int(start)]),
                ),
            )
            saved += 1
    return saved


# ---------------------------------------------------------------------------
# Phase B: string-fact ingestion
# ---------------------------------------------------------------------------

# const X = 'foo'   |   const X = "foo"   |   var X = `bar`
_CONST_STR_RE = re.compile(
    r"\b(?:var|let|const)\s+(?P<lhs>[A-Za-z_$][\w$]*)\s*="
    r"\s*(?:'(?P<v1>[^'\\]{0,200})'|\"(?P<v2>[^\"\\]{0,200})\"|"
    r"`(?P<v3>[^`\\]{0,200})`)",
)

_STR_CONCAT_RE = re.compile(
    r"\b(?:var|let|const)\s+(?P<lhs>[A-Za-z_$][\w$]*)\s*=\s*"
    r"(?P<rhs>(?:[A-Za-z_$][\w$]*|'[^']{0,80}'|\"[^\"]{0,80}\")"
    r"(?:\s*\+\s*(?:[A-Za-z_$][\w$]*|'[^']{0,80}'|\"[^\"]{0,80}\")){1,8})",
)


def ingest_string_facts(conn: sqlite3.Connection) -> int:
    """Scan every edges.raw line + capture string assignments. Returns
    row count. Cheap regex pass — the AST extractor can replace this
    with a precise emitter later.
    """
    saved = 0
    cur = conn.cursor()
    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        for m in _CONST_STR_RE.finditer(raw):
            lhs = m.group("lhs")
            v = m.group("v1") or m.group("v2") or m.group("v3") or ""
            cur.execute(
                "INSERT INTO string_facts "
                "(node_id, var_name, level, values_json, line) "
                "VALUES (?, ?, 'const', ?, ?) "
                "ON CONFLICT(node_id, var_name, line) DO UPDATE SET "
                "  level = excluded.level, values_json = excluded.values_json",
                (int(caller_id), lhs, json.dumps([v]), int(line or 0)),
            )
            saved += 1
        for m in _STR_CONCAT_RE.finditer(raw):
            lhs = m.group("lhs")
            rhs = m.group("rhs")
            literals = re.findall(r"['\"]([^'\"]{0,80})['\"]", rhs)
            if literals:
                concat = "".join(literals)
                cur.execute(
                    "INSERT INTO string_facts "
                    "(node_id, var_name, level, values_json, line) "
                    "VALUES (?, ?, 'set', ?, ?) "
                    "ON CONFLICT(node_id, var_name, line) DO UPDATE SET "
                    "  values_json = excluded.values_json",
                    (int(caller_id), lhs, json.dumps([concat]), int(line or 0)),
                )
                saved += 1
    return saved


# ---------------------------------------------------------------------------
# Phase D3: edge refinement
# ---------------------------------------------------------------------------


def _load_shapes_by_node(conn: sqlite3.Connection) -> dict[int, dict[str, PropShape]]:
    out: dict[int, dict[str, PropShape]] = defaultdict(dict)
    for row in conn.execute(
        "SELECT node_id, base_var, line, shape_kind, keys_json, "
        "keys_confidence, closed FROM prop_shapes"
    ):
        nid, base, line, kind, keys_json, conf, closed = row
        keys: list[str] = []
        try:
            keys = json.loads(keys_json) if keys_json else []
        except Exception:
            keys = []
        out[int(nid)][base] = PropShape(
            node_id=int(nid),
            base_var=base,
            line=int(line or 0),
            shape_kind=kind,
            keys=keys,
            keys_confidence=float(conf or 1.0),
            closed=bool(closed),
        )
    return out


def _load_string_facts(
    conn: sqlite3.Connection,
) -> dict[int, dict[str, StringLattice]]:
    out: dict[int, dict[str, StringLattice]] = defaultdict(dict)
    for row in conn.execute(
        "SELECT node_id, var_name, level, values_json FROM string_facts"
    ):
        nid, var, level, vj = row
        if level == "top":
            out[int(nid)][var] = StringLattice.top()
            continue
        try:
            vals = json.loads(vj) if vj else []
        except Exception:
            vals = []
        if len(vals) == 1:
            out[int(nid)][var] = StringLattice.const(vals[0])
        elif vals:
            out[int(nid)][var] = StringLattice.set(set(vals))
        else:
            out[int(nid)][var] = StringLattice.top()
    return out


# Pattern in edges.raw to detect a dynamic call: obj[k](...).
_DYN_CALL_RE = re.compile(
    r"(?P<base>[A-Za-z_$][\w$]*)\s*\[\s*(?P<key>[A-Za-z_$][\w$]*|'[^']+'|\"[^\"]+\")"
    r"\s*\]\s*\("
)


def refine_dynamic_edges(conn: sqlite3.Connection) -> dict:
    """Walk every ``dynamic`` edge and try to refine via prop_shapes +
    string_facts. Mutates ``edges.resolved_kind`` and inserts new rows
    for each concrete refinement. Returns a summary.
    """
    shapes = _load_shapes_by_node(conn)
    string_env = _load_string_facts(conn)
    refined_callsites = 0
    refined_edges = 0
    overflow_callsites = 0
    cur = conn.cursor()
    try:
        rows = conn.execute(
            "SELECT id, caller_id, callee_id, resolved_kind, raw, line FROM edges "
            "WHERE resolved_kind = 'dynamic' AND raw IS NOT NULL"
        ).fetchall()
    except sqlite3.OperationalError:
        return {"refined": 0, "overflowed": 0}
    for edge_id, caller, callee, _, raw, line in rows:
        if refined_edges >= MAX_REFINEMENT_TOTAL:
            break
        if not raw:
            continue
        m = _DYN_CALL_RE.search(raw)
        if not m:
            continue
        base = m.group("base")
        key_tok = m.group("key").strip("'\"")
        shape = shapes.get(int(caller), {}).get(base)
        if shape is None or not shape.keys:
            continue
        # Resolve the key via string lattice if the key token is a
        # variable; literal keys (quoted) resolve immediately.
        if key_tok in shape.keys:
            candidates = [key_tok]
        else:
            lat = string_env.get(int(caller), {}).get(key_tok)
            if lat is None or lat.is_top:
                continue
            candidates = [v for v in lat.iter_values() if v in shape.keys]
        if not candidates:
            continue
        if len(candidates) > MAX_REFINEMENT_PER_CALLSITE:
            cur.execute(
                "UPDATE edges SET resolved_kind = 'dynamic_overapprox' "
                "WHERE id = ?",
                (int(edge_id),),
            )
            overflow_callsites += 1
            continue
        # Materialize refined edges. We mark the original as
        # 'prop_shape' (with shape evidence) AND duplicate one edge per
        # additional candidate so downstream extractors see them as
        # separate paths.
        first = True
        for cand in candidates:
            if first:
                cur.execute(
                    "UPDATE edges SET resolved_kind = 'prop_shape' "
                    "WHERE id = ?",
                    (int(edge_id),),
                )
                first = False
            else:
                # Best-effort dup: copy the row with new resolved_kind.
                cur.execute(
                    "INSERT INTO edges (caller_id, callee_id, resolved_kind, line, raw) "
                    "VALUES (?, ?, 'prop_shape', ?, ?)",
                    (int(caller), int(callee) if callee else None,
                     int(line or 0), raw[:240]),
                )
            refined_edges += 1
        refined_callsites += 1
    conn.commit()
    return {
        "refined_callsites": refined_callsites,
        "refined_edges": refined_edges,
        "overflowed_callsites": overflow_callsites,
        "total_dynamic_seen": len(rows),
    }


def run(conn: sqlite3.Connection, target_dir: str | None = None) -> dict:
    """Convenience: run the full pipeline (ingest + refine) in order."""
    from pathlib import Path
    if target_dir is None:
        sources_root = None
    else:
        sources_root = str(Path(target_dir) / "sources")
    a = ingest_object_keys(conn, sources_root=sources_root)
    b = ingest_string_facts(conn)
    conn.commit()
    refined = refine_dynamic_edges(conn)
    return {"prop_shapes_rows": a, "string_facts_rows": b, **refined}
