"""SystemPromptBuilder — assemble static fragments by routing tier."""
from __future__ import annotations

from functools import cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"

TIER_FRAGMENTS: dict[int, list[str]] = {
    0: ["base", "code_analysis"],
    1: ["base", "concise"],
    2: ["base"],
    3: ["base", "security"],
}


@cache
def _load_fragment(name: str) -> str:
    path = _PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


class SystemPromptBuilder:
    def build(
        self,
        tier: int = 2,
        memory_content: str | None = None,
        skill_summaries: str = "",
        context_hints: list[str] | None = None,
    ) -> str:
        fragments = list(TIER_FRAGMENTS.get(tier, ["base"]))
        if context_hints and "rag" in context_hints:
            fragments.append("rag_synthesis")
        parts = [_load_fragment(f) for f in fragments]
        if skill_summaries:
            parts.append(f"## Available Skills\n{skill_summaries}")
        if memory_content:
            parts.append(f"## Project Memory\n{memory_content}")
        return "\n\n".join(p for p in parts if p)
