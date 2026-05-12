import json
from pathlib import Path
import pytest
from recon_mcp.artifacts import summarize


@pytest.fixture
def fake_out(tmp_path):
    base = tmp_path / "out"
    (base / "scan").mkdir(parents=True)
    (base / "subs").mkdir(parents=True)
    (base / "resolve").mkdir(parents=True)
    (base / "httpx").mkdir(parents=True)
    (base / "ferox").mkdir(parents=True)

    (base / "scan" / "hosts.txt").write_text("1.2.3.4\n5.6.7.8\n")
    (base / "scan" / "masscan_top10k.json").write_text(json.dumps([
        {"ip": "1.2.3.4", "ports": [{"port": 22, "proto": "tcp"}, {"port": 443, "proto": "tcp"}]},
        {"ip": "5.6.7.8", "ports": [{"port": 80, "proto": "tcp"}]},
    ]))
    (base / "scan" / "ptr.json").write_text(
        '{"ip": "1.2.3.4", "dig_ptr": "host.example.com", "nslookup_ptr": ""}\n'
    )

    (base / "subs" / "all.txt").write_text("a.example.com\nb.example.com\n")

    (base / "resolve" / "new_ips.txt").write_text("9.9.9.9\n")

    (base / "httpx" / "httpx.json").write_text(
        '{"url": "https://a.example.com", "status_code": 200, "title": "Home", "tech": ["nginx"]}\n'
        '{"url": "https://b.example.com", "status_code": 403, "title": "Forbidden"}\n'
    )

    (base / "ferox" / "https___a.example.com.json").write_text(
        '{"type": "response", "url": "https://a.example.com/admin", "status": 401, "content_length": 12}\n'
        '{"type": "response", "url": "https://a.example.com/login", "status": 200, "content_length": 1200}\n'
    )
    return tmp_path


def test_summarize_hosts_and_ports(fake_out):
    s = summarize(fake_out)
    by_ip = {h["ip"]: h for h in s["hosts"]}
    assert set(by_ip["1.2.3.4"]["ports"]) == {22, 443}
    assert by_ip["1.2.3.4"]["ptr"] == "host.example.com"


def test_summarize_new_ips(fake_out):
    s = summarize(fake_out)
    assert "9.9.9.9" in s["new_ips_from_resolve"]


def test_summarize_subdomains(fake_out):
    s = summarize(fake_out)
    assert set(s["subdomains"]) == {"a.example.com", "b.example.com"}


def test_summarize_httpx(fake_out):
    s = summarize(fake_out)
    urls = {e["url"]: e for e in s["http_endpoints"]}
    assert urls["https://a.example.com"]["status_code"] == 200
    assert urls["https://a.example.com"]["title"] == "Home"


def test_summarize_ferox(fake_out):
    s = summarize(fake_out)
    paths = {(f["url"], f["status"]) for f in s["ferox_findings"]}
    assert ("https://a.example.com/admin", 401) in paths
    assert ("https://a.example.com/login", 200) in paths


def test_summarize_missing_dirs_ok(tmp_path):
    (tmp_path / "out").mkdir()
    s = summarize(tmp_path)
    assert s["hosts"] == []
    assert s["subdomains"] == []
