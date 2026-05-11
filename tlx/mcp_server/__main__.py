"""Entrypoint: `python -m mcp_server`."""
from __future__ import annotations

import asyncio

from kernel import Kernel
from kernel.config import load_config
from mcp_server.server import run


async def main() -> None:
    cfg = load_config()
    kernel = await Kernel.boot(config=cfg, surface="mcp")
    try:
        await run(kernel)
    finally:
        kernel.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
