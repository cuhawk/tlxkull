"""V2 schema migration — adds 8 new tables for plans/ARCHITECTURE_EVOLUTION_V2.md.

All tables are additive. None of them are required for V1 pipeline to
run. Migration is idempotent: every CREATE / INDEX is `IF NOT EXISTS`.

Single point of truth for V2 schema. `bin/migrate_db.py` calls
``apply(conn)`` against per-target snapshots AND the global
``~/.tlx/js_analyzer.db`` when the user opts in.

Tables:
  storage_events       (§11)
  storage_edges_view   (§11 — view over storage_events)
  node_provenance      (§12)
  global_reads         (§13)
  clobber_candidates   (§13)
  implicit_lookups     (§14)
  pp_gadgets           (§14)
  sink_contexts        (§15)
  sink_lifecycle       (§22)
  auth_state_nodes     (§23)
  v2_meta              (migration bookkeeping)

`v2_meta` records the schema_version applied so later migrations can
detect skew without re-running.
"""
from __future__ import annotations

import sqlite3
from typing import Final

V2_SCHEMA_VERSION: Final = 4

V2_SCHEMA: Final = """
-- §11 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS storage_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         INTEGER NOT NULL,
    api             TEXT NOT NULL,
    op              TEXT NOT NULL,
    key_static      TEXT,
    key_dynamic     TEXT,
    key_provenance  TEXT,
    value_node      INTEGER,
    is_secret_hint  INTEGER NOT NULL DEFAULT 0,
    phase           TEXT,
    file            TEXT NOT NULL,
    line            INTEGER,
    framework_hint  TEXT,
    UNIQUE (node_id, api, op, line)
);
CREATE INDEX IF NOT EXISTS idx_storage_key ON storage_events(key_static, op);
CREATE INDEX IF NOT EXISTS idx_storage_api ON storage_events(api, op);
CREATE INDEX IF NOT EXISTS idx_storage_file ON storage_events(file);

-- §12 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS node_provenance (
    node_id              INTEGER PRIMARY KEY,
    origin_label         TEXT NOT NULL,
    channel              TEXT NOT NULL,
    validation_kind      TEXT,
    validation_expr_node INTEGER,
    bypass_classes       TEXT,
    confidence           REAL NOT NULL DEFAULT 0.8
);
CREATE INDEX IF NOT EXISTS idx_provenance_channel ON node_provenance(channel);
CREATE INDEX IF NOT EXISTS idx_provenance_origin  ON node_provenance(origin_label);

-- §13 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS global_reads (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id       INTEGER NOT NULL,
    global_name   TEXT NOT NULL,
    access_path   TEXT NOT NULL,
    unguarded     INTEGER NOT NULL DEFAULT 1,
    consumer_kind TEXT,
    consumer_node INTEGER,
    file          TEXT NOT NULL,
    line          INTEGER
);
CREATE INDEX IF NOT EXISTS idx_global_reads_name ON global_reads(global_name);
CREATE INDEX IF NOT EXISTS idx_global_reads_node ON global_reads(node_id);

CREATE TABLE IF NOT EXISTS clobber_candidates (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    html_sink_node           INTEGER NOT NULL,
    html_sink_attrs_allowed  TEXT,
    global_read_id           INTEGER NOT NULL REFERENCES global_reads(id),
    gadget_shape             TEXT NOT NULL,
    reachability_score       REAL,
    source_chain_id          TEXT
);
CREATE INDEX IF NOT EXISTS idx_clobber_sink ON clobber_candidates(html_sink_node);

-- §14 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS implicit_lookups (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id           INTEGER NOT NULL,
    object_origin     TEXT,
    key_kind          TEXT NOT NULL,
    key_value         TEXT,
    has_default       INTEGER NOT NULL DEFAULT 0,
    has_typeof_guard  INTEGER NOT NULL DEFAULT 0,
    consumer_kind     TEXT,
    consumer_node     INTEGER,
    file              TEXT NOT NULL,
    line              INTEGER
);
CREATE INDEX IF NOT EXISTS idx_implicit_lookups_node ON implicit_lookups(node_id);
CREATE INDEX IF NOT EXISTS idx_implicit_lookups_key  ON implicit_lookups(key_value);

CREATE TABLE IF NOT EXISTS pp_gadgets (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    framework     TEXT NOT NULL,
    version_range TEXT,
    key_path      TEXT NOT NULL,
    gadget_kind   TEXT NOT NULL,
    rationale     TEXT,
    confidence    REAL NOT NULL DEFAULT 0.8
);
CREATE INDEX IF NOT EXISTS idx_pp_gadgets_framework ON pp_gadgets(framework);

-- §15 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sink_contexts (
    node_id          INTEGER PRIMARY KEY,
    context_class    TEXT NOT NULL,
    encoding_state   TEXT NOT NULL,
    execution_viable TEXT NOT NULL,
    rationale        TEXT
);
CREATE INDEX IF NOT EXISTS idx_sink_contexts_class ON sink_contexts(context_class);

-- §22 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sink_lifecycle (
    node_id                INTEGER PRIMARY KEY,
    framework              TEXT NOT NULL,
    lifecycle_phase        TEXT NOT NULL,
    attacker_can_trigger   INTEGER NOT NULL DEFAULT 1
);

-- §23 ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auth_state_nodes (
    node_id        INTEGER PRIMARY KEY,
    role           TEXT NOT NULL,
    source         TEXT NOT NULL,
    framework      TEXT,
    trust          REAL NOT NULL,
    derives_from   INTEGER,
    consumer_node  INTEGER
);
CREATE INDEX IF NOT EXISTS idx_auth_state_role ON auth_state_nodes(role);

-- V1 §2 ─ Property shapes + string lattice (schema_version >= 4) ────
CREATE TABLE IF NOT EXISTS prop_shapes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         INTEGER NOT NULL,        -- function in which the shape lives
    base_var        TEXT NOT NULL,           -- e.g. "sinkMap"
    line            INTEGER NOT NULL,
    shape_kind      TEXT NOT NULL,           -- object_literal | class_inst | param | import | unknown
    keys_json       TEXT,                    -- JSON list of known string keys
    keys_confidence REAL NOT NULL,
    closed          INTEGER NOT NULL,        -- 1 iff no dynamic add observed
    evidence_lines  TEXT,                    -- JSON list of seed lines
    UNIQUE (node_id, base_var, line)
);
CREATE INDEX IF NOT EXISTS idx_prop_shapes_base ON prop_shapes(base_var);
CREATE INDEX IF NOT EXISTS idx_prop_shapes_node ON prop_shapes(node_id);

CREATE TABLE IF NOT EXISTS string_facts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         INTEGER NOT NULL,
    var_name        TEXT NOT NULL,
    level           TEXT NOT NULL,           -- top | const | set
    values_json     TEXT,                    -- JSON list when level in (const, set)
    line            INTEGER,
    UNIQUE (node_id, var_name, line)
);
CREATE INDEX IF NOT EXISTS idx_string_facts_node ON string_facts(node_id);

-- V1 §9 ─ Trusted Types policy analysis (schema_version >= 3) ──────
CREATE TABLE IF NOT EXISTS tt_policies (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id             INTEGER NOT NULL,
    policy_name         TEXT,
    handler             TEXT NOT NULL,        -- 'createHTML' | 'createScript' | 'createScriptURL'
    body_class          TEXT NOT NULL,        -- 'identity' | 'regex_only' | 'substring_check' | 'dompurify' | 'sanitize_html' | 'string_replace' | 'unknown' | 'reject_all'
    block_p             REAL NOT NULL,        -- effective P(blocks) in [0, 1]
    rationale           TEXT,
    file                TEXT,
    line                INTEGER,
    UNIQUE (node_id, handler)
);
CREATE INDEX IF NOT EXISTS idx_tt_policies_handler ON tt_policies(handler);

-- V1 §10 ─ Incremental recomputation (additive; schema_version >= 2) ─
CREATE TABLE IF NOT EXISTS node_hashes (
    node_id          INTEGER PRIMARY KEY,
    body_sha256      TEXT NOT NULL,
    deps_sha256      TEXT NOT NULL,
    last_indexed_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_node_hashes_body ON node_hashes(body_sha256);

CREATE TABLE IF NOT EXISTS taint_cache (
    node_id        INTEGER PRIMARY KEY,
    flows_json     TEXT NOT NULL,
    cache_sha256   TEXT NOT NULL,
    valid          INTEGER NOT NULL DEFAULT 1,
    cached_at      REAL NOT NULL DEFAULT (strftime('%s', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_taint_cache_valid ON taint_cache(valid);

-- Bookkeeping ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS v2_meta (
    schema_version INTEGER NOT NULL,
    applied_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def apply(conn: sqlite3.Connection) -> int:
    """Apply V2 schema to *conn*. Idempotent. Returns the schema_version.

    Caller owns the connection lifecycle. Commit is the caller's choice
    (so callers can wrap multi-step migrations in a single transaction).
    """
    cur = conn.cursor()
    cur.executescript(V2_SCHEMA)
    cur.execute("SELECT MAX(schema_version) FROM v2_meta")
    row = cur.fetchone()
    current = row[0] if row and row[0] is not None else 0
    if current < V2_SCHEMA_VERSION:
        cur.execute(
            "INSERT INTO v2_meta (schema_version) VALUES (?)",
            (V2_SCHEMA_VERSION,),
        )
    return V2_SCHEMA_VERSION


def current_version(conn: sqlite3.Connection) -> int:
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(schema_version) FROM v2_meta")
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else 0
    except sqlite3.OperationalError:
        return 0
