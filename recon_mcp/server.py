"""recon-mcp stdio server entrypoint."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import mcp.types as types
import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import load_config
from .do_client import DOClient
from .handlers.cancel import handle_cancel
from .handlers.cleanup import handle_cleanup_orphans
from .handlers.list_jobs import handle_list_jobs
from .handlers.results import handle_results
from .handlers.start import handle_start
from .handlers.status import handle_status
from .jobs import JobStore
from .tools import (
    ReconCancelIn,
    ReconResultsIn,
    ReconStartIn,
    ReconStatusIn,
)

log = structlog.get_logger(__name__)

_TOOL_NAMES = (
    "recon_start",
    "recon_status",
    "recon_results",
    "recon_cancel",
    "recon_list_jobs",
    "recon_cleanup_orphans",
)


def _ok(data) -> list[types.TextContent]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    return [types.TextContent(type="text", text=json.dumps(data, indent=2, default=str))]


async def build_server() -> Server:
    cfg = load_config()
    store = JobStore(db_path=str(cfg.db_path))
    await store.init()
    do = DOClient(token=cfg.do_api_token)
    artifacts_root = Path(os.environ.get("RECON_ARTIFACTS_ROOT", "targets")).resolve()
    artifacts_root.mkdir(parents=True, exist_ok=True)

    try:
        await handle_cleanup_orphans(store=store, do=do)
    except Exception as e:
        log.warning("orphan_sweep_failed", err=str(e))

    srv: Server = Server("recon-mcp")

    @srv.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="recon_start",
                description="Start a recon job over targets",
                inputSchema=ReconStartIn.model_json_schema(),
            ),
            types.Tool(
                name="recon_status",
                description="Get a job's status",
                inputSchema=ReconStatusIn.model_json_schema(),
            ),
            types.Tool(
                name="recon_results",
                description="Get the structured summary for a done job",
                inputSchema=ReconResultsIn.model_json_schema(),
            ),
            types.Tool(
                name="recon_cancel",
                description="Cancel a job and destroy its droplets",
                inputSchema=ReconCancelIn.model_json_schema(),
            ),
            types.Tool(
                name="recon_list_jobs",
                description="List recent jobs",
                inputSchema={"type": "object"},
            ),
            types.Tool(
                name="recon_cleanup_orphans",
                description="Destroy orphaned recon-mcp droplets",
                inputSchema={"type": "object"},
            ),
        ]

    @srv.call_tool()
    async def _call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
        args = arguments or {}
        if name == "recon_start":
            return _ok(await handle_start(ReconStartIn(**args), store=store, cfg=cfg, artifacts_root=artifacts_root))
        if name == "recon_status":
            return _ok(await handle_status(ReconStatusIn(**args), store=store))
        if name == "recon_results":
            return _ok(await handle_results(ReconResultsIn(**args), store=store))
        if name == "recon_cancel":
            return _ok(await handle_cancel(ReconCancelIn(**args), store=store, do=do))
        if name == "recon_list_jobs":
            return _ok(await handle_list_jobs(store=store))
        if name == "recon_cleanup_orphans":
            return _ok(await handle_cleanup_orphans(store=store, do=do))
        raise ValueError(f"unknown tool: {name}")

    return srv


async def _main() -> None:
    srv = await build_server()
    async with stdio_server() as (r, w):
        await srv.run(r, w, srv.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
