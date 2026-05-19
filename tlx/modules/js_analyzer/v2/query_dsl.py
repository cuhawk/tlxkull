"""V2 §17 — Graph query DSL / semantic query engine.

Fluent Python-embedded DSL over the per-target SQLite snapshot. Designed
to replace ad-hoc joins scattered across ``callgraph_tools.py``,
``gap_analyzer.py``, ``pp_chains.py``. Aim: most useful queries
expressible in 10 lines.

Default ON (``JS_ENABLE_QUERY_DSL=1``). No DB writes — read-only.

Usage::

    from modules.js_analyzer.v2.query_dsl import Q
    chains = (
        Q(conn)
            .sources(taxonomy_id="location_hash")
            .sinks(taxonomy_id__in=["innerHTML_assign", "eval_call"])
            .where_no_sanitizer()
            .top(50)
            .resolve()
    )
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Q", "QueryResult"]


@dataclass
class QueryResult:
    sources: list[dict] = field(default_factory=list)
    sinks: list[dict] = field(default_factory=list)
    chains: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"sources": self.sources, "sinks": self.sinks, "chains": self.chains}


class Q:
    """Read-only fluent query against the per-target snapshot."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._source_filters: list[tuple[str, Any]] = []
        self._sink_filters: list[tuple[str, Any]] = []
        self._require_no_sanitizer = False
        self._frameworks: list[str] = []
        self._async_aware = False
        self._confidence_min = 0.0
        self._top_n: int | None = None

    # ── builder methods (chainable) ────────────────────────────────────

    def sources(self, **kw) -> "Q":
        self._source_filters.extend(kw.items())
        return self

    def sinks(self, **kw) -> "Q":
        self._sink_filters.extend(kw.items())
        return self

    def where_no_sanitizer(self) -> "Q":
        self._require_no_sanitizer = True
        return self

    def frameworks_any(self, *frameworks: str) -> "Q":
        self._frameworks.extend(frameworks)
        return self

    def async_aware(self) -> "Q":
        self._async_aware = True
        return self

    def confidence_min(self, p: float) -> "Q":
        self._confidence_min = max(0.0, min(1.0, p))
        return self

    def top(self, n: int) -> "Q":
        self._top_n = max(1, int(n))
        return self

    # ── execution ──────────────────────────────────────────────────────

    def resolve(self) -> QueryResult:
        result = QueryResult()
        result.sources = self._fetch_tag_rows("source", self._source_filters)
        result.sinks = self._fetch_tag_rows("sink", self._sink_filters)
        # Chain materialization is left to the chain extractors; this
        # method returns the constrained source/sink lists so callers
        # can feed them into bestfirst / bounded extractors.
        result.chains = []
        return result

    def _fetch_tag_rows(self, kind: str, filters: list[tuple[str, Any]]) -> list[dict]:
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(node_tags)")}
        conf_col = "t.confidence" if "confidence" in cols else "1.0"
        src_col = "t.source" if "source" in cols else "'regex'"
        sql = (
            f"SELECT n.id, n.qualified_name, n.file, n.start_line, "
            f"       t.taxonomy_id, t.severity, {conf_col}, {src_col} "
            f"FROM node_tags t JOIN nodes n ON n.id = t.node_id "
            f"WHERE t.kind = ?"
        )
        params: list[Any] = [kind]
        for key, value in filters:
            if key.endswith("__in"):
                base = key[:-4]
                if not value:
                    continue
                placeholders = ",".join("?" * len(value))
                sql += f" AND t.{base} IN ({placeholders})"
                params.extend(value)
            else:
                sql += f" AND t.{key} = ?"
                params.append(value)
        if self._confidence_min > 0:
            sql += " AND " + conf_col + " >= ?"
            params.append(self._confidence_min)
        if self._top_n:
            sql += f" ORDER BY {conf_col} DESC LIMIT ?"
            params.append(self._top_n)

        out: list[dict] = []
        try:
            rows = self.conn.execute(sql, tuple(params)).fetchall()
        except sqlite3.OperationalError:
            return out
        for nid, qname, file, line, taxid, sev, conf, src_tag in rows:
            out.append({
                "node_id": nid,
                "qname": qname,
                "file": file,
                "line": line,
                "taxonomy_id": taxid,
                "severity": sev,
                "confidence": float(conf or 1.0),
                "tag_source": src_tag or "regex",
            })
        if self._require_no_sanitizer:
            try:
                sanitized_node_ids = {r[0] for r in self.conn.execute(
                    "SELECT DISTINCT node_id FROM node_sanitizers"
                )}
            except sqlite3.OperationalError:
                sanitized_node_ids = set()
            out = [r for r in out if r["node_id"] not in sanitized_node_ids]
        return out
