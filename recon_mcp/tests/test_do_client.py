import httpx
import pytest
import respx
from recon_mcp.do_client import DOClient, DOAPIError


@pytest.fixture
def client():
    return DOClient(token="t0k3n")


@respx.mock
@pytest.mark.asyncio
async def test_create_ssh_key(client):
    respx.post("https://api.digitalocean.com/v2/account/keys").mock(
        return_value=httpx.Response(201, json={"ssh_key": {"id": 42, "fingerprint": "ab:cd"}})
    )
    res = await client.create_ssh_key(name="job-abc", public_key="ssh-ed25519 AAA...")
    assert res["id"] == 42


@respx.mock
@pytest.mark.asyncio
async def test_create_droplet_returns_id(client):
    respx.post("https://api.digitalocean.com/v2/droplets").mock(
        return_value=httpx.Response(202, json={"droplet": {"id": 999, "status": "new"}})
    )
    res = await client.create_droplet(
        name="recon-1", region="nyc1", size="s-2vcpu-4gb",
        image="ubuntu-24-04-x64", ssh_key_ids=[42], user_data="#!/bin/bash\necho hi",
        tags=["recon", "job:abc"],
    )
    assert res["id"] == 999


@respx.mock
@pytest.mark.asyncio
async def test_get_droplet(client):
    respx.get("https://api.digitalocean.com/v2/droplets/999").mock(
        return_value=httpx.Response(200, json={"droplet": {
            "id": 999, "status": "active",
            "networks": {"v4": [{"type": "public", "ip_address": "1.2.3.4"}]},
        }})
    )
    res = await client.get_droplet(999)
    assert res["status"] == "active"


@respx.mock
@pytest.mark.asyncio
async def test_destroy_droplet(client):
    respx.delete("https://api.digitalocean.com/v2/droplets/999").mock(
        return_value=httpx.Response(204)
    )
    await client.destroy_droplet(999)


@respx.mock
@pytest.mark.asyncio
async def test_list_by_tag(client):
    respx.get("https://api.digitalocean.com/v2/droplets").mock(
        return_value=httpx.Response(200, json={"droplets": [
            {"id": 1, "name": "a"}, {"id": 2, "name": "b"},
        ]})
    )
    res = await client.list_by_tag("recon")
    assert [d["id"] for d in res] == [1, 2]


@respx.mock
@pytest.mark.asyncio
async def test_list_by_tag_pagination(client):
    """Follows `links.pages.next` across pages so >200-droplet runs don't silently truncate."""
    call_count = {"n": 0}

    def _handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        if call_count["n"] == 1:
            return httpx.Response(200, json={
                "droplets": [{"id": 1}, {"id": 2}],
                "links": {"pages": {
                    "next": "https://api.digitalocean.com/v2/droplets?tag_name=recon&page=2&per_page=200",
                }},
            })
        return httpx.Response(200, json={"droplets": [{"id": 3}]})

    respx.get("https://api.digitalocean.com/v2/droplets").mock(side_effect=_handler)
    res = await client.list_by_tag("recon")
    assert [d["id"] for d in res] == [1, 2, 3]
    assert call_count["n"] == 2


@respx.mock
@pytest.mark.asyncio
async def test_429_retries_then_raises(client):
    respx.get("https://api.digitalocean.com/v2/droplets/999").mock(
        side_effect=[
            httpx.Response(429, headers={"retry-after": "0"}, json={"id": "too_many", "message": "slow down"}),
            httpx.Response(429, headers={"retry-after": "0"}, json={"id": "too_many", "message": "slow down"}),
            httpx.Response(429, headers={"retry-after": "0"}, json={"id": "too_many", "message": "slow down"}),
        ]
    )
    with pytest.raises(DOAPIError, match="429"):
        await client.get_droplet(999)
