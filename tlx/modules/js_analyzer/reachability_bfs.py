"""Route → sink reachability BFS validation.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §22.4b + §22.5.

Companion to v2/sink_reachability.py. The base module builds
``sink_lifecycle`` (per-sink lifecycle phase) and ``route_map`` (per-
route entry modules) but doesn't connect them. This module walks the
callgraph forward from every route_map entry to enumerate which sinks
each route can reach, then writes ``route_sink_reach``.

Three downstream uses:

  1. **Dead-code pruning** — sinks that no route reaches are
     dead-code-flagged (``attacker_can_trigger`` cleared, activation
     × 0.1).
  2. **Route fanout bonus** — sinks reachable from many routes get a
     small bonus (caps at 1.2× to avoid runaway).
  3. **Hot-path enumeration** — surfaces "which routes does this sink
     live on" inside the audit prompt so the LLM can frame attacker
     entry.

Driver: bin/reachability_bfs.py
"""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path


__all__ = ["run", "ensure_schema", "compute_reachability"]


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS route_sink_reach (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id        INTEGER NOT NULL,    -- route_map.id
    sink_node_id    INTEGER NOT NULL,    -- nodes.id of the sink
    distance        INTEGER NOT NULL,    -- hop count from entry node to sink
    UNIQUE (route_id, sink_node_id)
);
CREATE INDEX IF NOT EXISTS idx_route_sink_reach_sink
  ON route_sink_reach(sink_node_id);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_CREATE_SCHEMA)


@dataclass
class ReachReport:
    routes_seen: int = 0
    sinks_reachable: int = 0
    sinks_dead: int = 0
    sinks_total: int = 0
    avg_routes_per_sink: float = 0.0
    elapsed_s: float = 0.0


