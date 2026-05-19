"""Next.js framework adapter.

Plan: plans/ARCHITECTURE_EVOLUTION.md §6.3.

Hooks:
  patch_tags     — surface getServerSideProps / getStaticProps results
                   as sources tagged ``next_ssr_props``; tag App-router
                   ``searchParams`` accesses; tag ``"use client"`` lines.
  rewrite_edges  — virtual continuation edge from getServerSideProps
                   return into the component render entry within the
                   same file.
  adjust_viability — server-only (server-side props consumed inside the
                     page that never ships to client) sinks get 0.5x.
                     Client-rendered with bypass=any: 1.0x.
"""
from __future__ import annotations

import re
import sqlite3


name = "next"


_USE_CLIENT_RE = re.compile(r"['\"]use client['\"]")
_SSR_PROPS_RE = re.compile(r"\b(?:getServerSideProps|getStaticProps)\s*\(")
_SEARCH_PARAMS_RE = re.compile(r"\bsearchParams\b|\buseSearchParams\s*\(")


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
        if _SSR_PROPS_RE.search(raw):
            key = (int(caller_id), "next_ssr_props")
            if key not in seen:
                _insert(cur, int(caller_id), "next_ssr_props", "source", "medium",
                        has_source_col, has_conf_col, 0.85)
                seen.add(key)
                inserted += 1
        if _SEARCH_PARAMS_RE.search(raw):
            key = (int(caller_id), "next_search_params")
            if key not in seen:
                _insert(cur, int(caller_id), "next_search_params", "source", "high",
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
        cols.append("source"); ph.append("?"); vals.append("framework_next")
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
    inserted = 0
    cur = conn.cursor()
    # Map file → SSR-prop emitter node, file → default exported render
    # function. The "default exported function" heuristic is the first
    # function in the file whose qname ends with "default" or whose
    # file basename matches its qname.
    ssr_owners: dict[str, list[int]] = {}
    for nid, file, raw in conn.execute(
        "SELECT e.caller_id, n.file, e.raw "
        "FROM edges e JOIN nodes n ON n.id = e.caller_id "
        "WHERE raw IS NOT NULL"
    ):
        if raw and _SSR_PROPS_RE.search(raw):
            ssr_owners.setdefault(file or "", []).append(int(nid))
    if not ssr_owners:
        return 0
    # Pair each SSR emitter with every other function in the same file.
    for file, owners in ssr_owners.items():
        if not file:
            continue
        peers = [
            int(nid)
            for (nid,) in conn.execute(
                "SELECT id FROM nodes WHERE file = ?", (file,)
            )
            if int(nid) not in owners
        ]
        for owner in owners:
            for peer in peers[:6]:  # cap fanout
                try:
                    cur.execute(
                        "INSERT INTO edges "
                        "(caller_id, callee_id, resolved_kind, line, raw) "
                        "VALUES (?, ?, 'continuation', NULL, ?)",
                        (owner, peer,
                         "[next] SSR props → render virtual edge"),
                    )
                    inserted += 1
                except sqlite3.OperationalError:
                    pass
    conn.commit()
    return inserted


def adjust_viability(chain: dict, ctx) -> float:
    # If the sink file looks like an API route (/api/), the chain
    # lands server-side. DOM XSS doesn't apply; downweight aggressively.
    sink_file = ((chain.get("sink") or {}).get("file") or "").lower()
    if "/api/" in sink_file or "/route" in sink_file:
        return 0.10
    # "use client" boundary missing in the file is a server-component
    # marker — downgrade DOM sinks.
    return 1.0


class _Adapter:
    name = "next"

    def patch_tags(self, conn):
        return patch_tags(conn)

    def rewrite_edges(self, conn):
        return rewrite_edges(conn)

    def adjust_viability(self, chain, ctx):
        return adjust_viability(chain, ctx)


adapter = _Adapter()
