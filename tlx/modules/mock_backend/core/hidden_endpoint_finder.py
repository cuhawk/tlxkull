"""Find paths observed during execution-driven discovery that are NOT in
the route_specs extracted statically by route_extractor.

Inputs:
    known    : list of RouteSpec (or any object with ``.path`` /
               ``.url`` attribute, or dicts with same keys)
    observed : list[str] of full URLs observed during execution_loop

Output:
    list[str] of paths in observed but not in known.

Templated routes (route_extractor emits ``*`` for collapsed template-
literal interpolation, e.g. ``/api/users/*/posts``) are matched
against observed paths via regex: each ``*`` segment becomes
``[^/]+`` (single segment, never crosses ``/``) and the pattern is
anchored. Routes without ``*`` fall through the literal-equality
fast path.
"""
from __future__ import annotations

import re
import urllib.parse
from typing import Any


def _url_to_path(url: str) -> str:
    if not url:
        return ""
    return urllib.parse.urlparse(url).path or "/"


def _route_path(route: Any) -> str:
    if isinstance(route, dict):
        v = route.get("path") or route.get("url") or ""
    else:
        v = getattr(route, "path", None) or getattr(route, "url", "") or ""
    return _url_to_path(str(v)) if str(v).startswith("http") else str(v)


def _route_pattern(path: str) -> re.Pattern[str]:
    """Convert a route path with ``*`` segments to an anchored regex.

    ``*`` matches a single path segment (``[^/]+``), never crossing a
    slash. Other characters are escaped.
    """
    parts = path.split("*")
    regex = "[^/]+".join(re.escape(p) for p in parts)
    return re.compile(rf"^{regex}$")


def find_hidden(known: list, observed: list[str]) -> list[str]:
    known_paths: set[str] = {_route_path(r) for r in known if r is not None}
    templated = [p for p in known_paths if "*" in p]
    patterns = [_route_pattern(p) for p in templated]
    out: list[str] = []
    seen: set[str] = set()
    for u in observed or []:
        if not isinstance(u, str):
            continue
        path = _url_to_path(u)
        if not path or path in seen:
            continue
        if path in known_paths:
            continue
        if any(pat.match(path) for pat in patterns):
            continue
        seen.add(path)
        out.append(path)
    return out
