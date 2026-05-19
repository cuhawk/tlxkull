"""Svelte (and SvelteKit) framework adapter.

Plan: plans/ARCHITECTURE_EVOLUTION.md §6.3.

Hooks:
  patch_tags     — surface ``{@html ...}`` directive sites (compiler
                   emits them as ``$$.element(..., html(x))`` after
                   compile) as ``svelte_at_html`` sinks. Tag
                   ``$page.url`` / ``page.params`` as ``svelte_kit_*``
                   sources.
  rewrite_edges  — Svelte's reactive ``$:`` statements are handled by
                   the compiler — no virtual edges needed.
  adjust_viability — chains landing in ``svelte_at_html`` track 1.0×.
                   Generic innerHTML in a .svelte-compiled file is
                   downweighted because compiler-emitted DOM ops escape
                   text children.
"""
from __future__ import annotations

import re
import sqlite3


name = "svelte"


_AT_HTML_RE = re.compile(r"\{@html\b|@html\s*\(")
_KIT_URL_RE = re.compile(r"\$page\.url|page\.url|useURL\s*\(")
_KIT_PARAMS_RE = re.compile(r"\$page\.params|page\.params|params\s*=\s*\$\$")


def patch_tags(conn: sqlite3.Connection) -> int:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(node_tags)")}
    has_source_col = "source" in cols
    has_conf_col = "confidence" in cols
    inserted = 0
    cur = conn.cursor()
    seen: set[tuple[int, str]] = set()
    for caller_id, raw in conn.execute(
        "SELECT DISTINCT caller_id, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        if _AT_HTML_RE.search(raw):
            key = (int(caller_id), "svelte_at_html")
            if key not in seen:
                _insert(cur, int(caller_id), "svelte_at_html", "sink", "high",
                        has_source_col, has_conf_col, 0.95)
                seen.add(key); inserted += 1
        if _KIT_URL_RE.search(raw):
            key = (int(caller_id), "svelte_kit_url")
            if key not in seen:
                _insert(cur, int(caller_id), "svelte_kit_url", "source", "medium",
                        has_source_col, has_conf_col, 0.80)
                seen.add(key); inserted += 1
        if _KIT_PARAMS_RE.search(raw):
            key = (int(caller_id), "svelte_kit_params")
            if key not in seen:
                _insert(cur, int(caller_id), "svelte_kit_params", "source", "high",
                        has_source_col, has_conf_col, 0.90)
                seen.add(key); inserted += 1
    conn.commit()
    return inserted


def _insert(cur, nid, taxid, kind, sev, has_source, has_conf, conf):
    cols = ["node_id", "taxonomy_id", "kind", "severity"]
    ph = ["?", "?", "?", "?"]
    vals: list = [nid, taxid, kind, sev]
    if has_source:
        cols.append("source"); ph.append("?"); vals.append("framework_svelte")
    if has_conf:
        cols.append("confidence"); ph.append("?"); vals.append(conf)
    try:
        cur.execute(
            f"INSERT OR IGNORE INTO node_tags ({', '.join(cols)}) "
            f"VALUES ({', '.join(ph)})", tuple(vals),
        )
    except sqlite3.OperationalError:
        pass


def rewrite_edges(conn: sqlite3.Connection) -> int:
    return 0


def adjust_viability(chain: dict, ctx) -> float:
    sink = (chain.get("sink") or {})
    taxid = sink.get("taxonomy_id") or ""
    if "at_html" in taxid:
        return 1.0
    sink_file = (sink.get("file") or "").lower()
    if sink_file.endswith((".svelte", ".svelte.js")) and "innerHTML" in taxid:
        return 0.25
    return 1.0


class _Adapter:
    name = "svelte"

    def patch_tags(self, conn):
        return patch_tags(conn)

    def rewrite_edges(self, conn):
        return rewrite_edges(conn)

    def adjust_viability(self, chain, ctx):
        return adjust_viability(chain, ctx)


adapter = _Adapter()
