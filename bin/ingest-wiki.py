"""One-shot: ingest wiki/sources/ + wiki/techniques/ into TLX `wiki` Chroma collection.

Run with the tlx venv: `tlx/.venv/bin/python bin/ingest-wiki.py`
Requires GOOGLE_API_KEY in env (text-embedding-004).
"""
import asyncio
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TLX = REPO / "tlx"
sys.path.insert(0, str(TLX))

from modules.rag.module import DocsConfig
from modules.rag.tools import docs_ingest_dir, docs_ingest
from kernel.embedders.google import GoogleEmbedder
from kernel.embedders.chroma_adapter import make_chroma_adapter

_EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "_external"}


async def ingest_large_dir(
    directory: str, glob: str, cfg, ef, concurrency: int = 12
) -> tuple[int, int]:
    """Ingest a directory with >200 files using concurrent docs_ingest calls."""
    dir_path = Path(directory)
    paths = sorted(
        p for p in dir_path.glob(glob)
        if p.is_file() and not any(part in _EXCLUDE_DIRS for part in p.parts)
    )
    sem = asyncio.Semaphore(concurrency)
    counters = {"files": 0, "chunks": 0, "done": 0, "total": len(paths)}

    async def _ingest_one(p: Path) -> None:
        async with sem:
            raw = await docs_ingest(str(p), "wiki", cfg, ef)
            r = json.loads(raw)
            if "error" not in r:
                counters["files"] += 1
                counters["chunks"] += r.get("ingested", 0)
            counters["done"] += 1
            if counters["done"] % 100 == 0:
                print(
                    f"  [{counters['done']}/{counters['total']}] "
                    f"files={counters['files']} chunks={counters['chunks']}"
                )

    await asyncio.gather(*(_ingest_one(p) for p in paths))
    return counters["files"], counters["chunks"]


async def main() -> None:
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    cfg = DocsConfig(collection="wiki")
    embedder = GoogleEmbedder()
    ef = make_chroma_adapter(embedder)

    # Recursive globs cover every existing + future subclass folder.
    # _external/ is intentionally excluded (vendored OSS; license + noise).
    # wiki root *.md kept narrow (SCHEMA only) so _lint_*.md and
    # _ingest_log.jsonl never enter the collection.
    targets = [
        (str(REPO / "wiki" / "sources"), "*.md"),
        (str(REPO / "wiki" / "sources" / "hacktivity"), "*.md"),  # large: uses per-file path
        (str(REPO / "wiki" / "sources" / "podcasts" / "ct"), "*.md"),
        (str(REPO / "wiki" / "sources" / "blogs"), "**/*.md"),
        (str(REPO / "wiki" / "techniques"), "**/*.md"),
        (str(REPO / "wiki" / "payloads"), "**/*.md"),
        (str(REPO / "wiki" / "tools"), "**/*.md"),
        (str(REPO / "wiki" / "findings"), "**/*.md"),
        (str(REPO / "wiki" / "people"), "**/*.md"),
        (str(REPO / "wiki" / "targets"), "**/*.md"),
        (str(REPO / "wiki"), "SCHEMA.md"),
    ]

    for directory, glob in targets:
        if not Path(directory).exists():
            print(f"SKIP (missing): {directory}")
            continue
        print(f"INGEST {directory} {glob}")
        try:
            # Count files first to decide path
            dir_path = Path(directory)
            file_count = sum(
                1 for p in dir_path.glob(glob)
                if p.is_file() and not any(part in _EXCLUDE_DIRS for part in p.parts)
            )
            if file_count > 200:
                files, chunks = await ingest_large_dir(directory, glob, cfg, ef)
                print(f"  -> files={files} chunks={chunks}")
                continue

            raw = await docs_ingest_dir(
                directory=directory,
                glob=glob,
                collection="wiki",
                cfg=cfg,
                embedding_function=ef,
            )
            r = json.loads(raw)
            if "error" in r:
                print(f"  ERR: {r['error']}")
                continue
            print(
                f"  -> files={r.get('files_processed')} "
                f"chunks={r.get('total_chunks')}"
            )
        except Exception as exc:
            print(f"  EX: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
