"""Build shaped JSON responses for routes — variants for probe injection."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .route_extractor import RouteSpec

PROBE_SENTINEL = "<probe>"


def _walk_replace(node: Any, replacer) -> Any:
    if isinstance(node, dict):
        return {k: _walk_replace(v, replacer) for k, v in node.items()}
    if isinstance(node, list):
        return [_walk_replace(v, replacer) for v in node]
    if isinstance(node, str):
        return replacer(node)
    return node


def build_response(
    route: RouteSpec,
    probe_id: str,
    variant: str = "default",
) -> Any:
    """Build a JSON-serialisable response for `route` keyed by `variant`."""
    if variant in ("admin_role", "pp_payload", "redirect"):
        raise NotImplementedError("7D")

    if variant == "default":
        return _build_default(route, probe_id)

    if variant == "deep_xss":
        return _build_deep_xss(route, probe_id)

    raise ValueError(f"unknown variant: {variant}")


def _build_default(route: RouteSpec, probe_id: str) -> Any:
    if route.shape_hint is None:
        return {"data": probe_id}
    shape = deepcopy(route.shape_hint)

    def repl(s: str) -> str:
        return probe_id if s == PROBE_SENTINEL else s

    return _walk_replace(shape, repl)


def _build_deep_xss(route: RouteSpec, probe_id: str) -> Any:
    payload = (
        f'{probe_id}<img src=x onerror=__tlxBeacon("{probe_id}")>'
    )
    if route.shape_hint is None:
        return {"data": payload}
    shape = deepcopy(route.shape_hint)

    def repl(s: str) -> str:
        return payload if s == PROBE_SENTINEL else s

    return _walk_replace(shape, repl)
