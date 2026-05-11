"""AdvisorEngine — wraps an executor + advisor, routes consult_advisor calls."""
from __future__ import annotations

import structlog

from kernel.engine import Engine
from kernel.schema import (
    ContentBlock,
    Cost,
    EngineResponse,
    Message,
    TextBlock,
    ToolResultBlock,
    Usage,
)
from kernel.tools import Tool

logger = structlog.get_logger(__name__)

_ADVISOR_TOOL_NAME = "consult_advisor"

CONSULT_ADVISOR_TOOL = Tool(
    name=_ADVISOR_TOOL_NAME,
    description=(
        "Ask the advisor model a hard question. Use when you need deeper "
        "reasoning, a second opinion, or a plan you're not confident about. "
        "The advisor sees only what you tell it — be specific."
    ),
    params={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Complete, self-contained question for the advisor.",
            }
        },
        "required": ["question"],
    },
    handler=lambda question: "",
    requires=[],
)


class AdvisorEngine:
    name = "advisor"

    def __init__(self, executor: Engine, advisor: Engine) -> None:
        self._executor = executor
        self._advisor = advisor
        self.advisor_cost_usd: float = 0.0
        self.model = f"{executor.model}+{advisor.model}"

    @property
    def executor(self) -> Engine:
        return self._executor

    @property
    def advisor(self) -> Engine:
        return self._advisor

    async def respond(
        self,
        messages: list[Message],
        tools: list[Tool],
        system: str | None,
    ) -> EngineResponse:
        executor_tools = list(tools) + [CONSULT_ADVISOR_TOOL]
        working: list[Message] = list(messages)

        agg_input = 0
        agg_output = 0
        agg_cache_read = 0
        agg_cache_write = 0
        agg_input_usd = 0.0
        agg_output_usd = 0.0
        advisor_total_usd = 0.0

        last: EngineResponse | None = None
        while True:
            resp = await self._executor.respond(working, executor_tools, system)
            agg_input += resp.usage.input_tokens
            agg_output += resp.usage.output_tokens
            agg_cache_read += resp.usage.cache_read_tokens
            agg_cache_write += resp.usage.cache_write_tokens
            agg_input_usd += resp.cost.input_usd
            agg_output_usd += resp.cost.output_usd
            last = resp

            advisor_calls = [c for c in resp.tool_calls if c.name == _ADVISOR_TOOL_NAME]
            non_advisor = [c for c in resp.tool_calls if c.name != _ADVISOR_TOOL_NAME]
            if not advisor_calls or non_advisor:
                break

            working.append(Message(role="assistant", content=list(resp.content)))

            tool_results: list[ContentBlock] = []
            for call in advisor_calls:
                question = str(call.args.get("question", ""))
                prompt = (
                    f"{question}\n\n---\nContext (last 3 turns):\n{_last3(messages)}"
                )
                advisor_resp = await self._advisor.respond(
                    [Message(role="user", content=prompt)],
                    [],
                    None,
                )
                self.advisor_cost_usd += advisor_resp.cost.total
                advisor_total_usd += advisor_resp.cost.total
                text = _extract_text(advisor_resp)
                tool_results.append(
                    ToolResultBlock(tool_use_id=call.id, content=text)
                )

            working.append(Message(role="user", content=tool_results))

        assert last is not None
        surfaced = [c for c in last.tool_calls if c.name != _ADVISOR_TOOL_NAME]
        return EngineResponse(
            content=last.content,
            tool_calls=surfaced,
            usage=Usage(
                input_tokens=agg_input,
                output_tokens=agg_output,
                cache_read_tokens=agg_cache_read,
                cache_write_tokens=agg_cache_write,
            ),
            cost=Cost(
                input_usd=agg_input_usd,
                output_usd=agg_output_usd,
                advisor_usd=advisor_total_usd,
            ),
            stop_reason=last.stop_reason,
        )


def _last3(messages: list[Message]) -> str:
    parts: list[str] = []
    for m in messages[-3:]:
        text = m.content if isinstance(m.content, str) else _content_text(m.content)
        parts.append(f"{m.role}: {text}")
    return "\n".join(parts)


def _content_text(blocks: list) -> str:
    out: list[str] = []
    for b in blocks:
        if isinstance(b, TextBlock):
            out.append(b.text)
    return "\n".join(out)


def _extract_text(resp: EngineResponse) -> str:
    parts: list[str] = []
    for b in resp.content:
        if isinstance(b, TextBlock):
            parts.append(b.text)
    return "\n".join(parts).strip()
