"""Docs RAG tools — file ingest + Chroma semantic search."""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import chromadb
import structlog

log = structlog.get_logger(__name__)

_CODE_EXTENSIONS = frozenset({
    ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".py", ".rb", ".go", ".java", ".c", ".cpp", ".h",
    ".cs", ".php", ".rs", ".swift", ".kt", ".scala",
    ".sh", ".bash", ".zsh",
})

_DATA_EXTENSIONS = frozenset({
    ".json", ".yaml", ".yml", ".toml", ".xml", ".csv",
})

_TOP_LEVEL_BOUNDARY = re.compile(
    r"(?=\n(?:export\s+(?:default\s+)?)?(?:async\s+)?(?:function|class)\s"
    r"|\nexport\s+(?:const|let|var)\s+\w+\s*="
    r"|\nmodule\.exports"
    r"|\n(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\(|(?:\w+\s*=>)))"
)


def _chunk(text: str, size: int, overlap: int) -> list[str]:
    if size <= overlap:
        overlap = 0
    step = size - overlap
    chunks: list[str] = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + size])
        i += step
    return chunks


def _chunk_code(text: str, size: int, overlap: int) -> list[str]:
    parts = _TOP_LEVEL_BOUNDARY.split(text)
    chunks: list[str] = []
    current = ""
    for part in parts:
        if len(current) + len(part) <= size:
            current += part
        else:
            if current:
                chunks.append(current)
            if len(part) > size:
                chunks.extend(_chunk(part, size, overlap))
                current = ""
            else:
                current = part
    if current:
        chunks.append(current)
    return chunks if chunks else _chunk(text, size, overlap)


def _load_pdf(path: Path, max_pages: int = 500) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            pages = pdf.pages[:max_pages]
            return "\n".join(p.extract_text() or "" for p in pages)
    except Exception:
        import pypdf
        reader = pypdf.PdfReader(str(path))
        pages = list(reader.pages)[:max_pages]
        return "\n".join(page.extract_text() or "" for page in pages)


def _load_epub(path: Path) -> str:
    import ebooklib
    from bs4 import BeautifulSoup
    from ebooklib import epub
    book = epub.read_epub(str(path))
    parts: list[str] = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        parts.append(BeautifulSoup(item.get_content(), "lxml").get_text())
    return "\n".join(parts)


def _load_text(path: str) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(p)
    if suffix in (".md", ".txt"):
        return p.read_text(encoding="utf-8", errors="replace")
    if suffix in (".html", ".htm"):
        from bs4 import BeautifulSoup
        return BeautifulSoup(
            p.read_text(encoding="utf-8", errors="replace"), "lxml"
        ).get_text(separator="\n")
    if suffix == ".epub":
        return _load_epub(p)
    if suffix in _CODE_EXTENSIONS:
        return p.read_text(encoding="utf-8", errors="replace")
    if suffix in _DATA_EXTENSIONS:
        return p.read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"Unsupported file type: {suffix!r}")


_MARKER_DOC = "__tlx_sha256_marker__"


def _stored_sha256(col, doc_id: str) -> str | None:
    try:
        existing = col.get(ids=[doc_id], include=["metadatas"])
    except Exception:
        return None
    metas = existing.get("metadatas") if isinstance(existing, dict) else None
    if not metas:
        return None
    first = metas[0] if isinstance(metas, list) and metas else None
    if not isinstance(first, dict):
        return None
    val = first.get("sha256")
    return val if isinstance(val, str) else None


def _collection(cfg, name: str, embedding_function: Any | None):
    """Open a collection without attaching an embedding_function.

    Callers pre-embed via the kernel embedder and pass `embeddings=` to
    upsert and `query_embeddings=` to query. Attaching an EF here causes
    chromadb to reject the collection if a different EF (or none) was
    persisted at create time. The `embedding_function` arg is retained
    only for the legacy adapter path; ignored when bypass mode is used.
    """
    client = chromadb.PersistentClient(path=cfg.chroma_path)
    return client.get_or_create_collection(name)


async def docs_ingest(
    path: str,
    collection: str,
    cfg,
    embedding_function: Any | None = None,
) -> str:
    try:
        text = await asyncio.to_thread(_load_text, path)
    except Exception as e:
        return json.dumps({
            "error": f"load_failed: {type(e).__name__}: {e}",
            "path": path,
        })

    suffix = Path(path).suffix.lower()
    if suffix in _CODE_EXTENSIONS:
        chunks = _chunk_code(text, cfg.chunk_size, cfg.chunk_overlap)
    else:
        chunks = _chunk(text, cfg.chunk_size, cfg.chunk_overlap)

    if not chunks:
        return json.dumps({"error": "no_content", "path": path})

    current = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
    doc_id = str(Path(path).resolve())  # noqa: ASYNC240

    try:
        col = _collection(cfg, collection, embedding_function)

        stored = await asyncio.to_thread(_stored_sha256, col, doc_id)
        if stored == current:
            log.info("docs.skip_unchanged", file=path)
            return json.dumps({
                "skipped": True,
                "reason": "unchanged",
                "collection": collection,
                "source": path,
            })

        source_name = Path(path).name
        ids = [f"{source_name}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"source": path, "chunk_idx": i, "sha256": current}
            for i in range(len(chunks))
        ]
        # Pre-embed via kernel embedder. Bypasses chromadb's attached EF
        # so collections written by different ingest paths stay queryable.
        if embedding_function is None or not hasattr(
            embedding_function, "_embedder"
        ):
            return json.dumps({
                "error": "no_kernel_embedder",
                "hint": "RAG module did not receive a kernel embedder; "
                        "MCP boot misconfigured.",
            })
        kernel_emb = embedding_function._embedder
        marker_vec = (await kernel_emb.embed([_MARKER_DOC]))[0]
        chunk_vecs = await kernel_emb.embed(chunks)
        await asyncio.to_thread(
            col.upsert,
            ids=[doc_id],
            embeddings=[marker_vec],
            documents=[_MARKER_DOC],
            metadatas=[{
                "source": path, "sha256": current, "marker": True,
            }],
        )
        await asyncio.to_thread(
            col.upsert,
            ids=ids,
            embeddings=chunk_vecs,
            documents=chunks,
            metadatas=metadatas,  # type: ignore[arg-type]
        )
    except Exception as e:
        return json.dumps({
            "error": f"chroma_failed: {type(e).__name__}: {e}",
            "chunks": len(chunks),
        })

    return json.dumps({
        "ingested": len(chunks),
        "collection": collection,
        "source": path,
    })


async def docs_query(
    question: str,
    collection: str,
    top_k: int,
    cfg,
    embedding_function: Any | None = None,
) -> str:
    try:
        col = _collection(cfg, collection, embedding_function)
        # Pre-embed the question with the kernel embedder, then query by
        # vector. Avoids chromadb attempting to embed with whatever EF
        # was attached at collection-create time (which may not match).
        if embedding_function is None or not hasattr(
            embedding_function, "_embedder"
        ):
            return json.dumps({
                "error": "no_kernel_embedder",
                "hint": "RAG module did not receive a kernel embedder; "
                        "MCP boot misconfigured.",
            })
        kernel_emb = embedding_function._embedder
        qvec = (await kernel_emb.embed([question]))[0]
        results = await asyncio.to_thread(
            col.query, query_embeddings=[qvec], n_results=top_k
        )
        items = []
        docs = results.get("documents") or []
        metas = results.get("metadatas") or []
        dists = results.get("distances") or []
        if not (docs and metas and dists):
            return json.dumps([])
        for doc, meta, dist in zip(
            docs[0], metas[0], dists[0], strict=False,
        ):
            # `source` from docs_ingest path; `path` from RagService bulk path.
            src = meta.get("source") or meta.get("path") or ""
            items.append({
                "text": doc,
                "source": src,
                "score": round(1 - dist, 4),
            })
        return json.dumps(items)
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


async def docs_list(cfg) -> str:
    try:
        def _list_sync() -> list[tuple[str, int]]:
            client = chromadb.PersistentClient(path=cfg.chroma_path)
            return [(c.name, c.count()) for c in client.list_collections()]

        pairs = await asyncio.to_thread(_list_sync)
        return json.dumps([{"name": n, "count": c} for n, c in pairs])
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


_EXCLUDE_DIRS = frozenset({
    "node_modules", ".git", ".next", "dist", "build",
    "__pycache__", ".venv", "venv", ".tox", "coverage",
})


async def docs_ingest_dir(
    directory: str,
    glob: str,
    collection: str,
    cfg,
    embedding_function: Any | None = None,
) -> str:
    base = Path(directory)
    all_paths = sorted(base.glob(glob))  # noqa: ASYNC240

    paths = [
        p for p in all_paths
        if p.is_file()
        and not any(part in _EXCLUDE_DIRS for part in p.parts)
        and ".min." not in p.name
    ]

    if not paths:
        return json.dumps({
            "error": "no_files_matched",
            "directory": directory,
            "glob": glob,
        })

    if len(paths) > 200:
        return json.dumps({
            "error": "too_many_files",
            "count": len(paths),
            "hint": "use a more specific glob or subdirectory",
        })

    results = []
    total_chunks = 0
    for file_path in paths:
        result = json.loads(
            await docs_ingest(
                str(file_path), collection, cfg, embedding_function,
            )
        )
        results.append({"file": file_path.name, **result})
        total_chunks += result.get("ingested", 0)

    return json.dumps({
        "files_processed": len(results),
        "total_chunks": total_chunks,
        "collection": collection,
        "results": results,
    })
