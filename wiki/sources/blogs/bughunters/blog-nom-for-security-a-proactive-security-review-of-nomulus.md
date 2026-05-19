---
source: bughunters
source_url: https://bughunters.google.com/blog/nom-for-security-a-proactive-security-review-of-nomulus
title: "Nom for Security: A Proactive Security Review of Nomulus - Google Bug Hunters"
description: "Curious to understand what our team looks for when reviewing product security? Read on to find out more about how we conducted our review of Nomulus, and the issues we discovered."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/nom-for-security-a-proactive-security-review-of-nomulus#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Nom for Security: A Proactive Security Review of Nomulus

![](https://storage.googleapis.com/bughunters-article-images/blogs/serb.jpg)

Sam Erb

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/jtaft.jpg)

Justin Taft

Information Security Engineer

Published: Feb 20, 2024

Security Engineering

[RSS Feed](https://bughunters.google.com/feed/en)

# Nom for Security: A Proactive Security Review of Nomulus

As part of our goal to keep Google/Alphabet products secure and our users safe,
our Information Security Engineering (ISE) team will proactively review products
outside of product design/launch lifecycles. In this post, we want to share an
example of such a review.

Note: You can learn more about the broader security team inside Google in the
[HACKING GOOGLE Series](http://g.co/safety/hackinggoogle).

## Introduction

In June 2023, we were reading the excellent blog post
[https://hackcompute.com/hacking-epp-servers/](https://hackcompute.com/hacking-epp-servers/) when we spotted a reference to a
Google open source project – [Nomulus](https://github.com/google/nomulus) (an
open source, scalable, cloud-based service for operating top-level domains
(TLDs), which is used by [https://registry.google/](https://registry.google/)). After reading the following
text, we decided to take a closer look:

> We spent a significant amount of time on Google's registry software and
> discovered an endpoint that we believe are \[sic\] not supposed to be accessed
> without authentication, but given that we couldn't prove much security impact,
> it was not reported to Google.

[Nomulus](https://github.com/google/nomulus) is an open source project, so we
wanted to share our findings in this blog post as they are also visible on
GitHub.

## Strategy

Our process for approaching Nomulus over about a week of time was to:

1. Deploy our own version of Nomulus onto Google App Engine. This gave us a
safe local environment to test privilege escalation issues and other
vulnerability types without risking production impact.
2. Manually review code, focusing on authentication & authorization systems
that may contain “business logic” vulnerabilities which may not be picked up
by automated code scans.
3. Run automated scans over the codebase, such as
[CodeQL](https://codeql.github.com/docs/codeql-overview/about-codeql/),
which may not have been run previously.

## Vulnerabilities

After deploying Nomulus, running [Burp Suite](https://portswigger.net/burp),
reviewing code, and running different scanning tools, we were able to identify a
handful of less severe (and now patched) issues that we can share.

### Admin Java Deserialization (Potential Remote Code Execution)

We observed that an administrative user could use the `/_dr/task/resaveEntity`
endpoint to exploit a Java deserialization vulnerability resulting in remote
code execution. Obviously, the administrators would already have full access to
any data in this system, but it is still important to prevent RCE. We were able
to generate a simple POC, but not a fully functional exploit. The Nomulus team
worked to harden this endpoint to eliminate this vulnerability.

Proof of concept:

```
Request:
java -jar ./core/build/libs/nomulus.jar -e alpha curl -u '/_dr/task/resaveEntity?requestedTime=5&resaveTimes=2&resourceKey=sql:<redacted base64 payload>@kind:Domain' --service BACKEND -X POST

Traceback observed:

Uncaught exception from servletjava.lang.IllegalArgumentException: Unable to deserialize: objectBytes=<redacted hex payload>    at

google.registry.util.SerializeUtils.deserialize(SerializeUtils.java:66)    at

google.registry.util.SerializeUtils.parse(SerializeUtils.java:89)    at

google.registry.persistence.VKey.createEppVKeyFromString(VKey.java:100)    at

google.registry.batch.ResaveEntityAction.lambda$run$0(ResaveEntityAction.java:77)
```

Resources:

- [Relevant code](https://github.com/google/nomulus/blob/2218663d550858f5e420d10402c2c95c55e180d5/util/src/main/java/google/registry/util/SerializeUtils.java#L63)
- Fix: [https://github.com/google/nomulus/pull/2150](https://github.com/google/nomulus/pull/2150)

### Credential leak via logging

In our test instance, we observed that end user OAuth access tokens were being
logged. In test instances, logging secrets can be OK, but leaked production logs
containing access tokens could lead to privilege escalation attacks. Luckily,
the access tokens have a one-hour expiration and access to the production logs
is limited to trusted administrators, so the actual risk is very low.

The Nomulus team stopped logging access tokens in production logs. This was also
mitigated in the long term by migrating from OAuth to OIDC.

Resources:

- [Relevant code](https://github.com/google/nomulus/blob/master/core/src/main/java/google/registry/request/auth/RequestAuthenticator.java#L96)
- Fix: [https://github.com/google/nomulus/pull/2148](https://github.com/google/nomulus/pull/2148)
- For more information:
[https://cheatsheetseries.owasp.org/cheatsheets/Logging\_Cheat\_Sheet.html#data-to-exclude](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html#data-to-exclude)

### Crypto Weakness (Password Hashing)

EPP access to registry.google is restricted by:

- Client certificate-based authentication
- IP address allowlists
- EPP password-based login

The EPP protocol itself requires password-based authentication. Because of this,
Nomulus is required to store and manage passwords. While reviewing this code, we
spotted that Nomulus uses SHA256 to hash these passwords before storage. Based
on our crypto team's recommendation, Nomulus is transitioning to scrypt.

Resources:

- [Relevant code](https://github.com/jianglai/nomulus/blob/8ec16dca8d8ad7ec46d52baaa6d2a3e1d906f19f/util/src/main/java/google/registry/util/PasswordUtils.java#L40)
- Fix: [https://github.com/google/nomulus/pull/2191](https://github.com/google/nomulus/pull/2191)
- RFC reference: [https://www.rfc-editor.org/rfc/rfc5730.html#section-2.9.1.1](https://www.rfc-editor.org/rfc/rfc5730.html#section-2.9.1.1)
- For more information:
[https://cheatsheetseries.owasp.org/cheatsheets/Password\_Storage\_Cheat\_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

### Crypto Weakness (Non-Constant Comparison Credential Check)

We spotted a concern that, depending on the Nomulus deployment, could lead to a
side-channel attack used to bypass the certificate cert auth check. While this
is an unlikely attack scenario, it is critical to use constant time comparisons
when validating any authenticator.

Resources:

- Fix: [https://github.com/google/nomulus/pull/2147](https://github.com/google/nomulus/pull/2147)
- An example of an unrelated crypto timing attack:
[https://faculty.cc.gatech.edu/~genkin/cachebleed/index.html](https://faculty.cc.gatech.edu/~genkin/cachebleed/index.html)

### Partial Auth Bypass on https://registry.google

Using internal bug reports and documentation, we were able to demonstrate an
insider threat risk to Nomulus that could bypass two of three authentication
methods to gain access to the system. We were not able to bypass the EPP
password-based login.

The Nomulus team worked to accelerate their transition from OAuth to OIDC which
contains mitigations for these insider threat risks.

Resources:

- Fix: [https://github.com/google/nomulus/pull/2171](https://github.com/google/nomulus/pull/2171)

### Epilogue

We worked closely with the Nomulus team throughout this process to remediate the
issues presented above. We hope that this list gives you some insight into what
our team looks for when reviewing product security.

If you want to report a security vulnerability to Google, please use the form
available at [https://bughunters.google.com/report/](https://bughunters.google.com/report/).

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab