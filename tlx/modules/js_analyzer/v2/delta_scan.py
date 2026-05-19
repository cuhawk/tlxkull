"""V2 §18 — Differential scan / delta analysis mode.

Given two snapshots (prior_run / current_run) of a per-target DB,
compute the set of changed nodes / tags / edges and report which
chains *transitively* changed.

Off by default; opt-in via the CLI driver. No automatic invocation
from the master pipeline.
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

__all__ = [
    "Delta",
    "compute_delta",
    "reachable_chains_from_delta",
    "expand_delta_via_callgraph",
    "classify_delta_chains",
]


@dataclass
class Delta:
    schema_version: str = "v2.delta.1"
    files_added: list[str] = field(default_factory=list)
    files_removed: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    nodes_added: list[str] = field(default_factory=list)
    nodes_removed: list[str] = field(default_factory=list)
    tags_added: list[dict] = field(default_factory=list)
    tags_removed: list[dict] = field(default_factory=list)
    edges_added: int = 0
    edges_removed: int = 0
    elapsed_s: float = 0.0


def _open_ro(path: str | Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{Path(path)}?mode=ro", uri=True)


def _file_hashes(conn: sqlite3.Connection) -> dict[str, str]:
    try:
        return {f: h for f, h in conn.execute("SELECT file, sha256 FROM file_hashes")}
    except sqlite3.OperationalError:
        return {}


def _qnames(conn: sqlite3.Connection) -> set[str]:
    return {q for (q,) in conn.execute("SELECT qualified_name FROM nodes")}


def _tag_keys(conn: sqlite3.Connection) -> set[tuple[str, str, str]]:
    try:
        return {(q, t, k) for q, t, k in conn.execute(
            "SELECT n.qualified_name, nt.taxonomy_id, nt.kind "
            "FROM node_tags nt JOIN nodes n ON n.id = nt.node_id"
        )}
    except sqlite3.OperationalError:
        return set()


def _edge_keys(conn: sqlite3.Connection) -> set[tuple[str, str, int]]:
    return {(a, b, c) for a, b, c in conn.execute(
        "SELECT caller.qualified_name, callee.qualified_name, e.line "
        "FROM edges e "
        "JOIN nodes caller ON caller.id = e.caller_id "
        "JOIN nodes callee ON callee.id = e.callee_id "
        "WHERE e.callee_id IS NOT NULL"
    )}


def compute_delta(prior_db: str | Path, current_db: str | Path) -> Delta:
    import time
    t0 = time.monotonic()
    delta = Delta()
    a = _open_ro(prior_db)
    b = _open_ro(current_db)
    try:
        h_a, h_b = _file_hashes(a), _file_hashes(b)
        delta.files_added = sorted(set(h_b) - set(h_a))
        delta.files_removed = sorted(set(h_a) - set(h_b))
        delta.files_modified = sorted(
            f for f in (set(h_a) & set(h_b)) if h_a[f] != h_b[f]
        )

        q_a, q_b = _qnames(a), _qnames(b)
        delta.nodes_added = sorted(q_b - q_a)[:1000]
        delta.nodes_removed = sorted(q_a - q_b)[:1000]

        t_a, t_b = _tag_keys(a), _tag_keys(b)
        delta.tags_added = [
            {"qname": q, "taxonomy_id": tid, "kind": k}
            for q, tid, k in sorted(t_b - t_a)[:1000]
        ]
        delta.tags_removed = [
            {"qname": q, "taxonomy_id": tid, "kind": k}
            for q, tid, k in sorted(t_a - t_b)[:1000]
        ]

        e_a, e_b = _edge_keys(a), _edge_keys(b)
        delta.edges_added = len(e_b - e_a)
        delta.edges_removed = len(e_a - e_b)
    finally:
        a.close()
        b.close()
    delta.elapsed_s = round(time.monotonic() - t0, 3)
    return delta


def reachable_chains_from_delta(
    chains_jsonl: str | Path, delta: Delta, *, radius: int = 3,
    current_db: str | Path | None = None,
) -> list[dict]:
    """Filter ``chains_jsonl`` to only those chains whose path intersects
    the delta — direct hit OR within ``radius`` hops via callgraph.

    When ``current_db`` is provided the function walks the callgraph
    forward AND backward from every delta node to build a fuller dirty
    neighborhood; without it the comparison degrades to a string match
    on qname + path_files (the original V1 semantics).
    """
    changed_qnames = set(delta.nodes_added) | set(delta.nodes_removed)
    changed_files = (
        set(delta.files_added) | set(delta.files_removed)
        | set(delta.files_modified)
    )
    expanded_qnames = changed_qnames
    if current_db is not None and radius > 0:
        try:
            expanded_qnames = expand_delta_via_callgraph(
                current_db, changed_qnames, radius=radius
            )
        except sqlite3.OperationalError:
            expanded_qnames = changed_qnames

    out: list[dict] = []
    for line in Path(chains_jsonl).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            chain = json.loads(line)
        except json.JSONDecodeError:
            continue
        path = chain.get("path") or []
        path_files = chain.get("path_files") or []
        if any(q in expanded_qnames for q in path):
            out.append(chain)
            continue
        if any(f in changed_files for f in path_files):
            out.append(chain)
    return out


def expand_delta_via_callgraph(
    db: str | Path, seed_qnames: set[str], *, radius: int
) -> set[str]:
    """BFS bidirectional from ``seed_qnames`` for ``radius`` hops.

    Returns the union of seeds + every node within ``radius`` callgraph
    hops (forward OR backward).
    """
    if not seed_qnames:
        return set()
    conn = _open_ro(db)
    try:
        # Map qname → id.
        seeds_ids: set[int] = set()
        for q in seed_qnames:
            r = conn.execute(
                "SELECT id FROM nodes WHERE qualified_name = ?", (q,)
            ).fetchone()
            if r:
                seeds_ids.add(int(r[0]))
        if not seeds_ids:
            return set(seed_qnames)
        visited = set(seeds_ids)
        frontier = set(seeds_ids)
        for _ in range(radius):
            if not frontier:
                break
            placeholders = ",".join("?" * len(frontier))
            # Forward + backward.
            rows = conn.execute(
                f"SELECT caller_id, callee_id FROM edges "
                f"WHERE caller_id IN ({placeholders}) OR callee_id IN ({placeholders})",
                tuple(frontier) + tuple(frontier),
            ).fetchall()
            new_frontier: set[int] = set()
            for caller, callee in rows:
                for nid in (caller, callee):
                    if nid is None:
                        continue
                    if nid in visited:
                        continue
                    new_frontier.add(int(nid))
            visited |= new_frontier
            frontier = new_frontier
        # Map back to qnames.
        if not visited:
            return set(seed_qnames)
        block = list(visited)
        out: set[str] = set(seed_qnames)
        for i in range(0, len(block), 500):
            chunk = block[i : i + 500]
            ph = ",".join("?" * len(chunk))
            for (q,) in conn.execute(
                f"SELECT qualified_name FROM nodes WHERE id IN ({ph})",
                tuple(chunk),
            ):
                if q:
                    out.add(q)
        return out
    finally:
        conn.close()


def classify_delta_chains(
    chains: list[dict], delta: Delta
) -> dict[str, list[dict]]:
    """Categorize delta-reachable chains:

      * delta_high  — path touches a node added in this delta
      * delta_low   — path touches only modified files (no new nodes)
      * delta_clean — direct seed equality (no expansion needed)
    """
    out: dict[str, list[dict]] = {
        "delta_high": [], "delta_low": [], "delta_clean": [],
    }
    direct_qnames = set(delta.nodes_added) | set(delta.nodes_removed)
    modified_files = set(delta.files_modified)
    for c in chains:
        path = set(c.get("path") or [])
        path_files = set(c.get("path_files") or [])
        if path & set(delta.nodes_added):
            out["delta_high"].append(c)
        elif path & direct_qnames:
            out["delta_clean"].append(c)
        elif path_files & modified_files:
            out["delta_low"].append(c)
        else:
            out["delta_clean"].append(c)
    return out
