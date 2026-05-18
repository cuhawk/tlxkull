#!/usr/bin/env python3
"""Phase 0 of cc-taint-adversarial: expand a chain into a rich snippet bundle.

Given a per-target chain (source fn + sink fn + path), reads the per-target
``js_analyzer.db`` and ``sources/`` tree to produce a JSON evidence bundle
containing:

* source and sink function bodies (full-fidelity if budget allows)
* callers up to N hops above the sink fn
* dominator guards detected above the sink line (if / try / role-check calls)
* framework lifecycle context (React useEffect, Vue setup, Angular handler, ...)

Output: ``targets/<name>/chains/expanded/<chain_id>.json``.

Per CLAUDE.md per-target-DB isolation: ``--db`` is explicit, no fallback to
``~/.tlx/``. Default is the per-target snapshot path.

Usage:
    python3 bin/expand_snippet.py --target <name> --chain-id <id>
    python3 bin/expand_snippet.py --target <name> --all
    cat chain.json | python3 bin/expand_snippet.py --target <name> --stdin
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    append_status_error,
    per_target_db,
    pick_chain_input,
    resolve_target_dir,
    write_status_phase,
    utcnow,
)

DEFAULT_BYTE_BUDGET = 12000
DEFAULT_MAX_HOPS = 2

_GUARD_PATTERNS = [
    ("if",      re.compile(r"^\s*(?:\}\s*else\s*)?if\s*\(")),
    ("else_if", re.compile(r"^\s*\}?\s*else\s+if\s*\(")),
    ("try",     re.compile(r"^\s*try\s*\{")),
    ("catch",   re.compile(r"^\s*\}\s*catch\b")),
    ("ternary", re.compile(r"\?[^:]+:")),
    ("guard_clause", re.compile(r"^\s*(?:return|throw)\s+")),
    ("fn_call", re.compile(
        r"\b("
        r"isSafe|isValid|isAllowed|isTrusted|isAuthenticated|isAuthorized|"
        r"can[A-Z]\w*|has[A-Z]\w*|check[A-Z]\w*|verify[A-Z]\w*|"
        r"require[A-Z]\w*|assert[A-Z]\w*|"
        r"sanitize|escape|encodeURI|encodeURIComponent|DOMPurify"
        r")\s*\(",
    )),
]

_FRAMEWORK_PATTERNS = [
    ("react",   "useEffect",        re.compile(r"\buseEffect\s*\(")),
    ("react",   "useMemo",          re.compile(r"\buseMemo\s*\(")),
    ("react",   "useCallback",      re.compile(r"\buseCallback\s*\(")),
    ("react",   "useState",         re.compile(r"\buseState\s*\(")),
    ("react",   "event_handler",    re.compile(r"\bon[A-Z]\w*\s*=")),
    ("react",   "dangerouslySetInnerHTML", re.compile(r"dangerouslySetInnerHTML")),
    ("vue",     "setup",            re.compile(r"\bsetup\s*\(")),
    ("vue",     "v-html",           re.compile(r"v-html=")),
    ("angular", "ngOnInit",         re.compile(r"\bngOnInit\s*\(")),
    ("angular", "inner_html_bind",  re.compile(r"\[innerHTML\]=")),
    ("angular", "bypass_security",  re.compile(r"bypassSecurityTrust\w+\s*\(")),
    ("svelte",  "onMount",          re.compile(r"\bonMount\s*\(")),
    ("next",    "getServerSideProps", re.compile(r"\bgetServerSideProps\s*\(")),
    ("dom",     "addEventListener", re.compile(r"\.addEventListener\s*\(")),
    ("dom",     "postMessage",      re.compile(r"\.postMessage\s*\(")),
    ("dom",     "onmessage",        re.compile(r"\bonmessage\s*=")),
    ("dom",     "window_onload",    re.compile(r"\bwindow\.onload\s*=")),
    ("rxjs",    "subscribe",        re.compile(r"\.subscribe\s*\(")),
]


@dataclass
class NodeRecord:
    id: int
    qname: str
    file: str
    name: str
    kind: str
    start_line: int
    end_line: int
    code: str = ""
    hop: int = 0


@dataclass
class Snippet:
    chain_id: int | str
    source: dict
    sink: dict
    callers: list[dict] = field(default_factory=list)
    dominator_guards: list[dict] = field(default_factory=list)
    framework_context: dict | None = None
    byte_budget: int = DEFAULT_BYTE_BUDGET
    truncated: bool = False
    notes: list[str] = field(default_factory=list)


def _connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _node_by_qname(conn: sqlite3.Connection, qname: str) -> NodeRecord | None:
    row = conn.execute(
        "SELECT id, qualified_name AS qname, file, name, kind, start_line, end_line"
        " FROM nodes WHERE qualified_name = ?",
        (qname,),
    ).fetchone()
    if not row:
        return None
    return NodeRecord(**dict(row))


def _read_lines(sources_dir: Path, file_rel: str, start: int, end: int) -> str:
    p = sources_dir / file_rel
    if not p.exists():
        return ""
    if start <= 0 or end <= 0 or end < start:
        return ""
    try:
        with p.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return ""
    # 1-indexed inclusive
    chunk = lines[max(0, start - 1) : end]
    return "".join(chunk).rstrip("\n")


def _summarize_body(code: str, head_lines: int = 5) -> str:
    lines = code.splitlines()
    if len(lines) <= head_lines + 2:
        return code
    head = "\n".join(lines[:head_lines])
    return f"{head}\n  // ... ({len(lines) - head_lines} more lines elided)"


_MAX_LINE_LEN_FOR_REGEX = 50_000


def _detect_guards(code: str, sink_line: int, fn_start: int) -> list[dict]:
    """Walk code lines above the sink and emit guard records.

    ``code`` is the body string (starting at ``fn_start``); ``sink_line`` is
    the 1-indexed absolute line of the sink. A guard is emitted only if the
    line is at or above the sink.

    Lines longer than ``_MAX_LINE_LEN_FOR_REGEX`` are skipped from regex
    scanning to avoid catastrophic backtracking on minified single-line
    bundles (Patch — coolblue expand_snippet hang at 100% CPU for 5+ min
    on 600KB lines). Guard detection on a 50KB+ line is unreliable anyway
    because true line breaks are absent.
    """
    out: list[dict] = []
    if not code:
        return out
    for offset, raw in enumerate(code.splitlines()):
        abs_line = fn_start + offset
        if abs_line >= sink_line + 1:
            break
        stripped = raw.strip()
        if not stripped:
            continue
        if len(stripped) > _MAX_LINE_LEN_FOR_REGEX:
            continue
        for kind, pat in _GUARD_PATTERNS:
            if pat.search(stripped):
                out.append(
                    {
                        "kind": kind,
                        "line": abs_line,
                        "expr": stripped[:160],
                        "covers_sink": True,
                    }
                )
                break
    return out


def _detect_framework(code: str) -> dict | None:
    if not code:
        return None
    # Cap framework regex against the same minified-line problem as
    # _detect_guards. A 600KB single-line bundle is unparseable for
    # line-by-line framework lifecycle detection — skip it.
    if any(len(l) > _MAX_LINE_LEN_FOR_REGEX for l in code.splitlines()):
        return None
    for framework, lifecycle, pat in _FRAMEWORK_PATTERNS:
        if pat.search(code):
            return {"framework": framework, "lifecycle": lifecycle}
    return None


def _walk_callers(
    conn: sqlite3.Connection, sink_id: int, path_qnames: list[str], max_hops: int
) -> list[NodeRecord]:
    """Return caller nodes up to ``max_hops`` upstream of the sink.

    Prefers the explicit chain ``path_qnames`` (skipping the sink itself),
    then augments with any direct callers from the ``edges`` table that the
    chain path doesn't already include.
    """
    seen_ids: set[int] = set()
    out: list[NodeRecord] = []

    explicit = [q for q in path_qnames if q]
    for hop, q in enumerate(reversed(explicit[:-1] if explicit else []), start=1):
        if hop > max_hops:
            break
        node = _node_by_qname(conn, q)
        if node and node.id not in seen_ids:
            node.hop = hop
            seen_ids.add(node.id)
            out.append(node)

    current_ids = {sink_id} | seen_ids
    for hop in range(1, max_hops + 1):
        rows = conn.execute(
            f"SELECT DISTINCT caller_id FROM edges WHERE callee_id IN ("
            f"{','.join('?' for _ in current_ids)}) AND caller_id IS NOT NULL",
            tuple(current_ids),
        ).fetchall()
        next_ids: set[int] = set()
        for r in rows:
            cid = r["caller_id"]
            if cid in seen_ids or cid == sink_id:
                continue
            row = conn.execute(
                "SELECT id, qualified_name AS qname, file, name, kind,"
                " start_line, end_line FROM nodes WHERE id = ?",
                (cid,),
            ).fetchone()
            if not row:
                continue
            node = NodeRecord(**dict(row), hop=hop)
            seen_ids.add(cid)
            next_ids.add(cid)
            out.append(node)
        if not next_ids:
            break
        current_ids = next_ids
    return out


def _node_payload(node: NodeRecord) -> dict:
    return {
        "qname": node.qname,
        "file": node.file,
        "lines": [node.start_line, node.end_line],
        "code": node.code,
        **({"hop": node.hop} if node.hop else {}),
        "kind": node.kind,
        "name": node.name,
    }


def _apply_budget(snippet: Snippet) -> None:
    """If serialised size exceeds the budget, elide caller bodies first."""
    total = len(json.dumps(asdict(snippet)))
    if total <= snippet.byte_budget:
        return
    snippet.truncated = True
    snippet.notes.append(
        f"serialized size {total}B exceeded byte_budget {snippet.byte_budget}B;"
        " caller bodies summarised"
    )
    for caller in snippet.callers:
        caller["code"] = _summarize_body(caller.get("code", ""))
    total = len(json.dumps(asdict(snippet)))
    if total <= snippet.byte_budget:
        return
    # Still over: trim the caller list from the deepest hops first.
    snippet.callers.sort(key=lambda c: -c.get("hop", 0))
    while snippet.callers and len(json.dumps(asdict(snippet))) > snippet.byte_budget:
        dropped = snippet.callers.pop(0)
        snippet.notes.append(f"dropped caller {dropped.get('qname')} (hop {dropped.get('hop')})")


def expand_chain(
    chain: dict,
    conn: sqlite3.Connection,
    sources_dir: Path,
    *,
    byte_budget: int = DEFAULT_BYTE_BUDGET,
    max_hops: int = DEFAULT_MAX_HOPS,
) -> Snippet:
    chain_id = chain.get("id") or chain.get("chain_id")
    src = chain.get("source") or {}
    sink = chain.get("sink") or {}
    path_qnames = chain.get("path") or []

    src_qname = src.get("qname")
    sink_qname = sink.get("qname")
    if not src_qname or not sink_qname:
        raise ValueError(f"chain {chain_id} missing source.qname or sink.qname")

    src_node = _node_by_qname(conn, src_qname)
    sink_node = _node_by_qname(conn, sink_qname)
    if not src_node:
        raise LookupError(f"source qname not found in DB: {src_qname}")
    if not sink_node:
        raise LookupError(f"sink qname not found in DB: {sink_qname}")

    src_node.code = _read_lines(sources_dir, src_node.file, src_node.start_line, src_node.end_line)
    sink_node.code = _read_lines(
        sources_dir, sink_node.file, sink_node.start_line, sink_node.end_line
    )

    callers = _walk_callers(conn, sink_node.id, path_qnames, max_hops)
    for c in callers:
        c.code = _read_lines(sources_dir, c.file, c.start_line, c.end_line)

    sink_abs_line = sink.get("line") or sink_node.start_line
    guards = _detect_guards(sink_node.code, sink_abs_line, sink_node.start_line)
    framework = _detect_framework(src_node.code) or _detect_framework(sink_node.code)

    snippet = Snippet(
        chain_id=chain_id,
        source=_node_payload(src_node),
        sink=_node_payload(sink_node),
        callers=[_node_payload(c) for c in callers],
        dominator_guards=guards,
        framework_context=framework,
        byte_budget=byte_budget,
    )
    _apply_budget(snippet)
    return snippet


def _iter_chains(input_path: Path) -> Iterable[dict]:
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _write_snippet(snippet: Snippet, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{snippet.chain_id}.json"
    out_path.write_text(json.dumps(asdict(snippet), indent=2))
    return out_path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Expand a taint chain into a snippet bundle.")
    ap.add_argument("--target", required=True, help="Target name or path under targets/")
    ap.add_argument("--db", help="Path to per-target js_analyzer.db (default: per-target snapshot)")
    ap.add_argument("--sources-dir", help="Override sources/ root (default: targets/<name>/sources)")
    ap.add_argument("--chains-input", help="Chain JSONL (default: dom_reachable.jsonl, fallback hot.jsonl)")
    ap.add_argument("--chain-id", help="Run on a single chain id from the input file")
    ap.add_argument("--all", action="store_true", help="Run on every chain in the input file")
    ap.add_argument("--stdin", action="store_true", help="Read a single chain JSON object on stdin")
    ap.add_argument("--byte-budget", type=int, default=DEFAULT_BYTE_BUDGET)
    ap.add_argument("--max-hops", type=int, default=DEFAULT_MAX_HOPS)
    ap.add_argument("--output-dir", help="Override output dir (default: targets/<name>/chains/expanded)")
    ap.add_argument("--no-status", action="store_true", help="Skip writing to status.json")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    target = resolve_target_dir(args.target)
    db_path = Path(args.db).resolve() if args.db else per_target_db(target)
    sources_dir = Path(args.sources_dir).resolve() if args.sources_dir else target / "sources"
    out_dir = Path(args.output_dir).resolve() if args.output_dir else target / "chains" / "expanded"

    try:
        conn = _connect(db_path)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    chains: list[dict] = []
    if args.stdin:
        chains = [json.loads(sys.stdin.read())]
    else:
        if args.chains_input:
            ci = Path(args.chains_input)
            input_path = ci.resolve() if ci.is_absolute() else (target / ci).resolve()
        else:
            input_path = pick_chain_input(target)
        if not input_path or not Path(input_path).exists():
            print("error: no chains input found (chains/dom_reachable.jsonl or chains/hot.jsonl)", file=sys.stderr)
            return 2
        all_chains = list(_iter_chains(Path(input_path)))
        if args.chain_id:
            wanted = str(args.chain_id)
            chains = [c for c in all_chains if str(c.get("id") or c.get("chain_id")) == wanted]
            if not chains:
                print(f"error: chain id {wanted} not found in {input_path}", file=sys.stderr)
                return 2
        elif args.all:
            chains = all_chains
        else:
            print("error: pass --chain-id, --all, or --stdin", file=sys.stderr)
            return 2

    written = 0
    errors: list[dict] = []
    for chain in chains:
        try:
            snippet = expand_chain(
                chain,
                conn,
                sources_dir,
                byte_budget=args.byte_budget,
                max_hops=args.max_hops,
            )
            path = _write_snippet(snippet, out_dir)
            written += 1
            if not args.all:
                print(path)
        except (LookupError, ValueError, sqlite3.DatabaseError) as e:
            cid = chain.get("id") or chain.get("chain_id")
            errors.append({"chain_id": cid, "error": str(e)})
            print(f"warn: chain {cid}: {e}", file=sys.stderr)

    conn.close()

    if not args.no_status:
        write_status_phase(
            target,
            "cc_taint_expand",
            {
                "status": "done" if not errors else "partial",
                "ts": utcnow(),
                "chains_expanded": written,
                "errors": errors[:20],
                "byte_budget": args.byte_budget,
                "max_hops": args.max_hops,
                "output_dir": str(out_dir.relative_to(target) if out_dir.is_relative_to(target) else out_dir),
            },
        )
        for err in errors:
            append_status_error(target, "cc-taint-expand", err.get("error", "unknown"), chain_id=err.get("chain_id"))

    if args.all:
        print(json.dumps({"chains_expanded": written, "errors": len(errors)}))
    return 0 if not errors or written else 1


if __name__ == "__main__":
    sys.exit(main())
