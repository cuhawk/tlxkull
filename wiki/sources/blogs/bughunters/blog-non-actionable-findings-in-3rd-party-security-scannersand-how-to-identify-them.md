---
source: bughunters
source_url: https://bughunters.google.com/blog/non-actionable-findings-in-3rd-party-security-scannersand-how-to-identify-them
title: "Non-Actionable Findings in 3rd-party Security Scanners...and How to Identify Them - Google Bug Hunters"
description: "False positive are a recurring issue when working with external scanning tools. This blog post discusses the most common types of false positives the AutoVM team at Google has observed in this context and provides instructions on how to identify them."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/non-actionable-findings-in-3rd-party-security-scannersand-how-to-identify-them#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Non-Actionable Findings in 3rd-party Security Scanners...and How to Identify Them

![](https://storage.googleapis.com/bughunters-article-images/blogs/erikvarga.jpg)

Erik Varga

Software Engineer

Published: Sep 16, 2024

Security Engineering  Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Non-Actionable Findings in 3rd-party Security Scanners...and How to Identify Them

Dependency scanners report vulnerabilities by identifying software packages
installed on hosts and then checking (public or private) vulnerability feeds to
see if these packages are affected by known vulnerabilities. The AutoVM team at
Google has found that 3rd-party dependency scanning tools often report
vulnerabilities that are either false positives or that we don't consider
security relevant or actionable.

This blog post lists the most common types of false positives we discovered
during our analysis of external scanning tools and provides instructions on how
to identify if a reported vulnerability is a false positive belonging to one of
these categories. The aim of this post is to help security researchers determine
whether findings reported in Google products (e.g. public images) by external
dependency scanners are actually security relevant.

## Non-actionable findings

The majority of false positives reported by external scanners can be grouped
into one of four main categories.

### Vulnerability rejected by feed

NVD- or OS-specific feeds might withdraw or reject a previously submitted CVE
entry if later analysis reveals the finding to not be security relevant or
submitted by mistake (for example:
[CVE-2023-4881](https://nvd.nist.gov/vuln/detail/CVE-2023-4881)).

Sometimes NVD can consider a finding security relevant while OS feed maintainers
decide it's of minimal severity and, in consequence, don't provide any patches
for their Linux distro. In such cases the details from the OS feed can be
considered more accurate and the findings can be classified as false positives
(for example: [CVE-2018-20657](https://ubuntu.com/security/CVE-2018-20657)).

**How to identify:** Look at the vulnerability description in NVD and in
vulnerability description pages specific to the OS on which the vulnerability
was found. Check if the vulnerability has been withdrawn or deprioritized.

### Imprecise version matching information

Scanners often use vulnerability feeds that report version ranges which are too
broad for the context in which the vulnerability was found. This usually happens
when matching is done using the generic NVD feed – feeds specific to the host OS
have more info about a vulnerability’s applicability or internal patches. These
kinds of false positives usually fall into one of the following categories:

#### Custom OS patches

Linux distro maintainers sometimes create OS-specific patch releases to fix
vulnerabilities in a given package and assign a custom version number to the
patched package. If a scanner uses more generic vulnerability feeds like NVD as
the source for vulnerabilities, it might consider a patched package to still be
vulnerable and thus report a false positive.

Example: [CVE-2020-14422](https://nvd.nist.gov/vuln/detail/cve-2020-14422) lists
Python version `3.6.10` as vulnerable, but Ubuntu
[released](https://ubuntu.com/security/CVE-2020-14422) a patch for it with the
custom version `3.6.9-1~18.04ubuntu1.1`. External scanners that scan an Ubuntu
host and use NVD instead of the Ubuntu-specific vulnerability feed will
mistakenly consider the patched Python version to be vulnerable.

**How to identify:** Look at the vulnerable version ranges in NVD and in the
vulnerability’s description page specific to the host OS. If NVD marks the
package version as vulnerable but the OS feed has a patch at that version, the
vulnerability has been patched by the OS and this finding is a false positive.

#### No vulnerability for given OS configuration

Distro-specific vulnerability feeds might have additional information about
certain vulnerabilities not being applicable to their distros even if the
package is installed and is in the vulnerable version range according to more
generic feeds.

Example: [CVE-2023-52426](https://ubuntu.com/security/CVE-2023-52426) is only
applicable if the package in question is compiled with certain flags enabled.
Ubuntu Focal doesn't enable those flags, so the vulnerability is not applicable
on Focal hosts. If a scanner uses the NVD feed to retrieve vulnerability range
information, it would mistakenly mark the package on Focal hosts as vulnerable.

**How to identify:** Look at the finding's entry in NVD and on the OS-specific
vulnerability page. If NVD marks the package as vulnerable but the OS feed
doesn't, this is a false positive. On Ubuntu, the
[classifications](https://git.launchpad.net/ubuntu-cve-tracker/tree/README#n299)
"`not vulnerable`", "`deferred`", "`does not exist`", or "`ignored`" usually mean that
the vulnerability is not present or does not pose a security risk.

#### Incomplete version info in NVD or in OS feed

New CVEs are not always properly analyzed before they're added to public
vulnerability feeds, leading to scanners ingesting incomplete or missing version
range info. A scanner that uses incomplete version data for a CVE might decide
to overreport and mark any package version vulnerable to the CVE, causing
potential false positives.

Example: The Ubuntu Focal feed for
[CVE-2022-3857](https://ubuntu.com/security/CVE-2022-3857) marks all versions of
the `libpng1.6` package as vulnerable. The CVE's
[NVD page](https://nvd.nist.gov/vuln/detail/CVE-2022-3857) has been updated
slightly more recently and includes a proper vulnerability version range. If a
scanner analyzes a package outside of this version range and uses the Ubuntu
Focal-specific feed, it would mistakenly report the package as vulnerable.

**How to identify:** Check the NVD and the OS-specific entries for the
vulnerability in question. If one feed has no vulnerability range (or marks all
packages as vulnerable) and the other feed has a vulnerability range that the
found package doesn't fall into, then this is a false positive reported by the
scanner.

### Imprecise information about affected packages

A lot of OS-specific vulnerability feeds such as the Debian feed report
vulnerabilities on source packages only. When determining if a binary package is
affected by the given vulnerability, scanners often just look at the source
package the binary is derived from, even though the binary package might not
actually have any of the vulnerable libraries installed.

Example:
[CVE-2024-6387](https://security-tracker.debian.org/tracker/CVE-2024-6387) only
affects OpenSSH servers, but Debian's vulnerability feed reports the source
package "openssh" as vulnerable. The binary packages "openssh-server" and
"openssh-client" both derive from this source package, thus a system that only
has “openssh-client” installed will be marked as vulnerable even though it
doesn't use any of the vulnerable libraries.

Other examples include binary packages that don't include any code from the
source file (e.g. a
[multiarch-support](https://packages.debian.org/sid/amd64/chromium-common/filelist)
binary package which might be marked as vulnerable to a
[CVE](https://security-tracker.debian.org/tracker/CVE-2015-8982) in glibc).

**How to identify:** Look at the vulnerability entry for the vulnerability in
question and identify the specific piece of software that's vulnerable. Check
the files installed by the package that was reported as vulnerable and see if it
actually includes any of the problematic libraries.

### Finding is not security relevant

Some scanners ingest and report supplementary advisory information on top of
CVE/GHSA entries that may not always have any security relevance. For example,
Trivy reports Debian Long Term Support Security Advisories (DLAs) such as
[time zone data updates](https://lists.debian.org/debian-lts-announce/2023/03/msg00020.html)
or
[new GPG key additions](https://lists.debian.org/debian-lts-announce/2023/07/msg00004.html).
Failing to apply these updates doesn't actually pose any security risks.

**How to identify:** If a finding doesn't have a CVE or GHSA, or any other
common vulnerability identifier associated, look up the finding details on its
description page. If the recommended updates don't actually fix any security
issue then this scanner report is not security relevant.

## Conclusion

As can be seen from the examples in this post, the findings of dependency
scanners should be taken with a grain of salt as there are many factors that can
influence whether a given vulnerability in a software package is applicable to
the system being scanned. We hope the tips shared here will help you distinguish
false positives from the real thing when using external scanners, and in turn
improve the quality (and rewards) of the vulnerability reports you submit to
Google's VRPs. Happy bug hunting!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab