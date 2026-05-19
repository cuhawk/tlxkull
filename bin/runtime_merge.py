#!/usr/bin/env python3
"""Static ↔ runtime reconciliation merger.

Plan: plans/ARCHITECTURE_EVOLUTION.md §7.4.

Reads ``targets/<name>/runtime/<run-id>/events.jsonl`` and joins each
event back to the static graph by:

  * file + line caller-frame extraction → callgraph node match
  * eval_source body → write to ``sources/_eval/<sha256>.js`` (so a
    subsequent ``js-index`` indexes it)
  * webpack_resolve chunkId → ``webpack_modules.json``
  * sink_fire (innerHTML, document.write, setAttribute) → upgrade the
    matching static sink's confidence + insert a node_tag row with
    source='runtime_observed', confidence 1.0
  * continuation (Promise.then etc.) → insert continuation edge row
  * set_proto → insert ``runtime_proto_write`` tag

Outputs:
  * inserts into ``edges`` (resolved_kind='runtime_observed')
  * inserts into ``node_tags`` (source='runtime_observed')
  * writes ``runtime/<run-id>/webpack_modules.json``
  * writes ``sources/_eval/`` (when --feed-eval is on)

Usage:
  bin/runtime_merge.py <target>                 # latest run
  bin/runtime_merge.py <target> --run <id>      # specific run
  bin/runtime_merge.py <target> --feed-eval     # also write eval corpus to sources/_eval/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    per_target_db,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


_FRAME_RE = re.compile(
    r"(?:at\s+)?(?P<fn>[^\s@(]+)\s*[@(]?\s*"
    r"(?P<file>[^\s:()]+):(?P<line>\d+):(?P<col>\d+)"
)


def _frame_match(frame: str) -> tuple[str, str, int] | None:
    m = _FRAME_RE.search(frame or "")
    if not m:
        return None
    return m.group("fn"), m.group("file"), int(m.group("line"))


def _latest_run(target: Path) -> Path | None:
    rt = target / "runtime"
    if not rt.exists():
        return None
    runs = sorted(p for p in rt.iterdir() if p.is_dir())
    return runs[-1] if runs else None


def _node_by_file_line(
    conn: sqlite3.Connection, file: str, line: int
) -> int | None:
    row = conn.execute(
        "SELECT id FROM nodes WHERE file LIKE ? "
        "  AND start_line <= ? AND (end_line IS NULL OR end_line >= ?) "
        "ORDER BY (end_line - start_line) ASC LIMIT 1",
        (f"%{Path(file).name}", line, line),
    ).fetchone()
    return int(row[0]) if row else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--run", default=None)
    ap.add_argument("--feed-eval", action="store_true")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    db = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2

    if args.run:
        run_dir = target / "runtime" / args.run
    else:
        run_dir = _latest_run(target)
    if not run_dir or not run_dir.exists():
        print(f"no runtime/<run-id> for {target.name}", file=sys.stderr)
        return 2
    events_jsonl = run_dir / "events.jsonl"
    if not events_jsonl.exists():
        print(f"no events.jsonl in {run_dir}", file=sys.stderr)
        return 2

    summary: dict = {
        "target": target.name,
        "run_dir": str(run_dir),
        "events": 0,
        "edges_added": 0,
        "tags_added": 0,
        "eval_bodies": 0,
        "webpack_modules": 0,
        "set_proto": 0,
        "by_kind": defaultdict(int),
    }
    webpack: dict[str, dict] = {}
    eval_bodies: dict[str, str] = {}

    tlx_sys_path()

    conn = sqlite3.connect(str(db))
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    has_source_col = "source" in cols
    has_conf_col = "confidence" in cols
    edge_cols = {r[1] for r in conn.execute("PRAGMA table_info(edges)")}
    has_eclass = "edge_class" in edge_cols

    cur = conn.cursor()
    with events_jsonl.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            summary["events"] += 1
            summary["by_kind"][ev.get("kind", "?")] += 1
            frames = ev.get("fn_caller") or []
            owner_node: int | None = None
            for fr in frames:
                m = _frame_match(fr)
                if not m:
                    continue
                _, file, line = m
                nid = _node_by_file_line(conn, file, line)
                if nid is not None:
                    owner_node = nid
                    break

            kind = ev.get("kind")
            if kind == "eval_source":
                bodies = [a for a in (ev.get("args_preview") or []) if isinstance(a, str)]
                if not bodies:
                    continue
                body = max(bodies, key=len)
                digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
                eval_bodies[digest] = body
            elif kind == "webpack_resolve":
                meta = ev.get("meta") or {}
                cid = str(meta.get("chunkId") or "?")
                webpack[cid] = {
                    "body_len": meta.get("body_len"),
                    "first_seen_url": ev.get("url"),
                }
            elif kind == "sink_fire" and owner_node is not None:
                meta = ev.get("meta") or {}
                taxid_map = {
                    "innerHTML": "innerHTML_assign",
                    "outerHTML": "outerHTML_assign",
                    "document.write": "document_write",
                    "setAttribute": "react_ref_callback",
                }
                taxid = taxid_map.get(meta.get("prop", ""), "runtime_dom_sink")
                _insert_tag(cur, owner_node, taxid, "sink", "high",
                            has_source_col, has_conf_col, 1.0,
                            origin="runtime_observed")
                summary["tags_added"] += 1
            elif kind == "continuation" and owner_node is not None:
                # Best-effort virtual edge: handler we couldn't see
                # statically. We can't always resolve callee_id from a
                # registration; mark caller-only with NULL callee.
                _insert_edge(cur, owner_node, None,
                             "runtime_observed", has_eclass,
                             "[runtime] handler registration")
                summary["edges_added"] += 1
            elif kind == "set_proto" and owner_node is not None:
                _insert_tag(cur, owner_node, "runtime_proto_write",
                            "sink", "medium",
                            has_source_col, has_conf_col, 1.0,
                            origin="runtime_observed")
                summary["set_proto"] += 1
                summary["tags_added"] += 1

    conn.commit()
    conn.close()

    # webpack_modules.json
    if webpack:
        (run_dir / "webpack_modules.json").write_text(
            json.dumps(webpack, indent=2, sort_keys=True)
        )
        summary["webpack_modules"] = len(webpack)

    # eval corpus feed
    if args.feed_eval and eval_bodies:
        eval_dir = target / "sources" / "_eval"
        eval_dir.mkdir(parents=True, exist_ok=True)
        idx_path = eval_dir / "_index.json"
        idx: dict = {}
        if idx_path.exists():
            try:
                idx = json.loads(idx_path.read_text())
            except Exception:
                idx = {}
        for d, body in eval_bodies.items():
            out = eval_dir / f"{d}.js"
            if not out.exists():
                out.write_text(body, encoding="utf-8")
                summary["eval_bodies"] += 1
            idx[d] = {"len": len(body), "from_run": run_dir.name}
        idx_path.write_text(json.dumps(idx, indent=2))
    elif eval_bodies:
        summary["eval_bodies"] = len(eval_bodies)

    summary["by_kind"] = dict(summary["by_kind"])
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "runtime_merge",
        {
            "status": "done",
            "ts": utcnow(),
            "events": summary["events"],
            "tags_added": summary["tags_added"],
            "edges_added": summary["edges_added"],
        },
    )
    return 0


def _insert_tag(
    cur, nid, taxid, kind, sev, has_source_col, has_conf_col, conf,
    *, origin: str = "runtime_observed",
) -> None:
    cols = ["node_id", "taxonomy_id", "kind", "severity"]
    ph = ["?", "?", "?", "?"]
    vals: list = [nid, taxid, kind, sev]
    if has_source_col:
        cols.append("source"); ph.append("?"); vals.append(origin)
    if has_conf_col:
        cols.append("confidence"); ph.append("?"); vals.append(conf)
    try:
        cur.execute(
            f"INSERT OR IGNORE INTO node_tags ({', '.join(cols)}) "
            f"VALUES ({', '.join(ph)})", tuple(vals),
        )
    except sqlite3.OperationalError:
        pass


def _insert_edge(
    cur, caller_id, callee_id, resolved_kind, has_eclass, raw: str
) -> None:
    try:
        if has_eclass:
            cur.execute(
                "INSERT INTO edges "
                "(caller_id, callee_id, resolved_kind, line, raw, edge_class) "
                "VALUES (?, ?, ?, NULL, ?, 'runtime_observed')",
                (caller_id, callee_id, resolved_kind, raw),
            )
        else:
            cur.execute(
                "INSERT INTO edges "
                "(caller_id, callee_id, resolved_kind, line, raw) "
                "VALUES (?, ?, ?, NULL, ?)",
                (caller_id, callee_id, resolved_kind, raw),
            )
    except sqlite3.OperationalError:
        pass


if __name__ == "__main__":
    raise SystemExit(main())
