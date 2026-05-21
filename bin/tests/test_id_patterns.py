"""Tests for bin/id_patterns.py.

Covers name scoring, value-shape classification, candidate extraction
across all four locations (path / query / header / json+form body),
and mutation generation per shape.
"""
from __future__ import annotations

import sys
from pathlib import Path

BIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN))

import id_patterns as ip  # noqa: E402


# --- score_name -------------------------------------------------------------

def test_score_name_strong():
    assert ip.score_name("user_id") >= 0.9
    assert ip.score_name("userId") >= 0.9
    assert ip.score_name("account_id") >= 0.9
    assert ip.score_name("X-User-Id") >= 0.6


def test_score_name_medium():
    assert 0.5 <= ip.score_name("orderRef") <= 0.9
    assert 0.5 <= ip.score_name("docHandle") <= 0.9


def test_score_name_weak():
    assert ip.score_name("email") == 0.4
    assert ip.score_name("username") == 0.4


def test_score_name_blocklist():
    for n in ("page", "limit", "offset", "sort", "q", "lang", "cursor"):
        assert ip.score_name(n) == 0.0, n


def test_score_name_empty():
    assert ip.score_name("") == 0.0


# --- classify_value ---------------------------------------------------------

def test_classify_int():
    s = ip.classify_value(42)
    assert s.name == "int" and s.confidence >= 0.9
    s2 = ip.classify_value("123456")
    assert s2.name == "int" and s2.extra["int_value"] == 123456


def test_classify_uuid():
    s = ip.classify_value("550e8400-e29b-41d4-a716-446655440000")
    assert s.name == "uuid" and s.confidence >= 0.95


def test_classify_objectid():
    s = ip.classify_value("507f1f77bcf86cd799439011")
    assert s.name == "objectid"


def test_classify_email():
    s = ip.classify_value("foo@example.com")
    assert s.name == "email"


def test_classify_jwt():
    jwt = "eyJhbGciOi.eyJzdWIiOi.SflKxwRJSM"
    s = ip.classify_value(jwt)
    assert s.name == "jwt"


def test_classify_ulid():
    s = ip.classify_value("01ARZ3NDEKTSV4RRFFQ69G5FAV")
    assert s.name == "ulid"


def test_classify_unknown():
    assert ip.classify_value(None).name == "unknown"
    assert ip.classify_value("").name == "unknown"
    assert ip.classify_value(True).name == "unknown"


# --- extract_candidates -----------------------------------------------------

def test_extract_path_segment():
    req = {"method": "GET",
           "url": "https://api.x.com/v1/users/42/orders",
           "headers": {}, "body": None}
    cands = ip.extract_candidates(req)
    assert any(c.location == "path" and c.shape.name == "int" and c.value == "42"
               for c in cands)


def test_extract_query_param():
    req = {"method": "GET",
           "url": "https://api.x.com/orders?order_id=99&page=2",
           "headers": {}, "body": None}
    cands = ip.extract_candidates(req)
    # page should be filtered, order_id should not.
    names = {c.name for c in cands if c.location == "query"}
    assert "order_id" in names
    assert "page" not in names


def test_extract_header_id():
    req = {"method": "GET", "url": "https://api.x.com/me",
           "headers": {"X-User-Id": "42", "Accept": "application/json"},
           "body": None}
    cands = ip.extract_candidates(req)
    assert any(c.location == "header" and c.name == "X-User-Id" for c in cands)


def test_extract_json_body():
    req = {"method": "POST", "url": "https://api.x.com/transfer",
           "headers": {"Content-Type": "application/json"},
           "body": '{"account_id": 7, "amount": 100, "note": "x"}'}
    cands = ip.extract_candidates(req)
    names = {c.name for c in cands if c.location == "body.json"}
    assert "account_id" in names
    assert "amount" not in names  # not an id-shaped name


def test_extract_form_body():
    req = {"method": "POST", "url": "https://api.x.com/transfer",
           "headers": {"Content-Type": "application/x-www-form-urlencoded"},
           "body": "user_id=42&amount=100"}
    cands = ip.extract_candidates(req)
    assert any(c.location == "body.form" and c.name == "user_id" for c in cands)


