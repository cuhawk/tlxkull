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


def test_opus_endpoint_returns_markdown(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)]).opus(1, "# verdict: FP\nreason: setTimeout callback fn")
    r = client.get("/api/target/t1/opus/1")
    assert r.status_code == 200
    assert r.json() == {"chain_id": 1, "markdown": "# verdict: FP\nreason: setTimeout callback fn"}


def test_opus_endpoint_404_when_missing(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)])
    r = client.get("/api/target/t1/opus/1")
    assert r.status_code == 404


def test_snippet_returns_source_slice(client, target_factory):
    src = "\n".join(f"line{i}" for i in range(1, 21))
    target_factory("t1").chains(all_=[_chain(1)]).index(
        nodes=[{"qname": "a.js::foo", "file": "a.js", "line": 8, "end_line": 12,
                "kind": "function", "parent": None, "name": "foo"}]
    ).source("a.js", src)
    r = client.get("/api/target/t1/snippet", params={"qname": "a.js::foo"})
    assert r.status_code == 200
    body = r.json()
    assert body["qname"] == "a.js::foo"
    assert body["file"] == "a.js"
    assert body["line"] == 8
    assert body["end_line"] == 12
    # ±3 lines of context => lines 5..15 inclusive
    assert body["start"] == 5
    assert body["end"] == 15
    assert body["source"].splitlines() == [f"line{i}" for i in range(5, 16)]


def test_snippet_404_when_qname_not_indexed(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)]).index(nodes=[])
    r = client.get("/api/target/t1/snippet", params={"qname": "a.js::missing"})
    assert r.status_code == 404
    assert "qname not indexed" in r.json()["detail"]


def test_snippet_404_when_source_file_missing(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)]).index(
        nodes=[{"qname": "a.js::foo", "file": "a.js", "line": 1, "end_line": 2,
                "kind": "function", "parent": None, "name": "foo"}]
    )  # no .source() call
    r = client.get("/api/target/t1/snippet", params={"qname": "a.js::foo"})
    assert r.status_code == 404
    assert "source file missing" in r.json()["detail"]


def test_post_verdict_appends_and_get_returns_latest(client, target_factory, targets_root):
    target_factory("t1").chains(all_=[_chain(1)])
    r1 = client.post("/api/target/t1/verdict/1", json={"verdict": "fp", "note": "first"})
    assert r1.status_code == 200
    r2 = client.post("/api/target/t1/verdict/1", json={"verdict": "tp", "note": "second"})
    assert r2.status_code == 200
    r3 = client.get("/api/target/t1/verdicts")
    assert r3.status_code == 200
    body = r3.json()
    assert body["verdicts"]["1"]["verdict"] == "tp"
    assert body["verdicts"]["1"]["note"] == "second"
    # And the underlying file is append-only (two lines)
    lines = (targets_root / "t1" / "verdicts.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2


def test_post_verdict_rejects_unknown_verdict_value(client, target_factory):
    target_factory("t1").chains(all_=[_chain(1)])
    r = client.post("/api/target/t1/verdict/1", json={"verdict": "maybe", "note": ""})
    assert r.status_code == 422


def test_root_serves_spa_index_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<div id=root>" in r.text


def test_unknown_non_api_route_falls_through_to_index_html(client):
    r = client.get("/some/spa/route")
    assert r.status_code == 200
    assert "<div id=root>" in r.text
