"""mcp_server.server: build_mcp_tools + dispatch_tool + lifecycle."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import mcp.types as types
import pytest

from kernel import Kernel
from kernel.tools import Tool
from mcp_server import server as srv
from mcp_server.allowlist import TOOL_ALLOWLIST


async def _boot_with_tools(tmp_path: Path) -> Kernel:
    kernel = await Kernel.boot(
        config_path=tmp_path / "missing-config.toml",
        db_path=tmp_path / "sessions.db",
        plugin_paths=[tmp_path / "no-plugins"],
        module_paths=[tmp_path / "no-modules"],
        surface="mcp",
    )
    # Register two tools: one allowlisted, one not.
    allowlisted = next(iter(TOOL_ALLOWLIST))
    kernel.tools.register(Tool(
        name=allowlisted,
        description=f"stub for {allowlisted}",
        params={
            "type": "object",
            "properties": {"x": {"type": "string"}},
            "required": [],
        },
        handler=lambda **kw: f"echo:{kw}",
    ))
    kernel.tools.register(Tool(
        name="not_allowlisted_xyz",
        description="must not surface",
        params={"type": "object", "properties": {}},
        handler=lambda **kw: "nope",
    ))
    return kernel


@pytest.mark.asyncio
async def test_build_mcp_tools_filters_to_allowlist(tmp_path: Path) -> None:
    kernel = await _boot_with_tools(tmp_path)
    try:
        out = srv.build_mcp_tools(kernel)
        names = {t.name for t in out}
        assert names <= TOOL_ALLOWLIST
        assert "not_allowlisted_xyz" not in names
        # at least the one we registered comes through
        assert any(t.name in TOOL_ALLOWLIST for t in out)
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_build_mcp_tools_fields_populated(tmp_path: Path) -> None:
    kernel = await _boot_with_tools(tmp_path)
    try:
        out = srv.build_mcp_tools(kernel)
        assert out, "expected at least one allowlisted tool"
        for t in out:
            assert isinstance(t, types.Tool)
            assert t.name and isinstance(t.name, str)
            assert t.description and isinstance(t.description, str)
            assert isinstance(t.inputSchema, dict)
            assert t.inputSchema.get("type") == "object"
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_build_mcp_tools_ignores_tool_search_mode(tmp_path: Path) -> None:
    """all_real() means tool_search_mode does not hide allowlisted tools."""
    kernel = await _boot_with_tools(tmp_path)
    try:
        kernel.tools.tool_search_mode = True
        out = srv.build_mcp_tools(kernel)
        assert out, "tool_search_mode must not hide allowlisted tools from MCP"
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_dispatch_tool_unknown_raises(tmp_path: Path) -> None:
    kernel = await _boot_with_tools(tmp_path)
    try:
        with pytest.raises(ValueError, match="not in allowlist"):
            await srv.dispatch_tool(kernel, "not_allowlisted_xyz", {})
        with pytest.raises(ValueError, match="not in allowlist"):
            await srv.dispatch_tool(kernel, "definitely_not_a_tool", {})
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_dispatch_tool_returns_text_content(tmp_path: Path) -> None:
    kernel = await _boot_with_tools(tmp_path)
    try:
        allowlisted = next(iter(TOOL_ALLOWLIST))
        out = await srv.dispatch_tool(kernel, allowlisted, {"x": "hi"})
        assert isinstance(out, list)
        assert len(out) == 1
        assert isinstance(out[0], types.TextContent)
        assert out[0].type == "text"
        assert "hi" in out[0].text
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_dispatch_tool_serializes_non_string(tmp_path: Path) -> None:
    kernel = await _boot_with_tools(tmp_path)
    try:
        allowlisted = "stub_returning_dict_" + next(iter(TOOL_ALLOWLIST))
        # second registration with same name forbidden — instead reuse
        # allowlisted by replacing its handler indirectly. Use another allowlisted
        # entry to keep things clean.
        another = sorted(TOOL_ALLOWLIST - {next(iter(TOOL_ALLOWLIST))})[0]
        kernel.tools.register(Tool(
            name=another,
            description="dict returner",
            params={"type": "object", "properties": {}},
            handler=lambda **kw: {"k": 1, "v": [1, 2]},
        ))
        out = await srv.dispatch_tool(kernel, another, {})
        assert out[0].text == '{"k": 1, "v": [1, 2]}'
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_make_server_handlers_present(tmp_path: Path) -> None:
    kernel = await _boot_with_tools(tmp_path)
    try:
        server = srv.make_server(kernel)
        assert server.name == "tlx-mcp"
        # Handlers registered for ListTools + CallTool requests.
        assert types.ListToolsRequest in server.request_handlers
        assert types.CallToolRequest in server.request_handlers
    finally:
        kernel.shutdown()


@pytest.mark.asyncio
async def test_run_eof_triggers_shutdown_path(tmp_path: Path) -> None:
    """When stdio_server context exits, run() returns; the caller's finally
    block (in __main__.main) calls kernel.shutdown(), firing on_shutdown hooks.
    Mock stdio_server to exit immediately and verify the path."""
    kernel = await _boot_with_tools(tmp_path)
    fired: list[str] = []
    kernel.on_shutdown(lambda: fired.append("hook"))

    class _StubStreams:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> tuple[Any, Any]:
            return (object(), object())

        async def __aexit__(self, *exc: Any) -> None:
            self.closed = True

    stub = _StubStreams()

    async def _fake_run(self_, read, write, init_opts) -> None:  # noqa: ARG001
        return None

    with patch("mcp_server.server.stdio_server", return_value=stub), \
         patch("mcp.server.lowlevel.server.Server.run", _fake_run):
        await srv.run(kernel)

    # Stub context exited cleanly.
    assert stub.closed is True
    # Now drive the lifecycle finally — same shape as __main__.main
    kernel.shutdown()
    assert "hook" in fired
