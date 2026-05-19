#!/usr/bin/env python3
"""Sanitizer-on-path CFG-dominance check for extracted taint chains.

Phase 2 of project_implicit_tags_plan.md. Targets the audited→confirmed
FP-rate problem (coralbug3-syn: 4/4 audited chains were FP).

For each chain in ``chains/all.jsonl`` (or ``--input``), walk the
``path`` qnames and query ``node_sanitizers`` for each function. If any
sanitizer's ``clears`` category matches the chain's sink taxonomy
category (or is ``any``), mark the chain as sanitized.

The full CFG-dominance variant ("sanitizer must lie between the source
read and the sink call on every control-flow path") would require AST
basic-block info we don't persist. The coarse-but-cheap proxy here is:

    sanitizer-line < next-call-line

i.e. the sanitizer executes BEFORE the value is forwarded. This catches
most defensive patterns (early return, throw, escape-and-reassign)
without requiring CFG block reconstruction.

Outputs (under ``targets/<name>/chains/``):
    sanitized.jsonl    — chains with at least one valid sanitizer on path
    clean.jsonl        — chains with NO sanitizer on path (the queue for
                         further auditing)
    all.jsonl          — rewritten in place with chain.sanitized +
                         chain.sanitizer_evidence fields
    triage_sanitizer.json — sanitizer hit-rate breakdown

Idempotent: re-running overwrites the *.jsonl files atomically.

Per CLAUDE.md API-key whitelist: no LLM calls.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    per_target_db,
    resolve_target_dir,
    utcnow,
    write_status_phase,
)


# Map sink/source taxonomy_id → category. Categories match the strings
# in sanitizers.json `clears` arrays. A sanitizer that clears any of the
# chain's endpoint categories (or `any`) defuses the chain.
_HTML_SINKS = frozenset({
    "innerHTML_assign", "outerHTML_assign", "insertAdjacentHTML_call",
    "document_write", "document_writeln", "srcdoc_assign",
    "dangerouslySetInnerHTML", "jquery_html", "vue_v_html_sink",
    "angular_inner_html_binding", "angular_bypass_trust_html",
    "pp_gadget_innerHTML",
})

_ATTR_SINKS = frozenset({
    "setAttribute_dangerous_attr", "setAttribute_dynamic_attr",
    "event_handler_attr_assign",
})

_URL_SINKS = frozenset({
    "location_href_assign", "location_assign_call", "location_replace_call",
    "fetch_call", "xhr_open_call", "axios_call",
    "electron_shell_openexternal", "anchor_href_assign",
})

_JS_SINKS = frozenset({
    "eval_call", "eval_indirect", "new_Function",
    "setTimeout_string", "setInterval_string", "setImmediate_string",
    "pp_gadget_setTimeout",
})


def _sink_categories(tax_id: str) -> set[str]:
    cats: set[str] = set()
    if tax_id in _HTML_SINKS:
        cats.add("html")
    if tax_id in _ATTR_SINKS:
        cats.add("attribute")
    if tax_id in _URL_SINKS:
        cats.add("url")
    if tax_id in _JS_SINKS:
        cats.add("js")
    return cats


def _parse_clears(clears_blob: str | None) -> set[str]:
    if not clears_blob:
        return set()
    return {c.strip() for c in clears_blob.split(",") if c.strip()}


_SANITIZER_JSON = (
    Path(__file__).resolve().parent.parent
    / "tlx" / "modules" / "js_analyzer" / "taxonomies" / "sanitizers.json"
)


def _load_canonical_clears() -> dict[str, set[str]]:
    """Load the ground-truth `clears` set per sanitizer id from the JSON
    taxonomy. Used to override stale `clears=any` rows in older snapshot
    DBs — e.g. sanitizer_Number_coerce was once `any` but is now
    `numeric`-only. Reading from JSON keeps the DB rewrites unnecessary
    while still defusing the over-defuse pattern.
    """
    out: dict[str, set[str]] = {}
    if not _SANITIZER_JSON.exists():
        return out
    try:
        rows = json.loads(_SANITIZER_JSON.read_text())
    except (json.JSONDecodeError, OSError):
        return out
    for r in rows:
        sid = r.get("id")
        clears = r.get("clears")
        if not sid or not isinstance(clears, list):
            continue
        out[sid] = {str(c) for c in clears}
    return out


def _load_sanitizers_by_qname(
    conn: sqlite3.Connection,
) -> dict[str, list[dict]]:
    """qname → list of sanitizer records {taxonomy_id, line, clears (set)}.

    Stale snapshot DBs may carry `clears=any` for sanitizers whose JSON
    taxonomy has been narrowed (e.g. Number_coerce, parseInt_parseFloat
    now only clear `numeric`). Override the DB value with the canonical
    JSON value when known — same effect as re-indexing, no schema
    churn. Tracked via _clears_override_counts for triage_sanitizer.json.
    """
    canonical = _load_canonical_clears()
    out: dict[str, list[dict]] = {}
    overrides: Counter[str] = Counter()
    rows = conn.execute(
        "SELECT n.qualified_name, ns.taxonomy_id, ns.line, ns.clears "
        "FROM node_sanitizers ns JOIN nodes n ON n.id = ns.node_id"
    ).fetchall()
    for qname, tax_id, line, clears in rows:
        db_clears = _parse_clears(clears)
        canon = canonical.get(tax_id)
        if canon is not None and canon != db_clears:
            db_clears = canon
            overrides[tax_id] += 1
        out.setdefault(qname, []).append({
            "taxonomy_id": tax_id,
            "line": int(line) if line is not None else 0,
            "clears": db_clears,
        })
    if overrides:
        print(f"sanitizer_clears_overrides={dict(overrides)}", file=sys.stderr)
    return out


def _load_call_lines(conn: sqlite3.Connection) -> dict[str, list[int]]:
    """qname → sorted list of call-out edge line numbers."""
    out: dict[str, list[int]] = {}
    rows = conn.execute(
        "SELECT n.qualified_name, e.line "
        "FROM edges e JOIN nodes n ON n.id = e.caller_id"
    ).fetchall()
    for qname, line in rows:
        if line is None:
            continue
        out.setdefault(qname, []).append(int(line))
    for k in out:
        out[k].sort()
    return out


def _next_call_line_after(qname: str, after_line: int,
                          call_lines_by_qname: dict[str, list[int]]) -> int | None:
    """Smallest call-out line in qname strictly greater than after_line."""
    lines = call_lines_by_qname.get(qname)
    if not lines:
        return None
    for ln in lines:
        if ln > after_line:
            return ln
    return None


def _evaluate_chain(
    chain: dict,
    sanitizers_by_qname: dict[str, list[dict]],
    call_lines_by_qname: dict[str, list[int]],
    strict_dominance: bool,
) -> dict | None:
    """Return sanitizer_evidence dict if chain is sanitized; else None.

    With strict_dominance=True a sanitizer only counts when its line
    precedes the next call-out on the same function (proxy for CFG
    dominance over the forwarding call).
    """
    sink_tax = (chain.get("sink") or {}).get("taxonomy_id", "")
    src_tax = (chain.get("source") or {}).get("taxonomy_id", "")
    target_cats = _sink_categories(sink_tax)
    # Source-side sanitizers (e.g. url-encoded location.search) also count
    # since the value is escaped before flowing further.
    target_cats |= _sink_categories(src_tax)
    if not target_cats:
        # Unknown taxonomy → only `any` sanitizers can defuse it.
        target_cats = set()

    path = chain.get("path") or []
    if not path:
        return None

    # On the LAST node (sink fn), don't require dominance over a next-call:
    # if sanitizer fires anywhere in the sink function we accept it.
    for idx, qname in enumerate(path):
        records = sanitizers_by_qname.get(qname)
        if not records:
            continue
        is_terminal = idx == len(path) - 1
        for r in records:
            r_cats = r["clears"]
            if not (r_cats & target_cats or "any" in r_cats):
                continue
            if not is_terminal and strict_dominance:
                # Sanitizer must run before the next call-out on this fn.
                next_call = _next_call_line_after(
                    qname, 0, call_lines_by_qname
                )
                if next_call is None or r["line"] >= next_call:
                    continue
            return {
                "sanitizer_id": r["taxonomy_id"],
                "qname": qname,
                "line": r["line"],
                "clears": sorted(r_cats),
                "matched_categories": sorted(r_cats & (target_cats | {"any"})),
                "path_index": idx,
                "strict_dominance": strict_dominance and not is_terminal,
            }
    return None


def annotate_chains(
    chains: list[dict],
    sanitizers_by_qname: dict[str, list[dict]],
    call_lines_by_qname: dict[str, list[int]],
    strict_dominance: bool,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (annotated_chains, sanitized_only, clean_only)."""
    annotated: list[dict] = []
    sanitized: list[dict] = []
    clean: list[dict] = []
    for chain in chains:
        ev = _evaluate_chain(chain, sanitizers_by_qname,
                             call_lines_by_qname, strict_dominance)
        out = dict(chain)
        if ev is None:
            out["sanitized"] = False
            clean.append(out)
        else:
            out["sanitized"] = True
            out["sanitizer_evidence"] = ev
            sanitized.append(out)
        annotated.append(out)
    return annotated, sanitized, clean


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    with tmp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    tmp.replace(path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("--db", default=None)
    ap.add_argument("--input", default=None,
                    help="Chain JSONL (default: chains/all.jsonl)")
    ap.add_argument(
        "--strict-dominance",
        dest="strict_dominance",
        action="store_true",
        default=True,
        help="Require sanitizer.line < next call-out line on the same fn. "
             "Default ON (FP-rate reduction). Use --coarse to revert.",
    )
    ap.add_argument(
        "--coarse",
        dest="strict_dominance",
        action="store_false",
        help="Coarse mode: sanitizer anywhere in fn counts. Default was "
             "this until 2026-05-19; flipped to strict because Number_coerce "
             "+ parseInt_parseFloat (clears=any) over-defused.",
    )
    ap.add_argument("--no-rewrite-all", action="store_true",
                    help="Skip rewriting chains/all.jsonl in place.")
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    t0 = time.monotonic()
    try:
        target = resolve_target_dir(args.target)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    if not db_path.exists():
        print(f"error: per-target DB missing: {db_path}", file=sys.stderr)
        if not args.no_status:
            append_status_error(target, "sanitizer-on-path",
                                FileNotFoundError(str(db_path)))
        return 2

    input_path = Path(args.input).resolve() if args.input else \
        (target / "chains" / "all.jsonl")
    if not input_path.exists():
        print(f"error: chains input missing: {input_path}", file=sys.stderr)
        return 2

    chains = [json.loads(line) for line in input_path.open() if line.strip()]
    if not chains:
        print("warn: no chains to evaluate", file=sys.stderr)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        sanitizers_by_qname = _load_sanitizers_by_qname(conn)
        call_lines_by_qname = _load_call_lines(conn) if args.strict_dominance \
            else {}
    finally:
        conn.close()

    annotated, sanitized, clean = annotate_chains(
        chains, sanitizers_by_qname, call_lines_by_qname,
        args.strict_dominance,
    )

    chains_dir = target / "chains"
    _write_jsonl(chains_dir / "sanitized.jsonl", sanitized)
    _write_jsonl(chains_dir / "clean.jsonl", clean)
    if not args.no_rewrite_all:
        _write_jsonl(input_path, annotated)

    sanitizer_dist = Counter(
        c["sanitizer_evidence"]["sanitizer_id"] for c in sanitized
    )
    sink_dist_sanitized = Counter(
        c["sink"]["taxonomy_id"] for c in sanitized
    )
    sink_dist_clean = Counter(
        c["sink"]["taxonomy_id"] for c in clean
    )
    triage = {
        "target": target.name,
        "input": str(input_path),
        "total_chains": len(annotated),
        "sanitized": len(sanitized),
        "clean": len(clean),
        "sanitized_pct": round(
            100.0 * len(sanitized) / max(1, len(annotated)), 1
        ),
        "strict_dominance": args.strict_dominance,
        "sanitizer_dist": dict(sanitizer_dist.most_common()),
        "sink_dist_sanitized": dict(sink_dist_sanitized.most_common(15)),
        "sink_dist_clean": dict(sink_dist_clean.most_common(15)),
        "elapsed_s": round(time.monotonic() - t0, 3),
    }
    (chains_dir / "triage_sanitizer.json").write_text(
        json.dumps(triage, indent=2)
    )
    print(json.dumps(triage, indent=2))

    if not args.no_status:
        write_status_phase(
            target,
            "sanitizer_on_path",
            {
                "status": "done",
                "ts": utcnow(),
                "total_chains": triage["total_chains"],
                "sanitized": triage["sanitized"],
                "clean": triage["clean"],
                "sanitized_pct": triage["sanitized_pct"],
                "strict_dominance": args.strict_dominance,
                "elapsed_s": triage["elapsed_s"],
            },
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
