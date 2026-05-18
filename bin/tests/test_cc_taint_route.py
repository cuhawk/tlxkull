"""Synthetic-fixture unit test for bin/cc_taint_route.py.

Covers:
1. Routing matrix: runtime/high → browser_confirm, runtime/medium →
   mock_run, drop → fp_archive, evidence_gap → re_expand (with retry
   bump).
2. Idempotency: a second run does not duplicate queue entries.
3. evidence_gap with retries already at the cap is parked under
   fp_archive with reason ``evidence_gap_max_retries``.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))
import cc_taint_route  # type: ignore[import-not-found]


def _seed(tmp: Path) -> Path:
    target = tmp / "targets" / "demo"
    (target / "opus").mkdir(parents=True)
    (target / "chains").mkdir(parents=True)

    chains = [
        {"id": 10, "source": {"qname": "f::a"}, "sink": {"qname": "f::a"}},  # high/runtime
        {"id": 11, "source": {"qname": "f::b"}, "sink": {"qname": "f::b"}},  # medium/runtime
        {"id": 12, "source": {"qname": "f::c"}, "sink": {"qname": "f::c"}},  # low/runtime
        {"id": 13, "source": {"qname": "f::d"}, "sink": {"qname": "f::d"}},  # evidence_gap (retries=0)
        {"id": 14, "source": {"qname": "f::e"}, "sink": {"qname": "f::e"}},  # evidence_gap (retries=2, capped)
        {"id": 15, "source": {"qname": "f::f"}, "sink": {"qname": "f::f"}},  # drop
    ]
    (target / "chains" / "dom_reachable.jsonl").write_text(
        "\n".join(json.dumps(c) for c in chains) + "\n"
    )

    opus_records = [
        (10, {"chain_id": 10, "exploit_argument": "x", "counterargument": "y",
              "blocking_unknowns": [], "confidence": "high",   "triage": "runtime"}),
        (11, {"chain_id": 11, "exploit_argument": "x", "counterargument": "y",
              "blocking_unknowns": [], "confidence": "medium", "triage": "runtime"}),
        (12, {"chain_id": 12, "exploit_argument": "x", "counterargument": "y",
              "blocking_unknowns": [], "confidence": "low",    "triage": "runtime"}),
        (13, {"chain_id": 13, "exploit_argument": "x", "counterargument": "y",
              "blocking_unknowns": ["need to see CSP"],
              "confidence": "medium", "triage": "evidence_gap"}),
        (14, {"chain_id": 14, "exploit_argument": "x", "counterargument": "y",
              "blocking_unknowns": ["already exhausted"],
              "confidence": "low", "triage": "evidence_gap", "retries": 2}),
        (15, {"chain_id": 15, "exploit_argument": "x", "counterargument": "y",
              "blocking_unknowns": [], "confidence": "high", "triage": "drop"}),
    ]
    for cid, rec in opus_records:
        (target / "opus" / f"{cid}.json").write_text(json.dumps(rec, indent=2))
    return target


def test_route_matrix() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed(Path(tmp))
        rc = cc_taint_route.main([
            "--target", str(target), "--no-status",
        ])
        assert rc == 0
        c = json.loads((target / "findings" / "_queue_browser_confirm.jsonl").read_text().splitlines()[0])
        assert c["chain_id"] == "10"
        assert c["confidence"] == "high"
        assert c["chain"]["id"] == 10

        mock_ids = [
            json.loads(line)["chain_id"]
            for line in (target / "findings" / "_queue_mock_run.jsonl").read_text().splitlines()
        ]
        assert sorted(mock_ids) == ["11", "12"]

        re_expand = [
            json.loads(line)
            for line in (target / "chains" / "_re_expand_queue.jsonl").read_text().splitlines()
        ]
        assert len(re_expand) == 1
        assert re_expand[0]["chain_id"] == "13"
        assert re_expand[0]["retries"] == 1
        assert "need to see CSP" in re_expand[0]["hint"]

        fp = [
            json.loads(line)
            for line in (target / "chains" / "_fp_archive.jsonl").read_text().splitlines()
        ]
        # chain 15 -> drop, chain 14 -> evidence_gap_max_retries (parked here)
        fp_ids = {r["chain_id"]: r for r in fp}
        assert "15" in fp_ids
        assert "14" in fp_ids
        assert fp_ids["14"].get("reason") == "evidence_gap_max_retries"

        # retries bumped on the opus record for chain 13:
        rec_13 = json.loads((target / "opus" / "13.json").read_text())
        assert rec_13["retries"] == 1


def test_idempotent() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed(Path(tmp))
        cc_taint_route.main(["--target", str(target), "--no-status"])
        # Snapshot all queue file line counts.
        counts_before = {
            "browser": len((target / "findings" / "_queue_browser_confirm.jsonl").read_text().splitlines()),
            "mock":    len((target / "findings" / "_queue_mock_run.jsonl").read_text().splitlines()),
            "re":      len((target / "chains" / "_re_expand_queue.jsonl").read_text().splitlines()),
            "fp":      len((target / "chains" / "_fp_archive.jsonl").read_text().splitlines()),
        }
        # Re-run — retries on chain 13 is now 1, so it would re-queue if dedupe broke.
        cc_taint_route.main(["--target", str(target), "--no-status"])
        counts_after = {
            "browser": len((target / "findings" / "_queue_browser_confirm.jsonl").read_text().splitlines()),
            "mock":    len((target / "findings" / "_queue_mock_run.jsonl").read_text().splitlines()),
            "re":      len((target / "chains" / "_re_expand_queue.jsonl").read_text().splitlines()),
            "fp":      len((target / "chains" / "_fp_archive.jsonl").read_text().splitlines()),
        }
        assert counts_before == counts_after, (counts_before, counts_after)


def test_dry_run_writes_nothing() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed(Path(tmp))
        cc_taint_route.main(["--target", str(target), "--no-status", "--dry-run"])
        assert not (target / "findings" / "_queue_browser_confirm.jsonl").exists()
        assert not (target / "findings" / "_queue_mock_run.jsonl").exists()
        assert not (target / "chains" / "_re_expand_queue.jsonl").exists()
        assert not (target / "chains" / "_fp_archive.jsonl").exists()
        # opus record retries should NOT have been bumped:
        rec_13 = json.loads((target / "opus" / "13.json").read_text())
        assert int(rec_13.get("retries", 0)) == 0


if __name__ == "__main__":
    test_route_matrix()
    test_idempotent()
    test_dry_run_writes_nothing()
    print("OK")
