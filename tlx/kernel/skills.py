"""Skills registry — discover SKILL.md files, expose summaries + full read."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SkillMeta:
    name: str
    triggers: list[str] = field(default_factory=list)
    version: str = "0.0.0"
    path: Path = field(default_factory=Path)


class SkillsRegistry:
    def __init__(self, search_paths: list[Path]) -> None:
        self._search_paths = search_paths
        self._skills: dict[str, SkillMeta] = {}

    def discover(self) -> list[SkillMeta]:
        self._skills.clear()
        for root in self._search_paths:
            if not root.is_dir():
                continue
            for skill_path in sorted(root.glob("**/SKILL.md")):
                try:
                    text = skill_path.read_text(encoding="utf-8")
                except OSError:
                    continue
                meta = _parse_frontmatter(text, skill_path)
                if meta is None or not meta.name:
                    continue
                self._skills[meta.name] = meta
        return list(self._skills.values())

    def summaries_for_prompt(self) -> str:
        if not self._skills:
            return ""
        lines = []
        for name in sorted(self._skills):
            meta = self._skills[name]
            triggers = ", ".join(meta.triggers)
            lines.append(f"- {name} v{meta.version}: triggers=[{triggers}]")
        return "\n".join(lines)

    async def read_skill(self, name: str) -> str:
        meta = self._skills.get(name)
        if meta is None:
            raise KeyError(name)
        return await asyncio.to_thread(meta.path.read_text, encoding="utf-8")

    def get(self, name: str) -> SkillMeta | None:
        return self._skills.get(name)

    def all(self) -> list[SkillMeta]:
        return list(self._skills.values())


def _parse_frontmatter(text: str, path: Path) -> SkillMeta | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end < 0:
        return None

    name = ""
    version = "0.0.0"
    triggers: list[str] = []
    in_triggers = False
    for raw in lines[1:end]:
        line = raw.rstrip()
        if not line:
            in_triggers = False
            continue
        if in_triggers and line.lstrip().startswith("- "):
            triggers.append(line.lstrip()[2:].strip())
            continue
        in_triggers = False
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if key == "name":
            name = value
        elif key == "version":
            version = value or "0.0.0"
        elif key == "triggers":
            if value:
                inner = value.strip("[]")
                triggers = [
                    t.strip().strip("'\"") for t in inner.split(",") if t.strip()
                ]
            else:
                in_triggers = True

    return SkillMeta(name=name, triggers=triggers, version=version, path=path)
