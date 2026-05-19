"""RAG module — semantic search over local files via Chroma.

Renamed from `docs` to `rag` (folder + module identifier). Tool names
(`docs_query`, `docs_ingest`, `docs_list`, `docs_ingest_dir`) are the
public MCP API surface and are kept unchanged for backward compatibility
with the allowlist + skill wiring.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel

from kernel.modules import ModuleSpec, RegisteredModule
from kernel.tools import Tool

# Bulk-ingest service file walk: matches what bin/rag_ingest.py needs.
_SUPPORTED_TEXT_EXT = frozenset({
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".json", ".md", ".html", ".css", ".vue", ".svelte",
    ".txt",
})
_EXCLUDE_DIRS_SERVICE = frozenset({
    "node_modules", ".git", ".next", "dist", "build",
    "__pycache__", ".venv", "venv", ".tox", "coverage",
})


def _chunk_chars(text: str, max_chars: int = 4000, overlap: int = 400) -> list[str]:
    if not text:
        return []
    out: list[str] = []
    step = max_chars - overlap
    i = 0
    while i < len(text):
        out.append(text[i:i + max_chars])
        i += step
    return out


class RagService:
    """Programmatic ingest service. Bypasses the 200-file MCP tool cap and
    exposes a stable Python entry point for bin/rag_ingest.py and any
    other bulk-ingest caller.

    Chunk strategy: 4000-char windows with 400-char overlap. Idempotent
    by (relpath, chunk_idx, leading-64-char-hash). Embeddings flow
    through the registered `embedder` service, which is the cached
    Google backend by default (sha256-keyed cache, batched throttle,
    429 retry).
    """

    def __init__(self, cfg: DocsConfig, kernel: Any) -> None:  # noqa: F821
        self._cfg = cfg
        self._kernel = kernel

    async def ingest_directory(
        self,
        collection: str,
        sources_dir: Path | str,
    ) -> dict[str, Any]:
        import chromadb
        sources_dir = Path(sources_dir).resolve()
        if not sources_dir.is_dir():
            raise FileNotFoundError(f"sources_dir not found: {sources_dir}")
        embedder = self._kernel.services.get("embedder")
        if embedder is None:
            raise RuntimeError("no embedder service registered")

        persist = Path(self._cfg.chroma_path)
        persist.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(persist))
        coll = client.get_or_create_collection(name=collection)

        files = [
            p for p in sources_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() in _SUPPORTED_TEXT_EXT
            and not any(part in _EXCLUDE_DIRS_SERVICE for part in p.parts)
            and ".min." not in p.name
        ]
        n_files = 0
        n_chunks = 0
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            chunks = _chunk_chars(text)
            if not chunks:
                continue
            rel = str(p.relative_to(sources_dir))
            ids, docs, metas = [], [], []
            for i, ch in enumerate(chunks):
                cid = hashlib.sha256(
                    f"{rel}:{i}:{ch[:64]}".encode()
                ).hexdigest()[:24]
                ids.append(cid)
                docs.append(ch)
                metas.append({"path": rel, "chunk": i})

            existing = await asyncio.to_thread(coll.get, ids=ids, include=[])
            already = set(existing.get("ids") or [])
            if already and len(already) == len(ids):
                n_files += 1
                n_chunks += len(chunks)
                continue
            if already:
                keep = [j for j, cid in enumerate(ids) if cid not in already]
                ids = [ids[j] for j in keep]
                docs = [docs[j] for j in keep]
                metas = [metas[j] for j in keep]

            embeddings = await embedder.embed(docs)
            # ChromaDB rejects single upserts >5461 rows. Split into safe chunks.
            UPSERT_BATCH = 5000
            for s in range(0, len(ids), UPSERT_BATCH):
                e = s + UPSERT_BATCH
                await asyncio.to_thread(
                    coll.upsert,
                    ids=ids[s:e],
                    embeddings=embeddings[s:e],
                    documents=docs[s:e],
                    metadatas=metas[s:e],
                )
            n_files += 1
            n_chunks += len(chunks)

        return {
            "collection": collection,
            "files": n_files,
            "chunks": n_chunks,
            "mode": "service",
        }


class DocsConfig(BaseModel):
    chroma_path: str = str(Path.home() / ".tlx" / "chroma")
    collection: str = "default"
    top_k: int = 5
    chunk_size: int = 800
    chunk_overlap: int = 100


async def _warmup(cfg: DocsConfig, embedding_function=None) -> None:
    import chromadb
    log = structlog.get_logger(__name__)
    try:
        client = chromadb.PersistentClient(path=cfg.chroma_path)
        if embedding_function is not None:
            col = client.get_or_create_collection(
                "__warmup__", embedding_function=embedding_function,
            )
        else:
            col = client.get_or_create_collection("__warmup__")
        await asyncio.to_thread(
            col.add,
            documents=["tlx warmup"],
            ids=["__warmup_0__"],
            metadatas=[{"source": "warmup"}],
        )
        client.delete_collection("__warmup__")
        log.debug("rag_warmup_complete")
    except Exception as e:
        log.debug("rag_warmup_failed", error=str(e))


def _register(kernel: Any, config: Any) -> RegisteredModule:
    cfg = config if isinstance(config, DocsConfig) else DocsConfig()
    from modules.rag.tools import (
        docs_ingest,
        docs_ingest_dir,
        docs_list,
        docs_query,
    )

    ef = None
    embedder = None
    services = getattr(kernel, "services", None)
    if services is not None and hasattr(services, "get"):
        embedder = services.get("embedder")
    if embedder is not None:
        from kernel.embedders.chroma_adapter import make_chroma_adapter
        ef = make_chroma_adapter(embedder)

    tools = [
        Tool(
            name="docs_ingest",
            description=(
                "Ingest a file (PDF/MD/HTML/epub/code/data) into a Chroma "
                "collection for semantic search."
            ),
            params={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File to ingest."},
                    "collection": {
                        "type": "string",
                        "description": "Collection name.",
                        "default": cfg.collection,
                    },
                },
                "required": ["path"],
            },
            handler=lambda path, collection=cfg.collection: docs_ingest(
                path, collection, cfg, ef,
            ),
            requires=["path_access"],
        ),
        Tool(
            name="docs_query",
            description="Semantic search over an ingested document collection.",
            params={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "collection": {"type": "string", "default": cfg.collection},
                    "top_k": {"type": "integer", "default": cfg.top_k},
                },
                "required": ["question"],
            },
            handler=lambda question, collection=cfg.collection, top_k=cfg.top_k: docs_query(
                question, collection, top_k, cfg, ef,
            ),
            requires=[],
        ),
        Tool(
            name="docs_list",
            description="List all Chroma collections with document counts.",
            params={"type": "object", "properties": {}},
            handler=lambda: docs_list(cfg),
            requires=[],
        ),
        Tool(
            name="docs_ingest_dir",
            description=(
                "Ingest all files in a directory matching a glob pattern into "
                "a collection. Use for bulk ingestion of JS files from a "
                "crawled app, HTML outputs from playwright, or any directory "
                "of files for RAG analysis."
            ),
            params={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path.",
                    },
                    "glob": {
                        "type": "string",
                        "description": "Glob pattern e.g. '**/*.js', '*.html', '*.md'.",
                        "default": "**/*",
                    },
                    "collection": {
                        "type": "string",
                        "description": "Collection name.",
                        "default": cfg.collection,
                    },
                },
                "required": ["directory"],
            },
            handler=lambda directory, glob="**/*", collection=cfg.collection: docs_ingest_dir(
                directory, glob, collection, cfg, ef,
            ),
            requires=["path_access"],
        ),
    ]
    for t in tools:
        kernel.tools.register(t)

    # Register bulk-ingest service (used by bin/rag_ingest.py).
    # Skip silently if already registered (re-boot scenarios).
    try:
        kernel.services.register("rag", RagService(cfg, kernel))
    except ValueError:
        pass

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_warmup(cfg, ef))
    except RuntimeError:
        pass

    return RegisteredModule(spec=MODULE, tools=tools)


MODULE = ModuleSpec(
    name="rag",
    version="0.1.0",
    requires_kernel=">=0.1.0",
    depends_on=[],
    config_schema=DocsConfig,
    register_fn=_register,
)
