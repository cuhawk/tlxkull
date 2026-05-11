"""Source map fetcher and decoder — extracts original sources from .js.map files."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests

_UA = "tlx-js-recon/0.1"
_TIMEOUT = 15
_MAX_DEPTH = 10


def _find_sourcemap_comment(content: str) -> str | None:
    lines = content.splitlines()
    for line in lines[-5:][::-1]:
        m = re.search(r"//#\s*sourceMappingURL\s*=\s*(\S+)", line)
        if m:
            return m.group(1)
    return None


def _sanitise_source_path(source: str) -> str:
    raw = source
    for prefix in ("webpack:///", "webpack://", "webpack:/"):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
            break
    had_traversal = ".." in raw
    raw = raw.lstrip("./")
    if had_traversal:
        return Path(raw).name or "_"
    parts = [p for p in raw.split("/") if p and p != "."]
    if len(parts) > _MAX_DEPTH:
        parts = parts[-_MAX_DEPTH:]
    return "/".join(parts) if parts else "_"


def _fetch(url: str) -> requests.Response:
    return requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": _UA})


def extract_source_map(
    js_path: str,
    base_url: str,
    output_dir: str,
) -> dict:
    out_dir_path = Path(output_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    result: dict = {
        "method": "not_found",
        "map_url": None,
        "sources_count": 0,
        "has_content": False,
        "output_dir": str(out_dir_path),
        "files_written": [],
        "error": None,
    }

    js_p = Path(js_path)
    try:
        content = js_p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        result["error"] = f"read failed: {e}"
        return result

    map_text: str | None = None
    map_url: str | None = None
    method = "not_found"

    comment_value = _find_sourcemap_comment(content)
    if comment_value:
        if comment_value.startswith("data:application/json"):
            try:
                _, b64 = comment_value.split(";base64,", 1)
                map_text = base64.b64decode(b64).decode(
                    "utf-8", errors="replace"
                )
                method = "inline_data"
                map_url = comment_value
            except Exception as e:
                result["error"] = f"data uri decode failed: {e}"
        elif comment_value.startswith(("http://", "https://")):
            map_url = comment_value
            method = "comment_absolute"
            try:
                r = _fetch(map_url)
                r.raise_for_status()
                map_text = r.text
            except Exception as e:
                result["error"] = f"map fetch failed: {e}"
        else:
            map_url = urljoin(base_url, comment_value)
            method = "comment_relative"
            try:
                r = _fetch(map_url)
                r.raise_for_status()
                map_text = r.text
            except Exception as e:
                result["error"] = f"map fetch failed: {e}"

    if map_text is None:
        try:
            r = _fetch(base_url)
            hdr = r.headers.get("SourceMap") or r.headers.get("X-SourceMap")
            if hdr:
                hdr_url = (
                    hdr if hdr.startswith(("http://", "https://"))
                    else urljoin(base_url, hdr)
                )
                rm = _fetch(hdr_url)
                rm.raise_for_status()
                map_text = rm.text
                map_url = hdr_url
                method = "header"
        except Exception:
            pass

    if map_text is None:
        sibling = base_url + ".map"
        try:
            r = _fetch(sibling)
            r.raise_for_status()
            map_text = r.text
            map_url = sibling
            method = "comment_relative"
        except Exception:
            pass

    if map_text is None:
        result["method"] = method
        result["map_url"] = map_url
        return result

    try:
        map_json = json.loads(map_text)
    except Exception as e:
        result["error"] = f"map parse failed: {e}"
        result["method"] = method
        result["map_url"] = map_url
        return result

    sources = map_json.get("sources") or []
    sources_content = map_json.get("sourcesContent") or []

    written: list[str] = []
    has_content = False
    for i, src in enumerate(sources):
        if not isinstance(src, str):
            continue
        rel = _sanitise_source_path(src)
        target = out_dir_path / "original" / rel
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            continue
        body: str | None = None
        if i < len(sources_content):
            sc = sources_content[i]
            if isinstance(sc, str) and sc:
                body = sc
                has_content = True
        if body is None and map_url and not map_url.startswith("data:"):
            try:
                src_url = (
                    src if src.startswith(("http://", "https://"))
                    else urljoin(map_url, src)
                )
                rsrc = _fetch(src_url)
                if rsrc.status_code == 200:
                    body = rsrc.text
            except Exception:
                body = None
        if body is not None:
            try:
                target.write_text(body, encoding="utf-8", errors="replace")
                written.append(str(target))
            except Exception:
                continue

    result["method"] = method
    result["map_url"] = map_url
    result["sources_count"] = len(sources)
    result["has_content"] = has_content
    result["files_written"] = written
    return result
