"""Tests for modules/js_analyzer/module.py — Phase 4 wiring."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from modules.js_analyzer.module import (
    MODULE,
    JsAnalyzerConfig,
    _slash_js_analyzer,
)


def test_module_spec_name():
    assert MODULE.name == "js_analyzer"
    assert MODULE.config_schema is JsAnalyzerConfig


def test_callgraph_creates_schema(tmp_path):
    from modules.js_analyzer.callgraph import CallGraph

    db_path = tmp_path / "cg.db"
    cg = CallGraph(db_path)
    try:
        assert db_path.exists()
        tables = {
            r[0] for r in cg.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {"nodes", "edges", "node_tags"}.issubset(tables)
    finally:
        cg.close()


def test_find_sinks_empty_db(tmp_path):
    from modules.js_analyzer import callgraph_tools as ct
    from modules.js_analyzer.callgraph import CallGraph

    cg = CallGraph(tmp_path / "cg.db")
    try:
        ct.set_callgraph(cg, base_paths=[tmp_path])
        result = ct.find_sinks()
        assert "sinks" in result
        assert result["sinks"] == []
        assert result["truncated"] is False
    finally:
        cg.close()


def test_slash_blocks_outside_sandbox(tmp_path):
    import asyncio
    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    kernel = MagicMock()
    kernel.sandbox.is_allowed.return_value = False
    out = asyncio.run(
        _slash_js_analyzer(str(tmp_path / "anywhere"), kernel, cfg)
    )
    assert "outside sandbox" in out


def test_score_chain_high_severity_short_depth():
    from modules.js_analyzer.reporter import score_chain

    chain = {
        "source": {"taxonomy_id": "location_hash"},
        "sink":   {"taxonomy_id": "innerHTML_assign"},
        "depth":  1,
        "path":   ["a.js::source", "a.js::sink"],
    }
    snippets = {
        "a.js::source": "const x = location.hash;",
        "a.js::sink":   "el.innerHTML = x;",
    }
    score = score_chain(chain, snippets)
    assert score > 50


def _kernel_with_state(tmp_path, sandbox_ok: bool = True):
    from modules.js_analyzer.module import JsAnalyzerState
    kernel = MagicMock()
    state = JsAnalyzerState()
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, default=None: services.get(k, default)
    kernel.sandbox.is_allowed.return_value = sandbox_ok
    return kernel, state


def test_export_findings_no_state_returns_error(tmp_path):
    from modules.js_analyzer.module import _export_findings
    kernel, _ = _kernel_with_state(tmp_path)
    out = _export_findings(kernel, "markdown", str(tmp_path / "x.md"))
    assert "no findings cached" in out


def test_export_findings_outside_sandbox_blocked(tmp_path):
    from modules.js_analyzer.module import _export_findings
    kernel, state = _kernel_with_state(tmp_path, sandbox_ok=False)
    state.last_findings = {"chains": []}
    state.last_report   = "# report"
    out = _export_findings(kernel, "markdown", str(tmp_path / "x.md"))
    assert "outside sandbox" in out


def test_export_findings_markdown_writes_file(tmp_path):
    from modules.js_analyzer.module import _export_findings
    kernel, state = _kernel_with_state(tmp_path)
    state.last_findings = {"chains": []}
    state.last_report   = "# my report\n\nbody"
    target = tmp_path / "out.md"
    msg = _export_findings(kernel, "markdown", str(target))
    assert "markdown written" in msg
    assert target.read_text() == "# my report\n\nbody"


def test_export_findings_sarif_writes_file(tmp_path):
    import json as _json

    from modules.js_analyzer.module import _export_findings
    kernel, state = _kernel_with_state(tmp_path)
    state.last_findings = {"chains": []}
    state.last_report   = "# report"
    target = tmp_path / "out.sarif"
    msg = _export_findings(kernel, "sarif", str(target))
    assert "sarif written" in msg
    doc = _json.loads(target.read_text())
    assert doc["version"] == "2.1.0"
    assert isinstance(doc["runs"], list)


def test_export_findings_unsupported_format_returns_error(tmp_path):
    from modules.js_analyzer.module import _export_findings
    kernel, state = _kernel_with_state(tmp_path)
    state.last_findings = {"chains": []}
    state.last_report   = "# report"
    out = _export_findings(kernel, "html", str(tmp_path / "x"))
    assert "unsupported format" in out


def test_detect_frameworks_called_with_pkg_json(tmp_path):
    """If package.json exists with react dep, framework detection runs."""
    from modules.js_analyzer.module import JsAnalyzerConfig, _index_target

    (tmp_path / "package.json").write_text(
        '{"dependencies": {"react": "^18.0.0"}}', encoding="utf-8"
    )
    (tmp_path / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))

    from unittest.mock import MagicMock, patch

    from modules.js_analyzer.callgraph import CallGraph
    cg = CallGraph(tmp_path / "cg.db")
    kernel = MagicMock()
    services = {"js_analyzer_callgraph": cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    captured = {}

    original_set = __import__(
        "modules.js_analyzer.ast_bridge", fromlist=["ASTExtractor"]
    ).ASTExtractor.set_frameworks

    def _capture_set_frameworks(self, tags):
        captured["frameworks"] = frozenset(tags)
        original_set(self, tags)

    with patch(
        "modules.js_analyzer.ast_bridge.ASTExtractor.set_frameworks",
        _capture_set_frameworks,
    ):
        _index_target(kernel, tmp_path, cfg)

    cg.close()
    assert "react" in captured.get("frameworks", frozenset())


def test_index_return_includes_framework_string(tmp_path):
    """Return string mentions detected frameworks."""
    from unittest.mock import MagicMock

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import JsAnalyzerConfig, _index_target

    (tmp_path / "package.json").write_text(
        '{"dependencies": {"vue": "^3.0.0"}}', encoding="utf-8"
    )
    (tmp_path / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")
    kernel = MagicMock()
    services = {"js_analyzer_callgraph": cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    result = _index_target(kernel, tmp_path, cfg)
    cg.close()

    assert "frameworks:" in result
    assert "vue" in result


def test_sarif_tool_identity():
    from modules.js_analyzer.sarif_writer import build_sarif

    findings = {"chains": []}
    report = "# report"
    doc = build_sarif(findings, report)
    driver = doc["runs"][0]["tool"]["driver"]
    assert driver["name"] == "tlx-js-analyzer"
    assert driver["version"] == "0.1.0"
    assert driver["informationUri"] == "https://github.com/cuhawk/tlx"


def test_no_print_in_ported_module_code():
    import re
    base = Path(__file__).resolve().parents[1]
    for fname in ("pp_chains.py", "sink_expander.py",
                  "ast_bridge.py", "reporter.py"):
        text = (base / fname).read_text(encoding="utf-8")
        stripped = re.sub(r'""".*?"""', "", text, flags=re.DOTALL)
        stripped = re.sub(r"'''.*?'''", "", stripped, flags=re.DOTALL)
        stripped = re.sub(r'"[^"\n]*"', "", stripped)
        stripped = re.sub(r"'[^'\n]*'", "", stripped)
        assert "print(" not in stripped, f"{fname} still has print()"


def test_index_runs_interprocedural_taint(tmp_path):
    """`_index_target` calls solve_interprocedural_taint; the flows table
    exists in the SQLite schema after a successful index."""
    from unittest.mock import patch

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import JsAnalyzerConfig, _index_target

    (tmp_path / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")

    class _StubExtractor:
        ready = True
        reason = ""
        def __init__(self, *a, **kw): pass  # noqa: E701
        def set_frameworks(self, fw): pass  # noqa: E701
        def extract(self, files): return {}  # noqa: E701

    kernel = MagicMock()
    services = {"js_analyzer_callgraph": cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    with patch("modules.js_analyzer.ast_bridge.ASTExtractor", _StubExtractor):
        out = _index_target(kernel, tmp_path, cfg)

    tables = {
        r[0] for r in cg.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    cg.close()

    assert "interprocedural_taint_flows" in tables
    assert "itp:" in out


def test_run_interprocedural_taint_demotes_solver_errors():
    """Solver exception → (0, 0) and a warning event; never raises."""
    import structlog

    from modules.js_analyzer.module import _run_interprocedural_taint

    bad_cg = MagicMock()
    bad_cg.conn.execute.side_effect = RuntimeError("boom")

    with structlog.testing.capture_logs() as logs:
        result = _run_interprocedural_taint(bad_cg)

    assert result == (0, 0)
    events = {r.get("event") for r in logs}
    assert "js_analyzer.itp_arg_edges_failed" in events


def test_slash_emits_progress_events_on_small_target(tmp_path):
    """js_analyzer slash should emit ≥3 progress events on a tiny fixture."""
    import asyncio
    import json as _json

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import (
        _index_target_payload,
        _slash_js_analyzer,
    )

    target = tmp_path / "fx"
    target.mkdir()
    (target / "a.js").write_text("function hi(){return 1;}\n", encoding="utf-8")

    cg = CallGraph(tmp_path / "cg.db")
    try:
        services = {"js_analyzer_callgraph": cg}
        kernel = MagicMock()
        kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
        kernel.sandbox.list_roots.return_value = [target]
        kernel.sandbox.is_allowed.return_value = True

        events: list[tuple[str, str]] = []

        def _record(stage, detail=""):
            events.append((stage, detail))

        kernel.report_progress = _record

        cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))

        async def _fake_dispatch(name, args):
            assert name == "js_index_target"
            payload = _index_target_payload(
                kernel, Path(args["target_folder"]), cfg,
            )
            return _json.dumps(payload)

        kernel.tools.dispatch = _fake_dispatch

        asyncio.run(_slash_js_analyzer(str(target), kernel, cfg))

        stages = [e[0] for e in events]
        assert len(events) >= 3
        assert any("scan" in s for s in stages)
        assert any("done" in s for s in stages)
    finally:
        cg.close()


def test_slash_entry_refreshes_callgraph_base_paths(tmp_path):
    """Slash handler refreshes ct._BASE_PATHS from kernel.sandbox.list_roots()."""
    import asyncio
    import json as _json

    from modules.js_analyzer import callgraph_tools as ct
    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import (
        _index_target_payload,
        _slash_js_analyzer,
    )

    cg = CallGraph(tmp_path / "cg.db")
    try:
        services = {"js_analyzer_callgraph": cg}
        kernel = MagicMock()
        kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

        a_dir = tmp_path / "a"
        a_dir.mkdir()
        kernel.sandbox.list_roots.return_value = [a_dir]
        kernel.sandbox.is_allowed.return_value = True
        cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))

        async def _fake_dispatch(name, args):
            assert name == "js_index_target"
            return _json.dumps(_index_target_payload(
                kernel, Path(args["target_folder"]), cfg,
            ))

        kernel.tools.dispatch = _fake_dispatch

        asyncio.run(_slash_js_analyzer(str(a_dir), kernel, cfg))
        assert [Path(p) for p in ct._BASE_PATHS] == [a_dir]

        b_dir = tmp_path / "b"
        b_dir.mkdir()
        kernel.sandbox.list_roots.return_value = [b_dir]
        asyncio.run(_slash_js_analyzer(str(b_dir), kernel, cfg))
        # _index_target then sets to [target] = [b_dir] — so still b_dir.
        assert [Path(p) for p in ct._BASE_PATHS] == [b_dir]
    finally:
        cg.close()


def test_save_hypotheses_kv_logs_warning_on_failure():
    import structlog

    from modules.js_analyzer.module import _save_hypotheses_kv

    kernel = MagicMock()
    kernel.session_store.set.side_effect = RuntimeError("disk full")

    with structlog.testing.capture_logs() as logs:
        _save_hypotheses_kv(kernel, {"sig1": {"status": "open"}})

    events = [r for r in logs if r.get("event") == "js_analyzer.hypothesis_kv_save_failed"]
    assert events
    assert events[0]["log_level"] == "warning"


def test_load_hypotheses_kv_logs_warning_on_failure():
    import structlog

    from modules.js_analyzer.module import _load_hypotheses_kv

    kernel = MagicMock()
    kernel.session_store.get.side_effect = RuntimeError("corrupt")

    with structlog.testing.capture_logs() as logs:
        result = _load_hypotheses_kv(kernel)

    assert result == {}
    events = [r for r in logs if r.get("event") == "js_analyzer.hypothesis_kv_load_failed"]
    assert events
    assert events[0]["log_level"] == "warning"


def test_walk_js_files_excludes_default_dirs(tmp_path):
    from modules.js_analyzer.module import JsAnalyzerConfig, _walk_js_files

    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "lib.js").write_text("//x", encoding="utf-8")
    (tmp_path / ".angular").mkdir()
    (tmp_path / ".angular" / "cache.js").write_text("//x", encoding="utf-8")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "out.js").write_text("//x", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.js").write_text("//ok", encoding="utf-8")

    cfg = JsAnalyzerConfig()
    files = _walk_js_files(tmp_path, cfg.exclude_dirs)
    rels = {f["rel"] for f in files}
    assert rels == {"src/app.js"}


def test_walk_js_files_custom_excludes_flips(tmp_path):
    from modules.js_analyzer.module import _walk_js_files

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.js").write_text("//x", encoding="utf-8")
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib" / "u.js").write_text("//ok", encoding="utf-8")

    files = _walk_js_files(tmp_path, ["src"])
    rels = {f["rel"] for f in files}
    assert rels == {"lib/u.js"}


def test_template_files_picked_up(tmp_path):
    """`.vue` and `.html` files outside excluded dirs end up in template_files."""
    from unittest.mock import patch

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import JsAnalyzerConfig, _index_target

    (tmp_path / "comp.vue").write_text("<template></template>", encoding="utf-8")
    (tmp_path / "page.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / ".angular").mkdir()
    (tmp_path / ".angular" / "skip.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")

    captured: dict = {}
    original_index_batch = cg.index_batch

    def _capture(results, root_dir=None, template_files=None):
        captured["template_files"] = dict(template_files or {})
        return original_index_batch(results, root_dir=root_dir, template_files=template_files)

    cg.index_batch = _capture  # type: ignore[assignment]

    kernel = MagicMock()
    services = {"js_analyzer_callgraph": cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    class _StubExtractor:
        ready = True
        reason = ""
        def __init__(self, *a, **kw): pass
        def set_frameworks(self, fw): pass
        def extract(self, files): return {}

    with patch(
        "modules.js_analyzer.ast_bridge.ASTExtractor", _StubExtractor
    ):
        _index_target(kernel, tmp_path, cfg)
    cg.close()

    rels = set(captured.get("template_files", {}).keys())
    assert "comp.vue" in rels
    assert "page.html" in rels
    assert ".angular/skip.html" not in rels


def test_slash_mock_extract_flag_runs_extract_when_module_registered(tmp_path):
    """--mock-extract: kernel.tools.get('mock_extract').handler is invoked
    with the same target_dir, and its output is appended."""
    from unittest.mock import patch

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import _slash_js_analyzer

    target_dir = tmp_path / "proj"
    target_dir.mkdir()
    (target_dir / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")

    captured: dict = {}

    class _FakeTool:
        @staticmethod
        def handler(**kw):
            captured.update(kw)
            return "scaffold: /tmp/x.html"

    services = {"js_analyzer_callgraph": cg}
    kernel = MagicMock()
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.sandbox.list_roots.return_value = [target_dir]
    kernel.sandbox.is_allowed.return_value = True
    kernel.tools.get.side_effect = lambda name: _FakeTool() if name == "mock_extract" else None

    import asyncio
    import json as _json

    from modules.js_analyzer.module import _index_target_payload

    async def _fake_dispatch(name, args):
        assert name == "js_index_target"
        return _json.dumps(_index_target_payload(
            kernel, Path(args["target_folder"]), cfg,
        ))

    kernel.tools.dispatch = _fake_dispatch

    class _StubExtractor:
        ready = True
        reason = ""
        def __init__(self, *a, **kw): pass
        def set_frameworks(self, fw): pass
        def extract(self, files): return {}

    with patch("modules.js_analyzer.ast_bridge.ASTExtractor", _StubExtractor):
        out = asyncio.run(
            _slash_js_analyzer(f"{target_dir} --mock-extract", kernel, cfg)
        )
    cg.close()

    assert captured.get("target_dir") == str(target_dir)
    assert "--- mock_extract ---" in out
    assert "scaffold: /tmp/x.html" in out


def test_slash_mock_extract_flag_warns_when_module_missing(tmp_path):
    from unittest.mock import patch

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import _slash_js_analyzer

    target_dir = tmp_path / "proj"
    target_dir.mkdir()
    (target_dir / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")

    services = {"js_analyzer_callgraph": cg}
    kernel = MagicMock()
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.sandbox.list_roots.return_value = [target_dir]
    kernel.sandbox.is_allowed.return_value = True
    kernel.tools.get.side_effect = lambda name: None

    import asyncio
    import json as _json

    from modules.js_analyzer.module import _index_target_payload

    async def _fake_dispatch(name, args):
        return _json.dumps(_index_target_payload(
            kernel, Path(args["target_folder"]), cfg,
        ))

    kernel.tools.dispatch = _fake_dispatch

    class _StubExtractor:
        ready = True
        reason = ""
        def __init__(self, *a, **kw): pass
        def set_frameworks(self, fw): pass
        def extract(self, files): return {}

    with patch("modules.js_analyzer.ast_bridge.ASTExtractor", _StubExtractor):
        out = asyncio.run(
            _slash_js_analyzer(f"{target_dir} --mock-extract", kernel, cfg)
        )
    cg.close()

    assert "mock_backend module is not registered" in out


def test_slash_without_mock_extract_flag_runs_only_indexing(tmp_path):
    from unittest.mock import patch

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import _slash_js_analyzer

    target_dir = tmp_path / "proj"
    target_dir.mkdir()
    (target_dir / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")

    services = {"js_analyzer_callgraph": cg}
    kernel = MagicMock()
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.sandbox.list_roots.return_value = [target_dir]
    kernel.sandbox.is_allowed.return_value = True

    extract_called = []

    class _FakeTool:
        @staticmethod
        def handler(**kw):
            extract_called.append(kw)
            return "x"

    kernel.tools.get.side_effect = lambda name: _FakeTool() if name == "mock_extract" else None

    import asyncio
    import json as _json

    from modules.js_analyzer.module import _index_target_payload

    async def _fake_dispatch(name, args):
        return _json.dumps(_index_target_payload(
            kernel, Path(args["target_folder"]), cfg,
        ))

    kernel.tools.dispatch = _fake_dispatch

    class _StubExtractor:
        ready = True
        reason = ""
        def __init__(self, *a, **kw): pass
        def set_frameworks(self, fw): pass
        def extract(self, files): return {}

    with patch("modules.js_analyzer.ast_bridge.ASTExtractor", _StubExtractor):
        out = asyncio.run(_slash_js_analyzer(str(target_dir), kernel, cfg))
    cg.close()

    assert extract_called == []
    assert "--- mock_extract ---" not in out


def test_index_no_pkg_json_still_works(tmp_path):
    """No package.json → frameworks defaults to node, indexing succeeds."""
    from unittest.mock import MagicMock

    from modules.js_analyzer.callgraph import CallGraph
    from modules.js_analyzer.module import JsAnalyzerConfig, _index_target

    (tmp_path / "app.js").write_text("const x = 1;", encoding="utf-8")

    cfg = JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))
    cg = CallGraph(tmp_path / "cg.db")
    kernel = MagicMock()
    services = {"js_analyzer_callgraph": cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    result = _index_target(kernel, tmp_path, cfg)
    cg.close()

    assert "js_analyzer indexed" in result or "unavailable" in result
