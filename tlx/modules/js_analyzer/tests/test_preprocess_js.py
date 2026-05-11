"""Tests for preprocess_js tool."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from modules.js_analyzer.tools.preprocess_js import (
    _is_minified,
    preprocess_js,
)


def test_is_minified_single_long_line(tmp_path):
    f = tmp_path / "a.js"
    f.write_text("x" * 6000)
    assert _is_minified(f) is True


def test_is_minified_high_avg_line_length(tmp_path):
    f = tmp_path / "b.js"
    f.write_text(("x" * 400 + "\n") * 10)
    assert _is_minified(f) is True


def test_not_minified_normal_file(tmp_path):
    f = tmp_path / "c.js"
    f.write_text("function foo() {\n  return 1;\n}\n")
    assert _is_minified(f) is False


def test_is_minified_missing_file(tmp_path):
    assert _is_minified(tmp_path / "missing.js") is False


def test_passthrough_for_readable_file(tmp_path):
    src = tmp_path / "app.js"
    src.write_text("function foo() {\n  return 1;\n}\n")
    result = preprocess_js(str(src), str(tmp_path / "out"))
    assert result["method"] == "passthrough"
    assert result["was_minified"] is False
    assert result["processed"] == str(src)
    assert result["error"] is None


def test_preprocess_runs_on_minified(tmp_path):
    src = tmp_path / "min.js"
    src.write_text("x" * 6000)
    out_dir = tmp_path / "out"

    def fake_webcrack(js_path, output_path):
        output_path.write_text("function deobf() {\n  return 1;\n}\n")
        return True, None

    def fake_prettier(js_path, output_path):
        output_path.write_text("function deobf() {\n  return 1;\n}\n")
        return True

    with patch(
        "modules.js_analyzer.tools.preprocess_js._run_webcrack",
        side_effect=fake_webcrack,
    ), patch(
        "modules.js_analyzer.tools.preprocess_js._run_prettier",
        side_effect=fake_prettier,
    ):
        result = preprocess_js(str(src), str(out_dir))

    assert result["method"] == "webcrack+prettier"
    assert result["was_minified"] is True
    assert result["line_count_after"] > result["line_count_before"]
    assert result["error"] is None
    assert Path(result["processed"]).exists()


def test_preprocess_falls_back_to_prettier_only(tmp_path):
    src = tmp_path / "min.js"
    src.write_text("x" * 6000)
    out_dir = tmp_path / "out"

    def fake_webcrack(js_path, output_path):
        import shutil
        shutil.copy2(js_path, output_path)
        return False, None

    def fake_prettier(js_path, output_path):
        output_path.write_text("// prettified\nvar x = 1;\n")
        return True

    with patch(
        "modules.js_analyzer.tools.preprocess_js._run_webcrack",
        side_effect=fake_webcrack,
    ), patch(
        "modules.js_analyzer.tools.preprocess_js._run_prettier",
        side_effect=fake_prettier,
    ):
        result = preprocess_js(str(src), str(out_dir))

    assert result["method"] == "prettier"
    assert result["error"] is None


def test_preprocess_missing_file_returns_error(tmp_path):
    result = preprocess_js(
        str(tmp_path / "missing.js"), str(tmp_path / "out")
    )
    assert result["error"] is not None
    assert result["method"] == "passthrough"


def test_preprocess_returns_map_path_when_webcrack_generates_one(tmp_path):
    src = tmp_path / "min.js"
    src.write_text("x" * 6000)
    out_dir = tmp_path / "out"

    def fake_webcrack(js_path, output_path):
        output_path.write_text("deobf()\n")
        map_path = output_path.with_suffix(".js.map")
        map_path.write_text('{"version":3}')
        return True, map_path

    def fake_prettier(js_path, output_path):
        output_path.write_text("deobf()\n")
        return True

    with patch(
        "modules.js_analyzer.tools.preprocess_js._run_webcrack",
        side_effect=fake_webcrack,
    ), patch(
        "modules.js_analyzer.tools.preprocess_js._run_prettier",
        side_effect=fake_prettier,
    ):
        result = preprocess_js(str(src), str(out_dir))

    assert result["map_path"] is not None
    assert Path(result["map_path"]).exists()
