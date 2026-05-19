"""React (and Preact) framework adapter.

Plan: plans/ARCHITECTURE_EVOLUTION.md §6.3.

Hooks:
  patch_tags     — surface ``react_dangerously_set_inner_html`` and
                   ``react_ref_callback`` tags.
  rewrite_edges  — add virtual ``useEffect`` / ``useLayoutEffect``
                   continuation edges so taint can flow from setState
                   into the effect body.
  adjust_viability — JSX children auto-escape: chains ending in JSX text
                   are downgraded; ``dangerouslySetInnerHTML`` is
                   unaffected; refs land at 1.0× (still exploitable).
"""
from __future__ import annotations

import re
import sqlite3


name = "react"


_DANGEROUS_RE = re.compile(r"dangerouslySetInnerHTML\s*[:=]")
_REF_CB_RE = re.compile(r"\bref\s*=\s*\{?\s*\(\s*[\w$]*\s*\)\s*=>")
_USE_EFFECT_RE = re.compile(r"\b(?:useEffect|useLayoutEffect)\s*\(\s*(?:async\s*)?\(\s*\)\s*=>")
_USE_STATE_SETTER_RE = re.compile(r"\bset[A-Z]\w*\s*\(")
_JSX_TEXT_RE = re.compile(r"\{[\w$]+\}")


def patch_tags(conn: sqlite3.Connection) -> int:
    """Add tag rows for React-specific source/sink markers found in
    edges.raw. Uses node_tags; idempotent.
    """
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    has_source_col = "source" in cols
    has_conf_col = "confidence" in cols
    inserted = 0
    cur = conn.cursor()
    seen: set[tuple[int, str]] = set()
    for caller_id, raw in conn.execute(
        "SELECT DISTINCT caller_id, raw FROM edges "
        "WHERE raw IS NOT NULL AND raw LIKE '%dangerouslySetInnerHTML%'"
    ):
        key = (int(caller_id), "react_dangerously_set_inner_html")
        if key in seen:
            continue
        seen.add(key)
        if not _DANGEROUS_RE.search(raw or ""):
            continue
        _insert_tag(
            cur, int(caller_id),
            "react_dangerously_set_inner_html", "sink", "high",
            has_source_col, has_conf_col, 0.95,
        )
        inserted += 1
    for caller_id, raw in conn.execute(
        "SELECT DISTINCT caller_id, raw FROM edges "
        "WHERE raw IS NOT NULL AND raw LIKE '%ref=%'"
    ):
        if not _REF_CB_RE.search(raw or ""):
            continue
        key = (int(caller_id), "react_ref_callback")
        if key in seen:
            continue
        seen.add(key)
        _insert_tag(
            cur, int(caller_id),
            "react_ref_callback", "sink", "medium",
            has_source_col, has_conf_col, 0.60,
        )
        inserted += 1
    conn.commit()
    return inserted


def _insert_tag(
    cur: sqlite3.Cursor, node_id: int, taxonomy_id: str,
    kind: str, severity: str, has_source: bool, has_conf: bool,
    confidence: float,
) -> None:
    cols = ["node_id", "taxonomy_id", "kind", "severity"]
    placeholders = ["?", "?", "?", "?"]
    values: list = [node_id, taxonomy_id, kind, severity]
    if has_source:
        cols.append("source")
        placeholders.append("?")
        values.append("framework_react")
    if has_conf:
        cols.append("confidence")
        placeholders.append("?")
        values.append(confidence)
    try:
        cur.execute(
            f"INSERT OR IGNORE INTO node_tags ({', '.join(cols)}) "
            f"VALUES ({', '.join(placeholders)})",
            tuple(values),
        )
    except sqlite3.OperationalError:
        pass


def rewrite_edges(conn: sqlite3.Connection) -> int:
    """Add virtual continuation edges from setState(...) sites to the
    useEffect handler within the same component file.
    """
    inserted = 0
    cur = conn.cursor()
    # Collect (file, caller_id) pairs for useEffect handlers and for
    # setState callers; pair them inside the same file.
    use_effect_owners: dict[str, list[int]] = {}
    for cid, file, raw in conn.execute(
        "SELECT e.caller_id, n.file, e.raw "
        "FROM edges e JOIN nodes n ON n.id = e.caller_id "
        "WHERE raw IS NOT NULL"
    ):
        if raw and _USE_EFFECT_RE.search(raw):
            use_effect_owners.setdefault(file or "", []).append(int(cid))
    if not use_effect_owners:
        return 0
    for cid, file, raw in conn.execute(
        "SELECT e.caller_id, n.file, e.raw "
        "FROM edges e JOIN nodes n ON n.id = e.caller_id "
        "WHERE raw IS NOT NULL"
    ):
        if not raw or not _USE_STATE_SETTER_RE.search(raw):
            continue
        owners = use_effect_owners.get(file or "", [])
        for owner in owners:
            if owner == int(cid):
                continue
            try:
                cur.execute(
                    "INSERT INTO edges "
                    "(caller_id, callee_id, resolved_kind, line, raw, edge_class) "
                    "VALUES (?, ?, 'continuation', NULL, ?, 'continuation')",
                    (int(cid), int(owner),
                     "[react] setState → useEffect virtual edge"),
                )
                inserted += 1
            except sqlite3.OperationalError:
                # edge_class column may not exist; fall back.
                try:
                    cur.execute(
                        "INSERT INTO edges "
                        "(caller_id, callee_id, resolved_kind, line, raw) "
                        "VALUES (?, ?, 'continuation', NULL, ?)",
                        (int(cid), int(owner),
                         "[react] setState → useEffect virtual edge"),
                    )
                    inserted += 1
                except sqlite3.OperationalError:
                    pass
    conn.commit()
    return inserted


def adjust_viability(chain: dict, ctx) -> float:
    sink = chain.get("sink") or {}
    taxid = sink.get("taxonomy_id") or ""
    if "dangerously" in taxid:
        return 1.0
    if "react_ref_callback" in taxid:
        return 1.0
    # JSX children auto-escape: chains landing in a generic innerHTML
    # tagged inside a React component file still benefit because
    # children pass through React's element-text escape unless
    # explicitly bypassed.
    sink_file = (sink.get("file") or "").lower()
    if sink_file.endswith((".jsx", ".tsx")) and "innerHTML" in taxid:
        return 0.25
    return 1.0


class _Adapter:
    name = "react"

    def patch_tags(self, conn):
        return patch_tags(conn)

    def rewrite_edges(self, conn):
        return rewrite_edges(conn)

    def adjust_viability(self, chain, ctx):
        return adjust_viability(chain, ctx)


adapter = _Adapter()
