"""Tests for mock_backend source_rewriter (Phase 7B Task 2)."""
from __future__ import annotations

from modules.mock_backend.core.source_rewriter import (
    inject_probe_in_response,
    rewrite_js,
)


def test_rewrite_replaces_bare_identifier():
    src = "var x = userInput; doStuff(userInput);"
    out = rewrite_js(src, {"userInput": '"PROBE-1"'})
    assert "userInput" not in out
    assert '"PROBE-1"' in out
    assert out.count('"PROBE-1"') == 2


def test_rewrite_does_not_touch_substrings():
    src = "var userInputs = userInput; var myUserInput = 1;"
    out = rewrite_js(src, {"userInput": '"P"'})
    # bare userInput → "P"; userInputs and myUserInput must remain intact
    assert "userInputs" in out
    assert "myUserInput" in out
    assert '= "P"' in out


def test_rewrite_no_change_when_identifier_absent():
    src = "var a = 1;"
    out = rewrite_js(src, {"missing": '"P"'})
    assert out == src


def test_rewrite_empty_inputs_safe():
    assert rewrite_js("", {"x": '"y"'}) == ""
    assert rewrite_js("var a = 1;", {}) == "var a = 1;"


def test_rewrite_multiple_identifiers():
    src = "fn(a); fn(b);"
    out = rewrite_js(src, {"a": '"AAA"', "b": '"BBB"'})
    assert '"AAA"' in out
    assert '"BBB"' in out


def test_inject_probe_in_response_noop_for_html():
    body = b"<div>userInput</div>"
    out = inject_probe_in_response(body, "text/html", {"userInput": '"P"'})
    assert out == body


def test_inject_probe_in_response_rewrites_javascript():
    body = b"console.log(userInput);"
    out = inject_probe_in_response(
        body, "application/javascript", {"userInput": '"PROBE"'}
    )
    assert b'"PROBE"' in out
    assert b"userInput" not in out


def test_inject_probe_in_response_handles_text_javascript():
    body = b"var x = userInput;"
    out = inject_probe_in_response(
        body, "text/javascript; charset=utf-8", {"userInput": '"P"'}
    )
    assert b'"P"' in out


def test_inject_probe_in_response_returns_bytes_unchanged_on_decode_error():
    body = b"\xff\xfe\x00bad"
    out = inject_probe_in_response(
        body, "application/javascript", {"x": '"y"'}
    )
    assert out == body


# --- Phase 7C Task 4: AST-mode rewrite ---


def test_rewrite_js_ast_subprocess_failure_falls_back_to_regex():
    from unittest.mock import patch

    from modules.mock_backend.core import source_rewriter

    src = "var x = userInput;"
    fake_proc = subprocess_result(returncode=1, stderr="boom")
    with patch.object(
        source_rewriter, "subprocess",
    ) as mock_sub, patch.object(
        source_rewriter.shutil, "which", return_value="/usr/bin/node"
    ), patch.object(
        source_rewriter, "rewrite_js", wraps=source_rewriter.rewrite_js,
    ) as regex_spy:
        mock_sub.run.return_value = fake_proc
        mock_sub.TimeoutExpired = Exception
        out = source_rewriter.rewrite_js_ast(src, {"userInput": '"P"'})
    assert regex_spy.called
    assert '"P"' in out


def test_rewrite_js_ast_invokes_node_subprocess_on_success():
    from unittest.mock import patch

    from modules.mock_backend.core import source_rewriter

    src = "var x = userInput;"
    expected = 'var x = "P";'
    fake_proc = subprocess_result(returncode=0, stdout=expected)
    with patch.object(
        source_rewriter, "subprocess",
    ) as mock_sub, patch.object(
        source_rewriter.shutil, "which", return_value="/usr/bin/node"
    ):
        mock_sub.run.return_value = fake_proc
        mock_sub.TimeoutExpired = Exception
        out = source_rewriter.rewrite_js_ast(src, {"userInput": '"P"'})
    assert out == expected
    assert mock_sub.run.called


def test_rewrite_js_ast_falls_back_when_node_missing():
    from unittest.mock import patch

    from modules.mock_backend.core import source_rewriter

    src = "var x = userInput;"
    with patch.object(
        source_rewriter.shutil, "which", return_value=None,
    ):
        out = source_rewriter.rewrite_js_ast(src, {"userInput": '"P"'})
    # Falls back to regex
    assert '"P"' in out


def test_inject_probe_mode_ast_calls_rewrite_js_ast():
    from unittest.mock import patch

    from modules.mock_backend.core import source_rewriter

    body = b"console.log(userInput);"
    with patch.object(
        source_rewriter, "rewrite_js_ast",
        return_value='console.log("P");',
    ) as ast_spy:
        out = source_rewriter.inject_probe_in_response(
            body, "application/javascript",
            {"userInput": '"P"'}, mode="ast",
        )
    assert ast_spy.called
    assert b'"P"' in out


def test_inject_probe_mode_regex_calls_rewrite_js_only():
    from unittest.mock import patch

    from modules.mock_backend.core import source_rewriter

    body = b"console.log(userInput);"
    with patch.object(
        source_rewriter, "rewrite_js_ast",
    ) as ast_spy, patch.object(
        source_rewriter, "rewrite_js",
        return_value='console.log("P");',
    ) as regex_spy:
        source_rewriter.inject_probe_in_response(
            body, "application/javascript",
            {"userInput": '"P"'}, mode="regex",
        )
    assert ast_spy.called is False
    assert regex_spy.called is True


def subprocess_result(returncode: int, stdout: str = "", stderr: str = ""):
    class _R:
        pass
    r = _R()
    r.returncode = returncode
    r.stdout = stdout
    r.stderr = stderr
    return r


def test_ast_script_exists_on_disk():
    from modules.mock_backend.core import source_rewriter

    assert source_rewriter._AST_SCRIPT.exists()
    assert source_rewriter._AST_SCRIPT.suffix == ".js"
