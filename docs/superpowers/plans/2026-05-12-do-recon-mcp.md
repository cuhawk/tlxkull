# DigitalOcean Recon MCP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a new stdio MCP server (`recon`) that, given IP lists / CIDRs / wildcard domains, provisions one or more ephemeral DigitalOcean droplets, runs a structured recon pipeline (DNS + reverse DNS + masscan + subdomain enumeration + reverse-IP + httpx + feroxbuster), collects artifacts back, and destroys every droplet — with optional multi-region probing and parallel execution across targets.

**Architecture:**
- A new MCP package `recon_mcp/` (sibling of `tlx/`), wired through `bin/recon-mcp.sh` and registered in `.claude/settings.json`.
- Job-oriented: each `recon_start` call creates a job in a local SQLite store; the MCP returns immediately and the orchestrator (asyncio) provisions droplets in parallel via the DigitalOcean v2 API. Each droplet self-bootstraps via a cloud-init script that installs the toolchain and clones a `recon_runner` repo of phase scripts.
- The host orchestrator polls droplet status, SSHes in to drive phase scripts, streams stdout into `targets/<name>/recon/<job_id>/logs/`, rsyncs artifacts back, and tears down droplets in a `finally` block. A separate watchdog enforces a hard max-runtime and an orphan-cleanup pass on every server start.
- Phases run as a DAG per target: input-classify → (IP/CIDR: masscan + PTR/Shodan/dig + hackertarget reverse-IP) ∥ (always: amass + subfinder + c99.nl) → merge → re-resolve → httpx → feroxbuster. Multi-region applies only to httpx/feroxbuster; scan-heavy phases run on a single cheapest-region droplet.
- Inputs and outputs are JSON-Schema typed; results land under `targets/<name>/recon/<job_id>/results.json` plus raw tool outputs.

**Tech Stack:**
- Python 3.11+, `mcp` (stdio server), `httpx` (async HTTP for DO API + c99 + hackertarget), `asyncssh` (parallel SSH/SFTP, more reliable than shelling out), `pydantic` v2 (typed tool I/O + job state), `aiosqlite` (job store), `structlog` (logging), `pytest` + `pytest-asyncio` + `respx` (mocks for httpx).
- On-droplet toolchain (installed by cloud-init): `masscan`, `dnsutils` (dig/nslookup), `nmap` (for service banner on hot ports), `amass`, `subfinder`, `httpx` (projectdiscovery), `feroxbuster`, `shodan` CLI (pip), `jq`, `git`, `python3`. SecLists cloned into `/opt/SecLists` for the `raft-large-directories.txt` wordlist.

---

## File Structure

Each file has one clear responsibility. Small focused modules so a single subagent can hold one file in context while editing.

```
recon_mcp/
├── __init__.py
├── server.py              # MCP stdio entry; registers tools; bootstrap
├── tools.py               # Tool I/O Pydantic models + handler dispatch
├── handlers/
│   ├── __init__.py
│   ├── start.py           # recon_start handler
│   ├── status.py          # recon_status handler
│   ├── results.py         # recon_results handler
│   ├── cancel.py          # recon_cancel handler
│   ├── list_jobs.py       # recon_list_jobs handler
│   └── cleanup.py         # recon_cleanup_orphans handler
├── input_parser.py        # classify "1.2.3.4", "1.0.0.0/24", "*.foo.com"
├── do_client.py           # DigitalOcean v2 REST wrapper (droplets, ssh keys, tags)
├── droplet.py             # provision/wait_active/destroy/ssh-exec wrappers
├── cloud_init.py          # template-renders the user-data bootstrap script
├── regions.py             # DO regions metadata + slug→country mapping
├── scanner.py             # phase orchestration per target on one droplet
├── jobs.py                # aiosqlite-backed job + droplet state store
├── artifacts.py           # rsync/sftp pull, parse tool outputs to JSON
├── safety.py              # scope checks, CIDR size caps, runtime caps
├── runner_scripts/        # bash scripts copied onto droplets, executed by SSH
│   ├── bootstrap.sh       # idempotent install (cloud-init invokes once)
│   ├── phase_scan.sh      # masscan top10k + rest, dig/nslookup/shodan PTR
│   ├── phase_subdomains.sh# amass + subfinder + c99 + hackertarget
│   ├── phase_resolve.sh   # bulk dns resolve subdomains → IP set
│   ├── phase_httpx.sh     # httpx -title -tech-detect -status-code -tls-grab
│   └── phase_ferox.sh     # feroxbuster raft-large with sane rate limits
├── config.py              # env loading, defaults, budget caps
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # fixtures: tmp sqlite, mocked httpx, fake DO API
│   ├── test_input_parser.py
│   ├── test_cloud_init.py
│   ├── test_do_client.py
│   ├── test_droplet.py
│   ├── test_regions.py
│   ├── test_jobs.py
│   ├── test_scanner.py
│   ├── test_artifacts.py
│   ├── test_safety.py
│   ├── test_handlers_start.py
│   ├── test_handlers_status.py
│   ├── test_handlers_results.py
│   ├── test_handlers_cancel.py
│   ├── test_handlers_cleanup.py
│   └── test_integration.py# end-to-end with fully mocked DO + SSH

bin/
├── recon-mcp.sh           # wrapper: sources .env, execs `python -m recon_mcp`
└── recon-orphan-sweep.sh  # cron-friendly: invokes recon_cleanup_orphans

.claude/
└── settings.json          # add "recon" MCP block + tool permissions
```

---

## Pre-task setup

### Task 0: Repo skeleton, deps, virtualenv

**Files:**
- Create: `recon_mcp/__init__.py`
- Create: `recon_mcp/pyproject.toml`
- Create: `bin/recon-mcp.sh`
- Modify: `.envrc`
- Modify: `.gitignore`

- [ ] **Step 1: Create package skeleton**

Create `recon_mcp/__init__.py`:

```python
"""recon_mcp — stdio MCP server for DigitalOcean ephemeral-droplet recon."""
__version__ = "0.1.0"
```

Create `recon_mcp/pyproject.toml`:

```toml
[project]
name = "recon-mcp"
version = "0.1.0"
description = "Ephemeral-droplet recon MCP for TLX"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.0.0",
    "httpx>=0.27",
    "asyncssh>=2.18",
    "pydantic>=2.7",
    "aiosqlite>=0.20",
    "structlog>=24.1",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "pyfakefs>=5.4",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 2: Create the bin wrapper**

Create `bin/recon-mcp.sh`:

```bash
#!/usr/bin/env bash
# recon MCP entrypoint — mirrors bin/tlx-mcp.sh pattern.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$HOME/.config/claude/.env" ] && set -a && . "$HOME/.config/claude/.env" && set +a
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
cd "$ROOT"
exec uv run --project recon_mcp python -m recon_mcp.server
```

Make executable: `chmod +x bin/recon-mcp.sh`

- [ ] **Step 3: Add required env vars to .envrc**

Append to `.envrc`:

```bash
# recon-mcp
export DO_API_TOKEN="${DO_API_TOKEN:-}"
export SHODAN_API_KEY="${SHODAN_API_KEY:-}"
export C99_API_KEY="${C99_API_KEY:-}"
export RECON_DB_PATH="${RECON_DB_PATH:-$PWD/.recon/jobs.sqlite}"
export RECON_SSH_KEY_DIR="${RECON_SSH_KEY_DIR:-$PWD/.recon/ssh}"
export RECON_MAX_DROPLETS_PER_JOB="${RECON_MAX_DROPLETS_PER_JOB:-10}"
export RECON_MAX_RUNTIME_MIN="${RECON_MAX_RUNTIME_MIN:-180}"
export RECON_DEFAULT_SCAN_REGION="${RECON_DEFAULT_SCAN_REGION:-nyc1}"
export RECON_DROPLET_SIZE="${RECON_DROPLET_SIZE:-s-2vcpu-4gb}"
```

- [ ] **Step 4: Ignore local state**

Append to `.gitignore`:

```
.recon/
recon_mcp/.venv/
```

- [ ] **Step 5: Install deps**

Run: `cd recon_mcp && uv venv && uv sync --extra dev`
Expected: virtualenv created, all packages installed, `uv run pytest --collect-only` shows 0 tests yet.

- [ ] **Step 6: Commit**

```bash
git add recon_mcp/__init__.py recon_mcp/pyproject.toml bin/recon-mcp.sh .envrc .gitignore
git commit -m "recon-mcp: scaffold package, deps, env wrapper"
```

---

## Phase 1: pure-logic modules (no I/O)

### Task 1: Input parser — classify and normalize targets

**Files:**
- Create: `recon_mcp/input_parser.py`
- Test: `recon_mcp/tests/test_input_parser.py`

Goal: turn a freeform list of strings into a typed list of `Target(kind, value)` where kind ∈ {ip, cidr, wildcard}. Reject malformed input loudly — recon on the wrong target is worse than no recon.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_input_parser.py`:

```python
import pytest
from recon_mcp.input_parser import parse_targets, Target, TargetKind, InputError


def test_single_ip():
    assert parse_targets(["1.2.3.4"]) == [Target(kind=TargetKind.IP, value="1.2.3.4")]


def test_cidr_v4():
    assert parse_targets(["10.0.0.0/24"]) == [Target(kind=TargetKind.CIDR, value="10.0.0.0/24")]


def test_wildcard_domain():
    assert parse_targets(["*.example.com"]) == [Target(kind=TargetKind.WILDCARD, value="example.com")]


def test_strips_protocol_and_path():
    assert parse_targets(["https://*.foo.io/login"]) == [Target(kind=TargetKind.WILDCARD, value="foo.io")]


def test_mixed_input():
    result = parse_targets(["1.2.3.4", "10.0.0.0/16", "*.acme.io"])
    assert {t.kind for t in result} == {TargetKind.IP, TargetKind.CIDR, TargetKind.WILDCARD}


def test_rejects_empty_list():
    with pytest.raises(InputError, match="empty"):
        parse_targets([])


def test_rejects_bare_domain_without_wildcard():
    with pytest.raises(InputError, match="wildcard"):
        parse_targets(["example.com"])


def test_rejects_garbage():
    with pytest.raises(InputError):
        parse_targets(["not a target"])


def test_rejects_ipv6_cidr_for_now():
    with pytest.raises(InputError, match="IPv6"):
        parse_targets(["2001:db8::/32"])


def test_dedupes_input():
    result = parse_targets(["1.1.1.1", "1.1.1.1"])
    assert len(result) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_input_parser.py -v`
Expected: ImportError — `recon_mcp.input_parser` does not exist.

- [ ] **Step 3: Implement the parser**

Create `recon_mcp/input_parser.py`:

```python
"""Classify recon targets into IP, CIDR, or wildcard-domain."""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class TargetKind(str, Enum):
    IP = "ip"
    CIDR = "cidr"
    WILDCARD = "wildcard"


@dataclass(frozen=True)
class Target:
    kind: TargetKind
    value: str


class InputError(Exception):
    pass


_DOMAIN_RE = re.compile(r"^(?:\*\.)?(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$", re.IGNORECASE)


def _strip(raw: str) -> str:
    raw = raw.strip()
    if "://" in raw:
        parsed = urlparse(raw)
        raw = parsed.netloc or parsed.path
    raw = raw.split("/", 1)[0] if not _looks_like_cidr(raw) else raw
    return raw.strip().rstrip(".")


def _looks_like_cidr(s: str) -> bool:
    return "/" in s and s.count(".") >= 1 and s.split("/")[-1].isdigit() and len(s.split("/")[-1]) <= 3


def _classify(token: str) -> Target:
    if "/" in token:
        try:
            net = ipaddress.ip_network(token, strict=False)
        except ValueError as e:
            raise InputError(f"bad CIDR: {token!r} ({e})") from e
        if net.version == 6:
            raise InputError(f"IPv6 not supported yet: {token!r}")
        return Target(TargetKind.CIDR, str(net))
    if token.startswith("*."):
        domain = token[2:]
        if not _DOMAIN_RE.match(domain):
            raise InputError(f"bad wildcard domain: {token!r}")
        return Target(TargetKind.WILDCARD, domain.lower())
    try:
        ip = ipaddress.ip_address(token)
    except ValueError:
        ip = None
    if ip is not None:
        if ip.version == 6:
            raise InputError(f"IPv6 not supported yet: {token!r}")
        return Target(TargetKind.IP, str(ip))
    if _DOMAIN_RE.match(token):
        raise InputError(f"bare domain {token!r} not allowed — pass as wildcard (*.{token})")
    raise InputError(f"unrecognized target: {token!r}")


def parse_targets(raw: list[str]) -> list[Target]:
    if not raw:
        raise InputError("empty target list")
    seen: set[tuple[TargetKind, str]] = set()
    out: list[Target] = []
    for r in raw:
        t = _classify(_strip(r))
        key = (t.kind, t.value)
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_input_parser.py -v`
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/input_parser.py recon_mcp/tests/test_input_parser.py recon_mcp/tests/__init__.py
git commit -m "recon-mcp: input parser for IP/CIDR/wildcard targets"
```

---

### Task 2: Regions registry

**Files:**
- Create: `recon_mcp/regions.py`
- Test: `recon_mcp/tests/test_regions.py`

Goal: map DO region slugs → ISO country code, list "probe-friendly" regions (one per continent), validate user-supplied region lists.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_regions.py`:

