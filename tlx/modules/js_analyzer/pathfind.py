"""BFS path-finding on the call graph (Task 5).

find_paths walks call edges from a starting node to nodes carrying a
target tag (sink/source) or to a specific qualified_name. Pure
call-flow reachability — no inter-procedural data flow / taint.

The engine behind trace_to_sink (Task 6).

Resolution / filter rules:
    - Edges with resolved_kind in {"dynamic", "unresolved"} are skipped
      unless include_dynamic / include_unresolved is set.
    - Cycles are detected per-path via the path's own visited set; each
      node may appear at most once per emitted path.
    - BFS yields paths in non-decreasing depth, so the first max_paths
      matches are guaranteed to be the shortest. Final list is sorted
      by (depth, terminal qualified_name) for stable ordering.

Out of scope: inter-procedural data flow (we report call paths, not
whether tainted data actually reaches the sink).
"""

import sqlite3
from collections import deque
from dataclasses import dataclass


@dataclass
class Path:
    nodes: list[int]
    qualified_names: list[str]
    tag: str | None
    depth: int
    sanitisers_in_path: list[dict]
    # Per-hop (resolved_kind, candidate_count). Len == depth (one tuple
    # per traversed edge). Populated when the edges table has the
    # candidate_count column; otherwise emitted as ("exact", 1).
    edge_kinds: list[tuple[str, int]] = None  # type: ignore[assignment]


def _collect_sanitisers(db: sqlite3.Connection, node_ids: list[int]) -> list[dict]:
    if not node_ids:
        return []
    qmarks = ",".join("?" * len(node_ids))
    rows = db.execute(
        f"SELECT ns.node_id, n.qualified_name, ns.taxonomy_id, ns.line, ns.clears "
        f"FROM node_sanitizers ns JOIN nodes n ON n.id = ns.node_id "
        f"WHERE ns.node_id IN ({qmarks})",
        node_ids,
    ).fetchall()
    return [
        {"node_id": r[0], "qname": r[1],
         "taxonomy_id": r[2], "line": r[3], "clears": r[4].split(",")}
        for r in rows
    ]


def find_paths(
    db: sqlite3.Connection,
    from_qname: str,
    to_kind: str = "sink",
    to_qname: str | None = None,
    severity: str | None = None,
    max_depth: int = 8,
    max_paths: int = 10,
    include_dynamic: bool = False,
    include_unresolved: bool = False,
    exclude_sanitised=False,
) -> list[Path]:
    if to_kind not in ("sink", "source", "node"):
        raise ValueError(
            f"to_kind must be 'sink' | 'source' | 'node', got {to_kind!r}"
        )
    if to_kind == "node" and not to_qname:
        raise ValueError("to_kind='node' requires to_qname")

    cur = db.cursor()
    row = cur.execute(
        "SELECT id FROM nodes WHERE qualified_name=?", (from_qname,)
    ).fetchone()
    if not row:
        return []
    start_id = row[0]

    # ── terminal matcher ─────────────────────────────────────────────────
    if to_kind in ("sink", "source"):
        if severity:
            tag_sql = (
                "SELECT taxonomy_id FROM node_tags "
                "WHERE node_id=? AND kind=? AND severity=? LIMIT 1"
            )

            def tag_params(nid):
                return (nid, to_kind, severity)
        else:
            tag_sql = (
                "SELECT taxonomy_id FROM node_tags "
                "WHERE node_id=? AND kind=? LIMIT 1"
            )

            def tag_params(nid):
                return (nid, to_kind)

        def match_terminal(nid):
            r = cur.execute(tag_sql, tag_params(nid)).fetchone()
            return (True, r[0]) if r else (False, None)
    else:
        target_row = cur.execute(
            "SELECT id FROM nodes WHERE qualified_name=?", (to_qname,)
        ).fetchone()
        if not target_row:
            return []
        target_id = target_row[0]

        def match_terminal(nid):
            return (nid == target_id, None)

    # ── edge filter clause (built once) ──────────────────────────────────
    # Note: 'this_cross_file' is intentionally NOT in skip_kinds —
    # it is treated as traversable, same as 'name_match'.
    edge_cols = {r[1] for r in cur.execute("PRAGMA table_info(edges)")}
    has_cand = "candidate_count" in edge_cols
    select_extra = ", resolved_kind"
    if has_cand:
        select_extra += ", candidate_count"
    skip_kinds = []
    if not include_dynamic:
        skip_kinds.append("dynamic")
    if not include_unresolved:
        skip_kinds.append("unresolved")
    if skip_kinds:
        placeholders = ",".join("?" * len(skip_kinds))
        edge_sql = (
            f"SELECT callee_id{select_extra} FROM edges "
            f"WHERE caller_id=? AND callee_id IS NOT NULL "
            f"AND resolved_kind NOT IN ({placeholders})"
        )
        edge_extra = tuple(skip_kinds)
    else:
        edge_sql = (
            f"SELECT callee_id{select_extra} FROM edges "
            f"WHERE caller_id=? AND callee_id IS NOT NULL"
        )
        edge_extra = ()

    # ── qname lookup cache ───────────────────────────────────────────────
    qname_cache: dict[int, str] = {start_id: from_qname}

    def qname_of(nid):
        q = qname_cache.get(nid)
        if q is None:
            r = cur.execute(
                "SELECT qualified_name FROM nodes WHERE id=?", (nid,)
            ).fetchone()
            q = r[0] if r else f"<unknown:{nid}>"
            qname_cache[nid] = q
        return q

    # ── BFS ──────────────────────────────────────────────────────────────
    # Filter cap: name_match edges with high candidate_count are
    # 1/N-ambiguous bare-name resolutions. Mirroring the bestfirst
    # extractor's --max-name-match default, drop edges with cand>10.
    MAX_NAME_MATCH_CAND = 10

    found: list[Path] = []
    queue: deque[tuple[list[int], list[tuple[str, int]]]] = deque()
    queue.append(([start_id], []))

    while queue and len(found) < max_paths:
        path_ids, path_edges = queue.popleft()
        cur_id = path_ids[-1]
        depth = len(path_ids) - 1

        ok, tag = match_terminal(cur_id)
        if ok:
            sanitisers = _collect_sanitisers(db, path_ids)
            if exclude_sanitised and sanitisers:
                continue
            found.append(Path(
                nodes=list(path_ids),
                qualified_names=[qname_of(n) for n in path_ids],
                tag=tag,
                depth=depth,
                sanitisers_in_path=sanitisers,
                edge_kinds=list(path_edges),
            ))
            continue  # don't traverse past a terminal match

        if depth >= max_depth:
            continue

        for row in cur.execute(edge_sql, (cur_id,) + edge_extra).fetchall():
            callee_id = row[0]
            rk = row[1] if len(row) > 1 else "exact"
            cand = row[2] if (has_cand and len(row) > 2) else 1
            if callee_id in path_ids:
                continue  # cycle within this path
            if rk == "name_match" and (cand or 1) > MAX_NAME_MATCH_CAND:
                continue  # ambiguous bare-name match — drop to cut FP volume
            queue.append((
                path_ids + [callee_id],
                path_edges + [(rk or "exact", int(cand or 1))],
            ))

    found.sort(key=lambda p: (p.depth, p.qualified_names[-1]))
    return found