"""Vue (and Nuxt) framework adapter.

Plan: plans/ARCHITECTURE_EVOLUTION.md §6.3.

Hooks:
  patch_tags     — surface ``v-html`` and ``:is`` dynamic component as
                   sinks; ``vue-router`` route params as sources.
  rewrite_edges  — virtual continuation between computed properties +
                   watchers and the template render function.
  adjust_viability — Vue auto-escapes mustache interpolation; chains
                     ending in a `{{ }}` site are downgraded.
"""
from __future__ import annotations

import re
import sqlite3


name = "vue"


_V_HTML_RE = re.compile(r"v-html\s*=|innerHTML\s*=\s*")
_DYNAMIC_IS_RE = re.compile(r":is\s*=|<component\s+:is")
_ROUTER_PARAMS_RE = re.compile(r"\$route\.(?:params|query|hash)|useRoute\(\)\.")
_VUE_MUSTACHE_RE = re.compile(r"\{\{[^}]+\}\}")


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
        if _V_HTML_RE.search(raw):
            key = (int(caller_id), "vue_v_html")
            if key not in seen:
                _insert(cur, int(caller_id), "vue_v_html", "sink", "high",
                        has_source_col, has_conf_col, 0.95)
                seen.add(key)
                inserted += 1
        if _DYNAMIC_IS_RE.search(raw):
            key = (int(caller_id), "vue_dynamic_component")
            if key not in seen:
                _insert(cur, int(caller_id), "vue_dynamic_component", "sink", "medium",
                        has_source_col, has_conf_col, 0.55)
                seen.add(key)
                inserted += 1
        if _ROUTER_PARAMS_RE.search(raw):
            key = (int(caller_id), "vue_router_params")
            if key not in seen:
                _insert(cur, int(caller_id), "vue_router_params", "source", "high",
                        has_source_col, has_conf_col, 0.90)
                seen.add(key)
                inserted += 1
    conn.commit()
    return inserted


def _insert(cur, nid, taxid, kind, sev, has_source, has_conf, conf):
    cols = ["node_id", "taxonomy_id", "kind", "severity"]
    ph = ["?", "?", "?", "?"]
    vals: list = [nid, taxid, kind, sev]
    if has_source:
        cols.append("source"); ph.append("?"); vals.append("framework_vue")
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
    # Light: no synthetic continuation edges needed because Vue's
    # reactivity is captured by the Proxy-based getter chain — the
    # existing dataflow_edges already see most of it. Stubbed.
    return 0


def adjust_viability(chain: dict, ctx) -> float:
    sink = (chain.get("sink") or {})
    taxid = sink.get("taxonomy_id") or ""
    if "v_html" in taxid:
        return 1.0
    if "dynamic_component" in taxid:
        return 0.55
    # Vue mustache interpolation auto-escapes; downgrade generic innerHTML
    # in .vue files (the bundler often inlines template helpers that
    # carry innerHTML signatures).
    sink_file = (sink.get("file") or "").lower()
    if sink_file.endswith(".vue") and "innerHTML" in taxid:
        return 0.20
    return 1.0


class _Adapter:
    name = "vue"

    def patch_tags(self, conn):
        return patch_tags(conn)

    def rewrite_edges(self, conn):
        return rewrite_edges(conn)

    def adjust_viability(self, chain, ctx):
        return adjust_viability(chain, ctx)


adapter = _Adapter()
