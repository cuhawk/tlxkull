"""Angular framework adapter.

Plan: plans/ARCHITECTURE_EVOLUTION.md §6.3.

Hooks:
  patch_tags     — tag ``bypassSecurityTrustHtml`` / TrustScript /
                   TrustResourceUrl callers as ``angular_bypass_*``
                   sinks; tag ``[innerHTML]`` template bindings; tag
                   ``ActivatedRoute.params`` / ``snapshot.queryParams``
                   as sources.
  rewrite_edges  — virtual edge from ``ngOnInit`` body to subscribe
                   callbacks within the same component.
  adjust_viability — Angular auto-sanitizes via DomSanitizer; chains
                     landing in ``[innerHTML]`` *without* a preceding
                     bypassSecurityTrustHtml are heavily downgraded.
"""
from __future__ import annotations

import re
import sqlite3


name = "angular"


_BYPASS_RE = re.compile(
    r"bypassSecurityTrust(?:Html|Script|ResourceUrl|Style|Url)\s*\("
)
_INNER_HTML_BINDING_RE = re.compile(r"\[innerHTML\]\s*=")
_ROUTE_PARAMS_RE = re.compile(
    r"\b(?:ActivatedRoute|activatedRoute)[\w.]*\."
    r"(?:params|queryParams|snapshot)\b"
)


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
        if _BYPASS_RE.search(raw):
            key = (int(caller_id), "angular_bypass_security_trust")
            if key not in seen:
                _insert(cur, int(caller_id), "angular_bypass_security_trust",
                        "sink", "high", has_source_col, has_conf_col, 0.95)
                seen.add(key); inserted += 1
        if _INNER_HTML_BINDING_RE.search(raw):
            key = (int(caller_id), "angular_inner_html_binding")
            if key not in seen:
                _insert(cur, int(caller_id), "angular_inner_html_binding",
                        "sink", "medium", has_source_col, has_conf_col, 0.55)
                seen.add(key); inserted += 1
        if _ROUTE_PARAMS_RE.search(raw):
            key = (int(caller_id), "angular_route_params")
            if key not in seen:
                _insert(cur, int(caller_id), "angular_route_params",
                        "source", "high", has_source_col, has_conf_col, 0.90)
                seen.add(key); inserted += 1
    conn.commit()
    return inserted


def _insert(cur, nid, taxid, kind, sev, has_source, has_conf, conf):
    cols = ["node_id", "taxonomy_id", "kind", "severity"]
    ph = ["?", "?", "?", "?"]
    vals: list = [nid, taxid, kind, sev]
    if has_source:
        cols.append("source"); ph.append("?"); vals.append("framework_angular")
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
    # Edge synthesis between ngOnInit and subscribe handlers requires
    # AST-level visibility we don't have here. Stubbed for parity.
    return 0


def adjust_viability(chain: dict, ctx) -> float:
    sink = (chain.get("sink") or {})
    taxid = sink.get("taxonomy_id") or ""
    path = chain.get("path") or []
    # bypassSecurityTrust unconditionally trusts attacker content.
    if "bypass_security_trust" in taxid:
        return 1.0
    # [innerHTML] without a preceding bypassSecurityTrustHtml is
    # auto-sanitized — strong downgrade.
    if "inner_html_binding" in taxid:
        path_str = " ".join(
            (h if isinstance(h, str) else h.get("qname", "")) for h in path
        )
        if "bypassSecurityTrust" in path_str:
            return 1.0
        return 0.05
    return 1.0


class _Adapter:
    name = "angular"

    def patch_tags(self, conn):
        return patch_tags(conn)

    def rewrite_edges(self, conn):
        return rewrite_edges(conn)

    def adjust_viability(self, chain, ctx):
        return adjust_viability(chain, ctx)


adapter = _Adapter()
