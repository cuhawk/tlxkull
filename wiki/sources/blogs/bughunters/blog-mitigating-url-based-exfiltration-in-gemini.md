---
source: bughunters
source_url: https://bughunters.google.com/blog/mitigating-url-based-exfiltration-in-gemini
title: "Mitigating URL-based Exfiltration in Gemini - Google Bug Hunters"
description: "This post takes a look at how Gemini and other agents created by Google mitigate URL-based data exfiltration attacks."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/mitigating-url-based-exfiltration-in-gemini#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Mitigating URL-based Exfiltration in Gemini

![](https://storage.googleapis.com/bughunters-article-images/blogs/jkokatsu.jpg)

Jun Kokatsu

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/vernooij.jpg)

Koen Vernooij

Software Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/fbornhofen.jpg)

Fabian Bornhofen

Software Engineer

Published: Mar 9, 2026

Vulnerability Research

[RSS Feed](https://bughunters.google.com/feed/en)

# Mitigating URL-based Exfiltration in Gemini

[(Indirect) Prompt Injection](https://www.google.com/url?q=https://support.google.com/a/answer/16479560&sa=D&source=docs&ust=1770631928753901&usg=AOvVaw1ty7xEl2wn4wH176l56seC)
is one of the major security risks in AI applications. A common technique to
exploit Prompt Injection is to exfiltrate user data through URLs. In this post,
we will explain how Gemini and other agents created by Google mitigate URL-based
exfiltration attacks.

Before diving into these mitigations, it’s important to understand the mechanics
of the attack. The core of this attack lies in a URL's ability to act as a data
exfiltration vector, carrying a payload (e.g., within its parameters) that can
be disclosed to the host when the URL is requested. Through Prompt Injection,
the LLM can be manipulated into constructing such a URL that could be accessed
either automatically or through unwitting cooperation by the victim (e.g., by
clicking a link).

![](https://storage.googleapis.com/bughunters-article-images/blogs/mitigating-url-based-exfiltration-in-gemini_01.png)

_Fig. 1. How markdown-based data exfiltration works_

Examples of such attacks include:

1. [Data exfiltration using markdown images](https://embracethered.com/blog/posts/2023/google-bard-data-exfiltration/)
2. [Abusing the browsing tool in Gemini](https://www.tenable.com/security/research/tra-2025-21)

## Data exfiltration primitives

There are three primitives required to exfiltrate data using Prompt Injection.
This is commonly known as
[the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/).

1. (An agent has) Access to secrets
\[ [1](https://bughunters.google.com/blog/mitigating-url-based-exfiltration-in-gemini#notes)\].
2. (An attacker has) The ability to inject a prompt (either direct
\[ [2](https://bughunters.google.com/blog/mitigating-url-based-exfiltration-in-gemini#notes)\] or indirect).
3. (An attacker has) An exfiltration vector.

From the defenders’ perspective, all you need in order to mitigate an
exfiltration vulnerability is to block one of the three primitives in the attack
chain. As illustrated in the introduction, the most common type of exfiltration
vulnerability is URL-based data exfiltration, which has a clearly defined
exfiltration vehicle, i.e. the URL. Hence, this blog post focuses on blocking
this exfiltration vector.

## Mitigation

### Core idea

URL-based exfiltration vectors abuse the fact that LLMs can mutate 2 inputs—an
attacker-supplied URL and a secret—into a URL, which means that URLs used for
exfiltration are often “generated” at runtime (because attackers don’t know the
secret they want to steal).

This suggests that if we know _all_ unmutated URLs fed to an agent at inference,
then we can only allow such URLs in the agent’s output and deny any other URL,
since the use of such a URL is likely a result of a hallucination or a Prompt
Injection attack.

### URL provenance

With the above idea in mind, how do we know if a URL fed to an agent isn’t a
“generated” URL?

To address this challenge, we developed a system called URL provenance, which
extracts URLs from a source (e.g., RAG data, user’s prompts, etc.) and annotates
them with source information. The critical distinction is between generative &
non-generative sources. A generative source is any source which can mutate
inputs into the output, such as sources backed by LLMs and code execution tools.
Any other sources backed by classic APIs (e.g., Search API, Gmail API, etc.) and
users’ prompts are considered to be non-generative sources.

As the LLM generates tokens, the output URLs are cross-checked with URL
provenance to validate that they originated from a non-generative source. While
adding a URL provenance check for tool inputs (such as the browsing tool) was
relatively easy \[ [3](https://bughunters.google.com/blog/mitigating-url-based-exfiltration-in-gemini#notes)\],
this turned out to be somewhat tricky for markdown outputs. Therefore, we
developed a special markdown sanitizer to address this problem.

### Markdown sanitizer

Similar to HTML sanitizers which prevent
[XSS](https://portswigger.net/web-security/cross-site-scripting), we developed a
sanitizer for markdown, where we parse markdown on the server-side and apply
_sanitization_ to markdown AST nodes which can be used for exfiltration. Let’s
dive into the details!

#### Image sanitization

As explained in the introduction, image URLs present in the markdown source can
be used for exfiltration. Since Gemini’s system already had a way to embed
images outside of markdown (for things like generated images), we simply decided
to remove all markdown images (except data: URL images) detected during markdown
parsing for sanitization, and asked developers to use alternative image
embedding methods if they needed to render images (which have no exfiltration
concerns).

#### Link sanitization

Similar to markdown images, markdown links can be used for exfiltration – if a
user clicks on a link present in the output, their browser will navigate to an
attacker-controlled URL. To address this, once the markdown parser detects link
nodes, we call URL provenance to cross-check that the URL in the link is
non-generative.

Furthermore, Markdown supports
[several link formats](https://www.markdownguide.org/basic-syntax/#links).

1. `[this is a link](https://example.com)`
2. `[this is a link][1]`

`[1]: https://example.com`
3. `<https://example.com>`

We decided to convert the 3rd link format to the 1st format to ensure we don’t
break links due to client-side HTML escapes.

#### HTML escapes

The markdown format supports
[HTML](https://www.markdownguide.org/basic-syntax/#html). While we perform HTML
sanitization when we convert markdown to HTML for web clients, HTML sanitizers
are designed to protect against XSS, rather than address exfiltration issues.
Therefore, things like exfiltration using the `<img>` tag (or any other tags
allowed by the HTML sanitizer) were possible. Given we didn't need to support
HTML in our markdown, we decided to perform HTML-escaping for HTML nodes in
markdown.

### Service signals & allowlists

URL provenance is the basis of the risk evaluation of a URL as it determines
whether a URL can be cross-referenced with original content. However, there are
some positive edge cases where it is fine for LLMs to generate URLs:

1. Rewrite of a URL that came from a user such as:
   - Adding “ _www._” at the beginning of a domain.
   - Fixing a misspelling (e.g., _exmaple.com_ -\> _example.com_).
2. URL generation from knowledge without a tool call (e.g., “What is the Google
website?” -> _google.com_).

Finally, there are reasons why we might want to block a URL that are not related
to data exfiltration (e.g., known phishing sites).

For all of these edge cases, we make use of service signals that provide
context-independent signals about the URL. For example, Gemini has access to
services to determine whether a URL is indexed, is a known bad site (such as
illegal or phishing), etc.

Additionally, there are some occasions where an agent needs to allow specific
URLs. Therefore, we do have a per-agent allowlist, which is kept minimal and
specific (referencing either an exact endpoint or at least containing a URL
path). Note that allowlists are generally not recommended since a wide use of
allowlists can result in a bypass through
[open redirectors](https://bughunters.google.com/learn/invalid-reports/web-platform/navigation/open-redirectors).

## Conclusion

The use of URL provenance and a markdown sanitizer allowed us to mitigate
URL-based data exfiltration attacks in Gemini. While a number of low-bandwidth
side channels remain difficult to block, we believe that limits applied (e.g.,
requiring user interaction) to such channels make exfiltration of large amounts
of data difficult. Additionally, as agents become more complex, there will be
other ways to exfiltrate data beyond the use of URLs. We are continuing our
journey to develop more mitigations as those new exfiltration methods are
identified.

## Notes

\[1\] Note that secrets don't need to be in the context of an agent. For example,
computer-use agents might be able to access secrets by _Ctrl+A_ and _Ctrl+C_
without read access to the actual data.

\[2\] Some AI applications allow an attacker to directly inject a prompt through a
query parameter. If such prompts are executed automatically, this has to be
considered as a valid attack (though ideally such a feature shouldn’t exist).

\[3\] The caveat here is that a prompt injection might leak a secret
character-by-character through repeated tool calls (assuming the tool call
doesn’t require user interaction). Limiting the number of these calls in a
single turn mitigates this risk.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab