---
title: ua-parser-js account hijack (Oct 2021)
slug: ua-parser-js
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, registry/npm, technique/account-takeover, technique/postinstall-script, technique/cryptominer, technique/info-stealer]
inbound: []
---

# ua-parser-js account hijack (Oct 2021)

## What happened

On **2021-10-22** between 12:15 UTC and ~16:25 UTC an attacker who
had taken over the npm account of maintainer **Faisal Salman**
published three malicious releases of `ua-parser-js`: **0.7.29,
0.8.0, and 1.0.0**. Each release shipped a `preinstall.sh` /
`preinstall.bat` that fetched a second-stage binary at install time --
**XMRig** Monero cryptominer on Linux, and a Windows DLL identified
as either **Danabot** or a Danabot-class credential stealer (FTP,
VNC, browsers, mail clients) on Windows. The package had **~7-8
million weekly downloads** and was a transitive dep of Facebook,
Microsoft, Amazon, Apple infra components -- the affected install
base is on the order of tens of thousands of distinct organisations.
CISA issued a public alert recommending re-imaging affected hosts.

Faisal published a GitHub issue (#536 on faisalman/ua-parser-js)
confirming the takeover within hours, npm pulled the malicious
versions, and 0.7.30 / 0.8.1 / 1.0.1 (clean releases) were published
the same day. Root cause: credential reuse + no 2FA on the npm
account. This incident -- combined with the eslint-scope and
coa/rc incidents from the same period -- accelerated npm's
mandatory-2FA rollout for top-500-package maintainers.

## Attack chain

1. **Credential stuffing or password leak.** The maintainer's npm
   password was reused on another service and surfaced in a public
   breach corpus. 2FA was not enabled on the npm account.
2. **Three rapid releases.** Attacker pushed `0.7.29`, `0.8.0`, and
   `1.0.0` in quick succession to maximize coverage of consumers
   pinning to different majors (the package had both legacy 0.7.x
   and brand-new 1.x users).
3. **`preinstall` script as the dropper.** Both `preinstall.sh`
   (POSIX) and `preinstall.bat` (Windows) were shipped. On
   `npm install` -- which runs preinstall before any code is
   examined -- the script `curl`d a stage-2 from
   `citationsherbe.at` (Linux) or `159.148.186.228` (Windows).
4. **Linux: XMRig.** A standalone XMRig Monero miner was extracted
   to `/tmp/jsextension`, ran as the install user (frequently root
   in CI / Docker base images), and pointed at a private pool.
5. **Windows: Danabot-class stealer.** A DLL `create.dll` was
   loaded via `regsvr32.exe -s create.dll`. Cado Security linked
   the DLL infrastructure to prior Danabot campaigns; the malware
   harvested credentials from 50+ apps including FileZilla, WinSCP,
   Outlook, Thunderbird, Chrome, Firefox, Edge.
6. **Discovery.** A community user filed npm and GitHub issues
   within ~3 hours of publication. Faisal himself filed issue #536
   the same day, openly acknowledging the account compromise.

## Lessons for bug hunters

- **`preinstall` / `postinstall` is the canonical npm-malware
  primitive.** When auditing a target's CI logs (`npm install -d`,
  `--foreground-scripts`), look for any dep whose lifecycle scripts
  fetch external URLs. Bonus: many programs disallow `npm install`
  in production but their CI is unconstrained -- if you can compromise
  a low-popularity dep, you get CI-shell.
- **Maintainer-account 2FA gaps are still findable.** Until 2022
  any maintainer of a top-100 package was a high-value password-reuse
  target. Hunter habit: when reviewing a target's deps, identify
  single-maintainer packages and check whether the maintainer's
  email is in HIBP. Use only as evidence to push the target to pin
  by SHA or to vendor.
- **Architectures matter.** This payload was Linux-vs-Windows
  conditional; macOS noped out and ran nothing. When investigating
  a possibly-malicious dep, run the install under all three OS
  targets, not just the dev box.
- **CI = root + outbound + crypto.** XMRig running in CI containers
  is the most common in-the-wild npm-incident outcome. Programs
  that don't egress-filter their CI are out a chunk of compute
  budget for as long as the package is undetected. This is also
  the easiest IoC: a CPU-bound process named `jsextension` /
  `update.exe` in `/tmp` after a dep install.
- **Three majors at once.** Backporting the malicious payload to
  legacy 0.7.x AND publishing a new major (1.0.0 -- which had been
  WIP) is the attacker pattern -- they push to *every* dist-tag
  reachable. When responding to a takeover, audit dist-tags
  `latest`, `next`, `legacy`, and any custom tags the maintainer
  used.

## Primary sources

- [ua-parser-js issue #536: Security issue: compromised npm packages](https://github.com/faisalman/ua-parser-js/issues/536)
  -- Faisal's own disclosure thread, with version timing and
  community IoCs.
- [Rapid7: NPM Library (ua-parser-js) Hijacked -- What you need to know](https://www.rapid7.com/blog/post/2021/10/25/npm-library-ua-parser-js-hijacked-what-you-need-to-know/)
  -- technical writeup of the preinstall dropper, XMRig and Danabot
  payload analysis, and IoCs.

## Related

- [[event-stream-flatmap-stream]]
- [[eslint-scope]]
- [[maintainer-domain-takeover]]
- [[ledger-connect-kit]]
