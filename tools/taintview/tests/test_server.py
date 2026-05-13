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
