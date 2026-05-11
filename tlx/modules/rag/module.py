"""RAG module — semantic search over local files via Chroma.

Renamed from `docs` to `rag` (folder + module identifier). Tool names
(`docs_query`, `docs_ingest`, `docs_list`, `docs_ingest_dir`) are the
public MCP API surface and are kept unchanged for backward compatibility
with the allowlist + skill wiring.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel

from kernel.modules import ModuleSpec, RegisteredModule
from kernel.tools import Tool


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
