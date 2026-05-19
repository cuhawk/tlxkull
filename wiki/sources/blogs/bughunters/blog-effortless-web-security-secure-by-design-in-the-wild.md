---
source: bughunters
source_url: https://bughunters.google.com/blog/effortless-web-security-secure-by-design-in-the-wild
title: "Effortless Web Security: Secure by Design in the Wild - Google Bug Hunters"
description: "This blog post presents two initiatives that demonstrate two ways Google shares security work with the industry: Contributing to the Secure Web Application Guidelines Community Group in W3C, and introducing auto-CSP in Angular."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/effortless-web-security-secure-by-design-in-the-wild#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Effortless Web Security: Secure by Design in the Wild

![](https://storage.googleapis.com/bughunters-article-images/blogs/aaronshim.jpeg)

Aaron Shim

Software Engineer

Published: Nov 14, 2025

Security Engineering

[RSS Feed](https://bughunters.google.com/feed/en)

# Effortless Web Security: Secure by Design in the Wild

Over the years, Google’s security engineering team has been engineering security
into the design of many different problem domains across hundreds of products at
Google. This philosophy, which we termed
[Secure by Design](https://research.google/pubs/secure-by-design-at-google/), is
about embedding low-friction security guardrails throughout the development
lifecycle. By providing opinionated, secure-by-default configurations that
absorb routine complexity, we accelerate velocity and make the secure path the
easiest path. Particularly in the field of web security, this approach leads to
being able to avoid entire bug classes at scale by defining development
primitives that follow the
[safe coding philosophy](https://research.google/pubs/if-its-not-secure-it-should-not-compile-preventing-dom-based-xss-in-large-scale-web-development-with-api-hardening/)
– a set of tools that guide the developer towards making safer choices and make
it difficult to unintentionally write vulnerable code \[1\].

As a direct result of this work, injection attacks like
[Cross-Site Scripting](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)
have been nearly eliminated on new codebases that adopt this approach, reaching
[almost zero](https://www.youtube.com/watch?v=hOOpn0xEqrQ&t=775s). These
accomplishments are a core component of our
[recipe for web security](https://bughunters.google.com/blog/5896512897417216/a-recipe-for-scaling-security),
which effectively scales across thousands of web applications and billions of
users.

One major aspect of
[our commitment](https://static.googleusercontent.com/media/publicpolicy.google/en//resources/google_commitment_secure_by_design_overview.pdf)
to Secure by Design is our team’s commitment to sharing the latest know-how
regarding this philosophy and its practical applications with the industry to
improve the security of the online ecosystem as a whole. In this blog post, we
will present two separate initiatives that demonstrate our work towards this
principle:

- Contributing to the Secure Web Application Guidelines Community Group in W3C
- Introducing Auto-CSP in Angular

## W3C Community Group: Secure Web Application Guidelines (SWAG)

In order to encourage secure development processes and the adoption of web
security best practices across all developer ecosystems, we are increasing our
engagement with the external web developer community.

The SWAG community group was kicked off during W3C’s Technical Plenary and
Advisory Committee (TPAC) 2024 with the stated goal of connecting developers and
security professionals to ensure the most effective use of the Web Security
features developed through the W3C Web Application Security Working Group
(WebAppSec). This community group brings professionals from across the industry
together, including contributors who also donate their expertise to other
foundations such as OpenSSF and OpenWebDocs and help with the cross-pollination
of ideas.

Given the feedback from the external developer community that many of these
security features on the Web might have lower adoption rates due to their
relative complexity, this community group has delivered – thanks to the support
of the excellent content team from OpenWebDocs – much improved documentation on
[XSS](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS),
[CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP),
[Trusted Types](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API),
[cross-site leaks](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XS-Leaks),
and
[prototype pollution](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution),
to name a few. In addition, the group hosts forums for industry leaders to
discuss novel approaches and
[best practices](https://www.youtube.com/watch?v=DSCazlJV-es&list=PLNhYw8KaLq2Wr27HLfSTD4d6JpC3G0PVr)
that embody Secure by Design, as well as publishing guidelines for both
[Web developers](https://github.com/w3c-cg/swag/blob/main/docs/security_guidelines.md)
and maintainers of important
[web dependencies](https://github.com/w3c-cg/swag/blob/main/docs/guidelines_for_libraries.md).

If you are interested in how Secure by Design principles are being used across
the industry to empower developers both in the industry and across the open
source ecosystem, [SWAG plenary calls](https://www.w3.org/community/swag/) are
open to all! Be a part of the conversation on how Secure by Design can shape a
safer web for everyone!

Additionally, the SWAG Community Group is preparing a
[“state of secure development” survey](https://docs.google.com/forms/d/e/1FAIpQLScbKJL2Q8XABAHVystmqGU2lQoE0tAJSL_dwhvwPwBcJ-M4fQ/viewform?pli=1&pli=1)
targeting web developers, with the goal of gaining a better understanding of
their friction points – please consider sharing your experience with the group
so that we can continue to advocate for a better developer experience for
security features integrated into the web platform!

## Auto-CSP in Angular

In addition to our engagement in industry and ecosystem-wide forums, we also aim
for technical contributions by shipping code that developers can use to embody
the security principles we recommend.

One example of a mitigation that has been used to effectively
[address cross-site scripting vulnerabilities](https://web.dev/articles/strict-csp)
(XSS) at Google is the Strict Content Security Policy (CSP). Strict CSP enhances
security by avoiding the problems of allowlist-based policies such as being
inadvertently
[overly permissive](https://dl.acm.org/doi/pdf/10.1145/2976749.2978363) and
difficult to keep up-to-date
( [details](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP#strict_csp)).

![](https://storage.googleapis.com/bughunters-article-images/blogs/effortless_01.png)

_Fig. 1. The elements of a Strict Content Security Policy_

Traditionally, configuring a nonce-based CSP was considered a difficult task by
many web developers, as it required:

1. A tight integration between the HTML generation and the serving
infrastructure of your web application to make sure that the nonce present
in the HTML is also present in your HTTP headers. This is difficult because
the business logic of a web application may be far away from its deployment
architecture, and is often taken care of by different teams.
2. Templating support for HTML that is able to add the nonce attribute to every
`<script>` and `<style>` tag known at HTML-generation time. This is
difficult in templating systems that do not support this capability
natively.
3. Guaranteeing that the nonces are only used once. This is difficult because
this means that the value of an HTML response cannot be cached – as the
nonce will have to change on every response. This is especially difficult
for single-page applications (SPAs) that ship a static HTML and JS bundle –
such as client side-rendered Angular applications.

A proposed alternate approach is a hash-based CSP – a policy that specifies that
an inline script is allowed to run by providing a hash of its inline contents as
a value that looks like `sha256-...` under the directive `script-src`:

![](https://storage.googleapis.com/bughunters-article-images/blogs/effortless_02.png)

_Fig. 2. An example of a hash-based CSP_

Auto-CSP is an automatic hash-based CSP that simplifies these difficulties by
generating a hash-based CSP during the final HTML and JS bundle generation time
for Angular browser-rendered applications.

Our approach, in simplified terms, works like this:

> Some background context can help understand our approach. There are two kinds
> of scripts:
>
> - Inline scripts, where JavaScript content resides between
>   `<script>`...`</script>` tags
> - Externally sourced script, where the JavaScript content lives at an
>   external location (specified by the `src` attribute) and is written as
>   `<script src=...></script>`, i.e. with no JavaScript content present
>   inline between the tags
>
> Since CSP's hashing mechanism checks the hash against the hashed version of
> the JavaScript content, it's easy to hash inline scripts from observing the
> content of the HTML. However, this does not hold true for external scripts,
> since their script content needs to be fetched over the network. For this
> reason we convert all external scripts into inline scripts by replacing them
> with an inline "loader" script.

1. All `<script>` tags with `src` attributes are rewritten to inline script
tags that dynamically add new script nodes to the DOM. This is done so that
we can hash this new loader script for the CSP and have it
[propagate trust with strict-dynamic](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src#strict-dynamic)
(`strict-dynamic` allows our loader script to execute all scripts that were
rewritten to be dynamically loaded).
2. All inline scripts are hashed to generate a CSP.
3. The CSP is added to the top of the newly generated HTML in the bundle. This
means that the script contents and the HTML-inserted CSP stay in sync as a
part of the same build process.

Here is an example of this process. A simple page might look like this:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple Script Example</title>
</head>
<body>
    <h1>Check the Console</h1>

    <script>
        console.log("Hello, world!");
    </script>

    <script src="https://example.com/script.js" type="module"></script>
    <script src="https://example.com/another_script.js"></script>
</body>
</html>
```

The non-inline scripts will be re-written like this (notice how all the
`<script>` tags with the `src` attribute have been turned into inline scripts
that will dynamically recreate these tags, while the preexisting inline
`<script>` tag remains unchanged):

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Simple Script Example</title>
  </head>
  <body>
    <h1>Check the Console</h1>

    <script>
      console.log("Hello, world!");
    </script>

    <script>
      var scripts = [{\
          "src": "https://example.com/script.js",\
          "type": "module"\
        },\
        {\
          "src": "https://example.com/another_script.js",\
          "type": undefined\
        }\
      ];

      scripts.forEach(function(scriptInfo) {
        var s = document.createElement('script');
        s.src = scriptInfo.src;

        if (scriptInfo.type) {
          s.type = scriptInfo.type;
        }

        s.async = false; // preserve execution order.
        document.body.appendChild(s);
      });
    </script>
  </body>
</html>
```

Now, we will hash the contents of the two inline scripts – the only scripts left
on the page – and generate a hash from it. This CSP will then be embedded into
the HTML itself as a meta tag. This approach of embedding the CSP directly into
the HTML asset simplifies the deployment process and addresses the risk that the
CSP defenses will be separated from the code that they secure due to
configuration of the deployment, etc.

```html
<meta http-equiv="Content-Security-Policy" content="script-src 'strict-dynamic' 'sha256-bry...' 'sha256-xyz...' https: 'unsafe-inline'; object-src 'none'; base-uri 'self';">
```

By developing this feature, we transformed a best-in-class mitigation for a
specific vulnerability class – previously difficult to adopt – into an easily
configurable option for Angular developers. This embodies a core value of the
Secure by Design principle: empowering developers by integrating security
features without imposing additional overhead. In addition, while implementing
this feature, we were careful to verify that this script transformation does not
lead to performance regressions. We believe that features developed according to
these principles enable developers to deliver exceptional functionality to their
customers while simultaneously providing world-class security. This
functionality has been available in Angular in
[every version since v19](https://blog.angular.dev/meet-angular-v19-7b29dfd05b84)
– please try it out today!

## What’s Next

We are committed to advancing Secure by Design on two parallel tracks: shipping
concrete technical solutions and fostering industry-wide collaboration. We need
your involvement on both fronts to help us build a safer web.

### Adopt Secure Defaults

Start using these technical innovations in your applications today:

- **Enable Auto-CSP in Angular:** If you are on Angular v19 or later,
[turn on this feature](https://angular.dev/best-practices/security#content-security-policy)
to instantly improve your security posture.
- **Give Technical Feedback:** [Specific feedback](https://github.com/angular/angular-cli/issues) on
Auto-CSP helps us refine it and paves the way for similar features in other
frameworks.

### Join the Community Conversation

Help us understand the real-world friction points developers face so we can
advocate for better platform standards:

- **Take the Developer Survey:** Influence the future of our work by sharing
your experience in our
[state of secure development survey](https://docs.google.com/forms/d/e/1FAIpQLScbKJL2Q8XABAHVystmqGU2lQoE0tAJSL_dwhvwPwBcJ-M4fQ/viewform?pli=1&pli=1).
- **Participate in W3C SWAG:** Join our
[plenary calls](https://www.w3.org/community/swag/) to connect directly with
other developers and security professionals.

## References

\[1\] Further papers and blog posts describing our approach to security include
[Secure by Design: Google's Blueprint for a High-Assurance Web Framework](https://bughunters.google.com/blog/6644316274294784/secure-by-design-google-s-blueprint-for-a-high-assurance-web-framework),
[An Overview of Google's Commitment to Secure by Design](https://static.googleusercontent.com/media/publicpolicy.google/en//resources/google_commitment_secure_by_design_overview.pdf),
and
[Developer Ecosystems for Software Safety](https://research.google/pubs/developer-ecosystems-for-software-safety-2/).

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab