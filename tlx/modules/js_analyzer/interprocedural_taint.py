"""Inter-procedural taint solver.

Two entry points:

  build_arg_to_param_edges(conn) -> int
    One-time post-pass: for every exact/this_cross_file/name_match edge,
    match caller __arg{N}__ variables to callee __param{N}__ variables
    and insert 'arg_to_param' dataflow_edges. Idempotent (guarded by
    existence check). Returns count of newly inserted edges.

  solve_interprocedural_taint(conn) -> list[dict]
    Worklist solver over (var_id, taint_label) pairs. Seeds from
    node_tags source entries, propagates along dataflow_edges (including
    arg_to_param), fires when a tainted var_id reaches a node with a
    sink tag. Persists results into interprocedural_taint_flows table.
    Idempotent (clears table before re-inserting). Returns list of flows.
"""

import json
import os
import sqlite3
import time

# ── Part A ───────────────────────────────────────────────────────────────────

def build_arg_to_param_edges(conn: sqlite3.Connection) -> int:
    """Emit arg_to_param dataflow edges for resolved call edges.

    Guards against double-insertion: returns 0 immediately if any
    arg_to_param edges already exist in the DB.
    """
    existing = conn.execute(
        "SELECT COUNT(*) FROM dataflow_edges WHERE edge_kind='arg_to_param'"
    ).fetchone()[0]
    if existing:
        return 0

    RESOLVED = ("exact", "this_cross_file", "name_match")
    placeholders = ",".join("?" * len(RESOLVED))
    call_edges = conn.execute(
        f"SELECT caller_id, callee_id FROM edges "
        f"WHERE callee_id IS NOT NULL "
        f"AND resolved_kind IN ({placeholders})",
        RESOLVED,
    ).fetchall()

    inserted = 0
    for caller_id, callee_id in call_edges:
        arg_vars = conn.execute(
            "SELECT id, name FROM variables "
            "WHERE node_id=? AND name LIKE '__arg%__'",
            (caller_id,),
        ).fetchall()
        param_vars = conn.execute(
            "SELECT id, name FROM variables "
            "WHERE node_id=? AND name LIKE '__param%__'",
            (callee_id,),
        ).fetchall()

        param_index: dict[int, int] = {}
        for var_id, name in param_vars:
            try:
                n = int(name.replace("__param", "").replace("__", ""))
                param_index[n] = var_id
            except ValueError:
                continue

        for arg_var_id, arg_name in arg_vars:
            try:
                n = int(arg_name.replace("__arg", "").replace("__", ""))
            except ValueError:
                continue
            param_var_id = param_index.get(n)
            if param_var_id is None:
                continue
            conn.execute(
                "INSERT OR IGNORE INTO dataflow_edges "
                "(from_var, to_var, edge_kind, line, sanitiser) "
                "VALUES (?, ?, 'arg_to_param', 0, NULL)",
                (arg_var_id, param_var_id),
            )
            inserted += 1

    conn.commit()
    return inserted


# ── Part B ───────────────────────────────────────────────────────────────────

_CREATE_FLOWS_TABLE = """
CREATE TABLE IF NOT EXISTS interprocedural_taint_flows (
    id              INTEGER PRIMARY KEY,
    source_node_id  INT  NOT NULL,
    sink_node_id    INT  NOT NULL,
    source_rule     TEXT NOT NULL,
    sink_rule       TEXT NOT NULL,
    via_var_ids     TEXT NOT NULL,
    sanitised_by    TEXT
);
CREATE INDEX IF NOT EXISTS idx_itp_source ON interprocedural_taint_flows(source_node_id);
CREATE INDEX IF NOT EXISTS idx_itp_sink   ON interprocedural_taint_flows(sink_node_id);
"""

MAX_ITERATIONS = 50_000

# Wall-clock budget caps total solver time. Iteration cap alone could
# spend 5+ minutes on dense graphs because each iter does several
# SQLite reads; this floor stops the index pipeline from hanging.
# Override via TLX_ITP_WALL_BUDGET_SECONDS (float seconds, 0 = disabled).
DEFAULT_WALL_BUDGET_SECONDS = 120.0


def _wall_budget_seconds() -> float:
    raw = os.environ.get("TLX_ITP_WALL_BUDGET_SECONDS")
    if raw is None:
        return DEFAULT_WALL_BUDGET_SECONDS
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        return DEFAULT_WALL_BUDGET_SECONDS


class InterproceduralTaintBudgetExceeded(RuntimeError):
    """Raised when solver hits wall-clock or iteration budget.

    Carries partial flow count so callers can decide whether to commit
    progress or roll back.
    """
    def __init__(self, message: str, *, flows_emitted: int, elapsed_s: float,
                 iterations: int, reason: str):
        super().__init__(message)
        self.flows_emitted = flows_emitted
        self.elapsed_s = elapsed_s
        self.iterations = iterations
        self.reason = reason  # 'iterations' | 'wall_clock'


