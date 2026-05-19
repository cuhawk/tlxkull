---
source: bughunters
source_url: https://bughunters.google.com/blog/escaping-and-in-attributes-how-it-helps-protect-against-mutation-xss
title: "Escaping '<' and '>' in attributes – how it helps protect against mutation XSS - Google Bug Hunters"
description: "The HTML specification has been updated to escape '<' and '>' in attributes to prevent mutation XSS (mXSS) vulnerabilities. This post details the reasoning behind this change and explains why this update improves security."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/escaping-and-in-attributes-how-it-helps-protect-against-mutation-xss#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Escaping '<' and '>' in attributes – how it helps protect against mutation XSS

![](https://storage.googleapis.com/bughunters-article-images/blogs/securitymb.jpg)

Michał Bentkowski

Information Security Engineer

Published: Jun 12, 2025

Chrome

[RSS Feed](https://bughunters.google.com/feed/en)

# Escaping '<' and '>' in attributes – how it helps protect against mutation XSS

As of May 20, 2025,
[the HTML specification has been updated](https://github.com/whatwg/html/pull/6362)
to escape `<` and `>` in attributes, helping prevent
[mutation XSS](https://cure53.de/fp170.pdf) (mXSS) vulnerabilities. This change
landed in Chrome M138, which was promoted to Beta on May 28, 2025, and will
become Stable on June 24, 2025.

This post details the reasoning behind this change and explains why this update
improves security. If you're interested in understanding what the implications
of this change are for web developers and what modifications they might need to
make, see our, see our
[related post on developer.chrome.com](http://developer.chrome.com/blog/escape-attributes).

## How are HTML sanitizers used in JavaScript?

Before going into details about the change, let’s take a short moment to talk
about the usage of HTML sanitizers in JavaScript because this change aims to
make the use of such client-side HTML sanitizers safer.

An example of a popular JavaScript-based HTML sanitizer is
[DOMPurify](https://github.com/cure53/DOMPurify). How is it typically used?
Assume that we have a potentially unsafe HTML snippet coming from a user and we
want to render it safely into `document.body`. This is what we might do:

```
document.body.innerHTML = DOMPurify.sanitize(unsafeHtml);
```

Even though it’s just a single line of code, there’s actually a lot going on
under the hood. Let’s break it down:

1. The right-hand side of the assignment (`DOMPurify.sanitize(unsafeHtml)`) is
evaluated first.
2. `DOMPurify` **parses** the string argument as HTML and creates a DOM tree.
3. `DOMPurify` iterates over all elements and attributes in the DOM tree and
removes or sanitizes anything it deems insecure.
4. `DOMPurify` **serializes** the safe DOM tree into a string.
5. The result is assigned to `innerHTML` which means that the browser will
**parse** the HTML into a DOM tree again.

You can notice that we’re performing the following operations: **parsing ->**
**serialization -> parsing**. You might expect that when you have a DOM tree that
you serialize and then parse for a second time, you should get the initial DOM
tree. However, this is not true in HTML. It’s even
[directly called out in the spec](https://html.spec.whatwg.org/multipage/parsing.html#serialising-html-fragments:html-parser-3)
with the following warning:

> It is possible that the output of this algorithm, if parsed with an HTML
> parser, will not return the original tree structure. Tree structures that do
> not roundtrip a serialize and reparse step can also be produced by the HTML
> parser itself, although such cases are typically non-conforming.

This behavior is the exact reason why a vulnerability known as **mutation XSS**
**(mXSS)** exists: it’s possible that a sanitizer may have a DOM tree it considers
safe; however, after re-parsing, this DOM tree will be materially different,
resulting in an XSS.

See the presentation slides from my talk
[Why is HTML a mutating beast?](https://docs.google.com/presentation/d/19H7zhb06ngQ7ipRQ8rBdyFIgkZyKWQAJBUuQbGkDYgI/edit?slide=id.g159a3d6718ad8e06_458&resourcekey=0-qCWjXLkYpcNatUBHD8T6kA#slide=id.g159a3d6718ad8e06_458)
for a couple of examples of mutations happening directly because of how the HTML
spec is written.

Before looking into a specific example of mXSS, let’s focus on how exactly
serialization works.

## HTML serialization

Serialization is a process of transforming a DOM tree into a textual
representation. In the web platform one way to serialize a DOM tree is to use
the `innerHTML` or `outerHTML` properties.

As an example, let’s consider the following DOM tree:

```
┗ p data-test="abc"
  ┗ b
    ┗ #text: "Example"
```

When you get `outerHTML` of the root element, you’ll get the following HTML:

```
<p data-test="abc"><b>Example</b></p>
```

This result should not be too surprising. But now let’s change our DOM tree a
bit:

```
┗ p data-test="<x>Test"
  ┗ b
    ┗ #text: "<y>Test2"
```

Before the spec change from May 20, 2025, this DOM tree was serialized to:

```
<p data-test="<x>Test"><b>&lt;y&gt;Test2</b></p>
```

Here you can notice that the characters `<` and `>` appear in both an
attribute and a text node. However they are _not_ escaped inside the attribute.
Let’s see how this fact can be relevant for mXSS.

## Mutation XSS

This example is based on a famous XSS in Google Search found by
[Masato Kinugawa](https://x.com/kinugawamasato), about which
[LiveOverflow recorded a great video](https://www.youtube.com/watch?v=lG7U3fuNw3A).

The key part of this exploit was the `<noscript>` tag. It is the only tag in the
HTML specification whose parsing depends on whether scripting is enabled or not.

Consider the following snippet of HTML:

```
<noscript>
  <a>Hello</a>
</noscript>
```

If scripting is enabled, all content inside a `<noscript>` is treated as a text.
If scripting is disabled, then content inside a `<noscript>` is parsed just like
regular HTML. The table below showcases DOM trees resulting from parsing in both
of these modes:

|     |     |
| --- | --- |
| **Scripting enabled** | **Scripting disabled** |
| ```<br>┗ noscript<br>  ┗ #text: "<a>Hello</a>"<br>``` | ```<br>┗ noscript<br>  ┗ a<br>    ┗ #text: "Hello"<br>``` |

So now let’s consider the payload that XSS-ed Google Search. It looked as
follows:

```
<noscript><a alt="</noscript><img src onerror=alert(1)>">Hello</a></noscript>
```

Google Search internally used
[Closure Sanitizer](https://github.com/google/closure-library/blob/master/closure/goog/html/sanitizer/htmlsanitizer.js)
to sanitize the HTML. Similar to DOMPurify, Closure internally parses the HTML
using
[DOMParser.parseFromString](https://developer.mozilla.org/en-US/docs/Web/API/DOMParser/parseFromString).
This method always parses the HTML with **scripting disabled**. This means that
it creates the following DOM tree:

```
┗ noscript
  ┗ a alt="</noscript><img src onerror=alert(1)>"
    ┗ #text: "Hello"
```

This DOM tree looks safe from Closure Sanitizer's perspective: both `<noscript>`
and `<a>` are allowlisted as well as the `alt` attribute. Therefore Closure
returns a serialized form of this DOM tree as follows:

```
<noscript><a alt="</noscript><img src onerror=alert(1)>">Hello</a></noscript>
```

Now when this DOM tree is parsed again on assignment to `innerHTML`, it is
parsed with **scripting enabled**. So this means that `<a... >` won’t open a new
tag but will be treated as text instead. It will therefore create the following
DOM tree:

```
┣ noscript
┃ ┗ #text: "<a alt=""
┣ img src="" onerror="alert(1)"
┗ #text: Hello
```

As you can see, suddenly a new `<img>` tag was created that wasn't there before
when Closure was looking at the DOM tree! This introduces an mXSS.

## How escaping \`<\` and \`>\` helps

Escaping `<` and `>` as `&lt;` and `&gt;` in HTML attributes mitigates
mutation XSS vulnerabilities by preventing the creation of unexpected HTML tags
during re-parsing. Previously, unescaped `<` and `>` characters within
attributes could be misinterpreted as tag delimiters when the serialized HTML
was parsed again with different parsing rules, such as when scripting is enabled
versus disabled. By consistently escaping these characters, they cannot be
inadvertently converted into HTML elements, thus preventing attackers from
injecting malicious tags that would execute code.

Let’s consider the same example as in the previous section. We have the
following DOM tree again:

```
┗ noscript
  ┗ a alt="</noscript><img src onerror=alert(1)>"
    ┗ #text: "Hello"
```

But now we’re serializing it with `<` and `>` escaped in attributes. This
results in the following HTML:

```
<noscript><a alt="&lt;/noscript&gt;&lt;img src onerror=alert(1)&gt;">Hello</a></noscript>
```

And when this text is re-parsed with scripting enabled it creates the following
DOM tree:

```
┗ noscript
  ┗ #text: "<a alt="&lt;/noscript&gt;&lt;img src onerror=alert(1)&gt;">Hello</a>"
```

As you can see, the escaped characters prevent the unintentional creation of
HTML tags, thus effectively blocking the mutation XSS attack vector in this
scenario.

This change will block all mXSS vectors which depend on creating new tags
because of unescaped `<` and `>` characters in attributes. We have already
[received feedback](https://infosec.exchange/@cure53/114619223500569817) that
this change successfully prevented a critical vulnerability in a real-world
application!

## Does this change prevent all mXSS vectors?

The short answer is: “no”. Some mXSS vectors depend on another specific behavior
of HTML elements, which is the fact that for some HTML tags their text content
is not escaped at all. In one of the previous examples we've shown that `<`
is escaped in text nodes. This is not true for certain elements, such as
`<style>`.

Consider the following snippet of JS:

```
const style = document.createElement("style");
style.textContent = "</style><img src onerror=alert(1)>"
console.log(style.outerHTML);
```

This snippet will log the following HTML:

```
<style></style><img src onerror=alert(1)></style>
```

Note that even though the intention was to have `</style><img src onerror=alert(1)>` as the text content of the style tag, this information is not
maintained after serialization. Therefore, mXSS vectors depending on using
[tags whose text content is serialized literally](https://html.spec.whatwg.org/multipage/parsing.html#serialising-html-fragments:text)
will not be blocked by the change described in this blog post. While there’s
currently no proposal that addresses this issue, the Google Information Security
Engineering team is planning to explore options to fix this vector as well.

## How to avoid mXSS altogether?

In the
[How are HTML sanitizers used in JavaScript?](https://bughunters.google.com/blog/5038742869770240/escaping-and-in-attributes-how-it-helps-protect-against-mutation-xss#how-are-html-sanitizers-used-in-javascript-)
section we described how the typical usage of HTML sanitizers involves the
roundtrip of parsing and serialization. However, it is possible to completely
bypass this problem by just assigning the safe DOM into a node, instead of
serializing it first.

This is how the new
[Sanitizer API](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API)
works – it doesn't even provide a method to return a string, instead it assigns
a sanitized DOM directly to the node. Other sanitizers may also provide such an
option. For example, DOMPurify has a configuration parameter `RETURN_DOM`, while
[safevalues](https://github.com/google/safevalues/tree/e9ee139db294a4bbbcc0a9d1ee40ee4fd7d87bf5/src/builders/html_sanitizer#:~:text=returning%20SafeHtml.-,sanitizeToFragment,-(html%3A%20string)%3A%20DocumentFragment)
has a method called `sanitizeToFragment`.

In general, if your sanitizer allows you to return a DOM node instead of a
string, you should prefer this approach as it allows you to completely avoid any
risk of mXSS.

## Conclusion

We hope this post has explained the rationale behind the recent changes to HTML
serialization and which mXSS vectors this update mitigates.

If you are looking for practical tips on what to look out for when coding, be
sure to check out the
[related post on developer.chrome.com](http://developer.chrome.com/blog/escape-attributes).

## Additional information

- [Original bug report about this proposed change](https://github.com/whatwg/html/issues/6235)
- [Pull request that changes the spec](https://github.com/whatwg/html/pull/6362)
- [ChromeStatus entry](https://chromestatus.com/feature/6264983847174144)
- [LiveOverflow's video about mXSS in Google Search](https://www.youtube.com/watch?v=lG7U3fuNw3A)
- [Another example of mXSS that would've been blocked by this change](https://research.securitum.com/dompurify-bypass-using-mxss/)
- [Blog post](http://developer.chrome.com/blog/escape-attributes) on
developer.chrome.com describing how this change affects web developers

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab