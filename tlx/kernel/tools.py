"""Unified tool contract — engine-agnostic Tool + ToolRegistry."""
from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# JSON Schema fields engines accept. Anything else stripped.
_ALLOWED_SCHEMA_KEYS: frozenset[str] = frozenset({
    "type",
    "properties",
    "required",
    "items",
    "enum",
    "description",
    "additionalProperties",
    "anyOf",
    "oneOf",
    "allOf",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
    "pattern",
    "format",
    "minItems",
    "maxItems",
    "uniqueItems",
    "default",
    "title",
})

_TOOL_SEARCH_NAME = "tool_search"
_TOOL_SEARCH_DESCRIPTION = (
    "Search registered tools by keyword. Returns matching tool declarations. "
    "Use when the desired tool is not directly visible."
)
_TOOL_SEARCH_PARAMS: dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Search keyword(s) for matching tool names/descriptions.",
        },
    },
    "required": ["query"],
}


class SchemaError(ValueError):
    """Raised when a tool's params dict is not a valid JSON-Schema object."""


@dataclass
class Tool:
    name: str
    description: str
    params: dict[str, Any]
    handler: Callable[..., Any]
    requires: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.params = normalize_schema(self.params)


def normalize_schema(params: dict[str, Any]) -> dict[str, Any]:
    """Strip unsupported fields recursively. Validate required structure."""
    if not isinstance(params, dict):
        raise SchemaError(f"params must be dict, got {type(params).__name__}")
    if "type" not in params:
        raise SchemaError("schema root must declare 'type'")
    if params["type"] == "object" and "properties" not in params:
        raise SchemaError("object schema must declare 'properties'")
    return _strip(params)


def _strip(node: Any) -> Any:
    if isinstance(node, dict):
        cleaned: dict[str, Any] = {}
        for k, v in node.items():
            if k.startswith("$"):
                continue
            if k not in _ALLOWED_SCHEMA_KEYS and k != "properties":
                continue
            if k == "properties" and isinstance(v, dict):
                cleaned[k] = {pk: _strip(pv) for pk, pv in v.items()}
            elif k in ("items", "additionalProperties") and isinstance(v, dict):
                cleaned[k] = _strip(v)
            elif k in ("anyOf", "oneOf", "allOf") and isinstance(v, list):
                cleaned[k] = [_strip(x) for x in v]
            else:
                cleaned[k] = v
        return cleaned
    return node


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self.tool_search_mode: bool = False

    def register(self, tool: Tool) -> None:
        if tool.name == _TOOL_SEARCH_NAME:
            raise ValueError(f"'{_TOOL_SEARCH_NAME}' is reserved")
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        """All visible tools. In search mode, returns only the meta-tool."""
        if self.tool_search_mode:
            return [self._build_search_tool()]
        return list(self._tools.values())

    def all_real(self) -> list[Tool]:
        """All registered tools, ignoring search mode (for internal use)."""
        return list(self._tools.values())

    async def dispatch(self, name: str, args: dict[str, Any]) -> Any:
        if name == _TOOL_SEARCH_NAME:
            return self._search(args.get("query", ""))
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"unknown tool: {name}")
        result = tool.handler(**args)
        if inspect.isawaitable(result):
            return await result
        return result

    def _build_search_tool(self) -> Tool:
        return Tool(
            name=_TOOL_SEARCH_NAME,
            description=_TOOL_SEARCH_DESCRIPTION,
            params=dict(_TOOL_SEARCH_PARAMS),
            handler=lambda query: self._search(query),
        )

    def _search(self, query: str) -> list[dict[str, Any]]:
        q = (query or "").lower().strip()
        out: list[dict[str, Any]] = []
        for tool in self._tools.values():
            if not q or q in tool.name.lower() or q in tool.description.lower():
                out.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "params": tool.params,
                    }
                )
        return out