```python
import pytest
from recon_mcp.regions import (
    REGIONS, validate_regions, default_probe_set, country_for, RegionError,
)


def test_known_regions_have_country():
    assert country_for("nyc1") == "US"
    assert country_for("fra1") == "DE"
    assert country_for("sgp1") == "SG"


def test_unknown_region_raises():
    with pytest.raises(RegionError, match="unknown"):
        country_for("mars1")


def test_validate_filters_unknown():
    with pytest.raises(RegionError, match="mars1"):
        validate_regions(["nyc1", "mars1"])


def test_validate_dedupes_and_orders():
    assert validate_regions(["nyc1", "nyc1", "fra1"]) == ["nyc1", "fra1"]


def test_default_probe_set_is_diverse():
    s = default_probe_set()
    countries = {country_for(r) for r in s}
    assert len(countries) >= 4
    assert "US" in countries
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_regions.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement regions**

Create `recon_mcp/regions.py`:

```python
"""DigitalOcean region metadata."""
from __future__ import annotations


class RegionError(ValueError):
    pass


REGIONS: dict[str, dict[str, str]] = {
    "nyc1": {"country": "US", "city": "New York"},
    "nyc3": {"country": "US", "city": "New York"},
    "sfo3": {"country": "US", "city": "San Francisco"},
    "tor1": {"country": "CA", "city": "Toronto"},
    "lon1": {"country": "GB", "city": "London"},
    "ams3": {"country": "NL", "city": "Amsterdam"},
    "fra1": {"country": "DE", "city": "Frankfurt"},
    "sgp1": {"country": "SG", "city": "Singapore"},
    "blr1": {"country": "IN", "city": "Bangalore"},
    "syd1": {"country": "AU", "city": "Sydney"},
}


def country_for(slug: str) -> str:
    try:
        return REGIONS[slug]["country"]
    except KeyError as e:
        raise RegionError(f"unknown region: {slug!r}") from e


def validate_regions(slugs: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    bad: list[str] = []
    for s in slugs:
        if s not in REGIONS:
            bad.append(s)
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    if bad:
        raise RegionError(f"unknown region(s): {bad}")
    return out


def default_probe_set() -> list[str]:
    return ["nyc1", "fra1", "sgp1", "syd1"]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_regions.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/regions.py recon_mcp/tests/test_regions.py
git commit -m "recon-mcp: region registry + default probe set"
```

---

### Task 3: Safety guards (CIDR caps, runtime caps, scope check)

**Files:**
- Create: `recon_mcp/safety.py`
- Test: `recon_mcp/tests/test_safety.py`

Goal: refuse jobs that would obviously cost too much or scan too widely. Centralize the rules so they can't be bypassed accidentally.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_safety.py`:

```python
import pytest
from recon_mcp.input_parser import Target, TargetKind
from recon_mcp.safety import (
    check_targets, SafetyError, MAX_CIDR_HOSTS, MAX_TARGETS_PER_JOB,
)


def test_small_cidr_ok():
    check_targets([Target(TargetKind.CIDR, "10.0.0.0/24")])


def test_huge_cidr_rejected():
    with pytest.raises(SafetyError, match="too large"):
        check_targets([Target(TargetKind.CIDR, "10.0.0.0/8")])


def test_too_many_targets_rejected():
    targets = [Target(TargetKind.IP, f"1.1.1.{i}") for i in range(MAX_TARGETS_PER_JOB + 1)]
    with pytest.raises(SafetyError, match="too many"):
        check_targets(targets)


def test_max_cidr_hosts_const_sane():
    # /16 = 65536 hosts. Should be allowed.
    assert MAX_CIDR_HOSTS >= 65536
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_safety.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement safety**

Create `recon_mcp/safety.py`:

```python
"""Pre-flight safety checks for recon jobs."""
from __future__ import annotations

import ipaddress

from .input_parser import Target, TargetKind


class SafetyError(ValueError):
    pass


MAX_CIDR_HOSTS = 1 << 17  # /15 = 131072 hosts; /8 (16M) blocked
MAX_TARGETS_PER_JOB = 100


def check_targets(targets: list[Target]) -> None:
    if len(targets) > MAX_TARGETS_PER_JOB:
        raise SafetyError(f"too many targets ({len(targets)} > {MAX_TARGETS_PER_JOB})")
    for t in targets:
        if t.kind is TargetKind.CIDR:
            n = ipaddress.ip_network(t.value).num_addresses
            if n > MAX_CIDR_HOSTS:
                raise SafetyError(
                    f"CIDR {t.value} too large ({n} > {MAX_CIDR_HOSTS}); split into smaller blocks"
                )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_safety.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/safety.py recon_mcp/tests/test_safety.py
git commit -m "recon-mcp: safety caps for CIDR size and target count"
```

---

### Task 4: Config module — env-driven defaults

**Files:**
- Create: `recon_mcp/config.py`
- Test: `recon_mcp/tests/test_config.py`

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_config.py`:

```python
import os
import pytest
from recon_mcp.config import load_config, ConfigError


def test_loads_defaults_when_env_present(monkeypatch, tmp_path):
    monkeypatch.setenv("DO_API_TOKEN", "do_v1_xxx")
    monkeypatch.setenv("RECON_DB_PATH", str(tmp_path / "jobs.sqlite"))
    monkeypatch.setenv("RECON_SSH_KEY_DIR", str(tmp_path / "ssh"))
    cfg = load_config()
    assert cfg.do_api_token == "do_v1_xxx"
    assert cfg.max_droplets_per_job == 10
    assert cfg.max_runtime_min == 180
    assert cfg.default_scan_region == "nyc1"


def test_rejects_missing_do_token(monkeypatch):
    monkeypatch.delenv("DO_API_TOKEN", raising=False)
    with pytest.raises(ConfigError, match="DO_API_TOKEN"):
        load_config()


def test_overrides_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("DO_API_TOKEN", "x")
    monkeypatch.setenv("RECON_DB_PATH", str(tmp_path / "j.sqlite"))
    monkeypatch.setenv("RECON_SSH_KEY_DIR", str(tmp_path / "ssh"))
    monkeypatch.setenv("RECON_MAX_DROPLETS_PER_JOB", "25")
    monkeypatch.setenv("RECON_DROPLET_SIZE", "s-4vcpu-8gb")
    cfg = load_config()
    assert cfg.max_droplets_per_job == 25
    assert cfg.droplet_size == "s-4vcpu-8gb"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_config.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement config**

Create `recon_mcp/config.py`:

```python
"""Env-driven config for recon-mcp."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    do_api_token: str
    shodan_api_key: str | None
    c99_api_key: str | None
    db_path: Path
    ssh_key_dir: Path
    max_droplets_per_job: int
    max_runtime_min: int
    default_scan_region: str
    droplet_size: str


def load_config() -> Config:
    tok = os.environ.get("DO_API_TOKEN", "").strip()
    if not tok:
        raise ConfigError("DO_API_TOKEN not set")
    return Config(
        do_api_token=tok,
        shodan_api_key=(os.environ.get("SHODAN_API_KEY") or None),
        c99_api_key=(os.environ.get("C99_API_KEY") or None),
        db_path=Path(os.environ.get("RECON_DB_PATH", ".recon/jobs.sqlite")),
        ssh_key_dir=Path(os.environ.get("RECON_SSH_KEY_DIR", ".recon/ssh")),
        max_droplets_per_job=int(os.environ.get("RECON_MAX_DROPLETS_PER_JOB", "10")),
        max_runtime_min=int(os.environ.get("RECON_MAX_RUNTIME_MIN", "180")),
        default_scan_region=os.environ.get("RECON_DEFAULT_SCAN_REGION", "nyc1"),
        droplet_size=os.environ.get("RECON_DROPLET_SIZE", "s-2vcpu-4gb"),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_config.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/config.py recon_mcp/tests/test_config.py
git commit -m "recon-mcp: config loader with env validation"
```

---

## Phase 2: I/O modules with mocks

### Task 5: DigitalOcean API client wrapper

**Files:**
- Create: `recon_mcp/do_client.py`
- Test: `recon_mcp/tests/test_do_client.py`

Goal: minimal async wrapper over the DO v2 REST API for the four endpoints we need: ssh_keys POST/DELETE, droplets POST/GET/DELETE, plus a tag-by-name list query so the orphan sweep can find leaked droplets.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_do_client.py`:

```python
import httpx
import pytest
import respx
from recon_mcp.do_client import DOClient, DOAPIError


@pytest.fixture
def client():
    return DOClient(token="t0k3n")


@respx.mock
@pytest.mark.asyncio
async def test_create_ssh_key(client):
    respx.post("https://api.digitalocean.com/v2/account/keys").mock(
        return_value=httpx.Response(201, json={"ssh_key": {"id": 42, "fingerprint": "ab:cd"}})
    )
    res = await client.create_ssh_key(name="job-abc", public_key="ssh-ed25519 AAA...")
    assert res["id"] == 42


@respx.mock
@pytest.mark.asyncio
async def test_create_droplet_returns_id(client):
    respx.post("https://api.digitalocean.com/v2/droplets").mock(
        return_value=httpx.Response(202, json={"droplet": {"id": 999, "status": "new"}})
    )
    res = await client.create_droplet(
        name="recon-1", region="nyc1", size="s-2vcpu-4gb",
        image="ubuntu-24-04-x64", ssh_key_ids=[42], user_data="#!/bin/bash\necho hi",
        tags=["recon", "job:abc"],
    )
    assert res["id"] == 999


@respx.mock
@pytest.mark.asyncio
async def test_get_droplet(client):
    respx.get("https://api.digitalocean.com/v2/droplets/999").mock(
        return_value=httpx.Response(200, json={"droplet": {
            "id": 999, "status": "active",
            "networks": {"v4": [{"type": "public", "ip_address": "1.2.3.4"}]},
        }})
    )
    res = await client.get_droplet(999)
    assert res["status"] == "active"


@respx.mock
@pytest.mark.asyncio
async def test_destroy_droplet(client):
    respx.delete("https://api.digitalocean.com/v2/droplets/999").mock(
        return_value=httpx.Response(204)
    )
    await client.destroy_droplet(999)


@respx.mock
@pytest.mark.asyncio
async def test_list_by_tag(client):
    respx.get("https://api.digitalocean.com/v2/droplets?tag_name=recon").mock(
        return_value=httpx.Response(200, json={"droplets": [
            {"id": 1, "name": "a"}, {"id": 2, "name": "b"},
        ]})
    )
    res = await client.list_by_tag("recon")
    assert [d["id"] for d in res] == [1, 2]


@respx.mock
@pytest.mark.asyncio
async def test_429_retries_then_raises(client):
    respx.get("https://api.digitalocean.com/v2/droplets/999").mock(
        side_effect=[
            httpx.Response(429, headers={"retry-after": "0"}, json={"id": "too_many", "message": "slow down"}),
            httpx.Response(429, headers={"retry-after": "0"}, json={"id": "too_many", "message": "slow down"}),
            httpx.Response(429, headers={"retry-after": "0"}, json={"id": "too_many", "message": "slow down"}),
        ]
    )
    with pytest.raises(DOAPIError, match="429"):
        await client.get_droplet(999)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_do_client.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement DOClient**

Create `recon_mcp/do_client.py`:

```python
"""Async DigitalOcean v2 REST client — only the slice recon-mcp needs."""
from __future__ import annotations

import asyncio
from typing import Any

import httpx


class DOAPIError(RuntimeError):
    pass


_BASE = "https://api.digitalocean.com/v2"


class DOClient:
    def __init__(self, token: str, timeout: float = 30.0) -> None:
        self._token = token
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    async def _req(self, method: str, path: str, **kw: Any) -> httpx.Response:
        url = f"{_BASE}{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as c:
            for attempt in range(3):
                r = await c.request(method, url, headers=self._headers(), **kw)
                if r.status_code != 429:
                    return r
                if attempt == 2:
                    raise DOAPIError(f"429 after retries: {r.text}")
                delay = float(r.headers.get("retry-after", "1"))
                await asyncio.sleep(max(delay, 0.1))
        raise AssertionError("unreachable")

    async def create_ssh_key(self, name: str, public_key: str) -> dict:
        r = await self._req("POST", "/account/keys", json={"name": name, "public_key": public_key})
        if r.status_code != 201:
            raise DOAPIError(f"ssh_key create failed: {r.status_code} {r.text}")
        return r.json()["ssh_key"]

    async def delete_ssh_key(self, key_id: int) -> None:
        r = await self._req("DELETE", f"/account/keys/{key_id}")
        if r.status_code not in (204, 404):
            raise DOAPIError(f"ssh_key delete failed: {r.status_code} {r.text}")

    async def create_droplet(
        self, *, name: str, region: str, size: str, image: str,
        ssh_key_ids: list[int], user_data: str, tags: list[str],
    ) -> dict:
        body = {
            "name": name, "region": region, "size": size, "image": image,
            "ssh_keys": ssh_key_ids, "user_data": user_data, "tags": tags,
            "ipv6": False, "monitoring": False,
        }
        r = await self._req("POST", "/droplets", json=body)
        if r.status_code != 202:
            raise DOAPIError(f"droplet create failed: {r.status_code} {r.text}")
        return r.json()["droplet"]

    async def get_droplet(self, droplet_id: int) -> dict:
        r = await self._req("GET", f"/droplets/{droplet_id}")
        if r.status_code != 200:
            raise DOAPIError(f"droplet get failed: {r.status_code} {r.text}")
        return r.json()["droplet"]

    async def destroy_droplet(self, droplet_id: int) -> None:
        r = await self._req("DELETE", f"/droplets/{droplet_id}")
        if r.status_code not in (204, 404):
            raise DOAPIError(f"droplet destroy failed: {r.status_code} {r.text}")

    async def list_by_tag(self, tag: str) -> list[dict]:
        r = await self._req("GET", "/droplets", params={"tag_name": tag})
        if r.status_code != 200:
            raise DOAPIError(f"list droplets failed: {r.status_code} {r.text}")
        return r.json().get("droplets", [])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_do_client.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/do_client.py recon_mcp/tests/test_do_client.py
git commit -m "recon-mcp: DigitalOcean API client (droplets + ssh keys)"
```

---

### Task 6: Cloud-init bootstrap template

**Files:**
- Create: `recon_mcp/cloud_init.py`
- Create: `recon_mcp/runner_scripts/bootstrap.sh`
- Test: `recon_mcp/tests/test_cloud_init.py`

Goal: render a `user-data` cloud-init script that installs the full toolchain idempotently and stages the runner scripts. Toolchain failures fail loud (the orchestrator polls for `/var/lib/recon/bootstrap.done`).

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_cloud_init.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_cloud_init.py -v`
Expected: ImportError.

- [ ] **Step 3: Create the bootstrap script**

Create `recon_mcp/runner_scripts/bootstrap.sh`:

```bash
#!/usr/bin/env bash
# Idempotent recon-droplet bootstrap. Invoked once via cloud-init.
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
mkdir -p /var/lib/recon /opt/recon /opt/recon/out

apt-get update -y
apt-get install -y --no-install-recommends \
    masscan nmap dnsutils whois jq curl wget git unzip ca-certificates \
    python3 python3-pip golang-go rsync

# projectdiscovery toolchain (pinned — @latest breaks bootstrap silently when upstream churns)
export GOBIN=/usr/local/bin
SUBFINDER_VER="v2.6.6"
HTTPX_VER="v1.6.10"
go install -v "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@${SUBFINDER_VER}"
go install -v "github.com/projectdiscovery/httpx/cmd/httpx@${HTTPX_VER}"

# amass
AMASS_VER="v4.2.0"
curl -fsSL -o /tmp/amass.zip "https://github.com/owasp-amass/amass/releases/download/${AMASS_VER}/amass_Linux_amd64.zip"
unzip -o /tmp/amass.zip -d /tmp/amass
install -m 0755 /tmp/amass/amass_Linux_amd64/amass /usr/local/bin/amass

# feroxbuster
FEROX_VER="2.11.0"
curl -fsSL -o /tmp/ferox.zip "https://github.com/epi052/feroxbuster/releases/download/v${FEROX_VER}/x86_64-linux-feroxbuster.zip"
unzip -o /tmp/ferox.zip -d /tmp/ferox
install -m 0755 /tmp/ferox/feroxbuster /usr/local/bin/feroxbuster

# shodan
pip3 install --break-system-packages shodan

# SecLists (shallow for speed)
git clone --depth 1 https://github.com/danielmiessler/SecLists.git /opt/SecLists

touch /var/lib/recon/bootstrap.done
```

- [ ] **Step 4: Implement cloud_init renderer**

Create `recon_mcp/cloud_init.py`:

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_cloud_init.py -v`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add recon_mcp/cloud_init.py recon_mcp/runner_scripts/bootstrap.sh recon_mcp/tests/test_cloud_init.py
git commit -m "recon-mcp: cloud-init bootstrap template + toolchain installer"
```

---

### Task 7: Droplet lifecycle (provision → wait → exec → destroy)

**Files:**
- Create: `recon_mcp/droplet.py`
- Test: `recon_mcp/tests/test_droplet.py`

Goal: a `Droplet` async context manager that creates a droplet, polls until `status=active` and bootstrap sentinel exists, exposes `run(cmd)` and `pull(remote, local)` via `asyncssh`, and guarantees destroy in `__aexit__` even on exception. Use ephemeral ed25519 keypair per job (generated and removed alongside).

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_droplet.py`:

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

from recon_mcp.droplet import Droplet, ProvisionError


@pytest.fixture
def fake_do():
    do = MagicMock()
    do.create_droplet = AsyncMock(return_value={"id": 111, "status": "new"})
    do.get_droplet = AsyncMock(side_effect=[
        {"id": 111, "status": "new",   "networks": {"v4": []}},
        {"id": 111, "status": "active","networks": {"v4": [{"type": "public", "ip_address": "9.9.9.9"}]}},
    ])
    do.destroy_droplet = AsyncMock()
    return do


@pytest.mark.asyncio
async def test_provision_waits_for_active(fake_do, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    d = Droplet(do=fake_do, name="t", region="nyc1", size="s-2vcpu-4gb",
                image="ubuntu-24-04-x64", ssh_key_ids=[1], user_data="x", tags=["t"])
    ip = await d._provision_and_wait(poll_interval=0)
    assert ip == "9.9.9.9"
    assert d.droplet_id == 111


@pytest.mark.asyncio
async def test_destroy_called_on_exception(fake_do, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    d = Droplet(do=fake_do, name="t", region="nyc1", size="s",
                image="i", ssh_key_ids=[1], user_data="x", tags=["t"])
    async def boom():
        async with d:
            raise RuntimeError("kaboom")
    with pytest.raises(RuntimeError):
        await boom()
    fake_do.destroy_droplet.assert_awaited_once_with(111)


@pytest.mark.asyncio
async def test_provision_timeout(monkeypatch):
    do = MagicMock()
    do.create_droplet = AsyncMock(return_value={"id": 1, "status": "new"})
    do.get_droplet = AsyncMock(return_value={"id": 1, "status": "new", "networks": {"v4": []}})
    do.destroy_droplet = AsyncMock()
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    d = Droplet(do=do, name="t", region="nyc1", size="s", image="i",
                ssh_key_ids=[1], user_data="x", tags=["t"], max_wait_sec=0.01)
    with pytest.raises(ProvisionError, match="timeout"):
        await d._provision_and_wait(poll_interval=0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_droplet.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement Droplet**

Create `recon_mcp/droplet.py`:

```python
"""Droplet lifecycle: async context manager that provisions, runs SSH, and tears down."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

import asyncssh
import structlog

from .do_client import DOClient

log = structlog.get_logger(__name__)


class ProvisionError(RuntimeError):
    pass


@dataclass
class Droplet:
    do: DOClient
    name: str
    region: str
    size: str
    image: str
    ssh_key_ids: list[int]
    user_data: str
    tags: list[str]
    ssh_private_key_path: str | None = None
    max_wait_sec: float = 300.0
    droplet_id: int | None = field(default=None, init=False)
    ip: str | None = field(default=None, init=False)

    async def _provision_and_wait(self, poll_interval: float = 5.0) -> str:
        created = await self.do.create_droplet(
            name=self.name, region=self.region, size=self.size, image=self.image,
            ssh_key_ids=self.ssh_key_ids, user_data=self.user_data, tags=self.tags,
        )
        self.droplet_id = created["id"]
        start = time.monotonic()
        while time.monotonic() - start < self.max_wait_sec:
            info = await self.do.get_droplet(self.droplet_id)
            if info.get("status") == "active":
                v4 = [n for n in info.get("networks", {}).get("v4", []) if n.get("type") == "public"]
                if v4:
                    self.ip = v4[0]["ip_address"]
                    return self.ip
            await asyncio.sleep(poll_interval)
        raise ProvisionError(f"droplet {self.droplet_id} provisioning timeout")

    async def _wait_bootstrap(self, poll_interval: float = 10.0, max_sec: float = 600.0) -> None:
        start = time.monotonic()
        while time.monotonic() - start < max_sec:
            try:
                rc, _, _ = await self.run("test -f /var/lib/recon/bootstrap.done", check=False)
                if rc == 0:
                    return
            except Exception as e:
                log.debug("bootstrap_poll_err", err=str(e))
            await asyncio.sleep(poll_interval)
        raise ProvisionError(f"droplet {self.droplet_id} bootstrap timeout")

    async def __aenter__(self) -> "Droplet":
        try:
            await self._provision_and_wait()
            await self._wait_bootstrap()
        except Exception:
            if self.droplet_id:
                await self.do.destroy_droplet(self.droplet_id)
            raise
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.droplet_id:
            try:
                await self.do.destroy_droplet(self.droplet_id)
            except Exception as e:
                log.error("destroy_failed", droplet_id=self.droplet_id, err=str(e))

    async def _connect(self) -> asyncssh.SSHClientConnection:
        if not self.ip or not self.ssh_private_key_path:
            raise RuntimeError("Droplet._connect: not provisioned (ip or key path missing)")
        return await asyncssh.connect(
            host=self.ip, username="root", client_keys=[self.ssh_private_key_path],
            known_hosts=None, connect_timeout=20,
        )

    async def run(self, cmd: str, *, check: bool = True, timeout: float = 1800.0) -> tuple[int, str, str]:
        async with await self._connect() as conn:
            r = await asyncio.wait_for(conn.run(cmd, check=False), timeout=timeout)
            if check and r.exit_status != 0:
                raise RuntimeError(f"remote cmd failed ({r.exit_status}): {cmd}\nSTDERR:\n{r.stderr}")
            return r.exit_status, r.stdout or "", r.stderr or ""

    async def pull(self, remote_path: str, local_path: str) -> None:
        async with await self._connect() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.get(remote_path, local_path, recurse=True)

    async def push(self, local_path: str, remote_path: str) -> None:
        async with await self._connect() as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.put(local_path, remote_path, recurse=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_droplet.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/droplet.py recon_mcp/tests/test_droplet.py
git commit -m "recon-mcp: droplet lifecycle with guaranteed teardown"
```

---

### Task 8: Job state store (aiosqlite)

**Files:**
- Create: `recon_mcp/jobs.py`
- Test: `recon_mcp/tests/test_jobs.py`

Goal: persistent job records: `(job_id, created_at, status, target_spec_json, regions_json, droplet_ids_json, artifacts_dir, error)`. Enables `recon_status`, `recon_list_jobs`, and orphan recovery.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_jobs.py`:

```python
import pytest
from recon_mcp.jobs import JobStore, JobStatus


@pytest.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_create_and_get(store):
    jid = await store.create(target_spec={"targets": ["1.2.3.4"]}, regions=["nyc1"])
    job = await store.get(jid)
    assert job["status"] == JobStatus.PENDING
    assert job["regions"] == ["nyc1"]


@pytest.mark.asyncio
async def test_update_status(store):
    jid = await store.create(target_spec={"targets": ["1.2.3.4"]}, regions=["nyc1"])
    await store.set_status(jid, JobStatus.RUNNING)
    assert (await store.get(jid))["status"] == JobStatus.RUNNING


@pytest.mark.asyncio
async def test_attach_droplet(store):
    jid = await store.create(target_spec={"targets": ["x"]}, regions=["nyc1"])
    await store.attach_droplet(jid, droplet_id=42, region="nyc1")
    job = await store.get(jid)
    assert {"id": 42, "region": "nyc1"} in job["droplets"]


@pytest.mark.asyncio
async def test_list_active(store):
    j1 = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    j2 = await store.create(target_spec={"t": 2}, regions=["nyc1"])
    await store.set_status(j2, JobStatus.DONE)
    active = await store.list_active()
    assert [j["id"] for j in active] == [j1]


@pytest.mark.asyncio
async def test_set_error(store):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    await store.set_error(jid, "boom")
    job = await store.get(jid)
    assert job["status"] == JobStatus.FAILED
    assert job["error"] == "boom"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_jobs.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement JobStore**

Create `recon_mcp/jobs.py`:

```python
"""Aiosqlite-backed job + droplet state store."""
from __future__ import annotations

import json
import os
import time
import uuid
from enum import StrEnum

import aiosqlite


class JobStatus(StrEnum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELED = "canceled"


_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    created_at REAL NOT NULL,
    status TEXT NOT NULL,
    target_spec TEXT NOT NULL,
    regions TEXT NOT NULL,
    droplets TEXT NOT NULL DEFAULT '[]',
    artifacts_dir TEXT,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
"""


class JobStore:
    def __init__(self, db_path: str) -> None:
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self._path) as db:
            await db.executescript(_SCHEMA)
            await db.commit()

    async def create(self, *, target_spec: dict, regions: list[str], artifacts_dir: str | None = None) -> str:
        jid = uuid.uuid4().hex[:12]
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                "INSERT INTO jobs (id, created_at, status, target_spec, regions, artifacts_dir) VALUES (?,?,?,?,?,?)",
                (jid, time.time(), JobStatus.PENDING.value, json.dumps(target_spec), json.dumps(regions), artifacts_dir),
            )
            await db.commit()
        return jid

    async def get(self, job_id: str) -> dict | None:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)) as cur:
                row = await cur.fetchone()
        if not row:
            return None
        return self._row_to_dict(row)

    async def set_status(self, job_id: str, status: JobStatus) -> None:
        async with aiosqlite.connect(self._path) as db:
            await db.execute("UPDATE jobs SET status = ? WHERE id = ?", (status.value, job_id))
            await db.commit()

    async def attach_droplet(self, job_id: str, *, droplet_id: int, region: str) -> None:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT droplets FROM jobs WHERE id = ?", (job_id,)) as cur:
                row = await cur.fetchone()
            drops = json.loads(row["droplets"]) if row else []
            drops.append({"id": droplet_id, "region": region})
            await db.execute("UPDATE jobs SET droplets = ? WHERE id = ?", (json.dumps(drops), job_id))
            await db.commit()

    async def set_error(self, job_id: str, msg: str) -> None:
        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                "UPDATE jobs SET status = ?, error = ? WHERE id = ?",
                (JobStatus.FAILED.value, msg, job_id),
            )
            await db.commit()

    async def list_active(self) -> list[dict]:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM jobs WHERE status NOT IN (?, ?, ?) ORDER BY created_at",
                (JobStatus.DONE.value, JobStatus.FAILED.value, JobStatus.CANCELED.value),
            ) as cur:
                rows = await cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    async def list_all(self) -> list[dict]:
        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM jobs ORDER BY created_at DESC") as cur:
                rows = await cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "status": row["status"],
            "target_spec": json.loads(row["target_spec"]),
            "regions": json.loads(row["regions"]),
            "droplets": json.loads(row["droplets"]),
            "artifacts_dir": row["artifacts_dir"],
            "error": row["error"],
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_jobs.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/jobs.py recon_mcp/tests/test_jobs.py
git commit -m "recon-mcp: aiosqlite job + droplet state store"
```

---

## Phase 3: phase scripts (run on droplets)

### Task 9: Phase scripts — scan, subdomains, resolve, httpx, ferox

**Files:**
- Create: `recon_mcp/runner_scripts/phase_scan.sh`
- Create: `recon_mcp/runner_scripts/phase_subdomains.sh`
- Create: `recon_mcp/runner_scripts/phase_resolve.sh`
- Create: `recon_mcp/runner_scripts/phase_httpx.sh`
- Create: `recon_mcp/runner_scripts/phase_ferox.sh`
- Test: `recon_mcp/tests/test_phase_scripts.py`

Goal: each phase is a small idempotent bash script that reads input lists from `/opt/recon/in/<name>.txt`, writes outputs to `/opt/recon/out/<name>/*.json|*.txt`, and exits non-zero only on hard failure (an empty result is success). Each script is independently runnable on the droplet.

- [ ] **Step 1: Write the failing tests (syntax + shellcheck)**

Create `recon_mcp/tests/test_phase_scripts.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_phase_scripts.py -v`
Expected: FileNotFoundError per phase.

- [ ] **Step 3: Create phase_scan.sh**

Create `recon_mcp/runner_scripts/phase_scan.sh`:

```bash
#!/usr/bin/env bash
# Scan phase: masscan top-10k + remainder, dig/nslookup PTR, shodan host lookup.
# Inputs: /opt/recon/in/ips.txt (one IP or CIDR per line)
# Outputs: /opt/recon/out/scan/{masscan_top10k.json,masscan_rest.json,ptr.json,shodan.json,hosts.txt}
set -euo pipefail

IN="/opt/recon/in/ips.txt"
OUT="/opt/recon/out/scan"
mkdir -p "$OUT"
test -s "$IN" || { echo "no IP input; skipping" >&2; exit 0; }

# masscan top 10000 ports
masscan -iL "$IN" --top-ports 10000 --rate 5000 -oJ "$OUT/masscan_top10k.json" || true

# remainder ports (1-65535 minus top10k). masscan's --exclude-ports requires a list,
# but running 1-65535 again at lower rate is simpler and still terminates in minutes.
masscan -iL "$IN" -p1-65535 --rate 2500 -oJ "$OUT/masscan_rest.json" || true

# Aggregate live hosts
jq -r '.[]?.ip' "$OUT/masscan_top10k.json" "$OUT/masscan_rest.json" 2>/dev/null \
    | sort -u > "$OUT/hosts.txt" || true

# dig + nslookup PTR for each live host
: > "$OUT/ptr.json"
while read -r ip; do
    [ -z "$ip" ] && continue
    ptr=$(dig +short -x "$ip" | sed 's/\.$//' | head -n1 || true)
    nptr=$(nslookup "$ip" 2>/dev/null | awk -F'= ' '/name =/ {print $2}' | sed 's/\.$//' | head -n1 || true)
    jq -nc --arg ip "$ip" --arg dig "$ptr" --arg nslookup "$nptr" \
        '{ip: $ip, dig_ptr: $dig, nslookup_ptr: $nslookup}' >> "$OUT/ptr.json"
done < "$OUT/hosts.txt"

# shodan host info (only if SHODAN_API_KEY is set in env)
: > "$OUT/shodan.json"
if [ -n "${SHODAN_API_KEY:-}" ]; then
    shodan init "$SHODAN_API_KEY" >/dev/null
    while read -r ip; do
        [ -z "$ip" ] && continue
        out=$(shodan host --format json "$ip" 2>/dev/null || true)
        [ -n "$out" ] && echo "$out" >> "$OUT/shodan.json"
    done < "$OUT/hosts.txt"
fi

echo "scan phase done; $(wc -l < "$OUT/hosts.txt") live hosts" >&2
```

- [ ] **Step 4: Create phase_subdomains.sh**

Create `recon_mcp/runner_scripts/phase_subdomains.sh`:

```bash
#!/usr/bin/env bash
# Subdomain enum: amass passive, subfinder, c99.nl API, hackertarget reverse-IP.
# Inputs:
#   /opt/recon/in/domains.txt  (one apex per line)
#   /opt/recon/in/ips.txt      (for reverse-IP via hackertarget)
# Outputs: /opt/recon/out/subs/{amass.txt,subfinder.txt,c99.txt,reverseip.txt,all.txt}
set -euo pipefail

OUT="/opt/recon/out/subs"
mkdir -p "$OUT"

DOM="/opt/recon/in/domains.txt"
IPS="/opt/recon/in/ips.txt"

: > "$OUT/amass.txt"
: > "$OUT/subfinder.txt"
: > "$OUT/c99.txt"
: > "$OUT/reverseip.txt"

if [ -s "$DOM" ]; then
    while read -r d; do
        [ -z "$d" ] && continue
        amass enum -passive -d "$d" -timeout 5 >> "$OUT/amass.txt" || true
        subfinder -silent -d "$d" >> "$OUT/subfinder.txt" || true
        if [ -n "${C99_API_KEY:-}" ]; then
            curl -fsSL "https://api.c99.nl/subdomainfinder?key=${C99_API_KEY}&domain=${d}&json" \
                | jq -r '.subdomains[]?.subdomain' >> "$OUT/c99.txt" || true
        fi
    done < "$DOM"
fi

if [ -s "$IPS" ]; then
    while read -r ip; do
        [ -z "$ip" ] && continue
        # hackertarget reverse-IP (free tier: rate-limited, ~50/day)
        curl -fsSL "https://api.hackertarget.com/reverseiplookup/?q=${ip}" \
            | grep -v 'API count' >> "$OUT/reverseip.txt" || true
        sleep 1
    done < "$IPS"
fi

cat "$OUT/amass.txt" "$OUT/subfinder.txt" "$OUT/c99.txt" "$OUT/reverseip.txt" \
    | tr '[:upper:]' '[:lower:]' | grep -E '^[a-z0-9.-]+\.[a-z]{2,}$' \
    | sort -u > "$OUT/all.txt"

echo "subdomain phase done; $(wc -l < "$OUT/all.txt") unique subs" >&2
```

- [ ] **Step 5: Create phase_resolve.sh**

Create `recon_mcp/runner_scripts/phase_resolve.sh`:

```bash
#!/usr/bin/env bash
# Resolve all collected subdomains back to IPs. Reveals IPs missed by initial input.
# Inputs:  /opt/recon/out/subs/all.txt
# Outputs: /opt/recon/out/resolve/{resolved.json,new_ips.txt}
set -euo pipefail

IN="/opt/recon/out/subs/all.txt"
ORIG_IPS="/opt/recon/in/ips.txt"
OUT="/opt/recon/out/resolve"
mkdir -p "$OUT"
test -s "$IN" || { echo "no subs to resolve" >&2; exit 0; }

: > "$OUT/resolved.json"
while read -r host; do
    [ -z "$host" ] && continue
    ips=$(dig +short A "$host" | tr '\n' ',' | sed 's/,$//')
    [ -z "$ips" ] && continue
    jq -nc --arg h "$host" --arg ips "$ips" '{host: $h, ips: ($ips | split(","))}' >> "$OUT/resolved.json"
done < "$IN"

# Find IPs not present in the original input list
jq -r '.ips[]' "$OUT/resolved.json" | sort -u > "$OUT/all_resolved_ips.txt"
if [ -s "$ORIG_IPS" ]; then
    sort -u "$ORIG_IPS" > "$OUT/orig_ips.sorted"
    comm -23 "$OUT/all_resolved_ips.txt" "$OUT/orig_ips.sorted" > "$OUT/new_ips.txt"
else
    cp "$OUT/all_resolved_ips.txt" "$OUT/new_ips.txt"
fi

echo "resolve phase done; $(wc -l < "$OUT/new_ips.txt") new IPs" >&2
```

- [ ] **Step 6: Create phase_httpx.sh**

Create `recon_mcp/runner_scripts/phase_httpx.sh`:

```bash
#!/usr/bin/env bash
# httpx liveness + fingerprint over (subs + hosts + new_ips).
# Inputs:  /opt/recon/out/subs/all.txt, /opt/recon/out/scan/hosts.txt, /opt/recon/out/resolve/new_ips.txt
# Outputs: /opt/recon/out/httpx/{targets.txt,httpx.json}
set -euo pipefail

OUT="/opt/recon/out/httpx"
mkdir -p "$OUT"

cat /opt/recon/out/subs/all.txt /opt/recon/out/scan/hosts.txt /opt/recon/out/resolve/new_ips.txt 2>/dev/null \
    | sort -u > "$OUT/targets.txt"

test -s "$OUT/targets.txt" || { echo "no targets for httpx" >&2; exit 0; }

httpx -silent -json \
    -status-code -title -tech-detect -tls-grab -content-length \
    -threads 50 -rate-limit 200 -timeout 10 -retries 1 \
    -ports 80,443,8080,8443,8000,8888 \
    -l "$OUT/targets.txt" -o "$OUT/httpx.json" || true

echo "httpx phase done; $(wc -l < "$OUT/httpx.json" 2>/dev/null || echo 0) live URLs" >&2
```

- [ ] **Step 7: Create phase_ferox.sh**

Create `recon_mcp/runner_scripts/phase_ferox.sh`:

```bash
#!/usr/bin/env bash
# feroxbuster directory brute over each httpx-validated URL.
# Input:  /opt/recon/out/httpx/httpx.json
# Output: /opt/recon/out/ferox/<sanitized_host>.json
set -euo pipefail

IN="/opt/recon/out/httpx/httpx.json"
OUT="/opt/recon/out/ferox"
WORDLIST="/opt/SecLists/Discovery/Web-Content/raft-large-directories.txt"
mkdir -p "$OUT"

test -s "$IN" || { echo "no httpx results; skipping" >&2; exit 0; }
test -s "$WORDLIST" || { echo "wordlist missing: $WORDLIST" >&2; exit 1; }

jq -r '.url' "$IN" | sort -u | while read -r url; do
    [ -z "$url" ] && continue
    safe=$(echo "$url" | sed 's|https\?://||; s|[/:?&=]|_|g')
    feroxbuster --silent --json \
        --url "$url" \
        --wordlist "$WORDLIST" \
        --threads 30 \
        --depth 2 \
        --timeout 7 \
        --status-codes 200,204,301,302,307,401,403 \
        --output "$OUT/${safe}.json" \
        || true
done

echo "ferox phase done" >&2
```

- [ ] **Step 8: Make all phase scripts executable**

```bash
chmod +x recon_mcp/runner_scripts/*.sh
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_phase_scripts.py -v`
Expected: ≥15 passed (5 phases × 3 always-on tests; shellcheck tests skip if not installed).

- [ ] **Step 10: Commit**

```bash
git add recon_mcp/runner_scripts/phase_*.sh recon_mcp/tests/test_phase_scripts.py
git commit -m "recon-mcp: per-phase runner scripts for masscan/dns/subs/resolve/httpx/ferox"
```

---

## Phase 4: scanner orchestration

### Task 10: Scanner — drive phases on a single droplet for one target

**Files:**
- Create: `recon_mcp/scanner.py`
- Test: `recon_mcp/tests/test_scanner.py`

Goal: given a `Droplet` (already provisioned + bootstrapped) and a single `Target`, push inputs, run the correct phase sequence, pull artifacts. Wildcard-only targets skip scan + resolve+masscan-on-new-IPs phases.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_scanner.py`:

```python
from unittest.mock import AsyncMock, MagicMock
import pytest
from recon_mcp.input_parser import Target, TargetKind
from recon_mcp.scanner import run_scan, PhaseResult


def fake_droplet():
    d = MagicMock()
    d.ip = "1.2.3.4"
    d.run = AsyncMock(return_value=(0, "ok", ""))
    d.push = AsyncMock()
    d.pull = AsyncMock()
    return d


@pytest.mark.asyncio
async def test_ip_target_runs_all_phases(tmp_path):
    d = fake_droplet()
    res = await run_scan(
        droplet=d, target=Target(TargetKind.IP, "9.9.9.9"),
        local_out=tmp_path, env={},
    )
    phases = [c.args[0] for c in d.run.await_args_list if "phase_" in str(c.args[0])]
    assert any("phase_scan.sh" in p for p in phases)
    assert any("phase_subdomains.sh" in p for p in phases)
    assert any("phase_resolve.sh" in p for p in phases)
    assert any("phase_httpx.sh" in p for p in phases)
    assert any("phase_ferox.sh" in p for p in phases)


@pytest.mark.asyncio
async def test_wildcard_target_skips_scan(tmp_path):
    d = fake_droplet()
    await run_scan(
        droplet=d, target=Target(TargetKind.WILDCARD, "example.com"),
        local_out=tmp_path, env={},
    )
    phases = [str(c.args[0]) for c in d.run.await_args_list]
    assert not any("phase_scan.sh" in p for p in phases)
    assert any("phase_subdomains.sh" in p for p in phases)
    assert any("phase_httpx.sh" in p for p in phases)


@pytest.mark.asyncio
async def test_cidr_runs_scan(tmp_path):
    d = fake_droplet()
    await run_scan(
        droplet=d, target=Target(TargetKind.CIDR, "10.0.0.0/24"),
        local_out=tmp_path, env={},
    )
    phases = [str(c.args[0]) for c in d.run.await_args_list]
    assert any("phase_scan.sh" in p for p in phases)


@pytest.mark.asyncio
async def test_pulls_artifacts_into_local_out(tmp_path):
    d = fake_droplet()
    await run_scan(
        droplet=d, target=Target(TargetKind.WILDCARD, "ex.com"),
        local_out=tmp_path, env={},
    )
    d.pull.assert_awaited()  # at least one pull happened


@pytest.mark.asyncio
async def test_phase_failure_recorded_not_raised(tmp_path):
    d = fake_droplet()
    # subdomains phase fails on this droplet
    async def run_side(cmd, *, check=False, **kw):
        if "phase_subdomains.sh" in cmd:
            return (2, "", "amass crashed")
        return (0, "ok", "")
    d.run.side_effect = run_side
    res = await run_scan(
        droplet=d, target=Target(TargetKind.WILDCARD, "ex.com"),
        local_out=tmp_path, env={},
    )
    sub = [p for p in res.phases if p.name == "subdomains"][0]
    assert sub.status == "failed"
    assert "amass crashed" in sub.stderr
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_scanner.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement scanner**

Create `recon_mcp/scanner.py`:

```python
"""Drive the per-target phase pipeline on a single droplet."""
from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from .input_parser import Target, TargetKind

log = structlog.get_logger(__name__)


@dataclass
class PhaseResult:
    name: str
    status: str  # "ok" | "failed" | "skipped"
    stdout: str = ""
    stderr: str = ""


@dataclass
class ScanResult:
    target: Target
    phases: list[PhaseResult] = field(default_factory=list)


_PHASE_BIN = "/opt/recon/scripts"


def _phases_for(target: Target) -> list[str]:
    if target.kind is TargetKind.WILDCARD:
        return ["subdomains", "resolve", "httpx", "ferox"]
    return ["scan", "subdomains", "resolve", "httpx", "ferox"]


def _input_payload(target: Target) -> dict[str, str]:
    if target.kind is TargetKind.IP:
        return {"ips.txt": target.value, "domains.txt": ""}
    if target.kind is TargetKind.CIDR:
        return {"ips.txt": target.value, "domains.txt": ""}
    return {"ips.txt": "", "domains.txt": target.value}


async def run_scan(
    *, droplet, target: Target, local_out: Path, env: dict[str, str],
) -> ScanResult:
    result = ScanResult(target=target)

    # Stage runner scripts and inputs
    await droplet.run(f"mkdir -p /opt/recon/in /opt/recon/out /opt/recon/scripts", check=True)
    # The scripts were placed by cloud-init bootstrap or pushed by the caller.
    for name, content in _input_payload(target).items():
        path = f"/opt/recon/in/{name}"
        # echo via heredoc so we don't have to push a file
        await droplet.run(f"cat > {path} <<'__EOF__'\n{content}\n__EOF__", check=True)

    env_prefix = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())
    for phase in _phases_for(target):
        cmd = f"{env_prefix} bash {_PHASE_BIN}/phase_{phase}.sh"
        rc, out, err = await droplet.run(cmd, check=False, timeout=3600)
        status = "ok" if rc == 0 else "failed"
        result.phases.append(PhaseResult(name=phase, status=status, stdout=out, stderr=err))
        if rc != 0:
            log.warning("phase_failed", target=target.value, phase=phase, stderr=err[:500])

    # Pull artifacts
    local_out.mkdir(parents=True, exist_ok=True)
    try:
        await droplet.pull("/opt/recon/out", str(local_out / "out"))
    except Exception as e:
        log.error("pull_failed", err=str(e))
        result.phases.append(PhaseResult(name="pull", status="failed", stderr=str(e)))

    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_scanner.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/scanner.py recon_mcp/tests/test_scanner.py
git commit -m "recon-mcp: scanner orchestrates phase pipeline per target"
```

---

### Task 11: Artifacts — parse phase outputs into a structured JSON summary

**Files:**
- Create: `recon_mcp/artifacts.py`
- Test: `recon_mcp/tests/test_artifacts.py`

Goal: given a pulled `out/` tree, return a single JSON-serializable summary: live hosts, open ports per host, PTR records, shodan banners, subdomains by source, http endpoints with title + tech, feroxbuster findings (path + status + size).

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_artifacts.py`:

```python
import json
from pathlib import Path
import pytest
from recon_mcp.artifacts import summarize


@pytest.fixture
def fake_out(tmp_path):
    """Fabricate the directory layout phase scripts produce."""
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_artifacts.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement summarize**

Create `recon_mcp/artifacts.py`:

```python
"""Parse pulled-down phase outputs into a single structured summary."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_lines(p: Path) -> list[str]:
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text().splitlines() if l.strip()]


def _read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out: list[dict] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _read_json(p: Path) -> Any:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def summarize(root: Path) -> dict:
    out = root / "out"
    hosts = _summarize_hosts(out)
    return {
        "hosts": hosts,
        "subdomains": _read_lines(out / "subs" / "all.txt"),
        "new_ips_from_resolve": _read_lines(out / "resolve" / "new_ips.txt"),
        "http_endpoints": _summarize_httpx(out),
        "ferox_findings": _summarize_ferox(out),
    }


def _summarize_hosts(out: Path) -> list[dict]:
    ips = _read_lines(out / "scan" / "hosts.txt")
    masscan = _read_json(out / "scan" / "masscan_top10k.json") or []
    masscan_rest = _read_json(out / "scan" / "masscan_rest.json") or []
    ports_by_ip: dict[str, set[int]] = {}
    for entry in [*masscan, *masscan_rest]:
        ip = entry.get("ip")
        if not ip:
            continue
        for p in entry.get("ports", []):
            port = p.get("port")
            if port is not None:
                ports_by_ip.setdefault(ip, set()).add(int(port))
    ptr = {rec["ip"]: rec for rec in _read_jsonl(out / "scan" / "ptr.json")}
    return [
        {
            "ip": ip,
            "ports": sorted(ports_by_ip.get(ip, set())),
            "ptr": (ptr.get(ip, {}).get("dig_ptr") or ptr.get(ip, {}).get("nslookup_ptr") or None),
        }
        for ip in sorted(set(ips) | ports_by_ip.keys())
    ]


def _summarize_httpx(out: Path) -> list[dict]:
    return [
        {
            "url": r.get("url"),
            "status_code": r.get("status_code"),
            "title": r.get("title"),
            "tech": r.get("tech") or [],
            "tls": r.get("tls"),
        }
        for r in _read_jsonl(out / "httpx" / "httpx.json")
        if r.get("url")
    ]


def _summarize_ferox(out: Path) -> list[dict]:
    findings: list[dict] = []
    ferox_dir = out / "ferox"
    if not ferox_dir.exists():
        return findings
    for f in ferox_dir.glob("*.json"):
        for r in _read_jsonl(f):
            if r.get("type") != "response":
                continue
            findings.append({
                "url": r.get("url"),
                "status": r.get("status"),
                "content_length": r.get("content_length"),
            })
    return findings
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_artifacts.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/artifacts.py recon_mcp/tests/test_artifacts.py
git commit -m "recon-mcp: artifact parser → structured summary"
```

---

## Phase 5: MCP handlers

### Task 12: Pydantic tool I/O schemas

**Files:**
- Create: `recon_mcp/tools.py`
- Test: `recon_mcp/tests/test_tools.py`

Goal: define the request/response models for all six MCP tools so the handler layer can validate inputs and the MCP server can advertise JSON Schemas.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_tools.py`:

```python
import pytest
from recon_mcp.tools import (
    ReconStartIn, ReconStatusIn, ReconResultsIn, ReconCancelIn,
)


def test_start_input_defaults():
    inp = ReconStartIn(targets=["1.2.3.4"], target_name="acme")
    assert inp.scan_region == "nyc1"
    assert inp.probe_regions == []
    assert inp.max_droplets == 10


def test_start_input_multi_region():
    inp = ReconStartIn(targets=["*.x.com"], target_name="x", probe_regions=["nyc1", "fra1"])
    assert inp.probe_regions == ["nyc1", "fra1"]


def test_start_input_rejects_unknown_field():
    with pytest.raises(Exception):
        ReconStartIn(targets=["x"], target_name="t", banana=1)


def test_status_in_requires_job_id():
    with pytest.raises(Exception):
        ReconStatusIn()


def test_cancel_in_requires_job_id():
    with pytest.raises(Exception):
        ReconCancelIn()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_tools.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement tool models**

Create `recon_mcp/tools.py`:

```python
"""Pydantic request/response models for recon-mcp tools."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReconStartIn(_Strict):
    targets: list[str] = Field(..., description="IPs, CIDRs, or *.domain.tld entries")
    target_name: str = Field(..., description="Engagement name (used for artifact dir)")
    scan_region: str = Field("nyc1", description="DO region for scan-heavy phases")
    probe_regions: list[str] = Field(
        default_factory=list,
        description="Additional regions to run httpx+feroxbuster from (geo-block detection)",
    )
    max_droplets: int = Field(10, ge=1, le=50)


class ReconStartOut(_Strict):
    job_id: str
    target_count: int
    droplet_plan: list[dict]  # [{"region": "nyc1", "purpose": "scan|probe", "targets": N}]


class ReconStatusIn(_Strict):
    job_id: str


class ReconStatusOut(_Strict):
    job_id: str
    status: str
    droplets: list[dict]
    artifacts_dir: str | None
    error: str | None
    phase_progress: dict[str, str] = Field(default_factory=dict)


class ReconResultsIn(_Strict):
    job_id: str


class ReconResultsOut(_Strict):
    job_id: str
    summary: dict


class ReconCancelIn(_Strict):
    job_id: str


class ReconCancelOut(_Strict):
    job_id: str
    destroyed_droplets: list[int]


class ReconListJobsOut(_Strict):
    jobs: list[dict]


class ReconCleanupOrphansOut(_Strict):
    destroyed: list[int]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_tools.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/tools.py recon_mcp/tests/test_tools.py
git commit -m "recon-mcp: pydantic tool I/O schemas"
```

---

### Task 13: `recon_start` handler — provision plan + background launch

**Files:**
- Create: `recon_mcp/handlers/__init__.py`
- Create: `recon_mcp/handlers/start.py`
- Test: `recon_mcp/tests/test_handlers_start.py`

Goal: validate input, persist a `pending` job, return `(job_id, droplet_plan)` immediately, and spawn an asyncio background task that does the real work. The background task: generates ephemeral SSH keypair → uploads as DO ssh-key → provisions droplets concurrently (1 scan + N probe) → runs scanners in parallel → collects → summarizes → marks job DONE → tears down → removes SSH key.

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/handlers/__init__.py`: (empty)

Create `recon_mcp/tests/test_handlers_start.py`:

```python
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from recon_mcp.tools import ReconStartIn
from recon_mcp.handlers.start import handle_start
from recon_mcp.jobs import JobStore, JobStatus


@pytest.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.fixture
def cfg(tmp_path):
    from recon_mcp.config import Config
    return Config(
        do_api_token="t", shodan_api_key=None, c99_api_key=None,
        db_path=tmp_path / "j.sqlite", ssh_key_dir=tmp_path / "ssh",
        max_droplets_per_job=10, max_runtime_min=180,
        default_scan_region="nyc1", droplet_size="s-2vcpu-4gb",
    )


@pytest.mark.asyncio
async def test_start_returns_job_id_and_plan(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["1.2.3.4", "*.x.com"], target_name="acme")
    with patch("recon_mcp.handlers.start._run_job", new=AsyncMock()):
        out = await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)
    assert out.job_id
    assert out.target_count == 2
    assert any(p["purpose"] == "scan" for p in out.droplet_plan)


@pytest.mark.asyncio
async def test_start_persists_pending_job(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["1.2.3.4"], target_name="acme")
    with patch("recon_mcp.handlers.start._run_job", new=AsyncMock()):
        out = await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)
    job = await store.get(out.job_id)
    assert job["status"] == JobStatus.PENDING


@pytest.mark.asyncio
async def test_start_rejects_huge_cidr(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["10.0.0.0/8"], target_name="acme")
    with pytest.raises(Exception, match="too large"):
        await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)


@pytest.mark.asyncio
async def test_start_with_probe_regions(store, cfg, tmp_path):
    inp = ReconStartIn(targets=["*.x.com"], target_name="x", probe_regions=["fra1", "sgp1"])
    with patch("recon_mcp.handlers.start._run_job", new=AsyncMock()):
        out = await handle_start(inp, store=store, cfg=cfg, artifacts_root=tmp_path)
    regions = {p["region"] for p in out.droplet_plan}
    assert {"nyc1", "fra1", "sgp1"}.issubset(regions)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_start.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement handle_start + _run_job**

Create `recon_mcp/handlers/start.py`:

```python
"""recon_start handler — validates input, persists job, spawns background runner."""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path

import structlog

from ..artifacts import summarize
from ..cloud_init import render_user_data
from ..config import Config
from ..do_client import DOClient
from ..droplet import Droplet
from ..input_parser import parse_targets, TargetKind
from ..jobs import JobStatus, JobStore
from ..regions import validate_regions
from ..safety import check_targets
from ..scanner import run_scan
from ..tools import ReconStartIn, ReconStartOut

log = structlog.get_logger(__name__)


def _droplet_plan(targets, scan_region: str, probe_regions: list[str]) -> list[dict]:
    plan = [{"region": scan_region, "purpose": "scan", "targets": len(targets)}]
    for r in probe_regions:
        plan.append({"region": r, "purpose": "probe", "targets": len(targets)})
    return plan


async def handle_start(
    inp: ReconStartIn, *, store: JobStore, cfg: Config, artifacts_root: Path,
) -> ReconStartOut:
    targets = parse_targets(inp.targets)
    check_targets(targets)
    probe_regions = validate_regions(inp.probe_regions) if inp.probe_regions else []
    scan_region = inp.scan_region or cfg.default_scan_region
    plan = _droplet_plan(targets, scan_region, probe_regions)

    artifacts_dir = artifacts_root / f"recon_{store._path}_jobs"  # placeholder; replaced below
    job_id = await store.create(
        target_spec={"targets": [{"kind": t.kind.value, "value": t.value} for t in targets],
                     "target_name": inp.target_name},
        regions=[scan_region, *probe_regions],
        artifacts_dir=str(artifacts_root / inp.target_name / "recon" / "_pending"),
    )
    final_dir = artifacts_root / inp.target_name / "recon" / job_id
    final_dir.mkdir(parents=True, exist_ok=True)

    asyncio.create_task(_run_job(
        job_id=job_id, targets=targets, scan_region=scan_region,
        probe_regions=probe_regions, store=store, cfg=cfg, out_dir=final_dir,
    ))

    return ReconStartOut(job_id=job_id, target_count=len(targets), droplet_plan=plan)


def _gen_ssh_keypair(ssh_dir: Path, job_id: str) -> tuple[Path, str]:
    ssh_dir.mkdir(parents=True, exist_ok=True)
    priv = ssh_dir / f"{job_id}.key"
    pub = ssh_dir / f"{job_id}.key.pub"
    subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-N", "", "-C", f"recon-{job_id}", "-f", str(priv)],
        check=True, capture_output=True,
    )
    os.chmod(priv, 0o600)
    return priv, pub.read_text().strip()


async def _run_job(*, job_id, targets, scan_region, probe_regions, store, cfg, out_dir: Path) -> None:
    do = DOClient(token=cfg.do_api_token)
    priv_key, pub_key = _gen_ssh_keypair(cfg.ssh_key_dir, job_id)
    try:
        ssh_key = await do.create_ssh_key(name=f"recon-{job_id}", public_key=pub_key)
    except Exception as e:
        await store.set_error(job_id, f"ssh_key_create: {e}")
        return
    try:
        await store.set_status(job_id, JobStatus.PROVISIONING)
        user_data = render_user_data(authorized_key=pub_key, job_id=job_id)
        droplets: list[tuple[Droplet, str]] = []  # (droplet, purpose)
        regions = [(scan_region, "scan")] + [(r, "probe") for r in probe_regions]

        async def make(region: str, purpose: str) -> tuple[Droplet, str]:
            d = Droplet(
                do=do, name=f"recon-{job_id}-{purpose}-{region}",
                region=region, size=cfg.droplet_size, image="ubuntu-24-04-x64",
                ssh_key_ids=[ssh_key["id"]], user_data=user_data,
                tags=["recon-mcp", f"job:{job_id}"],
            )
            d.ssh_private_key_path = str(priv_key)
            return (d, purpose)

        droplets = await asyncio.gather(*[make(r, p) for r, p in regions])

        async def with_provision(d: Droplet, purpose: str):
            await d.__aenter__()
            await store.attach_droplet(job_id, droplet_id=d.droplet_id, region=d.region)
            return (d, purpose)

        try:
            droplets = await asyncio.gather(*[with_provision(d, p) for d, p in droplets])
            await store.set_status(job_id, JobStatus.RUNNING)
            env = {}
            if cfg.shodan_api_key:
                env["SHODAN_API_KEY"] = cfg.shodan_api_key
            if cfg.c99_api_key:
                env["C99_API_KEY"] = cfg.c99_api_key

            # Run scanners in parallel: one droplet handles all targets sequentially per droplet.
            async def per_droplet(d: Droplet, purpose: str):
                local_out = out_dir / f"{purpose}_{d.region}"
                local_out.mkdir(parents=True, exist_ok=True)
                for t in targets:
                    await run_scan(droplet=d, target=t, local_out=local_out / t.value.replace("/", "_"),
                                   env=env)

            await asyncio.gather(*[per_droplet(d, p) for d, p in droplets])

            # Summarize the scan-region run only (probe regions are duplicates for geo comparison)
            scan_dir = out_dir / f"scan_{scan_region}"
            summary = {}
            if scan_dir.exists():
                for t_dir in scan_dir.iterdir():
                    if t_dir.is_dir():
                        summary[t_dir.name] = summarize(t_dir)
            (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))

            await store.set_status(job_id, JobStatus.DONE)
        finally:
            for d, _ in droplets:
                try:
                    await d.__aexit__(None, None, None)
                except Exception as e:
                    log.error("teardown_failed", err=str(e))
    except Exception as e:
        log.exception("run_job_failed", err=str(e))
        await store.set_error(job_id, str(e))
    finally:
        try:
            await do.delete_ssh_key(ssh_key["id"])
        except Exception:
            pass
        try:
            os.remove(priv_key)
            os.remove(str(priv_key) + ".pub")
        except Exception:
            pass
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_start.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/handlers/__init__.py recon_mcp/handlers/start.py recon_mcp/tests/test_handlers_start.py
git commit -m "recon-mcp: recon_start handler with parallel droplet provisioning"
```

---

### Task 14: `recon_status` handler

**Files:**
- Create: `recon_mcp/handlers/status.py`
- Test: `recon_mcp/tests/test_handlers_status.py`

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_handlers_status.py`:

```python
import pytest
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.status import handle_status
from recon_mcp.tools import ReconStatusIn


@pytest.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_status_returns_job(store):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    out = await handle_status(ReconStatusIn(job_id=jid), store=store)
    assert out.job_id == jid
    assert out.status == JobStatus.PENDING


@pytest.mark.asyncio
async def test_status_unknown_job(store):
    with pytest.raises(KeyError):
        await handle_status(ReconStatusIn(job_id="nope"), store=store)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_status.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement handler**

Create `recon_mcp/handlers/status.py`:

```python
"""recon_status handler — reads job row from store."""
from __future__ import annotations

from ..jobs import JobStore
from ..tools import ReconStatusIn, ReconStatusOut


async def handle_status(inp: ReconStatusIn, *, store: JobStore) -> ReconStatusOut:
    job = await store.get(inp.job_id)
    if not job:
        raise KeyError(f"unknown job: {inp.job_id}")
    return ReconStatusOut(
        job_id=job["id"],
        status=job["status"],
        droplets=job["droplets"],
        artifacts_dir=job["artifacts_dir"],
        error=job["error"],
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_status.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/handlers/status.py recon_mcp/tests/test_handlers_status.py
git commit -m "recon-mcp: recon_status handler"
```

---

### Task 15: `recon_results` handler

**Files:**
- Create: `recon_mcp/handlers/results.py`
- Test: `recon_mcp/tests/test_handlers_results.py`

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_handlers_results.py`:

```python
import json
from pathlib import Path
import pytest
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.results import handle_results
from recon_mcp.tools import ReconResultsIn


@pytest.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_returns_summary_when_done(store, tmp_path):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"], artifacts_dir=str(tmp_path))
    await store.set_status(jid, JobStatus.DONE)
    (tmp_path / "summary.json").write_text(json.dumps({"1.2.3.4": {"hosts": []}}))
    out = await handle_results(ReconResultsIn(job_id=jid), store=store)
    assert "1.2.3.4" in out.summary


@pytest.mark.asyncio
async def test_rejects_pending(store, tmp_path):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"], artifacts_dir=str(tmp_path))
    with pytest.raises(RuntimeError, match="not done"):
        await handle_results(ReconResultsIn(job_id=jid), store=store)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_results.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement handler**

Create `recon_mcp/handlers/results.py`:

```python
"""recon_results handler — reads summary.json under artifacts_dir."""
from __future__ import annotations

import json
from pathlib import Path

from ..jobs import JobStatus, JobStore
from ..tools import ReconResultsIn, ReconResultsOut


async def handle_results(inp: ReconResultsIn, *, store: JobStore) -> ReconResultsOut:
    job = await store.get(inp.job_id)
    if not job:
        raise KeyError(f"unknown job: {inp.job_id}")
    if job["status"] != JobStatus.DONE:
        raise RuntimeError(f"job {inp.job_id} not done (status={job['status']})")
    summary_path = Path(job["artifacts_dir"]) / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    return ReconResultsOut(job_id=inp.job_id, summary=summary)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_results.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/handlers/results.py recon_mcp/tests/test_handlers_results.py
git commit -m "recon-mcp: recon_results handler"
```

---

### Task 16: `recon_cancel` + `recon_list_jobs` + `recon_cleanup_orphans`

**Files:**
- Create: `recon_mcp/handlers/cancel.py`
- Create: `recon_mcp/handlers/list_jobs.py`
- Create: `recon_mcp/handlers/cleanup.py`
- Test: `recon_mcp/tests/test_handlers_cancel.py`
- Test: `recon_mcp/tests/test_handlers_cleanup.py`

Goal: cancel destroys every droplet attached to the job and marks it canceled. cleanup_orphans destroys every droplet tagged `recon-mcp` whose `job:<id>` tag refers to a job whose status is DONE/FAILED/CANCELED (or doesn't exist).

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_handlers_cancel.py`:

```python
from unittest.mock import AsyncMock, MagicMock
import pytest
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.cancel import handle_cancel
from recon_mcp.tools import ReconCancelIn


@pytest.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_cancel_destroys_attached_droplets(store):
    jid = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    await store.attach_droplet(jid, droplet_id=11, region="nyc1")
    await store.attach_droplet(jid, droplet_id=22, region="fra1")
    do = MagicMock()
    do.destroy_droplet = AsyncMock()
    out = await handle_cancel(ReconCancelIn(job_id=jid), store=store, do=do)
    assert set(out.destroyed_droplets) == {11, 22}
    do.destroy_droplet.assert_any_await(11)
    do.destroy_droplet.assert_any_await(22)
    job = await store.get(jid)
    assert job["status"] == JobStatus.CANCELED
```

Create `recon_mcp/tests/test_handlers_cleanup.py`:

```python
from unittest.mock import AsyncMock, MagicMock
import pytest
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.cleanup import handle_cleanup_orphans


@pytest.fixture
async def store(tmp_path):
    s = JobStore(db_path=str(tmp_path / "j.sqlite"))
    await s.init()
    return s


@pytest.mark.asyncio
async def test_destroys_droplets_for_unknown_or_finished_jobs(store):
    j_done = await store.create(target_spec={"t": 1}, regions=["nyc1"])
    await store.set_status(j_done, JobStatus.DONE)
    j_active = await store.create(target_spec={"t": 2}, regions=["nyc1"])
    await store.set_status(j_active, JobStatus.RUNNING)

    do = MagicMock()
    do.list_by_tag = AsyncMock(return_value=[
        {"id": 100, "tags": ["recon-mcp", f"job:{j_done}"]},   # finished → kill
        {"id": 200, "tags": ["recon-mcp", f"job:{j_active}"]}, # active → keep
        {"id": 300, "tags": ["recon-mcp", "job:ghostid"]},     # unknown → kill
    ])
    do.destroy_droplet = AsyncMock()

    out = await handle_cleanup_orphans(store=store, do=do)
    assert set(out.destroyed) == {100, 300}
    do.destroy_droplet.assert_any_await(100)
    do.destroy_droplet.assert_any_await(300)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_cancel.py tests/test_handlers_cleanup.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement cancel**

Create `recon_mcp/handlers/cancel.py`:

```python
"""recon_cancel handler."""
from __future__ import annotations

from ..do_client import DOClient
from ..jobs import JobStatus, JobStore
from ..tools import ReconCancelIn, ReconCancelOut


async def handle_cancel(inp: ReconCancelIn, *, store: JobStore, do: DOClient) -> ReconCancelOut:
    job = await store.get(inp.job_id)
    if not job:
        raise KeyError(f"unknown job: {inp.job_id}")
    destroyed: list[int] = []
    for drop in job["droplets"]:
        try:
            await do.destroy_droplet(drop["id"])
            destroyed.append(drop["id"])
        except Exception:
            pass
    await store.set_status(inp.job_id, JobStatus.CANCELED)
    return ReconCancelOut(job_id=inp.job_id, destroyed_droplets=destroyed)
```

- [ ] **Step 4: Implement list_jobs**

Create `recon_mcp/handlers/list_jobs.py`:

```python
"""recon_list_jobs handler."""
from __future__ import annotations

from ..jobs import JobStore
from ..tools import ReconListJobsOut


async def handle_list_jobs(*, store: JobStore) -> ReconListJobsOut:
    jobs = await store.list_all()
    return ReconListJobsOut(jobs=[
        {k: v for k, v in j.items() if k not in ("target_spec",)} for j in jobs
    ])
```

- [ ] **Step 5: Implement cleanup**

Create `recon_mcp/handlers/cleanup.py`:

```python
"""recon_cleanup_orphans handler — destroys recon-mcp droplets whose owning job is finished/missing."""
from __future__ import annotations

import re

from ..do_client import DOClient
from ..jobs import JobStatus, JobStore
from ..tools import ReconCleanupOrphansOut

_JOB_TAG = re.compile(r"^job:([a-z0-9]+)$")
_TERMINAL = {JobStatus.DONE.value, JobStatus.FAILED.value, JobStatus.CANCELED.value}


async def handle_cleanup_orphans(*, store: JobStore, do: DOClient) -> ReconCleanupOrphansOut:
    drops = await do.list_by_tag("recon-mcp")
    destroyed: list[int] = []
    for d in drops:
        tags = d.get("tags") or []
        job_id = next((m.group(1) for t in tags if (m := _JOB_TAG.match(t))), None)
        if not job_id:
            continue
        row = await store.get(job_id)
        if row is None or row["status"] in _TERMINAL:
            try:
                await do.destroy_droplet(d["id"])
                destroyed.append(d["id"])
            except Exception:
                pass
    return ReconCleanupOrphansOut(destroyed=destroyed)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_handlers_cancel.py tests/test_handlers_cleanup.py -v`
Expected: 2 passed.

- [ ] **Step 7: Commit**

```bash
git add recon_mcp/handlers/cancel.py recon_mcp/handlers/list_jobs.py recon_mcp/handlers/cleanup.py recon_mcp/tests/test_handlers_cancel.py recon_mcp/tests/test_handlers_cleanup.py
git commit -m "recon-mcp: cancel, list_jobs, cleanup_orphans handlers"
```

---

## Phase 6: MCP server entry + wiring

### Task 17: MCP server stdio entry

**Files:**
- Create: `recon_mcp/server.py`
- Test: `recon_mcp/tests/test_server.py`

Goal: stdio MCP server that registers six tools, dispatches to handlers, returns JSON content blocks. On startup: init JobStore + run `cleanup_orphans` once (idempotent safety sweep).

- [ ] **Step 1: Write the failing tests**

Create `recon_mcp/tests/test_server.py`:

```python
import pytest
from recon_mcp.server import build_server


@pytest.mark.asyncio
async def test_server_advertises_six_tools(monkeypatch, tmp_path):
    monkeypatch.setenv("DO_API_TOKEN", "x")
    monkeypatch.setenv("RECON_DB_PATH", str(tmp_path / "j.sqlite"))
    monkeypatch.setenv("RECON_SSH_KEY_DIR", str(tmp_path / "ssh"))
    srv = await build_server()
    tools = await srv.list_tools()
    names = {t.name for t in tools}
    assert names == {
        "recon_start", "recon_status", "recon_results",
        "recon_cancel", "recon_list_jobs", "recon_cleanup_orphans",
    }
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd recon_mcp && uv run pytest tests/test_server.py -v`
Expected: ImportError.

- [ ] **Step 3: Implement server**

Create `recon_mcp/server.py`:

```python
"""recon-mcp stdio server entrypoint."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import mcp.types as types
import structlog
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import load_config
from .do_client import DOClient
from .handlers.cancel import handle_cancel
from .handlers.cleanup import handle_cleanup_orphans
from .handlers.list_jobs import handle_list_jobs
from .handlers.results import handle_results
from .handlers.start import handle_start
from .handlers.status import handle_status
from .jobs import JobStore
from .tools import (
    ReconCancelIn, ReconResultsIn, ReconStartIn, ReconStatusIn,
)

log = structlog.get_logger(__name__)


def _ok(data) -> list[types.TextContent]:
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    return [types.TextContent(type="text", text=json.dumps(data, indent=2, default=str))]


async def build_server() -> Server:
    cfg = load_config()
    store = JobStore(db_path=str(cfg.db_path))
    await store.init()
    do = DOClient(token=cfg.do_api_token)
    artifacts_root = Path(os.environ.get("RECON_ARTIFACTS_ROOT", "targets")).resolve()
    artifacts_root.mkdir(parents=True, exist_ok=True)

    # Best-effort orphan sweep on boot (don't block startup if DO is down)
    try:
        await handle_cleanup_orphans(store=store, do=do)
    except Exception as e:
        log.warning("orphan_sweep_failed", err=str(e))

    srv = Server("recon-mcp")

    @srv.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return [
            types.Tool(name="recon_start", description="Start a recon job over targets",
                       inputSchema=ReconStartIn.model_json_schema()),
            types.Tool(name="recon_status", description="Get a job's status",
                       inputSchema=ReconStatusIn.model_json_schema()),
            types.Tool(name="recon_results", description="Get the structured summary for a done job",
                       inputSchema=ReconResultsIn.model_json_schema()),
            types.Tool(name="recon_cancel", description="Cancel a job and destroy its droplets",
                       inputSchema=ReconCancelIn.model_json_schema()),
            types.Tool(name="recon_list_jobs", description="List recent jobs", inputSchema={"type":"object"}),
            types.Tool(name="recon_cleanup_orphans", description="Destroy orphaned recon-mcp droplets",
                       inputSchema={"type":"object"}),
        ]

    @srv.call_tool()
    async def _call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
        args = arguments or {}
        if name == "recon_start":
            return _ok(await handle_start(ReconStartIn(**args), store=store, cfg=cfg, artifacts_root=artifacts_root))
        if name == "recon_status":
            return _ok(await handle_status(ReconStatusIn(**args), store=store))
        if name == "recon_results":
            return _ok(await handle_results(ReconResultsIn(**args), store=store))
        if name == "recon_cancel":
            return _ok(await handle_cancel(ReconCancelIn(**args), store=store, do=do))
        if name == "recon_list_jobs":
            return _ok(await handle_list_jobs(store=store))
        if name == "recon_cleanup_orphans":
            return _ok(await handle_cleanup_orphans(store=store, do=do))
        raise ValueError(f"unknown tool: {name}")

    return srv


async def _main() -> None:
    srv = await build_server()
    async with stdio_server() as (r, w):
        await srv.run(r, w, srv.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_server.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add recon_mcp/server.py recon_mcp/tests/test_server.py
git commit -m "recon-mcp: stdio MCP server with six tools + boot orphan sweep"
```

---

### Task 18: Cloud-init copies runner scripts into the droplet

Currently `cloud_init.py` only embeds `bootstrap.sh`. The phase scripts must also be staged onto each droplet so `scanner.py` can call them via `/opt/recon/scripts/phase_*.sh`. Two options: embed them in cloud-init (one big user-data blob) or push via SFTP after provisioning. Push via SFTP keeps cloud-init small and avoids 16KB user-data limits.

**Files:**
- Modify: `recon_mcp/droplet.py:1-200`
- Modify: `recon_mcp/handlers/start.py:1-200`
- Test: `recon_mcp/tests/test_droplet.py` (add test for push_scripts)

- [ ] **Step 1: Add a failing test for `push_scripts`**

Append to `recon_mcp/tests/test_droplet.py`:

```python
@pytest.mark.asyncio
async def test_push_scripts_uploads_phase_scripts(monkeypatch, tmp_path):
    from recon_mcp.droplet import push_scripts
    d = MagicMock()
    d.push = AsyncMock()
    d.run = AsyncMock(return_value=(0, "", ""))
    await push_scripts(d)
    # one push per phase script
    pushed = [c.args[1] for c in d.push.await_args_list]
    assert any("phase_scan.sh" in p for p in pushed)
    assert any("phase_ferox.sh" in p for p in pushed)
    d.run.assert_any_await("chmod +x /opt/recon/scripts/*.sh", check=True)
```

- [ ] **Step 2: Run test, see failure**

Run: `cd recon_mcp && uv run pytest tests/test_droplet.py::test_push_scripts_uploads_phase_scripts -v`
Expected: ImportError on `push_scripts`.

- [ ] **Step 3: Implement `push_scripts` in droplet.py**

Append to `recon_mcp/droplet.py`:

```python
async def push_scripts(droplet: "Droplet") -> None:
    """Upload all phase scripts to /opt/recon/scripts and chmod them."""
    from pathlib import Path
    script_dir = Path(__file__).parent / "runner_scripts"
    await droplet.run("mkdir -p /opt/recon/scripts", check=True)
    for phase in ("scan", "subdomains", "resolve", "httpx", "ferox"):
        local = script_dir / f"phase_{phase}.sh"
        await droplet.push(str(local), f"/opt/recon/scripts/phase_{phase}.sh")
    await droplet.run("chmod +x /opt/recon/scripts/*.sh", check=True)
```

- [ ] **Step 4: Call `push_scripts` after provisioning in start.py**

In `recon_mcp/handlers/start.py`, modify the `with_provision` helper:

```python
async def with_provision(d: Droplet, purpose: str):
    await d.__aenter__()
    from ..droplet import push_scripts
    await push_scripts(d)
    await store.attach_droplet(job_id, droplet_id=d.droplet_id, region=d.region)
    return (d, purpose)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd recon_mcp && uv run pytest tests/test_droplet.py tests/test_handlers_start.py -v`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add recon_mcp/droplet.py recon_mcp/handlers/start.py recon_mcp/tests/test_droplet.py
git commit -m "recon-mcp: SFTP push phase scripts post-bootstrap"
```

---

### Task 19: Integration test — end-to-end with fully mocked DO + SSH

**Files:**
- Create: `recon_mcp/tests/test_integration.py`

Goal: a single test that exercises `handle_start` → background `_run_job` → eventual `JobStatus.DONE` with `summary.json` written, using mocks for DOClient and asyncssh.

- [ ] **Step 1: Write the integration test**

Create `recon_mcp/tests/test_integration.py`:

```python
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from recon_mcp.config import Config
from recon_mcp.jobs import JobStore, JobStatus
from recon_mcp.handlers.start import handle_start
from recon_mcp.tools import ReconStartIn


@pytest.mark.asyncio
async def test_end_to_end_smoke(tmp_path, monkeypatch):
    db = tmp_path / "j.sqlite"
    ssh = tmp_path / "ssh"
    cfg = Config(
        do_api_token="t", shodan_api_key=None, c99_api_key=None,
        db_path=db, ssh_key_dir=ssh,
        max_droplets_per_job=5, max_runtime_min=30,
        default_scan_region="nyc1", droplet_size="s-2vcpu-4gb",
    )
    store = JobStore(db_path=str(db))
    await store.init()

    # Patch DOClient methods
    fake_droplet_info = {"id": 1, "status": "active",
                        "networks": {"v4": [{"type": "public", "ip_address": "9.9.9.9"}]}}
    with patch("recon_mcp.handlers.start.DOClient") as DO, \
         patch("recon_mcp.handlers.start.Droplet") as DropCls, \
         patch("recon_mcp.handlers.start.subprocess.run") as subprun:
        subprun.return_value = MagicMock(returncode=0)
        (ssh).mkdir(parents=True, exist_ok=True)
        (ssh / "x.key.pub").write_text("ssh-ed25519 AAA== test")
        # Monkey: ssh-keygen pretends to write ssh dir; intercept the actual filenames
        monkeypatch.setattr(
            "recon_mcp.handlers.start._gen_ssh_keypair",
            lambda d, j: (d / f"{j}.key", "ssh-ed25519 AAA== test"),
        )

        do_inst = DO.return_value
        do_inst.create_ssh_key = AsyncMock(return_value={"id": 7})
        do_inst.delete_ssh_key = AsyncMock()
        do_inst.create_droplet = AsyncMock(return_value=fake_droplet_info)
        do_inst.get_droplet = AsyncMock(return_value=fake_droplet_info)
        do_inst.destroy_droplet = AsyncMock()

        drop_inst = DropCls.return_value
        drop_inst.droplet_id = 1
        drop_inst.region = "nyc1"
        drop_inst.__aenter__ = AsyncMock(return_value=drop_inst)
        drop_inst.__aexit__ = AsyncMock(return_value=None)
        drop_inst.run = AsyncMock(return_value=(0, "", ""))
        drop_inst.push = AsyncMock()
        drop_inst.pull = AsyncMock()

        out = await handle_start(
            ReconStartIn(targets=["1.2.3.4"], target_name="acme"),
            store=store, cfg=cfg, artifacts_root=tmp_path,
        )
        for _ in range(50):
            await asyncio.sleep(0.05)
            row = await store.get(out.job_id)
            if row["status"] in (JobStatus.DONE, JobStatus.FAILED):
                break
        assert row["status"] == JobStatus.DONE, row.get("error")
        # summary.json should be written
        sm = tmp_path / "acme" / "recon" / out.job_id / "summary.json"
        assert sm.exists()
```

- [ ] **Step 2: Run the integration test**

Run: `cd recon_mcp && uv run pytest tests/test_integration.py -v`
Expected: 1 passed.

- [ ] **Step 3: Commit**

```bash
git add recon_mcp/tests/test_integration.py
git commit -m "recon-mcp: integration smoke test (mocked DO + droplet)"
```

---

## Phase 7: wire-up, docs, skill

### Task 20: Register recon MCP in `.claude/settings.json`

**Files:**
- Modify: `.claude/settings.json`

- [ ] **Step 1: Add the `recon` MCP block**

In `.claude/settings.json`, under `mcpServers`, after the `caido` block, add:

```json
"recon": {
  "$comment": "DigitalOcean ephemeral-droplet recon MCP.",
  "command": "/Users/soural/Documents/TLX/bin/recon-mcp.sh",
  "args": []
}
```

- [ ] **Step 2: Add tool permissions to the `permissions.allow` list**

Add these strings to the `permissions.allow` array (alphabetical placement near other `mcp__tlx__` entries is fine):

```
"mcp__recon__recon_start",
"mcp__recon__recon_status",
"mcp__recon__recon_results",
"mcp__recon__recon_cancel",
"mcp__recon__recon_list_jobs",
"mcp__recon__recon_cleanup_orphans"
```

- [ ] **Step 3: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('.claude/settings.json'))"`
Expected: no output (valid JSON).

- [ ] **Step 4: Commit**

```bash
git add .claude/settings.json
git commit -m "recon-mcp: register MCP server + tool permissions"
```

---

### Task 21: Add a `recon` skill so Claude knows when to call the MCP

**Files:**
- Create: `.claude/skills/recon/SKILL.md`
- Modify: `skills.md`

- [ ] **Step 1: Write the skill**

Create `.claude/skills/recon/SKILL.md`:

```markdown
---
name: recon
description: Run the DigitalOcean ephemeral-droplet recon pipeline over a list of IPs, CIDRs, or wildcard domains. Use when target-init has produced http.md scope but recon (port scan, subdomain enum, httpx, feroxbuster) is missing. Spawns droplets, runs in parallel, tears down. Optional multi-region for geo-block detection.
---

# recon

Front-door for the `recon` MCP server.

## When to invoke

- New target where `targets/<name>/recon/` is empty.
- User asks for "recon", "port scan", "subdomain enum", "ferox" on a target.
- Multi-region geo check requested.

## Inputs (from `targets/<name>/http.md`)

Parse the scope section. Build a `targets` list:
- IPs and CIDRs go through verbatim.
- Wildcard apex domains become `*.<apex>`.
- Bare domains MUST be promoted to `*.<domain>` (the parser will refuse otherwise).

## How to call

```
recon_start({
  "targets": ["1.2.3.4", "10.0.0.0/24", "*.acme.io"],
  "target_name": "acme",
  "scan_region": "nyc1",
  "probe_regions": [],     # add e.g. ["fra1","sgp1"] for geo-block detection
  "max_droplets": 10
})
```

Poll with `recon_status({"job_id": ...})` every 30–60 s until `status == "done"` or `"failed"`.
Then `recon_results({"job_id": ...})` for the structured summary.
Persist into `targets/<name>/status.json.recon = {job_id, summary_path, finished_at}`.

## Hard rules

- Never start a recon job whose `targets` include hosts outside `targets/<name>/http.md` scope.
- Confirm with the user before `probe_regions` longer than 3 (cost).
- If `recon_cancel` is invoked, also verify droplet count is 0 via `recon_list_jobs`.

## Failure handling

- `status == "failed"` → inspect `error`; surface to user; do not retry automatically.
- Stuck `running` past `RECON_MAX_RUNTIME_MIN` → call `recon_cancel`, surface, suggest splitting CIDR.
```

- [ ] **Step 2: Add a line to skills.md (project skill index)**

In `skills.md`, append under the existing skill list:

```
| recon | DO ephemeral-droplet recon (port scan, subdomains, httpx, ferox). Multi-region optional. | recon |
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/recon/SKILL.md skills.md
git commit -m "recon-mcp: add recon skill so Claude routes scope→recon_start"
```

---

### Task 22: Cron-friendly orphan sweep script

**Files:**
- Create: `bin/recon-orphan-sweep.sh`

- [ ] **Step 1: Create the sweep script**

Create `bin/recon-orphan-sweep.sh`:

```bash
#!/usr/bin/env bash
# Cron entry: every 15 min run cleanup_orphans against the recon MCP.
# This kills droplets that escaped a crashed MCP process — runaway cost protection.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$HOME/.config/claude/.env" ] && set -a && . "$HOME/.config/claude/.env" && set +a
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
cd "$ROOT"
uv run --project recon_mcp python -c '
import asyncio
from recon_mcp.config import load_config
from recon_mcp.do_client import DOClient
from recon_mcp.jobs import JobStore
from recon_mcp.handlers.cleanup import handle_cleanup_orphans

async def main():
    cfg = load_config()
    store = JobStore(db_path=str(cfg.db_path))
    await store.init()
    do = DOClient(token=cfg.do_api_token)
    out = await handle_cleanup_orphans(store=store, do=do)
    print("destroyed:", out.destroyed)

asyncio.run(main())
'
```

Make executable: `chmod +x bin/recon-orphan-sweep.sh`

Suggested crontab entry (not auto-installed; document for user):

```
*/15 * * * * /Users/soural/Documents/TLX/bin/recon-orphan-sweep.sh >> /tmp/recon-sweep.log 2>&1
```

- [ ] **Step 2: Commit**

```bash
git add bin/recon-orphan-sweep.sh
git commit -m "recon-mcp: cron-friendly orphan sweep script"
```

---

### Task 23: Final full-suite green run + README

**Files:**
- Create: `recon_mcp/README.md`

- [ ] **Step 1: Run the full test suite**

Run: `cd recon_mcp && uv run pytest -v`
Expected: all tests pass.

- [ ] **Step 2: Write a short README**

Create `recon_mcp/README.md`:

```markdown
# recon-mcp

Stdio MCP server that runs ephemeral DigitalOcean recon droplets.

## Tools

- `recon_start({targets, target_name, scan_region?, probe_regions?, max_droplets?})`
- `recon_status({job_id})`
- `recon_results({job_id})`
- `recon_cancel({job_id})`
- `recon_list_jobs({})`
- `recon_cleanup_orphans({})`

## Env

| Var | Default | Required |
| --- | --- | --- |
| `DO_API_TOKEN` | — | yes |
| `SHODAN_API_KEY` | — | no (shodan phase skipped if unset) |
| `C99_API_KEY` | — | no (c99 phase skipped if unset) |
| `RECON_DB_PATH` | `.recon/jobs.sqlite` | no |
| `RECON_SSH_KEY_DIR` | `.recon/ssh` | no |
| `RECON_MAX_DROPLETS_PER_JOB` | 10 | no |
| `RECON_MAX_RUNTIME_MIN` | 180 | no |
| `RECON_DEFAULT_SCAN_REGION` | nyc1 | no |
| `RECON_DROPLET_SIZE` | s-2vcpu-4gb | no |

## Pipeline

For each target:

| kind     | phases run                                                  |
|----------|-------------------------------------------------------------|
| IP       | scan → subdomains → resolve → httpx → ferox                 |
| CIDR     | scan → subdomains → resolve → httpx → ferox                 |
| wildcard | subdomains → resolve → httpx → ferox  (scan skipped)        |

Phases run sequentially per droplet but droplets run in parallel across regions and across targets. The scan-region droplet handles the heavyweight masscan; probe-region droplets duplicate the httpx + ferox phases for geo comparison.

## Costs

s-2vcpu-4gb ≈ $0.036/h. A 90-min job = $0.054 per droplet. Five regions × 90 min ≈ $0.27. Orphan sweep cron (`bin/recon-orphan-sweep.sh`) kills runaways every 15 min.

## Safety

- CIDRs > /15 (≥131k hosts) refused.
- > 100 targets per job refused.
- Every droplet tagged `recon-mcp` + `job:<id>`.
- Cancel destroys every tagged droplet attached to the job.
- Cleanup-orphans destroys every tagged droplet whose owning job is terminal or unknown.
```

- [ ] **Step 3: Commit**

```bash
git add recon_mcp/README.md
git commit -m "recon-mcp: README"
```

---

## Self-Review Checklist (filled in)

**1. Spec coverage:**

| Requirement | Task |
|-------------|------|
| New MCP tool for DO recon | Tasks 0, 17, 20 |
| Accept IP list / CIDR / wildcard | Task 1 (parser) |
| Spin up droplet | Tasks 5–7, 13 |
| Run `dig` for DNS + PTR | Task 9 (`phase_scan.sh`) |
| Shodan reverse lookup | Task 9 (`phase_scan.sh`, gated by SHODAN_API_KEY) |
| `nslookup` reverse DNS | Task 9 (`phase_scan.sh`) |
| masscan top 10k then rest | Task 9 (`phase_scan.sh`) |
| Gather main domains from IP resolving | Tasks 9–11 (PTR + shodan hostnames feed subdomain enum) |
| Reverse-IP subdomain enum | Task 9 (`phase_subdomains.sh`, hackertarget) |
| amass | Task 9 (`phase_subdomains.sh`) |
| subfinder | Task 9 (`phase_subdomains.sh`) |
| subdomainfinder.c99.nl | Task 9 (`phase_subdomains.sh`, c99 API) |
| Re-resolve subs → find missed IPs | Task 9 (`phase_resolve.sh`) |
| Same flow for CIDR | Task 1 normalizes; Task 9 scripts accept CIDR via `masscan -iL` |
| Wildcard-only: subdomain enum only | Task 10 `_phases_for(WILDCARD)` |
| httpx over everything | Task 9 (`phase_httpx.sh`) |
| feroxbuster + seclists raft-large | Task 9 (`phase_ferox.sh`) |
| Destroy droplet after | Tasks 7 (`__aexit__`), 13 (finally block), 22 (orphan sweep) |
| Multi-country probe option | Tasks 2, 12 (`probe_regions`), 13 (`_droplet_plan`), 21 (skill doc) |
| Parallel for many targets | Task 13 (`asyncio.gather` over droplets); per-droplet sequential per target |

**2. Placeholder scan:** None of "TBD", "add error handling", "similar to Task N", "implement later" appear in step bodies. Every code step shows the full code.

**3. Type consistency:**
- `Target`, `TargetKind` → consistent across input_parser, safety, scanner.
- `JobStatus` enum values referenced everywhere as `JobStatus.<VAL>`; never as raw strings except inside SQL.
- `Droplet.droplet_id`, `.ip`, `.region`, `.ssh_private_key_path` referenced consistently in droplet.py, scanner.py, start.py.
- Handler functions are all `async def handle_<verb>(inp, *, store, ...) -> ReconXxxOut` — same pattern across the six tools.
- Cloud-init writes `bootstrap.done` sentinel under `/var/lib/recon/`; droplet `_wait_bootstrap` polls the same path.
- Phase script directory `/opt/recon/scripts` is set in bootstrap, push_scripts, and scanner.

No drift found.
