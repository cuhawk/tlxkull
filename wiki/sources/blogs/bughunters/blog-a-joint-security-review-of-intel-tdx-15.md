---
source: bughunters
source_url: https://bughunters.google.com/blog/a-joint-security-review-of-intel-tdx-15
title: "Strengthening the Foundation: A Joint Security Review of Intel TDX 1.5 - Google Bug Hunters"
description: "This blog post details the results of the joint security review of the Intel Trust Domain Extensions (TDX) 1.5 Google performed together with Intel."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/a-joint-security-review-of-intel-tdx-15#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Strengthening the Foundation: A Joint Security Review of Intel TDX 1.5

![](https://storage.googleapis.com/bughunters-article-images/blogs/swidowski.jpg)

Kirk Swidowski

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/danielmm.jpg)

Daniel Moghimi

Senior Research Scientist

![](https://storage.googleapis.com/bughunters-article-images/blogs/josheads.jpg)

Josh Eads

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/erdemaktas.jpg)

Erdem Aktas

Staff Software Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/jiaxma.jpg)

Jia Ma

Software Engineering Manager

Published: Feb 10, 2026

Product Security Engineering  Cloud Vulnerability Research  Cloud CISO  Google Cloud

[RSS Feed](https://bughunters.google.com/feed/en)

# Strengthening the Foundation: A Joint Security Review of Intel TDX 1.5

Today, in coordination with Intel’s
[security advisory](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-01397.html)
and
[blog post](https://www.intel.com/content/www/us/en/security/security-practices/blogs/google-collaboration-strengthen-intel-tdx.html),
we published the results of our joint security review of the Intel Trust Domain
Extensions (TDX) 1.5. We identified five vulnerabilities, which Intel has
remediated, and 35 other bugs, weaknesses, and improvement suggestions.

Our research extends Google’s
[previous review](https://googleprojectzero.blogspot.com/2023/04/technical-report-into-intel-tdx.html)
by covering major changes since Intel TDX 1.0, and it contributes to broader
community efforts to secure critical components in the confidential computing
space
( [1](https://www.intel.com/content/dam/www/public/us/en/security-advisory/documents/intel_tdx_joint_security_review_with_microsoft.pdf),
[2](https://www.usenix.org/system/files/usenixsecurity25-rauscher.pdf),
[3](https://dl.acm.org/doi/pdf/10.1145/3658644.3690230),
[4](https://cispa.de/news/2026/stackwarp-final.pdf),
[5](https://heracles-attack.github.io/Heracles-CCS2025.pdf),
[6](https://arxiv.org/pdf/2307.14757), [7](https://arxiv.org/abs/2506.15924)).

While confidential computing aims to minimize the **Trusted Computing Base**
**(TCB)**, the integrity of that TCB requires rigorous validation. In a perfect
world, the TCB would be bug-free; in reality, the complexity of modern systems
makes continuous assessment essential. Collaborative reviews allow industry
leaders to proactively fix vulnerabilities while fostering transparency for
everyone who relies on the technology. Furthermore, when remediation is required
a robust technology enables timely updates, minimizes disruption, and customers
are able to attest to the changes once confirmed to meet their security policy.

Our partnership with Intel’s
[INT31](https://www.intel.com/content/www/us/en/security/security-practices/int31.html)
Security Research team during this review enabled us to quickly ramp up on
changes, validate understanding, report bugs in real-time, and validate
remediations.

## The Background

**Confidential Virtual Machines (CVMs)**, such as those enabled by Intel TDX are
essential for advancing modern security and privacy services because they offer
a hardware-enforced Trusted Execution Environment (TEE). This ensures that
sensitive data and code remain isolated even during execution.

The introduction of **TDX version 1.5** brings significant new features like
**Live Migration** and **Trust Domain (TD) Partitioning** (through nested VMs),
which inherently expand the Trusted Computing Base (TCB) for TDX.This expansion
is evidenced by the addition of 34,862 lines of code to the TDX module firmware,
including over 8,000 lines associated with migration metadata and state
management. We conducted this assessment at a critical time, spanning spring to
fall 2025, after TDX 1.5 was publicly released but before it was widely adopted
by Cloud Service Providers.

We focused on a **thorough API review** of changes since TDX 1.0, augmenting it
with **static analysis** tools and the development of **TDXplore**–a bespoke
Python-based experimentation framework to explore complex flows and edge cases.
We leveraged Gemini 2.5 Pro and NotebookLM to navigate technical specifications
and aid with analysis.

## Outcome

This effort resulted in the identification and subsequent remediation of
multiple vulnerabilities and bugs. We also recommended several code changes,
defense-in depth measures, and architectural improvements, such as **Attestable**
**Global Feature Disablement**, which if implemented would limit attack surface
growth by allowing a host to enable only used features and interfaces during TDX
Module initialization.

Most significantly, our research uncovered **one vulnerability** that would have
allowed an **untrusted operator to completely compromise the security guarantees**
**of TDX**.

Specifically, [CVE-2025-30513](https://nvd.nist.gov/vuln/detail/CVE-2025-30513)
is capable of converting a migratable TD to a debuggable TD during the migration
process. A host can **exploit a Time-of-Check to Time-of-Use vulnerability** to
change the TD’s `attributes` from `migratable` to `debug` as its immutable state
is being imported. **Once triggered the entire decrypted TD state is**
**accessible** from the host. At this point a **malicious host could construct**
**another TD with the decrypted state or perform live monitoring activities**.
Because a migration can occur at any point during the TD lifecycle, this attack
can be performed after a TD has completed attestation, ensuring secret material
is present in its state.

This vulnerability was uncovered toward the end of our research effort,
following extensive static analysis and the development of the TDXplore toolkit.
It was the result of our API audit, which provided the necessary context to
identify a flaw in the TDX Module’s TD lifecycle management. We observed a
critical disconnect between how the TD `op_state` Finite State Machine (FSM) was
tracked, how import activities could be interrupted, and how TD state is
modified but not reverted when failures are encountered.

## Working with Intel

The collaborative framework between Intel and Google was agreed upon prior to
the project and drew on our previous history of engagement. We utilized a shared
issue tracking platform as a centralized hub for reporting findings and
conducting technical Q&A, with weekly synchronization meetings to discuss
progress. This frequent contact ensured that findings were reported quickly and
technical questions could be addressed by Intel engineers with domain knowledge.
Publicly accessible source code, architectural documentation, and a production
TDX module were used for research and development.

At the end of the project Intel promptly assigned CVEs, and we worked with them
to develop a responsible disclosure timeline. To address the identified
vulnerabilities and bugs, the TDX module needed to be updated, which is highly
disruptive to production environments that don't fully support TD Preservation
and Live Migration. New TDX Modules were made available within the typical
90-day public disclosure period but customers needed time to test, qualify, and
safely roll out the fix to their infrastructure, which pushed the public
disclosure deadline to about 180 days. Lastly, some of the identified items
(less critical bug fixes and some security weaknesses) are not included in the
February 2026 release but are expected to be addressed in subsequent releases.

## Conclusion

This research illustrates why it is critically important that leaders in the
Confidential Compute (CC) industry continually perform security reviews. Intel
TDX 1.5 introduces new features and functionality that bring confidential
computing significantly closer to feature parity with traditional virtualization
solutions. At the same time these features have increased the complexity of a
highly privileged software component in the TCB.

Community involvement in security assessments and research builds expertise in
the ecosystem. To this end we are contributing back to the community through the
release of the technical
[white paper](https://services.google.com/fh/files/misc/intel_tdx_1.5-full_report.pdf)
discussing the findings of our security review, the exploration toolkit
[source code](https://github.com/google/security-research/tree/master/pocs/cpus/tdxplore),
and proof-of-concept
[exploits](https://github.com/google/security-research/tree/master/pocs/cpus/tdxploits)
for two of the disclosed vulnerabilities. We have also written a
[blog post](https://security.googlecloudcommunity.com/community-blog-42/beyond-confidential-establishing-trust-in-your-computing-environment-6290)
discussing the importance of attestation and how reports can be used to check
attributes associated with a CVM.

Lastly, we appreciate the continued engagement with Intel and would like to
thank the following Intel engineers for their collaboration during this review:
Uri Bear, Dror Caspi, Stephen Haruna, Simon Johnson, Nagaraju Kodalapura, Alon
Levi, Dhinesh Manoharan, Avishai Redelman, Bernie Reeber, Fahimeh Rezaei, Boaz
Tamir, and Jonathan Valamehr.

## References

- [Security Assessment of Intel TDX with Support for Live Migration](https://services.google.com/fh/files/misc/intel_tdx_1.5-full_report.pdf)
– 2026 Google White paper
- [Safeguarding Foundational Technologies: How Intel and Google Collaborate to\\
Strengthen Intel®\\
TDX](https://www.intel.com/content/www/us/en/security/security-practices/blogs/google-collaboration-strengthen-intel-tdx.html)
– Intel Blog post
- [Beyond Confidential: Establishing Trust in Your Computing Environment](https://security.googlecloudcommunity.com/community-blog-42/beyond-confidential-establishing-trust-in-your-computing-environment-6290)
– Google Cloud Security Community blog post
- [Intel® Product Security Center Advisory](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-01397.html)
- [Google Confidential Compute Security Bulletin](https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/security-bulletins)
- [TDXplore GitHub](https://github.com/google/security-research/tree/master/pocs/cpus/tdxplore)
– Toolkit Source code
- [TDXploits GitHub](https://github.com/google/security-research/tree/master/pocs/cpus/tdxploits)
– Exploit Source code

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab