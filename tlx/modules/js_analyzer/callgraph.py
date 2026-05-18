"""SQLite call graph built from ast_extractor.js output.

Schema:
    nodes(id, qualified_name UNIQUE, file, name, parent, kind, start_line, end_line)
    edges(caller_id, callee_id NULL, line, raw, callee_raw, resolved_kind,
          PK(caller_id, line, callee_raw))

Resolution rules (in order):
    1. callee_kind == 'dynamic'         -> resolved_kind='dynamic',  callee_id=NULL
    2. unique node match by bare name   -> resolved_kind='exact'
    3. multiple matches                 -> resolved_kind='name_match',
                                           pick first by alphabetical qualified_name
    4. no match                         -> resolved_kind='unresolved', callee_id=NULL

Idempotent: re-indexing a file purges its existing nodes (and edges originating
from those nodes) before re-inserting. Edges *into* deleted nodes from other
files become orphaned (callee_id pointing to a now-missing id) — they are
re-resolved when their owning file is re-indexed.

Cross-file import resolution: handled by Phase D2 (additive repair pass over
edges left as 'unresolved' by Phase D). Uses ast_extractor's `import_map`
(persisted in import_edges table) to map a bare callee identifier back to
the imported module + name, then matches against nodes by file + name.

Out of scope (Tasks 3+): this-binding tracking refinements,
sink/source tagging, path-finding queries.
"""

import hashlib
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

import structlog

from modules.js_analyzer.taint import solve_function_taint

_log = structlog.get_logger(__name__)

# Rule IDs handled by ast_extractor.js AST visitors.
# For these IDs the regex path is suppressed; the AST tag is used instead.
# Keep in sync with the AST_RULES visitor block in ast_extractor.js.
AST_COVERED_RULE_IDS: frozenset[str] = frozenset({
    # sinks
    'innerHTML_assign',
    'outerHTML_assign',
    'srcdoc_assign',
    'event_handler_attr_assign',
    'location_href_assign',
    'location_assign_call',
    'location_replace_call',
    'eval_call',
    'eval_indirect',
    'new_Function',
    'setTimeout_string',
    'setInterval_string',
    'setImmediate_string',
    'document_write',
    'document_writeln',
    'insertAdjacentHTML_call',
    'setAttribute_dangerous_attr',
    'setAttribute_dynamic_attr',
    'dangerouslySetInnerHTML',
    'fetch_call',
    'xhr_open_call',
    'axios_call',
    # sources
    'location_hash',
    'location_search',
    'location_pathname',
    'location_href_read',
    'document_URL',
    'document_documentURI',
    'document_baseURI',
    'document_referrer',
    'document_cookie',
    'window_name',
    'message_event_data_read',
    'URLSearchParams_ctor',
    'searchParams_get',
    # prototype-pollution write sources (regex path retained for proto_assign_merge)
    'proto_assign_bracket',
    'proto_assign_direct',
    # framework-aware sources (AST-emitted, gated by ACTIVE_FRAMEWORKS)
    'express_req_body',
    'express_req_query',
    'express_req_params',
    'express_req_headers',
    'express_req_cookies',
    'express_req_files',
    'nextjs_searchparams',
    'nextjs_api_req',
    'angular_activatedroute_params',
    'fs_path_user',
    'child_process_input',
    # framework-aware sinks (AST-emitted, gated by ACTIVE_FRAMEWORKS)
    'angular_bypass_trust_html',
    'angular_inner_html_binding',
    'child_process_exec_sink',
    'child_process_spawn_sink',
    'sql_injection_sink',
    'nosql_injection_sink',
    'path_traversal_sink',
    'electron_shell_openexternal',
    'electron_nodeintegration_sink',
    'vue_v_html_sink',
})


# Framework tags active for the current scan. Set by main.py via
# `set_active_frameworks()` before indexing. Defaults to {'node'} so existing
# call sites that never opt in still get baseline behaviour.
ACTIVE_FRAMEWORKS: frozenset[str] = frozenset({'node'})


def set_active_frameworks(tags) -> None:
    """Install the framework tag set used to gate framework-aware rules."""
    global ACTIVE_FRAMEWORKS
    if tags is None:
        ACTIVE_FRAMEWORKS = frozenset({'node'})
        return
    cleaned = {str(t).strip() for t in tags if str(t).strip()}
    if not cleaned:
        cleaned = {'node'}
    cleaned.add('node')
    ACTIVE_FRAMEWORKS = frozenset(cleaned)


SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id             INTEGER PRIMARY KEY,
    qualified_name TEXT UNIQUE,
    file           TEXT,
    name           TEXT,
    parent         TEXT,
    kind           TEXT,
    start_line     INT,
    end_line       INT
);
CREATE TABLE IF NOT EXISTS edges (
    caller_id        INT NOT NULL,
    callee_id        INT,
    line             INT,
    raw              TEXT,
    callee_raw       TEXT,
    resolved_kind    TEXT,
    candidate_count  INT NOT NULL DEFAULT 1,
    PRIMARY KEY (caller_id, line, callee_raw)
);
CREATE TABLE IF NOT EXISTS node_tags (
    node_id     INT NOT NULL,
    taxonomy_id TEXT NOT NULL,
    kind        TEXT NOT NULL,
    severity    TEXT NOT NULL,
    line        INT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'regex',
    confidence  REAL NOT NULL DEFAULT 1.0,
    evidence    TEXT,
    PRIMARY KEY (node_id, taxonomy_id, line)
);
CREATE TABLE IF NOT EXISTS url_refs (
    id           INTEGER PRIMARY KEY,
    file         TEXT NOT NULL,
    url_template TEXT NOT NULL,
    type         TEXT NOT NULL,
    method       TEXT,
    query_params TEXT,
    body_params  TEXT,
    line         INT NOT NULL,
    in_function  TEXT
);
CREATE TABLE IF NOT EXISTS node_sanitizers (
    node_id     INT NOT NULL,
    taxonomy_id TEXT NOT NULL,
    line        INT NOT NULL,
    clears      TEXT NOT NULL,
    PRIMARY KEY (node_id, taxonomy_id, line)
);
CREATE TABLE IF NOT EXISTS node_taint_flows (
    node_id          INT NOT NULL,
    source_rule      TEXT NOT NULL,
    source_line      INT NOT NULL,
    sink_rule        TEXT NOT NULL,
    sink_line        INT NOT NULL,
    via_vars         TEXT NOT NULL,
    sanitised_by     TEXT,
    sanitiser_clears TEXT,
    PRIMARY KEY (node_id, source_line, sink_line, source_rule, sink_rule)
);
CREATE TABLE IF NOT EXISTS variables (
    id           INTEGER PRIMARY KEY,
    node_id      INT NOT NULL,
    name         TEXT NOT NULL,
    first_line   INT NOT NULL,
    UNIQUE(node_id, name)
);
CREATE TABLE IF NOT EXISTS dataflow_edges (
    from_var     INT,
    to_var       INT NOT NULL,
    edge_kind    TEXT NOT NULL,
    line         INT NOT NULL,
    sanitiser    TEXT,
    PRIMARY KEY (from_var, to_var, line, edge_kind)
);
CREATE INDEX IF NOT EXISTS idx_taint_node ON node_taint_flows(node_id);
CREATE INDEX IF NOT EXISTS idx_var_node   ON variables(node_id);
CREATE INDEX IF NOT EXISTS idx_df_to      ON dataflow_edges(to_var);
CREATE INDEX IF NOT EXISTS idx_df_from    ON dataflow_edges(from_var);
CREATE INDEX IF NOT EXISTS idx_san_node ON node_sanitizers(node_id);
CREATE INDEX IF NOT EXISTS idx_edges_caller ON edges(caller_id);
CREATE INDEX IF NOT EXISTS idx_edges_callee ON edges(callee_id);
CREATE INDEX IF NOT EXISTS idx_nodes_name   ON nodes(name);
CREATE INDEX IF NOT EXISTS idx_nodes_file   ON nodes(file);
CREATE INDEX IF NOT EXISTS idx_tags_node    ON node_tags(node_id);
CREATE INDEX IF NOT EXISTS idx_tags_kind    ON node_tags(kind, severity);
CREATE INDEX IF NOT EXISTS idx_url_refs_file ON url_refs(file);
CREATE INDEX IF NOT EXISTS idx_url_refs_type ON url_refs(type);
CREATE TABLE IF NOT EXISTS import_edges (
    id            INTEGER PRIMARY KEY,
    file          TEXT NOT NULL,
    local_name    TEXT NOT NULL,
    source_module TEXT NOT NULL,
    imported_name TEXT NOT NULL,
    line          INT  NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_import_file  ON import_edges(file);
CREATE INDEX IF NOT EXISTS idx_import_local ON import_edges(local_name);
CREATE TABLE IF NOT EXISTS file_hashes (
    file       TEXT PRIMARY KEY,
    sha256     TEXT NOT NULL,
    indexed_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS js_audit_runs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    shell_session_id  TEXT NOT NULL,
    target_folder     TEXT NOT NULL,
    started_at        TEXT NOT NULL,
    finished_at       TEXT,
    status            TEXT NOT NULL,
    total_tokens      INTEGER DEFAULT 0,
    cost_usd          REAL DEFAULT 0.0,
    consults_used     INTEGER DEFAULT 0,
    consults_cost_usd REAL DEFAULT 0.0,
    failure_reason    TEXT,
    external_run_id   TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_runs_external
    ON js_audit_runs(external_run_id) WHERE external_run_id IS NOT NULL;
CREATE TABLE IF NOT EXISTS js_audit_turns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER NOT NULL REFERENCES js_audit_runs(id) ON DELETE CASCADE,
    turn_index   INTEGER NOT NULL,
    role         TEXT NOT NULL,
    content_json TEXT NOT NULL,
    tokens_in    INTEGER,
    tokens_out   INTEGER,
    cost_usd     REAL,
    observed_at  TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_audit_turns_run ON js_audit_turns(run_id);
"""


_MODULE_EXTS: tuple[str, ...] = (".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx")


def _resolve_module_to_rel(
    caller_file: str, specifier: str, root_dir: Path | None
) -> str | None:
    """Normalise a relative import specifier to a project-rel path string.

    Returns None for non-relative (external / bare-package) specifiers and
    for paths that escape the graph root.
    """
    if not (specifier.startswith("./") or specifier.startswith("../")
            or specifier.startswith("/")):
        return None
    if specifier.startswith("/"):
        return None  # filesystem-absolute; not handled

    raw = Path(caller_file).parent / specifier
    parts: list[str] = []
    for p in raw.parts:
        if p == "..":
            if parts and parts[-1] != "..":
                parts.pop()
            else:
                parts.append("..")
        elif p in (".", ""):
            continue
        else:
            parts.append(p)
    if not parts or parts[0] == "..":
        return None
    rel = "/".join(parts)
    # root_dir is currently advisory — relative-spec normalisation does not
    # need filesystem access. Reserved for future absolute-spec handling.
    _ = root_dir
    return rel


def _candidate_files(rel: str) -> list[str]:
    """Generate candidate file paths a module specifier may resolve to."""
    out: list[str] = [rel]
    if not any(rel.endswith(e) for e in _MODULE_EXTS):
        for e in _MODULE_EXTS:
            out.append(rel + e)
        for e in _MODULE_EXTS:
            out.append(f"{rel}/index{e}")
    return out


def _bare_name(name: str | None) -> str:
    """Last dotted segment of a function name. 'Foo.bar' -> 'bar', '#priv' -> '#priv'."""
    if not name:
        return ""
    return name.rsplit(".", 1)[-1]


def _resolve_target(callee: str, kind: str) -> str | None:
    """Reduce extractor's callee string to the bare name to look up in nodes.name."""
    if kind == "dynamic":
        return None
    if kind == "new":
        rest = callee[4:] if callee.startswith("new ") else callee
        return rest.rsplit(".", 1)[-1] or None
    if kind in ("this", "super"):
        if "." in callee:
            return callee.split(".", 1)[1]
        return None
    if kind == "member":
        return callee.rsplit(".", 1)[-1] or None
    if kind == "ident":
        return callee or None
    return None


def _resolve_this_binding(
    caller_parent: str,
    caller_file: str,
    method_name: str,
    conn: sqlite3.Connection,
) -> tuple[int | None, str]:
    """Resolve a this.method() call using the caller's class parent.

    Strategy (tried in order):
    1. Same file, same parent class, matching name  → 'exact'
    2. Any file, same parent class, matching name
       and unique result                             → 'this_cross_file'
    3. Fall back to None                             → 'unresolved'

    Returns (callee_id, resolved_kind).
    """
    if not caller_parent or not method_name:
        return None, "unresolved"

    # ast_extractor stores method name as "Parent.method" (parent column also set);
    # accept either form.
    qualified = f"{caller_parent}.{method_name}"

    rows = conn.execute(
        "SELECT id FROM nodes WHERE file=? AND parent=? AND (name=? OR name=?)",
        (caller_file, caller_parent, method_name, qualified),
    ).fetchall()
    if len(rows) == 1:
        return rows[0][0], "exact"

    rows = conn.execute(
        "SELECT id FROM nodes WHERE parent=? AND (name=? OR name=?)",
        (caller_parent, method_name, qualified),
    ).fetchall()
    if len(rows) == 1:
        return rows[0][0], "this_cross_file"

    return None, "unresolved"


class CallGraph:
    """SQLite-backed call graph. One DB per workspace, lives next to Chroma."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.executescript(SCHEMA)
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(node_tags)")}
        if 'source' not in cols:
            self.conn.execute(
                "ALTER TABLE node_tags ADD COLUMN source TEXT NOT NULL DEFAULT 'regex'"
            )
        if 'confidence' not in cols:
            self.conn.execute(
                "ALTER TABLE node_tags ADD COLUMN confidence REAL NOT NULL DEFAULT 1.0"
            )
        if 'evidence' not in cols:
            self.conn.execute(
                "ALTER TABLE node_tags ADD COLUMN evidence TEXT"
            )
        edge_cols = {r[1] for r in self.conn.execute("PRAGMA table_info(edges)")}
        if 'candidate_count' not in edge_cols:
            self.conn.execute(
                "ALTER TABLE edges ADD COLUMN candidate_count INT NOT NULL DEFAULT 1"
            )
        # Phase 10 migration: original line mapping from source-map remapping
        node_cols = {r[1] for r in self.conn.execute("PRAGMA table_info(nodes)")}
        if "original_line" not in node_cols:
            self.conn.execute(
                "ALTER TABLE nodes ADD COLUMN original_line INTEGER"
            )
            self.conn.execute(
                "ALTER TABLE nodes ADD COLUMN original_file TEXT"
            )
        # Phase 8D migration: external uuid run_id for MCP-facing js_run_audit
        run_cols = {
            r[1] for r in self.conn.execute("PRAGMA table_info(js_audit_runs)")
        }
        if "external_run_id" not in run_cols:
            self.conn.execute(
                "ALTER TABLE js_audit_runs ADD COLUMN external_run_id TEXT"
            )
            self.conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_runs_external "
                "ON js_audit_runs(external_run_id) "
                "WHERE external_run_id IS NOT NULL"
            )
        self.conn.commit()
        self.ambiguities: list[tuple[str, list[str]]] = []

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _qname(file: str, fn: dict) -> str:
        # name from ast_extractor already includes parent for class methods
        # (e.g., 'Foo.init'), so don't double-prefix.
        return f"{file}::{fn.get('name', 'anonymous')}"

    def _purge_file(self, file: str) -> None:
        c = self.conn.cursor()
        ids = [r[0] for r in c.execute("SELECT id FROM nodes WHERE file=?", (file,))]
        if ids:
            qmarks = ",".join("?" * len(ids))
            c.execute(f"DELETE FROM edges     WHERE caller_id IN ({qmarks})", ids)
            c.execute(f"DELETE FROM node_tags WHERE node_id   IN ({qmarks})", ids)
            c.execute(f"DELETE FROM node_sanitizers WHERE node_id IN ({qmarks})", ids)
            c.execute(f"DELETE FROM node_taint_flows WHERE node_id IN ({qmarks})", ids)
            c.execute(
                f"DELETE FROM dataflow_edges WHERE "
                f"from_var IN (SELECT id FROM variables WHERE node_id IN ({qmarks})) OR "
                f"to_var   IN (SELECT id FROM variables WHERE node_id IN ({qmarks}))",
                ids + ids,
            )
            c.execute(f"DELETE FROM variables WHERE node_id IN ({qmarks})", ids)
        c.execute("DELETE FROM nodes WHERE file=?", (file,))
        c.execute("DELETE FROM url_refs WHERE file=?", (file,))
        c.execute("DELETE FROM import_edges WHERE file=?", (file,))

    # ── public API ───────────────────────────────────────────────────────

    # ── file-hash cache (Phase 7C Task 2) ────────────────────────────────

    def is_file_unchanged(
        self, file_rel: str, abs_path: Path, *, force: bool = False,
    ) -> bool:
        """Return True if `abs_path`'s sha256 matches the cached entry.

        force=True bypasses the cache check (always returns False).
        """
        if force:
            return False
        try:
            digest = hashlib.sha256(
                Path(abs_path).read_bytes()
            ).hexdigest()
        except OSError:
            return False
        row = self.conn.execute(
            "SELECT sha256 FROM file_hashes WHERE file=?", (file_rel,),
        ).fetchone()
        if row is not None and row[0] == digest:
            _log.info("callgraph.skip_unchanged", file=file_rel)
            return True
        return False

    def record_file_hash(self, file_rel: str, abs_path: Path) -> None:
        try:
            digest = hashlib.sha256(
                Path(abs_path).read_bytes()
            ).hexdigest()
        except OSError:
            return
        self.conn.execute(
            "INSERT OR REPLACE INTO file_hashes "
            "(file, sha256, indexed_at) VALUES (?, ?, datetime('now'))",
            (file_rel, digest),
        )
        self.conn.commit()

    def index_file(
        self, file: str, ast_entry: dict, *,
        taxonomy=None, source: str | None = None,
        root_dir: Path | None = None,
        force: bool = False,
        abs_path: Path | None = None,
    ) -> None:
        """Index a single file. Convenience wrapper over index_batch.

        When `abs_path` is supplied and `force=False`, sha256 cache is
        consulted; an unchanged file is skipped and logged.
        """
        if abs_path is not None and self.is_file_unchanged(
            file, abs_path, force=force,
        ):
            return
        sources = {file: source} if source is not None else None
        self.index_batch({file: ast_entry}, taxonomy=taxonomy,
                         file_sources=sources, root_dir=root_dir)
        if abs_path is not None:
            self.record_file_hash(file, abs_path)

    def index_batch(
        self, ast_results: dict, *,
        taxonomy=None, file_sources: dict | None = None,
        root_dir: Path | None = None,
        template_files: dict | None = None,
    ) -> dict:
        """Persist nodes + edges for a batch of AST results.

        ast_results: {rel_path: {'ok': bool, 'functions': [...], 'error': ...}}
        taxonomy: optional Taxonomy instance — when supplied with file_sources,
            tags every node with sink/source matches inside its line range.
        file_sources: {rel_path: full file text}. Required for tagging.
        template_files: {rel_path: full file text} for .vue / .html templates
            scanned via template_analyzer (Vue v-html, Angular [innerHTML]).

        Returns stats dict with counts per resolved_kind plus tag counts.
        """
        c = self.conn.cursor()

        # Phase A: purge prior data for these files (idempotent re-index)
        for file in ast_results.keys():
            self._purge_file(file)

        # Phase B: collect all functions in this batch
        node_meta: list[tuple[str, dict]] = []
        ast_tags_by_file: dict[str, list[dict]] = {}
        for file, entry in ast_results.items():
            if not isinstance(entry, dict) or not entry.get("ok"):
                continue
            for fn in entry.get("functions", []) or []:
                if not isinstance(fn, dict):
                    continue
                node_meta.append((file, fn))
            tags = entry.get("ast_tags")
            if isinstance(tags, list):
                ast_tags_by_file[file] = tags

        # Insert nodes first so cross-file calls within the batch can resolve
        for file, fn in node_meta:
            qname = self._qname(file, fn)
            c.execute(
                "INSERT OR IGNORE INTO nodes "
                "(qualified_name, file, name, parent, kind, start_line, end_line, "
                " original_line, original_file) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (qname, file, fn.get("name"), fn.get("parent"), fn.get("kind"),
                 fn.get("start"), fn.get("end"),
                 fn.get("original_line"),   # None if no source map
                 fn.get("original_file")),  # None if no source map
            )

        # Phase B2: persist import declarations from this batch.
        # Idempotent — _purge_file already cleared this file's prior rows.
        for file, entry in ast_results.items():
            if not isinstance(entry, dict) or not entry.get("ok"):
                continue
            for imp in entry.get("import_map") or []:
                if not isinstance(imp, dict):
                    continue
                local_name    = imp.get("local_name")
                source_module = imp.get("source_module")
                imported_name = imp.get("imported_name")
                if not (local_name and source_module and imported_name):
                    continue
                c.execute(
                    "INSERT INTO import_edges "
                    "(file, local_name, source_module, imported_name, line) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (file, local_name, source_module, imported_name,
                     imp.get("line", 0) or 0),
                )

        # Phase C: build bare-name index from full DB state — query covers
        # ALL nodes (prior batches + current), not just this batch, so calls
        # into functions defined in earlier-indexed files can resolve.
        bare_index: dict[str, list[tuple[int, str]]] = defaultdict(list)
        for nid, qname, name in c.execute(
            "SELECT id, qualified_name, name FROM nodes"
        ):
            bare = _bare_name(name)
            if bare:
                bare_index[bare].append((nid, qname))

        # Map (file, qname) -> caller_id for fast lookup
        caller_ids: dict[str, int] = {}
        for file, fn in node_meta:
            qname = self._qname(file, fn)
            row = c.execute(
                "SELECT id FROM nodes WHERE qualified_name=?", (qname,)
            ).fetchone()
            if row:
                caller_ids[qname] = row[0]

        # Phase D: emit edges
        stats = {
            "nodes": len(node_meta), "edges": 0,
            "exact": 0, "name_match": 0, "unresolved": 0,
            "dynamic": 0, "this_cross_file": 0,
            "import_resolved": 0, "import_ambiguous": 0,
        }
        for file, fn in node_meta:
            caller_id = caller_ids.get(self._qname(file, fn))
            if caller_id is None:
                continue
            for call in fn.get("calls", []) or []:
                if not isinstance(call, dict):
                    continue
                kind       = call.get("callee_kind")
                callee_raw = call.get("callee", "") or ""
                line       = call.get("line", 0) or 0
                raw        = call.get("raw", "") or ""

                # candidate_count tracks how many same-bare-name nodes
                # were candidates for this call. Tag is 1 for exact /
                # this_cross_file / unresolved / dynamic; >1 only when
                # the resolver had to pick one out of N name-shared
                # functions. Extract_chains filters by quality = 1/N.
                candidate_count = 1
                if kind == "dynamic":
                    callee_id, resolved = None, "dynamic"
                elif kind == "this":
                    method_name = _resolve_target(callee_raw, kind)
                    caller_row = c.execute(
                        "SELECT parent, file FROM nodes WHERE id=?", (caller_id,)
                    ).fetchone()
                    caller_parent = caller_row[0] or "" if caller_row else ""
                    caller_file   = caller_row[1] or "" if caller_row else ""
                    callee_id, resolved = _resolve_this_binding(
                        caller_parent, caller_file, method_name or "", self.conn
                    )
                    if callee_id is None and method_name:
                        matches = bare_index.get(method_name, [])
                        if len(matches) == 1:
                            callee_id, resolved = matches[0][0], "name_match"
                else:
                    target  = _resolve_target(callee_raw, kind or "")
                    matches = bare_index.get(target or "", [])
                    if not matches:
                        callee_id, resolved = None, "unresolved"
                    elif len(matches) == 1:
                        callee_id, resolved = matches[0][0], "exact"
                    else:
                        sorted_m = sorted(matches, key=lambda x: x[1])
                        callee_id, resolved = sorted_m[0][0], "name_match"
                        candidate_count = len(sorted_m)
                        self.ambiguities.append(
                            (callee_raw, [m[1] for m in sorted_m])
                        )

                cur = c.execute(
                    "INSERT OR IGNORE INTO edges "
                    "(caller_id, callee_id, line, raw, callee_raw, "
                    " resolved_kind, candidate_count) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (caller_id, callee_id, line, raw, callee_raw,
                     resolved, candidate_count),
                )
                if cur.rowcount > 0:
                    stats["edges"] += 1
                    stats[resolved] += 1

        # Phase D2: import-based repair pass.
        # Additive — only edges Phase D left as 'unresolved' with a bare-name
        # callee are reconsidered. Existing resolved_kind values are untouched.
        unresolved = c.execute(
            "SELECT e.caller_id, e.line, e.callee_raw, n.file "
            "FROM edges e JOIN nodes n ON n.id = e.caller_id "
            "WHERE e.resolved_kind='unresolved' AND e.callee_raw != ''"
        ).fetchall()

        for caller_id, edge_line, callee_raw, caller_file in unresolved:
            if not callee_raw or "." in callee_raw or callee_raw.startswith("<"):
                continue
            imp_row = c.execute(
                "SELECT source_module, imported_name FROM import_edges "
                "WHERE file=? AND local_name=?",
                (caller_file, callee_raw),
            ).fetchone()
            if not imp_row:
                continue
            source_module, imported_name = imp_row
            target_rel = _resolve_module_to_rel(
                caller_file, source_module, root_dir
            )
            if target_rel is None:
                continue
            if imported_name == "*":
                # Namespace import: bare local name shouldn't be called
                # directly — member calls (utils.fn()) are out of scope here.
                continue
            candidates = _candidate_files(target_rel)
            qmarks = ",".join("?" * len(candidates))
            if imported_name == "default":
                rows = c.execute(
                    f"SELECT id, qualified_name FROM nodes "
                    f"WHERE file IN ({qmarks}) AND kind='default_export'",
                    candidates,
                ).fetchall()
            else:
                rows = c.execute(
                    f"SELECT id, qualified_name FROM nodes "
                    f"WHERE file IN ({qmarks}) AND name=?",
                    candidates + [imported_name],
                ).fetchall()
            if not rows:
                continue
            if len(rows) == 1:
                new_id, new_kind = rows[0][0], "import_resolved"
            else:
                rows_sorted = sorted(rows, key=lambda r: r[1])
                new_id, new_kind = rows_sorted[0][0], "import_ambiguous"
                self.ambiguities.append(
                    (callee_raw, [r[1] for r in rows_sorted])
                )
            c.execute(
                "UPDATE edges SET callee_id=?, resolved_kind=? "
                "WHERE caller_id=? AND line=? AND callee_raw=?",
                (new_id, new_kind, caller_id, edge_line, callee_raw),
            )
            stats[new_kind] += 1
            stats["unresolved"] -= 1

        # Phase E: taxonomy tagging (optional)
        tag_stats = {"tags_sink": 0, "tags_source": 0,
                     "tags_high": 0, "tags_medium": 0, "tags_low": 0,
                     "tags_critical": 0}
        if taxonomy is not None and file_sources:
            tag_stats = self._tag_nodes(node_meta, caller_ids, taxonomy,
                                        file_sources, ast_tags_by_file)

        # Phase E2: template analysis for .vue / .html files
        if template_files:
            t_stats = self._tag_templates(template_files, taxonomy)
            for k, v in t_stats.items():
                tag_stats[k] = tag_stats.get(k, 0) + v

        # Phase F: persist extracted URLs
        for file, entry in ast_results.items():
            if not isinstance(entry, dict) or not entry.get("ok"):
                continue
            for rec in entry.get("extracted_urls", []) or []:
                if not isinstance(rec, dict):
                    continue
                fn_name = rec.get("in_function")
                qname   = f"{file}::{fn_name}" if fn_name else None
                c.execute(
                    "INSERT INTO url_refs "
                    "(file, url_template, type, method, query_params, "
                    " body_params, line, in_function) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        file,
                        rec.get("url", ""),
                        rec.get("type", "unknown"),
                        rec.get("method"),
                        json.dumps(rec.get("query_params") or []),
                        json.dumps(rec.get("body_params")  or []),
                        rec.get("line", 0),
                        qname,
                    ),
                )

        # Phase G: intra-procedural taint flows
        flow_count = 0
        for file, entry in ast_results.items():
            if not isinstance(entry, dict) or not entry.get("ok"):
                continue
            for fn in entry.get("functions", []) or []:
                if not isinstance(fn, dict):
                    continue
                qname = self._qname(file, fn)
                node_id = caller_ids.get(qname)
                if node_id is None:
                    continue
                taint_facts = fn.get("taint_facts") or []
                if not taint_facts:
                    continue
                flows = solve_function_taint(taint_facts)
                for flow in flows:
                    cur = c.execute(
                        "INSERT OR IGNORE INTO node_taint_flows "
                        "(node_id, source_rule, source_line, sink_rule, sink_line, "
                        " via_vars, sanitised_by, sanitiser_clears) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            node_id,
                            flow.get("source_rule", ""),
                            flow.get("source_line", 0),
                            flow.get("sink_rule", ""),
                            flow.get("sink_line", 0),
                            ",".join(flow.get("via_vars") or []),
                            flow.get("sanitised_by"),
                            "",
                        ),
                    )
                    if cur.rowcount > 0:
                        flow_count += 1

        # Phase H: variables + dataflow edges
        var_id_map: dict[tuple[int, str], int] = {}
        var_count = 0
        edge_count = 0
        for file, entry in ast_results.items():
            if not isinstance(entry, dict) or not entry.get("ok"):
                continue
            for fn in entry.get("functions", []) or []:
                if not isinstance(fn, dict):
                    continue
                qname = self._qname(file, fn)
                node_id = caller_ids.get(qname)
                if node_id is None:
                    continue
                for var_rec in fn.get("variables", []) or []:
                    name = var_rec.get("name")
                    if not name:
                        continue
                    first_line = var_rec.get("first_line", 0) or 0
                    cur = c.execute(
                        "INSERT OR IGNORE INTO variables "
                        "(node_id, name, first_line) VALUES (?, ?, ?)",
                        (node_id, name, first_line),
                    )
                    if cur.rowcount > 0:
                        var_count += 1
                    row = c.execute(
                        "SELECT id FROM variables WHERE node_id=? AND name=?",
                        (node_id, name),
                    ).fetchone()
                    if row:
                        var_id_map[(node_id, name)] = row[0]
                for edge_rec in fn.get("dataflow", []) or []:
                    from_name = edge_rec.get("from")
                    to_name   = edge_rec.get("to")
                    if not to_name:
                        continue
                    to_id = var_id_map.get((node_id, to_name))
                    if to_id is None:
                        continue
                    from_id = var_id_map.get((node_id, from_name)) if from_name else None
                    cur = c.execute(
                        "INSERT OR IGNORE INTO dataflow_edges "
                        "(from_var, to_var, edge_kind, line, sanitiser) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            from_id,
                            to_id,
                            edge_rec.get("edge_kind", "assign"),
                            edge_rec.get("line", 0) or 0,
                            edge_rec.get("sanitiser"),
                        ),
                    )
                    if cur.rowcount > 0:
                        edge_count += 1

        self.conn.commit()
        stats["ambiguities"] = len(self.ambiguities)
        stats.update(tag_stats)
        stats["taint_flows"]    = flow_count
        stats["variables"]      = var_count
        stats["dataflow_edges"] = edge_count
        return stats

    def _tag_nodes(
        self, node_meta, caller_ids, taxonomy, file_sources,
        ast_tags_by_file: dict[str, list[dict]] | None = None,
    ) -> dict:
        """Tag each node with sink/source matches in its source-line range.

        For rule IDs in AST_COVERED_RULE_IDS: use the ast_tags emitted by the
        extractor — position-accurate, no comment/string false positives.
        For other rule IDs: fall back to the existing regex path.
        """
        c = self.conn.cursor()
        line_cache: dict[str, list[str]] = {}
        stats = {"tags_sink": 0, "tags_source": 0, "tags_sanitizer": 0,
                "tags_high": 0, "tags_medium": 0, "tags_low": 0,
                "tags_critical": 0}

        severity_by_id: dict[str, str] = {}
        kind_by_id: dict[str, str] = {}
        if taxonomy is not None:
            for entry in taxonomy.entries:
                severity_by_id[entry["id"]] = entry["severity"]
                kind_by_id[entry["id"]]     = entry["kind"]

        ast_tags_by_file = ast_tags_by_file or {}

        for file, fn in node_meta:
            qname     = self._qname(file, fn)
            caller_id = caller_ids.get(qname)
            if caller_id is None:
                continue

            start = fn.get("start") or 0
            end   = fn.get("end")   or 0
            if start <= 0 or end < start:
                continue

            # ── AST path ─────────────────────────────────────────────────
            for tag in ast_tags_by_file.get(file, []):
                tag_line = tag.get("line", 0)
                # Bounds guard (Patch — coolblue showed 51% of historical
                # tags had lines outside their owning fn body). Reject
                # AST tags that don't claim a body-local line.
                if not (start <= tag_line <= end):
                    continue
                rule_id = tag.get("rule_id", "")
                if rule_id not in AST_COVERED_RULE_IDS:
                    continue
                severity = severity_by_id.get(rule_id, "medium")
                kind     = kind_by_id.get(rule_id) or tag.get("kind", "sink")
                cur = c.execute(
                    "INSERT OR IGNORE INTO node_tags "
                    "(node_id, taxonomy_id, kind, severity, line, source) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (caller_id, rule_id, kind, severity, tag_line, 'ast'),
                )
                if cur.rowcount > 0:
                    if kind == "sink":   stats["tags_sink"]   += 1
                    if kind == "source": stats["tags_source"] += 1
                    key = f"tags_{severity}"
                    if key in stats: stats[key] += 1

            # ── Regex path (unchanged for non-AST rules) ─────────────────
            if taxonomy is None:
                continue
            text = file_sources.get(file)
            if text is None:
                continue
            if file not in line_cache:
                line_cache[file] = text.splitlines()
            lines = line_cache[file]
            slice_ = lines[start - 1:end]
            if not slice_:
                continue

            # Skip regex pass on pathological minified-bundle slices.
            # A slice with a single mega-line (>100KB) is a minified
            # function body where regex backtracking can stall for
            # minutes (Patch — coolblue expand_snippet hang) AND any
            # match would be inside that one line, indistinguishable
            # at line granularity from neighbouring code.
            MAX_SLICE_LINE_LEN = 100_000
            if any(len(l) > MAX_SLICE_LINE_LEN for l in slice_):
                continue
            matches = taxonomy.match_lines(slice_)
            for m in matches:
                if m.id in AST_COVERED_RULE_IDS:
                    continue
                abs_line = (start - 1) + m.line
                # Bounds guard — never insert a tag whose line falls
                # outside the owning function's [start..end] body.
                # The combination above (slice_ comes from
                # lines[start-1:end], m.line in [1..len(slice_)]) means
                # abs_line should always satisfy this; the explicit
                # check defends against future indexer regressions.
                if not (start <= abs_line <= end):
                    continue
                cur = c.execute(
                    "INSERT OR IGNORE INTO node_tags "
                    "(node_id, taxonomy_id, kind, severity, line, source) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (caller_id, m.id, m.kind, m.severity, abs_line, 'regex'),
                )
                if cur.rowcount > 0:
                    if m.kind == "sink":   stats["tags_sink"]   += 1
                    if m.kind == "source": stats["tags_source"] += 1
                    key = f"tags_{m.severity}"
                    if key in stats: stats[key] += 1

            for m in matches:
                if m.kind != "sanitizer":
                    continue
                abs_line = (start - 1) + m.line
                entry = next((e for e in taxonomy.entries if e["id"] == m.id), None)
                clears = ",".join(entry.get("clears", [])) if entry else ""
                cur = c.execute(
                    "INSERT OR IGNORE INTO node_sanitizers "
                    "(node_id, taxonomy_id, line, clears) VALUES (?, ?, ?, ?)",
                    (caller_id, m.id, abs_line, clears),
                )
                if cur.rowcount > 0:
                    stats["tags_sanitizer"] += 1
        return stats

    def _tag_templates(self, template_files: dict, taxonomy) -> dict:
        """Run template_analyzer on each .vue / .html file and emit node_tags.

        A synthetic node ('<rel>::__template__') is created per file so the
        tag has a foreign-key target. `_purge_file` already cleared prior
        nodes for this file, so re-runs stay idempotent.
        """
        from modules.js_analyzer.template_analyzer import analyze_template

        stats = {"tags_sink": 0, "tags_source": 0,
                 "tags_high": 0, "tags_medium": 0, "tags_low": 0,
                 "tags_critical": 0, "tags_sanitizer": 0}
        if not template_files:
            return stats

        c = self.conn.cursor()
        sev_by_id: dict[str, str] = {}
        kind_by_id: dict[str, str] = {}
        if taxonomy is not None:
            for entry in taxonomy.entries:
                sev_by_id[entry["id"]] = entry["severity"]
                kind_by_id[entry["id"]] = entry["kind"]

        for rel, content in template_files.items():
            if not content:
                continue
            tags = analyze_template(rel, content, ACTIVE_FRAMEWORKS)
            if not tags:
                continue

            qname = f"{rel}::__template__"
            line_count = content.count("\n") + 1
            c.execute(
                "INSERT OR IGNORE INTO nodes "
                "(qualified_name, file, name, parent, kind, start_line, end_line, "
                " original_line, original_file) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (qname, rel, "__template__", None, "template",
                 1, line_count, None, None),
            )
            row = c.execute(
                "SELECT id FROM nodes WHERE qualified_name=?", (qname,),
            ).fetchone()
            if not row:
                continue
            node_id = row[0]

            for tag in tags:
                rule_id = tag.get("rule_id", "")
                if not rule_id:
                    continue
                kind     = kind_by_id.get(rule_id) or tag.get("kind", "sink")
                severity = sev_by_id.get(rule_id) or tag.get("severity", "high")
                line     = int(tag.get("line", 0) or 0)
                cur = c.execute(
                    "INSERT OR IGNORE INTO node_tags "
                    "(node_id, taxonomy_id, kind, severity, line, source) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (node_id, rule_id, kind, severity, line, 'template'),
                )
                if cur.rowcount > 0:
                    if kind == "sink":   stats["tags_sink"]   += 1
                    if kind == "source": stats["tags_source"] += 1
                    key = f"tags_{severity}"
                    if key in stats: stats[key] += 1
        return stats

    # ── query helpers (basic — full graph queries land in Task 5) ────────

    def node_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]

    def edge_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

    def find_node(self, qualified_name: str) -> dict | None:
        row = self.conn.execute(
            "SELECT id, qualified_name, file, name, parent, kind, "
            "       start_line, end_line, original_line, original_file "
            "FROM nodes WHERE qualified_name=?", (qualified_name,),
        ).fetchone()
        if not row:
            return None
        keys = ("id", "qualified_name", "file", "name", "parent",
                "kind", "start_line", "end_line", "original_line", "original_file")
        return dict(zip(keys, row))

    def callees_of(self, qualified_name: str) -> list[dict]:
        node = self.find_node(qualified_name)
        if not node:
            return []
        rows = self.conn.execute(
            "SELECT e.callee_raw, n.qualified_name, e.line, e.raw, e.resolved_kind "
            "FROM edges e LEFT JOIN nodes n ON n.id = e.callee_id "
            "WHERE e.caller_id=? ORDER BY e.line", (node["id"],),
        ).fetchall()
        return [
            {"callee_raw": r[0], "callee_qname": r[1],
             "line": r[2], "raw": r[3], "resolved_kind": r[4]}
            for r in rows
        ]

    def callers_of(self, qualified_name: str) -> list[dict]:
        node = self.find_node(qualified_name)
        if not node:
            return []
        rows = self.conn.execute(
            "SELECT n.qualified_name, e.line, e.raw, e.resolved_kind "
            "FROM edges e JOIN nodes n ON n.id = e.caller_id "
            "WHERE e.callee_id=? ORDER BY n.qualified_name, e.line", (node["id"],),
        ).fetchall()
        return [
            {"caller_qname": r[0], "line": r[1], "raw": r[2], "resolved_kind": r[3]}
            for r in rows
        ]

    def tag_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM node_tags").fetchone()[0]

    def this_binding_count(self) -> int:
        """Count edges resolved via class-aware this-binding (cross-file)."""
        r = self.conn.execute(
            "SELECT COUNT(*) FROM edges WHERE resolved_kind='this_cross_file'"
        ).fetchone()
        return r[0] if r else 0

    def tags_for(self, qualified_name: str) -> list[dict]:
        node = self.find_node(qualified_name)
        if not node:
            return []
        rows = self.conn.execute(
            "SELECT taxonomy_id, kind, severity, line FROM node_tags "
            "WHERE node_id=? ORDER BY line, taxonomy_id", (node["id"],),
        ).fetchall()
        return [
            {"taxonomy_id": r[0], "kind": r[1], "severity": r[2], "line": r[3]}
            for r in rows
        ]

    def stats(self) -> dict:
        rows = dict(self.conn.execute(
            "SELECT resolved_kind, COUNT(*) FROM edges GROUP BY resolved_kind"
        ).fetchall())
        tag_kinds = dict(self.conn.execute(
            "SELECT kind, COUNT(*) FROM node_tags GROUP BY kind"
        ).fetchall())
        return {
            "nodes":       self.node_count(),
            "edges":       self.edge_count(),
            "exact":       rows.get("exact", 0),
            "name_match":  rows.get("name_match", 0),
            "unresolved":  rows.get("unresolved", 0),
            "dynamic":     rows.get("dynamic", 0),
            "this_cross_file":   rows.get("this_cross_file", 0),
            "import_resolved":   rows.get("import_resolved", 0),
            "import_ambiguous":  rows.get("import_ambiguous", 0),
            "tags_sink":   tag_kinds.get("sink", 0),
            "tags_source": tag_kinds.get("source", 0),
        }
