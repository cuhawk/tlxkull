"""Phase 4F audit-loop kernel-engine port tests."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import modules.js_analyzer.module as _ja_module  # noqa: F401  install shim
from kernel.schema import (
    Cost,
    EngineResponse,
    ToolCall,
    ToolUseBlock,
    Usage,
)
from modules.js_analyzer import claude_agent
from modules.js_analyzer.claude_agent import (
    CLAUDE_MODEL,
    _resolve_audit_engine,
)
from modules.js_analyzer.module import JsAnalyzerState


def _resp_end() -> EngineResponse:
    return EngineResponse(
        content=[],
        tool_calls=[],
        usage=Usage(input_tokens=0, output_tokens=0),
        cost=Cost(input_usd=0.0, output_usd=0.0),
        stop_reason="end_turn",
    )


def _resp_tool(name: str, args: dict, in_tok: int = 100, out_tok: int = 50,
               cost_in: float = 0.001, cost_out: float = 0.002) -> EngineResponse:
    return EngineResponse(
        content=[ToolUseBlock(id="t1", name=name, input=args)],
        tool_calls=[ToolCall(id="t1", name=name, args=args)],
        usage=Usage(input_tokens=in_tok, output_tokens=out_tok),
        cost=Cost(input_usd=cost_in, output_usd=cost_out),
        stop_reason="tool_use",
    )


def _kernel_with_state(findings: dict):
    state = JsAnalyzerState()
    state.last_findings = findings
    kernel = MagicMock()
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_store.get.return_value = None
    kernel.session_store.set.return_value = None
    return kernel, state


def _install_fake_engine(monkeypatch, *responses):
    queue = list(responses) or [_resp_end()]
    last = queue[-1]

    captured = {"calls": 0, "tools": None, "system": None}

    async def _respond(messages, tools, system, max_tokens=None):
        captured["calls"] += 1
        captured["tools"] = tools
        captured["system"] = system
        return queue.pop(0) if queue else last

    fake_engine = MagicMock()
    fake_engine.respond = _respond
    fake_engine.model = CLAUDE_MODEL
    monkeypatch.setattr(
        claude_agent, "_resolve_audit_engine", lambda kernel: fake_engine,
    )
    return fake_engine, captured


_FINDINGS = {
    "target_folder": "/tmp/app",
    "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
    "chains": [],
    "snippets": {},
}


def test_engine_resolution_reuses_kernel_engine_when_claude_sonnet():
    from kernel.engines.claude import ClaudeEngine
    eng = ClaudeEngine(model=CLAUDE_MODEL)
    kernel = SimpleNamespace(engine=eng)
    out = _resolve_audit_engine(kernel)
    assert out is eng


def test_engine_resolution_makes_fresh_when_kernel_engine_is_gemini():
    fake_engine = SimpleNamespace(model="gemini-2.5-pro", name="gemini")
    kernel = SimpleNamespace(engine=fake_engine)
    out = _resolve_audit_engine(kernel)
    from kernel.engines.claude import ClaudeEngine
    assert isinstance(out, ClaudeEngine)
    assert out is not fake_engine
    assert out.model == CLAUDE_MODEL


def test_engine_resolution_makes_fresh_when_kernel_has_no_engine():
    kernel = SimpleNamespace()
    out = _resolve_audit_engine(kernel)
    from kernel.engines.claude import ClaudeEngine
    assert isinstance(out, ClaudeEngine)
    assert out.model == CLAUDE_MODEL


def test_engine_resolution_makes_fresh_when_claude_but_wrong_model():
    from kernel.engines.claude import ClaudeEngine
    eng = ClaudeEngine(model="claude-haiku-4-5")
    kernel = SimpleNamespace(engine=eng)
    out = _resolve_audit_engine(kernel)
    assert out is not eng
    assert isinstance(out, ClaudeEngine)
    assert out.model == CLAUDE_MODEL


@pytest.mark.asyncio
async def test_audit_loop_uses_resolved_engine_not_direct_anthropic(monkeypatch):
    """Loop must drive itself via the resolved engine, not anthropic.Anthropic.

    js_consult_opus is the *only* allowed direct-anthropic call site
    (CLAUDE.md case 2). The executor path is forbidden from touching it.
    """
    kernel, _ = _kernel_with_state(_FINDINGS)
    _, captured = _install_fake_engine(monkeypatch, _resp_end())

    sentinel = MagicMock(side_effect=AssertionError(
        "executor path must not instantiate anthropic.Anthropic"
    ))
    monkeypatch.setattr(claude_agent.anthropic, "Anthropic", sentinel)

    await claude_agent.analyse_chains_async(_FINDINGS, kernel)
    assert captured["calls"] == 1
    sentinel.assert_not_called()


@pytest.mark.asyncio
async def test_audit_loop_dispatches_tool_calls_via_handlers(monkeypatch):
    """Tool calls in EngineResponse must be dispatched to _make_tools handlers."""
    findings = {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "chains": [
            {
                "id": 1,
                "source": {"qname": "a.js::src", "file": "a.js", "line": 1,
                           "taxonomy_id": "x"},
                "sink":   {"qname": "a.js::sink", "file": "a.js", "line": 5,
                           "taxonomy_id": "y"},
                "depth": 1,
                "path":  ["a.js::src", "a.js::sink"],
            }
        ],
        "snippets": {"a.js::src": "src", "a.js::sink": "sink"},
    }
    kernel, state = _kernel_with_state(findings)
    state.total_chains = 1

    _install_fake_engine(
        monkeypatch,
        _resp_tool("js_examine_chain", {"chain_id": 1}),
        _resp_tool(
            "js_submit_finding",
            {"chain_id": 1, "verdict": "true_positive",
             "severity": "high", "vuln_class": "DOM XSS",
             "proof": "trace shows location.hash flowing to innerHTML"},
        ),
        _resp_end(),
    )

    await claude_agent.analyse_chains_async(findings, kernel)
    assert 1 in state.verdicts
    assert state.verdicts[1]["verdict"] == "true_positive"


@pytest.mark.asyncio
async def test_cost_telemetry_matches_engine_cost_total(monkeypatch):
    kernel, state = _kernel_with_state(_FINDINGS)
    _install_fake_engine(
        monkeypatch,
        EngineResponse(
            content=[],
            tool_calls=[],
            usage=Usage(input_tokens=200, output_tokens=100),
            cost=Cost(input_usd=0.0006, output_usd=0.0015),
            stop_reason="end_turn",
        ),
    )
    await claude_agent.analyse_chains_async(_FINDINGS, kernel)
    assert state.last_audit_cost_usd == pytest.approx(0.0021)
    assert state.last_audit_tokens == 300


@pytest.mark.asyncio
async def test_js_consult_opus_handler_still_uses_direct_anthropic(monkeypatch):
    """CLAUDE.md case 2: js_consult_opus is the canonical single-shot
    direct-anthropic site, must keep working that way after the port."""
    findings = {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "framework_tags": ["angular"],
        "chains": [
            {
                "id": 1,
                "source": {"qname": "a.js::src", "file": "a.js", "line": 1,
                           "taxonomy_id": "x"},
                "sink":   {"qname": "a.js::sink", "file": "a.js", "line": 5,
                           "taxonomy_id": "y"},
                "depth": 1,
                "path":  ["a.js::src", "a.js::sink"],
            }
        ],
        "snippets": {"a.js::src": "x", "a.js::sink": "y"},
    }
    kernel, state = _kernel_with_state(findings)
    state.total_chains = 1

    _install_fake_engine(
        monkeypatch,
        _resp_tool(
            "js_consult_opus",
            {"chain_id": "1", "question": "q", "confidence_so_far": "low"},
        ),
        _resp_end(),
    )

    captured: dict = {}
    fake_resp = MagicMock()
    block = MagicMock()
    block.text = "verdict: not_exploitable"
    fake_resp.content = [block]
    fake_resp.usage.input_tokens = 200
    fake_resp.usage.output_tokens = 50

    def _create(**kwargs):
        captured.update(kwargs)
        return fake_resp

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = _create
    monkeypatch.setattr(
        claude_agent.anthropic, "Anthropic", lambda **kw: fake_client,
    )

    await claude_agent.analyse_chains_async(findings, kernel)

    fake_client.messages.create.assert_called_once()
    assert "tools" not in captured  # single-shot, no tools
    assert captured["model"] == claude_agent.CLAUDE_OPUS_MODEL


@pytest.mark.asyncio
async def test_compaction_triggers_at_60pct_threshold(monkeypatch):
    """When total_tokens crosses TOKEN_LIMIT * 0.6, compactor.compact runs in-loop."""
    kernel, _ = _kernel_with_state(_FINDINGS)

    threshold = int(claude_agent.TOKEN_LIMIT * 0.6)
    big_resp = EngineResponse(
        content=[],
        tool_calls=[],
        usage=Usage(input_tokens=threshold + 100, output_tokens=0),
        cost=Cost(input_usd=0.0, output_usd=0.0),
        stop_reason="end_turn",
    )
    _install_fake_engine(monkeypatch, big_resp)

    compact_calls = {"n": 0}

    async def _compact(messages, keep_recent: int = 4):
        compact_calls["n"] += 1
        from kernel.compaction import CompactionResult
        return messages, CompactionResult(summary="x", turns_replaced=0)

    fake_compactor = MagicMock()
    fake_compactor.compact = _compact
    kernel.compactor = fake_compactor

    await claude_agent.analyse_chains_async(_FINDINGS, kernel)
    assert compact_calls["n"] == 1


@pytest.mark.asyncio
async def test_compaction_failure_does_not_break_loop(monkeypatch):
    """compact() raising must not break the audit loop — log and continue."""
    kernel, _ = _kernel_with_state(_FINDINGS)

    threshold = int(claude_agent.TOKEN_LIMIT * 0.6)
    big_resp = EngineResponse(
        content=[],
        tool_calls=[],
        usage=Usage(input_tokens=threshold + 100, output_tokens=0),
        cost=Cost(input_usd=0.0, output_usd=0.0),
        stop_reason="end_turn",
    )
    _install_fake_engine(monkeypatch, big_resp)

    async def _broken(messages, keep_recent: int = 4):
        raise RuntimeError("compactor down")

    kernel.compactor = MagicMock()
    kernel.compactor.compact = _broken

    out = await claude_agent.analyse_chains_async(_FINDINGS, kernel)
    assert out is not None  # loop returned cleanly despite compactor failure


@pytest.mark.asyncio
async def test_compaction_skipped_when_no_compactor_attribute(monkeypatch):
    kernel, _ = _kernel_with_state(_FINDINGS)
    # explicitly clear: MagicMock attrs return mocks, so use a real namespace
    kernel.compactor = None

    threshold = int(claude_agent.TOKEN_LIMIT * 0.6)
    _install_fake_engine(
        monkeypatch,
        EngineResponse(
            content=[], tool_calls=[],
            usage=Usage(input_tokens=threshold + 100, output_tokens=0),
            cost=Cost(input_usd=0.0, output_usd=0.0),
            stop_reason="end_turn",
        ),
    )
    await claude_agent.analyse_chains_async(_FINDINGS, kernel)


@pytest.mark.asyncio
async def test_compaction_does_not_trigger_below_threshold(monkeypatch):
    kernel, _ = _kernel_with_state(_FINDINGS)
    _install_fake_engine(
        monkeypatch,
        EngineResponse(
            content=[], tool_calls=[],
            usage=Usage(input_tokens=10, output_tokens=10),
            cost=Cost(input_usd=0.0, output_usd=0.0),
            stop_reason="end_turn",
        ),
    )

    compact_calls = {"n": 0}

    async def _compact(messages, keep_recent: int = 4):
        compact_calls["n"] += 1
        from kernel.compaction import CompactionResult
        return messages, CompactionResult(summary="", turns_replaced=0)

    kernel.compactor = MagicMock()
    kernel.compactor.compact = _compact

    await claude_agent.analyse_chains_async(_FINDINGS, kernel)
    assert compact_calls["n"] == 0


@pytest.mark.asyncio
async def test_run_finish_called_in_finally_on_exception(monkeypatch, tmp_path):
    """If the engine raises, AuditRun.finish must still mark the run failed."""
    import sqlite3

    from modules.js_analyzer.callgraph import SCHEMA

    db = tmp_path / "ja.db"
    conn = sqlite3.connect(str(db))
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

    fake_cg = SimpleNamespace(db_path=str(db))
    kernel, _ = _kernel_with_state(_FINDINGS)
    services = {"js_analyzer_state": kernel.services.get("js_analyzer_state"),
                "js_analyzer_callgraph": fake_cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_id = "shell-X"

    async def _boom(*_a, **_kw):
        raise RuntimeError("engine exploded")

    fake_engine = MagicMock()
    fake_engine.respond = _boom
    fake_engine.model = CLAUDE_MODEL
    monkeypatch.setattr(
        claude_agent, "_resolve_audit_engine", lambda kernel: fake_engine,
    )

    with pytest.raises(RuntimeError, match="engine exploded"):
        await claude_agent.analyse_chains_async(_FINDINGS, kernel)

    conn = sqlite3.connect(str(db))
    row = conn.execute(
        "SELECT status, failure_reason, finished_at FROM js_audit_runs"
    ).fetchone()
    conn.close()
    assert row[0] == "failed"
    assert "engine exploded" in row[1]
    assert row[2] is not None


@pytest.mark.asyncio
async def test_audit_run_persists_assistant_and_tool_result_turns(monkeypatch, tmp_path):
    import sqlite3

    from modules.js_analyzer.callgraph import SCHEMA

    findings = {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "chains": [
            {
                "id": 1,
                "source": {"qname": "a.js::src", "file": "a.js", "line": 1,
                           "taxonomy_id": "x"},
                "sink":   {"qname": "a.js::sink", "file": "a.js", "line": 5,
                           "taxonomy_id": "y"},
                "depth": 1,
                "path":  ["a.js::src", "a.js::sink"],
            }
        ],
        "snippets": {"a.js::src": "src", "a.js::sink": "sink"},
    }

    db = tmp_path / "ja.db"
    conn = sqlite3.connect(str(db))
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

    fake_cg = SimpleNamespace(db_path=str(db))
    kernel, state = _kernel_with_state(findings)
    state.total_chains = 1
    services = {"js_analyzer_state": state, "js_analyzer_callgraph": fake_cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_id = "shell-Y"

    _install_fake_engine(
        monkeypatch,
        _resp_tool("js_examine_chain", {"chain_id": 1}),
        _resp_end(),
    )

    await claude_agent.analyse_chains_async(findings, kernel)

    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        "SELECT role FROM js_audit_turns ORDER BY turn_index"
    ).fetchall()
    run_row = conn.execute(
        "SELECT status, shell_session_id, target_folder FROM js_audit_runs"
    ).fetchone()
    conn.close()

    roles = [r[0] for r in rows]
    assert "user" in roles  # initial overview
    assert "assistant" in roles
    assert "tool_result" in roles
    assert run_row[0] == "completed"
    assert run_row[1] == "shell-Y"
    assert run_row[2] == "/tmp/app"


@pytest.mark.asyncio
async def test_audit_run_cap_exceeded_when_iteration_limit_hit(monkeypatch, tmp_path):
    import sqlite3

    from modules.js_analyzer.callgraph import SCHEMA

    db = tmp_path / "ja.db"
    conn = sqlite3.connect(str(db))
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

    fake_cg = SimpleNamespace(db_path=str(db))
    kernel, _ = _kernel_with_state(_FINDINGS)
    services = {"js_analyzer_state": kernel.services.get("js_analyzer_state"),
                "js_analyzer_callgraph": fake_cg}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_id = "shell-Z"

    monkeypatch.setattr(claude_agent, "MAX_ITER", 1)

    _install_fake_engine(
        monkeypatch,
        _resp_tool("js_get_hypothesis", {"chain_id": 1}),
    )

    await claude_agent.analyse_chains_async(_FINDINGS, kernel)
    conn = sqlite3.connect(str(db))
    status = conn.execute("SELECT status FROM js_audit_runs").fetchone()[0]
    conn.close()
    assert status == "cap_exceeded"
