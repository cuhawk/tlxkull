import shutil
import subprocess
from pathlib import Path
import pytest

SCRIPT_DIR = Path(__file__).parent.parent / "runner_scripts"
PHASES = ["phase_scan.sh", "phase_subdomains.sh", "phase_resolve.sh", "phase_httpx.sh", "phase_ferox.sh"]


@pytest.mark.parametrize("name", PHASES)
def test_script_exists_and_executable(name):
    p = SCRIPT_DIR / name
    assert p.exists(), f"missing: {p}"
    assert p.stat().st_mode & 0o111, f"not executable: {p}"


@pytest.mark.parametrize("name", PHASES)
def test_bash_syntax_check(name):
    p = SCRIPT_DIR / name
    r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("name", PHASES)
def test_uses_strict_mode(name):
    text = (SCRIPT_DIR / name).read_text()
    assert "set -euo pipefail" in text


@pytest.mark.skipif(shutil.which("shellcheck") is None, reason="shellcheck not installed")
@pytest.mark.parametrize("name", PHASES)
def test_shellcheck_clean(name):
    p = SCRIPT_DIR / name
    r = subprocess.run(["shellcheck", "-s", "bash", "-S", "warning", str(p)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
