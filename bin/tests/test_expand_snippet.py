"""Synthetic-fixture unit test for bin/expand_snippet.py.

No real target needed — builds a temp ``targets/<name>/`` tree with a minimal
``js_analyzer.db`` (nodes + edges + node_tags), a ``sources/`` file, and a
``chains/hot.jsonl``, then runs ``expand_snippet.main()`` and asserts the
output JSON has every required key.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

BIN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))
import expand_snippet  # type: ignore[import-not-found]


SOURCE_JS = """\
export function getInput() {
  // hop2 caller: reads location.hash and forwards to renderer
  const raw = window.location.hash;
  return renderHash(raw);
}

export function renderHash(value) {
  // hop1 caller: validates length then delegates
  if (!isSafe(value)) {
    return null;
  }
  return setSink(value);
}

export function setSink(html) {
  try {
    if (html && html.length < 1024) {
      document.body.innerHTML = html;
    }
  } catch (err) {
    console.error(err);
  }
}
"""


def _build_fixture(root: Path) -> dict:
    target = root / "targets" / "demo"
    (target / "db").mkdir(parents=True)
    (target / "sources" / "host" / "app").mkdir(parents=True)
    (target / "chains").mkdir(parents=True)

    src_path = target / "sources" / "host" / "app" / "main.js"
    src_path.write_text(SOURCE_JS)

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
        CREATE TABLE edges (
            caller_id INT NOT NULL,
            callee_id INT,
            line INT,
            raw TEXT,
            callee_raw TEXT,
            resolved_kind TEXT,
            PRIMARY KEY (caller_id, line, callee_raw)
        );
        CREATE TABLE node_tags (
            node_id INT NOT NULL,
            taxonomy_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            severity TEXT NOT NULL,
            line INT NOT NULL,
            source TEXT NOT NULL DEFAULT 'regex',
            PRIMARY KEY (node_id, taxonomy_id, line)
        );
        """
    )
    file_rel = "host/app/main.js"
    rows = [
        # id, qname, file, name, kind, start, end
        (1, f"{file_rel}::getInput",   file_rel, "getInput",   "function", 1, 5),
        (2, f"{file_rel}::renderHash", file_rel, "renderHash", "function", 7, 13),
        (3, f"{file_rel}::setSink",    file_rel, "setSink",    "function", 15, 23),
    ]
    for r in rows:
        conn.execute(
            "INSERT INTO nodes (id, qualified_name, file, name, kind, start_line, end_line)"
            " VALUES (?,?,?,?,?,?,?)",
            r,
        )
    conn.executemany(
        "INSERT INTO edges (caller_id, callee_id, line, raw, callee_raw, resolved_kind)"
        " VALUES (?,?,?,?,?,?)",
        [
            (1, 2, 4,  "renderHash(raw)", "renderHash", "exact"),
            (2, 3, 11, "setSink(value)",  "setSink",    "exact"),
        ],
    )
    conn.executemany(
        "INSERT INTO node_tags (node_id, taxonomy_id, kind, severity, line, source)"
        " VALUES (?,?,?,?,?,?)",
        [
            (1, "location_hash",   "source", "high",     3,  "regex"),
            (3, "innerHTML_assign","sink",   "critical", 18, "ast"),
        ],
    )
    conn.commit()
    conn.close()

    chain = {
        "id": 42,
        "source": {
            "qname": f"{file_rel}::getInput",
            "file": file_rel,
            "line": 3,
            "taxonomy_id": "location_hash",
            "kind": "source",
        },
        "sink": {
            "qname": f"{file_rel}::setSink",
            "file": file_rel,
            "line": 18,
            "taxonomy_id": "innerHTML_assign",
            "kind": "sink",
        },
        "path": [
            f"{file_rel}::getInput",
            f"{file_rel}::renderHash",
            f"{file_rel}::setSink",
        ],
        "depth": 2,
        "cross_file": False,
        "score": 95.0,
        "vuln_class_hint": "DOM XSS",
    }
    (target / "chains" / "hot.jsonl").write_text(json.dumps(chain) + "\n")
    return {"target": target, "chain": chain}


def test_expand_snippet_writes_complete_bundle() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fx = _build_fixture(Path(tmp))
        target = fx["target"]

        rc = expand_snippet.main(
            [
                "--target", str(target),
                "--chain-id", "42",
                "--no-status",
            ]
        )
        assert rc == 0, f"expand_snippet exited {rc}"

        out_path = target / "chains" / "expanded" / "42.json"
        assert out_path.exists(), "expanded snippet file missing"
        data = json.loads(out_path.read_text())

        for key in (
            "chain_id", "source", "sink", "callers",
            "dominator_guards", "framework_context", "byte_budget",
        ):
            assert key in data, f"missing key: {key}"

        assert data["chain_id"] == 42
        assert data["source"]["qname"].endswith("::getInput")
        assert "window.location.hash" in data["source"]["code"]
        assert data["sink"]["qname"].endswith("::setSink")
        assert "document.body.innerHTML" in data["sink"]["code"]

        caller_qnames = {c["qname"] for c in data["callers"]}
        assert any(q.endswith("::renderHash") for q in caller_qnames), (
            f"renderHash caller missing: {caller_qnames}"
        )

        guard_kinds = {g["kind"] for g in data["dominator_guards"]}
        assert "try" in guard_kinds or "if" in guard_kinds, (
            f"expected if/try guard, got: {guard_kinds}"
        )
        assert data["byte_budget"] == 12000


def test_budget_truncates_oversize_callers() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fx = _build_fixture(Path(tmp))
        target = fx["target"]
        rc = expand_snippet.main(
            [
                "--target", str(target),
                "--chain-id", "42",
                "--byte-budget", "800",
                "--no-status",
            ]
        )
        assert rc == 0
        data = json.loads((target / "chains" / "expanded" / "42.json").read_text())
        assert data["truncated"] is True
        assert data["notes"], "expected at least one truncation note"


def test_stdin_mode() -> None:
    import io

    with tempfile.TemporaryDirectory() as tmp:
        fx = _build_fixture(Path(tmp))
        target = fx["target"]

        old_stdin = sys.stdin
        sys.stdin = io.StringIO(json.dumps(fx["chain"]))
        try:
            rc = expand_snippet.main(
                ["--target", str(target), "--stdin", "--no-status"]
            )
        finally:
            sys.stdin = old_stdin
        assert rc == 0
        assert (target / "chains" / "expanded" / "42.json").exists()


if __name__ == "__main__":
    test_expand_snippet_writes_complete_bundle()
    test_budget_truncates_oversize_callers()
    test_stdin_mode()
    print("OK")
