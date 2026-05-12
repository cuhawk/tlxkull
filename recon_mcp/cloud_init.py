"""Render the cloud-init user-data that bootstraps a recon droplet."""
from __future__ import annotations

from pathlib import Path

_BOOTSTRAP = Path(__file__).parent / "runner_scripts" / "bootstrap.sh"


def render_user_data(*, authorized_key: str, job_id: str) -> str:
    bootstrap = _BOOTSTRAP.read_text()
    return f"""#cloud-config
# recon-mcp job: {job_id}
ssh_authorized_keys:
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
