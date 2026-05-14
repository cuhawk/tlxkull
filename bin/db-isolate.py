#!/usr/bin/env python3
"""Per-target DB isolation for the TLX js_analyzer and rag stores.

The js_analyzer SQLite at ~/.tlx/js_analyzer.db has no target column, so
data from earlier engagements co-mingles with the current target and pollutes
js_get_chains / js_run_audit. The chroma vector store at ~/.tlx/chroma/ is
per-collection but its segment files all live in one directory.

This helper enforces a per-target layout. Output goes under:
    targets/<name>/db/
        js_analyzer.db          # filtered to this target only
        chroma/                  # chroma collection segment files (copied)
        chroma.sqlite3           # chroma metadata (filtered to this collection)

Subcommands:
    snapshot   targets/<name>     host-prefix-1 [host-prefix-2 ...]
        Copy the global js_analyzer.db into the target dir, then drop rows
        whose `file` column does NOT match one of the given host prefixes
        (e.g. "eu1.dev.ict.dematic.dev/"). Also copy the chroma collection
        named target_<name> into the target dir.

    wipe-foreign  host-prefix-1 [host-prefix-2 ...]
        From the global ~/.tlx/js_analyzer.db, DELETE every row whose
        `file` column does NOT match one of the given host prefixes.
        Used to clear leftover state from earlier targets before resuming
        chain-triage / audit on the current target.

    wipe-target   host-prefix-1 [host-prefix-2 ...]
        From the global ~/.tlx/js_analyzer.db, DELETE every row matching
        the given host prefixes. Used after `snapshot` to leave the global
        DB clean for the next target.

Both wipe modes operate on these tables, in FK-safe order:
    dataflow_edges -> variables -> node_taint_flows -> node_sanitizers ->
    node_tags -> edges -> import_edges -> url_refs -> file_hashes -> nodes
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from pathlib import Path

TLX_HOME = Path.home() / ".tlx"
DEFAULT_DB = TLX_HOME / "js_analyzer.db"
CHROMA_DIR = TLX_HOME / "chroma"
CHROMA_META_DB = CHROMA_DIR / "chroma.sqlite3"


def _prefix_clause(prefixes: list[str], col: str = "file", negate: bool = False) -> tuple[str, list]:
    if not prefixes:
        raise ValueError("at least one host prefix required")
    op = "NOT LIKE" if negate else "LIKE"
    joiner = " AND " if negate else " OR "
    parts = [f"{col} {op} ?" for _ in prefixes]
    params = [f"{p}%" if p.endswith("/") else f"{p}/%" for p in prefixes]
    return "(" + joiner.join(parts) + ")", params


def _delete_for_node_ids(conn: sqlite3.Connection, where_node_ids: str, params: list) -> dict[str, int]:
    """Cascade delete given a WHERE clause that yields node ids of interest."""
    counts: dict[str, int] = {}
    cur = conn.cursor()

    def run(sql: str, p: list = []) -> int:
        cur.execute(sql, p)
        return cur.rowcount

    counts["dataflow_edges"] = run(
        f"DELETE FROM dataflow_edges WHERE from_var IN "
        f"(SELECT id FROM variables WHERE node_id IN ({where_node_ids})) OR "
        f"to_var IN (SELECT id FROM variables WHERE node_id IN ({where_node_ids}))",
        params + params,
    )
    counts["variables"] = run(
        f"DELETE FROM variables WHERE node_id IN ({where_node_ids})", params
    )
    counts["node_taint_flows"] = run(
        f"DELETE FROM node_taint_flows WHERE node_id IN ({where_node_ids})", params
    )
    counts["node_sanitizers"] = run(
        f"DELETE FROM node_sanitizers WHERE node_id IN ({where_node_ids})", params
    )
    counts["node_tags"] = run(
        f"DELETE FROM node_tags WHERE node_id IN ({where_node_ids})", params
    )
    counts["edges"] = run(
        f"DELETE FROM edges WHERE caller_id IN ({where_node_ids}) "
        f"OR callee_id IN ({where_node_ids})",
        params + params,
    )
    return counts


def _delete_by_file(conn: sqlite3.Connection, clause: str, params: list) -> dict[str, int]:
    counts: dict[str, int] = {}
    where_node_ids = f"SELECT id FROM nodes WHERE {clause}"
    counts.update(_delete_for_node_ids(conn, where_node_ids, params))

    cur = conn.cursor()
    counts["import_edges"] = cur.execute(
        f"DELETE FROM import_edges WHERE {clause}", params
    ).rowcount
    counts["url_refs"] = cur.execute(
        f"DELETE FROM url_refs WHERE {clause}", params
    ).rowcount
    counts["file_hashes"] = cur.execute(
        f"DELETE FROM file_hashes WHERE {clause}", params
    ).rowcount
    counts["nodes"] = cur.execute(
        f"DELETE FROM nodes WHERE {clause}", params
    ).rowcount
    return counts


def _filter_db(db_path: Path, prefixes: list[str], keep: bool) -> dict[str, int]:
    """Open db_path and delete rows matching (keep=False) or NOT matching (keep=True) the prefixes."""
    clause, params = _prefix_clause(prefixes, negate=keep)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = OFF;")
        counts = _delete_by_file(conn, clause, params)
        conn.commit()
        conn.execute("VACUUM;")
        return counts
    finally:
        conn.close()


def _snapshot_chroma(target_name: str, out_dir: Path) -> dict:
    """Copy the target's chroma collection (all segment dirs) plus a filtered
    chroma.sqlite3 metadata DB. The metadata copy is dropped down to rows that
    reference only this collection so the snapshot is self-contained.
    """
    if not CHROMA_META_DB.exists():
        return {"chroma_skipped": "no chroma.sqlite3"}
    coll_name = f"target_{target_name}"
    src = sqlite3.connect(str(CHROMA_META_DB))
    src.row_factory = sqlite3.Row
    coll_row = src.execute(
        "SELECT id FROM collections WHERE name = ?", (coll_name,)
    ).fetchone()
    if coll_row is None:
        src.close()
        return {"chroma_skipped": f"no collection {coll_name}"}
    coll_id = coll_row["id"]
    seg_ids = [
        r["id"] for r in src.execute(
            "SELECT id FROM segments WHERE collection = ?", (coll_id,)
        )
    ]
    src.close()

    target_chroma = out_dir / "chroma"
    target_chroma.mkdir(parents=True, exist_ok=True)

    copied_segs: list[str] = []
    missing_segs: list[str] = []
    for seg_id in seg_ids:
        seg_src = CHROMA_DIR / seg_id
        if not seg_src.is_dir():
            missing_segs.append(seg_id)
            continue
        seg_dst = target_chroma / seg_id
        if seg_dst.exists():
            shutil.rmtree(seg_dst)
        shutil.copytree(seg_src, seg_dst)
        copied_segs.append(seg_id)

    meta_dst = target_chroma / "chroma.sqlite3"
    shutil.copyfile(CHROMA_META_DB, meta_dst)
    # Filter metadata copy to this collection only.
    m = sqlite3.connect(str(meta_dst))
    m.execute("PRAGMA foreign_keys = OFF;")
    m.execute("DELETE FROM collections WHERE id != ?", (coll_id,))
    for tbl, col in [
        ("segments", "collection"),
        ("collection_metadata", "collection_id"),
    ]:
        try:
            m.execute(f"DELETE FROM {tbl} WHERE {col} != ?", (coll_id,))
        except sqlite3.OperationalError:
            pass
    m.commit()
    m.execute("VACUUM;")
    m.close()
    return {
        "chroma_collection": coll_name,
        "chroma_collection_id": coll_id,
        "segments_copied": copied_segs,
        "segments_missing_on_disk": missing_segs,
    }


def cmd_snapshot(target_dir: Path, prefixes: list[str]) -> int:
    target_dir = target_dir.resolve()
    name = target_dir.name
    out = target_dir / "db"
    out.mkdir(parents=True, exist_ok=True)

    snap = out / "js_analyzer.db"
    shutil.copyfile(DEFAULT_DB, snap)
    print(f"copied {DEFAULT_DB} -> {snap}", file=sys.stderr)
    counts = _filter_db(snap, prefixes, keep=True)
    print(f"snapshot filtered: {counts}", file=sys.stderr)

    chroma_info = _snapshot_chroma(name, out)
    print(f"chroma: {chroma_info}", file=sys.stderr)
    return 0


def cmd_wipe_foreign(prefixes: list[str]) -> int:
    counts = _filter_db(DEFAULT_DB, prefixes, keep=True)
    print(f"wiped foreign rows: {counts}", file=sys.stderr)
    return 0


def cmd_wipe_target(prefixes: list[str]) -> int:
    counts = _filter_db(DEFAULT_DB, prefixes, keep=False)
    print(f"wiped target rows: {counts}", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("snapshot")
    sp.add_argument("target_dir")
    sp.add_argument("host_prefixes", nargs="+")

    wf = sub.add_parser("wipe-foreign")
    wf.add_argument("host_prefixes", nargs="+")

    wt = sub.add_parser("wipe-target")
    wt.add_argument("host_prefixes", nargs="+")

    a = ap.parse_args()
    if a.cmd == "snapshot":
        return cmd_snapshot(Path(a.target_dir), a.host_prefixes)
    if a.cmd == "wipe-foreign":
        return cmd_wipe_foreign(a.host_prefixes)
    if a.cmd == "wipe-target":
        return cmd_wipe_target(a.host_prefixes)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
