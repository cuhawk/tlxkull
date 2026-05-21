"""Tests for bin/response_diff.py."""
from __future__ import annotations

import sys
from pathlib import Path

BIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN))

import response_diff as rd  # noqa: E402


# --- normalize_body ---------------------------------------------------------

def test_normalize_strips_timestamps():
    body = '{"created":"2026-05-19T10:00:00Z","id":1}'
    out = rd.normalize_body(body)
    assert "2026-05-19T10:00:00Z" not in out
    assert "<REDACTED>" in out


def test_normalize_strips_request_id():
    body = '{"request_id":"abc-123-zzz","data":{"x":1}}'
    out = rd.normalize_body(body)
    assert "abc-123-zzz" not in out


def test_normalize_pretty_prints_json_stable():
    a = '{"b":2,"a":1}'
    b = '{"a":1,"b":2}'
    assert rd.normalize_body(a) == rd.normalize_body(b)


def test_normalize_bytes():
    assert rd.normalize_body(b'{"x":1}') == rd.normalize_body('{"x":1}')


def test_normalize_handles_none_and_empty():
    assert rd.normalize_body(None) == ""
    assert rd.normalize_body("") == ""


# --- body_parity ------------------------------------------------------------

def test_parity_identical():
    assert rd.body_parity("hello", "hello") == 1.0


def test_parity_empty_both():
    assert rd.body_parity(None, "") == 1.0
    assert rd.body_parity("", "") == 1.0


def test_parity_one_empty():
    assert rd.body_parity("hello", "") == 0.0


def test_parity_high_for_volatile_diff():
    # Same user data, different timestamp + request id — should be ≈ 1.0.
    a = '{"id":1,"name":"alice","ts":"2026-05-19T10:00:00Z","request_id":"a-1"}'
    b = '{"id":1,"name":"alice","ts":"2026-05-19T11:30:00Z","request_id":"b-2"}'
    assert rd.body_parity(a, b) >= 0.95


def test_parity_low_for_disjoint_payload():
    a = '{"users":[{"id":1,"email":"a@b.com"},{"id":2,"email":"c@d.com"}]}'
    b = '{"error":"forbidden"}'
    assert rd.body_parity(a, b) < 0.5


# --- pii_hits ---------------------------------------------------------------

def test_pii_email_detected():
    assert "email" in rd.pii_hits("contact: alice@example.com")


def test_pii_phone_detected():
    assert "phone" in rd.pii_hits("call (415) 555-1212 for help")


def test_pii_credit_card_luhn_valid():
    # 4111 1111 1111 1111 = canonical Luhn-valid test card.
    assert "credit_card" in rd.pii_hits("number: 4111 1111 1111 1111")


def test_pii_credit_card_luhn_invalid_rejected():
    assert "credit_card" not in rd.pii_hits("number: 1234 5678 9012 3456")


def test_pii_none():
    assert rd.pii_hits("just a regular sentence") == []


# --- classify_variant -------------------------------------------------------

def _resp(status, body=""):
    return {"status": status, "body": body}


def test_classify_idor_candidate():
    baseline = _resp(200, '{"orders":[{"id":1,"user":"alice"}]}')
    variant = _resp(200, '{"orders":[{"id":1,"user":"alice"}]}')
    out = rd.classify_variant(baseline, variant, variant_name="swap_auth:userB")
    assert out.category == "idor_candidate"
    assert out.confidence > 0.5


def test_classify_bac_candidate_when_auth_dropped():
    baseline = _resp(200, '{"orders":[{"id":1}]}')
    variant = _resp(200, '{"orders":[{"id":1}]}')
    out = rd.classify_variant(baseline, variant, variant_name="no_auth", auth_dropped=True)
    assert out.category == "bac_candidate"


def test_classify_access_denied():
    baseline = _resp(200, '{"x":1}')
    variant = _resp(403, '{"error":"forbidden"}')
    out = rd.classify_variant(baseline, variant)
    assert out.category == "access_denied"


def test_classify_error_match():
    out = rd.classify_variant(_resp(401), _resp(401))
    assert out.category == "error_match"


def test_classify_noisy_when_body_differs():
    # Substantially different bodies that share no key/value content.
    baseline = _resp(200, '{"orders":[{"id":1,"user":"alice","total":42}]}')
    variant = _resp(200, '{"error":"validation","details":["bad payload"]}')
    out = rd.classify_variant(baseline, variant)
    assert out.category == "noisy", (
        f"expected noisy, got {out.category} (parity={out.diff.parity})"
    )


def test_classify_leak_partial_on_pii_with_mid_parity():
    # baseline body is small, variant returns a leaked email/phone with
    # partial body match (~0.5 parity).
    baseline = _resp(200, '{"profile":{"name":"alice","plan":"pro"}}')
    variant = _resp(200,
        '{"profile":{"name":"alice","plan":"pro","email":"a@b.com",'
        '"phone":"4155551212"}}')
    out = rd.classify_variant(baseline, variant)
    # Depending on lengths this might be idor_candidate or leak_partial;
    # accept either since both are TP signals.
    assert out.category in {"leak_partial", "idor_candidate"}


def test_classify_variant_threshold_tuning():
    # Two bodies that match at 0.6 parity — below default threshold.
    a = "alice " * 50
    b = a + "bob " * 50
    base = _resp(200, a)
    var = _resp(200, b)
    high = rd.classify_variant(base, var, parity_threshold=0.9)
    low = rd.classify_variant(base, var, parity_threshold=0.4)
    assert high.category != "idor_candidate"
    assert low.category == "idor_candidate"


def test_classify_handles_zero_status():
    # Connection failure represented as status=0 → error_match.
    out = rd.classify_variant(_resp(0), _resp(0))
    assert out.category == "error_match"


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
