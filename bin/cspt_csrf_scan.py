#!/usr/bin/env python3
"""CSPT-2-CSRF candidate scan (T2.2).

Scan ``chains/dom_reachable.jsonl`` (fallback ``chains/hot.jsonl``) for
chains where the sink belongs to the CSPT family (URL-construction sites
in fetch/XHR/axios with interpolation), AND the chain involves a
path-traversal marker. Produces a candidate list per Doyensec's
CSPT2CSRF playbook — flag every cookie-authed mutation endpoint as a
CSRF candidate for live confirmation.

Heuristic — a chain is a CSPT-CSRF candidate iff:
  - sink.taxonomy_id starts with ``cspt_`` (defined in
    ``taxonomies/extra_cspt.json``), OR
  - sink.taxonomy_id ∈ {fetch_url, xhr_url, axios_url} AND chain has a
    `cspt_path_traversal_marker` tag on any path node.

Mutating verbs (POST/PUT/PATCH/DELETE) are the higher-severity
subset — surface those first.

Usage:
  bin/cspt_csrf_scan.py <target_dir>
      [--input chains/...jsonl]   # default: dom_reachable then hot
      [--db <per-target.db>]

Output:
    targets/<name>/chains/cspt_csrf.jsonl
    status.json.phases.cspt_csrf
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
    pick_chain_input,
    resolve_target_dir,
    utcnow,
    write_status_phase,
)


CSPT_FAMILY_PREFIXES = ("cspt_",)
CSPT_FAMILY_TAXONOMIES = {
    "fetch_url",
    "xhr_url",
    "axios_url",
    "request_url",
}
MUTATING_HINT_KEYWORDS = (
    "post",
    "put",
    "patch",
    "delete",
    "create",
    "update",
    "remove",
)


def is_cspt_sink(taxonomy_id: str) -> bool:
    if not taxonomy_id:
        return False
    if any(taxonomy_id.startswith(p) for p in CSPT_FAMILY_PREFIXES):
        return True
    return taxonomy_id in CSPT_FAMILY_TAXONOMIES


def has_pathtrav_tag(conn: sqlite3.Connection, qnames: list[str]) -> bool:
    if not qnames:
        return False
    qmarks = ",".join("?" * len(qnames))
    row = conn.execute(
        f"""
        SELECT COUNT(*) FROM node_tags t
        JOIN nodes n ON n.id = t.node_id
        WHERE n.qualified_name IN ({qmarks})
          AND t.taxonomy_id IN ('cspt_path_traversal_marker', 'path_traversal')
        """,
        qnames,
    ).fetchone()
    return (row[0] if row else 0) > 0


def looks_mutating(chain: dict) -> bool:
    sink = chain.get("sink", {}) or {}
    sname = (sink.get("qname") or "").lower()
    stax = (sink.get("taxonomy_id") or "").lower()
    blob = sname + " " + stax
    return any(k in blob for k in MUTATING_HINT_KEYWORDS)


def build_candidate(chain: dict, *, has_pathtrav: bool) -> dict:
    sink = chain.get("sink", {}) or {}
    severity = "high" if looks_mutating(chain) else "medium"
    if has_pathtrav and severity == "high":
        severity = "critical"
    return {
        "chain_id": chain.get("id"),
        "kind": "cspt_csrf_candidate",
        "severity": severity,
        "sink": {
            "qname": sink.get("qname"),
            "file": sink.get("file"),
            "line": sink.get("line"),
            "taxonomy_id": sink.get("taxonomy_id"),
        },
        "source": chain.get("source"),
        "path": chain.get("path"),
        "mutating_verb_hint": looks_mutating(chain),
        "has_path_traversal_marker": has_pathtrav,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target_dir")
    ap.add_argument("--input", default=None)
    ap.add_argument("--db", default=None)
    args = ap.parse_args()

    try:
        target = resolve_target_dir(args.target_dir)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    input_path = pick_chain_input(target, args.input)
    if input_path is None:
        skipped = {
            "status": "skipped",
            "ts": utcnow(),
            "reason": "no input chains file (need chains/dom_reachable.jsonl or chains/hot.jsonl)",
        }
        write_status_phase(target, "cspt_csrf", skipped)
        print(json.dumps(skipped, indent=2))
        return 0

    db_path = Path(args.db) if args.db else per_target_db(target)
    if not db_path.exists():
        print(
            f"[warn] per-target DB missing ({db_path}); path-traversal "
            "tagging disabled, severity capped at high",
            file=sys.stderr,
        )
    conn = sqlite3.connect(str(db_path)) if db_path.exists() else None

    candidates: list[dict] = []
    total = 0
    matched_sink = 0
    matched_with_pathtrav = 0

    try:
        with input_path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    chain = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                sink_tax = (chain.get("sink") or {}).get("taxonomy_id") or ""
                if not is_cspt_sink(sink_tax):
                    continue
                matched_sink += 1
                has_pt = (
                    has_pathtrav_tag(conn, chain.get("path") or [])
                    if conn is not None
                    else False
                )
                if has_pt:
                    matched_with_pathtrav += 1
                candidates.append(build_candidate(chain, has_pathtrav=has_pt))
    finally:
        if conn is not None:
            conn.close()

    candidates.sort(
        key=lambda c: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(c["severity"], 9),
            -int(bool(c["has_path_traversal_marker"])),
        )
    )

    out_dir = target / "chains"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "cspt_csrf.jsonl"
    with out_file.open("w") as f:
        for c in candidates:
            f.write(json.dumps(c) + "\n")

    result = {
        "status": "done",
        "ts": utcnow(),
        "input": str(input_path.relative_to(target)),
        "chains_scanned": total,
        "matched_cspt_sink": matched_sink,
        "with_path_traversal_marker": matched_with_pathtrav,
        "candidates_written": len(candidates),
        "output_file": str(out_file.relative_to(target)),
    }
    write_status_phase(target, "cspt_csrf", result)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
