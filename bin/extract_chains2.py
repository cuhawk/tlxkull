#!/usr/bin/env python3
"""Instrumented variant of extract_chains.py with per-source timeout + progress log.

Wraps trace_to_sink with SIGALRM so a source that triggers BFS blowup is
skipped instead of hanging the whole extract. Emits one log line per source
so progress is visible.

Usage:
  bin/extract_chains2.py <target_dir>
      [--db <path>] [--severity high|medium|low]
      [--per-source-timeout 5]
      [--max-hot N]
"""
from __future__ import annotations

import argparse
import json
import math
import signal
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TLX = ROOT / "tlx"
sys.path.insert(0, str(TLX))


class _TimeoutError(Exception):
    pass


def _alarm_handler(signum, frame):
    raise _TimeoutError()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target_dir")
    ap.add_argument("--db", default=None)
    ap.add_argument("--severity", default="high")
    ap.add_argument("--max-hot", type=int, default=20)
    ap.add_argument("--per-source-timeout", type=int, default=5,
                    help="seconds budget per source trace_to_sink call")
    ap.add_argument("--max-sources", type=int, default=0,
                    help="if >0, cap number of sources processed")
    a = ap.parse_args()

    target_dir = Path(a.target_dir).resolve()
    name = target_dir.name
    db_path = Path(a.db) if a.db else (target_dir / "db" / "js_analyzer.db")
    if not db_path.exists():
        print(f"snapshot DB missing: {db_path}", file=sys.stderr)
        return 2

    out_dir = target_dir / "chains"
    out_dir.mkdir(parents=True, exist_ok=True)

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.callgraph_tools import (
        set_callgraph, trace_to_sink, find_sinks, list_entry_points,
    )
    from modules.js_analyzer.reporter import (
        _collect_sink_meta, _collect_source_meta, _reported_line,
    )

    cg = CallGraph(db_path)
    set_callgraph(cg, base_paths=[str(target_dir / "sources")])

    sinks_result = find_sinks(severity=a.severity)
    sources_result = list_entry_points()
    sinks_by_qname = _collect_sink_meta(sinks_result.get("sinks", []))
    sources_by_qname = _collect_source_meta(sources_result.get("sources", []))
    if not sources_by_qname or not sinks_by_qname:
        print("no sources or sinks", file=sys.stderr)
        return 3

    src_items = list(sources_by_qname.items())
    if a.max_sources > 0:
        src_items = src_items[: a.max_sources]
    total_src = len(src_items)
    print(f"sources={total_src} sinks={len(sinks_by_qname)} "
          f"per_source_timeout={a.per_source_timeout}s",
          file=sys.stderr, flush=True)

    signal.signal(signal.SIGALRM, _alarm_handler)

    chains: list[dict] = []
    chain_id = 0
    timeouts = 0
    no_paths = 0
    t0 = time.time()

    for i, (src_qname, src_meta) in enumerate(src_items, 1):
        elapsed = time.time() - t0
        if i == 1 or i % 25 == 0:
            print(f"[{elapsed:6.1f}s] {i}/{total_src} "
                  f"chains={len(chains)} timeouts={timeouts} "
                  f"no_paths={no_paths} src={src_qname[:80]}",
                  file=sys.stderr, flush=True)
        signal.alarm(a.per_source_timeout)
        try:
            result = trace_to_sink(from_qname=src_qname, severity=a.severity)
            paths = result.get("paths", [])
        except _TimeoutError:
            timeouts += 1
            print(f"[{elapsed:6.1f}s]   TIMEOUT src={src_qname[:80]}",
                  file=sys.stderr, flush=True)
            continue
        finally:
            signal.alarm(0)

        if not paths:
            no_paths += 1
            continue

        for path_obj in paths:
            nodes = path_obj.get("nodes", [])
            if not nodes:
                continue
            sink_qname = nodes[-1]
            sink_meta = sinks_by_qname.get(sink_qname, {})
            sink_tax = (
                sink_meta.get("taxonomy_id")
                or path_obj.get("terminal_tag")
                or ""
            )
            sink_file = sink_meta.get("original_file") or sink_meta.get("file", "")
            if not sink_file:
                row = cg.conn.execute(
                    "SELECT file FROM nodes WHERE qualified_name=?", (sink_qname,)
                ).fetchone()
                if row:
                    sink_file = row[0]
            chain_id += 1
            chains.append({
                "id": chain_id,
                "source": {
                    "qname": src_qname,
                    "file": src_meta.get("original_file") or src_meta.get("file", ""),
                    "line": _reported_line(src_meta),
                    "taxonomy_id": src_meta.get("taxonomy_id", ""),
                    "kind": "source",
                },
                "sink": {
                    "qname": sink_qname,
                    "file": sink_file,
                    "line": _reported_line(sink_meta) if sink_meta else None,
                    "taxonomy_id": sink_tax,
                    "kind": "sink",
                },
                "depth": path_obj.get("depth", len(nodes) - 1),
                "path": nodes,
                "cross_file": (
                    src_meta.get("file", "") != sink_file
                    and bool(src_meta.get("file")) and bool(sink_file)
                ),
            })

    elapsed = time.time() - t0
    print(f"[{elapsed:6.1f}s] DONE chains={len(chains)} timeouts={timeouts} "
          f"no_paths={no_paths}", file=sys.stderr, flush=True)

    if not chains:
        return 0

    # Score: simple — high-sev sink + cross_file bonus + (8 - depth)
    def score(c):
        s = 50.0
        if c["sink"]["taxonomy_id"] in (
            "innerHTML_assign", "outerHTML_assign",
            "document.write", "eval", "new_Function",
            "setTimeout_string", "setInterval_string", "setImmediate_string",
            "srcdoc_assign", "insertAdjacentHTML_call",
        ):
            s += 30
        if c["cross_file"]:
            s += 15
        s += max(0, 8 - c.get("depth", 8)) * 2
        return s

    for c in chains:
        c["score"] = score(c)
    chains.sort(key=lambda c: -c["score"])

    (out_dir / "all.jsonl").write_text(
        "\n".join(json.dumps(c) for c in chains) + "\n"
    )
    n_hot = min(a.max_hot, max(1, math.ceil(len(chains) * 0.1)))
    (out_dir / "hot.jsonl").write_text(
        "\n".join(json.dumps(c) for c in chains[:n_hot]) + "\n"
    )

    sink_dist = Counter(c["sink"]["taxonomy_id"] for c in chains)
    src_dist = Counter(c["source"]["taxonomy_id"] for c in chains)
    triage = {
        "target": name,
        "db": str(db_path),
        "severity": a.severity,
        "total": len(chains),
        "hot": n_hot,
        "timeouts": timeouts,
        "no_paths": no_paths,
        "sink_dist": dict(sink_dist.most_common()),
        "source_dist": dict(src_dist.most_common()),
    }
    (out_dir / "triage.json").write_text(json.dumps(triage, indent=2))
    print(json.dumps(triage, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
