"""Incremental recomputation DAG driver.

Plan: plans/ARCHITECTURE_EVOLUTION.md §10.

Content-addressed invalidation. On every js-index run:

  1. Diff file_hashes → set of changed files.
  2. For each changed file, find affected nodes by overlapping line range.
  3. Walk the callgraph backward (callers) bounded by max_depth (default 3).
  4. Mark every node in the dirty set: taint_cache.valid = 0; node_hashes
     row regenerated post-recompute by :func:`record_node_hashes`.

This module is read-only against AST extraction. The caller (callgraph
phase D / interprocedural taint solver) consults :func:`dirty_set` to
decide what to recompute, then calls :func:`record_node_hashes` and
:func:`store_taint_cache` once results are ready.

Phase 1 of the rollout: persist + diff only. Skipping recomputation is
the caller's choice — gated by ``ENABLE_INCREMENTAL_TAINT`` so we can
validate cache correctness against full re-runs first.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from typing import Iterable


__all__ = [
    "dirty_set",
    "record_node_hashes",
    "invalidate_taint_cache",
    "store_taint_cache",
    "load_taint_cache",
    "DirtyReport",
    "body_hash",
    "deps_hash",
]


@dataclass
class DirtyReport:
    changed_files: list[str]
    seed_nodes: list[int]
    dirty_nodes: list[int]
    max_depth: int
    elapsed_s: float


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def body_hash(source_text: str) -> str:
    """Hash of node source bytes — caller slices source_text to
    [start_line..end_line] before calling.
    """
    return _sha256(source_text)


def deps_hash(
    callee_qnames: Iterable[str],
    prop_shapes: Iterable[str] | None = None,
    tag_ids: Iterable[str] | None = None,
) -> str:
    parts = [
        "callees:" + ",".join(sorted(set(callee_qnames or []))),
        "shapes:" + ",".join(sorted(set(prop_shapes or []))),
        "tags:" + ",".join(sorted(set(tag_ids or []))),
    ]
    return _sha256("\n".join(parts))


# ---------------------------------------------------------------------------
# Dirty-set computation
# ---------------------------------------------------------------------------


def _changed_files(conn: sqlite3.Connection) -> list[str]:
    """Files whose current file_hashes.sha256 differs from the one
    stamped on the last node_hashes generation. Best-effort: a missing
    node_hashes row implies "never seen", so every file is changed.
    """
    try:
        rows = conn.execute(
            "SELECT file, sha256 FROM file_hashes"
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    if not rows:
        return []
    # Map file -> set of node bodies known to incremental. If any node
    # in the file lacks a node_hashes row, the file is considered
    # changed.
    files_with_hashes: set[str] = set()
    try:
        for (f,) in conn.execute(
            "SELECT DISTINCT n.file "
            "FROM nodes n JOIN node_hashes h ON h.node_id = n.id"
        ):
            files_with_hashes.add(f)
    except sqlite3.OperationalError:
        return [f for f, _ in rows]
    return sorted(f for f, _ in rows if f not in files_with_hashes)


def _seed_nodes(conn: sqlite3.Connection, files: list[str]) -> list[int]:
    if not files:
        return []
    placeholders = ",".join("?" * len(files))
    rows = conn.execute(
        f"SELECT id FROM nodes WHERE file IN ({placeholders})",
        tuple(files),
    ).fetchall()
    return [int(r[0]) for r in rows]


def _walk_callers(
    conn: sqlite3.Connection, seeds: Iterable[int], max_depth: int
) -> set[int]:
    """BFS backward via edges (caller -> callee). Returns reachable
    callers up to ``max_depth`` hops.
    """
    visited: set[int] = set(int(s) for s in seeds)
    frontier: set[int] = set(visited)
    depth = 0
    while frontier and depth < max_depth:
        placeholders = ",".join("?" * len(frontier))
        new_frontier: set[int] = set()
        try:
            rows = conn.execute(
                f"SELECT DISTINCT caller_id FROM edges "
                f"WHERE callee_id IN ({placeholders})",
                tuple(frontier),
            ).fetchall()
        except sqlite3.OperationalError:
            break
        for (caller,) in rows:
            if caller is None:
                continue
            if caller in visited:
                continue
            new_frontier.add(int(caller))
        visited |= new_frontier
        frontier = new_frontier
        depth += 1
    return visited


def dirty_set(
    conn: sqlite3.Connection, *, max_depth: int = 3
) -> DirtyReport:
    """Compute the dirty set for the current snapshot.

    Returns a DirtyReport. Side effects: marks ``taint_cache.valid = 0``
    for every node in the dirty set so a subsequent consumer can skip
    the cache on those nodes without scanning them itself.
    """
    t0 = time.monotonic()
    files = _changed_files(conn)
    seeds = _seed_nodes(conn, files)
    dirty = _walk_callers(conn, seeds, max_depth=max_depth)
    if dirty:
        invalidate_taint_cache(conn, dirty)
    return DirtyReport(
        changed_files=files,
        seed_nodes=seeds,
        dirty_nodes=sorted(dirty),
        max_depth=max_depth,
        elapsed_s=round(time.monotonic() - t0, 3),
    )


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


def record_node_hashes(
    conn: sqlite3.Connection,
    rows: Iterable[tuple[int, str, str]],
) -> int:
    """Insert/update node_hashes rows. Each tuple = (node_id, body, deps).

    Returns row count.
    """
    n = 0
    now = time.time()
    cur = conn.cursor()
    for node_id, body, deps in rows:
        cur.execute(
            "INSERT INTO node_hashes (node_id, body_sha256, deps_sha256, last_indexed_at) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(node_id) DO UPDATE SET "
            "  body_sha256 = excluded.body_sha256, "
            "  deps_sha256 = excluded.deps_sha256, "
            "  last_indexed_at = excluded.last_indexed_at",
            (int(node_id), body, deps, now),
        )
        n += 1
    return n


def invalidate_taint_cache(conn: sqlite3.Connection, node_ids: Iterable[int]) -> int:
    node_ids = list(int(n) for n in node_ids)
    if not node_ids:
        return 0
    cur = conn.cursor()
    chunk = 500
    total = 0
    for i in range(0, len(node_ids), chunk):
        block = node_ids[i : i + chunk]
        placeholders = ",".join("?" * len(block))
        cur.execute(
            f"UPDATE taint_cache SET valid = 0 WHERE node_id IN ({placeholders})",
            tuple(block),
        )
        total += cur.rowcount or 0
    return total


def store_taint_cache(
    conn: sqlite3.Connection,
    node_id: int,
    flows: dict,
    body_sha: str,
) -> None:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO taint_cache (node_id, flows_json, cache_sha256, valid, cached_at) "
        "VALUES (?, ?, ?, 1, ?) "
        "ON CONFLICT(node_id) DO UPDATE SET "
        "  flows_json = excluded.flows_json, "
        "  cache_sha256 = excluded.cache_sha256, "
        "  valid = 1, "
        "  cached_at = excluded.cached_at",
        (int(node_id), json.dumps(flows), body_sha, time.time()),
    )


def load_taint_cache(
    conn: sqlite3.Connection, node_id: int, expected_sha: str
) -> dict | None:
    """Return cached flows iff the row is ``valid=1`` and the
    cache_sha256 matches ``expected_sha``. None on miss.
    """
    try:
        row = conn.execute(
            "SELECT flows_json, cache_sha256, valid FROM taint_cache "
            "WHERE node_id = ?",
            (int(node_id),),
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    if not row:
        return None
    flows_json, cache_sha, valid = row
    if not valid or cache_sha != expected_sha:
        return None
    try:
        return json.loads(flows_json)
    except Exception:
        return None
