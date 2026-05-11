"""Core schema models — engine-agnostic message/tool/usage types."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

StopReason = Literal["end_turn", "tool_use", "max_tokens", "other"]
Role = Literal["user", "assistant", "system", "tool"]


class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ToolUseBlock(BaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict


class ToolResultBlock(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str


ContentBlock = Annotated[
    TextBlock | ToolUseBlock | ToolResultBlock,
    Field(discriminator="type"),
]


class Message(BaseModel):
    role: Role
    content: str | list[ContentBlock]
    tool_call_id: str | None = None


class ToolCall(BaseModel):
    id: str
    name: str
    args: dict


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0


class Cost(BaseModel):
    input_usd: float
    output_usd: float
    advisor_usd: float = 0.0

    @property
    def total(self) -> float:
        return self.input_usd + self.output_usd + self.advisor_usd


class EngineResponse(BaseModel):
    content: list[ContentBlock]
    tool_calls: list[ToolCall]
    usage: Usage
    cost: Cost
    stop_reason: StopReason
