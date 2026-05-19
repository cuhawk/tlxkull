#!/usr/bin/env python3
"""Compress a chains JSONL file (bestfirst or bounded).

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §20.

Wraps tlx.modules.js_analyzer.chain_compress.compress_chain so both
path shapes (list[str] from extract_chains_bestfirst.py and list[dict]
from extract_chains_bounded.py) are handled.

Usage:
  bin/chain_compress.py <target>              # auto-detect hot/all
  bin/chain_compress.py <target> --input chains/hot.jsonl
  bin/chain_compress.py <target> --render-md  # also emit markdown narrative
  bin/chain_compress.py <target> --out chains/all_compressed.jsonl
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--input", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--render-md", action="store_true")
    args = ap.parse_args()

    target = resolve_target_dir(args.target)
    src = Path(args.input).resolve() if args.input else pick_chain_input(target)
    if not src or not src.exists():
        print(f"no chain input found for {target.name}", file=sys.stderr)
        return 2

    out_path = (
        Path(args.out).resolve()
        if args.out
        else src.with_name(src.stem + "_compressed.jsonl")
    )

    tlx_sys_path()
    from modules.js_analyzer.chain_compress import (  # noqa: E402
        compress_chain,
        render_narrative,
    )

    total = compressed = preserved_evidence = 0
    sum_ratio = 0.0
    with src.open("r", encoding="utf-8") as fin, out_path.open(
        "w", encoding="utf-8"
    ) as fout:
        for raw in fin:
            raw = raw.strip()
            if not raw:
                continue
            chain = json.loads(raw)
            compress_chain(chain)
            total += 1
            ratio = float(chain.get("compression_ratio", 0.0) or 0.0)
            sum_ratio += ratio
            if ratio > 0:
                compressed += 1
            preserved_evidence += len(chain.get("decisions_preserved") or [])
            fout.write(json.dumps(chain, ensure_ascii=False) + "\n")
            if args.render_md:
                fout.write("---\n" + render_narrative(chain) + "\n---\n")

    avg_ratio = round(sum_ratio / total, 4) if total else 0.0
    summary = {
        "target": target.name,
        "input": str(src),
        "output": str(out_path),
        "chains_seen": total,
        "chains_compressed": compressed,
        "avg_compression_ratio": avg_ratio,
        "decisions_preserved_total": preserved_evidence,
    }
    print(json.dumps(summary, indent=2))

    write_status_phase(
        target,
        "chain_compress",
        {
            "status": "done",
            "ts": utcnow(),
            "input": str(src),
            "output": str(out_path),
            "chains_compressed": compressed,
            "avg_compression_ratio": avg_ratio,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
