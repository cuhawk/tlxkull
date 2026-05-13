def test_health_returns_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_list_targets_returns_only_targets_with_chains(client, targets_root):
    (targets_root / "alpha" / "chains").mkdir(parents=True)
    (targets_root / "alpha" / "chains" / "all.jsonl").write_text("")
    (targets_root / "beta").mkdir()  # no chains/all.jsonl -- excluded
    (targets_root / "gamma" / "chains").mkdir(parents=True)
    (targets_root / "gamma" / "chains" / "all.jsonl").write_text("")

    r = client.get("/api/targets")
    assert r.status_code == 200
    assert sorted(r.json()["targets"]) == ["alpha", "gamma"]


def _chain(cid: int) -> dict:
    return {
        "id": cid,
        "source": {"qname": f"a.js::src{cid}", "file": "a.js", "line": 1, "taxonomy_id": "url_query"},
        "sink": {"qname": f"b.js::sink{cid}", "file": "b.js", "line": 2, "taxonomy_id": "dom_innerHTML"},
        "depth": 1,
        "path": [f"a.js::src{cid}", f"b.js::sink{cid}"],
        "score": 70.0 + cid,
        "scoring": {},
        "variants": [],
    }


def test_chains_endpoint_returns_hot_and_reach_flags(client, target_factory):
    target_factory("t1").chains(
        all_=[_chain(1), _chain(2), _chain(3)],
        hot=[_chain(1), _chain(2)],
        reachable=[_chain(1)],
        unreachable=[_chain(2)],
    )
    r = client.get("/api/target/t1/chains")
    assert r.status_code == 200
    body = r.json()
    by_id = {c["id"]: c for c in body["chains"]}
    assert by_id[1]["is_hot"] is True
    assert by_id[1]["reach"] == "reachable"
    assert by_id[2]["is_hot"] is True
    assert by_id[2]["reach"] == "unreachable"
    assert by_id[3]["is_hot"] is False
    assert by_id[3]["reach"] == "unknown"


def test_chains_endpoint_404_for_missing_target(client):
    r = client.get("/api/target/nope/chains")
    assert r.status_code == 404
