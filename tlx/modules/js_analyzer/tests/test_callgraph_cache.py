"""Phase 7C Task 2 — file_hashes incremental cache for callgraph index."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import modules.js_analyzer.module as ja_module
from modules.js_analyzer.callgraph import CallGraph


def test_file_hashes_table_present(tmp_path):
    cg = CallGraph(tmp_path / "cg.db")
    try:
        tables = {
            r[0] for r in cg.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "file_hashes" in tables
    finally:
        cg.close()


def test_record_then_unchanged(tmp_path):
    cg = CallGraph(tmp_path / "cg.db")
    try:
        f = tmp_path / "a.js"
        f.write_text("const x = 1;")
        rel = "a.js"
        assert cg.is_file_unchanged(rel, f) is False
        cg.record_file_hash(rel, f)
        assert cg.is_file_unchanged(rel, f) is True
    finally:
        cg.close()


def test_changed_content_invalidates_cache(tmp_path):
    cg = CallGraph(tmp_path / "cg.db")
    try:
        f = tmp_path / "a.js"
        f.write_text("const x = 1;")
        cg.record_file_hash("a.js", f)
        assert cg.is_file_unchanged("a.js", f) is True
        f.write_text("const x = 2;")
        assert cg.is_file_unchanged("a.js", f) is False
    finally:
        cg.close()


def test_force_bypasses_cache(tmp_path):
    cg = CallGraph(tmp_path / "cg.db")
    try:
        f = tmp_path / "a.js"
        f.write_text("const x = 1;")
        cg.record_file_hash("a.js", f)
        assert cg.is_file_unchanged("a.js", f, force=True) is False
    finally:
        cg.close()


def test_index_target_skips_extractor_on_unchanged(tmp_path):
    """Second run on unchanged JS must NOT call ASTExtractor.extract."""
    target = tmp_path / "src"
    target.mkdir()
    (target / "a.js").write_text("const x = 1;")

    cg = CallGraph(tmp_path / "cg.db")
    kernel = MagicMock()
    kernel.services.get.return_value = cg

    cfg = ja_module.JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))

    fake_extractor = MagicMock()
    fake_extractor.ready = True
    fake_extractor.reason = None
    fake_extractor.extract.return_value = {}

    try:
        with patch(
            "modules.js_analyzer.ast_bridge.ASTExtractor",
            return_value=fake_extractor,
        ), patch(
            "modules.js_analyzer.framework_detect.detect_frameworks",
            return_value={"node"},
        ), patch(
            "modules.js_analyzer.module._run_interprocedural_taint",
            return_value=(0, 0),
        ):
            ja_module._index_target(kernel, target, cfg)
            assert fake_extractor.extract.call_count == 1

            ja_module._index_target(kernel, target, cfg)
            # Second run: cached → no extract call
            assert fake_extractor.extract.call_count == 1
    finally:
        cg.close()


def test_index_target_force_bypasses_cache(tmp_path):
    target = tmp_path / "src"
    target.mkdir()
    (target / "a.js").write_text("const x = 1;")

    cg = CallGraph(tmp_path / "cg.db")
    kernel = MagicMock()
    kernel.services.get.return_value = cg

    cfg = ja_module.JsAnalyzerConfig(db_path=str(tmp_path / "cg.db"))

    fake_extractor = MagicMock()
    fake_extractor.ready = True
    fake_extractor.reason = None
    fake_extractor.extract.return_value = {}

    try:
        with patch(
            "modules.js_analyzer.ast_bridge.ASTExtractor",
            return_value=fake_extractor,
        ), patch(
            "modules.js_analyzer.framework_detect.detect_frameworks",
            return_value={"node"},
        ), patch(
            "modules.js_analyzer.module._run_interprocedural_taint",
            return_value=(0, 0),
        ):
            ja_module._index_target(kernel, target, cfg)
            ja_module._index_target(kernel, target, cfg, force=True)
            assert fake_extractor.extract.call_count == 2
    finally:
        cg.close()


def test_record_after_index_inserts_row(tmp_path):
    cg = CallGraph(tmp_path / "cg.db")
    try:
        f = tmp_path / "a.js"
        f.write_text("const x = 1;")
        cg.record_file_hash("a.js", f)
        row = cg.conn.execute(
            "SELECT file, sha256 FROM file_hashes WHERE file=?", ("a.js",),
        ).fetchone()
        assert row is not None
        assert row[0] == "a.js"
        assert len(row[1]) == 64
    finally:
        cg.close()
