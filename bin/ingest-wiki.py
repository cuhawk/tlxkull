"""One-shot: ingest wiki/sources/ + wiki/techniques/ into TLX `wiki` Chroma collection.

Run with the tlx venv: `tlx/.venv/bin/python bin/ingest-wiki.py`
Requires GOOGLE_API_KEY in env (text-embedding-004).
"""
import asyncio
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TLX = REPO / "tlx"
sys.path.insert(0, str(TLX))

from modules.rag.module import DocsConfig
from modules.rag.tools import docs_ingest_dir
from kernel.embedders.google import GoogleEmbedder
from kernel.embedders.chroma_adapter import make_chroma_adapter


async def main() -> None:
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    cfg = DocsConfig(collection="wiki")
    embedder = GoogleEmbedder()
    ef = make_chroma_adapter(embedder)

    targets = [
        (str(REPO / "wiki" / "sources"), "*.md"),
        (str(REPO / "wiki" / "sources" / "podcasts" / "ct"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "dom-xss"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "idor"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "oauth"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "postmessage"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "prototype-pollution"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "race-conditions"), "*.md"),
        (str(REPO / "wiki" / "techniques" / "server-side"), "*.md"),
        (str(REPO / "wiki" / "payloads" / "dom-xss"), "*.md"),
        (str(REPO / "wiki" / "tools"), "**/*.md"),
        (str(REPO / "wiki"), "SCHEMA.md"),
    ]

    for directory, glob in targets:
        if not Path(directory).exists():
            print(f"SKIP (missing): {directory}")
            continue
        print(f"INGEST {directory} {glob}")
        try:
            result = await docs_ingest_dir(
                directory=directory,
                glob=glob,
                collection="wiki",
                cfg=cfg,
                embedding_function=ef,
            )
            print(f"  -> {result}")
        except Exception as exc:
            print(f"  ERROR: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
