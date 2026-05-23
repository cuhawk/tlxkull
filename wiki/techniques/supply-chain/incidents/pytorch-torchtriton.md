---
title: PyTorch torchtriton dependency confusion (Dec 2022)
slug: pytorch-torchtriton
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, language/python, registry/pypi, technique/dependency-confusion, exfil/dns-tunnel]
inbound: []
---

# PyTorch torchtriton dependency confusion (Dec 2022)

## What happened

Between **25 and 30 December 2022** anyone who installed the PyTorch
**nightly** wheel pulled in a malicious `torchtriton` from PyPI instead
of the legitimate package from PyTorch's private index
`download.pytorch.org/whl/nightly`. The PyTorch team had used the
unclaimed name `torchtriton` on their private index without also
squatting it on public PyPI; on 25 Dec 2022 someone uploaded a wheel
with the same name and a higher version number to PyPI. Because `pip`
resolves the highest visible version across **all** configured indexes
and PyTorch's install instructions added PyPI as a fallback, the
malicious wheel won.

The wheel shipped a binary `triton` placed at
`site-packages/triton/runtime/triton`. On import it harvested
hostname, IP, username, current working directory, the contents of
`/etc/passwd`, `/etc/hosts`, `~/.gitconfig`, `~/.ssh/*` (id_rsa,
id_rsa.pub, known_hosts), the first 1000 files in `$HOME`, and
exfiltrated everything via **DNS A-record queries** to `*.h4ck.cfd` via
the `wheezy.io` nameserver (chunked, base64-encoded labels). The
PyTorch stable channel was never affected -- only nightlies. PyTorch
rotated the package name to `pytorch-triton` and PyPI swapped the
malicious record for a benign placeholder.

## Attack chain

1. **Find a private-index package name that's not registered on the
   public index.** PyTorch nightly's install instructions added PyPI as
   `--extra-index-url`. `torchtriton` existed only on the PyTorch
   index. Public PyPI namespace was open.
2. **Publish a higher-version wheel with the same name.** `pip` default
   resolver picks the highest version across all configured indexes;
   public PyPI's `1.0.0+ahackers-version` beat the private nightly tag.
3. **Hide the payload in a binary, not Python source.** Python wheel
   ships an ELF named `triton`; the wheel's `__init__.py` invokes it on
   first import. Bypasses casual `grep` over `*.py` and most static
   scanners that only flag Python source.
4. **DNS-tunnel exfil.** Each harvested file is base64'd, chunked into
   sub-63-byte labels, queried as `<chunk>.<file-id>.h4ck.cfd`. The
   attacker controls `wheezy.io` authoritative DNS and parses queries
   from `tcpdump`. Survives outbound HTTP firewalls.
5. **High-value harvest.** SSH keys + git config + first ~1000 home-dir
   files lifted from a single ML researcher's laptop typically yields
   GitHub PATs, AWS keys, Hugging Face tokens, OpenAI keys, internal
   cluster SSH access.

## Lessons for bug hunters

- **Audit every `--extra-index-url` and `--index-url` in your target's
  `Dockerfile`, `pyproject.toml`, `requirements*.txt`, CI YAML.** Any
  private package name not also registered on PyPI / npm public is a
  free supply-chain primitive. Same applies to `npm config registry`
  fallbacks and `~/.gemrc` source order. See [[ultralytics-pypi]] and
  [[ctx-pypi]] for adjacent classes.
- **Pin by hash, not version.** `pip install --require-hashes`
  defeats this entirely because the public-PyPI wheel hash won't match
  the lockfile entry.
- **Dependency confusion still pays out.** Original Birsan writeup is
  from 2021 but ML / AI startups in particular ship internal libs whose
  names leak via Sentry stack traces, GitHub Actions logs, public Slack
  archives, and dependency graphs of OSS forks.
- **DNS exfil is the canonical "egress-restricted" bypass.** When a
  target's CI runner blocks outbound HTTP but allows DNS resolution,
  base64-into-A-record-queries works. Detecting it requires DNS query
  inspection, which most blue teams don't run.
- **Binary-in-Python-wheel pattern.** Any wheel with a non-pure-Python
  payload (`*.so`, ELF, Mach-O) deserves a closer look -- `unzip` and
  `file` are enough for a first triage. The Sonatype / Reversinglabs
  feeds flag these but most teams don't subscribe.

## Primary sources

- [PyTorch official disclosure: "Compromised PyTorch-nightly dependency chain between December 25th and December 30th, 2022"](https://pytorch.org/blog/compromised-nightly-dependency/)
- [Wiz Research: "Malicious PyTorch dependency 'torchtriton' on PyPI: everything you need to know"](https://www.wiz.io/blog/malicious-pytorch-dependency-torchtriton-on-pypi-everything-you-need-to-know)

## Related

- [[ctx-pypi]]
- [[ultralytics-pypi]]
- [[xz-utils-cve-2024-3094]]
