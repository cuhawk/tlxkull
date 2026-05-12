"""Render the cloud-init user-data that bootstraps a recon droplet."""
from __future__ import annotations

from pathlib import Path

_BOOTSTRAP = Path(__file__).parent / "runner_scripts" / "bootstrap.sh"


def render_user_data(
    *,
    authorized_key: str,
    job_id: str,
    host_private_key: str | None = None,
    host_public_key: str | None = None,
) -> str:
    """Render cloud-config user-data.

    When `host_private_key`/`host_public_key` are supplied, cloud-init installs them
    as the droplet's SSH host key. The caller then knows the host fingerprint in
    advance, so the very first SSH connect can verify it (no TOFU window).
    """
    bootstrap = _BOOTSTRAP.read_text()
    ssh_keys_block = ""
    if host_private_key and host_public_key:
        ssh_keys_block = (
            "ssh_keys:\n"
            "  ed25519_private: |\n"
            f"{_indent(host_private_key.strip(), 4)}\n"
            f"  ed25519_public: {host_public_key.strip()}\n"
        )
    return f"""#cloud-config
# recon-mcp job: {job_id}
{ssh_keys_block}ssh_authorized_keys:
  - {authorized_key}
write_files:
  - path: /opt/recon/bootstrap.sh
    permissions: '0755'
    content: |
{_indent(bootstrap, 6)}
  - path: /etc/recon/job_id
    content: {job_id}
runcmd:
  - [ bash, -lc, "/opt/recon/bootstrap.sh 2>&1 | tee /var/log/recon-bootstrap.log" ]
"""


def _indent(s: str, n: int) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in s.splitlines())
