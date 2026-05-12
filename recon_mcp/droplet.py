"""Droplet lifecycle: async context manager that provisions, runs SSH, and tears down."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

import asyncssh
import structlog

from .do_client import DOClient

log = structlog.get_logger(__name__)


class ProvisionError(Exception):
    pass


@dataclass
class Droplet:
    do: DOClient
    name: str
    region: str
    size: str
    image: str
    ssh_key_ids: list[int]
    user_data: str
    tags: list[str]
    ssh_private_key_path: str | None = None
    max_wait_sec: float = 300.0
    droplet_id: int | None = field(default=None, init=False)
    ip: str | None = field(default=None, init=False)

    async def _provision_and_wait(self, poll_interval: float = 5.0) -> str:
        created = await self.do.create_droplet(
            name=self.name, region=self.region, size=self.size, image=self.image,
            ssh_key_ids=self.ssh_key_ids, user_data=self.user_data, tags=self.tags,
        )
        self.droplet_id = created["id"]
        start = time.monotonic()
        while time.monotonic() - start < self.max_wait_sec:
            info = await self.do.get_droplet(self.droplet_id)
            if info.get("status") == "active":
                v4 = [n for n in info.get("networks", {}).get("v4", []) if n.get("type") == "public"]
                if v4:
                    self.ip = v4[0]["ip_address"]
                    return self.ip
            await asyncio.sleep(poll_interval)
        raise ProvisionError(f"droplet {self.droplet_id} provisioning timeout")

    async def _wait_bootstrap(self, poll_interval: float = 10.0, max_sec: float = 600.0) -> None:
        start = time.monotonic()
        while time.monotonic() - start < max_sec:
            try:
                rc, _, _ = await self.run("test -f /var/lib/recon/bootstrap.done", check=False)
                if rc == 0:
                    return
            except Exception as e:
                log.debug("bootstrap_poll_err", err=str(e))
            await asyncio.sleep(poll_interval)
        raise ProvisionError(f"droplet {self.droplet_id} bootstrap timeout")

    async def __aenter__(self) -> "Droplet":
        try:
            await self._provision_and_wait()
            await self._wait_bootstrap()
        except Exception:
            if self.droplet_id:
                await self.do.destroy_droplet(self.droplet_id)
            raise
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.droplet_id:
            try:
                await self.do.destroy_droplet(self.droplet_id)
            except Exception as e:
                log.error("destroy_failed", droplet_id=self.droplet_id, err=str(e))

    async def _connect(self) -> asyncssh.SSHClientConnection:
        assert self.ip and self.ssh_private_key_path, "not provisioned"
        return await asyncssh.connect(
            host=self.ip, username="root", client_keys=[self.ssh_private_key_path],
            known_hosts=None, connect_timeout=20,
        )

    async def run(self, cmd: str, *, check: bool = True, timeout: float = 1800.0) -> tuple[int, str, str]:
        async with await self._connect() as conn:
            r = await asyncio.wait_for(conn.run(cmd, check=False), timeout=timeout)
            if check and r.exit_status != 0:
                raise RuntimeError(f"remote cmd failed ({r.exit_status}): {cmd}\nSTDERR:\n{r.stderr}")
            return r.exit_status, r.stdout or "", r.stderr or ""

    async def pull(self, remote_path: str, local_path: str) -> None:
        async with await self._connect() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(remote_path, local_path, recurse=True)

    async def push(self, local_path: str, remote_path: str) -> None:
        async with await self._connect() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.put(local_path, remote_path, recurse=True)
