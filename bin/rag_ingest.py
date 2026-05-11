#!/usr/bin/env python3
"""Ingest a directory of source files into a TLX docs ChromaDB collection.

The `tlx` MCP exposes `docs_query` but not the ingest path. This script
boots a kernel in mcp surface, resolves the docs module's ingest path
through the registered service, and walks <sources_dir> file-by-file.

Usage:
  GOOGLE_API_KEY=... python bin/rag_ingest.py <collection_name> <sources_dir>

Run from the repository root (so the `tlx` subpackage imports resolve).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

# Make the vendored tlx subset importable.
ROOT = Path(__file__).resolve().parents[1]
TLX = ROOT / "tlx"
sys.path.insert(0, str(TLX))


SUPPORTED_TEXT_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
                      ".json", ".md", ".html", ".css", ".vue", ".svelte"}


async def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    collection = sys.argv[1]
    sources_dir = Path(sys.argv[2]).resolve()
    if not sources_dir.is_dir():
        print(f"sources_dir not found: {sources_dir}", file=sys.stderr)
        return 2
    if not os.environ.get("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY env var is required for the embedder.", file=sys.stderr)
        return 2

    # Imports happen after sys.path tweak.
    from kernel import Kernel  # noqa: E402
    from kernel.config import load_config  # noqa: E402

    cfg = load_config()
    kernel = await Kernel.boot(config=cfg, surface="mcp")

    try:
        # Resolve docs module ingest path. The docs module registers a
        # "docs" service exposing collection helpers.
        docs_svc = (kernel.services.get("rag")
                    or kernel.services.get("docs")            # legacy name
                    or kernel.services.get("docs_module"))    # legacy name
        if docs_svc is None:
            # Fallback: use chromadb client directly with the kernel embedder.
            return await _direct_ingest(kernel, collection, sources_dir)
        # Service-provided ingest (preferred). Signature may differ across
        # TLX versions; we try the most likely shape and fall back.
        if hasattr(docs_svc, "ingest_directory"):
            stats = await docs_svc.ingest_directory(collection, sources_dir)
        elif hasattr(docs_svc, "add_files"):
            files = [p for p in sources_dir.rglob("*")
                     if p.is_file() and p.suffix.lower() in SUPPORTED_TEXT_EXT]
            stats = await docs_svc.add_files(collection, files)
        else:
            return await _direct_ingest(kernel, collection, sources_dir)
        print(json.dumps(stats, default=str, indent=2))
    finally:
        kernel.shutdown()
    return 0


async def _direct_ingest(kernel, collection: str, sources_dir: Path) -> int:
    """Chromadb-direct fallback if docs module doesn't expose ingest."""
    import chromadb  # noqa: E402
    embedder = kernel.services.get("embedder")
    if embedder is None:
        print("No embedder service registered; cannot ingest.", file=sys.stderr)
        return 3

    persist = Path(os.path.expanduser("~/.tlx/chroma"))
    persist.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist))

    coll = client.get_or_create_collection(name=collection)

    files = [p for p in sources_dir.rglob("*")
             if p.is_file() and p.suffix.lower() in SUPPORTED_TEXT_EXT]
    n_files = 0
    n_chunks = 0
    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        chunks = _chunk(text, max_chars=4000, overlap=400)
        if not chunks:
            continue
        rel = str(p.relative_to(sources_dir))
        # ids are content-hash + chunk index to keep idempotency.
        ids, docs, metas = [], [], []
        for i, ch in enumerate(chunks):
            cid = hashlib.sha256(f"{rel}:{i}:{ch[:64]}".encode()).hexdigest()[:24]
            ids.append(cid)
            docs.append(ch)
            metas.append({"path": rel, "chunk": i})
        embeddings = await embedder.embed(docs)
        coll.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
        n_files += 1
        n_chunks += len(chunks)

    print(json.dumps({"collection": collection, "files": n_files,
                      "chunks": n_chunks, "mode": "direct_fallback"}, indent=2))
    return 0


def _chunk(text: str, max_chars: int = 4000, overlap: int = 400) -> list[str]:
    if not text:
        return []
    out = []
    i = 0
    while i < len(text):
        out.append(text[i:i + max_chars])
        i += max_chars - overlap
    return out


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
