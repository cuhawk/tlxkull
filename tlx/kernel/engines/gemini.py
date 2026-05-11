"""Google Gemini engine adapter."""
from __future__ import annotations

from typing import Any

from kernel.schema import (
    ContentBlock,
    Cost,
    EngineResponse,
    Message,
    StopReason,
    TextBlock,
    ToolCall,
    ToolUseBlock,
    Usage,
)
from kernel.tools import Tool

PRICING: dict[str, tuple[float, float]] = {
    "gemini-2.5-flash-lite": (0.10, 0.40),
}


class GeminiEngine:
    name = "gemini"

    def __init__(
        self,
        model: str = "gemini-2.5-flash-lite",
        client: Any | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self._client = client
        self._api_key = api_key

    def _get_client(self) -> Any:
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def respond(
        self,
        messages: list[Message],
        tools: list[Tool],
        system: str | None,
        max_tokens: int | None = None,
    ) -> EngineResponse:
        contents = _to_gemini_contents(messages)
        config: dict[str, Any] = {}
        if system:
            config["system_instruction"] = system
        if tools:
            config["tools"] = [{"function_declarations": _serialize_tools(tools)}]
        if max_tokens is not None:
            config["max_output_tokens"] = max_tokens

        client = self._get_client()
        response = await client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        return _parse_response(response, self.model)


_GEMINI_UNSUPPORTED = frozenset({
    "additionalProperties",
    "default",
    "format",
    "title",
    "uniqueItems",
    "minItems",
    "maxItems",
    "minLength",
    "maxLength",
    "pattern",
})


def _strip_gemini_unsupported(schema: dict) -> dict:
    """Gemini function declarations reject additionalProperties and other
    JSON Schema fields it doesn't support."""
    out: dict[str, Any] = {}
    for k, v in schema.items():
        if k in _GEMINI_UNSUPPORTED:
            continue
        if k == "properties" and isinstance(v, dict):
            out[k] = {pk: _strip_gemini_unsupported(pv) for pk, pv in v.items()}
        elif k == "items" and isinstance(v, dict):
            out[k] = _strip_gemini_unsupported(v)
        elif k in ("anyOf", "oneOf", "allOf") and isinstance(v, list):
            out[k] = [_strip_gemini_unsupported(x) for x in v]
        else:
            out[k] = v
    return out


def _serialize_tools(tools: list[Tool]) -> list[dict[str, Any]]:
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": _strip_gemini_unsupported(tool.params),
        }
        for tool in tools
    ]


def _build_tool_use_id_to_name(messages: list[Message]) -> dict[str, str]:
    """Map tool_use_id → function name from assistant tool_use blocks.
    Gemini's function_response.name must be the function name, not the id."""
    id_to_name: dict[str, str] = {}
    for msg in messages:
        if msg.role != "assistant" or not isinstance(msg.content, list):
            continue
        for b in msg.content:
            if b.type == "tool_use":
                id_to_name[b.id] = b.name
    return id_to_name


def _to_gemini_contents(messages: list[Message]) -> list[dict[str, Any]]:
    id_to_name = _build_tool_use_id_to_name(messages)
    out: list[dict[str, Any]] = []
    for msg in messages:
        if msg.role == "system":
            continue
        if msg.role == "tool":
            parts = _tool_message_parts(msg, id_to_name)
            if parts:
                out.append({"role": "user", "parts": parts})
            continue

        role = "user" if msg.role == "user" else "model"
        if isinstance(msg.content, str):
            out.append({"role": role, "parts": [{"text": msg.content}]})
            continue

        parts2: list[dict[str, Any]] = []
        for b in msg.content:
            if b.type == "text":
                parts2.append({"text": b.text})
            elif b.type == "tool_use":
                parts2.append(
                    {"function_call": {"name": b.name, "args": dict(b.input)}}
                )
            elif b.type == "tool_result":
                fn_name = id_to_name.get(b.tool_use_id, b.tool_use_id)
                parts2.append(
                    {
                        "function_response": {
                            "name": fn_name,
                            "response": {"content": b.content},
                        }
                    }
                )
        out.append({"role": role, "parts": parts2})
    return out


def _tool_message_parts(
    msg: Message, id_to_name: dict[str, str]
) -> list[dict[str, Any]]:
    if isinstance(msg.content, str):
        tid = msg.tool_call_id or ""
        return [
            {
                "function_response": {
                    "name": id_to_name.get(tid, tid or "tool"),
                    "response": {"content": msg.content},
                }
            }
        ]
    parts: list[dict[str, Any]] = []
    for b in msg.content:
        if b.type == "tool_result":
            parts.append(
                {
                    "function_response": {
                        "name": id_to_name.get(b.tool_use_id, b.tool_use_id),
                        "response": {"content": b.content},
                    }
                }
            )
    return parts


def _parse_response(response: Any, model: str) -> EngineResponse:
    blocks: list[ContentBlock] = []
    tool_calls: list[ToolCall] = []
    finish: StopReason = "end_turn"

    candidates = getattr(response, "candidates", None) or []
    if candidates:
        cand = candidates[0]
        finish = _map_finish_reason(getattr(cand, "finish_reason", None))
        content = getattr(cand, "content", None)
        parts = getattr(content, "parts", None) if content is not None else None
        for part in parts or []:
            text = getattr(part, "text", None)
            fc = getattr(part, "function_call", None)
            if text:
                blocks.append(TextBlock(text=text))
            if fc is not None:
                fc_name = getattr(fc, "name", "") or ""
                fc_args_raw = getattr(fc, "args", {}) or {}
                fc_args = dict(fc_args_raw) if not isinstance(fc_args_raw, dict) else dict(fc_args_raw)
                fc_id = getattr(fc, "id", None) or f"call_{len(tool_calls)}"
                blocks.append(ToolUseBlock(id=fc_id, name=fc_name, input=fc_args))
                tool_calls.append(ToolCall(id=fc_id, name=fc_name, args=fc_args))
                finish = "tool_use"

    usage_obj = getattr(response, "usage_metadata", None)
    input_tokens = int(getattr(usage_obj, "prompt_token_count", 0) or 0)
    output_tokens = int(getattr(usage_obj, "candidates_token_count", 0) or 0)
    cache_read = int(getattr(usage_obj, "cached_content_token_count", 0) or 0)

    usage = Usage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read,
        cache_write_tokens=0,
    )

    in_price, out_price = PRICING.get(model, (0.0, 0.0))
    billable_input = input_tokens + cache_read
    cost = Cost(
        input_usd=billable_input * in_price / 1_000_000,
        output_usd=output_tokens * out_price / 1_000_000,
    )

    return EngineResponse(
        content=blocks,
        tool_calls=tool_calls,
        usage=usage,
        cost=cost,
        stop_reason=finish,
    )


def _map_finish_reason(reason: Any) -> StopReason:
    if reason is None:
        return "end_turn"
    s = str(reason).lower()
    if "stop" in s:
        return "end_turn"
    if "max" in s or "length" in s:
        return "max_tokens"
    if "tool" in s or "function" in s:
        return "tool_use"
    return "other"
