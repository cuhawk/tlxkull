#!/usr/bin/env python3
"""Export TLX's internal js_analyzer artifacts for one target into
targets/<name>/index/ so the engagement folder is self-contained.

Reads from ~/.tlx/sessions.db (or the js_analyzer-specific SQLite store
inside ~/.tlx/) and writes:
  index/nodes.jsonl
  index/edges.jsonl
  index/tags.jsonl
  index/frameworks.json
  index/_skipped.json   (files the analyzer couldn't parse)

Usage:
  python bin/export_index.py <target_name> <out_dir>
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TLX_HOME = Path(os.path.expanduser("~/.tlx"))


def _open_callgraph_db() -> sqlite3.Connection:
    """js_analyzer persists the callgraph in its own SQLite file inside
    ~/.tlx/. The exact name has varied; we probe the few common ones."""
    candidates = [
        TLX_HOME / "callgraph.db",
        TLX_HOME / "js_analyzer.db",
        TLX_HOME / "sessions.db",
    ]
    for c in candidates:
        if c.exists():
            return sqlite3.connect(c)
    raise FileNotFoundError(
        f"No TLX callgraph DB found in {TLX_HOME}. Run js-index first.")


def export(target_name: str, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    conn = _open_callgraph_db()
    conn.row_factory = sqlite3.Row

    def _rows(query: str, params: tuple = ()) -> list:
        try:
            return [dict(r) for r in conn.execute(query, params).fetchall()]
        except sqlite3.OperationalError:
            return []

    # Tables/column names may differ across TLX phases. We try a few.
    nodes = _rows("SELECT * FROM nodes WHERE target = ?", (target_name,)) \
        or _rows("SELECT * FROM cg_nodes")
    edges = _rows("SELECT * FROM edges WHERE target = ?", (target_name,)) \
        or _rows("SELECT * FROM cg_edges")
    tags  = _rows("SELECT * FROM tags  WHERE target = ?", (target_name,)) \
        or _rows("SELECT * FROM cg_tags")
    fws   = _rows("SELECT * FROM frameworks WHERE target = ?", (target_name,)) \
        or _rows("SELECT * FROM cg_frameworks")
    skipped = _rows("SELECT * FROM skipped_files WHERE target = ?", (target_name,))

    def _write_jsonl(name: str, rows: list) -> None:
        with (out_dir / name).open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, default=str) + "\n")

    _write_jsonl("nodes.jsonl", nodes)
    _write_jsonl("edges.jsonl", edges)
    _write_jsonl("tags.jsonl", tags)
    (out_dir / "frameworks.json").write_text(json.dumps(fws, indent=2, default=str))
    (out_dir / "_skipped.json").write_text(json.dumps(skipped, indent=2, default=str))

    summary = {
        "target": target_name,
        "nodes": len(nodes), "edges": len(edges),
        "tags": len(tags), "frameworks": fws, "skipped": len(skipped),
    }
    print(json.dumps(summary, default=str, indent=2))
    return summary


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    export(sys.argv[1], Path(sys.argv[2]).resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
