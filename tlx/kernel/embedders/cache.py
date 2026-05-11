"""SQLite-backed embedding cache wrapper.

Schema: (sha256 TEXT, model TEXT, vec BLOB, created_at TEXT)
PK (sha256, model). WAL mode. Vectors packed as little-endian float32.

Wraps any Embedder. On embed(): for each text, sha256+model lookup;
unknown ones get batched through to backend, then written back.
"""
from __future__ import annotations

import array
import datetime as _dt
import hashlib
import sqlite3
import threading
from pathlib import Path

from kernel.embeddings import Embedder


def _default_db_path() -> Path:
    return Path.home() / ".tlx" / "embedding.db"


def _pack(vec: list[float]) -> bytes:
    return array.array("f", vec).tobytes()


def _unpack(blob: bytes) -> list[float]:
    a = array.array("f")
    a.frombytes(blob)
    return list(a)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


class CachedEmbedder:
    """Thread-safe SQLite cache around an Embedder backend."""

    def __init__(
        self,
        backend: Embedder,
        db_path: Path | None = None,
    ) -> None:
        self._backend = backend
        self.model_id = backend.model_id
        self._db_path = db_path if db_path is not None else _default_db_path()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS embeddings (
                sha256 TEXT NOT NULL,
                model TEXT NOT NULL,
                vec BLOB NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (sha256, model)
            )"""
        )
        self._conn.commit()

    @property
    def backend(self) -> Embedder:
        return self._backend

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.close()
            except Exception:
                pass

    def _get_many(self, keys: list[tuple[str, str]]) -> dict[tuple[str, str], list[float]]:
        if not keys:
            return {}
        with self._lock:
            out: dict[tuple[str, str], list[float]] = {}
            cur = self._conn.cursor()
            for sha, model in keys:
                row = cur.execute(
                    "SELECT vec FROM embeddings WHERE sha256=? AND model=?",
                    (sha, model),
                ).fetchone()
                if row is not None:
                    out[(sha, model)] = _unpack(row[0])
            return out

    def _put_many(self, items: list[tuple[str, str, list[float]]]) -> None:
        if not items:
            return
        now = _dt.datetime.utcnow().isoformat(timespec="seconds")
        rows = [(sha, model, _pack(vec), now) for sha, model, vec in items]
        with self._lock:
            self._conn.executemany(
                "INSERT OR REPLACE INTO embeddings "
                "(sha256, model, vec, created_at) VALUES (?, ?, ?, ?)",
                rows,
            )
            self._conn.commit()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self.model_id
        shas = [_sha256(t) for t in texts]
        cached = self._get_many([(s, model) for s in shas])

        miss_idx: list[int] = []
        miss_texts: list[str] = []
        for i, (s, t) in enumerate(zip(shas, texts, strict=True)):
            if (s, model) not in cached:
                miss_idx.append(i)
                miss_texts.append(t)

        new_vecs: list[list[float]] = []
        if miss_texts:
            new_vecs = await self._backend.embed(miss_texts)
            if len(new_vecs) != len(miss_texts):
                raise RuntimeError(
                    f"backend returned {len(new_vecs)} vectors for "
                    f"{len(miss_texts)} inputs"
                )
            self._put_many([
                (shas[idx], model, vec)
                for idx, vec in zip(miss_idx, new_vecs, strict=True)
            ])

        result: list[list[float]] = [None] * len(texts)  # type: ignore[list-item]
        for i, s in enumerate(shas):
            hit = cached.get((s, model))
            if hit is not None:
                result[i] = hit
        for idx, vec in zip(miss_idx, new_vecs, strict=True):
            result[idx] = vec
        return result
