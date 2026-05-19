#!/usr/bin/env python3
"""Corpus management driver.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §19.

Three subcommands:

  match <target>          # match every chain in chains/hot.jsonl against
                            the corpus and emit chains/_corpus_matches.jsonl
  record <target> <id>    # record a confirmed chain into the corpus
                            (id is the chain['id'] from chains/hot.jsonl)
  decay                   # walk fingerprints and downweight stale ones
  list                    # dump every fingerprint id + weight
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    pick_chain_input,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


def _frameworks(target: Path) -> list[str]:
    fp = target / "frameworks.json"
    if not fp.exists():
        return []
    try:
        data = json.loads(fp.read_text())
    except Exception:
        return []
    if isinstance(data, dict):
        for key in ("detected", "frameworks"):
            if key in data and isinstance(data[key], list):
                return [str(x) for x in data[key]]
    if isinstance(data, list):
        return [str(x) for x in data]
    return []


def cmd_match(target: Path) -> int:
    chains = pick_chain_input(target)
    if not chains or not chains.exists():
        print(f"no chain input for {target.name}", file=sys.stderr)
        return 2
    tlx_sys_path()
    from modules.js_analyzer.corpus import match  # noqa: E402

    frameworks = _frameworks(target)
    out_rows: list[dict] = []
    rows_total = matched = 0
    with chains.open("r", encoding="utf-8") as fin:
        for raw in fin:
            raw = raw.strip()
            if not raw:
                continue
            chain = json.loads(raw)
            rows_total += 1
            hits = match(chain, framework_set=frameworks)
            if not hits:
                continue
            matched += 1
            out_rows.append({
                "chain_id": chain.get("id"),
                "matches": [
                    {"id": fp.id, "score": s, "weight": fp.weight,
                     "archetype_md": fp.archetype_md}
                    for fp, s in hits[:5]
                ],
            })
    out = target / "chains" / "_corpus_matches.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r) for r in out_rows)
                   + ("\n" if out_rows else ""))
    summary = {
        "target": target.name,
        "chains_total": rows_total,
        "chains_matched": matched,
        "output": str(out),
    }
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target, "corpus_match",
        {"status": "done", "ts": utcnow(), "matched": matched},
    )
    return 0


def cmd_record(target: Path, chain_id: int) -> int:
    chains = pick_chain_input(target)
    if not chains or not chains.exists():
        print(f"no chain input for {target.name}", file=sys.stderr)
        return 2
    tlx_sys_path()
    from modules.js_analyzer.corpus_post_confirm import record_confirmation  # noqa: E402

    frameworks = _frameworks(target)
    chain: dict | None = None
    with chains.open("r", encoding="utf-8") as fin:
        for raw in fin:
            raw = raw.strip()
            if not raw:
                continue
            row = json.loads(raw)
            if row.get("id") == chain_id or str(row.get("id")) == str(chain_id):
                chain = row
                break
    if chain is None:
        print(f"chain id {chain_id} not found in {chains}", file=sys.stderr)
        return 2
    out = record_confirmation(chain, target, frameworks=frameworks)
    print(json.dumps({"recorded": str(out), "chain_id": chain.get("id")}, indent=2))
    return 0


def cmd_decay() -> int:
    tlx_sys_path()
    from modules.js_analyzer.corpus_post_confirm import decay_corpus_weights  # noqa: E402

    changes = decay_corpus_weights()
    print(json.dumps({
        "decayed": [{"path": p, "old": old, "new": new}
                    for p, (old, new) in changes.items()],
        "count": len(changes),
    }, indent=2))
    return 0


def cmd_list() -> int:
    tlx_sys_path()
    from modules.js_analyzer.corpus import load_fingerprints  # noqa: E402

    fps = load_fingerprints()
    rows = [
        {"id": fp.id, "weight": fp.weight,
         "source_kinds": list(fp.source_kinds),
         "sink_kinds": list(fp.sink_kinds),
         "provenance_count": fp.provenance_count}
        for fp in fps
    ]
    print(json.dumps(rows, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_m = sub.add_parser("match")
    sp_m.add_argument("target")

    sp_r = sub.add_parser("record")
    sp_r.add_argument("target")
    sp_r.add_argument("chain_id", type=int)

    sub.add_parser("decay")
    sub.add_parser("list")

    args = ap.parse_args()
    if args.cmd == "match":
        return cmd_match(resolve_target_dir(args.target))
    if args.cmd == "record":
        return cmd_record(resolve_target_dir(args.target), args.chain_id)
    if args.cmd == "decay":
        return cmd_decay()
    if args.cmd == "list":
        return cmd_list()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
