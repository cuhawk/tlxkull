#!/usr/bin/env python3
"""Export TLX's internal js_analyzer artifacts for one target into
targets/<name>/index/ so the engagement folder is self-contained.

Reads from ~/.tlx/js_analyzer.db and writes:
  index/nodes.jsonl
  index/edges.jsonl
  index/tags.jsonl
  index/frameworks.json   (only if --frameworks provided)
  index/_skipped.json     (best-effort; empty if analyzer doesn't track)

Usage:
  bin/export_index.py <target_name> <out_dir> [--frameworks '["react",...]']
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TLX_HOME = Path(os.path.expanduser("~/.tlx"))
DB_PATH = TLX_HOME / "js_analyzer.db"


def export(target_name: str, out_dir: Path, frameworks: list | None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        raise FileNotFoundError(f"missing {DB_PATH}; run js_index_target first")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    nodes = [
        {
            "qname": r["qualified_name"],
            "file": r["file"],
            "line": r["start_line"],
            "end_line": r["end_line"],
            "kind": r["kind"],
            "parent": r["parent"],
            "name": r["name"],
            "original_file": r["original_file"],
            "original_line": r["original_line"],
        }
        for r in conn.execute(
            "SELECT id, qualified_name, file, name, parent, kind, "
            "start_line, end_line, original_file, original_line FROM nodes"
        )
    ]

    edges = [
        {
            "caller_qname": r["caller_qname"],
            "callee_qname": r["callee_qname"] or r["callee_raw"],
            "callee_raw": r["callee_raw"],
            "edge_kind": r["resolved_kind"],
            "line": r["line"],
        }
        for r in conn.execute(
            "SELECT n1.qualified_name AS caller_qname, "
            "       n2.qualified_name AS callee_qname, "
            "       e.callee_raw, e.resolved_kind, e.line "
            "FROM edges e "
            "JOIN nodes n1 ON n1.id = e.caller_id "
            "LEFT JOIN nodes n2 ON n2.id = e.callee_id"
        )
    ]

    tags = [
        {
            "qname": r["qualified_name"],
            "file": r["file"],
            "taxonomy_id": r["taxonomy_id"],
            "kind": r["kind"],
            "severity": r["severity"],
            "line": r["line"],
            "source": r["source"],
        }
        for r in conn.execute(
            "SELECT n.qualified_name, n.file, t.taxonomy_id, t.kind, "
            "       t.severity, t.line, t.source "
            "FROM node_tags t JOIN nodes n ON n.id = t.node_id"
        )
    ]

    def _write_jsonl(name: str, rows: list) -> None:
        with (out_dir / name).open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, default=str) + "\n")

    _write_jsonl("nodes.jsonl", nodes)
    _write_jsonl("edges.jsonl", edges)
    _write_jsonl("tags.jsonl", tags)
    (out_dir / "frameworks.json").write_text(
        json.dumps(frameworks or [], indent=2)
    )
    (out_dir / "_skipped.json").write_text("[]")

    summary = {
        "target": target_name,
        "nodes": len(nodes), "edges": len(edges),
        "tags": len(tags), "frameworks": frameworks or [], "skipped": 0,
    }
    print(json.dumps(summary, indent=2))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target_name")
    ap.add_argument("out_dir")
    ap.add_argument("--frameworks", default=None,
                    help='JSON array of detected frameworks, e.g. \'["react"]\'')
    a = ap.parse_args()
    fws = json.loads(a.frameworks) if a.frameworks else None
    export(a.target_name, Path(a.out_dir).resolve(), fws)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