def _entry_nodes_for_route(
    conn: sqlite3.Connection, entry_module: str
) -> list[int]:
    """A route's entry_module typically points at a file. Take every
    function defined in that file as a possible entry node.
    """
    if not entry_module:
        return []
    try:
        rows = conn.execute(
            "SELECT id FROM nodes WHERE file = ?",
            (entry_module,),
        ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [int(r[0]) for r in rows]


def _forward_adj(conn: sqlite3.Connection) -> dict[int, list[int]]:
    out: dict[int, list[int]] = defaultdict(list)
    try:
        rows = conn.execute(
            "SELECT caller_id, callee_id FROM edges WHERE callee_id IS NOT NULL"
        ).fetchall()
    except sqlite3.OperationalError:
        return out
    for caller, callee in rows:
        out[int(caller)].append(int(callee))
    return out


def _bfs(
    starts: list[int],
    adj: dict[int, list[int]],
    sink_set: set[int],
    *,
    max_depth: int,
) -> dict[int, int]:
    """Return {sink_node_id: min_distance}."""
    found: dict[int, int] = {}
    seen: dict[int, int] = {s: 0 for s in starts}
    queue: deque[int] = deque(starts)
    while queue:
        n = queue.popleft()
        d = seen[n]
        if n in sink_set and (n not in found or d < found[n]):
            found[n] = d
        if d >= max_depth:
            continue
        for c in adj.get(n, ()):
            if c in seen:
                continue
            seen[c] = d + 1
            queue.append(c)
    return found


def compute_reachability(
    conn: sqlite3.Connection, *, max_depth: int = 12
) -> ReachReport:
    """Populate route_sink_reach. Returns ReachReport summary.

    Marks sinks unreachable from any route as dead in sink_lifecycle by
    setting activation_likelihood *= 0.1 and attacker_can_trigger = 0.
    """
    import time
    t0 = time.monotonic()
    rep = ReachReport()
    ensure_schema(conn)
    conn.execute("DELETE FROM route_sink_reach")

    # Sink set.
    try:
        sink_ids = {
            int(r[0])
            for r in conn.execute(
                "SELECT DISTINCT node_id FROM node_tags WHERE kind = 'sink'"
            )
        }
    except sqlite3.OperationalError:
        sink_ids = set()
    rep.sinks_total = len(sink_ids)
    if not sink_ids:
        rep.elapsed_s = round(time.monotonic() - t0, 3)
        return rep

    # Routes.
    try:
        routes = conn.execute(
            "SELECT id, route_path, entry_module FROM route_map"
        ).fetchall()
    except sqlite3.OperationalError:
        routes = []
    rep.routes_seen = len(routes)

    adj = _forward_adj(conn)
    reachable_sinks: set[int] = set()
    cur = conn.cursor()
    routes_per_sink: dict[int, int] = defaultdict(int)
    for route_id, route_path, entry_module in routes:
        starts = _entry_nodes_for_route(conn, entry_module)
        if not starts:
            continue
        found = _bfs(starts, adj, sink_ids, max_depth=max_depth)
        for sink_node_id, distance in found.items():
            cur.execute(
                "INSERT OR IGNORE INTO route_sink_reach "
                "(route_id, sink_node_id, distance) VALUES (?, ?, ?)",
                (int(route_id), int(sink_node_id), int(distance)),
            )
            reachable_sinks.add(int(sink_node_id))
            routes_per_sink[int(sink_node_id)] += 1

    rep.sinks_reachable = len(reachable_sinks)
    rep.sinks_dead = max(0, len(sink_ids) - len(reachable_sinks))
    rep.avg_routes_per_sink = (
        round(sum(routes_per_sink.values()) / len(routes_per_sink), 3)
        if routes_per_sink
        else 0.0
    )

    # Dead-code pruning: downgrade sinks the BFS could not reach. We
    # *only* downgrade if sink_lifecycle has a row already — otherwise
    # we'd shadow the v2 sink_reachability module's classification.
    if rep.sinks_dead:
        dead = list(sink_ids - reachable_sinks)
        for i in range(0, len(dead), 500):
            block = dead[i : i + 500]
            ph = ",".join("?" * len(block))
            cur.execute(
                f"UPDATE sink_lifecycle SET "
                f"  attacker_can_trigger = 0, "
                f"  activation_likelihood = activation_likelihood * 0.1, "
                f"  rationale = COALESCE(rationale, '') || "
                f"              ' [BFS: no route reaches this sink]' "
                f"WHERE node_id IN ({ph})",
                tuple(block),
            )

    # Route-fanout bonus: cap at 1.2x. Only applied when fanout >= 4.
    high_fanout = [nid for nid, n in routes_per_sink.items() if n >= 4]
    for nid in high_fanout:
        n = routes_per_sink[nid]
        bonus = min(1.2, 1.0 + (n - 3) * 0.03)
        cur.execute(
            "UPDATE sink_lifecycle SET "
            "  activation_likelihood = MIN(1.0, activation_likelihood * ?), "
            "  rationale = COALESCE(rationale, '') || "
            "             ' [BFS: " + f"{n}" + " routes reach this sink]' "
            "WHERE node_id = ?",
            (bonus, int(nid)),
        )

    conn.commit()
    rep.elapsed_s = round(time.monotonic() - t0, 3)
    return rep


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    rep = compute_reachability(conn)
    out_dir = Path(target_dir) / "v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "reachability_bfs.json").write_text(
        json.dumps(
            {
                "routes_seen": rep.routes_seen,
                "sinks_total": rep.sinks_total,
                "sinks_reachable": rep.sinks_reachable,
                "sinks_dead": rep.sinks_dead,
                "avg_routes_per_sink": rep.avg_routes_per_sink,
                "elapsed_s": rep.elapsed_s,
            },
            indent=2,
        )
    )
    return {
        "routes_seen": rep.routes_seen,
        "sinks_reachable": rep.sinks_reachable,
        "sinks_dead": rep.sinks_dead,
        "sinks_total": rep.sinks_total,
        "avg_routes_per_sink": rep.avg_routes_per_sink,
        "elapsed_s": rep.elapsed_s,
    }
