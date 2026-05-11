"""Engine protocols — uniform contract for LLM adapters."""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from kernel.schema import EngineResponse, Message
from kernel.tools import Tool


@runtime_checkable
class Engine(Protocol):
    name: str
    model: str

    async def respond(
        self,
        messages: list[Message],
        tools: list[Tool],
        system: str | None,
        max_tokens: int | None = None,
    ) -> EngineResponse: ...


@runtime_checkable
class StreamingEngine(Engine, Protocol):
    async def stream(
        self,
        messages: list[Message],
        tools: list[Tool],
        system: str | None,
    ) -> AsyncIterator[str]: ...
