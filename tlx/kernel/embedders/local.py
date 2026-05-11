"""Local backend: chromadb ONNX all-MiniLM-L6-v2.

384-dim output. No API key. Used when TLX_EMBEDDER=local or as the
no-network test backend.

The ONNX runtime call is sync; wrap each batch in asyncio.to_thread.
"""
from __future__ import annotations

import asyncio
from typing import Any

MODEL_ID = "all-MiniLM-L6-v2"


class LocalEmbedder:
    model_id = MODEL_ID

    def __init__(self, ef: Any | None = None) -> None:
        self._ef = ef

    def _get_ef(self) -> Any:
        if self._ef is None:
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
            self._ef = ONNXMiniLM_L6_V2()
        return self._ef

    def _embed_sync(self, texts: list[str]) -> list[list[float]]:
        raw = self._get_ef()(texts)
        return [[float(x) for x in v] for v in raw]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._embed_sync, texts)
