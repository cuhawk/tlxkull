"""chromadb EmbeddingFunction adapter.

chromadb wants a sync callable with signature `(input: list[str]) -> list[list[float]]`.
We wrap an async Embedder by running its coroutine on an isolated background
event loop owned by the adapter (never touches the caller's loop).
"""
from __future__ import annotations

import asyncio
import threading
from typing import Any

from kernel.embeddings import Embedder


class _LoopRunner:
    """Single dedicated thread + event loop for sync->async bridging."""

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def _ensure(self) -> asyncio.AbstractEventLoop:
        with self._lock:
            if self._loop is not None and self._thread is not None and self._thread.is_alive():
                return self._loop
            loop = asyncio.new_event_loop()

            def _runner() -> None:
                asyncio.set_event_loop(loop)
                loop.run_forever()

            t = threading.Thread(
                target=_runner, name="tlx.embedder.loop", daemon=True
            )
            t.start()
            self._loop = loop
            self._thread = t
            return loop

    def run(self, coro: Any) -> Any:
        loop = self._ensure()
        fut = asyncio.run_coroutine_threadsafe(coro, loop)
        return fut.result()


_RUNNER = _LoopRunner()


def _build_base_class() -> type:
    """Subclass chromadb's EmbeddingFunction if importable; else object."""
    try:
        from chromadb.utils.embedding_functions import EmbeddingFunction
        return EmbeddingFunction
    except Exception:
        return object


class TlxEmbeddingFunction(_build_base_class()):  # type: ignore[misc]
    """Sync EmbeddingFunction wrapping an async Embedder."""

    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder

    @property
    def embedder(self) -> Embedder:
        return self._embedder

    def __call__(self, input: list[str]) -> list[list[float]]:  # noqa: A002
        if not input:
            return []
        return _RUNNER.run(self._embedder.embed(list(input)))

    def name(self) -> str:
        return f"tlx:{self._embedder.model_id}"


def make_chroma_adapter(embedder: Embedder) -> TlxEmbeddingFunction:
    return TlxEmbeddingFunction(embedder)
