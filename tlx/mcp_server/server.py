"""MCP stdio server: tool listing + dispatch over the kernel ToolRegistry."""
from __future__ import annotations

import json
from typing import Any

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from kernel import Kernel
from mcp_server.allowlist import TOOL_ALLOWLIST


def build_mcp_tools(kernel: Kernel) -> list[types.Tool]:
    """Filter kernel.tools.all_real() by TOOL_ALLOWLIST, convert Tool -> mcp.types.Tool.

    Reuses Tool.params directly as inputSchema — One Tool model rule preserved.
    Uses all_real() so tool_search_mode does not hide allowlisted tools.
    """
    return [
        types.Tool(
            name=t.name,
            description=t.description,
            inputSchema=t.params,
        )
        for t in kernel.tools.all_real()
        if t.name in TOOL_ALLOWLIST
    ]


def _to_text(result: Any) -> str:
    if isinstance(result, str):
        return result
    try:
        return json.dumps(result)
    except (TypeError, ValueError):
        return str(result)


async def dispatch_tool(
    kernel: Kernel, name: str, arguments: dict[str, Any] | None,
) -> list[types.TextContent]:
    """Allowlist-gated tool dispatch. Raises ValueError on unknown name."""
    if name not in TOOL_ALLOWLIST:
        raise ValueError(f"tool {name!r} not in allowlist")
    result = await kernel.tools.dispatch(name, arguments or {})
    return [types.TextContent(type="text", text=_to_text(result))]


def make_server(kernel: Kernel) -> Server:
    """Build a configured MCP Server bound to the given kernel."""
    server: Server = Server("tlx-mcp")

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return build_mcp_tools(kernel)

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        return await dispatch_tool(kernel, name, arguments)

    return server


async def run(kernel: Kernel) -> None:
    server = make_server(kernel)
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
