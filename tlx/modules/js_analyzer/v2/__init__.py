"""TLX JS Analyzer V2 subsystems.

Each module in this package implements one section of
``plans/ARCHITECTURE_EVOLUTION_V2.md`` (§11 through §24). All subsystems
are additive: they ship behind a feature flag in
``js_analyzer_config.py`` and degrade to a no-op when disabled.

Public surface is exposed via ``v2.run_enabled_stages(conn, target_dir)``
which inspects the env flags and invokes only the enabled subsystems.
Each subsystem returns a small ``dict`` of stats.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

__all__ = [
    "run_enabled_stages",
    "enabled_stages",
    "SCHEMA_VERSION",
]


SCHEMA_VERSION = "v2.1"


def enabled_stages() -> dict[str, bool]:
    """Snapshot of which V2 stages are turned on right now."""
    from modules.js_analyzer.js_analyzer_config import v2_summary
    return v2_summary()


def run_enabled_stages(
    conn: sqlite3.Connection,
    target_dir: str | Path,
    *,
    only: list[str] | None = None,
) -> dict[str, Any]:
    """Run every enabled V2 stage against the per-target DB.

    Args:
        conn:        Open SQLite connection to ``targets/<name>/db/js_analyzer.db``.
        target_dir:  Path to ``targets/<name>``.
        only:        Optional whitelist; only run stages whose key is in this list.

    Returns:
        ``{stage_name: stats_dict_or_error}`` for every stage attempted.
    """
    stages_enabled = enabled_stages()
    results: dict[str, Any] = {}

    # Import lazily so an import error in one stage doesn't break the rest.
    stage_map = {
        "parser_context":          ("modules.js_analyzer.v2.parser_context",          "run"),
        "persistent_taint":        ("modules.js_analyzer.v2.persistent_taint",        "run"),
        "origin_trust":            ("modules.js_analyzer.v2.origin_trust",            "run"),
        "dom_clobber":             ("modules.js_analyzer.v2.dom_clobber",             "run"),
        "pp_gadgets":              ("modules.js_analyzer.v2.pp_gadgets",              "run"),
        "deobfuscation_normalize": ("modules.js_analyzer.v2.deobfuscation_normalize", "run"),
        "corpus_patterns":         ("modules.js_analyzer.v2.corpus_patterns",         "run"),
        "sink_reachability":       ("modules.js_analyzer.v2.sink_reachability",       "run"),
        "auth_abuse":              ("modules.js_analyzer.v2.auth_abuse",              "run"),
        "worker_semantics":        ("modules.js_analyzer.v2.worker_semantics",        "run"),
        # Compression / delta / multi-target / query_dsl have non-DB
        # surfaces and are invoked elsewhere; skip here.
    }
    for stage, (modpath, fnname) in stage_map.items():
        if only is not None and stage not in only:
            continue
        if not stages_enabled.get(stage, False):
            continue
        try:
            mod = __import__(modpath, fromlist=[fnname])
            fn = getattr(mod, fnname)
            results[stage] = fn(conn, target_dir)
        except Exception as exc:        # pragma: no cover - defensive
            results[stage] = {"error": str(exc), "type": exc.__class__.__name__}

    return {
        "schema_version": SCHEMA_VERSION,
        "stages": results,
        "stages_enabled_snapshot": stages_enabled,
    }
