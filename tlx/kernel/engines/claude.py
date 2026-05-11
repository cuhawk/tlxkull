"""Anthropic Claude engine adapter."""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from kernel.schema import (
    Cost,
    EngineResponse,
    Message,
    StopReason,
    TextBlock,
    ToolCall,
    ToolResultBlock,
    ToolUseBlock,
    Usage,
)
from kernel.tools import Tool

PRICING: dict[str, tuple[float, float]] = {
    "claude-sonnet-4-6":   (3.0, 15.0),
    "claude-haiku-4-5":    (1.0,  5.0),
    "claude-opus-4-7":     (5.0, 25.0),
}


def price_per_token(model: str) -> tuple[float, float]:
    """Returns (input_per_token_usd, output_per_token_usd).
    Unknown model → (0.0, 0.0) with a structlog warning."""
    if model not in PRICING:
        import structlog
        structlog.get_logger(__name__).warning(
            "claude_engine.unknown_model_pricing", model=model
        )
        return (0.0, 0.0)
    in_per_m, out_per_m = PRICING[model]
    return (in_per_m / 1e6, out_per_m / 1e6)

_CACHE_EPHEMERAL: dict[str, str] = {"type": "ephemeral"}
_DEFAULT_MAX_TOKENS = 4096


class ClaudeEngine:
    name = "claude"

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        client: Any | None = None,
        api_key: str | None = None,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._client = client
        self._api_key = api_key
        self._last_usage: Usage | None = None
        self._last_cost: Cost | None = None
        self._last_stream_response: EngineResponse | None = None

    def _get_client(self) -> Any:
        if self._client is None:
            import anthropic

            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        return self._client

    async def respond(
        self,
        messages: list[Message],
        tools: list[Tool],
        system: str | None,
        max_tokens: int | None = None,
    ) -> EngineResponse:
        api_messages = _to_anthropic_messages(messages)
        _add_conversation_cache_breakpoint(api_messages)

        effective = max_tokens if max_tokens is not None else self.max_tokens
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": effective,
            "messages": api_messages,
        }

        if system:
            kwargs["system"] = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": dict(_CACHE_EPHEMERAL),
                }
            ]

        if tools:
            kwargs["tools"] = _serialize_tools(tools)

        client = self._get_client()
        response = await client.messages.create(**kwargs)
        return _parse_response(response, self.model)

    async def stream(
        self,
        messages: list[Message],
        tools: list[Tool],
        system: str | None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        api_messages = _to_anthropic_messages(messages)
        _add_conversation_cache_breakpoint(api_messages)

        effective = max_tokens if max_tokens is not None else self.max_tokens
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": effective,
            "messages": api_messages,
        }
        if system:
            kwargs["system"] = [
                {"type": "text", "text": system, "cache_control": dict(_CACHE_EPHEMERAL)}
            ]
        if tools:
            kwargs["tools"] = _serialize_tools(tools)

        client = self._get_client()
        async with client.messages.stream(**kwargs) as s:
            async for chunk in s.text_stream:
                yield chunk
            final = await s.get_final_message()
            self._last_usage = Usage(
                input_tokens=int(getattr(final.usage, "input_tokens", 0) or 0),
                output_tokens=int(getattr(final.usage, "output_tokens", 0) or 0),
                cache_read_tokens=int(getattr(final.usage, "cache_read_input_tokens", 0) or 0),
                cache_write_tokens=int(getattr(final.usage, "cache_creation_input_tokens", 0) or 0),
            )
            in_price, out_price = PRICING.get(self.model, (0.0, 0.0))
            u = self._last_usage
            billable = u.input_tokens + u.cache_read_tokens + u.cache_write_tokens
            self._last_cost = Cost(
                input_usd=billable * in_price / 1_000_000,
                output_usd=u.output_tokens * out_price / 1_000_000,
            )
            self._last_stream_response = _parse_response(final, self.model)


def _serialize_tools(tools: list[Tool]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for tool in tools:
        out.append(
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.params,
            }
        )
    if out:
        out[-1]["cache_control"] = dict(_CACHE_EPHEMERAL)
    return out


def _to_anthropic_messages(messages: list[Message]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for msg in messages:
        if msg.role == "system":
            continue
        role = "assistant" if msg.role == "assistant" else "user"
        content = _convert_content(msg)
        if content == "" or content == []:
            continue
        out.append({"role": role, "content": content})
    return out


def _convert_content(msg: Message) -> Any:
    if isinstance(msg.content, str):
        if msg.role == "tool":
            return [
                {
                    "type": "tool_result",
                    "tool_use_id": msg.tool_call_id or "",
                    "content": msg.content,
                }
            ]
        return msg.content
    blocks: list[dict[str, Any]] = []
    for b in msg.content:
        blocks.append(b.model_dump())
    return blocks


def _add_conversation_cache_breakpoint(api_messages: list[dict[str, Any]]) -> None:
    if len(api_messages) < 2:
        return
    target = api_messages[-2]
    content = target["content"]
    if isinstance(content, str):
        target["content"] = [
            {
                "type": "text",
                "text": content,
                "cache_control": dict(_CACHE_EPHEMERAL),
            }
        ]
        return
    if isinstance(content, list) and content:
        last = content[-1]
        if isinstance(last, dict):
            last["cache_control"] = dict(_CACHE_EPHEMERAL)


def _parse_response(response: Any, model: str) -> EngineResponse:
    blocks: list[TextBlock | ToolUseBlock | ToolResultBlock] = []
    tool_calls: list[ToolCall] = []

    for part in getattr(response, "content", []) or []:
        ptype = getattr(part, "type", None)
        if ptype == "text":
            blocks.append(TextBlock(text=getattr(part, "text", "")))
        elif ptype == "tool_use":
            tu_id = getattr(part, "id", "")
            tu_name = getattr(part, "name", "")
            tu_input = getattr(part, "input", {}) or {}
            blocks.append(ToolUseBlock(id=tu_id, name=tu_name, input=dict(tu_input)))
            tool_calls.append(ToolCall(id=tu_id, name=tu_name, args=dict(tu_input)))

    usage_obj = getattr(response, "usage", None)
    input_tokens = int(getattr(usage_obj, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage_obj, "output_tokens", 0) or 0)
    cache_read = int(getattr(usage_obj, "cache_read_input_tokens", 0) or 0)
    cache_write = int(getattr(usage_obj, "cache_creation_input_tokens", 0) or 0)

    usage = Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read,
        cache_write_tokens=cache_write,
    )

    in_price, out_price = PRICING.get(model, (0.0, 0.0))
    billable_input = input_tokens + cache_read + cache_write
    cost = Cost(
        input_usd=billable_input * in_price / 1_000_000,
        output_usd=output_tokens * out_price / 1_000_000,
    )

    raw_stop = getattr(response, "stop_reason", "end_turn") or "end_turn"
    if raw_stop == "end_turn":
        stop_reason: StopReason = "end_turn"
    elif raw_stop == "tool_use":
        stop_reason = "tool_use"
    elif raw_stop == "max_tokens":
        stop_reason = "max_tokens"
    else:
        stop_reason = "other"

    return EngineResponse(
        content=blocks,
        tool_calls=tool_calls,
        usage=usage,
        cost=cost,
        stop_reason=stop_reason,
    )