def solve_interprocedural_taint(conn: sqlite3.Connection) -> list[dict]:
    """Worklist solver: propagates taint across function boundaries.

    Returns list of flow dicts:
      {source_node_id, sink_node_id, source_rule, sink_rule,
       via_var_ids: [int], sanitised_by: str|None}

    Idempotent: clears interprocedural_taint_flows before re-inserting.
    Raises InterproceduralTaintBudgetExceeded if worklist exceeds
    MAX_ITERATIONS or wall-clock budget. Already-persisted partial flows
    remain committed for inspection.
    """
    conn.executescript(_CREATE_FLOWS_TABLE)
    conn.execute("DELETE FROM interprocedural_taint_flows")
    conn.commit()
    started = time.monotonic()
    wall_budget = _wall_budget_seconds()

    worklist: list[tuple[int, str]] = []
    taint_state: dict[int, dict[str, dict]] = {}
    visited: set[tuple[int, str]] = set()

    source_rows = conn.execute(
        "SELECT v.id, v.node_id, t.taxonomy_id "
        "FROM variables v "
        "JOIN node_tags t ON t.node_id = v.node_id AND t.kind = 'source'"
    ).fetchall()

    for var_id, node_id, taxonomy_id in source_rows:
        label = taxonomy_id
        if var_id not in taint_state:
            taint_state[var_id] = {}
        taint_state[var_id][label] = {
            "source_node_id": node_id,
            "sanitised_by": None,
            "via": [var_id],
        }
        key = (var_id, label)
        if key not in visited:
            worklist.append(key)
            visited.add(key)

    sink_map: dict[int, list[str]] = {}
    for node_id, taxonomy_id in conn.execute(
        "SELECT node_id, taxonomy_id FROM node_tags WHERE kind='sink'"
    ).fetchall():
        sink_map.setdefault(node_id, []).append(taxonomy_id)

    var_to_node: dict[int, int] = {}
    for var_id, node_id in conn.execute("SELECT id, node_id FROM variables").fetchall():
        var_to_node[var_id] = node_id

    emitted: set[tuple[str, str, int]] = set()
    flows: list[dict] = []

    iterations = 0
    while worklist:
        iterations += 1
        if iterations > MAX_ITERATIONS:
            conn.commit()
            elapsed = time.monotonic() - started
            raise InterproceduralTaintBudgetExceeded(
                f"Interprocedural taint solver exceeded {MAX_ITERATIONS} "
                f"iterations ({len(flows)} flows emitted in {elapsed:.1f}s).",
                flows_emitted=len(flows),
                elapsed_s=elapsed,
                iterations=iterations,
                reason="iterations",
            )
        # Wall-clock check only every 256 iters — time.monotonic is cheap
        # but unbounded calls still show up at high iteration counts.
        if wall_budget and (iterations & 0xFF) == 0:
            elapsed = time.monotonic() - started
            if elapsed > wall_budget:
                conn.commit()
                raise InterproceduralTaintBudgetExceeded(
                    f"Interprocedural taint solver exceeded "
                    f"{wall_budget:.0f}s wall-clock budget "
                    f"({len(flows)} flows emitted, {iterations} iters).",
                    flows_emitted=len(flows),
                    elapsed_s=elapsed,
                    iterations=iterations,
                    reason="wall_clock",
                )

        var_id, label = worklist.pop(0)
        state = taint_state.get(var_id, {}).get(label)
        if state is None:
            continue

        node_id = var_to_node.get(var_id)
        if node_id and node_id in sink_map:
            for sink_rule in sink_map[node_id]:
                dedup_key = (label, sink_rule, node_id)
                if dedup_key not in emitted:
                    emitted.add(dedup_key)
                    flow = {
                        "source_node_id": state["source_node_id"],
                        "sink_node_id":   node_id,
                        "source_rule":    label,
                        "sink_rule":      sink_rule,
                        "via_var_ids":    state["via"],
                        "sanitised_by":   state["sanitised_by"],
                    }
                    flows.append(flow)
                    conn.execute(
                        "INSERT INTO interprocedural_taint_flows "
                        "(source_node_id, sink_node_id, source_rule, sink_rule, "
                        " via_var_ids, sanitised_by) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (
                            flow["source_node_id"],
                            flow["sink_node_id"],
                            flow["source_rule"],
                            flow["sink_rule"],
                            json.dumps(flow["via_var_ids"]),
                            flow["sanitised_by"],
                        ),
                    )

        out_edges = conn.execute(
            "SELECT to_var, sanitiser FROM dataflow_edges WHERE from_var=?",
            (var_id,),
        ).fetchall()

        for to_var, sanitiser in out_edges:
            new_san = state["sanitised_by"] or sanitiser
            new_via = state["via"] + [to_var]

            if to_var not in taint_state:
                taint_state[to_var] = {}
            existing = taint_state[to_var].get(label)
            if existing is None:
                taint_state[to_var][label] = {
                    "source_node_id": state["source_node_id"],
                    "sanitised_by":   new_san,
                    "via":            new_via,
                }
                key = (to_var, label)
                if key not in visited:
                    visited.add(key)
                    worklist.append(key)

    conn.commit()
    return flows
