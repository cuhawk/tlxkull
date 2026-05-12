"""Async DigitalOcean v2 REST client — only the slice recon-mcp needs."""
from __future__ import annotations

import asyncio
from typing import Any

import httpx


class DOAPIError(Exception):
    pass


_BASE = "https://api.digitalocean.com/v2"


class DOClient:
    def __init__(self, token: str, timeout: float = 30.0) -> None:
        self._token = token
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    async def _req(self, method: str, path: str, **kw: Any) -> httpx.Response:
        url = f"{_BASE}{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as c:
            for attempt in range(3):
                r = await c.request(method, url, headers=self._headers(), **kw)
                if r.status_code == 429 and attempt < 2:
                    delay = float(r.headers.get("retry-after", "1"))
                    await asyncio.sleep(max(delay, 0.1))
                    continue
                return r
            raise DOAPIError(f"429 after retries: {r.text}")

    async def create_ssh_key(self, name: str, public_key: str) -> dict:
        r = await self._req("POST", "/account/keys", json={"name": name, "public_key": public_key})
        if r.status_code != 201:
            raise DOAPIError(f"ssh_key create failed: {r.status_code} {r.text}")
        return r.json()["ssh_key"]

    async def delete_ssh_key(self, key_id: int) -> None:
        r = await self._req("DELETE", f"/account/keys/{key_id}")
        if r.status_code not in (204, 404):
            raise DOAPIError(f"ssh_key delete failed: {r.status_code} {r.text}")

    async def create_droplet(
        self, *, name: str, region: str, size: str, image: str,
        ssh_key_ids: list[int], user_data: str, tags: list[str],
    ) -> dict:
        body = {
            "name": name, "region": region, "size": size, "image": image,
            "ssh_keys": ssh_key_ids, "user_data": user_data, "tags": tags,
            "ipv6": False, "monitoring": False,
        }
        r = await self._req("POST", "/droplets", json=body)
        if r.status_code != 202:
            raise DOAPIError(f"droplet create failed: {r.status_code} {r.text}")
        return r.json()["droplet"]

    async def get_droplet(self, droplet_id: int) -> dict:
        r = await self._req("GET", f"/droplets/{droplet_id}")
        if r.status_code == 429:
            raise DOAPIError(f"429 after retries: {r.text}")
        if r.status_code != 200:
            raise DOAPIError(f"droplet get failed: {r.status_code} {r.text}")
        return r.json()["droplet"]

    async def destroy_droplet(self, droplet_id: int) -> None:
        r = await self._req("DELETE", f"/droplets/{droplet_id}")
        if r.status_code not in (204, 404):
            raise DOAPIError(f"droplet destroy failed: {r.status_code} {r.text}")

    async def list_by_tag(self, tag: str) -> list[dict]:
        r = await self._req("GET", "/droplets", params={"tag_name": tag})
        if r.status_code != 200:
            raise DOAPIError(f"list droplets failed: {r.status_code} {r.text}")
        return r.json().get("droplets", [])
