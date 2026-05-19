"""V2 §16 — Obfuscation-aware normalization layer.

Lightweight passes that record (do not mutate) obfuscation evidence so
downstream queries can apply confidence adjustments. Heavy AST-level
normalization (cfg unflatten, full alias resolution) is out of scope
for this MVP; we ship the evidence layer + string-unfold detection.

Off by default; ``JS_ENABLE_DEOBFUSCATION_NORMALIZE=1`` to enable.

Output:
- table ``obfuscation_evidence`` keyed by node_id
- sidecar ``obfuscation_report.json``
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from modules.js_analyzer.v2._common import (
    clear_table,
    exec_ddl,
    load_node_meta,
    write_sidecar,
)

__all__ = ["run"]


_CREATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS obfuscation_evidence (
    id INTEGER PRIMARY KEY,
    node_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
        -- 'string_unfold' | 'wrapper_alias' | 'dead_branch'
        -- | 'flattened_cfg' | 'runtime_decoder' | 'constant_assembly'
    detail TEXT,
    file TEXT,
    line INTEGER
);
CREATE INDEX IF NOT EXISTS idx_obf_kind ON obfuscation_evidence(kind);
"""


_STRING_UNFOLD_RE = re.compile(r"(?:\\x[0-9a-fA-F]{2}|\\u[0-9a-fA-F]{4}){3,}")
_WRAPPER_ALIAS_RE = re.compile(
    r"\b(?:var|let|const)\s+([A-Za-z_$][\w$]*)\s*=\s*"
    r"(?:innerHTML|outerHTML|eval|setTimeout|setInterval|Function)\b",
)
_DEAD_BRANCH_RE = re.compile(
    r"if\s*\(\s*(?:false|0|!\s*1|!\s*['\"`][^'\"`]*['\"`]\s*===\s*['\"`][^'\"`]*['\"`])\s*\)",
)
_FLATTENED_CFG_RE = re.compile(
    r"while\s*\(\s*!!\s*\[\s*\]\s*\)|switch\s*\(\s*[a-zA-Z_$][\w$]*\s*\)\s*\{(?:\s*case\s+['\"`]\d+['\"`]\s*:[^{}]{0,400}){5,}",
)
_RUNTIME_DECODER_RE = re.compile(
    r"\batob\s*\(\s*['\"`][A-Za-z0-9+/=]{12,}['\"`]\s*\)"
    r"|\bdecodeURIComponent\s*\(\s*['\"`][^'\"`]{20,}['\"`]\s*\)",
)
_CONSTANT_ASSEMBLY_RE = re.compile(
    r"(?:['\"`][a-zA-Z]{2,8}['\"`]\s*\+\s*){2,}['\"`][a-zA-Z]{2,8}['\"`]",
)


def _detectors() -> list[tuple[str, re.Pattern]]:
    return [
        ("string_unfold",      _STRING_UNFOLD_RE),
        ("wrapper_alias",      _WRAPPER_ALIAS_RE),
        ("dead_branch",        _DEAD_BRANCH_RE),
        ("flattened_cfg",      _FLATTENED_CFG_RE),
        ("runtime_decoder",    _RUNTIME_DECODER_RE),
        ("constant_assembly",  _CONSTANT_ASSEMBLY_RE),
    ]


def run(conn: sqlite3.Connection, target_dir: str | Path) -> dict:
    exec_ddl(conn, _CREATE_SCHEMA)
    clear_table(conn, "obfuscation_evidence")

    meta = load_node_meta(conn)
    detectors = _detectors()
    inserted = 0
    by_kind: dict[str, int] = {}

    for caller_id, line, raw in conn.execute(
        "SELECT caller_id, line, raw FROM edges WHERE raw IS NOT NULL"
    ):
        if not raw:
            continue
        node = meta.get(caller_id, {})
        for kind, pat in detectors:
            m = pat.search(raw)
            if not m:
                continue
            conn.execute(
                "INSERT INTO obfuscation_evidence "
                "(node_id, kind, detail, file, line) VALUES (?,?,?,?,?)",
                (caller_id, kind, m.group(0)[:120],
                 node.get("file", ""), int(line or 0)),
            )
            inserted += 1
            by_kind[kind] = by_kind.get(kind, 0) + 1
    conn.commit()

    sidecar = {
        "rows_inserted": inserted,
        "by_kind": by_kind,
        "advice": _advice(by_kind),
    }
    write_sidecar(target_dir, "obfuscation_report.json", sidecar)
    return sidecar


def _advice(by_kind: dict[str, int]) -> list[str]:
    tips: list[str] = []
    if by_kind.get("flattened_cfg", 0) >= 5:
        tips.append("control-flow flattening detected; manual review of switch-state nodes recommended")
    if by_kind.get("wrapper_alias", 0) >= 5:
        tips.append("wrapper aliases of dangerous primitives detected; expand implicit-tags decay if missed")
    if by_kind.get("runtime_decoder", 0) >= 5:
        tips.append("base64/decode decoders detected; consider running runtime augmentation when available")
    return tips
