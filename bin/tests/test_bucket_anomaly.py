"""Synthetic-fixture unit test for bin/bucket_anomaly.py.

Covers:
1. ``prepare`` mode bucket-by-sink-file grouping and prompt rendering.
2. ``ingest`` mode strips verdict-flavoured keys before persisting.
3. ``--dry-run`` writes no files.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))
import bucket_anomaly  # type: ignore[import-not-found]


def _seed_target(tmp: Path) -> Path:
    target = tmp / "targets" / "demo"
    (target / "db").mkdir(parents=True)
    (target / "chains" / "expanded").mkdir(parents=True)
    (target / "sources").mkdir(parents=True)

    db_path = target / "db" / "js_analyzer.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY,
            qualified_name TEXT UNIQUE,
            file TEXT,
            name TEXT,
            parent TEXT,
            kind TEXT,
            start_line INT,
            end_line INT,
            original_line INTEGER,
            original_file TEXT
        );
        """
    )
    file_a = "host/app/A.js"
    file_b = "host/app/B.js"
    rows = [
        (1, f"{file_a}::renderRaw",  file_a, "renderRaw",  "function", 1,  10),
        (2, f"{file_a}::renderSafe", file_a, "renderSafe", "function", 12, 22),
        (3, f"{file_a}::__noise",    file_a, "__noise",    "function", 25, 27),
        (4, f"{file_b}::leakHash",   file_b, "leakHash",   "function", 1,  8),
    ]
    for r in rows:
        conn.execute(
            "INSERT INTO nodes (id, qualified_name, file, name, kind, start_line, end_line)"
            " VALUES (?,?,?,?,?,?,?)",
            r,
        )
    conn.commit()
    conn.close()

    chains = [
        {
            "id": 100,
            "source": {"qname": f"{file_a}::renderRaw", "file": file_a, "line": 3,
                       "taxonomy_id": "location_hash", "kind": "source"},
            "sink":   {"qname": f"{file_a}::renderRaw", "file": file_a, "line": 5,
                       "taxonomy_id": "innerHTML_assign", "kind": "sink"},
            "path": [f"{file_a}::renderRaw"], "depth": 0,
        },
        {
            "id": 101,
            "source": {"qname": f"{file_a}::renderSafe", "file": file_a, "line": 13,
                       "taxonomy_id": "location_hash", "kind": "source"},
            "sink":   {"qname": f"{file_a}::renderSafe", "file": file_a, "line": 18,
                       "taxonomy_id": "innerHTML_assign", "kind": "sink"},
            "path": [f"{file_a}::renderSafe"], "depth": 0,
        },
        {
            "id": 200,
            "source": {"qname": f"{file_b}::leakHash", "file": file_b, "line": 3,
                       "taxonomy_id": "location_hash", "kind": "source"},
            "sink":   {"qname": f"{file_b}::leakHash", "file": file_b, "line": 6,
                       "taxonomy_id": "fetch_call", "kind": "sink"},
            "path": [f"{file_b}::leakHash"], "depth": 0,
        },
    ]
    chains_path = target / "chains" / "dom_reachable.jsonl"
    chains_path.write_text("\n".join(json.dumps(c) for c in chains) + "\n")

    for c in chains:
        (target / "chains" / "expanded" / f"{c['id']}.json").write_text(
            json.dumps(
                {
                    "chain_id": c["id"],
                    "source": {"qname": c["source"]["qname"], "code": "// src"},
                    "sink":   {"qname": c["sink"]["qname"], "code": "// sink"},
                    "callers": [],
                    "dominator_guards": [],
                    "framework_context": None,
                    "byte_budget": 12000,
                }
            )
        )
    return target


def test_prepare_groups_by_sink_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed_target(Path(tmp))
        rc = bucket_anomaly.main([
            "--target", str(target),
            "--no-status",
            "prepare",
        ])
        assert rc == 0
        manifest = json.loads((target / "chains" / "anomalies" / "_manifest.json").read_text())
        buckets = manifest["buckets"]
        assert set(buckets.keys()) == {"host/app/A.js", "host/app/B.js"}
        a_bucket = buckets["host/app/A.js"]
        assert sorted(a_bucket["chains"]) == [100, 101]
        assert buckets["host/app/B.js"]["chain_count"] == 1

        prompt_path = target / a_bucket["prompt_path"]
        body = prompt_path.read_text()
        assert "host/app/A.js" in body
        assert '"chain_ids"' in body
        assert "::renderRaw" in body and "::renderSafe" in body
        # NEVER an emitted verdict in our own template:
        assert "verdict" not in body.lower() or "no `verdict`" in body.lower()


def test_dry_run_writes_no_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed_target(Path(tmp))
        rc = bucket_anomaly.main([
            "--target", str(target),
            "--no-status",
            "--dry-run",
        ])
        assert rc == 0
        assert not (target / "chains" / "anomalies" / "_manifest.json").exists()
        prompts_dir = target / "chains" / "anomalies" / "_prompts"
        assert not prompts_dir.exists() or not any(prompts_dir.iterdir())


def test_ingest_strips_verdict_keys() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = _seed_target(Path(tmp))
        # Prepare first so the anomalies/ dir exists.
        bucket_anomaly.main([
            "--target", str(target), "--no-status", "prepare",
        ])
        verdict_laden = {
            "bucket": "host/app/A.js",
            "chains_seen": [100, 101],
            "anomalies": [
                {
                    "type": "missing_guard_vs_peers",
                    "evidence": "renderRaw hits innerHTML without isSafe; renderSafe wraps",
                    "affected_chains": [100],
                    # forbidden:
                    "verdict": "true_positive",
                    "confidence": "high",
                    "severity": "critical",
                    "tp": True,
                },
                {
                    "type": "BOGUS_TYPE",
                    "evidence": "should be coerced to sibling_divergence",
                    "affected_chains": [101],
                    "triage": "runtime",
                },
            ],
            # forbidden at top level:
            "verdict": "tp",
            "classification": "xss",
        }
        rf = target / "_response.json"
        rf.write_text(json.dumps(verdict_laden))
        rc = bucket_anomaly.main([
            "--target", str(target),
            "--no-status",
            "ingest",
            "--bucket", "host/app/A.js",
            "--response-file", str(rf),
        ])
        assert rc == 0

        # Find the written anomaly file.
        anomaly_files = list((target / "chains" / "anomalies").glob("*.json"))
        anomaly_files = [p for p in anomaly_files if p.name != "_manifest.json"]
        assert anomaly_files, "no anomaly file written"
        data = json.loads(anomaly_files[0].read_text())

        # Top-level verdict keys gone.
        forbidden = {"verdict", "tp", "fp", "classification", "confidence",
                     "severity", "triage", "true_positive", "false_positive"}
        assert not (set(data.keys()) & forbidden), data.keys()
        # Per-anomaly verdict keys gone too.
        for a in data["anomalies"]:
            assert not (set(a.keys()) & forbidden), a
        # Bogus type coerced.
        bogus = [a for a in data["anomalies"] if "should be coerced" in a["evidence"]]
        assert bogus and bogus[0]["type"] == "sibling_divergence"
        # Tracked which keys we dropped.
        assert "_stripped_keys" in data
        assert any(k in data["_stripped_keys"] for k in ("verdict", "tp", "classification"))


if __name__ == "__main__":
    test_prepare_groups_by_sink_file()
    test_dry_run_writes_no_files()
    test_ingest_strips_verdict_keys()
    print("OK")
