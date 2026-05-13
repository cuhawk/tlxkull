"""Google Gemini embedding backend.

Architectural exception: kernel/embedders/*.py may import google.genai
(documented in CLAUDE.md, like kernel/engines/gemini.py).

Uses gemini-embedding-001 (text-embedding-004 retired on v1beta).
Sync genai client wrapped via asyncio.to_thread.
Batched in chunks of 100 to stay under per-call limits.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

BATCH = 100
MODEL_ID = os.environ.get("TLX_EMBED_MODEL", "gemini-embedding-001")
# Throttle: seconds to sleep between batches to stay under TPM/RPM caps.
# Tier 1 (paid, default): 100 RPM, 1M TPM. 100-chunk batches at ~1k tok each
# = ~100k tok/batch → need ≤10 batches/min → 6.0s sleep is a safe floor.
BATCH_SLEEP = float(os.environ.get("TLX_EMBED_BATCH_SLEEP", "6.0"))
# Retry on 429 (RESOURCE_EXHAUSTED). Exponential backoff capped.
MAX_429_RETRIES = int(os.environ.get("TLX_EMBED_MAX_429_RETRIES", "5"))


class GoogleEmbedder:
    model_id = MODEL_ID

    def __init__(
        self,
        client: Any | None = None,
        api_key: str | None = None,
    ) -> None:
        self._client = client
        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY") or None

    def _get_client(self) -> Any:
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _embed_batch_sync(self, batch: list[str]) -> list[list[float]]:
        client = self._get_client()
        resp = client.models.embed_content(
            model=self.model_id,
            contents=batch,
        )
        out: list[list[float]] = []
        for emb in resp.embeddings:
            vals = getattr(emb, "values", None)
            if vals is None and isinstance(emb, dict):
                vals = emb.get("values")
            if vals is None:
                raise RuntimeError(
                    "google embed response missing 'values' on item"
                )
            out.append(list(vals))
        return out

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        results: list[list[float]] = []
        total_batches = (len(texts) + BATCH - 1) // BATCH
        for i in range(0, len(texts), BATCH):
            chunk = texts[i:i + BATCH]
            attempt = 0
            while True:
                try:
                    vecs = await asyncio.to_thread(self._embed_batch_sync, chunk)
                    break
                except Exception as e:
                    msg = str(e)
                    is_429 = "429" in msg or "RESOURCE_EXHAUSTED" in msg
                    if not is_429 or attempt >= MAX_429_RETRIES:
                        raise
                    backoff = min(60.0, BATCH_SLEEP * (2 ** attempt))
                    await asyncio.sleep(backoff)
                    attempt += 1
            results.extend(vecs)
            # Throttle between batches (skip after last).
            if i + BATCH < len(texts) and BATCH_SLEEP > 0:
                await asyncio.sleep(BATCH_SLEEP)
        return results
