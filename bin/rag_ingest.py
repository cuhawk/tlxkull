#!/usr/bin/env python3
"""Ingest a directory of source files into a TLX RAG ChromaDB collection.

Boots the TLX kernel in `mcp` surface, resolves the `rag` service, and
calls `ingest_directory(collection, sources_dir)`. The service walks the
directory, chunks supported file types, and embeds through the kernel's
cached Google embedder (sha256 cache, throttled, 429-retry).

Usage:
  GOOGLE_API_KEY=... python bin/rag_ingest.py <collection_name> <sources_dir>

Run from the repository root (so the `tlx` subpackage imports resolve).

Throttle env vars (consumed by the GoogleEmbedder backend):
  TLX_EMBED_BATCH_SLEEP        seconds between 100-chunk batches (default 6.0)
  TLX_EMBED_MAX_429_RETRIES    backoff retries on RESOURCE_EXHAUSTED (default 5)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# Make the vendored tlx subset importable.
ROOT = Path(__file__).resolve().parents[1]
TLX = ROOT / "tlx"
sys.path.insert(0, str(TLX))


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

    from kernel import Kernel  # noqa: E402
    from kernel.config import load_config  # noqa: E402

    cfg = load_config()
    kernel = await Kernel.boot(config=cfg, surface="mcp")

    try:
        rag = kernel.services.get("rag")
        if rag is None or not hasattr(rag, "ingest_directory"):
            print(
                "rag service not registered or missing ingest_directory. "
                "Check that the `rag` module is enabled in tlx config and "
                "that `tlx/modules/rag/module.py` loaded cleanly.",
                file=sys.stderr,
            )
            return 3
        stats = await rag.ingest_directory(collection, sources_dir)
        print(json.dumps(stats, default=str, indent=2))
    finally:
        kernel.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
