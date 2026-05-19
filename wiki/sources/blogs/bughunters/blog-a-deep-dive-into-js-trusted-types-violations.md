---
source: bughunters
source_url: https://bughunters.google.com/blog/a-deep-dive-into-js-trusted-types-violations
title: "A Deep Dive into JS Trusted Types Violations - Google Bug Hunters"
description: "Join us as we take a closer look at the technical details of how we identified the root causes for TT violations in two flagship rollouts: Gmail and AppSheet."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/a-deep-dive-into-js-trusted-types-violations#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# A Deep Dive into JS Trusted Types Violations

![](https://storage.googleapis.com/bughunters-article-images/blogs/ecenazo.jpg)

Jen Ozmen

Software Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/kjamali.png)

Kian Jamali

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/aaronshim.jpeg)

Aaron Shim

Software Engineer

Published: Feb 27, 2025

Security Engineering  Web Security

[RSS Feed](https://bughunters.google.com/feed/en)

# A Deep Dive into JS Trusted Types Violations

In our
[previous blogpost](https://bughunters.google.com/blog/6037890662793216/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet),
we provided a comprehensive overview of the Trusted Types (TT) rollout in
AppSheet, highlighting the importance of this web security standard for
mitigating Cross-Site Scripting (XSS) vulnerabilities.

Now, we're ready to dive into the technical details of how we identified the
root causes for TT violations. In particular, this blog post will detail the
challenges we encountered with 2 flagship rollouts:
[Gmail](https://workspaceupdates.googleblog.com/2024/01/extending-trusted-types-to-gmail.html)
and
[AppSheet](https://bughunters.google.com/blog/6037890662793216/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet).
Since the rollout of Trusted Types in those products a year ago, we didn’t have
a single DOM XSS reported in them. Both services presented us with unique
obstacles during the Trusted Types rollout, yet they also shared common
characteristics whose complexity we had to deal with (large codebase, diverse
OSS and OSS legacy stack, …). The code was not written following Google standard
practises so we could not use Google standard toolings. Therefore, we believe
that our approach to these Trusted Types rollouts will be applicable to many
products outside of Google.

## Quick Refresher on Trusted Types

Trusted Types, as a reminder, introduces a security model that requires
developers to use
["trusted" values](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API)
– values that have intentionally gone through a
[policy-governed transformation](https://developer.mozilla.org/en-US/docs/Web/API/TrustedTypePolicy)
– for potentially dangerous operations like inserting content into the DOM.
Trusted Types policies can be centrally maintained and reviewed by security
experts, providing high confidence that all values that flow into risky DOM APIs
are indeed trustworthy. This shift from relying on raw strings to using
explicitly trusted values (sanitized, developer-controlled, escaped) is a major
change for many codebases, including AppSheet and Gmail.

In this post, we'll share the specific techniques and best practices we employed
to refactor Trusted Types violations. We'll walk you through common patterns of
Trusted Types violations we encountered in AppSheet and Gmail, the strategies we
used to fix them, and the lessons we learned along the way. By the end of this
post, you'll have a practical toolkit for refactoring Trusted Types-incompatible
code in your own web applications.

> **Important Note**: The specific techniques covered in this article may vary
> depending on your development environment, codebase structure, and the types
> of violations you encounter. However, the general principles and concepts
> presented here are applicable across most web applications transitioning to
> Trusted Types.

## Taking the developer’s perspective

As security engineers partnering with product teams to deploy Trusted Types, our
first step was to set up our development environment just as a software engineer
working on the product team would set it up. Although this required some ramp up
as the setup process was bespoke to the team’s tech stack, it was a one-time
effort that paid dividends: it allowed us to reproduce bugs later on and suggest
process changes that would be useful from the point of view of an engineer
working on the product. Once this setup was completed, it was critical for us to
understand the team’s coding and testing practices to gauge the pace at which we
could fix violations. We found that comprehensive test coverage enabled us to
confidently update code to address potential Trusted Types violations without
reliability issues. While the security team typically maintains tight controls
over Google's internal frameworks by influencing API design and tooling (such as
heavily customized static analysis pipelines on the Google monorepo), AppSheet
(built on OSS) and Gmail (using a legacy, non-standard framework) presented
unique engineering challenges. These proved to be very interesting use cases for
exploring the different aspects of a Trusted Types adoption.

In addition to the technical benefits, enrolling into the development lifecycle
as security engineers was also critical to gain the trust of the product team.
The deployment of Trusted Types into an existing application, while
significantly increasing its security posture, can be quite stressful for
development teams due to the potential for introducing regressions in product
functionality. We acknowledge that it is an additional feature request for a
team with an already full backlog. A core value of the Safe Coding philosophy is
_Empathy for the Developer_ – we strive to make the deployment of security
mechanisms as smooth as possible to ensure product teams do not perceive
security as a burden. At the end of this process, we established clear
communication channels with the leads of different parts of AppSheet and Gmail
and were able to ship code to production.

## Shift left!

Integrating security best practices early in the software development life cycle
is key to long-term maintainability. This proactive approach helps identify and
address potentially risky patterns before they reach production, and before the
code change is even submitted. Although we recognize that in the context of
Trusted Types compatibility, static analysis checks are not comprehensive \[1\],
we found that in practice this is a highly cost-effective way to identify the
majority of incompatible code patterns very early in the process. This left us
more time to focus on the more difficult violations and incompatibilities that
are only observable at runtime in the deployed application.

In the Google monorepo, we have a set of static analysis checks that we call
“conformance” and which are designed to check – at build time – for changes to
the codebase that might be harmful. For example, in the domain of Trusted Types
refactorings and adoption, we have conformance rules that check for uses of DOM
APIs being supplied with values of an incorrect (non-Trusted) type and ad-hoc
creation of TT policies, without in-depth security review.

Our application of these static guarantees for all JavaScript code (and its
transitive dependencies) was possible for Gmail, given that it was built on our
internal tooling, but there was no equivalent for our AppSheet codebase. This
inspired us to build a similar tool (available in the open source ecosystem)
called [safety-web](https://github.com/google/safety-web) for scanning
JavaScript codebases (and, in the future, their transitive dependencies). This
was a rewrite of our earlier efforts of creating similar tooling called
[tsec](https://github.com/google/tsec), with a special focus on compatibility
and developer experience to make it more applicable to a wider range of
codebases. We achieved this by building on top of [ESLint](https://eslint.org/)
– a widely accepted tool for static analysis and linting in the open source
JavaScript ecosystem today.

In addition to conformance, another approach that we rely on to produce Trusted
Types-compatible and XSS-resistant code is an API design that follows our
[safe coding approach](https://github.com/google/safe-html-types/blob/main/doc/index.md).
Specifically, in our Trusted Types use case, this means that we provide users
with a wrapper library around dangerous DOM APIs
( [safevalues](https://github.com/google/safevalues)) that makes safer uses of
these APIs more natural than the potentially unsafe uses. Combined with
conformance rules to ban usages of DOM APIs without our safevalues wrappers,
this is a powerful tool to nudge developers towards our best practices.

So, as you can see, it’s perfectly possible to replicate our internal tooling
approach by using existing open source tools, and we highly recommend doing so!

For more information on how we use these shift-left principles such as safe
coding and conformance at Google, please refer to the
[A Recipe for Scaling Security](https://bughunters.google.com/blog/5896512897417216/a-recipe-for-scaling-security#more-tools)
and [Google Secure By Design](https://dl.acm.org/doi/10.1145/3651621) articles.

## Time to start the detective work

In our
[previous blogpost](https://bughunters.google.com/blog/6037890662793216/enabling-trusted-types-in-a-complex-web-application-a-case-study-of-appsheet?ref=weekly.infosecwriteups.com#investigation-of-a-trusted-type-violation),
we covered the most important fields in TT reports. Now, let’s go through them
in a bit more detail to highlight our methodology for finding the root cause of
TT violations:

### 1\. Searching for the \`script-sample\`

We can find a large amount of code locations that generate violations by just
carefully reading our application code with an eye for patterns suggested by our
violation reports. The `script-sample` in the violation report lists two bits of
important information:

```

{
 "csp-report": {
    "document-uri": "https://my.url.example",
    "violated-directive": "require-trusted-types-for",
    "disposition": "report",
    "blocked-uri": "trusted-types-sink",
    "line-number": 39,
    "column-number": 12,
    "source-file": "https://my.url.example/script.js",
    "status-code": 0,
    "script-sample": "Element innerHTML | This is a test."
 }
}
```

The `script-sample` follows this syntax:

```
<dangerous API that was used> | <the string input (truncated to 40 chars)>
```

As an example, if we had the following line in our codebase:

```
document.body.innerHtml = "This is a test"
```

…the `script-sample` in the violation report would be:

```
Element.innerHTML | This is a test.
```

With a simple grep in our codebase, we could find the root cause of the
violation, specifically because the input string is a completely static value
that’s easily greppable. But even if the input strings were not completely
static, we could guess where they might have been generated in the code and
follow where they might have ended up at the DOM API assignment.

The `source-file` is quite useful here as well, as it points to the JS file that
contains the Trusted Types violating line and can narrow down your search for
the offending line. Note that this field may be empty in some scenarios like if
the offending line was in an inline script or in extension code.

> **Note**: One important caveat here is that not all violations will be in our
> application’s code and thus under our control, but that they can also come
> from dependencies we use. Therefore, if you cannot find the string patterns in
> your application’s codebase, you also need to grep open source libraries to
> see whether the pattern appears there.
>
> - **For our AppSheet rollout**, we used
>   [Sourcegraph](https://sourcegraph.com/search) to search for strings that
>   occur across multiple different public GitHub repositories, which provided
>   a much better experience than GitHub’s native search UI.
> - **For Gmail**: Given that
>   [Google's monorepo](https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/)
>   holds "vendored" copies of third-party libraries, we were able to use the
>   [internal CodeSearch tool](https://research.google/pubs/how-developers-search-for-code-a-case-study/)
>   over the monorepo to find potential locations of these strings.
>   Furthermore, using the static analysis tooling (conformance)
>   [discussed previously](https://bughunters.google.com/blog/5850786553528320/a-deep-dive-into-js-trusted-types-violations#shift-left-), we
>   were able to cross-check these strings against the linter warnings that
>   were produced on a particular project build and its transitive
>   dependencies. But this is not an absolute requirement, for AppSheet, using
>   Sourcegraph was more than enough!

### 2\. Reproducing the violation via runtime analysis

If we don't find the violation by the approach described above (which is very
possible), we can now continue by performing some runtime analysis. Thanks to
the `document-uri`, we should know on which page the violation is occurring.
Using your intuition and the `script-sample` input sink, you can try to trigger
the violation by guessing the right user workflow to run on that page. If you
succeed, you will be able to see an error message logged to the violation on the
Chrome Devtools Console:

![](https://storage.googleapis.com/bughunters-article-images/blogs/jstt_violations_01.png)

_Fig. 1. Chrome DevTools shows Trusted Types violations_

From here, you can click on the triangle to the left of the console error
message to go through the call stack and see in which file the violation is
occurring – but do keep in mind that the JS files served in production may have
been bundled and minified.

As a neat trick, Chrome also supports adding breakpoints for Trusted Types
violation natively. To give it a try, you can
[enable it from the console](https://developer.chrome.com/docs/devtools/javascript/breakpoints#trusted-type).

### 3\. Analyzing minified JS: A whole art in itself

As mentioned in the previous sections, it is common to observe that many of the
JavaScript resources examined while analyzing violation reports and also during
live debugging are minified and do not resemble the source files in our
application’s repository.

The easiest way to solve this problem is to use sourcemaps generated by your
bundler to relate the bundled and minified code back to the original source
location. However, when live debugging the production resources being served on
the web app, this is not always possible. Some applications load pre-minified
files directly (e.g., via script tags); in such cases, source maps won't be
available, and the minified code will be the only version accessible.

In these cases, there are still a couple of tricks that help us relate these
minified code locations back to the pre-bundled and pre-minified versions:

1. Use Chrome’s pretty-print button if viewing the file in the Chrome Dev Tools
source viewer. This is the curly braces button (`{ }`) in the bottom right
hand corner of the source code panel.
2. Look for symbols and static strings that are not minified. While variable
names and user-defined function names can be minified, Web Platform APIs
cannot. For instance, we might see references to `Q(a)`, but a call like
`a.innerHTML` still preserves the un-minified function name. Similarly,
static string constants in code (for example, `a.setAttribute('href', …)`)
are also not minified.
3. Observe the control flow of the statements. Sometimes (at least for Closure
Compiler), the control flow logic may be rewritten, but these rewrites are
limited to inlining of certain functions. If the structure of loops and
if-statements with minified names, especially when viewed after
pretty-printing, looks similar to your source code with extra verbosity from
inlined functions, then this is likely the correct place.

## Conclusion

We've given you all the tools you need to investigate violations by yourself!
This toolkit should be enough to deal with most of the violations that you might
face.

Do you want to try out some of these tips and techniques yourself to make your
codebase more secure against XSS? Based on the lessons learned from our journeys
described above, we built a Chrome Extension that will collect Trusted Types
violations as you interact with a web app and surface information that you will
find useful in the investigation! Try out
[Trusted Types Helper](https://github.com/google/trusted-types-helper)!

Now you know about investigating Trusted Types violations. But once you found
the root cause of your violation, you might be wondering: How do I fix it? To
find out how, follow our guidelines on fixing common
[Trusted Types violation patterns](https://web.dev/articles/trusted-types#fix-violations).
These guidelines describe an approach which will empower you to handle most of
the violations you'll face.

By fixing Trusted Types violations in your web app, you're taking a step towards
improved security. And when you address these violations in an open source
library used by other web apps, you're enhancing the security of the whole JS
ecosystem. We welcome PRs to any public library you're fixing and invite you to
join us in our mission to eliminate XSS for everyone.

## References

\[1\] In the context of Trusted Types compatibility, static analysis checks are
not comprehensive for two reasons: (a) there are opportunities for both false
positives and negatives due to the dynamic nature of the JavaScript language,
and (b) type checking on the TypeScript or Closure compiler does not guarantee
that the values being assigned to DOM APIs are not user-controlled.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab