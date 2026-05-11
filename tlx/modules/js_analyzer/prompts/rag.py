"""Prompt-RAG — separate Chroma collection for prompt retrieval.

Sits next to code-RAG / web-RAG on the shared RAGEngine. Distinct
collection ("prompts") so prompt retrieval never blends with code chunks.

Indexing rules:
- Each Prompt becomes one or more Chroma docs.
- If body length > CHUNK_SIZE, split on paragraph boundaries; each chunk
  carries the same prompt-id + chunk index.
- Manifest records {prompt_id: content_hash, chunk_ids}; reindex only
  when content_hash changes or file is added/removed.

Embedder contract (Phase 8E):
Any RAGEngine plugged into PromptRAG must construct its Chroma
collections with an `embedding_function` sourced from
`kernel.embedders.chroma_adapter.make_chroma_adapter(
    kernel.services.get("embedder"))`. That keeps prompt-RAG on the
same backend (Google text-embedding-004 default; local MiniLM via
TLX_EMBEDDER=local) as docs-RAG. PromptRAG itself never touches
chromadb directly — the engine owns that boundary.
"""

from dataclasses import dataclass
from pathlib import Path

from .loader import Prompt

CHUNK_SIZE  = 2000      # chars; split larger bodies
COLLECTION  = "prompts"


@dataclass
class IndexStats:
    added:     int = 0
    updated:   int = 0
    removed:   int = 0
    unchanged: int = 0
    chunks:    int = 0


class PromptRAG:
    """Owns the 'prompts' Chroma collection on a shared RAGEngine.

    The engine may be disabled (no chromadb installed); in that case
    reindex() is a no-op and query() returns []. Registry must handle
    both modes.
    """

    def __init__(self, engine, prompts_dir: Path):
        self.engine        = engine
        self.prompts_dir   = Path(prompts_dir)
        self.enabled       = bool(engine and getattr(engine, "enabled", False))
        self.collection    = (
            engine.collection(COLLECTION) if self.enabled else None
        )

    # ── manifest helpers ────────────────────────────────────────────────

    def _load_manifest(self) -> dict:
        if not self.enabled:
            return {}
        return self.engine.load_manifest(COLLECTION)

    def _save_manifest(self, m: dict) -> None:
        if self.enabled:
            self.engine.save_manifest(COLLECTION, m)

    # ── chunking ────────────────────────────────────────────────────────

    @staticmethod
    def _chunk_body(body: str) -> list[str]:
        if len(body) <= CHUNK_SIZE:
            return [body]
        # Split on blank lines first.
        paragraphs = [p for p in body.split("\n\n") if p.strip()]
        chunks: list[str] = []
        cur = ""
        for p in paragraphs:
            candidate = (cur + "\n\n" + p) if cur else p
            if len(candidate) > CHUNK_SIZE and cur:
                chunks.append(cur)
                cur = p
            else:
                cur = candidate
        if cur:
            chunks.append(cur)
        # Hard-cap any chunk that's still too long.
        out: list[str] = []
        for c in chunks:
            if len(c) <= CHUNK_SIZE:
                out.append(c)
            else:
                for i in range(0, len(c), CHUNK_SIZE):
                    out.append(c[i:i + CHUNK_SIZE])
        return out

    @staticmethod
    def _chunk_ids(prompt: Prompt, n: int) -> list[str]:
        return [f"{prompt.id}::{i}" for i in range(n)]

    def _to_chunks(self, prompt: Prompt) -> list[dict]:
        bodies = self._chunk_body(prompt.body)
        ids    = self._chunk_ids(prompt, len(bodies))
        meta   = prompt.to_meta()
        return [
            {
                "id":   ids[i],
                "text": f"{prompt.title}\n\n{bodies[i]}",
                "meta": {**meta, "chunk_index": i, "chunk_count": len(bodies)},
            }
            for i in range(len(bodies))
        ]

    # ── public API ──────────────────────────────────────────────────────

    def reindex(self, prompts: list[Prompt]) -> IndexStats:
        """Hash-based incremental reindex. Returns stats."""
        stats = IndexStats()
        if not self.enabled:
            return stats

        manifest    = self._load_manifest()
        seen        = set()
        all_new_chunks: list[dict] = []
        delete_ids: list[str]     = []

        for p in prompts:
            seen.add(p.id)
            entry = manifest.get(p.id)
            chunks = self._to_chunks(p)
            stats.chunks += len(chunks)
            if entry and entry.get("hash") == p.content_hash \
                    and entry.get("chunk_ids") == [c["id"] for c in chunks]:
                stats.unchanged += 1
                continue
            if entry:
                # content changed — drop old chunks
                delete_ids.extend(entry.get("chunk_ids", []))
                stats.updated += 1
            else:
                stats.added += 1
            all_new_chunks.extend(chunks)
            manifest[p.id] = {
                "hash":      p.content_hash,
                "chunk_ids": [c["id"] for c in chunks],
                "kind":      p.kind,
            }

        # Drop prompts removed from disk
        for pid in list(manifest.keys()):
            if pid not in seen:
                delete_ids.extend(manifest[pid].get("chunk_ids", []))
                del manifest[pid]
                stats.removed += 1

        if delete_ids:
            self.engine.delete_chunks(self.collection, delete_ids)
        if all_new_chunks:
            self.engine.upsert_chunks(self.collection, all_new_chunks)

        self._save_manifest(manifest)
        return stats

    def query(
        self, text: str, kind: str | None = None, top_k: int = 3
    ) -> list[dict]:
        """Top-k prompt chunks for a free-text task query.

        Each hit includes the original prompt id/title/kind in metadata.
        Same prompt_id only appears once (deduped on first hit's chunk).
        """
        if not self.enabled:
            return []
        where = {"kind": kind} if kind else None
        result = self.engine.query(
            self.collection, text, top_k=top_k * 3, where=where,
        )
        if result.get("error"):
            return []

        seen_ids = set()
        deduped: list[dict] = []
        for hit in result.get("results", []):
            pid = hit.get("id")
            if not pid or pid in seen_ids:
                continue
            seen_ids.add(pid)
            deduped.append(hit)
            if len(deduped) >= top_k:
                break
        return deduped
