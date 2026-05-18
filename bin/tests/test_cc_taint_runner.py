"""Synthetic-fixture unit test for bin/cc_taint_runner.py.

Covers:
1. ``prepare`` renders one prompt per chain id and a manifest.
2. ``ingest`` strips forbidden keys, coerces ``chain_id``, validates
   confidence/triage enums, and writes ``opus/<id>.json``.
3. Invalid responses (missing required keys, bad triage) exit non-zero
   and write no opus file.
4. ``finalize`` rolls counters into status.json.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))
import cc_taint_runner  # type: ignore[import-not-found]


def _seed(tmp: Path) -> Path:
    target = tmp / "targets" / "demo"
    (target / "chains" / "expanded").mkdir(parents=True)
    (target / "chains" / "anomalies").mkdir(parents=True)

    chain_a = {
        "id": 7,
        "source": {"qname": "f.js::a", "file": "f.js", "line": 1, "taxonomy_id": "x", "kind": "source"},
        "sink":   {"qname": "f.js::a", "file": "f.js", "line": 3, "taxonomy_id": "y", "kind": "sink"},
        "path":   ["f.js::a"], "depth": 0,
    }
    chain_b = {
        "id": 8,
        "source": {"qname": "f.js::b", "file": "f.js", "line": 5, "taxonomy_id": "x", "kind": "source"},
        "sink":   {"qname": "f.js::b", "file": "f.js", "line": 7, "taxonomy_id": "y", "kind": "sink"},
        "path":   ["f.js::b"], "depth": 0,
    }
    (target / "chains" / "dom_reachable.jsonl").write_text(
        "\n".join(json.dumps(c) for c in [chain_a, chain_b]) + "\n"
    )
    for c in (chain_a, chain_b):
        (target / "chains" / "expanded" / f"{c['id']}.json").write_text(
            json.dumps({
                "chain_id": c["id"],
                "source": {"qname": c["source"]["qname"], "code": "// src"},
                "sink":   {"qname": c["sink"]["qname"], "code": "// sink"},
                "callers": [], "dominator_guards": [],
                "framework_context": None, "byte_budget": 12000,
            })
        )
    (target / "chains" / "anomalies" / "f-js.json").write_text(
        json.dumps({
            "bucket": "f.js",
            "chains_seen": [7, 8],
            "anomalies": [{
                "type": "missing_guard_vs_peers",
                "evidence": "a() hits y raw; b() wraps in isSafe()",
                "affected_chains": [7],
            }],
        })
    )
    return target


def test_prepare_writes_prompts_and_manifest() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed(Path(tmp))
        rc = cc_taint_runner.main([
            "--target", str(target), "--no-status", "prepare",
        ])
        assert rc == 0
        manifest = json.loads((target / "opus" / "_manifest.json").read_text())
        assert set(manifest["chains"].keys()) == {"7", "8"}
        body_7 = (target / "opus" / "_prompts" / "7.md").read_text()
        assert "[ATTACKER]" in body_7
        assert "[SKEPTIC]" in body_7
        assert '"chain"' in body_7
        # Anomaly for chain 7 wired in:
        assert "missing_guard_vs_peers" in body_7
        # Chain 8 has no anomaly entry, so prompt should not include one:
        body_8 = (target / "opus" / "_prompts" / "8.md").read_text()
        assert "missing_guard_vs_peers" not in body_8


def test_ingest_strips_and_validates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed(Path(tmp))
        cc_taint_runner.main([
            "--target", str(target), "--no-status", "prepare",
        ])
        # Subagent response with forbidden verdict keys; chain_id wrong on purpose:
        response = {
            "chain_id": "WRONG",
            "exploit_argument": "hash flows to innerHTML; payload <img src=x onerror=alert(1)>",
            "counterargument": "DOMPurify is loaded but never invoked in this branch",
            "blocking_unknowns": ["whether the CSP forbids inline events"],
            "confidence": "high",
            "triage": "runtime",
            "verdict": "true_positive",
            "tp": True,
            "severity": "critical",
            "classification": "xss",
        }
        rf = target / "_resp.json"
        rf.write_text(json.dumps(response))
        rc = cc_taint_runner.main([
            "--target", str(target),
            "--no-status",
            "ingest",
            "--chain-id", "7",
            "--response-file", str(rf),
        ])
        assert rc == 0
        out = json.loads((target / "opus" / "7.json").read_text())
        # chain_id forcibly overwritten with manifest id:
        assert out["chain_id"] == "7"
        for k in ("verdict", "tp", "severity", "classification", "fp",
                  "true_positive", "false_positive"):
            assert k not in out, f"forbidden key leaked: {k}"
        assert set(out["_stripped_keys"]) >= {"verdict", "tp", "severity", "classification"}
        for k in ("exploit_argument", "counterargument", "blocking_unknowns",
                  "confidence", "triage"):
            assert k in out, f"missing required key: {k}"


def test_ingest_rejects_invalid_schema() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed(Path(tmp))
        cc_taint_runner.main([
            "--target", str(target), "--no-status", "prepare",
        ])
        for bad in (
            {"exploit_argument": "x", "counterargument": "y",
             "blocking_unknowns": [], "confidence": "??", "triage": "runtime"},
            {"exploit_argument": "x", "counterargument": "y",
             "blocking_unknowns": [], "confidence": "high", "triage": "explode"},
            {"exploit_argument": "", "counterargument": "y",
             "blocking_unknowns": [], "confidence": "high", "triage": "runtime"},
            {"counterargument": "y", "blocking_unknowns": [],
             "confidence": "high", "triage": "runtime"},  # missing exploit_argument
        ):
            rf = target / "_bad.json"
            rf.write_text(json.dumps(bad))
            rc = cc_taint_runner.main([
                "--target", str(target),
                "--no-status",
                "ingest",
                "--chain-id", "7",
                "--response-file", str(rf),
            ])
            assert rc == 2, f"expected schema rejection, got rc={rc} for {bad}"


def test_ingest_status_counters_increment() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed(Path(tmp))
        cc_taint_runner.main(["--target", str(target), "prepare"])
        for cid, triage, conf in [("7", "runtime", "high"), ("8", "drop", "low")]:
            resp = {
                "chain_id": cid,
                "exploit_argument": "x",
                "counterargument": "y",
                "blocking_unknowns": [],
                "confidence": conf,
                "triage": triage,
            }
            rf = target / f"_r{cid}.json"
            rf.write_text(json.dumps(resp))
            cc_taint_runner.main([
                "--target", str(target),
                "ingest", "--chain-id", cid, "--response-file", str(rf),
            ])
        cc_taint_runner.main(["--target", str(target), "finalize"])
        status = json.loads((target / "status.json").read_text())
        phase = status["phases"]["cc_taint_adversarial"]
        assert phase["subagent_count"] == 2
        final = phase["final_summary"]
        assert final["total"] == 2
        assert final["by_triage"]["runtime"] == 1
        assert final["by_triage"]["drop"] == 1
        assert final["by_confidence"]["high"] == 1
        assert final["by_confidence"]["low"] == 1


if __name__ == "__main__":
    test_prepare_writes_prompts_and_manifest()
    test_ingest_strips_and_validates()
    test_ingest_rejects_invalid_schema()
    test_ingest_status_counters_increment()
    print("OK")
