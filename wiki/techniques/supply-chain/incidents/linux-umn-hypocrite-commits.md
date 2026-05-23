---
title: UMN "Hypocrite Commits" Linux kernel research (Apr 2021)
slug: linux-umn-hypocrite-commits
created_utc: 2026-05-22T00:00:00Z
updated_utc: 2026-05-22T00:00:00Z
tags: [incident/supply-chain, project/linux-kernel, technique/social-engineering, technique/review-bypass, ecosystem/oss]
inbound: []
---

# UMN "Hypocrite Commits" Linux kernel research (Apr 2021)

## What happened

In **2020 and early 2021**, PhD student **Qiushi Wu** and assistant
professor **Kangjie Lu** at the University of Minnesota ran a research
project titled *"On the Feasibility of Stealthily Introducing
Vulnerabilities in Open-Source Software via Hypocrite Commits"*. They
deliberately submitted patches to the Linux kernel whose stated fixes
masked the introduction of new use-after-free / double-free / NULL-deref
bugs. The paper claimed three such patches were accepted into the kernel
tree as a proof of concept.

In **April 2021** a follow-on patch from the same lab triggered a
review push-back from senior maintainer **Al Viro**, after which
**Greg Kroah-Hartman** publicly banned all `@umn.edu` contributions and
**reverted 190+ historical commits** from the lab for re-review. The
incident exposed that the kernel review process -- relying on
maintainer attention and Reviewed-by tags -- was structurally
vulnerable to *good-faith-shaped* malicious patches, and that academic
ethics review (the lab's IRB approval) had blessed an experiment that
treated kernel maintainers as non-consenting research subjects.

## Attack chain

1. **Hypocrite patch primitive.** Submit a patch that fixes a real
   minor bug *but* introduces a new latent bug as a side effect --
   e.g. plugs a `goto` cleanup path while creating a UAF in the
   non-error path. Reviewer scans the stated fix, misses the new bug.
2. **Cover from churn.** Trivial driver/staging cleanups
   (`mwifiex`, `rsi`, `qlogic`, etc.) are reviewed by drive-by
   maintainers with limited bandwidth; bugs introduced in such patches
   typically take months to surface and are blamed on the original
   driver, not the patch author.
3. **Volume produces accidental authority.** Over 200 commits across
   2018-2021 built a contributor reputation for the UMN lab.
   Reviewers extended baseline trust to subsequent patches based on
   that history, lowering scrutiny per patch -- the same dynamic
   "Jia Tan" later weaponised in [[xz-utils-cve-2024-3094]].
4. **Detection by senior review push-back.** Viro questioned a 2021
   patch as "a fix that does not fix anything"; the lab's published
   paper made the original intent searchable, and Kroah-Hartman
   connected the patch to the experiment.
5. **Mass-revert remediation.** GKH ripped 190+ commits and required
   per-commit re-review by independent maintainers before
   reinstatement. UMN issued a public statement, suspended the line of
   research, and the paper was retracted from IEEE S&P 2021.

## Lessons for bug hunters

- **Patches that "fix" something can be the vuln introduction.** When
  triaging a possible CVE, do not assume the commit that introduced the
  bug is labelled as a feature commit. Search `git log --all -G<sink>`
  not just by commit subject. The hypocrite primitive works against any
  large OSS project: kernel, browser engines, OpenSSL, sudo. Same
  pattern as [[php-git-backdoor]] (commit framed as "Fix Typo").
- **Reviewer-fatigue clusters are exploitable.** Subsystems with one
  active maintainer reviewing >50 patches/week are reachable. On any
  in-scope OSS bug-bounty target, identify the lowest-attention
  subsystems via `git shortlog -ns` and weight your audit there --
  that is where the latent vulns hide.
- **University and corporate email domains are not trust roots.**
  GitHub Verified badges, `@umn.edu`, even GPG-signed commits do not
  imply benign intent. When reviewing a finding's history of patches,
  cluster by email *domain* and look for whole-domain anomalies (an
  organisation that suddenly submits 30 driver patches in a month).
- **Adjacent-function-gap is the audit primitive.** The opposite of
  hypocrite commits -- looking for a sibling function that *omits* a
  control its peers all call -- finds organic versions of the same
  class of bug. See `wiki/techniques/recon/adjacent-function-gap.md`
  and the `opus-gap-audit` skill.
- **IRB/legal cover does not bind your targets.** Some bug-bounty
  programs explicitly forbid "research-style" commits even from
  university researchers. Re-read the program brief before submitting
  any chain that involves contributing code upstream.

## Primary sources

- [Greg Kroah-Hartman's mass-revert mail (LKML, 2021-04-21)](https://lore.kernel.org/lkml/YH%2FfM%2FTsbmcZzwnX@kroah.com/)
  -- the ban announcement and the maintainer-side reasoning.
- [Qiushi Wu & Kangjie Lu, "On the Feasibility of Stealthily Introducing Vulnerabilities in Open-Source Software via Hypocrite Commits" (PDF, retracted)](https://www-users.cse.umn.edu/~kjlu/papers/full-disclosure.pdf)
  -- the original research paper describing the methodology.

## Related

- [[xz-utils-cve-2024-3094]]
- [[php-git-backdoor]]
