#!/usr/bin/env python3
"""Diff two chain JSONL files OR two callgraph snapshots.

Chain mode (default):
    bin/chain_diff.py <old.jsonl> <new.jsonl>

  Diffs taint chain pairs (source_qname, sink_qname). Reports added /
  removed / kept plus distributions.

Snapshot mode (--snapshots):
    bin/chain_diff.py --snapshots <old.json> <new.json>

  Diffs callgraph snapshots produced by CallGraph.snapshot_graph(),
  reporting newly-tagged sinks, newly-reachable edges, and changed
  tag set on existing nodes.

Combined baseline mode:
    bin/chain_diff.py --baseline <prev.jsonl> --new <current.jsonl>
                      [--baseline-snapshot <prev_graph.json>]
                      [--new-snapshot <current_graph.json>]

  Chain diff plus optional snapshot context. Designed for CI/CD: exit 1
  if any chain in the new set is also new in the graph snapshot (i.e.
  the snapshot proves the chain was introduced by this scan).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


# ─── chain-mode helpers ──────────────────────────────────────────────────


def load_chains(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def chain_pair(c: dict) -> tuple[str, str]:
    return (c["source"]["qname"], c["sink"]["qname"])


def chain_diff(old: list[dict], new: list[dict]) -> dict:
    old_pairs = {chain_pair(c): c for c in old}
    new_pairs = {chain_pair(c): c for c in new}
    added = sorted(set(new_pairs) - set(old_pairs))
    removed = sorted(set(old_pairs) - set(new_pairs))
    kept = sorted(set(new_pairs) & set(old_pairs))
    return {
        "old_count":   len(old),
        "new_count":   len(new),
        "added":       added,
        "removed":     removed,
        "kept":        kept,
        "added_chains":   [new_pairs[p] for p in added],
        "removed_chains": [old_pairs[p] for p in removed],
    }


def print_chain_diff(diff: dict) -> None:
    print(f"old: {diff['old_count']}  new: {diff['new_count']}")
    print(f"  added:   {len(diff['added'])}")
    print(f"  removed: {len(diff['removed'])}")
    print(f"  kept:    {len(diff['kept'])}")
    print()

    added_chains = diff["added_chains"]
    if added_chains:
        print("=== added: file-pair distribution ===")
        fp = Counter(
            (c["source"]["file"].split("__")[0], c["sink"]["file"].split("__")[0])
            for c in added_chains
        )
        for k, n in fp.most_common(20):
            print(f"  {n:4d}  {k[0][:40]:40s} -> {k[1][:40]}")
        print()
        print("=== added: taxonomy-pair distribution ===")
        tx = Counter(
            (c["source"]["taxonomy_id"], c["sink"]["taxonomy_id"])
            for c in added_chains
        )
        for k, n in tx.most_common(20):
            print(f"  {n:4d}  {k[0]:40s} -> {k[1]}")
        print()
        print("=== added: cross-file chains (top 30 by score) ===")
        cross = [c for c in added_chains if c.get("cross_file")]
        for c in sorted(cross, key=lambda x: -x.get("score", 0))[:30]:
            print(
                f"  score={c.get('score',0):.1f}  "
                f"{c['source']['taxonomy_id']:30s} -> {c['sink']['taxonomy_id']:30s}  "
                f"{c['source']['file'][:30]} -> {c['sink']['file'][:30]}"
            )


# ─── snapshot-mode helpers ───────────────────────────────────────────────


def load_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot_diff(old: dict, new: dict) -> dict:
    """Diff two callgraph snapshots by (qname, kind) for nodes and by
    (caller_qname, callee_qname, kind) for edges. Sink-tag changes are
    computed on the node-qname basis so node-id churn between scans
    doesn't produce false 'added' signal."""
    old_nodes = {n["qname"]: n for n in old.get("nodes", [])}
    new_nodes = {n["qname"]: n for n in new.get("nodes", [])}
    old_node_id_to_qname = {n["id"]: n["qname"] for n in old.get("nodes", [])}
    new_node_id_to_qname = {n["id"]: n["qname"] for n in new.get("nodes", [])}

    added_nodes   = sorted(set(new_nodes) - set(old_nodes))
    removed_nodes = sorted(set(old_nodes) - set(new_nodes))

    def edge_key(e: dict, id_to_q: dict) -> tuple[str, str, str] | None:
        c = id_to_q.get(e.get("from"))
        d = id_to_q.get(e.get("to"))
        if not c or not d:
            return None
        return (c, d, e.get("kind", ""))

    old_edges = {k for e in old.get("edges", [])
                 if (k := edge_key(e, old_node_id_to_qname)) is not None}
    new_edges = {k for e in new.get("edges", [])
                 if (k := edge_key(e, new_node_id_to_qname)) is not None}
    added_edges   = sorted(new_edges - old_edges)
    removed_edges = sorted(old_edges - new_edges)

    def tag_set(snap: dict, id_to_q: dict) -> set[tuple[str, str, str]]:
        out: set[tuple[str, str, str]] = set()
        for t in snap.get("tags", []):
            q = id_to_q.get(t.get("node"))
            if not q:
                continue
            out.add((q, t.get("kind", ""), t.get("taxonomy", "")))
        return out

    old_tags = tag_set(old, old_node_id_to_qname)
    new_tags = tag_set(new, new_node_id_to_qname)
    added_tags   = sorted(new_tags - old_tags)
    removed_tags = sorted(old_tags - new_tags)

    new_sinks   = [t for t in added_tags   if t[1] == "sink"]
    new_sources = [t for t in added_tags   if t[1] == "source"]

    return {
        "old_hash":      old.get("content_hash"),
        "new_hash":      new.get("content_hash"),
        "node_added":    added_nodes,
        "node_removed":  removed_nodes,
        "edge_added":    added_edges,
        "edge_removed":  removed_edges,
        "tag_added":     added_tags,
        "tag_removed":   removed_tags,
        "new_sinks":     new_sinks,
        "new_sources":   new_sources,
    }


def print_snapshot_diff(diff: dict) -> None:
    print(f"old hash: {diff['old_hash']}")
    print(f"new hash: {diff['new_hash']}")
    print()
    print(f"nodes  added:   {len(diff['node_added'])}")
    print(f"nodes  removed: {len(diff['node_removed'])}")
    print(f"edges  added:   {len(diff['edge_added'])}")
    print(f"edges  removed: {len(diff['edge_removed'])}")
    print(f"tags   added:   {len(diff['tag_added'])} "
          f"(new sinks: {len(diff['new_sinks'])}, "
          f"new sources: {len(diff['new_sources'])})")
    print(f"tags   removed: {len(diff['tag_removed'])}")
    print()
    if diff["new_sinks"]:
        print("=== newly-tagged sinks ===")
        for q, _kind, tax in diff["new_sinks"][:40]:
            print(f"  {tax:32s}  {q}")
    if diff["new_sources"]:
        print()
        print("=== newly-tagged sources ===")
        for q, _kind, tax in diff["new_sources"][:40]:
            print(f"  {tax:32s}  {q}")


# ─── CLI ─────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])

    # Back-compat positional form: two args = chain diff
    if (
        len(argv) == 2
        and not argv[0].startswith("-")
        and not argv[1].startswith("-")
    ):
        diff = chain_diff(load_chains(Path(argv[0])), load_chains(Path(argv[1])))
        print_chain_diff(diff)
        return 0

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshots", action="store_true",
        help="Diff two callgraph snapshots instead of chain JSONL files.",
    )
    parser.add_argument(
        "--baseline", type=Path,
        help="Baseline chain JSONL (combined-mode chain diff).",
    )
    parser.add_argument(
        "--new", dest="new_chains", type=Path,
        help="Current chain JSONL (combined-mode chain diff).",
    )
    parser.add_argument(
        "--baseline-snapshot", type=Path,
        help="Baseline callgraph snapshot JSON.",
    )
    parser.add_argument(
        "--new-snapshot", type=Path,
        help="Current callgraph snapshot JSON.",
    )
    parser.add_argument(
        "--fail-on-new", action="store_true",
        help="Exit 1 if any chain or sink was newly introduced.",
    )
    parser.add_argument(
        "positional", nargs="*",
        help="In --snapshots mode: <old.json> <new.json>.",
    )
    args = parser.parse_args(argv)

    introduced = 0

    if args.snapshots:
        if len(args.positional) != 2:
            parser.error("--snapshots requires two positional snapshot paths")
        diff = snapshot_diff(
            load_snapshot(Path(args.positional[0])),
            load_snapshot(Path(args.positional[1])),
        )
        print_snapshot_diff(diff)
        introduced += len(diff["new_sinks"])

    if args.baseline and args.new_chains:
        diff = chain_diff(
            load_chains(args.baseline),
            load_chains(args.new_chains),
        )
        print_chain_diff(diff)
        introduced += len(diff["added"])
    elif args.baseline or args.new_chains:
        parser.error("--baseline and --new must be passed together")

    if args.baseline_snapshot and args.new_snapshot:
        if args.baseline and args.new_chains:
            print()
            print("--- snapshot context ---")
        diff = snapshot_diff(
            load_snapshot(args.baseline_snapshot),
            load_snapshot(args.new_snapshot),
        )
        print_snapshot_diff(diff)
        introduced += len(diff["new_sinks"])
    elif args.baseline_snapshot or args.new_snapshot:
        parser.error("--baseline-snapshot and --new-snapshot must be passed together")

    if args.fail_on_new and introduced > 0:
        print(f"\n!! fail-on-new: {introduced} new chain(s)/sink(s) detected")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
