---
source: bughunters
source_url: https://bughunters.google.com/blog/secure-by-design-googles-blueprint-for-a-high-assurance-web-framework
title: "Secure by Design: Google's Blueprint for a High-Assurance Web Framework - Google Bug Hunters"
description: "Learn more about how Google has created and deployed a high-assurance web framework that almost completely eliminates exploitable web vulnerabilities."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/secure-by-design-googles-blueprint-for-a-high-assurance-web-framework#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Secure by Design: Google's Blueprint for a High-Assurance Web Framework

![](https://storage.googleapis.com/bughunters-article-images/blogs/dworken.jpg)

David Dworken

Software Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/lwe.jpg)

Lukas Weichselbaum

Software Engineer

Published: Feb 4, 2025

Security Engineering  Web Security

[RSS Feed](https://bughunters.google.com/feed/en)

# Secure by Design: Google's Blueprint for a High-Assurance Web Framework

Google maintains one of the world's largest ecosystems of web applications.
Depending on how you count, we have either hundreds or several thousand of
distinct web services, most of which are sensitive from a security perspective.
The size of our web app ecosystem has grown substantially in the past decade,
which one might expect to have led to a similar growth in the number of security
vulnerabilities affecting our services. In reality, however, we've actually
managed to reduce the number of critical web vulnerabilities like
[XSS](https://en.wikipedia.org/wiki/Cross-site_scripting) in our applications by
over an order of magnitude, all while supporting this ever-growing ecosystem.

![](https://storage.googleapis.com/bughunters-article-images/blogs/web_framework.png)

_Fig. 1. This graph shows the number of_
_[XSS](https://en.wikipedia.org/wiki/Cross-site_scripting) vulnerabilities_
_reported to us through our_
_[Vulnerability Rewards Program](https://bughunters.google.com/) over time._
_Despite an increasing number of web apps and increasing reward amounts, the_
_number of reported vulnerabilities has consistently trended downwards. It is_
_worth noting that for hundreds of services that have fully adopted recommended_
_high-assurance web frameworks, the number of XSS vulnerabilities is even lower_
_(~1 per year across all of Google)._

This significant security improvement can be directly linked to our commitment
to Secure by Design principles, which we wrote about in this recent
[whitepaper](https://static.googleusercontent.com/media/publicpolicy.google/en//resources/google_commitment_secure_by_design_overview.pdf).
This blog post aims to provide a detailed blueprint for how Google has created
and deployed a high-assurance web framework that almost completely eliminates
exploitable web vulnerabilities.

## The Challenges of Web Security

The web was originally envisioned as a system to link and share information, and
it excelled at these goals. Over time this has led to the web growing in scope
such that it is now the standard channel through which users interact with many
applications, some of which manage users' most sensitive personal data. This
makes web security critical, but it requires building on top of a platform–what
we call " _the web platform_"–that was not originally designed with such
applications in mind. This created a situation where security was essentially an
afterthought for the web platform and has led to what we have come to refer to
as the " [_3 original sins_](https://arturjanc.com/usenix2019/#15)" of web
security:

1. (lack of) **Encryption**: Easy to build an application without
encryption-in-transit
2. **Injection**: The web's core building blocks (HTML, JS, URLs) allow easily
mixing code and data
3. (lack of) **Isolation**: Cross-origin interactions between different
applications are allowed by default

Each of these factors made the web platform easy to adopt and were conducive to
the explosive growth of the web. At the same time, these factors also lead to a
wide range of critical vulnerability classes:

1. (lack of) **Encryption**: Easy to build an application without
encryption-in-transit

→ By default, the web is unencrypted and data is visible over the network.
Unencrypted data allows MITM attackers to intercept and modify web apps in a
variety of malicious ways.

2. **Injection**: The web's core building blocks (HTML, JS, URLs) allow easily
mixing code and data

→ Mixing code and data makes it possible for data (e.g. the title of a photo
album or a blog) to be misinterpreted as code, leading to issues like XSS
vulnerabilities.

3. (lack of) **Isolation**: Cross-origin interactions are allowed by default

→ Cross-origin interactions between different applications allow malicious
websites to interact with sensitive apps and lead to issues like
[XSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery),
[clickjacking](https://en.wikipedia.org/wiki/Clickjacking), and several
types of [XS-Leaks](https://en.wikipedia.org/wiki/Cross-site_leaks).


It is worth drawing attention to the fact that almost all web vulnerabilities
can be connected to one of these risks. This is why Google takes a
platform-centric approach to security where we partner closely with Chrome, the
W3C, and other web browser vendors to evolve the web platform, with the goal of
fixing as many of these risks in the web platform as possible. But, where this
isn't possible to do by-default, we need to ensure that our web applications are
still comprehensively defended against such vulnerabilities. And this is where
our blueprint for a high-assurance web framework comes in.

> A quick note on web security: Our focus here on web security vulnerabilities
> stems from the fact that almost all Google services are exposed as web apps,
> where a client-side vulnerability like an XSS could completely compromise a
> user's data. So while it may seem like XSS is less impactful than attacks
> performed directly against web servers such as remote code executions or SQL
> injection, XSS vulnerabilities are extremely critical to Google and something
> that we go to great lengths to prevent. It is also worth noting that similar
> reasoning is why [MITRE currently ranks XSS as the #1 software security\\
> weakness across the\\
> industry](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html).

## Elements of a high-assurance web framework

In our experience, there are three critical components that work together to
achieve a high-assurance web framework:

### \#1: Safe Coding

" [_Safe Coding_](https://research.google/pubs/developer-ecosystems-for-software-safety-2)"
is the term we use for our approach to ensuring that developers can write code
in a way that is secure-by-design, without having to think about security. The
fundamental goal of Safe Coding is to ensure that security is easy and automatic
for developers.

This is done by ensuring that the default behavior is secure, and that
guardrails exist to prevent security regressions. Our goal is to ensure that if
code compiles and runs successfully, it is secure. While this may seem simple,
we've learned that achieving this while preserving a positive developer
experience is difficult, but essential. Ultimately, developers are just trying
to accomplish their goal of building and shipping a delightful web app for our
users. And we need to ensure that rather than saying "No" to a developer's
question, we always can say "Yes! The secure way is…". This is rooted in one of
our team mottos: "empathy for the developer".

### \#2: Adaptability

Due to changes in the web platform and novel security research, security is an
ever-moving target, which means we need to ensure that our approach to web
security is adaptable, allowing us to adjust to whatever may come in the future.
We continually perform in-depth research to ensure that our web frameworks are
defending us and our users against both classic and newly emerging security
vulnerabilities. When we find a gap, we go through the process of:

1. Designing new security mechanisms. This often starts with designing new
targeted mitigations for our own frameworks and libraries to test our ideas
and prove they work. But from there, we frequently try to upstream our
solutions to the web platform where they can benefit as many people as
possible.
2. Enabling these new security mitigations by default and adding guardrails to
prevent regressions (see #1 Safe Coding)
3. Running large-scale changes to enable these new security mitigations for
existing services
4. Measuring progress on our rollouts to understand mitigation coverage (see #3
Observability)

The goal of this process is that once an application is built on a
high-assurance web framework, application owners will typically not have to
worry about the treadmill of keeping up with ~~the joneses~~ security. Adopting
new security mitigations is done transparently and centrally, without any
required action from application owners. See
[this post](https://bughunters.google.com/blog/5896512897417216/a-recipe-for-scaling-security)
for a more detailed description of how we approach this.

### \#3: Observability

The last key component of a high-assurance web framework is observability. In
order to make the above components work, it is essential for the security team
to have a deep understanding of the security posture of every application. Of
course, a manual approach to observability would not scale, so instead we rely
on building observability features into frameworks and infrastructure that allow
us to understand framework behavior, security feature adoption, and much much
more. See
[our Security Signals paper](https://research.google/pubs/security-signals-making-web-security-posture-measurable-at-scale/)
which explains how we've made web security measurable at Google.

## Key Security Controls

At this point, one might ask: So what exactly are the security controls that
make up a high-assurance web framework? We want to emphasize that this is an
evolving list, and that enabling every feature in the below table is not enough
to guarantee that an application will be safe. A true high-assurance web
framework needs to enable these features, but also do so in a scalable and
adaptable way that preserves the developer experience and prevents regressions.

With that context, here is the current list of features automatically enabled by
our high-assurance web frameworks:

| Control | Risk Category | Description |
| --- | --- | --- |
| [Secure cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#secure) | Encryption | All cookies should use the \`Secure\` attribute to ensure they're only available to pages that use HTTPS. |
| [HTTPS Redirects](https://web.dev/articles/enable-https#redirect-to-https) | Encryption | All HTTP responses should redirect HTTP requests to HTTPS. |
| [HSTS](https://web.dev/articles/security-headers#hsts) | Encryption | All HTTP responses should use HSTS to ensure that browsers default to HTTPS URLs. |
| [XSRF Protection](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) | Isolation | All state-changing endpoints should deploy strong protections against XSRF vulnerabilities. |
| [SameSite cookies](https://web.dev/articles/samesite-cookies-explained) | Isolation | All cookies should use the \`SameSite\` attribute to ensure that they are not attached to cross-site requests. |
| [Framing Protections](https://web.dev/articles/security-headers#xfo) | Isolation | All pages should deploy framing protections to prevent untrusted third-parties from iframing sensitive pages. |
| [Cross-Origin Opener Policy](https://web.dev/articles/security-headers#coop) | Isolation | All pages should deploy COOP to prevent untrusted third-party pages from opening them in a popup and interacting with them. |
| [Fetch Metadata Protections](https://web.dev/articles/fetch-metadata) | Isolation | All pages should deploy Fetch Metadata protections to block cross-site requests by default. |
| [Cross-Origin Resource Policy](https://web.dev/articles/security-headers#corp) | Isolation | All pages should set the CORP header to prevent them from being loaded in unexpected cross-site contexts. |
| [Hostname Validation](https://portswigger.net/web-security/host-header#how-to-prevent-http-host-header-attacks) | Isolation | All services should validate the \`Host\` header and reject requests with unexpected values. |
| [JS/TS Conformance](https://github.com/google/safety-web) | Injection | All services should use compile-time conformance to block JS/TS code from using unsafe patterns. |
| SafeResponse Types | Injection | An automated conformance check should ensure that all HTTP responses are built via API abstractions that guarantee that they are constructed in an XSS-free way, for example via a safe auto-escaping template system. |
| [Contextual Auto-Escaping Template System](https://github.com/google/closure-templates) | Injection | All HTML responses should be built by a template system that supports contextual auto-escaping to guarantee the response is free of XSS vulnerabilities. |
| Default Content-Type | Injection | All HTTP responses should explicitly set a \`Content-Type\` header. If this is missing, responses should default to a safe value (e.g. \`text/plain\`). |
| [HttpOnly cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#httponly) | Injection | All cookies should use the \`HttpOnly\` attribute to ensure that they are not accessible to client-side JS. |
| [Strict CSP](https://web.dev/articles/strict-csp) | Injection | All pages should deploy a Strict nonce-based CSP to mitigate XSS vulnerabilities. |
| [Trusted Types](https://web.dev/articles/trusted-types) | Injection | All pages should deploy Trusted Types to mitigate DOM-XSS vulnerabilities. |
| Allowlist CSP | Injection | All pages should deploy an allowlist CSP to constrain the set of allowed JS sources to reviewed and trusted JS serving hosts. This helps mitigate runtime supply chain attacks. |
| Strict dependency controls | Injection | All libraries consumed at build-time should be reviewed to mitigate build-time supply chain attacks. |
| JS Integrity Validation | Injection | All pages should validate the integrity of all included scripts to ensure they are not modified between build-time and runtime. |
| Prototype Pollution Mitigations | Injection | All pages should deploy mitigations against Prototype Pollution. |

It is worth emphasizing: Everything in this list is maintained by the security
team. With our high-assurance web frameworks, application owners don't need to
be aware of any of these features–they all are enabled and work out of the box.
Some of these features do constrain the code that application owners write (e.g.
they'll block writing code such as `document.body.innerHTML = "foo"`) but this
is a purposeful part of our "Safe Coding" approach to security described
[in a previous post](https://bughunters.google.com/blog/5896512897417216/a-recipe-for-scaling-security).

![](https://storage.googleapis.com/bughunters-article-images/blogs/web_framework_02.png)

_Fig. 2. A typical response of an application built on our high-assurance web_
_framework where security-relevant HTTP response headers are enabled by default._

### Case Study: XSS Mitigations

We can examine how these different security controls layer together to provide
high-assurance protections through a short case-study. We can examine the
question of: What would it take for an XSS to occur with all of these
mitigations enabled?

The classic XSS vectors are all mitigated:

1. Reflected & Persistent XSS: Mitigated by SafeResponse Types, Contextual
Auto-Escaping Template System, and Strict CSP
   - For a reflected or persistent XSS to occur, it would need to involve a
     SafeResponse bypass, a vulnerability in the templating system, and a
     bypass of the strict CSP.
2. DOM XSS: Mitigated by JS/TS Conformance, Strict CSP, and Trusted Types
   - For a DOM XSS to occur, it would need to bypass our compile-time JS/TS
     conformance, the strict CSP, and Trusted Types.

On top of this, other types of XSS are also mitigated:

- Prototype Pollution → XSS: Mitigated by freezing and sealing the prototype
chain.
- Supplychain attacks → XSS: Mitigated by the allowlist CSP.

Taken together, the above mitigations bring us to the point where we can be very
confident that applications built on a high-assurance web framework are free of
XSS flaws.

## Conclusion

We hope that our approach to building and deploying a high-assurance web
framework can serve as an existence proof that it is possible to scalably build
secure web applications. In the past 3 years, for hundreds of complex web
applications built on our high-assurance web framework, we've averaged less than
**one** XSS report per year—not _per_ application, but across all of them! This
demonstrates that it truly is practical (and cost-effective) to build secure web
applications, at scale, via high-assurance web frameworks. The key advantages of
these frameworks is that they offer:

- **High Assurance & Reduced Vulnerabilities:** We've analyzed data from both
our [VRP](https://bughunters.google.com/) and internal research and the data
is clear: secure frameworks drastically reduce the number of exploitable web
vulnerabilities.
- **Multiple Layers of Protection:** We deploy multiple layers of protection,
both at compile-time and runtime, to ensure defense-in-depth. This ensures
that if there is a gap in any of our protections, it is likely to be stopped
by one of the multiple overlapping layers of protection.
- **Increased Developer Productivity:** By letting the framework handle
security, we free developers from having to think about security and enable
them to focus on their core product goals. We also have sped up product
launches by enabling automated launch reviews for products built on secure
frameworks.
- **Improved Maintainability:** Thanks to built-in adaptability and
observability, our secure frameworks are easy to maintain and can be
extended in the future as needed.

As always with security, there is no silver bullet. But we believe that a
[framework-centric approach to security](https://speakerdeck.com/lweichselbaum/googles-recipe-for-scaling-web-security-locomocosec-2024)
is as close as we can get to eliminating decades-old vulnerabilities like XSS
and XSRF once and for all. We've built these frameworks internally, but we
strongly believe that the broader web ecosystem would also benefit from adopting
many of these ideas to provide high-security assurances and we aim to bring this
idea to the external open source web ecosystem in the future.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab