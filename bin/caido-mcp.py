#!/usr/bin/env python3
"""Caido MCP wrapper — stdio MCP server exposing Caido GraphQL operations.

Skills consume these tools:
  caido-capture  → caido_health, caido_project_ensure, caido_scope_set
  caido-replay   → caido_request_get, caido_replay, caido_diff
  caido-idor     → caido_requests_list, caido_workflow_run, caido_replay (batch)

Each tool is a thin wrapper over Caido's local GraphQL endpoint (default
http://127.0.0.1:8080/api/graphql; override via CAIDO_API_URL env). The
GraphQL schema differs slightly across Caido releases — every tool below
is marked TODO(caido-api) where the operation string must be verified
against the running Caido version. Run `caido_introspect()` once to see
the live schema and update.

Install deps:
  uv pip install mcp httpx structlog python-dotenv

Run standalone:
  python bin/caido-mcp.py
Wired via .claude/settings.json as the "caido" MCP server.
"""
from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import httpx
import mcp.types as types
import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server

log = structlog.get_logger(__name__)

CAIDO_API_URL = os.environ.get("CAIDO_API_URL", "http://127.0.0.1:8080/api/graphql")
CAIDO_API_TOKEN = os.environ.get("CAIDO_API_TOKEN", "")  # optional bearer


# ----------------- low-level GraphQL helper -----------------

async def gql(query: str, variables: dict | None = None) -> dict:
    """Send a GraphQL request to Caido. Returns the JSON `data` field."""
    headers = {"Content-Type": "application/json"}
    if CAIDO_API_TOKEN:
        headers["Authorization"] = f"Bearer {CAIDO_API_TOKEN}"
    payload = {"query": query, "variables": variables or {}}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(CAIDO_API_URL, json=payload, headers=headers)
        r.raise_for_status()
        body = r.json()
    if "errors" in body and body["errors"]:
        raise RuntimeError(f"caido gql errors: {body['errors']}")
    return body.get("data", {})


# ----------------- tool implementations -----------------

async def caido_health() -> dict:
    """Probe Caido API. Returns version + reachable=True or an error dict."""
    try:
        # TODO(caido-api): replace `__schema { queryType { name } }` with a
        # real version query once we know the field name in your Caido build.
        data = await gql("{ __schema { queryType { name } } }")
        return {"reachable": True, "raw": data}
    except Exception as e:
        return {"reachable": False, "error": str(e),
                "hint": "Open Caido GUI → Settings → Other → enable API."}


async def caido_introspect() -> dict:
    """Full GraphQL introspection. Run once after installing Caido to
    discover the schema for project/request/replay/workflow operations,
    then update the TODO(caido-api) queries below."""
    query = """
    {
      __schema {
        queryType   { name fields { name args { name type { name } } } }
        mutationType{ name fields { name args { name type { name } } } }
      }
    }
    """
    return await gql(query)


async def caido_project_ensure(name: str) -> dict:
    """Ensure a Caido project named <name> exists; select it as current.
    TODO(caido-api): verify mutation names against your build."""
    # Try to find an existing project.
    listing = await gql(
        "query($q: String!){ projects(filter:{name:$q}){ id name } }",
        {"q": name},
    )
    projects = listing.get("projects", [])
    if projects:
        pid = projects[0]["id"]
    else:
        created = await gql(
            "mutation($n: String!){ createProject(input:{name:$n}){ id name } }",
            {"n": name},
        )
        pid = created["createProject"]["id"]
    # Select it.
    await gql(
        "mutation($i: ID!){ selectProject(id:$i){ id } }", {"i": pid},
    )
    return {"id": pid, "name": name, "created": not projects}


async def caido_scope_set(in_: list[str], out: list[str]) -> dict:
    """Set the current project's scope rules.
    TODO(caido-api): map `in_`/`out` to your scope-rules mutation shape."""
    q = """
    mutation($in: [String!]!, $out: [String!]!){
      setScope(input:{include:$in, exclude:$out}){ ok }
    }
    """
    return await gql(q, {"in": in_, "out": out})


async def caido_recent_requests(count: int = 50) -> dict:
    """List N most recent requests in the current project.
    TODO(caido-api): adjust field selection (host/path/method/status)."""
    q = """
    query($n: Int!){
      requests(first:$n, orderBy:{field:CREATED_AT, direction:DESC}){
        edges { node { id host method path status length } }
      }
    }
    """
    return await gql(q, {"n": count})


async def caido_request_get(request_id: str) -> dict:
    """Fetch a request by id with full headers + body for replay.
    TODO(caido-api): field names may differ; verify with introspection."""
    q = """
    query($id: ID!){
      request(id:$id){
        id method url
        headers { name value }
        body
        response { status length headers { name value } body }
      }
    }
    """
    return await gql(q, {"id": request_id})


async def caido_replay(request: dict, variant: dict) -> dict:
    """Replay a request with a variant mutation. Returns the new response.
    The variant shape is what `caido-replay` SKILL describes:
      { name, drop_headers?, set_headers?, method?, body?, param_fuzz? }

    TODO(caido-api): your build likely has a `replay` or `repeater.send`
    mutation that accepts a serialized request. Verify and replace."""
    modified = _apply_variant(request, variant)
    q = """
    mutation($req: ReplayRequestInput!){
      sendReplay(input:$req){
        response { status length headers { name value } body }
        durationMs
      }
    }
    """
    return await gql(q, {"req": modified})


async def caido_diff(req_a: dict, req_b: dict, ignore_headers: list[str] | None = None,
                    ignore_body_regex: list[str] | None = None) -> dict:
    """Pure-python diff. Not a Caido call — keep local for speed.

    Returns:
      { status_differs, length_delta, header_diff, body_normalized_diff }
    """
    import re
    ignore_headers = set(h.lower() for h in (ignore_headers or []))
    ignore_body_regex = ignore_body_regex or []

    a_resp = req_a.get("response", {})
    b_resp = req_b.get("response", {})

    def _normalize(body: str) -> str:
        for pat in ignore_body_regex:
            body = re.sub(pat, "<NORM>", body)
        return body

    def _hdr_dict(hs):
        return {h["name"].lower(): h["value"] for h in (hs or [])
                if h["name"].lower() not in ignore_headers}

    a_h = _hdr_dict(a_resp.get("headers", []))
    b_h = _hdr_dict(b_resp.get("headers", []))
    a_b = _normalize(a_resp.get("body", "") or "")
    b_b = _normalize(b_resp.get("body", "") or "")

    return {
        "status_a": a_resp.get("status"),
        "status_b": b_resp.get("status"),
        "status_differs": a_resp.get("status") != b_resp.get("status"),
        "length_a": len(a_b),
        "length_b": len(b_b),
        "length_delta": len(b_b) - len(a_b),
        "header_added":   sorted(set(b_h) - set(a_h)),
        "header_removed": sorted(set(a_h) - set(b_h)),
        "header_changed": [k for k in (set(a_h) & set(b_h)) if a_h[k] != b_h[k]],
        "body_equal_normalized": a_b == b_b,
    }


async def caido_workflow_run(workflow_id: str) -> dict:
    """Run a Caido workflow (e.g. a login automation) and return its
    output (typically a cookie / auth header to use in subsequent replays).
    TODO(caido-api): your Caido build's workflow API field names."""
    q = """
    mutation($id: ID!){
      runWorkflow(id:$id){
        ok output { name value }
      }
    }
    """
    return await gql(q, {"id": workflow_id})


# ----------------- helpers -----------------

def _apply_variant(request: dict, variant: dict) -> dict:
    """Build a modified request from a Caido request + variant spec."""
    out = json.loads(json.dumps(request))  # deep copy
    drops = set(h.lower() for h in variant.get("drop_headers", []))
    if drops:
        out["headers"] = [h for h in out.get("headers", [])
                          if h["name"].lower() not in drops]
    sets = variant.get("set_headers", {})
    if sets:
        existing_names = {h["name"].lower() for h in out.get("headers", [])}
        out["headers"] = [h for h in out.get("headers", [])
                          if h["name"].lower() not in {k.lower() for k in sets}]
        for k, v in sets.items():
            out["headers"].append({"name": k, "value": v})
    if "method" in variant:
        out["method"] = variant["method"]
    if "body" in variant:
        out["body"] = variant["body"]
    if "param_fuzz" in variant:
        # Caller is expected to expand param_fuzz into multiple variants
        # before this point. Leave passthrough.
        pass
    return out


# ----------------- MCP server -----------------

def make_server() -> Server:
    server: Server = Server("caido-mcp")

    tools: list[types.Tool] = [
        types.Tool(
            name="caido_health",
            description="Probe Caido API reachability. Call once on session start.",
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        types.Tool(
            name="caido_introspect",
            description="Full GraphQL introspection. Run once per Caido upgrade.",
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        types.Tool(
            name="caido_project_ensure",
            description="Ensure a Caido project named <name> exists and is current.",
            inputSchema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"], "additionalProperties": False,
            },
        ),
        types.Tool(
            name="caido_scope_set",
            description="Set in-/out-of-scope rules on the current Caido project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "in_": {"type": "array", "items": {"type": "string"}},
                    "out": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["in_", "out"], "additionalProperties": False,
            },
        ),
        types.Tool(
            name="caido_recent_requests",
            description="List the N most recent requests in the current project.",
            inputSchema={
                "type": "object",
                "properties": {"count": {"type": "integer", "default": 50}},
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="caido_request_get",
            description="Fetch a request by id with full headers + body + response.",
            inputSchema={
                "type": "object",
                "properties": {"request_id": {"type": "string"}},
                "required": ["request_id"], "additionalProperties": False,
            },
        ),
        types.Tool(
            name="caido_replay",
            description="Replay a Caido request with a variant mutation spec. Returns response.",
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {"type": "object"},
                    "variant": {"type": "object"},
                },
                "required": ["request", "variant"], "additionalProperties": False,
            },
        ),
        types.Tool(
            name="caido_diff",
            description="Pure-python diff of two replay responses with header/body ignore lists.",
            inputSchema={
                "type": "object",
                "properties": {
                    "req_a": {"type": "object"},
                    "req_b": {"type": "object"},
                    "ignore_headers": {"type": "array", "items": {"type": "string"}},
                    "ignore_body_regex": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["req_a", "req_b"], "additionalProperties": False,
            },
        ),
        types.Tool(
            name="caido_workflow_run",
            description="Run a Caido workflow (e.g. login automation). Returns output headers/cookies.",
            inputSchema={
                "type": "object",
                "properties": {"workflow_id": {"type": "string"}},
                "required": ["workflow_id"], "additionalProperties": False,
            },
        ),
    ]

    @server.list_tools()
    async def _list_tools():
        return tools

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        impls = {
            "caido_health": lambda: caido_health(),
            "caido_introspect": lambda: caido_introspect(),
            "caido_project_ensure": lambda: caido_project_ensure(**arguments),
            "caido_scope_set": lambda: caido_scope_set(**arguments),
            "caido_recent_requests": lambda: caido_recent_requests(**arguments),
            "caido_request_get": lambda: caido_request_get(**arguments),
            "caido_replay": lambda: caido_replay(**arguments),
            "caido_diff": lambda: caido_diff(**arguments),
            "caido_workflow_run": lambda: caido_workflow_run(**arguments),
        }
        if name not in impls:
            raise ValueError(f"unknown tool: {name}")
        result = await impls[name]()
        return [types.TextContent(type="text", text=json.dumps(result, default=str))]

    return server


async def main() -> None:
    server = make_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
