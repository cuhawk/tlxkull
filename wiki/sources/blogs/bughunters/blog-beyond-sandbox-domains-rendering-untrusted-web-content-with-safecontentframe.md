---
source: bughunters
source_url: https://bughunters.google.com/blog/beyond-sandbox-domains-rendering-untrusted-web-content-with-safecontentframe
title: "Beyond Sandbox Domains: Rendering Untrusted Web Content with SafeContentFrame - Google Bug Hunters"
description: "Rendering untrusted web content is fraught with security risks. Learn how SafeContentFrame, a new TypeScript library, offers a robust solution for isolating web content and protecting against threats like XSS and side-channel attacks."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/beyond-sandbox-domains-rendering-untrusted-web-content-with-safecontentframe#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Beyond Sandbox Domains: Rendering Untrusted Web Content with SafeContentFrame

![](https://storage.googleapis.com/bughunters-article-images/blogs/jangora.jpg)

Jan Gora

Information Security Engineer

Published: Sep 18, 2025

Security Engineering  Web Security

[RSS Feed](https://bughunters.google.com/feed/en)

# Beyond Sandbox Domains: Rendering Untrusted Web Content with SafeContentFrame

In a previous blog post,
[Securely Hosting User Data in Modern Web Applications](https://security.googleblog.com/2023/04/securely-hosting-user-data-in-modern.html),
we touched on how we approach serving untrusted active and inactive content.
While our solution for serving inactive content continues to reliably serve
Google's needs, the active version encountered a couple of problems such as
caching performance or breakages coming from null origin iframes.

To address these issues, we’ve developed **SafeContentFrame**, a new TypeScript
library that not only solves the aforementioned problems but also significantly
increases content isolation. SafeContentFrame provides a secure way to render
untrusted content of various formats – anything a browser can render, including
HTML, PDF, XML, SVG, and more – inside an iframe.

## Problems we are trying to solve

Historically, rendering user content in a browser has relied on sandbox domains
such as `googleusercontent.com`. This isolates untrusted content from the main
application, leveraging the browser's
[Same-Origin Policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
(SOP). However, despite the protections of the SOP, this approach might have
other isolation problems:

- Two same-site documents could share the same site-scoped state (e.g.
cookies, HTTP cache), because browsers usually isolate storage at the
[eTLD+1](https://web.dev/articles/same-site-same-origin) level (referred to
as “same-site isolation”).
- Two same-site documents could share the same browser renderer process and
therefore be susceptible to hardware side-channel leaks (e.g. SPECTRE),
because browser-level process isolation also occurs at the eTLD+1 level.

This means that a malicious file could potentially compromise a user's sensitive
data that’s been rendered on another subdomain.

![](https://storage.googleapis.com/bughunters-article-images/blogs/safecontentframe_01.svg)

_Fig. 1. Potential issues with isolation when relying on sandboxed domains_

### The genesis of SafeContentFrame: A tale of CTFs and research

The journey to SafeContentFrame was heavily influenced by our research into
secure content rendering, much of which was battle-tested and showcased in
Google CTF challenges. Historically, a common solution for rendering untrusted
active content was to sandbox it on a semi-random subdomain. This approach had a
critical flaw: the domain was brute-forceable, allowing an attacker to
potentially render a malicious document on the same origin as a sensitive one,
breaking origin isolation. This very issue led to a vulnerability in Google
Drive, which we simulated in the [Secdriven](https://ctftime.org/writeup/29310)
challenge in Google CTF 2021.

The quest for a more secure solution unearthed various subtle pitfalls that
content-hosting solutions need to account for, including client-side
race-conditions, unique origin leaks, and cryptographic weaknesses. These
discoveries inspired the "Postviewer" series in subsequent Google CTFs:
[Postviewer](https://ctftime.org/writeup/39218),
[Postviewer v2](https://ctftime.org/writeup/39216),
[Postviewer v3](https://ctftime.org/writeup/39220),
[Game Arcade](https://gist.github.com/terjanq/27230afcee73ee75484ac14ac53e78bc#file-gamearcade-md),
and most recently,
[Postviewer v5²](https://gist.github.com/terjanq/e66c2843b5b73aa48405b72f4751d5f8)
in 2025, which featured the production version of SafeContentFrame.

## Our solution

SafeContentFrame is a client-side TypeScript library requiring no special
server-side integration beyond serving a static file on a wildcard domain.

### PSL domain – usercontent.goog

A key component of our solution is a new sandbox domain – `usercontent.goog`. We
solved the same-site isolation problems by placing `*.usercontent.goog` onto the
[Public Suffix List (PSL)](https://publicsuffix.org/). As a result,
`subproduct.product.usercontent.goog` acts as `eTLD+1`, providing strong
browser-enforced isolation for storage and processes between different rendered
resources.

In practice, this means that each of the two files rendered on
`file1.scf.usercontent.goog` and `file2.scf.usercontent.goog` will have their
own storage and – in browsers that support site isolation – isolated browser
processes.

### Infrastructure & how it works

The library consists of two main parts: the client-side JS library and an HTML
"shim" served from a CDN-like service which greatly decreases latency. The JS
library and the HTML shim interact through the following steps:

1. **Iframe Creation:** The JS library creates an iframe pointing to the shim
hosted on a unique URL on `*.scf.usercontent.goog`.
2. **Content Delivery:** The library sends the content to be rendered to the
shim iframe via `postMessage`.
3. **Integrity Checks:** The shim verifies the message origin and recomputes
the hash using the included `salt` to ensure the message is authentic and
from the correct parent origin.
4. **Content Rendering:** If the checks pass, the shim, running on the unique
origin, creates a Blob from the received content and navigates the iframe to
the `blob:` URL.

![](https://storage.googleapis.com/bughunters-article-images/blogs/safecontentframe_02.svg)

_Fig. 2. How the JS library and the HTML shim interact_

### Secure unique origin

By default, every file is hosted on a secure URL in the form of:

```
https://<hash>-h<version>.scf.usercontent.goog/<product>/shim.html?origin=<parent_origin>
```

Where:

- `<hash>`: A cryptographic hash derived from the `<product>`,
`<parent_origin>`, and a unique `salt` (which is based on file content or a
random value).
- `<version>`: The version of the shim file, ensuring updates don't break
existing instances and allowing for security fixes.
- `<product>`: A product-specific identifier.
- `<parent_origin>`: The origin of the page embedding SafeContentFrame, used
for `postMessage` validation.

![](https://storage.googleapis.com/bughunters-article-images/blogs/safecontentframe_03.svg)

_Fig. 3. Default secure URL syntax_

### Integrity checks

The shim performs crucial integrity checks before rendering content:

1. **Origin Verification:** Ensures the `postMessage` comes from the expected
`<parent_origin>` specified in the URL query parameter.
2. **Hash Verification:** Recomputes the `<hash>` using the received `salt` and
other parameters, and compares it against the hash in its own hostname. This
verifies the integrity of the payload and the sender's identity, ensuring
the message was indeed initiated by a legitimate SafeContentFrame library
instance with the correct content/salt.

These checks ensure that only the legitimate embedding page can render content
in this specific iframe instance and that the content corresponds to the unique
origin.

The shim’s core logic can be visualized as the following JavaScript snippet:

```js
/* JavaScript snippet served on:
https://<hash>-h<version>.scf.usercontent.goog/<product>/shim.html?origin=<parent_origin>*/
onmessage = evt => {
  if (originFromUrl === evt.origin
      && VERIFY_HASH(
             hashFromUrl, productFromUrl, parentOriginFromUrl, evt.data.salt)) {
    const blob = new Blob([evt.data.body], {type: evt.data.mimeType});
    location.replace(URL.createObjectURL(blob));
  }
}
```

### Threat Model

SafeContentFrame is designed to defend against a variety of threats:

1. **Cross-Site Scripting (XSS) in Rendered Content:** The primary goal is to
render untrusted content. By design, content is rendered on a unique,
sandboxed origin on `*.scf.usercontent.goog`. This origin is different from
the embedding application's origin, preventing the rendered content from
accessing the parent page's data or cookies, due to the Same-Origin Policy.
2. **Origin Leakage:** Each SafeContentFrame instance uses a unique,
hard-to-guess origin like
`https://<hash>-h<version>.scf.usercontent.goog.` But even if the
exact URL is leaked to an attacker, they cannot reuse it to render their own
malicious content. This is because the `<parent_origin>` is embedded as part
of the computed `<hash>`. To make the shim accept a `postMessage` on the
leaked origin, the attacker would need to control a page on
`<parent_origin>`, or otherwise the shim's integrity checks would fail.
3. **Isolation from Unauthorized Origins:** The shim strictly verifies that any
incoming `postMessage` originates from the exact `<parent_origin>` specified
in its URL query parameters (i.e., `event.origin === <parent_origin>`).
This prevents malicious websites (e.g., `attacker.com`) from sending
messages to the shim iframe.
4. **Isolation Between Rendered Resources:** The use of a `salt` in the hash
calculation ensures that different resources generally render on different
origins.
5. **Spectre/Side-Channel Attacks:** Because `*.usercontent.goog` is on the
Public Suffix List, each `<hash>-h<version>.scf.usercontent.goog` domain
is treated as a separate eTLD+1. Modern browsers leverage this to enforce
process isolation, mitigating the risk of side-channel attacks between
different rendered content instances.
6. **Shim Vulnerabilities:** The shim version is included in the hostname
(`-h<version>`). If a vulnerability is discovered in a specific shim
version, new SafeContentFrame instances will use an updated shim URL with a
new version number. This prevents new renderings from being affected by the
old vulnerability, and old instances on the vulnerable shim version remain
isolated and cannot affect newer, patched instances.
7. **Integrity Against Manipulation:** The `<hash>` in the URL is recomputed by
the shim using the `salt` provided in the `postMessage`. The shim compares
this recomputed hash with the one in its own hostname. This ensures that the
`salt` (and other parameters like `<product>` and `<parent_origin>`) used to
generate the origin in the first place matches those provided during the
content rendering message, proving the message's authenticity and integrity.

#### Caching Modes

SafeContentFrame supports different caching modes to balance security and
performance:

- **Caching Disabled (the default):**
  - _Origin Generation:_ Random `salt` for each rendering.
  - _Isolation:_ Strongest isolation, unique origin every time.
- **Caching Enabled (with default salt generation):**
  - _Origin Generation:_`salt` derived from `sha256(file_contents + parent.location.pathname)`.
  - _Isolation:_ Identical content on the same path shares an origin.
- **Caching Enabled (with custom salt):**
  - _Origin Generation:_`salt` derived from a product-provided
    `customFileIdentifier`.
  - _Isolation:_ Content with the same custom ID shares an origin.

## Our Users

SafeContentFrame has already been adopted across various products with currently
over 50 internal and external Google products generating millions of requests
daily. It has also recently become a popular choice for our fast-growing line of
AI services. For example, it's used in our popular AI products –
[Gemini Canvas](https://blog.google/products/gemini/gemini-collaboration-features/)
and
[Google AI Studio](https://ai.google.dev/gemini-api/docs/ai-studio-quickstart) –
for previewing and rendering user-provided mini-applications. The library's
simplicity and built-in security features help teams ship products faster while
maintaining Google's high security standards without manual configuration.

## SafeContentFrame Demo

Explore the features of SafeContentFrame in more detail on our
[interactive demo](https://safecontentframe.static.usercontent.goog/).

We encourage security researchers to examine SafeContentFrame. Findings can be
reported through the
[Google Vulnerability Reward Program (VRP)](https://bughunters.google.com/about/rules/google-friends/6625378258649088/google-and-alphabet-vulnerability-reward-program-vrp-rules).

## Conclusion

SafeContentFrame offers a robust and modern solution for rendering untrusted
content on the web. By leveraging unique origins on a Public Suffix List domain,
strong cryptographic integrity checks, and process isolation, it provides a high
degree of security against a range of attacks, from XSS to side-channel
vulnerabilities. Its design, refined through real-world application and insights
from security research and CTF challenges, aims to make secure content isolation
easy for developers to implement.

The library's flexibility in caching modes and its independence from complex
server-side setups make it a practical choice for many applications, especially
those handling user-generated content or content from third parties. As web
threats evolve, SafeContentFrame will continue to be updated to provide a
reliable defense, helping developers build safer applications without
compromising user experience.

We believe SafeContentFrame is a significant step forward in securely handling
active content on the web and encourage its adoption. Furthermore, we hope that
the security principles and mechanisms demonstrated in SafeContentFrame can help
other web application developers and inspire future web platform standards,
making the entire web safer for everyone.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab