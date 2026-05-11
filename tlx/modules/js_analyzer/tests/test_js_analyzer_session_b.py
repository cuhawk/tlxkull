"""Session B tests — chain-confirmation tools and async engine loop."""
from __future__ import annotations

import asyncio
import json
import time
from unittest.mock import MagicMock

import pytest

from kernel.schema import Cost, EngineResponse, Usage
from modules.js_analyzer.module import (
    JsAnalyzerState,
    _tool_examine_chain,
    _tool_generate_report,
    _tool_get_hypothesis,
    _tool_submit_finding,
    _tool_update_hypothesis,
)


def _resp_end(in_tok: int = 0, out_tok: int = 0) -> EngineResponse:
    return EngineResponse(
        content=[],
        tool_calls=[],
        usage=Usage(input_tokens=in_tok, output_tokens=out_tok),
        cost=Cost(input_usd=0.0, output_usd=0.0),
        stop_reason="end_turn",
    )


def _install_fake_engine(monkeypatch, *responses, slow_seconds: float | None = None):
    """Patch _resolve_audit_engine to return a fake whose .respond awaits these EngineResponses."""
    from modules.js_analyzer import claude_agent

    queue = list(responses) or [_resp_end()]
    last = queue[-1]

    async def _respond(*_a, **_kw):
        if slow_seconds is not None:
            await asyncio.sleep(slow_seconds)
        return queue.pop(0) if queue else last

    fake_engine = MagicMock()
    fake_engine.respond = _respond
    fake_engine.model = claude_agent.CLAUDE_MODEL
    monkeypatch.setattr(
        claude_agent, "_resolve_audit_engine", lambda kernel: fake_engine,
    )
    return fake_engine


def _kernel_with_findings(findings: dict | None = None):
    state = JsAnalyzerState()
    if findings is not None:
        state.last_findings = findings
        state.total_chains = len(findings.get("chains", []))
    kernel = MagicMock()
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)
    kernel.session_store.get.return_value = None
    kernel.session_store.set.return_value = None
    return kernel, state


def _simple_findings():
    return {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 10, "edges": 5, "tags": 2},
        "chains": [
            {
                "id": 1,
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


def test_examine_chain_returns_chain_and_snippets():
    kernel, _ = _kernel_with_findings(_simple_findings())
    result = json.loads(_tool_examine_chain(kernel, 1))
    assert result["chain"]["id"] == 1
    assert "a.js::src" in result["snippets"]


def test_examine_chain_unknown_id_returns_error():
    kernel, _ = _kernel_with_findings(_simple_findings())
    result = json.loads(_tool_examine_chain(kernel, 99))
    assert "error" in result
    assert "valid_ids" in result


def test_examine_chain_no_findings_returns_error():
    kernel, _ = _kernel_with_findings(None)
    result = json.loads(_tool_examine_chain(kernel, 1))
    assert "error" in result


def test_submit_finding_records_verdict_and_decrements():
    kernel, state = _kernel_with_findings(_simple_findings())
    result = json.loads(
        _tool_submit_finding(kernel, 1, "true_positive", "xss via hash", "high", "DOM XSS")
    )
    assert result["ok"] is True
    assert result["chains_remaining"] == 0
    assert state.verdicts[1]["verdict"] == "true_positive"
    assert 1 in state.reviewed


def test_generate_report_after_submit():
    kernel, state = _kernel_with_findings(_simple_findings())
    _tool_submit_finding(kernel, 1, "true_positive", "proof", "high", "DOM XSS")
    result = json.loads(_tool_generate_report(kernel))
    assert result["ok"] is True
    assert "Security Analysis Report" in result["report"]
    assert "DOM XSS" in result["report"]
    assert state.audit_status == "done"
    assert state.last_report is not None


def test_generate_report_false_positive():
    kernel, state = _kernel_with_findings(_simple_findings())
    _tool_submit_finding(kernel, 1, "false_positive", "sanitiser present")
    result = json.loads(_tool_generate_report(kernel))
    assert "False Positives" in result["report"]
    assert "High Severity" in result["report"]


def test_update_and_get_hypothesis_roundtrip():
    kernel, state = _kernel_with_findings(_simple_findings())
    _tool_update_hypothesis(kernel, 1, status="confirmed", note="xss confirmed",
                            confidence=0.9, tested_path="a.js::src")
    hyp = json.loads(_tool_get_hypothesis(kernel, 1))
    assert hyp["status"] == "confirmed"
    assert "xss confirmed" in hyp["notes"]
    assert hyp["confidence"] == pytest.approx(0.9)
    assert "a.js::src" in hyp["tested_paths"]


def test_get_hypothesis_missing_returns_open():
    kernel, _ = _kernel_with_findings(_simple_findings())
    hyp = json.loads(_tool_get_hypothesis(kernel, 99))
    assert hyp["status"] == "open"
    assert hyp["confidence"] == pytest.approx(0.5)


def test_hypotheses_persisted_on_submit():
    kernel, state = _kernel_with_findings(_simple_findings())
    _tool_update_hypothesis(kernel, 1, status="confirmed", note="note")
    _tool_submit_finding(kernel, 1, "true_positive", "proof")
    kernel.session_store.set.assert_called()

    hyp_calls = [
        c for c in kernel.session_store.set.call_args_list
        if c[0][0] == "js_analyzer_hypotheses"
    ]
    assert hyp_calls
    data = json.loads(hyp_calls[-1][0][1])
    assert len(data) == 1
    only_key = next(iter(data))
    assert len(only_key) == 16
    assert data[only_key]["status"] == "confirmed"


@pytest.mark.asyncio
async def test_analyse_chains_writes_cost_to_state(monkeypatch):
    from modules.js_analyzer import claude_agent

    findings = {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "chains": [],
        "snippets": {},
    }
    kernel, state = _kernel_with_findings(findings)

    _install_fake_engine(monkeypatch, _resp_end(in_tok=100, out_tok=25))

    await claude_agent.analyse_chains_async(findings, kernel)
    assert state.last_audit_cost_usd >= 0
    assert state.last_audit_tokens == 125


@pytest.mark.asyncio
async def test_audit_loop_passes_system_prompt_and_tools_to_engine(monkeypatch):
    """Replaces the previous direct-anthropic cache-control assertion. Cache
    control is now applied by ClaudeEngine; the audit's job is to hand the
    engine the system prompt and Tool list."""
    from kernel.tools import Tool
    from modules.js_analyzer import claude_agent

    findings = {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "chains": [],
        "snippets": {},
    }
    kernel, _ = _kernel_with_findings(findings)

    captured: dict = {}

    async def _respond(messages, tools, system, max_tokens=None):
        captured["system"] = system
        captured["tools"] = tools
        captured["messages"] = messages
        return _resp_end()

    fake_engine = MagicMock()
    fake_engine.respond = _respond
    fake_engine.model = claude_agent.CLAUDE_MODEL
    monkeypatch.setattr(
        claude_agent, "_resolve_audit_engine", lambda kernel: fake_engine,
    )

    await claude_agent.analyse_chains_async(findings, kernel)

    assert isinstance(captured["system"], str)
    assert "How to work" in captured["system"]
    assert isinstance(captured["tools"], list)
    assert all(isinstance(t, Tool) for t in captured["tools"])
    assert captured["tools"][-1].name == "js_consult_opus"


@pytest.mark.asyncio
async def test_dispatch_async_awaits_coroutine():
    from kernel.slash import SlashCommand, SlashRegistry
    reg = SlashRegistry()

    async def _async_handler(args, kernel):
        return "async result"

    reg.register(SlashCommand(
        name="test_async",
        description="test",
        handler=_async_handler,
    ))

    result = await reg.dispatch_async("/test_async", None)
    assert result == "async result"


@pytest.mark.asyncio
async def test_dispatch_async_works_for_sync_handler():
    from kernel.slash import SlashRegistry
    reg = SlashRegistry()
    result = await reg.dispatch_async("/help", MagicMock())
    assert "available commands" in result


def test_price_per_token_known_model():
    from kernel.engines.claude import price_per_token

    in_p, out_p = price_per_token("claude-sonnet-4-6")
    assert in_p == pytest.approx(3.00 / 1e6)
    assert out_p == pytest.approx(15.00 / 1e6)


def test_price_per_token_unknown_model_warns():
    import structlog

    from kernel.engines.claude import price_per_token

    with structlog.testing.capture_logs() as logs:
        in_p, out_p = price_per_token("nonexistent-model-2099")

    assert in_p == 0.0 and out_p == 0.0
    events = [r for r in logs if r.get("event") == "claude_engine.unknown_model_pricing"]
    assert events
    assert events[0]["log_level"] == "warning"
    assert events[0]["model"] == "nonexistent-model-2099"


@pytest.mark.asyncio
async def test_analyse_chains_does_not_block_event_loop(monkeypatch):
    from modules.js_analyzer import claude_agent

    findings = {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "chains": [],
        "snippets": {},
    }
    kernel, state = _kernel_with_findings(findings)

    _install_fake_engine(monkeypatch, _resp_end(), slow_seconds=0.5)

    beats: list[float] = []

    async def heartbeat():
        for _ in range(20):
            await asyncio.sleep(0.05)
            beats.append(time.monotonic())

    await asyncio.gather(
        claude_agent.analyse_chains_async(findings, kernel),
        heartbeat(),
    )

    assert len(beats) >= 5


def test_chain_signature_stable_across_runs():
    from modules.js_analyzer.module import _chain_signature

    chain_a = {
        "id": 1,
        "source": {"qname": "a.js::src", "line": 10},
        "sink":   {"qname": "a.js::sink", "line": 42},
    }
    chain_b = {
        "id": 99,
        "source": {"qname": "a.js::src", "line": 10},
        "sink":   {"qname": "a.js::sink", "line": 42},
    }
    assert _chain_signature(chain_a) == _chain_signature(chain_b)


def test_chain_signature_differs_on_line_shift():
    from modules.js_analyzer.module import _chain_signature

    chain_a = {
        "source": {"qname": "a.js::src", "line": 10},
        "sink":   {"qname": "a.js::sink", "line": 42},
    }
    chain_b = {
        "source": {"qname": "a.js::src", "line": 11},
        "sink":   {"qname": "a.js::sink", "line": 42},
    }
    assert _chain_signature(chain_a) != _chain_signature(chain_b)


def test_hypothesis_kv_round_trips_sig_keyed():
    from modules.js_analyzer.module import (
        _load_hypotheses_kv,
        _save_hypotheses_kv,
    )

    storage: dict[str, str] = {}

    kernel = MagicMock()
    kernel.session_store.set.side_effect = lambda k, v: storage.__setitem__(k, v)
    kernel.session_store.get.side_effect = lambda k: storage.get(k)

    payload = {"abc1234567890def": {"status": "confirmed", "notes": ["note"]}}
    _save_hypotheses_kv(kernel, payload)
    loaded = _load_hypotheses_kv(kernel)
    assert loaded == payload


def test_legacy_chain_id_keyed_hypotheses_dropped():
    import structlog

    from modules.js_analyzer.module import _load_hypotheses_kv

    kernel = MagicMock()
    kernel.session_store.get.return_value = json.dumps({"1": {"status": "open"}})

    with structlog.testing.capture_logs() as logs:
        result = _load_hypotheses_kv(kernel)

    assert result == {}
    events = [r for r in logs if r.get("event") == "js_analyzer.hypothesis_kv_legacy_dropped"]
    assert events


def _findings_with_chains(ids: list[int]) -> dict:
    return {
        "target_folder": "/tmp/app",
        "index_stats": {"nodes": 0, "edges": 0, "tags": 0},
        "chains": [
            {
                "id": cid,
                "source": {"qname": f"f{cid}.js::src", "file": f"f{cid}.js", "line": 1,
                            "taxonomy_id": "x"},
                "sink":   {"qname": f"f{cid}.js::sink", "file": f"f{cid}.js", "line": 5,
                            "taxonomy_id": "y"},
                "depth": 1,
                "path":  [f"f{cid}.js::src", f"f{cid}.js::sink"],
            }
            for cid in ids
        ],
        "snippets": {},
    }


@pytest.mark.asyncio
async def test_verdict_persists_then_resumes(monkeypatch):
    from modules.js_analyzer import claude_agent
    from modules.js_analyzer.module import (
        _save_verdicts_kv,
    )

    findings = _findings_with_chains([1, 2, 3])
    storage: dict[str, str] = {}

    kernel = MagicMock()
    kernel.session_store.set.side_effect = lambda k, v: storage.__setitem__(k, v)
    kernel.session_store.get.side_effect = lambda k: storage.get(k)

    from modules.js_analyzer.module import JsAnalyzerState
    state = JsAnalyzerState()
    state.last_findings = findings
    state.total_chains = 3
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    state.verdicts = {
        1: {"chain_id": 1, "verdict": "true_positive", "severity": "high",
            "vuln_class": "x", "proof": "p1"},
        2: {"chain_id": 2, "verdict": "false_positive", "severity": "n/a",
            "vuln_class": "", "proof": "p2"},
    }
    _save_verdicts_kv(kernel, state.verdicts)
    assert storage.get("js_analyzer_verdicts_inflight")

    _install_fake_engine(monkeypatch, _resp_end())

    fresh_state = JsAnalyzerState()
    fresh_state.last_findings = findings
    services["js_analyzer_state"] = fresh_state

    await claude_agent.analyse_chains_async(findings, kernel)
    assert set(fresh_state.verdicts.keys()) == {1, 2}
    assert fresh_state.reviewed == {1, 2}


@pytest.mark.asyncio
async def test_resume_with_unrelated_findings_clears(monkeypatch):
    from modules.js_analyzer import claude_agent
    from modules.js_analyzer.module import JsAnalyzerState, _save_verdicts_kv

    findings = _findings_with_chains([10, 11])
    storage: dict[str, str] = {}

    kernel = MagicMock()
    kernel.session_store.set.side_effect = lambda k, v: storage.__setitem__(k, v)
    kernel.session_store.get.side_effect = lambda k: storage.get(k)

    state = JsAnalyzerState()
    state.last_findings = findings
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    _save_verdicts_kv(kernel, {
        1: {"chain_id": 1, "verdict": "true_positive", "severity": "high",
            "vuln_class": "", "proof": ""},
        2: {"chain_id": 2, "verdict": "false_positive", "severity": "n/a",
            "vuln_class": "", "proof": ""},
        3: {"chain_id": 3, "verdict": "true_positive", "severity": "high",
            "vuln_class": "", "proof": ""},
    })

    _install_fake_engine(monkeypatch, _resp_end())

    await claude_agent.analyse_chains_async(findings, kernel)
    assert state.verdicts == {}


@pytest.mark.asyncio
async def test_clear_after_report_generation():
    from modules.js_analyzer.module import (
        JsAnalyzerState,
        _save_verdicts_kv,
        _tool_generate_report,
    )

    findings = _findings_with_chains([1])
    storage: dict[str, str] = {}

    kernel = MagicMock()
    kernel.session_store.set.side_effect = lambda k, v: storage.__setitem__(k, v)
    kernel.session_store.get.side_effect = lambda k: storage.get(k)

    state = JsAnalyzerState()
    state.last_findings = findings
    state.total_chains = 1
    state.verdicts = {1: {"chain_id": 1, "verdict": "true_positive",
                          "severity": "high", "vuln_class": "x", "proof": "p"}}
    services = {"js_analyzer_state": state}
    kernel.services.get.side_effect = lambda k, d=None: services.get(k, d)

    _save_verdicts_kv(kernel, state.verdicts)
    assert storage["js_analyzer_verdicts_inflight"] != "{}"

    _tool_generate_report(kernel)
    assert storage["js_analyzer_verdicts_inflight"] == "{}"
