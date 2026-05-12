from recon_mcp.cloud_init import render_user_data


def test_renders_required_tools():
    out = render_user_data(authorized_key="ssh-ed25519 AAA== test", job_id="abc")
    assert "#cloud-config" in out
    for tool in ("masscan", "dnsutils", "amass", "subfinder", "httpx", "feroxbuster", "shodan"):
        assert tool in out
    assert "ssh-ed25519 AAA== test" in out


def test_includes_seclists_clone():
    out = render_user_data(authorized_key="k", job_id="abc")
    assert "danielmiessler/SecLists" in out
    assert "raft-large-directories.txt" in out


def test_writes_done_sentinel():
    out = render_user_data(authorized_key="k", job_id="abc")
    assert "/var/lib/recon/bootstrap.done" in out


def test_embeds_job_id():
    out = render_user_data(authorized_key="k", job_id="job-12345")
    assert "job-12345" in out
