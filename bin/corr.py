#!/usr/bin/env python3
"""Multi-target correlation engine driver.

Plan: plans/ARCHITECTURE_EVOLUTION_V2.md §21.

Computes per-file bundle fingerprints (one per distinct file in the
per-target snapshot DB) and stores them under ``~/.tlx/corr/bundles/``.
Match operation queries the corpus for nearest neighbors by Jaccard
overlap of the top-100 qname set.

Usage:
  bin/corr.py fingerprint <target> [--bundle <file>]
  bin/corr.py match <target> [--threshold 0.3] [--top 10]
  bin/corr.py list [--target <name>]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    per_target_db,
    resolve_target_dir,
    tlx_sys_path,
    utcnow,
    write_status_phase,
)


def _frameworks_for_target(target: Path) -> tuple[list[str], dict[str, str]]:
    fp = target / "frameworks.json"
    if not fp.exists():
        return [], {}
    try:
        data = json.loads(fp.read_text())
    except Exception:
        return [], {}
    names: list[str] = []
    versions: dict[str, str] = {}
    if isinstance(data, dict):
        # Common shape: {"detected": [...], "versions": {name: ver}}.
        d = data.get("detected") or data.get("frameworks") or list(data.keys())
        if isinstance(d, list):
            names = [str(x) for x in d]
        v = data.get("versions") or data.get("library_versions") or {}
        if isinstance(v, dict):
            versions = {str(k): str(v[k]) for k in v}
    elif isinstance(data, list):
        names = [str(x) for x in data]
    return names, versions


def cmd_fingerprint(target: Path, bundle: str | None) -> int:
    db = per_target_db(target)
    if not db.exists():
        print(f"missing db: {db}", file=sys.stderr)
        return 2
    tlx_sys_path()
    from modules.js_analyzer.v2.multi_target_corr import (  # noqa: E402
        compute_fingerprint,
        save_fingerprint,
    )
    frameworks, versions = _frameworks_for_target(target)
    conn = sqlite3.connect(str(db))
    try:
        fps = compute_fingerprint(
            conn,
            target_name=target.name,
            bundle_file=bundle,
            frameworks=frameworks,
            library_versions=versions,
        )
    finally:
        conn.close()
    saved = [str(save_fingerprint(fp)) for fp in fps]
    summary = {
        "target": target.name,
        "bundles_fingerprinted": len(fps),
        "frameworks": frameworks,
        "saved": saved[:20] + ([f"... +{len(saved) - 20} more"] if len(saved) > 20 else []),
    }
    print(json.dumps(summary, indent=2))
    write_status_phase(
        target,
        "multi_target_corr_fingerprint",
        {"status": "done", "ts": utcnow(), "bundles": len(fps)},
    )
    return 0


def cmd_match(target: Path, threshold: float, top: int) -> int:
    tlx_sys_path()
    from modules.js_analyzer.v2.multi_target_corr import (  # noqa: E402
        load_target_fingerprints,
        match_against_corpus,
    )
    fps = load_target_fingerprints(target.name)
    if not fps:
        print(
            f"no fingerprints for {target.name}; "
            f"run `bin/corr.py fingerprint {target.name}` first",
            file=sys.stderr,
        )
        return 2
    payload: list[dict] = []
    for fp in fps:
        matches = match_against_corpus(fp, threshold=threshold)[:top]
        payload.append(
            {
                "bundle_id": fp.bundle_id,
                "file": fp.file,
                "matches": matches,
            }
        )
    out = {
        "target": target.name,
        "bundles_queried": len(fps),
        "threshold": threshold,
        "results": payload,
    }
    print(json.dumps(out, indent=2))
    write_status_phase(
        target,
        "multi_target_corr_match",
        {"status": "done", "ts": utcnow(), "bundles_queried": len(fps)},
    )
    return 0


def cmd_list(target_name: str | None) -> int:
    tlx_sys_path()
    from modules.js_analyzer.v2.multi_target_corr import (  # noqa: E402
        CORPUS_ROOT,
    )
    bundles_dir = CORPUS_ROOT / "bundles"
    rows: list[dict] = []
    if bundles_dir.exists():
        for p in sorted(bundles_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if target_name and data.get("target") != target_name:
                continue
            rows.append(
                {
                    "bundle_id": data.get("bundle_id"),
                    "target": data.get("target"),
                    "file": data.get("file"),
                    "frameworks": data.get("framework_set") or [],
                }
            )
    print(json.dumps({"corpus_root": str(CORPUS_ROOT), "bundles": rows}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_fp = sub.add_parser("fingerprint")
    sp_fp.add_argument("target")
    sp_fp.add_argument("--bundle", default=None,
                       help="restrict to one file (default: every distinct file)")

    sp_m = sub.add_parser("match")
    sp_m.add_argument("target")
    sp_m.add_argument("--threshold", type=float, default=0.3)
    sp_m.add_argument("--top", type=int, default=10)

    sp_l = sub.add_parser("list")
    sp_l.add_argument("--target", default=None)

    args = ap.parse_args()
    if args.cmd == "fingerprint":
        return cmd_fingerprint(resolve_target_dir(args.target), args.bundle)
    if args.cmd == "match":
        return cmd_match(resolve_target_dir(args.target), args.threshold, args.top)
    if args.cmd == "list":
        return cmd_list(args.target)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
