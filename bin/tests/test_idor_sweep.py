"""Tests for bin/idor_sweep.py (plan + consume phases).

Uses a tmp target dir to avoid polluting real engagements.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

BIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN))

import idor_sweep as sw  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mk_target(tmp: Path, name: str = "t") -> Path:
    """Create a minimal target dir with status.json."""
    tdir = tmp / "targets" / name
    tdir.mkdir(parents=True)
    (tdir / "status.json").write_text("{}")
    return tdir


def _patch_targets_root(monkey_tmp: Path) -> Path:
    """Point _lib.TARGETS_DIR at a temp dir for the duration of a test."""
    import _lib
    original = _lib.TARGETS_DIR
    _lib.TARGETS_DIR = monkey_tmp / "targets"
    return original


def _restore_targets_root(original: Path) -> None:
    import _lib
    _lib.TARGETS_DIR = original


# ---------------------------------------------------------------------------
# _apply_mutation — unit
# ---------------------------------------------------------------------------

def test_apply_mutation_path():
    import id_patterns as ip
    req = {"method": "GET", "url": "https://x.com/v1/users/42/orders",
           "headers": {}, "body": None}
    cands = ip.extract_candidates(req)
    target = next(c for c in cands if c.location == "path" and c.value == "42")
    new_req = sw._apply_mutation(req, target, 99)
    assert "/users/99/orders" in new_req["url"]


def test_apply_mutation_query():
    import id_patterns as ip
    req = {"method": "GET", "url": "https://x.com/orders?order_id=99&page=2",
           "headers": {}, "body": None}
    cand = next(c for c in ip.extract_candidates(req) if c.name == "order_id")
    new_req = sw._apply_mutation(req, cand, 100)
    assert "order_id=100" in new_req["url"]
    assert "page=2" in new_req["url"]


def test_apply_mutation_header():
    import id_patterns as ip
    req = {"method": "GET", "url": "https://x.com/me",
           "headers": {"X-User-Id": "42"}, "body": None}
    cand = next(c for c in ip.extract_candidates(req) if c.location == "header")
    new_req = sw._apply_mutation(req, cand, 99)
    assert new_req["headers"]["X-User-Id"] == "99"


def test_apply_mutation_body_json():
    import id_patterns as ip
    req = {"method": "POST", "url": "https://x.com/cmd",
           "headers": {"Content-Type": "application/json"},
           "body": '{"user_id": 5, "amount": 10}'}
    cand = next(c for c in ip.extract_candidates(req) if c.name == "user_id")
    new_req = sw._apply_mutation(req, cand, 99)
    body = new_req["body"]
    if isinstance(body, str):
        body = json.loads(body)
    assert body["user_id"] == 99
    assert body["amount"] == 10


def test_apply_mutation_body_form():
    import id_patterns as ip
    req = {"method": "POST", "url": "https://x.com/cmd",
           "headers": {"Content-Type": "application/x-www-form-urlencoded"},
           "body": "user_id=42&amount=10"}
    cand = next(c for c in ip.extract_candidates(req) if c.name == "user_id")
    new_req = sw._apply_mutation(req, cand, 99)
    assert "user_id=99" in new_req["body"]
    assert "amount=10" in new_req["body"]


# ---------------------------------------------------------------------------
# build_variants — unit
# ---------------------------------------------------------------------------

def test_build_variants_includes_baseline_no_auth_and_mutations():
    req = {
        "id": "req-1",
        "method": "GET",
        "url": "https://x.com/v1/users/42/orders?status=open",
        "headers": {"Cookie": "session=abc"},
        "body": None,
    }
    variants = sw.build_variants(req, identities={"userB": {"Cookie": "session=def"}})
    names = [v["variant"] for v in variants]
    assert "baseline" in names
    assert "no_auth" in names
    assert "swap_auth:userB" in names
    assert any(n.startswith("mutate:path:users:int_delta_+1") for n in names)


def test_build_variants_drops_auth_for_no_auth_only():
    req = {"id": "r", "method": "GET",
           "url": "https://x.com/v1/users/42",
           "headers": {"Cookie": "x", "Authorization": "Bearer t"},
           "body": None}
    variants = sw.build_variants(req, identities={})
    no_auth = next(v for v in variants if v["variant"] == "no_auth")
    assert "Cookie" not in no_auth["request"]["headers"]
    assert "Authorization" not in no_auth["request"]["headers"]
    baseline = next(v for v in variants if v["variant"] == "baseline")
    assert baseline["request"]["headers"]["Cookie"] == "x"


def test_build_variants_peer_values_used():
    req = {"id": "r", "method": "GET",
           "url": "https://x.com/orders?order_id=99",
           "headers": {"Cookie": "x"}, "body": None}
    variants = sw.build_variants(req, peer_values=[12345])
    peer_variants = [v for v in variants
                     if "peer_value" in v.get("variant", "")]
    assert peer_variants


def test_build_variants_max_mutations_per_id():
    req = {"id": "r", "method": "GET",
           "url": "https://x.com/orders?order_id=99",
           "headers": {}, "body": None}
    v_low = sw.build_variants(req, max_mutations_per_id=2)
    v_high = sw.build_variants(req, max_mutations_per_id=100)
    mutate_low = [v for v in v_low if v["variant"].startswith("mutate:")]
    mutate_high = [v for v in v_high if v["variant"].startswith("mutate:")]
    assert len(mutate_low) < len(mutate_high)


# ---------------------------------------------------------------------------
# plan + consume — integration on a tmp target
# ---------------------------------------------------------------------------

def test_plan_then_consume_end_to_end():
    tmp = Path(tempfile.mkdtemp(prefix="idor_sweep_test_"))
    orig = _patch_targets_root(tmp)
    try:
        target = _mk_target(tmp, "demo")

        # Write a captured-requests JSONL with one request.
        req = {
            "id": "req-1",
            "method": "GET",
            "url": "https://x.com/v1/orders?order_id=99",
            "headers": {"Cookie": "session=A"},
            "body": None,
        }
        req_path = tmp / "requests.jsonl"
        req_path.write_text(json.dumps(req) + "\n")

        # Plan.
        ns = type("NS", (), {})()
        ns.target = "demo"
        ns.requests = str(req_path)
        ns.identities = None
        ns.peer_ids = None
        ns.max_mutations = 4
        assert sw.plan(ns) == 0
        plan_path = target / "caido" / "idor" / "plan.jsonl"
        assert plan_path.exists()
        plan_rows = [json.loads(l) for l in plan_path.read_text().splitlines() if l]
        assert any(r["variant"] == "baseline" for r in plan_rows)
        assert any(r["variant"] == "no_auth" for r in plan_rows)

        # Fake Caido execution: baseline + no_auth + one mutation all
        # return the same 200 body → bac + idor candidates.
        results = []
        for r in plan_rows:
            results.append({
                "request_id": r["request_id"],
                "variant": r["variant"],
                "status": 200,
                "body": '{"orders":[{"id":99,"user":"alice","email":"a@b.com"}]}',
            })
        res_path = target / "caido" / "idor" / "results.jsonl"
        res_path.parent.mkdir(parents=True, exist_ok=True)
        res_path.write_text("\n".join(json.dumps(r) for r in results) + "\n")

        # Consume.
        ns2 = type("NS", (), {})()
        ns2.target = "demo"
        ns2.plan = None
        ns2.results = None
        assert sw.consume(ns2) == 0
        cand_path = target / "caido" / "idor" / "candidates.jsonl"
        md_path = target / "findings" / "idor-candidates.md"
        assert cand_path.exists()
        assert md_path.exists()
        cands = [json.loads(l) for l in cand_path.read_text().splitlines() if l]
        categories = {c["category"] for c in cands}
        # no_auth returned baseline → bac_candidate must be present.
        assert "bac_candidate" in categories

        # Markdown is non-empty + mentions both target + category.
        md = md_path.read_text()
        assert "IDOR" in md
        assert "demo" in md
    finally:
        _restore_targets_root(orig)
        shutil.rmtree(tmp, ignore_errors=True)


def test_consume_skips_when_no_baseline():
    tmp = Path(tempfile.mkdtemp(prefix="idor_sweep_no_base_"))
    orig = _patch_targets_root(tmp)
    try:
        target = _mk_target(tmp, "demo")
        plan_path = target / "caido" / "idor" / "plan.jsonl"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(json.dumps({
            "request_id": "r1", "variant": "no_auth",
            "auth_dropped": True, "request": {"url": "https://x/", "method": "GET"},
        }) + "\n")
        res_path = target / "caido" / "idor" / "results.jsonl"
        res_path.write_text(json.dumps({
            "request_id": "r1", "variant": "no_auth",
            "status": 200, "body": "{}"
        }) + "\n")
        ns = type("NS", (), {})()
        ns.target = "demo"
        ns.plan = None
        ns.results = None
        assert sw.consume(ns) == 0
        # No baseline → no candidates emitted.
        cand_path = target / "caido" / "idor" / "candidates.jsonl"
        assert cand_path.read_text() == ""
    finally:
        _restore_targets_root(orig)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in list(globals().items()) if k.startswith("test_")]
    fails = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as e:
            fails += 1
            print(f"FAIL {fn.__name__}: {e}")
            traceback.print_exc()
    if fails:
        sys.exit(1)
    print(f"\nAll {len(fns)} tests passed.")
