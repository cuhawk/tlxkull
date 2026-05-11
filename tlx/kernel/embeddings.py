"""Embedder Protocol + factory.

Kernel-level embedding abstraction. Two backends:
  - google: text-embedding-004 (768d). Default. Requires GOOGLE_API_KEY.
  - local : chromadb ONNX all-MiniLM-L6-v2 (384d). No API key.

Wrapped in a SQLite cache (~/.tlx/embedding.db) keyed by (sha256, model).

Backend choice: env TLX_EMBEDDER overrides cfg.embedder ("google" default).
"""
from __future__ import annotations

import os
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Embedder(Protocol):
    model_id: str

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


def make_embedder(cfg: Any) -> Embedder:
    """Resolve backend, wrap in cache layer, return the cached Embedder."""
    name = os.environ.get("TLX_EMBEDDER") or getattr(cfg, "embedder", "google")
    name = name.strip().lower()

    if name == "local":
        from kernel.embedders.local import LocalEmbedder
        backend: Embedder = LocalEmbedder()
    elif name == "google":
        from kernel.embedders.google import GoogleEmbedder
        backend = GoogleEmbedder()
    else:
        raise ValueError(f"unknown embedder backend: {name!r}")

    from kernel.embedders.cache import CachedEmbedder
    return CachedEmbedder(backend)
