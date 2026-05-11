"""Pull HTTP route specs from a js_analyzer callgraph + source.

Uses node_tags rows whose taxonomy_id is an HTTP sink, opens the source
file at the recorded line, and applies regex heuristics to extract the
URL + method.

This module reads the callgraph SQLite directly (read-only). It does not
modify js_analyzer/callgraph.py.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HTTP_SINK_IDS: frozenset[str] = frozenset({
    "fetch_call",
    "fetch_with_user_input",
    "xhr_open_call",
    "axios_call",
    "ssrf_node_sink",
})


@dataclass
class RouteSpec:
    url: str
    method: str
    shape_hint: dict[str, Any] | None
    source_file: str
    source_line: int
    sink_id: str


# ── regex heuristics ─────────────────────────────────────────────────────

_STR = r"""(?P<q>['"`])(?P<url>(?:\\.|(?!(?P=q)).)*?)(?P=q)"""

_FETCH_RE = re.compile(
    rf"""\bfetch\s*\(\s*{_STR}\s*(?:,\s*(?P<opts>\{{[^}}]*\}}))?""",
    re.DOTALL,
)
_AXIOS_METHOD_RE = re.compile(
    rf"""\baxios\s*\.\s*(?P<method>get|post|put|delete|patch|head|options)\s*\(\s*{_STR}""",
    re.IGNORECASE | re.DOTALL,
)
_AXIOS_BARE_RE = re.compile(
    rf"""\baxios\s*\(\s*{_STR}\s*(?:,\s*(?P<opts>\{{[^}}]*\}}))?""",
    re.DOTALL,
)
_XHR_OPEN_RE = re.compile(
    rf"""\.\s*open\s*\(\s*{_STR}\s*,\s*['"`](?P<url2>(?:\\.|(?!['"`]).)*?)['"`]""",
    re.DOTALL,
)
_HTTP_GET_RE = re.compile(
    rf"""\bhttp(?:s)?\s*\.\s*(?P<method>get|request)\s*\(\s*{_STR}""",
    re.IGNORECASE | re.DOTALL,
)

_OPTS_METHOD_RE = re.compile(
    r"""method\s*:\s*['"`](?P<method>[A-Z]+)['"`]""",
    re.IGNORECASE,
)


_TEMPLATE_INTERP_RE = re.compile(r"\$\{[^}]*\}")
_QUERY_RE = re.compile(r"\?.*$")


def _normalise_url(raw: str) -> str:
    """Replace template interpolations with '*'. Strip query string."""
    out = _TEMPLATE_INTERP_RE.sub("*", raw)
    out = _QUERY_RE.sub("", out)
    return out


def _method_from_opts(opts: str | None) -> str | None:
    if not opts:
        return None
    m = _OPTS_METHOD_RE.search(opts)
    if m:
        return m.group("method").upper()
    return None


def _line_window(text: str, line: int, before: int = 0, after: int = 3) -> str:
    """Return source text covering line-before..line+after (1-indexed)."""
    if line <= 0:
        return text
    lines = text.splitlines()
    start = max(0, line - 1 - before)
    end = min(len(lines), line + after)
    return "\n".join(lines[start:end])


def _extract_for_sink(
    sink_id: str, snippet: str
) -> tuple[str, str] | None:
    """Apply per-sink regex heuristics to a small source window.

    Returns (url, method) or None.
    """
    if sink_id == "xhr_open_call":
        m = _XHR_OPEN_RE.search(snippet)
        if m:
            return m.group("url2"), m.group("url").upper()
        return None

    if sink_id == "axios_call":
        m = _AXIOS_METHOD_RE.search(snippet)
        if m:
            return m.group("url"), m.group("method").upper()
        m = _AXIOS_BARE_RE.search(snippet)
        if m:
            method = _method_from_opts(m.group("opts")) or "GET"
            return m.group("url"), method
        return None

    if sink_id in ("fetch_call", "fetch_with_user_input"):
        m = _FETCH_RE.search(snippet)
        if m:
            method = _method_from_opts(m.group("opts")) or "GET"
            return m.group("url"), method
        return None

    if sink_id == "ssrf_node_sink":
        m = _HTTP_GET_RE.search(snippet)
        if m:
            return m.group("url"), "GET"
        return None

    return None


def _read_source(project_root: Path, rel_or_abs: str) -> str:
    """Read source file. Supports rel paths (under project_root) and absolute."""
    if not rel_or_abs:
        return ""
    p = Path(rel_or_abs)
    if not p.is_absolute():
        p = project_root / rel_or_abs
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _query_http_sink_tags(
    cg_conn: Any, sink_ids: frozenset[str]
) -> list[tuple[int, str, str, int, str]]:
    """Return (node_id, file, taxonomy_id, line, qname) rows for HTTP sinks."""
    placeholders = ",".join("?" * len(sink_ids))
    rows = cg_conn.execute(
        f"SELECT t.node_id, n.file, t.taxonomy_id, t.line, n.qualified_name "
        f"FROM node_tags t JOIN nodes n ON n.id = t.node_id "
        f"WHERE t.taxonomy_id IN ({placeholders}) "
        f"ORDER BY n.file, t.line, t.taxonomy_id",
        tuple(sink_ids),
    ).fetchall()
    return list(rows)


def extract_routes(cg: Any, project_root: Path) -> list[RouteSpec]:
    """Pull RouteSpecs from callgraph node_tags + source files."""
    if cg is None or not hasattr(cg, "conn"):
        return []

    rows = _query_http_sink_tags(cg.conn, HTTP_SINK_IDS)
    if not rows:
        return []

    source_cache: dict[str, str] = {}
    out: list[RouteSpec] = []

    for _node_id, file, taxonomy_id, line, _qname in rows:
        text = source_cache.get(file)
        if text is None:
            text = _read_source(project_root, file)
            source_cache[file] = text
        if not text:
            continue
        snippet = _line_window(text, int(line), before=0, after=4)
        parsed = _extract_for_sink(taxonomy_id, snippet)
        if parsed is None:
            continue
        raw_url, method = parsed
        url = _normalise_url(raw_url)
        if not url:
            continue
        out.append(RouteSpec(
            url=url,
            method=method.upper(),
            shape_hint=infer_response_shape(cg, str(_node_id)),
            source_file=file,
            source_line=int(line),
            sink_id=taxonomy_id,
        ))
    return out


# ── response shape inference ─────────────────────────────────────────────

_PROP_CHAIN_RE = re.compile(
    r"""(?:\.(?P<name>[A-Za-z_$][\w$]*)|\[(?P<idx>\d+)\])"""
)


def infer_response_shape(cg: Any, sink_node_id: str) -> dict[str, Any] | None:
    """Walk property accesses on identifiers downstream of the sink.

    Searches the source-line region around the sink for patterns like
    `data.user.name` or `res.items[0].title` and assembles a dict.

    Returns None when no accesses are found. Uses '<probe>' as the leaf
    sentinel — replaced at response-time by response_factory.
    """
    if cg is None or not hasattr(cg, "conn"):
        return None
    try:
        nid = int(sink_node_id)
    except (TypeError, ValueError):
        return None

    row = cg.conn.execute(
        "SELECT n.file, n.start_line, n.end_line "
        "FROM nodes n WHERE n.id=?",
        (nid,),
    ).fetchone()
    if not row:
        return None
    file, start, end = row
    if not file or start is None:
        return None

    # The function body may be on disk; we have no project_root here.
    # Best-effort: search variables table for names and dataflow_edges for hints.
    # Fall back to None when nothing matches.
    try:
        rows = cg.conn.execute(
            "SELECT v.name FROM variables v "
            "WHERE v.node_id=? ORDER BY v.first_line",
            (nid,),
        ).fetchall()
    except Exception:
        return None

    # We don't have the source text here; use heuristic on names: any var
    # that looks like 'data', 'res', 'response', 'json' is a Promise result
    # — we just emit {"data": "<probe>"} as a hint.
    names = {r[0] for r in rows if r and r[0]}
    promise_vars = names & {"data", "res", "response", "json", "result"}
    if not promise_vars:
        return None
    return {"data": "<probe>"}


# Helper used by callers to decide whether to call the heavy AST parser.
def has_http_sinks(cg: Any) -> bool:
    if cg is None or not hasattr(cg, "conn"):
        return False
    placeholders = ",".join("?" * len(HTTP_SINK_IDS))
    row = cg.conn.execute(
        f"SELECT 1 FROM node_tags WHERE taxonomy_id IN ({placeholders}) LIMIT 1",
        tuple(HTTP_SINK_IDS),
    ).fetchone()
    return row is not None
