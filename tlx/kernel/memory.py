"""ProjectMemory — per-cwd persistent agent notes (memory.md)."""
from __future__ import annotations

import asyncio
from pathlib import Path


class ProjectMemory:
    def __init__(self, cwd: Path) -> None:
        self._path = cwd / "memory.md"
        self.content: str | None = None

    async def load(self) -> str | None:
        if not self._path.exists():
            self.content = None
            return None
        self.content = await asyncio.to_thread(
            self._path.read_text, encoding="utf-8"
        )
        return self.content

    async def write(self, content: str) -> None:
        await asyncio.to_thread(
            self._path.write_text, content, encoding="utf-8"
        )
        self.content = content

    def path(self) -> Path:
        return self._path
