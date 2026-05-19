"""Wiki RAG context fetcher for the js_analyzer audit + exploit passes.

Queries the ``wiki`` Chroma collection (built by ``bin/ingest-wiki.py``) for
prior techniques + payloads + finding notes relevant to a candidate chain.

Two retrieval modes:

- ``fetch_prior_techniques`` — broad query covering vuln_class + framework +
  sanitizer family. Feeds Sonnet (claude_analyst) verdict prompt.
- ``fetch_prior_exploits`` — narrower query restricted to finding/payload
  pages. Feeds Opus exploit-synthesis prompt.

Both are best-effort: if the embedder service or the wiki collection is
missing they return an empty list and never raise.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import structlog

_logger = structlog.get_logger(__name__)

_WIKI_COLLECTION = "wiki"
_CHROMA_PATH_DEFAULT = str(Path.home() / ".tlx" / "chroma")


def _chain_query_keys(chain: dict) -> tuple[str, str, str]:
    """Pull (vuln_class, framework_hint, sanitizer_family) for query build."""
    src_id = (chain.get("source") or {}).get("taxonomy_id", "")
    sink_id = (chain.get("sink") or {}).get("taxonomy_id", "")
    hint = chain.get("vuln_class_hint") or ""
    if not hint:
        if "innerHTML" in sink_id or "html" in sink_id.lower():
            hint = "DOM XSS"
        elif sink_id.startswith("proto_") or src_id.startswith("proto_"):
            hint = "Prototype Pollution"
        elif "sql" in sink_id.lower():
            hint = "SQL injection"
        elif "redirect" in sink_id.lower():
            hint = "Open redirect"
        elif "path_traversal" in sink_id.lower():
            hint = "Path traversal"
        else:
            hint = sink_id or "unspecified"

    sanitizers = chain.get("sanitizers_in_path") or []
    if not sanitizers:
        sanitizers = chain.get("sanitizers") or []
    san_family = ""
    for s in sanitizers:
        name = (s.get("library") if isinstance(s, dict) else str(s)) or ""
        if name:
            san_family = name
            break
    return hint, "", san_family


def _build_technique_query(chain: dict, framework_tags: list[str]) -> str:
    vuln_class, _, sanitizer = _chain_query_keys(chain)
    fw = ", ".join(framework_tags[:3]) if framework_tags else "vanilla"
    sink_id = (chain.get("sink") or {}).get("taxonomy_id", "")
    src_id = (chain.get("source") or {}).get("taxonomy_id", "")
    parts = [
        f"vulnerability class: {vuln_class}",
        f"sink taxonomy: {sink_id}",
        f"source taxonomy: {src_id}",
        f"framework: {fw}",
    ]
    if sanitizer:
        parts.append(f"sanitizer: {sanitizer}")
    return "; ".join(parts)


def _build_exploit_query(
    vuln_class: str, sink_taxonomy: str, framework_tags: list[str],
) -> str:
    fw = ", ".join(framework_tags[:3]) if framework_tags else "vanilla"
    return (
        f"exploit payload for {vuln_class} via sink {sink_taxonomy} "
        f"on framework {fw}"
    )


def _resolve_chroma_path(kernel: Any) -> str:
    services = getattr(kernel, "services", None)
    if services is None:
        return _CHROMA_PATH_DEFAULT
    rag = services.get("rag")
    cfg = getattr(rag, "_cfg", None)
    path = getattr(cfg, "chroma_path", None)
    return path or _CHROMA_PATH_DEFAULT


async def _query_wiki(
    kernel: Any, query: str, *, top_k: int, where: dict | None = None,
) -> list[dict]:
    services = getattr(kernel, "services", None)
    if services is None:
        return []
    embedder = services.get("embedder")
    if embedder is None:
        return []

    try:
        import chromadb
    except Exception as e:
        _logger.debug("wiki_rag.chromadb_missing", error=str(e))
        return []

    try:
        qvec = (await embedder.embed([query]))[0]
    except Exception as e:
        _logger.debug("wiki_rag.embed_failed", error=str(e))
        return []

    chroma_path = _resolve_chroma_path(kernel)

    def _do_query() -> dict:
        client = chromadb.PersistentClient(path=chroma_path)
        try:
            coll = client.get_collection(_WIKI_COLLECTION)
        except Exception:
            return {}
        kwargs: dict[str, Any] = {"n_results": top_k}
        if where:
            kwargs["where"] = where
        return coll.query(query_embeddings=[qvec], **kwargs)

    try:
        results = await asyncio.to_thread(_do_query)
    except Exception as e:
        _logger.debug("wiki_rag.query_failed", error=str(e))
        return []

    if not results:
        return []

    docs = results.get("documents") or []
    metas = results.get("metadatas") or []
    dists = results.get("distances") or []
    if not (docs and docs[0]):
        return []

    items: list[dict] = []
    for doc, meta, dist in zip(
        docs[0], metas[0] or [], dists[0] or [], strict=False,
    ):
        src = (meta or {}).get("source") or (meta or {}).get("path") or ""
        items.append({
            "text": doc,
            "source": src,
            "score": round(1 - float(dist), 4),
        })
    return items


async def fetch_prior_techniques(
    chain: dict, kernel: Any, *, framework_tags: list[str] | None = None,
    top_k: int = 3, score_floor: float = 0.30,
) -> list[dict]:
    """Top-K wiki excerpts for vuln-class + framework + sanitizer context.

    Returns [] on any failure (no embedder, no wiki collection, no kernel).
    """
    fw = framework_tags or []
    query = _build_technique_query(chain, fw)
    items = await _query_wiki(kernel, query, top_k=top_k)
    return [it for it in items if it["score"] >= score_floor]


async def fetch_prior_exploits(
    *,
    vuln_class: str,
    sink_taxonomy: str,
    framework_tags: list[str],
    kernel: Any,
    top_k: int = 3,
    score_floor: float = 0.30,
) -> list[dict]:
    """Top-K wiki excerpts biased toward finding/payload pages."""
    query = _build_exploit_query(vuln_class, sink_taxonomy, framework_tags)
    items = await _query_wiki(kernel, query, top_k=top_k * 2)
    bucket_hits: list[dict] = []
    other_hits: list[dict] = []
    for it in items:
        if it["score"] < score_floor:
            continue
        src = (it.get("source") or "").lower()
        if (
            "findings/" in src
            or "payloads/" in src
            or "techniques/" in src
        ):
            bucket_hits.append(it)
        else:
            other_hits.append(it)
    ranked = bucket_hits + other_hits
    return ranked[:top_k]


def fetch_prior_exploits_sync(**kwargs: Any) -> list[dict]:
    """Sync wrapper for callers outside an event loop (exploit_agent)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return []
    except RuntimeError:
        pass
    try:
        return asyncio.run(fetch_prior_exploits(**kwargs))
    except Exception as e:
        _logger.debug("wiki_rag.sync_wrap_failed", error=str(e))
        return []