def test_extract_nested_json_body():
    req = {"method": "POST", "url": "https://api.x.com/cmd",
           "headers": {"Content-Type": "application/json"},
           "body": '{"target": {"user_id": "550e8400-e29b-41d4-a716-446655440000"}}'}
    cands = ip.extract_candidates(req)
    targets = [c for c in cands if c.location == "body.json"]
    assert any(c.name == "user_id" and c.shape.name == "uuid" for c in targets)


def test_candidates_sorted_by_score():
    req = {"method": "GET",
           "url": "https://x.com/orders?order_id=99&email=foo@b.com",
           "headers": {}, "body": None}
    cands = ip.extract_candidates(req)
    scores = [c.score for c in cands]
    assert scores == sorted(scores, reverse=True)


def test_empty_request_no_candidates():
    req = {"method": "GET", "url": "https://x.com/", "headers": {}, "body": None}
    assert ip.extract_candidates(req) == []


# --- enumerate_mutations ----------------------------------------------------

def test_int_mutations_include_delta_one():
    cand = ip.IdCandidate(
        location="query", name="user_id", value="42",
        shape=ip.IdShape("int", 0.95, {"int_value": 42}),
        name_score=0.9, pointer="$.query.user_id",
    )
    muts = ip.enumerate_mutations(cand)
    by_name = {m.name: m.value for m in muts}
    assert by_name.get("int_delta_+1") == 43
    assert by_name.get("int_delta_-1") == 41
    assert by_name.get("int_zero") == 0
    assert by_name.get("int_negative_one") == -1


def test_uuid_mutations_include_nil():
    cand = ip.IdCandidate(
        location="path", name="users", value="550e8400-e29b-41d4-a716-446655440000",
        shape=ip.IdShape("uuid", 0.99),
        name_score=0.7, pointer="$.path[3]",
    )
    muts = ip.enumerate_mutations(cand)
    names = {m.name for m in muts}
    assert "uuid_nil" in names
    assert "uuid_bitflip_last" in names


def test_objectid_increment():
    cand = ip.IdCandidate(
        location="path", name="docs", value="507f1f77bcf86cd799439011",
        shape=ip.IdShape("objectid", 0.9),
        name_score=0.6, pointer="$.path[2]",
    )
    muts = ip.enumerate_mutations(cand)
    bumped = next(m for m in muts if m.name == "objectid_increment")
    assert bumped.value == "507f1f77bcf86cd799439012"


def test_email_mutations():
    cand = ip.IdCandidate(
        location="query", name="email", value="bob@example.com",
        shape=ip.IdShape("email", 0.95),
        name_score=0.4, pointer="$.query.email",
    )
    muts = ip.enumerate_mutations(cand)
    names = {m.name for m in muts}
    assert "email_admin" in names
    by_name = {m.name: m.value for m in muts}
    assert by_name["email_admin"] == "admin@example.com"
    assert by_name["email_plus_tag"] == "bob+idor@example.com"


def test_mutations_include_peer_values():
    cand = ip.IdCandidate(
        location="query", name="user_id", value="42",
        shape=ip.IdShape("int", 0.95, {"int_value": 42}),
        name_score=0.9, pointer="$.query.user_id",
    )
    muts = ip.enumerate_mutations(cand, peer_values=[999, 1000])
    peer_names = [m.name for m in muts if m.name.startswith("peer_value:")]
    assert len(peer_names) == 2


def test_mutations_universal_always_present():
    cand = ip.IdCandidate(
        location="query", name="user_id", value="42",
        shape=ip.IdShape("int", 0.95, {"int_value": 42}),
        name_score=0.9, pointer="$.query.user_id",
    )
    muts = ip.enumerate_mutations(cand)
    names = {m.name for m in muts}
    assert {"empty", "null_literal", "array_wrap", "wildcard"}.issubset(names)


def test_shift_last_char_helpers():
    assert ip._shift_last_char("abc") == "abd"
    assert ip._shift_last_char("abz") == "aba"
    assert ip._shift_last_char("ab9") == "ab0"
    assert ip._shift_last_char("") == ""


def test_shift_hex_helper():
    assert ip._shift_hex("0a", 1) == "0b"
    assert ip._shift_hex("ff", 1) == "00"  # wrap


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
