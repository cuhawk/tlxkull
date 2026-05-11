"""Tests for sourcemap_extractor tool."""
from __future__ import annotations

import base64
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from modules.js_analyzer.tools.sourcemap_extractor import extract_source_map


def _make_map(sources, contents=None):
    m = {"version": 3, "sources": sources, "mappings": ""}
    if contents is not None:
        m["sourcesContent"] = contents
    return json.dumps(m)


def test_extracts_inline_data_uri(tmp_path):
    map_json = _make_map(["src/app.ts"], ["const x = 1;"])
    b64 = base64.b64encode(map_json.encode()).decode()
    js = (
        f"console.log(1)\n"
        f"//# sourceMappingURL=data:application/json;base64,{b64}\n"
    )
    js_file = tmp_path / "app.js"
    js_file.write_text(js)

    result = extract_source_map(
        str(js_file), "https://example.com/app.js", str(tmp_path / "out")
    )
    assert result["method"] == "inline_data"
    assert result["sources_count"] == 1
    assert result["has_content"] is True
    assert result["error"] is None
    written = list(Path(result["output_dir"]).rglob("*.ts"))
    assert len(written) == 1


def test_extracts_relative_comment(tmp_path):
    map_json = _make_map(["src/main.ts"], ["export {}"])
    js = "// code\n//# sourceMappingURL=app.js.map\n"
    js_file = tmp_path / "app.js"
    js_file.write_text(js)

    map_resp = MagicMock()
    map_resp.status_code = 200
    map_resp.text = map_json
    map_resp.raise_for_status = MagicMock()

    with patch(
        "modules.js_analyzer.tools.sourcemap_extractor.requests.get",
        return_value=map_resp,
    ):
        result = extract_source_map(
            str(js_file),
            "https://example.com/js/app.js",
            str(tmp_path / "out"),
        )
    assert result["method"] == "comment_relative"
    assert result["sources_count"] == 1


def test_returns_not_found_gracefully(tmp_path):
    js_file = tmp_path / "plain.js"
    js_file.write_text("console.log(1)\n")

    with patch(
        "modules.js_analyzer.tools.sourcemap_extractor.requests.get",
        side_effect=Exception("404"),
    ):
        result = extract_source_map(
            str(js_file),
            "https://example.com/plain.js",
            str(tmp_path / "out"),
        )
    assert result["method"] == "not_found"
    assert result["sources_count"] == 0


def test_sanitises_traversal_paths(tmp_path):
    map_json = _make_map(["../../etc/passwd"], ["root:x:0:0"])
    b64 = base64.b64encode(map_json.encode()).decode()
    js = (
        f"x\n//# sourceMappingURL=data:application/json;base64,{b64}\n"
    )
    js_file = tmp_path / "app.js"
    js_file.write_text(js)

    result = extract_source_map(
        str(js_file), "https://example.com/app.js", str(tmp_path / "out")
    )
    for f in result["files_written"]:
        assert "etc" not in f or "passwd" not in f
        assert ".." not in f
