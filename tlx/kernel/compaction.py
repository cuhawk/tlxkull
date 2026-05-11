"""Conversation compaction — summarize older turns with a cheap engine."""
from __future__ import annotations

from dataclasses import dataclass

from kernel.engine import Engine
from kernel.schema import Message, TextBlock

COMPACTION_RUBRIC = """\
Summarize this conversation. Output exactly these four sections:
## Facts established
## Tool results (key findings only)
## Decisions made
## Open questions / next steps
Be terse. Preserve all technical specifics verbatim (paths, hashes,
CVEs, payloads, URLs). Do not add commentary."""


@dataclass
class CompactionResult:
    summary: str
    turns_replaced: int


class Compactor:
    def __init__(self, summary_engine: Engine) -> None:
        self._engine = summary_engine

    async def compact(
        self,
        messages: list[Message],
        keep_recent: int = 4,
    ) -> tuple[list[Message], CompactionResult]:
        if len(messages) <= keep_recent:
            return messages, CompactionResult(summary="", turns_replaced=0)

        older = messages[:-keep_recent]
        recent = messages[-keep_recent:]

        resp = await self._engine.respond(older, [], COMPACTION_RUBRIC)
        summary = _extract_text(resp)

        compacted: list[Message] = [
            Message(role="user", content=f"[Context summary]\n{summary}"),
            Message(role="assistant", content="Understood."),
            *recent,
        ]
        return compacted, CompactionResult(
            summary=summary,
            turns_replaced=len(messages) - keep_recent,
        )


def _extract_text(resp: object) -> str:
    parts: list[str] = []
    for block in getattr(resp, "content", []) or []:
        if isinstance(block, TextBlock):
            parts.append(block.text)
    return "\n".join(parts).strip()
