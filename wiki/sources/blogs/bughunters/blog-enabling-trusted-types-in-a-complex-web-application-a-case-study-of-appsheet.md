---
source: bughunters
source_url: https://bughunters.google.com/blog/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet
title: "Enabling Trusted Types in a Complex Web Application: A Case Study of AppSheet - Google Bug Hunters"
description: "Want to know more about adopting Trusted Types to improve the security posture of an application? Take a look at our case study describing how we rolled out Trusted Types in AppSheet, a Google product."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Enabling Trusted Types in a Complex Web Application: A Case Study of AppSheet

![](https://storage.googleapis.com/bughunters-article-images/blogs/kjamali.png)

Kian Jamali

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/aaronshim.jpeg)

Aaron Shim

Software Engineer

Published: Jul 1, 2024

Security Engineering  Web Security

[RSS Feed](https://bughunters.google.com/feed/en)

# Enabling Trusted Types in a Complex Web Application: A Case Study of AppSheet

Trusted Types are a powerful web defense mechanism that effectively protects
applications against XSS vulnerabilities. In this blog post, we'll take a closer
look at Trusted Types and describe how we adopted and rolled out Trusted Types
in AppSheet, a Google product.

### Why Trusted Types?

Over the last several years at Google, we have been committed to shipping the
latest and greatest web security protections to our end users. Trusted Types are
the best defense we have against
[DOM XSS](https://owasp.org/www-community/attacks/DOM_Based_XSS), and its
rollouts have contributed to a large reduction in XSS vulnerabilities in our
products. Additionally, we had extraordinary success in rolling out these
features
[at scale](https://bughunters.google.com/blog/5896512897417216/a-recipe-for-scaling-security)
within first-party Google applications built with Google-internal stacks, so we
were naturally curious whether we could scale our approach to other Google
products that weren’t necessarily built with our internal technologies.

### Why AppSheet?

[AppSheet](https://about.appsheet.com/home/) is a platform that lets
non-programmers build scalable, cost-effective apps for the web with a
user-friendly drag-and-drop interface and pre-built components. As a part of
[Google Workspace](https://about.appsheet.com/google-workspace/), AppSheet is a
vital part of the ecosystem that adds extensibility to productivity tools that
millions depend upon daily. Although we had rolled out Trusted Types at scale to
some of the other Workspace products such as Docs and Gmail, AppSheet did not
benefit from these prior investments because – being an acquisition – it was
built in a development ecosystem that was different from Google's internal
first-party frameworks.

Due to the complex nature of its drag-and-drop UI, AppSheet had been
particularly susceptible to DOM XSS for several years. Notably, during this
period, AppSheet had a significant number of exploitable XSS vulnerabilities
reported through our
[Vulnerability Rewards Program](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules).
Given the importance of the product and our commitment to upholding
industry-leading security standards across all Workspace products, we decided to
launch a remediation program using our best layer of defense against DOM XSS:
[Trusted Types](https://web.dev/articles/trusted-types).

Thanks to this remediation, we were able to eliminate existing DOM XSS vectors
(including ones that we discovered in the course of this work) and ensure that
no additional ones would be added to the product.

### A Quick Primer on Trusted Types

Before we dive into the description of how we enforced Trusted Types on
AppSheet, there are a couple of points that we want to highlight that will be
crucial for understanding the steps in our adoption journey!

XSS vulnerabilities arise when an application allows untrusted,
attacker-controlled strings to reach an
[_injection sink_](https://w3c.github.io/trusted-types/dist/spec/#injection-sink)
without appropriate sanitization or escaping. Injection sinks include DOM APIs
and properties such as `innerHTML`. We've found that these vulnerabilities can
be prevented most effectively by
[relying on type systems](https://research.google/pubs/if-its-not-secure-it-should-not-compile-preventing-dom-based-xss-in-large-scale-web-development-with-api-hardening/)
to ensure that only safely-constructed, trustworthy values can ever reach
injection sinks.
[Trusted Types](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)
is a defense-in-depth mechanism that implements this approach in the browser. It
is delivered through a
[Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)
header, and comes in two modes: **enforcement** and **report-only**. The
enforcement mode provides the full benefits of the protection mechanism by
refusing to execute code at runtime that could potentially lead to DOM XSS. For
example, code that assigns a value of type `TrustedHTML` to an element's
`innerHTML` property executes successfully, while assignment of any other type,
including plain strings, raises an error. The report-only mode surfaces console
warnings and generates violation reports for code that would be blocked in
enforcement mode, but without changing the execution of the JS code. This is
meant as an intermediate stage in the adoption process for a large, existing
codebase where we want to be extra careful to not break any preexisting
user-visible behavior that depends on JavaScript execution.

These generated reports are JSON data that contain the URL of the page and the
code location that triggered the violation. The reports are sent to the endpoint
defined by the
[report-uri](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/report-uri)
directive (or the
[report-to](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/report-to)
reporting group name, if using the
[Reporting API](https://developer.mozilla.org/en-US/docs/Web/API/Reporting_API)).
We had the benefit of already having a server-side endpoint ready to accept JSON
data of this type and persist it for later querying with tools similar to
[BigQuery](https://cloud.google.com/bigquery) (which allows more sophisticated
analysis like deduplication and pattern matching).

In addition to understanding the reporting mechanism for Trusted Types
adoptions, it is also important to note that for a Trusted Types enforcement to
be successful on a given page, **all JS code running on that page must also be**
**Trusted Types compatible.** In an age of easy-to-import dependencies and more
complex user-facing interfaces, this is no easy feat – and you will see how we
handled this in the upcoming sections!

For a more comprehensive introduction to Trusted Types that describes far more
details than we can hope to cover in the scope of this introductory section,
please refer to our
[companion post over at web.dev](https://web.dev/articles/trusted-types).

### Trusted Types rollout process

Before initiating the rollout process, we can potentially employ static code
analysis to identify and mitigate some Trusted Types (TT) violations. While we
did not leverage it for AppSheet, it is a preliminary step that can save a
significant amount of time during the rollout process that we generally follow
(see [https://ieeexplore.ieee.org/abstract/document/9583692](https://ieeexplore.ieee.org/abstract/document/9583692)).

To roll out Trusted Types on an existing codebase, we followed the methodology
described below, which can be summarized in 5 phases.

1. **Report-only mode**: Collecting Trusted Types violation reports is the
first step. Doing so allows us to estimate the effort required to fix the
Trusted Types violations in the application code based on the nature and
number of violations. To achieve this, we need to configure the backend to
send a CSP response header which enables Trusted Types, as well as accept
violation reports in order to begin our investigation. See
[Report-Only Mode](https://bughunters.google.com/blog/6037890662793216/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet#report-only-mode)
for further details.

2. **Collect and triage violations**: During this phase, we are simply waiting
for our users to interact with the application and generate reports. In our
rollout, we waited around two weeks. As a general rule, you should wait for
enough user traffic to have been generated for you to be confident that a
sufficient amount of user interaction patterns have been triggered so that
hopefully all potentially violating code paths are exercised.

3. **Refactor blockers**: Once the reports have been collected, it is time to
fix the corresponding violations. This is a critical step that involves
identifying the violations and patching them – which sometimes requires a
bit of effort and research. We will expand on how these two tasks can be
done efficiently in the
[Report-only mode](https://bughunters.google.com/blog/6037890662793216/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet#report-only-mode)
section below.

Step 3 poses a substantial challenge due to the difficulty in identifying
violations. This aspect will be explored in greater detail in the following
section (See
[Investigation of a trusted type violation](https://bughunters.google.com/blog/6037890662793216/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet#investigation-of-a-trusted-type-violation)).

4. **Repeat steps 2 and 3 if necessary**: Once all the refactoring work is
done, we wait to see whether our violation reports disappear and whether new
violations come up. If we find any new violations, or if we find that our
previous refactorings did not remove the violations as expected, we need to
refactor them.

5. **Enforcement**: Finally, if no new violations are identified, we can
proceed with turning on enforcement mode. In the following sections, we will
describe our approach of carefully rolling out this change to avoid
impacting any application functionality.


### Report-only mode

Once we gained an initial familiarity with the codebase setup of AppSheet, we
started contributing code towards adopting Trusted Types by adding code to
collect violation data. The first data points we need before fixing any Trusted
Types violation is information about where these violations happen in the
application code. To capture these data points, we can start sending Trusted
Types headers in report-only mode (See
[Trusted Types rollout process](https://bughunters.google.com/blog/6037890662793216/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet#trusted-types-rollout-process)).

We were fortunate to be able to direct all of the violation reports to a
collection server and pipeline for web security violations data shared across
all of Google’s first-party products, called the Security Collector. The
Security Collector is a platform we built with Google scale in mind; billions of
users generating trillions of page views requires a lot of data-intensive
engineering! This platform provides an endpoint capable of accepting Trusted
Types violation reports generated and sent by the browser. In most adoption
projects that do not have a Google-sized user base, however, any endpoint
capable of persisting JSON violation reports and querying over them would be
sufficient.

Concretely, to instruct the browser to run Trusted Types in the Report-only mode
and direct all the reports from AppSheet to our Security Collector endpoint, we
added this static HTTP header to all main Document requests using a centralized
middleware available in the AppSheet codebase:

```
Content-Security-Policy-Report-Only: require-trusted-types-for 'script'; report-uri {security_collector_endpoint}
```

After waiting a couple days until our users interacted with enough pages in the
application to generate sufficient violation data, we verified that we were
starting to receive Trusted Types reports.

If your application does not generate enough user traffic to quickly verify that
report collection is working, you can always create synthetic violation reports
by triggering your own Trusted Types violations. Open the Chrome Dev console and
execute the following line of JavaScript:

```
document.body.innerHTML = 'This is a Trusted Types violation!';
```

After verifying that there is a console error corresponding to this attempted
DOM API assignment, you can immediately check the _Network_ tab of the Chrome
Dev console to see that this report was sent and accepted by the backend.

In the following section where we describe how we fixed the identified
violations, we will also go into more detail on what the reports contain exactly
and how they can be leveraged.

### Investigation of a Trusted Type violation

Fixing Trusted Types violations can be a tricky task. The reports provide a lot
of information about each violation, but tracing them back to the violations
root cause is not always trivial. In this section, we will describe the
methodology we followed to fix TT violations.

Let’s analyze what type of information each report is providing. A report
contains multiple fields, of which a few are critical when you are looking to
understand the root cause of a violation:

1. **source-file**: This field indicates the Javascript resource where the
offending line causing the violation is located. If you're lucky, you will
even have a line and column number. This field can significantly speed up
the process of finding your violation, but only if it points directly to the
right file with the offending code. If this field is empty, then you can
assume that the violation is probably in a `<script>` block contained
directly in the HTML response. Unfortunately, it could also point to:


   - A minified file which will be quite hard to read
   - A runtime dependency that you won't find in your bundled JS
   - An external CDNs from which some minified JS is imported

In these cases, identifying the location of the offending code may be more
difficult.

2. **document-uri**: This field indicates the page where the violation is
occurring. This allows you to navigate to your app page and see if you can
trigger the violation yourself. If you can do so, this will greatly
facilitate your ability to fix the violation. Note that this field can also
be empty.

3. **script-sample**: This field is arguably the most important one. It
contains two pieces of data, separated by a pipe character (\|). The first
part, appearing before the pipe character, specifies the underlying API call
that caused the violation (e.g. innerHTML). The second part of the field,
appearing after the pipe character, contains a prefix of the input that was
fed into the unsafe DOM API. Before persisting the script-sample, we heavily
redact it to ensure that it does not contain any user data. This includes
removing all strings and numbers along with a custom set of additional rules
to ensure the script-sample only contains non-personalized JavaScript code.


### Refactoring for compatibility with Trusted Types

The approach to resolving Trusted Types violations varies depending on the
application.
[Several primary methods](https://web.dev/articles/trusted-types#fix-violations)
exist to refactor a Trusted Types violation. We will elaborate on these methods
in a forthcoming article that will provide details on how we conducted the
Trusted Types refactoring on AppSheet and other workspace products (e.g. Gmail).

### Enforcement

Once all the violations were patched, we were finally ready for enforcement! The
enforcement process itself is quite simple, we simply needed to add this static
header to all requests:

```
Content-Security-Policy: require-trusted-types-for 'script'
```

We could have deployed this header to the whole application at once, but that
would have introduced a risk of breaking production functionality. We'd been
very meticulous to make sure that we removed all violations from the
application, but what if we missed one of them? And what if this one violation
ended up breaking the login for all users? Once the enforcement is in place, the
browser will strictly block all offending line executions. Therefore, we do not
recommend applying enforcement to all traffic at once. Instead, we proceeded
with a percentage-based rollout (a
[production best practice at Google](https://sre.google/sre-book/service-best-practices/#:~:text=Progressive%20Rollouts)),
gradually increasing the amount of traffic impacted by enforcement (1%, 5%, 10%,
30%, 100%). This way, if any new violation were to occur, we could have quickly
rolled back to minimize user impact.

Once enforcement is in place, you want to ensure that any potential new
violations will be detected as early as possible during the development process.
To achieve this, we enforced Trusted Types in AppSheet's testing infrastructure
(in unit tests and integration tests), and in the development/staging
environment. This way, we ensured that any new violation would be detected, in
this order (from the earliest detection to the latest):

1. By the developer while they are adding code incompatible with Trusted Types.
This is usually easy to notice because it results in visible breakage in the
developer's local environment.
2. Through unit/integration test failures.
3. By the testing team due to breakages in the staging environment.

This kind of setup should prevent violations from getting into production and
breaking any existing functionality. In our specific case, this approach allowed
quick detection of new violations in AppSheet after the enforcement was in
place.

### Conclusion

In this blog post, we explored the Trusted Types security feature and outlined
how we approached its adoption in AppSheet, a Google Workspace product. We went
on to describe the rollout process we followed, the challenges we faced, and the
solutions we implemented.

We hope that this post has provided you with valuable insights into Trusted
Types and its adoption. By following the steps outlined in this post, you can
successfully implement Trusted Types in your own web applications and enhance
their security.

Although implementing Trusted Types is not a trivial task, it is a worthwhile
endeavor. Trusted Types contributes
[to the scalable safe coding platform](https://bughunters.google.com/blog/5896512897417216/a-recipe-for-scaling-security)
that Google Security has been building for so many years. By mitigating the
risks associated with malicious code execution, Trusted Types can help protect
your users and your organization against critical threats posed by DOM XSS
vulnerabilities.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab