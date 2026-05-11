"""Tests for js_consult_opus — bounded second-opinion tool."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

# Importing module first installs the path shim so `import config` resolves
# inside js_analyzer/ before claude_agent.py is imported.
from modules.js_analyzer.module import JsAnalyzerState  # isort:skip
from modules.js_analyzer import claude_agent  # noqa: I001
from modules.js_analyzer.claude_agent import (  # noqa: I001
    JS_CONSULT_OPUS_SCHEMA,
    JS_CONSULT_OPUS_TOOL,
    _RunContext,
    _consult_opus,
    _dispatch,
    _make_tools,
)
from kernel.schema import (
    Cost,
    EngineResponse,
    ToolCall,
    ToolUseBlock,
    Usage,
)


def _resp_end(in_tok: int = 0, out_tok: int = 0) -> EngineResponse:
    return EngineResponse(
        content=[],
        tool_calls=[],
        usage=Usage(input_tokens=in_tok, output_tokens=out_tok),
        cost=Cost(input_usd=0.0, output_usd=0.0),
        stop_reason="end_turn",
    )


def _resp_tool(name: str, args: dict, tool_id: str = "t1",
               in_tok: int = 100, out_tok: int = 50) -> EngineResponse:
    return EngineResponse(
        content=[ToolUseBlock(id=tool_id, name=name, input=args)],
        tool_calls=[ToolCall(id=tool_id, name=name, args=args)],
        usage=Usage(input_tokens=in_tok, output_tokens=out_tok),
        cost=Cost(input_usd=0.0, output_usd=0.0),
        stop_reason="tool_use",
    )


def _install_fake_engine(monkeypatch, *responses):
    queue = list(responses) or [_resp_end()]
    last = queue[-1]

    async def _respond(*_a, **_kw):
        return queue.pop(0) if queue else last

    fake_engine = MagicMock()
    fake_engine.respond = _respond
    fake_engine.model = claude_agent.CLAUDE_MODEL
    monkeypatch.setattr(
        claude_agent, "_resolve_audit_engine", lambda kernel: fake_engine,
    )
    return fake_engine


def _findings_with_chain(cid: int = 1) -> dict:
    return {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "framework_tags": ["angular"],
        "chains": [
            {
                "id": cid,
                "source": {"qname": "a.js::src", "file": "a.js", "line": 1,
                           "taxonomy_id": "location_hash"},
                "sink":   {"qname": "a.js::sink", "file": "a.js", "line": 5,
                           "taxonomy_id": "innerHTML_assign"},
                "depth": 1,
                "path":  ["a.js::src", "a.js::sink"],
            }
        ],
        "snippets": {
            "a.js::src":  "const x = location.hash;",
            "a.js::sink": "el.innerHTML = x;",
        },
    }


def _kernel_with_state():
    state = JsAnalyzerState()
    kernel = MagicMock()
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    return kernel, state


def _fake_opus_response(in_tok: int = 200, out_tok: int = 50, text: str = "verdict: not_exploitable"):
    resp = MagicMock()
    block = MagicMock()
    block.text = text
    resp.content = [block]
    resp.usage.input_tokens = in_tok
    resp.usage.output_tokens = out_tok
    return resp


def _patch_anthropic(monkeypatch, response):
    fake_client = MagicMock()
    fake_client.messages.create.return_value = response
    fake_client._captured_kwargs = []  # for inspection if needed

    def _create(**kwargs):
        fake_client._captured_kwargs.append(kwargs)
        return response
    fake_client.messages.create.side_effect = _create

    monkeypatch.setattr(
        claude_agent.anthropic, "Anthropic",
        lambda **kw: fake_client,
    )
    return fake_client


# ── tool registration / schema ───────────────────────────────────────────


def _stub_tools():
    return _make_tools({"chains": []}, None, None, _RunContext())


def test_consult_opus_tool_registered():
    names = [t.name for t in _stub_tools()]
    assert "js_consult_opus" in names


def test_consult_opus_tool_appended_after_existing():
    """consult_opus must be the LAST tool — append-only for cache discipline."""
    tools = _stub_tools()
    assert tools[-1].name == "js_consult_opus"
    # And the tools that existed before consult_opus must all still be there
    existing = {
        "js_examine_chain", "js_get_snippet", "js_submit_finding",
        "js_update_hypothesis", "js_get_hypothesis", "js_generate_report",
    }
    assert existing.issubset({t.name for t in tools[:-1]})


def test_consult_opus_description_contains_only_guard():
    desc = JS_CONSULT_OPUS_TOOL["description"]
    assert "ONLY when ALL of the following" in desc


def test_consult_opus_description_lists_specific_cases():
    desc = JS_CONSULT_OPUS_TOOL["description"]
    assert "prototype-pollution" in desc
    assert "bypassSecurityTrust" in desc
    assert "v-html" in desc
    assert "dangerouslySetInnerHTML" in desc


def test_consult_opus_schema_requires_chain_id_question_confidence():
    req = set(JS_CONSULT_OPUS_SCHEMA["required"])
    assert req == {"chain_id", "question", "confidence_so_far"}
    enum = JS_CONSULT_OPUS_SCHEMA["properties"]["confidence_so_far"]["enum"]
    assert set(enum) == {"very_low", "low", "medium"}


# ── handler behaviour ────────────────────────────────────────────────────


def test_consult_opus_rejects_medium_confidence(monkeypatch):
    fake = _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    out = _consult_opus(
        {"chain_id": "1", "question": "q", "confidence_so_far": "medium"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "medium" in out
    assert ctx.consults_used == 0
    fake.messages.create.assert_not_called()


def test_consult_opus_rejects_unknown_chain_id(monkeypatch):
    fake = _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    out = _consult_opus(
        {"chain_id": "999", "question": "q", "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "not in findings" in out
    assert ctx.consults_used == 0
    fake.messages.create.assert_not_called()


def test_consult_opus_rejects_invalid_confidence(monkeypatch):
    fake = _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    out = _consult_opus(
        {"chain_id": "1", "question": "q", "confidence_so_far": "high"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "invalid confidence_so_far" in out
    fake.messages.create.assert_not_called()


def test_consult_opus_rejects_empty_question(monkeypatch):
    fake = _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    out = _consult_opus(
        {"chain_id": "1", "question": "   ", "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "empty question" in out
    fake.messages.create.assert_not_called()


def test_consult_opus_respects_max_consults_cap(monkeypatch):
    fake = _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    ctx.consults_used = claude_agent.MAX_CONSULTS  # already at cap

    out = _consult_opus(
        {"chain_id": "1", "question": "q", "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "consult limit reached" in out
    fake.messages.create.assert_not_called()
    assert ctx.consults_used == claude_agent.MAX_CONSULTS  # unchanged


def test_consult_opus_respects_budget_cap(monkeypatch):
    fake = _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    ctx.consults_cost_usd = claude_agent.CONSULT_BUDGET_USD + 0.01

    out = _consult_opus(
        {"chain_id": "1", "question": "q", "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "consult budget reached" in out
    fake.messages.create.assert_not_called()


def test_consult_opus_returns_limit_message_when_capped(monkeypatch):
    _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    ctx.consults_used = claude_agent.MAX_CONSULTS

    out = _consult_opus(
        {"chain_id": "1", "question": "q", "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert f"{claude_agent.MAX_CONSULTS}/{claude_agent.MAX_CONSULTS}" in out


def test_consult_opus_happy_path_records_log(monkeypatch):
    fake = _patch_anthropic(monkeypatch, _fake_opus_response(in_tok=300, out_tok=100))
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    out = _consult_opus(
        {"chain_id": "1", "question": "does jQuery .html() escape?",
         "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "verdict" in out.lower() or "[js_consult_opus]" in out
    assert ctx.consults_used == 1
    assert len(ctx.consult_logs) == 1
    log = ctx.consult_logs[0]
    assert log["tokens_in"] == 300
    assert log["tokens_out"] == 100
    assert log["confidence"] == "low"
    assert log["cost_usd"] > 0
    fake.messages.create.assert_called_once()


def test_consult_opus_opus_call_has_no_tools(monkeypatch):
    """Anti-recursion: Opus must be invoked WITHOUT tools."""
    captured = {}

    def _create(**kwargs):
        captured.update(kwargs)
        return _fake_opus_response()

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = _create
    monkeypatch.setattr(
        claude_agent.anthropic, "Anthropic",
        lambda **kw: fake_client,
    )

    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    _consult_opus(
        {"chain_id": "1", "question": "q", "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "tools" not in captured
    assert captured["model"] == claude_agent.CLAUDE_OPUS_MODEL
    assert captured["max_tokens"] == 2048


def test_consult_opus_counts_iteration_toward_max_iter(monkeypatch):
    """Each consult goes through the loop iteration, so it counts toward MAX_ITER."""
    findings = _findings_with_chain()
    kernel = MagicMock()
    state = JsAnalyzerState()
    state.last_findings = findings
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_store.get.return_value = None
    kernel.session_store.set.return_value = None

    call_log: list[str] = []

    async def _respond(*_a, **_kw):
        call_log.append("respond")
        if len(call_log) == 1:
            return _resp_tool(
                "js_consult_opus",
                {"chain_id": "1", "question": "q", "confidence_so_far": "low"},
            )
        return _resp_end(in_tok=1, out_tok=1)

    fake_engine = MagicMock()
    fake_engine.respond = _respond
    fake_engine.model = claude_agent.CLAUDE_MODEL
    monkeypatch.setattr(
        claude_agent, "_resolve_audit_engine", lambda kernel: fake_engine,
    )

    opus_client = MagicMock()
    opus_client.messages.create.return_value = _fake_opus_response()
    monkeypatch.setattr(
        claude_agent.anthropic, "Anthropic", lambda **kw: opus_client,
    )

    import asyncio as _aio
    _aio.run(claude_agent.analyse_chains_async(findings, kernel))
    assert len(call_log) == 2
    assert opus_client.messages.create.call_count == 1


def test_consult_opus_cost_added_to_total_budget_check(monkeypatch):
    """Loop's BUDGET_LIMIT short-circuit must factor in ctx.consults_cost_usd.

    Pre-load consults_cost_usd by patching _RunContext's default factory.
    Then the very first iteration must short-circuit and the stop_reason
    string must mention 'consults'.
    """
    findings = _findings_with_chain()
    kernel = MagicMock()
    state = JsAnalyzerState()
    state.last_findings = findings
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_store.get.return_value = None
    kernel.session_store.set.return_value = None

    # Replace _RunContext with a subclass that starts pre-loaded with cost
    class _Preloaded(_RunContext):
        def __init__(self):
            super().__init__()
            self.consults_cost_usd = 5.0  # > BUDGET_LIMIT (2.0)

    monkeypatch.setattr(claude_agent, "_RunContext", _Preloaded)

    call_count = {"n": 0}

    async def _respond(*_a, **_kw):
        call_count["n"] += 1
        return _resp_end()

    fake_engine = MagicMock()
    fake_engine.respond = _respond
    fake_engine.model = claude_agent.CLAUDE_MODEL
    monkeypatch.setattr(
        claude_agent, "_resolve_audit_engine", lambda kernel: fake_engine,
    )

    import asyncio as _aio
    out = _aio.run(claude_agent.analyse_chains_async(findings, kernel))
    # Loop must short-circuit before calling the engine
    assert call_count["n"] == 0
    # Partial report should mention consult cost in stop_reason
    assert "consults" in out.lower() or "budget" in out.lower()


def test_consult_opus_counter_resets_per_audit_run(monkeypatch):
    """Two back-to-back analyse_chains_async runs must each start with a fresh ctx."""
    findings = _findings_with_chain()
    kernel = MagicMock()
    state = JsAnalyzerState()
    state.last_findings = findings
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_store.get.return_value = None
    kernel.session_store.set.return_value = None

    _install_fake_engine(monkeypatch, _resp_end())

    import asyncio as _aio
    _aio.run(claude_agent.analyse_chains_async(findings, kernel))
    after_first = state.last_consults_used
    state.last_consults_used = 99   # forcibly poison
    state.last_consult_log = [{"x": "y"}]
    state.last_consult_cost_usd = 99.0

    _aio.run(claude_agent.analyse_chains_async(findings, kernel))
    # Second run wrote fresh telemetry: zeros (no tool calls happened)
    assert state.last_consults_used == 0 == after_first
    assert state.last_consult_log == []
    assert state.last_consult_cost_usd == 0.0


def test_consult_opus_writes_to_state_consult_log(monkeypatch):
    """When loop ends, ctx.consult_logs must land on state.last_consult_log."""
    findings = _findings_with_chain()
    kernel = MagicMock()
    state = JsAnalyzerState()
    state.last_findings = findings
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_store.get.return_value = None
    kernel.session_store.set.return_value = None

    _install_fake_engine(
        monkeypatch,
        _resp_tool(
            "js_consult_opus",
            {"chain_id": "1", "question": "qstr",
             "confidence_so_far": "very_low"},
            in_tok=100, out_tok=50,
        ),
        _resp_end(in_tok=1, out_tok=1),
    )
    opus_client = MagicMock()
    opus_client.messages.create.return_value = _fake_opus_response()
    monkeypatch.setattr(
        claude_agent.anthropic, "Anthropic", lambda **kw: opus_client,
    )

    import asyncio as _aio
    _aio.run(claude_agent.analyse_chains_async(findings, kernel))

    assert state.last_consults_used == 1
    assert len(state.last_consult_log) == 1
    assert state.last_consult_log[0]["confidence"] == "very_low"
    assert state.last_consult_cost_usd > 0


def test_consult_opus_dispatch_routes_to_handler(monkeypatch):
    """_dispatch must route 'js_consult_opus' through _consult_opus."""
    _patch_anthropic(monkeypatch, _fake_opus_response())
    kernel, state = _kernel_with_state()
    ctx = _RunContext()
    out = _dispatch(
        "js_consult_opus",
        {"chain_id": "1", "question": "q", "confidence_so_far": "low"},
        _findings_with_chain(), state, kernel, ctx,
    )
    assert "[js_consult_opus]" in out
    assert ctx.consults_used == 1


def test_reporter_renders_consult_section():
    """When state has consults logged, generate_report must include the table."""
    state = JsAnalyzerState()
    state.last_findings = _findings_with_chain()
    state.total_chains = 1
    state.verdicts = {1: {
        "chain_id": 1, "verdict": "true_positive",
        "severity": "high", "vuln_class": "DOM XSS", "proof": "p",
    }}
    state.last_consult_log = [{
        "chain_id": "1", "question": "q", "confidence": "low",
        "tokens_in": 100, "tokens_out": 50, "cost_usd": 0.1234,
    }]
    state.last_consult_cost_usd = 0.1234
    state.last_consults_used = 1

    out = claude_agent._generate_report(state, state.last_findings, kernel=None)
    report = out["report"]
    assert "## Opus consultations" in report
    assert "0.1234" in report
    assert "Consult total" in report


def test_consult_opus_max_consults_default():
    assert claude_agent.MAX_CONSULTS == 5


def test_consult_opus_budget_default():
    assert claude_agent.CONSULT_BUDGET_USD == pytest.approx(1.50)
