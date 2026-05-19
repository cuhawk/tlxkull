"""Framework adapter registry.

Plan: plans/ARCHITECTURE_EVOLUTION.md §6.

Each adapter implements three hooks:
  patch_tags(conn) -> int          # framework-aware tag rows added
  rewrite_edges(conn) -> int       # virtual continuation edges added
  adjust_viability(chain, ctx)     # multiplier for chain viability

The registry maps lowercased framework names → adapter modules. Loaded
lazily: ``get(name)`` returns None when the adapter isn't shipped.
Callers should treat absence as "no adjustment".
"""
from __future__ import annotations

import importlib
import sqlite3
from typing import Protocol


__all__ = ["FrameworkAdapter", "get", "all_names"]


class FrameworkAdapter(Protocol):
    name: str

    def patch_tags(self, conn: sqlite3.Connection) -> int: ...
    def rewrite_edges(self, conn: sqlite3.Connection) -> int: ...
    def adjust_viability(self, chain: dict, ctx) -> float: ...


_REGISTRY = {
    "react":    "modules.js_analyzer.frameworks.react",
    "preact":   "modules.js_analyzer.frameworks.react",
    "next":     "modules.js_analyzer.frameworks.nextjs",
    "nextjs":   "modules.js_analyzer.frameworks.nextjs",
    "vue":      "modules.js_analyzer.frameworks.vue",
    "nuxt":     "modules.js_analyzer.frameworks.vue",
    "angular":  "modules.js_analyzer.frameworks.angular",
    "svelte":   "modules.js_analyzer.frameworks.svelte",
    "sveltekit": "modules.js_analyzer.frameworks.svelte",
}


def get(name: str) -> FrameworkAdapter | None:
    """Return an adapter for ``name`` (case-insensitive) or None."""
    if not name:
        return None
    mod_path = _REGISTRY.get(name.lower())
    if mod_path is None:
        return None
    try:
        mod = importlib.import_module(mod_path)
    except Exception:
        return None
    if not hasattr(mod, "adapter"):
        return None
    return mod.adapter  # type: ignore[no-any-return]


def all_names() -> list[str]:
    return sorted(set(_REGISTRY.keys()))
