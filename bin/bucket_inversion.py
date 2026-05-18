#!/usr/bin/env python3
"""Phase 5 of project_implicit_tags_plan.md: bucket-inversion sink/source seeder.

`bucket_anomaly.py` runs the *forward* direction: take chains, bucket
by sink file, ask a sub-agent to flag siblings that DON'T match the
guard pattern of the tagged ones. This script runs the *inverse*: when
N or more sibling functions (same file + same parent class) already
carry a tag for the same taxonomy, the remaining siblings are
probably also sinks/sources but were missed by regex + AST extraction.
Seed them as implicit-bucket tags with confidence 0.5.

Conservative thresholds:
* ``--min-siblings 3`` — need at least 3 tagged peers to infer the rest.
* Untagged sibling must share BOTH file AND parent class — no
  cross-class inference.
* Confidence ``0.5`` sits between implicit_naming (0.3-0.4) and
  implicit_closure-hop1 (0.7). It's a stronger signal than naming
  but weaker than callgraph closure because we have no syntactic
  evidence the sibling actually calls the dangerous primitive.

Idempotent: clears prior ``source = 'implicit_bucket'`` rows before
inserting. Per CLAUDE.md whitelist: no LLM calls.

Output: rows appended to ``targets/<name>/tags_discovered.jsonl`` +
``status.json.phases.bucket_inversion``.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    per_target_db,
    resolve_target_dir,
    utcnow,
    write_status_phase,
)


@dataclass
class BucketTag:
    node_id: int
    qname: str
    file: str
    line: int
    taxonomy_id: str
    kind: str
    severity: str
    source: str = "implicit_bucket"
    confidence: float = 0.5
    evidence: dict = field(default_factory=dict)


def _load_sibling_groups(
    conn: sqlite3.Connection,
) -> dict[tuple[str, str], list[dict]]:
    """Return {(file, parent) -> [node_records]}.

    Excludes nodes with NULL/empty parent — those are file-level
    functions where 'sibling' has no meaning beyond "same file",
    which is too coarse for tag inference.
    """
    out: dict[tuple[str, str], list[dict]] = {}
    rows = conn.execute(
        "SELECT id, qualified_name, file, name, parent, kind, start_line "
        "FROM nodes "
        "WHERE kind IN ('function','arrow','method') "
        "AND parent IS NOT NULL AND parent != ''"
    ).fetchall()
    for nid, qname, file, name, parent, kind, start_line in rows:
        key = (file or "", parent or "")
        out.setdefault(key, []).append({
            "id": nid,
            "qname": qname,
            "file": file or "",
            "name": name or "",
            "parent": parent or "",
            "kind": kind,
            "start_line": int(start_line) if start_line is not None else 0,
        })
    return out


def _load_tagged_by_node(
    conn: sqlite3.Connection,
    direct_only: bool,
) -> dict[int, list[dict]]:
    """node_id → list of {taxonomy_id, kind, severity, confidence}."""
    where = ""
    if direct_only:
        where = "WHERE source NOT LIKE 'implicit_%'"
    rows = conn.execute(
        f"SELECT node_id, taxonomy_id, kind, severity, confidence "
        f"FROM node_tags {where}"
    ).fetchall()
    out: dict[int, list[dict]] = {}
    for nid, tid, kind, sev, conf in rows:
        out.setdefault(nid, []).append({
            "taxonomy_id": tid,
            "kind": kind,
            "severity": sev,
            "confidence": float(conf) if conf is not None else 1.0,
        })
    return out


def discover(
    conn: sqlite3.Connection,
    *,
    min_siblings: int = 3,
    confidence: float = 0.5,
    direct_only: bool = True,
) -> list[BucketTag]:
    """For every (file, parent) group, find taxonomies tagged on
    ``min_siblings`` or more group members; seed the untagged members
    as derived tags.

    ``direct_only=True`` (default): only direct (non-implicit) tags
    count toward the sibling-density threshold. Prevents feedback
    loops where implicit-closure tags seed more implicit tags.
    """
    groups = _load_sibling_groups(conn)
    density_tagged = _load_tagged_by_node(conn, direct_only=direct_only)
    # ALL tags — used for dedup so we don't emit implicit_bucket for a
    # node that already carries the same taxonomy via any other source
    # (regex, ast, implicit_naming, implicit_closure, …).
    all_tagged = _load_tagged_by_node(conn, direct_only=False)

    out: list[BucketTag] = []
    for (file, parent), members in groups.items():
        if len(members) < min_siblings + 1:
            # Need at least min_siblings tagged + 1 untagged candidate.
            continue
        # taxonomy_id → set of member node_ids carrying that tag (per
        # the density filter)
        tag_density: dict[str, dict[str, set[int] | str]] = {}
        for m in members:
            for t in density_tagged.get(m["id"], ()):
                key = t["taxonomy_id"]
                rec = tag_density.setdefault(key, {
                    "nodes": set(),
                    "kind": t["kind"],
                    "severity": t["severity"],
                })
                rec["nodes"].add(m["id"])
        for tax_id, rec in tag_density.items():
            tagged_nodes: set[int] = rec["nodes"]
            if len(tagged_nodes) < min_siblings:
                continue
            for m in members:
                if m["id"] in tagged_nodes:
                    continue
                # Dedup against ALL tag sources, not just direct.
                if any(t["taxonomy_id"] == tax_id
                       for t in all_tagged.get(m["id"], ())):
                    continue
                out.append(BucketTag(
                    node_id=m["id"],
                    qname=m["qname"],
                    file=m["file"],
                    line=m["start_line"],
                    taxonomy_id=tax_id,
                    kind=str(rec["kind"]),
                    severity=str(rec["severity"]),
                    confidence=round(confidence, 4),
                    evidence={
                        "rule": "sibling_density",
                        "file": file,
                        "parent": parent,
                        "tagged_siblings": len(tagged_nodes),
                        "total_siblings": len(members),
                    },
                ))
    return out


def persist(
    conn: sqlite3.Connection,
    tags: list[BucketTag],
    *,
    clear_existing: bool = True,
) -> dict:
    stats = {"cleared": 0, "inserted": 0, "duplicate": 0}
    cur = conn.cursor()
    if clear_existing:
        before = conn.total_changes
        cur.execute(
            "DELETE FROM node_tags WHERE source = 'implicit_bucket'"
        )
        stats["cleared"] = conn.total_changes - before
    for t in tags:
        evidence_json = json.dumps(t.evidence, separators=(",", ":"))
        before = conn.total_changes
        cur.execute(
            "INSERT OR IGNORE INTO node_tags "
            "(node_id, taxonomy_id, kind, severity, line, source, "
            " confidence, evidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (t.node_id, t.taxonomy_id, t.kind, t.severity, t.line,
             t.source, t.confidence, evidence_json),
        )
        if conn.total_changes > before:
            stats["inserted"] += 1
        else:
            stats["duplicate"] += 1
    conn.commit()
    return stats


def _append_jsonl(out_path: Path, tags: list[BucketTag]) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("a", encoding="utf-8") as f:
        for t in tags:
            f.write(json.dumps(asdict(t), separators=(",", ":")) + "\n")
            n += 1
    return n


def _migrate(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    if "confidence" not in cols:
        conn.execute(
            "ALTER TABLE node_tags ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0"
        )
    if "evidence" not in cols:
        conn.execute("ALTER TABLE node_tags ADD COLUMN evidence TEXT")
    if "source" not in cols:
        conn.execute(
            "ALTER TABLE node_tags ADD COLUMN source TEXT NOT NULL DEFAULT 'regex'"
        )
    conn.commit()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--min-siblings", type=int, default=3)
    ap.add_argument("--confidence", type=float, default=0.5)
    ap.add_argument(
        "--count-implicit-siblings",
        action="store_true",
        help="Allow implicit (closure/naming/bucket) tags to count "
             "toward sibling density. Default is direct-only.",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Compute + print stats; skip JSONL append + DB insert.",
    )
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db_path.exists():
        print(f"error: per-target DB missing: {db_path}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "bucket-inversion",
                                FileNotFoundError(str(db_path)))
        return 2

    t0 = time.monotonic()
    conn = sqlite3.connect(str(db_path))
    try:
        _migrate(conn)
        tags = discover(
            conn,
            min_siblings=args.min_siblings,
            confidence=args.confidence,
            direct_only=not args.count_implicit_siblings,
        )

        by_kind = {"sink": 0, "source": 0}
        by_tax: dict[str, int] = {}
        for t in tags:
            by_kind[t.kind] = by_kind.get(t.kind, 0) + 1
            by_tax[t.taxonomy_id] = by_tax.get(t.taxonomy_id, 0) + 1

        persist_stats = {"cleared": 0, "inserted": 0, "duplicate": 0}
        appended = 0
        jsonl_path = target / "tags_discovered.jsonl"
        if not args.dry_run:
            persist_stats = persist(conn, tags, clear_existing=True)
            appended = _append_jsonl(jsonl_path, tags)

        elapsed_s = round(time.monotonic() - t0, 3)
        summary = {
            "target": target.name,
            "db": str(db_path),
            "min_siblings": args.min_siblings,
            "confidence": args.confidence,
            "direct_only": not args.count_implicit_siblings,
            "discovered": len(tags),
            "by_kind": by_kind,
            "by_taxonomy_top": dict(
                sorted(by_tax.items(), key=lambda kv: -kv[1])[:15]
            ),
            "persist": persist_stats,
            "jsonl_path": str(jsonl_path),
            "jsonl_appended": appended,
            "dry_run": bool(args.dry_run),
            "elapsed_s": elapsed_s,
        }
        print(json.dumps(summary, indent=2))

        if not args.no_status and not args.dry_run:
            write_status_phase(
                target,
                "bucket_inversion",
                {
                    "status": "done",
                    "ts": utcnow(),
                    "discovered": len(tags),
                    "by_kind": by_kind,
                    "by_taxonomy_top": summary["by_taxonomy_top"],
                    "inserted": persist_stats["inserted"],
                    "cleared": persist_stats["cleared"],
                    "min_siblings": args.min_siblings,
                    "confidence": args.confidence,
                    "elapsed_s": elapsed_s,
                },
            )
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
